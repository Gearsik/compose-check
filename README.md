# Compose Check

Compose Check is a pretty small Python command-line tool that performs a number of pre-flight checks on Docker Compose files before they're used to start or deploy an app.

I had previously worked and encountered a few issues with Docker Compose files when working on some personal projects, and that was the main driving thought behind this idea. A Compose file can be valid YAML while still containing relatively simple configuration problems which only become obvious later. So with that in mind, I wanted to build a small tool which could catch a few of these problems earlier, and see how that would work.

ComposeCheck currently checks for:
- duplicate host ports across services
- missing relative bind-mount paths
- environment variables referenced using `${VARIABLE}` which are not available in the current shell or a local `.env` file

I should mention it's not intended to replace Docker's own Compose validation. The goal was simply to provide an additional check for a small number of common project-level problems.

## Running the project

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Then run ComposeCheck by passing it the path to a Compose file:
```bash
python compose_check.py path/to/compose.yaml
```

For example:
```bash
python compose_check.py compose_check_test.yaml
```

Note: `compose_check_test.yaml` is included as a simple test file. It references a local `./nginx` bind-mount path and a `${DB_PASSWORD}` environment variable, neither of which is included in the repository. To make the sample pass all checks, create the required `nginx` directory and provide `DB_PASSWORD` either in the current shell or in a local `.env` file.

If all checks pass, the program exits with status code `0`. If a problem is found, or the supplied file cannot be loaded correctly, it exits with status code `1`. These exit codes are mainly intended for automation or scripting rather than being displayed directly to the user.

## How it works

The supplied file is first loaded using PyYAML. ComposeCheck checks that the file exists, that the YAML can be parsed, and that a top-level `services` section is present.

It then works through the services and checks:
- whether the same host port is used more than once
- whether relative bind-mount paths beginning with `./` or `../` exist
- whether referenced environment variables exist in either the current process environment or a `.env` file beside the Compose file

## Testing and pre-commit checks

The project includes automated tests written with pytest:
```bash
pytest
```

The current test set covers successful and unsuccessful cases for the three main checks, as well as missing `services` section handling.

A pre-commit hook is also included. Before a commit is accepted, the hook automatically runs the full pytest test suite. If any test fails, the commit is blocked until the problem is corrected.

After cloning the repository, the hook can be enabled with:
```bash
pre-commit install
```

## Current limitations and future improvements

The tool currently focuses on a small set of common cases rather than the full Docker Compose specification. For example, port checking is based on the common short syntax, while bind-mount checking currently focuses on relative paths.

One of the main improvements I would make is to improve the way results are displayed. Rather than only showing one final success message, I would prefer each individual check to report its own `PASS` or `FAIL` result, together with more specific information when something goes wrong. Colour-coded terminal output could also make the result easier to understand at a glance.

I would also like to expand the automation further. The current pre-commit hook runs the automated test suite before allowing a commit, but a future version could make it easier to use ComposeCheck itself as a hook inside another project. Ideally, a failed check would immediately show which part of the Compose configuration caused the problem without requiring the user to run additional commands.

Finally, with more time I would expand support for additional Compose syntax and environment-variable formats beyond the smaller set currently handled by the project.