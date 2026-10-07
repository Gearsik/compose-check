import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("compose_file")

args = parser.parse_args()

with open(args.compose_file) as file:
    compose_data = yaml.safe_load(file)

print(compose_data)