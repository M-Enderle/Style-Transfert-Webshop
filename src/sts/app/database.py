"""
This file contains the database models for the application.
"""

from sqlalchemy import VARCHAR, Column, DateTime, ForeignKey, Integer, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError

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
        """
        This function returns the password of the user.
        """
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
    street = Column(VARCHAR(45), nullable=False)
    city = Column(VARCHAR(45), nullable=False)
    state = Column(VARCHAR(45), nullable=False)
    zip = Column(VARCHAR(45), nullable=False)
    country = Column(VARCHAR(45), nullable=False)

    def __repr__(self):
        return f"Address {self.street}, {self.city}, {self.state}, {self.zip}, {self.country}."

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.street == other.street
            and self.city == other.city
            and self.state == other.state
            and self.zip == other.zip
            and self.country == other.country
        )


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


def get_user_information(username):
    """
    Retrieve user information for a given username.
    Args:
        username (str): The username of the user.
    Returns:
        list: A list containing a dictionary with user information. The dictionary includes the following keys:
              - "Username": The username of the user.
              - "Name": The name of the user.
              - "E-mail": The email address of the user.
    Raises:
        None.
    """
    session = create_session()
    try:
        user = session.query(User).filter_by(username=username).one()
        session.close()
        return {"Username": user.username, "Name": user.name, "E-mail": user.email}
    except Exception as e:
        # If the user is not found
        session.close()
        return [e]


def get_order_information(username):
    """
    Retrieve order information for a given user.
    Args:
        username (str): The username of the user.
    Returns:
    list: A list of dictionaries containing order information.
        Each dictionary represents an order and includes the following keys:
              - "Order time": Timestamp indicating when the order was made.
              - "Status": Current status of the order.
              - "Address": String representation of the order's address
                in the format "country, state, zip, city, street".
    """
    session = create_session()
    try:
        user = session.query(User).filter_by(username=username).one()
        session.close()
        orders_info = []
        for order in user.orders:
            address = order.address
            address_str = f"{address.country}, {address.state}, \
                {address.zip}, {address.city}, {address.street}"
            orders_info.append(
                {
                    "Order time": order.timestamp,
                    "Status": order.status,
                    "Address": address_str,
                }
            )
        return orders_info
    except Exception as e:
        session.close()
        return [e]


def check_if_order(username):
    """
    Check if a user has any orders.
    Args: username(str): The username of the user to check.
    Returns: bool: Treu if the user has at least one orther, False otherwise.
    Raises: None
    """
    session = create_session()

    try:
        user = session.query(User).filter_by(username=username).one()
        orders = user.orders
        session.close()
        return len(orders) > 0
    except IntegrityError:
        # no order found
        session.close()
        return False
    except Exception as e:
        session.close()
        return False


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
        except IntegrityError:
            session.rollback()
            return False
        except Exception as e:
            session.rollback()
            return False

    session.close()
    return True


engine = create_database()
