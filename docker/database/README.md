# Development

## Database

As we do not want to develop using the live database, we set up a docker container which simulates the exact same schema and allows to 
develop without the risk of losing or manipulating data.

### Requirements

- Docker

### Setup

1. Clone the repository
2. Open a terminal in the root directory of the repository
3. Run `docker build -t database -f docker/database/Dockerfile .`
4. Run `docker run --name mariadb3 -ti -d -p 3306:3306 database`

### Connecting to the database

If you developing without compose, change the connection details in `default.toml` to `localhost` as host.

### Adding data

To add data to the database, you can use the `docker/database/insert_data.sql` file. It contains some example data already.

## Maintainer

- [Moritz Enderle](https://mygit.th-deg.de/me04536)