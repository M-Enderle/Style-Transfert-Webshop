"""
This file contains the database models for the application.
"""

from sqlalchemy import VARCHAR, Column, DateTime, ForeignKey, Integer, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import Session

from sts.utils.utils import load_user_toml

MyBase = declarative_base()

user_data = load_user_toml()
host = user_data["database"]["host"]
port = int(user_data["database"]["port"])
username = user_data["database"]["username"]
password = user_data["database"]["password"]


class User(MyBase):
    """
    This class represents a user in the database.
    It has the following attributes:
     - id: the id of the user
     - username: the username of the user
     - password_hash: the hashed password of the user
     - email: the email of the user
    """

    __tablename__ = "User"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(VARCHAR(45), nullable=False, unique=True)
    name = Column(VARCHAR(45), nullable=False)
    email = Column(VARCHAR(45), nullable=False, unique=False)
    password_hash = Column(VARCHAR(512), nullable=False)

    orders = relationship("Order")

    def __repr__(self):
        return f"User {self.username} with email {self.email}."

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.email == other.email

    def get_plain_password(self):
        return self.password_hash

    def set_plain_password(self, password):
        self.password_hash = password


class Address(MyBase):
    """
    This class represents an address in the database.
    It has the following attributes:
     - id: the id of the address
     - street: the street of the address
     - city: the city of the address
     - state: the state of the address
     - zip: the zip code of the address
     - country: the country of the address
    """

    __tablename__ = "Address"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    full_name = Column(VARCHAR(128), nullable=False)
    street = Column(VARCHAR(45), nullable=False)
    city = Column(VARCHAR(45), nullable=False)
    zip = Column(VARCHAR(45), nullable=False)
    country = Column(VARCHAR(45), nullable=False)

    def __repr__(self):
        return f"Address for {self.full_name} at {self.street}, {self.city}, {self.zip}, {self.country}."

    def __str__(self):
        return self.__repr__()


class Order(MyBase):
    """
    This class represents an order in the database.
    It has the following attributes:
     - id: the id of the order
     - user_id: the id of the user who placed the order
     - address_id: the id of the address where the order is to be shipped
     - timestamp: the timestamp of the order
     - status: the status of the order
    """

    __tablename__ = "Order"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("Address.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    status = Column(VARCHAR(45), nullable=False)

    user = relationship("User", back_populates="orders")
    address = relationship("Address")

    def __repr__(self):
        return f"Order {self.id} for user {self.user.username} at address {self.address_id}."

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.user == other.user and self.address == other.address


def create_database() -> Engine:
    """
    This function creates the database and returns the engine.
    """

    _engine = create_engine(
        f"mysql+pymysql://{username}:{password}@{host}:{port}/StyleTransfer"
    )
    return _engine


def create_session() -> Session:
    """
    This function creates the session.
    """
    _session = sessionmaker(engine)
    return _session()


def add_users(credentails: dict):
    """
    This function adds all users from the credentials to the database.
    """

    session = create_session()
    for user in credentails["usernames"].keys():
        try:
            if not session.query(User).filter(User.username == user).first():
                session.add(
                    User(
                        username=user,
                        name=credentails["usernames"][user]["name"],
                        email=credentails["usernames"][user]["email"],
                        password_hash=credentails["usernames"][user]["password"],
                    )
                )
                session.commit()
                session.flush()
        except Exception as e:
            print(e)
            session.rollback()

    session.close()


engine = create_database()
