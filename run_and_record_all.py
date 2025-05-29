import subprocess
import re
import neptune
import numpy as np
from collections import defaultdict
from argparse import ArgumentParser

# --- CLI args ---
parser = ArgumentParser()
parser.add_argument("--project", dest="project", type=str, required=True)
parser.add_argument("--mode", dest="mode", type=int, required=True)
parser.add_argument("--size", dest="size", type=int, required=True)
args = parser.parse_args()

# --- Neptune setup ---
API_TOKEN = "eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiI3ZTZjOWE3Yi0xOGU3LTQwOTEtYWIzNS1hYzRmOGZiMjhhNTcifQ=="
run = neptune.init_run(project=args.project, api_token=API_TOKEN)
run["mode"] = args.mode
run["size"] = args.size

# --- Regex to extract test accuracy
pattern = re.compile(r"ind/([\w]+)_test_acc\s*│\s*([\d.]+)")

# --- Run seeds for both commands ---
results = defaultdict(list)
cmd = f"python graphany/run.py dataset=train{args.mode:02d}_size{args.size:02d} total_steps=500 n_hidden=64 n_mlp_layer=1 entropy=2 n_per_label_examples=5"
for seed in range(5):
    print(f"seed {seed}")
    full_cmd = f"{cmd} seed={seed}"
    try:
        result = subprocess.run(full_cmd, shell=True, text=True, capture_output=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        print("Error:\n", e.stderr)
        output = e.stdout

    for match in pattern.finditer(output):
        dataset, acc = match.groups()
        results[dataset].append(float(acc))

# --- Aggregate statistics and log to Neptune ---
all_means = []
all_stds = []

for dataset in sorted(set(results)):
    accs = results.get(dataset, [])

    mean = np.mean(accs) if accs else 0.0
    std = np.std(accs) if accs else 0.0

    run[f"results/{dataset}/mean"] = mean
    run[f"results/{dataset}/std"] = std

    all_means.append(mean)
    all_stds.append(std)

# --- Overall metrics ---
global_mean = np.mean(all_means)
global_std = np.mean(all_stds)

run["results/global/mean"] = global_mean
run["results/global/std"] = global_std

print("\n📊 Summary:")
print(f"Aux overall mean:  {global_mean:.4f}")
print(f"Aux overall std:  {global_std:.4f}")

run.stop()
