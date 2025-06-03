import itertools
import os
import shutil
import math
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The new expected hps to be passed as key=value (Hydra-style)
arg_names = [
    'dataset', 'total_steps', 'n_hidden', 'n_mlp_layer', 'entropy', 'n_per_label_examples'
]

# You can tune these based on your needs
def get_grid(dataset_name: str):
    grid = [
        [dataset_name],        # dataset
        [500, 1000, 1500],                # total_steps
        [32, 64, 128],            # n_hidden
        [1, 2, 3],                # n_mlp_layer
        [1, 2],            # entropy
        [5],                # n_per_label_examples
    ]
    return grid


commands = []
for dataset in ["size1", "size3", "size5", "size7", "size9"]:
    for args in itertools.product(*get_grid(dataset)):
        command_str = ' '.join([f"{key}={value}" for key, value in zip(arg_names, args)])
        cmd = f"--project GFM/Multi-GraphAny --command '{command_str}'"
        commands.append(cmd)

print(f"Total commands generated: {len(commands)}")

# Split into batches
batch_size = math.ceil(len(commands) / 12)
batches = [commands[i:i + batch_size] for i in range(0, len(commands), batch_size)]
print(f"Batches: {len(batches)}")

# Create output folder
command_folder = os.path.join(ROOT_DIR, 'scripts_euler', 'grid')
if os.path.exists(command_folder):
    shutil.rmtree(command_folder)
os.makedirs(command_folder)

# Write batches to files
for i, batch in enumerate(batches, start=1):
    with open(os.path.join(command_folder, f'batch_{i}.txt'), 'w') as f:
        for command in batch:
            f.write(command + '\n')
