from compose_check import load_compose_data, check_duplicate_ports, check_bind_mounts, check_env_var
import pytest


def test_missing_services_section_exits(tmp_path):
    compose_file = tmp_path / "compose.yaml"

    compose_file.write_text("""
name: test
""")

    with pytest.raises(SystemExit) as error:
        load_compose_data(compose_file)

    assert error.value.code == 1

def test_duplicate_ports_detected():
    compose_data = {
        "services": {
            "nginx1": {
                "ports": ["8080:80"]
            },
            "nginx2": {
                "ports": ["8080:80"]
            }
        }
    }

    result = check_duplicate_ports(compose_data)
    assert result is False

def test_unique_ports_pass():
    compose_data = {
        "services": {
            "nginx1": {
                "ports": ["8080:80"]
            },
            "nginx2": {
                "ports": ["8081:80"]
            }
        }
    }

    result = check_duplicate_ports(compose_data)
    assert result is True

def test_missing_bind_mount_detected(tmp_path):
    compose_file = tmp_path / "compose.yaml"

    compose_data = {
        "services": {
            "nginx1": {
                "volumes": ["./missing-folder:/usr/share/nginx/html"]
            }
        }
    }

    result = check_bind_mounts(compose_data, compose_file)
    assert result is False


def test_existing_bind_mount_passes(tmp_path):
    compose_file = tmp_path / "compose.yaml"

    existing_folder = tmp_path / "nginx-data"
    existing_folder.mkdir()

    compose_data = {
        "services": {
            "nginx1": {
                "volumes": ["./nginx-data:/usr/share/nginx/html"]
            }
        }
    }

    result = check_bind_mounts(compose_data, compose_file)
    assert result is True

def test_missing_env_var_detected(tmp_path, monkeypatch):
    compose_file = tmp_path / "compose.yaml"

    monkeypatch.delenv("DB_PASSWORD", raising=False)

    compose_data = {
        "services": {
            "nginx1": {
                "environment": {
                    "DB_PASSWORD": "${DB_PASSWORD}"
                }
            }
        }
    }

    result = check_env_var(compose_data, compose_file)
    assert result is False


def test_env_var_in_shell_passes(tmp_path, monkeypatch):
    compose_file = tmp_path / "compose.yaml"

    monkeypatch.setenv("DB_PASSWORD", "test123")

    compose_data = {
        "services": {
            "nginx1": {
                "environment": {
                    "DB_PASSWORD": "${DB_PASSWORD}"
                }
            }
        }
    }

    result = check_env_var(compose_data, compose_file)
    assert result is True


def test_env_var_in_dotenv_passes(tmp_path, monkeypatch):
    compose_file = tmp_path / "compose.yaml"

    monkeypatch.delenv("DB_PASSWORD", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text("DB_PASSWORD=test123")

    compose_data = {
        "services": {
            "nginx1": {
                "environment": {
                    "DB_PASSWORD": "${DB_PASSWORD}"
                }
            }
        }
    }

    result = check_env_var(compose_data, compose_file)
    assert result is True