import os
import shutil
import math
from itertools import combinations

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# === Dataset definitions with names for traceability ===

project = 'GFM/GraphAny-all-Size'
commands = []
combo_counter = 0

# === Generate --mode <idx> command for each combination ===

for idx in range(8):
    for train_size in [1, 3, 5, 7, 9]:
        commands.append(
            f'--project {project} --size {train_size:02d} --mode {idx:02d}'
        )
        combo_counter += 1

# === Divide commands into batches ===

batch_size = math.ceil(len(commands) / 10)
batches = [commands[i:i + batch_size] for i in range(0, len(commands), batch_size)]

print(f'✅ Total combinations: {combo_counter}')
print(f'📦 Number of batches: {len(batches)}')

# === Write to files ===

command_folder = os.path.join(ROOT_DIR, 'scripts_euler', 'grid')
if os.path.exists(command_folder):
    shutil.rmtree(command_folder)
os.makedirs(command_folder)

for i, batch in enumerate(batches, start=1):
    with open(os.path.join(command_folder, f'batch_{i}.txt'), 'w') as f:
        for command in batch:
            f.write(command + '\n')
