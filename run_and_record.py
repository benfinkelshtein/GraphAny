import subprocess
import re
import neptune
import numpy as np
from collections import defaultdict
from argparse import ArgumentParser

# --- CLI args ---
parser = ArgumentParser()
parser.add_argument("--project", type=str, required=True)
parser.add_argument("dataset", type=str)
parser.add_argument("total_steps", type=int)
parser.add_argument("n_hidden", type=int)
parser.add_argument("n_mlp_layer", type=int)
parser.add_argument("entropy", type=float)
parser.add_argument("n_per_label_examples", type=int)
args = parser.parse_args()

# --- Neptune setup ---
API_TOKEN = "eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiI3ZTZjOWE3Yi0xOGU3LTQwOTEtYWIzNS1hYzRmOGZiMjhhNTcifQ=="
run = neptune.init_run(project=args.project, api_token=API_TOKEN)
run["params/dataset"] = args.dataset
run["params/total_steps"] = args.total_steps
run["params/n_hidden"] = args.n_hidden
run["params/n_mlp_layer"] = args.n_mlp_layer
run["params/entropy"] = args.entropy
run["params/n_per_label_examples"] = args.n_per_label_examples


# --- Updated Regex: capture both val and test accuracies ---
pattern = re.compile(r"ind/([\w]+)_(val|test)_acc\s*│\s*([\d.]+)")

# Store as: results[dataset][split] = list of accs
results = defaultdict(lambda: defaultdict(list))

# --- Run command with 5 seeds ---
for seed in range(5):
    print(f"🚀 Running seed {seed}")
    full_cmd = f"python graphany/run.py dataset={args.dataset} total_steps={args.total_steps} " \
               f"n_hidden={args.n_hidden} n_mlp_layer={args.n_mlp_layer} entropy={args.entropy} " \
               f"n_per_label_examples={args.n_per_label_examples} seed={seed}"
    try:
        result = subprocess.run(full_cmd, shell=True, text=True, capture_output=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in seed {seed}:\n", e.stderr)
        output = e.stdout

    for match in pattern.finditer(output):
        dataset, split, acc = match.groups()
        acc = float(acc)
        results[dataset][split].append(acc)
        print(f"📈 {dataset} | {split}_acc | seed {seed}: {acc:.4f}")

# --- Custom exceptions ---
exclude_cora = {"cora"}
custom_exclude = {'cora', 'texa', 'tolo', 'roma', 'amzp', 'airu', 'acto', 'amzc', 'aire'}  # Add any datasets to exclude here

# Store per dataset stats
test_means = {}
test_stds = {}

# Log dataset-level stats to Neptune
for dataset, splits in results.items():
    test_accs = splits.get("test", [])
    if not test_accs:
        continue

    mean_test = np.mean(test_accs)
    std_test = np.std(test_accs)

    test_means[dataset] = mean_test
    test_stds[dataset] = std_test

    run[f"results/{dataset}/test_metric_mean"] = mean_test
    run[f"results/{dataset}/test_metric_std"] = std_test

    mean_val = np.mean(splits["val"])
    std_val = np.std(splits["val"])
    run[f"results/{dataset}/val_metric_mean"] = mean_val
    run[f"results/{dataset}/val_metric_std"] = std_val

# --- Filtered group-level metrics ---

def compute_group_stats(exclude_set):
    filtered_means = [mean for ds, mean in test_means.items() if ds not in exclude_set]
    filtered_stds = [std for ds, std in test_stds.items() if ds not in exclude_set]

    if filtered_means:
        mean_group = np.mean(filtered_means)
        std_group = np.mean(filtered_stds)
    else:
        mean_group = 0.0
        std_group = 0.0

    return mean_group, std_group

# (1) All datasets except cora
mean_excl_cora, std_excl_cora = compute_group_stats(exclude_cora)
run["results/test_metric_mean"] = mean_excl_cora
run["results/test_metric_std"] = std_excl_cora

# (2) All datasets except for those in custom exclusion list
mean_excl_custom, std_excl_custom = compute_group_stats(custom_exclude)
run["results/test_metric_mean20"] = mean_excl_custom
run["results/test_metric_std20"] = std_excl_custom

# --- Print summary ---
print("\n📊 Summary:")
print(f"Mean (excluding cora):        {mean_excl_cora:.4f}")
print(f"Std  (mean of stds):          {std_excl_cora:.4f}")
print(f"Mean (excluding {custom_exclude}): {mean_excl_custom:.4f}")
print(f"Std  (mean of stds):          {std_excl_custom:.4f}")

run.stop()
