# Style Transfer Webshop

## Introduction

This is a webshop for style transfer. It is a project for the course "AI Project" at the Deggendorf Institute of Technology.

## Development

To keep the requirements for this project consistent, we use [poetry](https://python-poetry.org/) to manage the dependencies. You can install it with `pip install poetry`.

### Requirements

- Python 3.10.11
- Poetry

### Setup

1. Clone the repository
2. Open a terminal in the root directory of the repository
3. Run `poetry install` to install the dependencies
    - If the python version is not matching, but the correct version is installed, use `poetry env use /path/to/preferred/python/version` to manually set the correct python version as default
4. Run `poetry shell` to activate the virtual environment

### Adding dependencies

To add a dependency, run `poetry add <dependency>`. If you want to add a development dependency, run `poetry add --dev <dependency>`. 
Do not install any dependencies via pip as this will not update the `pyproject.toml` file.

## Docker

### Requirements

Docker is required to run the webshop. You can download it [here](https://www.docker.com/products/docker-desktop).

### Setup

1. Clone the repository
2. Open a terminal in the root directory of the repository
3. Run `docker build -t style-transfer-webshop -f Dockerfile .`

## Authors

- [Moritz Enderle](https://mygit.th-deg.de/me04536)
- [Florian Eder](https://mygit.th-deg.de/fe02174)
- [Amelie Kammerer](https://mygit.th-deg.de/ak23131)
- [Quirin Joshua Groszeibl](https://mygit.th-deg.de/qg23320)
