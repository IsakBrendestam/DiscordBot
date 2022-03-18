import yaml

def load_config(filename):
    with open(filename) as f:
        return yaml.load(f, Loader=yaml.BaseLoader)

def save_config(config, filename):
    with open(filename, 'w+') as f:
        yaml.safe_dump(config, f, default_flow_style=False)
