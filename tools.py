import yaml


def read_yml_file(file_path: str) -> dict:
    with open(file_path, "r") as f:
        content = yaml.safe_load(f)
    return content
