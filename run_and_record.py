import subprocess
import re
import neptune
import numpy as np
from collections import defaultdict
from argparse import ArgumentParser

# --- CLI args ---
parser = ArgumentParser()
parser.add_argument("--project", dest="project", type=str, required=True)
parser.add_argument("--mode", dest="mode", type=str, required=True)
parser.add_argument("--source9", dest="source9", type=str, required=False)
parser.add_argument("--source7", dest="source7", type=str, required=False)
args = parser.parse_args()

# --- Neptune setup ---
API_TOKEN = "eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiI3ZTZjOWE3Yi0xOGU3LTQwOTEtYWIzNS1hYzRmOGZiMjhhNTcifQ=="
run = neptune.init_run(project=args.project, api_token=API_TOKEN)
run["mode"] = args.mode
run["source9"] = args.source9
run["source7"] = args.source7

# --- Commands ---
commands = {
    "Aux": f"python graphany/run.py dataset={args.mode}_Aux total_steps=500 n_hidden=64 n_mlp_layer=1 entropy=2 n_per_label_examples=5",
    "Cora": f"python graphany/run.py dataset={args.mode}_Cora total_steps=500 n_hidden=64 n_mlp_layer=1 entropy=2 n_per_label_examples=5"
}

# --- Regex to extract test accuracy
pattern = re.compile(r"ind/([\w]+)_test_acc\s*│\s*([\d.]+)")

# --- Store results
results = {
    "Aux": defaultdict(list),
    "Cora": defaultdict(list)
}
aggregated = {
    "Aux": {},
    "Cora": {},
    "Delta": {}
}

# --- Run seeds for both commands ---
for label, cmd in commands.items():
    for seed in range(5):
        print(f"Running {label} | seed {seed}")
        full_cmd = f"{cmd} seed={seed}"
        try:
            result = subprocess.run(full_cmd, shell=True, text=True, capture_output=True, check=True)
            output = result.stdout
        except subprocess.CalledProcessError as e:
            print("Error:\n", e.stderr)
            output = e.stdout

        for match in pattern.finditer(output):
            dataset, acc = match.groups()
            results[label][dataset].append(float(acc))

# --- Aggregate statistics and log to Neptune ---
all_means_aux = []
all_stds_aux = []
all_means_cora = []
all_stds_cora = []

for dataset in sorted(set(results["Aux"]) | set(results["Cora"])):
    accs_aux = results["Aux"].get(dataset, [])
    accs_cora = results["Cora"].get(dataset, [])

    mean_aux = np.mean(accs_aux) if accs_aux else 0.0
    std_aux = np.std(accs_aux) if accs_aux else 0.0
    mean_cora = np.mean(accs_cora) if accs_cora else 0.0
    std_cora = np.std(accs_cora) if accs_cora else 0.0
    delta = mean_aux - mean_cora

    aggregated["Aux"][dataset] = {"mean": mean_aux, "std": std_aux}
    aggregated["Cora"][dataset] = {"mean": mean_cora, "std": std_cora}
    aggregated["Delta"][dataset] = delta

    run[f"results/{dataset}/Aux_mean"] = mean_aux
    run[f"results/{dataset}/Aux_std"] = std_aux
    run[f"results/{dataset}/Cora_mean"] = mean_cora
    run[f"results/{dataset}/Cora_std"] = std_cora
    run[f"results/{dataset}/delta"] = delta

    all_means_aux.append(mean_aux)
    all_stds_aux.append(std_aux)
    all_means_cora.append(mean_cora)
    all_stds_cora.append(std_cora)

# --- Overall metrics ---
global_mean_aux = np.mean(all_means_aux)
global_std_aux = np.mean(all_stds_aux)
global_mean_cora = np.mean(all_means_cora)
global_std_cora = np.mean(all_stds_cora)
global_delta = global_mean_aux - global_mean_cora

run["results/global/Aux_mean"] = global_mean_aux
run["results/global/Aux_std"] = global_std_aux
run["results/global/Cora_mean"] = global_mean_cora
run["results/global/Cora_std"] = global_std_cora
run["results/global/delta"] = global_delta

print("\n📊 Summary:")
print(f"Aux overall mean:  {global_mean_aux:.4f}")
print(f"Aux overall std:  {global_std_aux:.4f}")
print(f"Cora overall mean: {global_mean_cora:.4f}")
print(f"Aux overall std:  {global_std_cora:.4f}")
print(f"Delta (Aux - Cora): {global_delta:.4f}")

run.stop()
