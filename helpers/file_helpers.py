from pathlib import Path
import yaml


def load_sql(file_name: str) -> str:
    """Загружает SQL из файла в папке data"""
    sql_file = Path(__file__).parent.parent / "data" / file_name
    with open(sql_file, mode="r", encoding="utf-8") as file:
        return file.read()

def load_yaml(file_name: str) -> dict:
    """Загружает YAML из файла в папке schemas"""
    yaml_file = Path(__file__).parent.parent / "schemas" / file_name
    with yaml_file.open(mode="r", encoding="utf-8") as file:
        return yaml.safe_load(file)