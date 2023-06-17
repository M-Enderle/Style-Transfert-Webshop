# Style Transfer Webshop

## Introduction

This is a webshop for style transfer merch. It is a project for the course "AI Project" at the Deggendorf Institute of Technology.

## Development

To keep the requirements for this project consistent, we use [poetry](https://python-poetry.org/) to manage the dependencies. You can install it with `pip install poetry`.

### Requirements

- [Python 3.10.*](https://www.python.org/) 
- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Setup Local

1. Clone the repository with `git clone https://mygit.th-deg.de/me04536/style-transfer-webshop.git`
2. Open a terminal in the root directory of the repository
3. Run `poetry install` to install the dependencies
    - If the python version is not matching, but the correct version is installed, use `poetry env use /path/to/preferred/python/version` to manually set the correct python version as default
4. Run `poetry shell` to activate the virtual environment

### Setup with Compose

1. Clone the repository with `git clone https://mygit.th-deg.de/me04536/style-transfer-webshop.git`
2. Open a terminal in the root directory of the repository
3. Run `docker-compose up --build` to build and run the services

### Compose for local development

For development, you can also run the services individually. To do so, run `docker-compose up --build <service>` in the root directory of the repository.
It is recommended to run the database and the ai service using the docker containers. The web service can be run locally using `python -m sts`.

### Adding dependencies

To add a dependency, run `poetry add <dependency>`. If you want to add a development dependency, run `poetry add --dev <dependency>`. 
Do not install any dependencies via pip as this will not update the `pyproject.toml` file.

### Linting

Before committing, please check your code with the following commands:

- `black src` to format the code (will fix errors automatically)
- `mypy src` to check for type errors

If you do not fix all errors, the commit will be rejected!

## Authors

- [Moritz Enderle](https://mygit.th-deg.de/me04536)
    - Project Owner
    - Lead Developer
    - Backend Development
    - Project Maintenance
    - Deployment
    - UI Design
- [Florian Eder](https://mygit.th-deg.de/fe02174)
    - AI Development
    - Backend Development
    - Streamlit Development
- [Amelie Kammerer](https://mygit.th-deg.de/ak23131)
    - Streamlit Development
    - User Area
    - Checkout Process
- [Quirin Joshua Groszeibl](https://mygit.th-deg.de/qg23320)
    - Streamlit Development
    - Lead Design
    - Product Design Process
