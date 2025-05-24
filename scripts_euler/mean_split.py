import os
import shutil
import math
from itertools import combinations

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

## Grid arguments
candidate_datasets = [
    "Citeseer", "AmzComp", "LastFMAsia", "AmzPhoto", "Deezer",
    "Texas", "AirUS", "AirEU", "Chameleon", "Actor", "Squirrel",
    "Roman", "Tolokers",
    # "Minesweeper", "Questions", "AirBrazil", "Wisconsin", "Cornell", "DBLP",
    # "Pubmed", "AmzRatings", -- consider
]
project = 'GFM/GraphAny4'
num_combinations = len(list(combinations(candidate_datasets, 8)))


commands = []
command = []
for idx in range(num_combinations):
    commands.append(f'--project {project} --mode {idx:04d}')

# Divide the commands into equal-sized batches
batch_size = math.ceil(len(commands) / 10)  # dict_batch_size[dataset]
batches = [commands[i:i + batch_size] for i in range(0, len(commands), batch_size)]
print(f'batches: {len(batches)}')

# Write each batch to a separate file
command_folder = os.path.join(ROOT_DIR, 'scripts_euler', 'grid')
if os.path.exists(command_folder):
    shutil.rmtree(command_folder)
os.mkdir(command_folder)

for i, batch in enumerate(batches, start=1):
    with open(os.path.join(command_folder, f'batch_{i}.txt'), 'w') as f:
        for command in batch:
            f.write(command + '\n')
