import yaml

CITY_YAML_PATH = "cities.yaml"

def _load_cities():
    with open(CITY_YAML_PATH) as city_yaml_file:
        return yaml.load(city_yaml_file)

city_to_id = _load_cities()

def get_city_id(name):
    return city_to_id.get(name, 0)