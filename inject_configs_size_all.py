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

# Define training sets
train_sets1 = [
    [],
    ['Texas', 'Tolokers'],
    ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ['Citeseer', 'AmzComp', 'AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ['Citeseer', 'AmzComp', 'AmzPhoto', 'Deezer', 'Texas', 'AirUS', 'Roman', 'Tolokers'],
]

train_sets2 = [
    [],
    ['Texas', 'Tolokers'],
    ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ['AmzComp', 'AmzPhoto', 'Texas', 'AirUS', 'Roman', 'Tolokers'],
    ['Citeseer', 'AmzComp', 'AmzPhoto', 'Deezer', 'Texas', 'AirUS', 'Roman', 'Tolokers'],
]

train_sets3 = [
    [],
    ['Texas', 'Tolokers'],
    ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ['Citeseer', 'AmzPhoto', 'Texas', 'Actor', 'Roman', 'Tolokers'],
    ['Citeseer', 'AmzComp', 'AmzPhoto', 'Deezer', 'Texas', 'Actor', 'Roman', 'Tolokers'],
]

train_sets4 = [
    [],
    ['Texas', 'Tolokers'],
    ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ['AmzPhoto', 'Deezer', 'Texas', 'Actor', 'Roman', 'Tolokers'],
    ['Citeseer', 'AmzComp', 'AmzPhoto', 'Deezer', 'Texas', 'Actor', 'Roman', 'Tolokers'],
]

train_sets5 = [
    [],
    ['Texas', 'Tolokers'],
    ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ['Citeseer', 'AmzPhoto', 'Texas', 'AirEU', 'Roman', 'Tolokers'],
    ['Citeseer', 'AmzPhoto', 'Deezer', 'Texas', 'AirEU', 'Actor', 'Roman', 'Tolokers'],
]

train_sets6 = [
    [],
    ['Roman', 'Tolokers'],
    ['Texas', 'Actor', 'Roman', 'Tolokers'],
    ['AmzPhoto', 'Texas', 'AirEU', 'Actor', 'Roman', 'Tolokers'],
    ['Citeseer', 'AmzPhoto', 'Deezer', 'Texas', 'AirEU', 'Actor', 'Roman', 'Tolokers'],
]

train_sets7 = [
    [],
    ['Texas', 'Tolokers'],
    ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ['AmzComp', 'AmzPhoto', 'Texas', 'AirUS', 'Roman', 'Tolokers'],
    ['AmzComp', 'AmzPhoto', 'Texas', 'AirUS', 'AirEU', 'Actor', 'Roman', 'Tolokers'],
]

train_sets8 = [
    [],
    ['Texas', 'Tolokers'],
    ['AmzPhoto', 'Texas', 'Roman', 'Tolokers'],
    ['AmzPhoto', 'Texas', 'AirUS', 'Actor', 'Roman', 'Tolokers'],
    ['AmzComp', 'AmzPhoto', 'Texas', 'AirUS', 'AirEU', 'Actor', 'Roman', 'Tolokers'],
]

train_sets_list = [
    train_sets1, train_sets2, train_sets3, train_sets4,
    train_sets5, train_sets6, train_sets7, train_sets8
]

# Inject configuration
for idx, train_sets in enumerate(train_sets_list):
    for train_set in train_sets:
        train_size = len(train_set) + 1
        name = f"train{idx:02d}_size{train_size:02d}"

        train_with_cora = ["Cora"] + train_set
        eval_set = [d for d in all_datasets if d not in train_sets[-1]]

        config_data["_dataset_lookup"][name] = {
            "train": train_with_cora,
            "eval": eval_set,
            "train_idx": idx,
            "train_size": train_size,
        }

# Save back to YAML
with open(path, "w") as f:
    yaml.dump(config_data, f, sort_keys=False)

print(f"✅ Injected configuration groups into {path}")
