import argparse
import yaml
import os
import sys 
from pathlib import Path

def load_compose_data(compose_path):

    try: 
        with open(compose_path) as file:
            compose_data = yaml.safe_load(file)

        if not isinstance(compose_data, dict) or 'services' not in compose_data:
            print(f'ERROR: Compose file does not contain a services section: {compose_path}')
            sys.exit(1)

        return compose_data
            
    except FileNotFoundError:
        print(f'ERROR: Compose file not found: {compose_path}')
        sys.exit(1)
            
    except yaml.YAMLError:
        print(f'ERROR: Invalid YAML in Compose file: {compose_path}')
        sys.exit(1)


def check_duplicate_ports(compose_data):
    host_ports = set()
    check_passed = True

    for service in compose_data['services']:
        service_config = compose_data["services"][service]
        if 'ports' in service_config:
            for every_port in service_config['ports']:
                port_mapping = every_port.split(':')

                current_port = port_mapping[0]

                if current_port in host_ports:
                    print('duplicate host ports on 2 different services, please pick unique host port numbers')
                    check_passed = False
                else:
                    host_ports.add(current_port)

    return check_passed

def check_bind_mounts(compose_data, compose_path):
    bind_mounts_ok = True

    for service in compose_data['services']:
        service_config = compose_data["services"][service]
        if 'volumes' in service_config:
            for every_volume in service_config['volumes']:
                volumes_binding = every_volume.split(':')
                volumes_path = volumes_binding[0]

                bind_path = Path(volumes_path)
                full_path = compose_path.parent / bind_path

                if volumes_path.startswith(('./', '../')) and not full_path.exists():
                    print('the path file doesnt exist or the path is incorrect')
                    bind_mounts_ok = False

    return bind_mounts_ok

def check_env_var(compose_data, compose_path):
    env_var_ok = True

    for service in compose_data['services']:
        service_config = compose_data["services"][service]
        if 'environment' in service_config:
            for every_env in service_config['environment']:

                found = False
                env_var = service_config['environment'][every_env]

                if env_var.startswith('${') and env_var.endswith('}'):
                    env_value = env_var.removeprefix("${").removesuffix("}")

                    if env_value not in os.environ:
                        env_file = compose_path.parent / '.env'

                        if env_file.exists():
                            with open(env_file) as file:
                                env_file_data = file.read().splitlines()

                                for line in env_file_data:
                                    lines = line.split('=', 1)

                                    if lines[0] == env_value:
                                        found = True

                                if not found:
                                    print(f'The file is missing environment variable: {env_value}')
                                    env_var_ok = False

                        else:
                            print(f'Missing environment variable: {env_value} (.env file not found)')
                            env_var_ok = False

    return env_var_ok

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("compose_file")

    args = parser.parse_args()
    compose_path = Path(args.compose_file).resolve()

    compose_data = load_compose_data(compose_path)

    ports_ok = check_duplicate_ports(compose_data)
    bind_mounts_ok = check_bind_mounts(compose_data, compose_path)
    env_var_ok = check_env_var(compose_data, compose_path)

    if ports_ok and bind_mounts_ok and env_var_ok:
        print('PASS: No configuration issues found')
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()