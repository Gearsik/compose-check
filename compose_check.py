import argparse
import yaml
import os 
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("compose_file")

args = parser.parse_args()
compose_path = Path(args.compose_file).resolve()

with open(args.compose_file) as file:
    compose_data = yaml.safe_load(file)

host_ports = set()

for service in compose_data['services']:
    service_config = compose_data["services"][service]

    if 'ports' in service_config:
        for every_port in (service_config['ports']):
            port_mapping = every_port.split(':')

            current_port = port_mapping[0]

            if current_port in host_ports:
                print('duplicate host ports on 2 different services, please pick unique host port numbers')
            else:
                host_ports.add(current_port)

    if 'volumes' in service_config:
        for every_volume in (service_config['volumes']):
            volumes_binding = every_volume.split(':')
            volumes_path = volumes_binding[0]

            bind_path = Path(volumes_path)
            full_path = compose_path.parent/bind_path

            if volumes_path.startswith(('./', '../')) and not full_path.exists():
                print('the path file doesnt exist or the path is incorrect')

    if 'environment' in service_config:
        for every_env in service_config['environment']:

            found = False
            env_var = service_config['environment'][every_env]

            if env_var.startswith('${') and env_var.endswith('}'):
                env_value = env_var.removeprefix("${").removesuffix("}")

                if env_value not in os.environ:
                    env_file = compose_path.parent/'.env'

                    if env_file.exists():
                        with open(env_file) as file:
                            env_file_data = file.read().splitlines()

                            for line in env_file_data:
                                lines = line.split('=', 1)

                                if lines[0] == env_value:
                                    found = True

                            if not found:
                                print(f'The file is missing environment variable: {env_value}')

                    else:
                        print(f'Missing environment variable: {env_value} (.env file not found)')