import argparse

parser = argparse.ArgumentParser()
parser.add_argument("compose_file")

args = parser.parse_args()
print(args.compose_file)