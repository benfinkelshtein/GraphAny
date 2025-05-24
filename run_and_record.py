import subprocess
import re
import neptune
import numpy as np
from collections import defaultdict
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--project", dest="project", type=str, required=True)
parser.add_argument("--mode", dest="mode", type=str, required=True)
args = parser.parse_args()

# Initialize Neptune
API_TOKEN = "eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiI3ZTZjOWE3Yi0xOGU3LTQwOTEtYWIzNS1hYzRmOGZiMjhhNTcifQ=="
run = neptune.init_run(project=args.project, api_token=API_TOKEN)

# Set Neptune tag
run["mode"] = args.mode

# Base command
base_command = f"python graphany/run.py dataset={args.mode} " \
               "total_steps=500 n_hidden=64 n_mlp_layer=1 entropy=2 n_per_label_examples=5"

# Regex pattern
pattern = re.compile(r"ind/([\w]+)_test_acc\s*│\s*([\d.]+)")

# Store results for aggregation
results_by_dataset = defaultdict(list)

# Run multiple seeds
for idx in range(5):
    cmd = base_command + f" seed={idx}"
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)
        print("Success:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error output:\n", e.stderr)
        print("Standard output before error:\n", e.stdout)
    output = result.stdout

    for match in pattern.finditer(output):
        dataset, acc = match.groups()
        acc = float(acc)
        results_by_dataset[dataset].append(acc)
        run[f"results/{dataset}/seed_{idx}"] = acc  # optional: store per-seed

# Compute mean and std per dataset
for dataset, accs in results_by_dataset.items():
    mean = np.mean(accs)
    std = np.std(accs)
    run[f"results/{dataset}/mean"] = mean
    run[f"results/{dataset}/std"] = std

# Optionally log global average across datasets
all_means = [np.mean(v) for v in results_by_dataset.values()]
all_stds = [np.std(v) for v in results_by_dataset.values()]
run["results/mean"] = np.mean(all_means)
run["results/std"] = np.mean(all_stds)
