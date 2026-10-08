import argparse
import yaml
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