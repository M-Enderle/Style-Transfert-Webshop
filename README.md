# Style Transfer Webshop

## Introduction

This is a webshop for style transfer. It is a project for the course "AI Project" at the Deggendorf Institute of Technology.

## Installation

### Requirements

Docker is required to run the webshop. You can download it [here](https://www.docker.com/products/docker-desktop).

### Setup

1. Clone the repository
2. Open a terminal in the root directory of the repository
3. Run `docker build --build-arg -f Dockerfile . -t style-transfer-webshop`

#### Building in a specific branch

If you want to build a specific branch, you can use the `--build-arg` flag. For example, if you want to build the `develop` branch, you can run `docker build --build-arg BRANCH=develop -f Dockerfile . -t style-transfer-webshop`.

## Authors

- [Moritz Enderle](https://mygit.th-deg.de/me04536)
- [Florian Eder](https://mygit.th-deg.de/fe02174)
- [Amelie Kammerer](https://mygit.th-deg.de/ak23131)
- [Quirin Joshua Groszeibl](https://mygit.th-deg.de/qg23320)
