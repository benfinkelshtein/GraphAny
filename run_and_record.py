import subprocess
import re
import neptune
import os
import numpy as np
from collections import defaultdict

# Initialize Neptune
API_TOKEN = "..."  # keep this secure
run = neptune.init_run(project="GraphAny", api_token=API_TOKEN)

# Set Neptune tag
run["setup"] = "Multi"

# Base command
base_command = "python graphany/run.py dataset=Multi total_steps=1000 " \
               "n_hidden=32 n_mlp_layer=2 entropy=1 n_per_label_examples=5"

# Regex pattern
pattern = re.compile(r"ind/([\w]+)_test_acc\s*│\s*([\d.]+)")

# Store results for aggregation
results_by_dataset = defaultdict(list)

# Run multiple seeds
for idx in range(5):
    cmd = base_command + f" seed={idx}"
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)
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
