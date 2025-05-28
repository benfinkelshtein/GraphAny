import yaml
from itertools import combinations

path = "configs/data.yaml"

all_datasets = [
    'Arxiv', 'Cora', 'FCora', 'Citeseer', 'DBLP', 'Pubmed', 'Wiki', 'WkCS', 'Reddit', 'Product',
    'AmzComp', 'AmzPhoto', 'BlogCatalog', 'LastFMAsia', 'Deezer', 'CoCS', 'CoPhysics', 'Cornell',
    'Texas', 'Wisconsin', 'AirBrazil', 'AirUS', 'AirEU', 'Chameleon', 'Actor', 'Squirrel', 'Roman',
    'AmzRatings', 'Minesweeper', 'Tolokers', 'Questions'
]

# Load existing YAML
with open(path, "r") as f:
    config_data = yaml.safe_load(f)

# Ensure the lookup dictionary exists
if "_dataset_lookup" not in config_data:
    config_data["_dataset_lookup"] = {}

# Candidate sets
candidates = {
    ("0266", "0008"): ['Citeseer', 'AmzComp', 'AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ("0266", "0025"): ['AmzComp', 'AmzPhoto', 'Texas', 'AirUS', 'Roman', 'Tolokers'],

    ("0285", "0047"): ['Citeseer', 'AmzPhoto', 'Texas', 'Actor', 'Roman', 'Tolokers'],
    ("0285", "0055"): ['AmzPhoto', 'Deezer', 'Texas', 'Actor', 'Roman', 'Tolokers'],

    ("0700", "0068"): ['Citeseer', 'AmzPhoto', 'Texas', 'AirEU', 'Roman', 'Tolokers'],
    ("0700", "0082"): ['AmzPhoto', 'Texas', 'AirEU', 'Actor', 'Roman', 'Tolokers'],

    ("1066", "0089"): ['AmzComp', 'AmzPhoto', 'Texas', 'AirUS', 'Roman', 'Tolokers'],
    ("1066", "0108"): ['AmzPhoto', 'Texas', 'AirUS', 'Actor', 'Roman', 'Tolokers']
}

combo_counter = 0

for (source_counter9, source_counter7), candidate_datasets in candidates.items():
    all_combinations = list(combinations(candidate_datasets, 4))

    for combo in all_combinations:
        name_aux = f"{combo_counter:04d}_Aux"
        name_cora = f"{combo_counter:04d}_Cora"

        train_with_aux = ["Cora"] + list(combo)
        eval_set = [d for d in all_datasets if d not in train_with_aux]

        config_data["_dataset_lookup"][name_aux] = {
            "train": train_with_aux,
            "eval": eval_set,
            "source9": source_counter9,
            "source7": source_counter7
        }
        config_data["_dataset_lookup"][name_cora] = {
            "train": ["Cora"],
            "eval": eval_set,
            "source9": source_counter9,
            "source7": source_counter7
        }

        combo_counter += 1

# Write back to YAML
with open(path, "w") as f:
    yaml.dump(config_data, f, sort_keys=False)

print(f"✅ Injected {combo_counter} configuration groups into {path}")
