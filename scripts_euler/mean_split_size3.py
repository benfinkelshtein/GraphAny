import os
import shutil
import math
from itertools import combinations

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# === Dataset definitions with names for traceability ===

candidates = {
    ("0266", "0008", "0014"): ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    # ("0266", "0025", "0027"): ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],

    # ("0285", "0047", "0042"): ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    # ("0285", "0055", "0053"): ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],

    # ("0700", "0068", "0072"): ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ("0700", "0082", "0088"): ['Texas', 'Actor', 'Roman', 'Tolokers'],

    # ("1066", "0089", "0102"): ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    # ("1066", "0108", "0110"): ['AmzPhoto', 'Texas', 'Roman', 'Tolokers']
}

project = 'GFM/GraphAny-Size3'
commands = []
combo_counter = 0

# Optional size flag (if you intend to use it)
size = 4  # Default to 6 as used in combinations

# === Generate --mode <idx> command for each combination ===

for (source_counter9, source_counter7, source_counter5), candidate_datasets in candidates.items():
    all_combos = list(combinations(candidate_datasets, size))
    for _ in all_combos:
        commands.append(
            f'--project {project} --source9 {source_counter9} --source7 {source_counter7}'
            f'--source5 {source_counter5} --mode {combo_counter:04d}'
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
