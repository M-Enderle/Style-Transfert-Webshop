# Development

## Database

As we do not want to develop using the live database, we set up a docker container which simulates the exact same schema and allows to 
develop without the risk of losing or manipulating data.

### Requirements

- Docker

### Setup

1. Clone the repository
2. Open a terminal in the root directory of the repository
3. Run `docker build -t style-transfer-webshop-db -f development/database/Dockerfile .`
4. Run `sudo docker run --name mariadb3 -ti -d -p 3306:3306 style-transfer-webshop-db`

### Connecting to the database

The connection details are stored in default.toml in the project root. You can change them there if you want to use a different port or database name.

In live mode, the toml file is ignored and the connection details are read from the environment variables. This is done to allow the application to deploy automatically.

### Adding data

To add data to the database, you can use the `development/database/insert_data.sql` file. It contains some example data already.

## Maintainer

- [Moritz Enderle](https://mygit.th-deg.de/me04536)