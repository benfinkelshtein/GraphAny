import random
import yaml
from itertools import combinations

path = "configs/data.yaml"

# === Configuration ===

all_datasets = ['Arxiv', 'Cora', 'FCora', 'Citeseer', 'DBLP', 'Pubmed', 'Wiki', 'WkCS', 'Reddit', 'Product',
                'AmzComp', 'AmzPhoto', 'BlogCatalog', 'LastFMAsia', 'Deezer', 'CoCS', 'CoPhysics', 'Cornell',
                'Texas', 'Wisconsin', 'AirBrazil', 'AirUS', 'AirEU', 'Chameleon', 'Actor', 'Squirrel', 'Roman',
                'AmzRatings', 'Minesweeper', 'Tolokers', 'Questions']


# All candidate datasets excluding Cora
candidate_datasets = [
    "Citeseer", "AmzComp", "LastFMAsia", "AmzPhoto", "Deezer",
    "Texas", "AirUS", "AirEU", "Chameleon", "Actor", "Squirrel",
    "Roman", "Tolokers",
    # "Minesweeper", "Questions", "AirBrazil", "Wisconsin", "Cornell", "DBLP",
    # "Pubmed", "AmzRatings", -- consider
]

# Load existing data.yml
with open(path, "r") as f:
    config_data = yaml.safe_load(f)

# Sample combinations
random.seed(42)
all_combinations = list(combinations(candidate_datasets, 8))
print(f'Number of combinations: {len(all_combinations)}')
sampled_combos = all_combinations #random.sample(all_combinations, N_CONFIGS)

# Add configurations
for i, combo in enumerate(sampled_combos):
    name_aux = f"{i:04d}_Aux"
    name_cora = f"{i:04d}_Cora"
    train_with_aux = ["Cora"] + list(combo)
    eval_set = [d for d in all_datasets if d not in train_with_aux]

    config_data["_dataset_lookup"][name_aux] = {
        "train": train_with_aux,
        "eval": eval_set
    }
    config_data["_dataset_lookup"][name_cora] = {
        "train": ["Cora"],
        "eval": eval_set
    }

# Save updated data.yml
with open(path, "w") as f:
    yaml.dump(config_data, f)

print(f"✅ Injected the configuration pairs into {path}")