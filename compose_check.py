import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("compose_file")

args = parser.parse_args()

with open(args.compose_file) as file:
    compose_data = yaml.safe_load(file)

host_ports = set()

for service in compose_data['services']:
    service_config = compose_data["services"][service]

    if 'ports' in service_config:
        for every_port in (service_config["ports"]):
            port_mapping = every_port.split(':')

            current_port = port_mapping[0]

            if current_port in host_ports:
                print('duplicate host ports on 2 different services, please pick unique host port numbers')
            else:
                host_ports.add(current_port)
