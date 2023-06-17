# Development

## Database

As we do not want to develop using the live database, we set up a docker container which simulates the exact same schema and allows to 
develop without the risk of losing or manipulating data.

### Requirements

- Docker
- Compose

### Setup

To setup the database, run the following command in the project root:

```bash
docker-compose up --build database
```

### Adding data

To add data to the database, you can use the `docker/database/insert_data.sql` file. It contains some example data already.

## Maintainer

- [Moritz Enderle](https://mygit.th-deg.de/me04536)