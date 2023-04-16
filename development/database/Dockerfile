FROM mariadb:latest

ENV MYSQL_ROOT_PASSWORD Test123456
ENV MYSQL_DATABASE StyleTransfer
ENV MYSQL_USER root_user
ENV MYSQL_PASSWORD Test123456

COPY ./development/database/ /docker-entrypoint-initdb.d/

EXPOSE 3306

CMD ["mysqld"]