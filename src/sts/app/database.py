"""
This file contains the database models for the application.
"""

from datetime import datetime

from sqlalchemy import (
    DECIMAL,
    VARCHAR,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    create_engine,
)
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
        """
        This function returns the representation of the user.
        """
        return f"User {self.username} with email {self.email}."

    def __str__(self):
        """
        This function returns the string representation of the user.
        """
        return self.__repr__()

    def __eq__(self, other):
        """
        This function checks if two users are equal.
        """
        return self.email == other.email


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

    def __repr__(self):
        """
        This function returns the representation of the address.
        """
        return f"Address {self.street} in {self.city}, {self.zip}."

    def __str__(self):
        """
        This function returns the string representation of the address.
        """
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
    total_price = Column(DECIMAL(10, 2), nullable=False)

    user = relationship("User", back_populates="orders")
    address = relationship("Address")

    def __repr__(self):
        """
        This function returns the representation of the order.
        """
        return f"Order {self.id} for user {self.user.username} \
            at address {self.address_id}."

    def __str__(self):
        """
        This function returns the string representation of the order.
        """
        return self.__repr__()

    def __eq__(self, other):
        """
        This function checks if two orders are equal.
        """
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
        list: A list containing a dictionary with user information.
        The dictionary includes the following keys:
              - "Username": The username of the user.
              - "Name": The name of the user.
              - "E-mail": The email address of the user.
    Raises:
        None.
    """
    session = create_session()
    try:
        user = session.query(User).filter_by(username=username).one()
        return_dict = {
            "Username": user.username,
            "Name": user.name,
            "E-mail": user.email,
        }
        session.close()
        return return_dict
    except Exception:
        session.close()


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
        orders_info = []
        for order in user.orders:
            address = order.address
            address_str = f"{address.zip}, {address.city}, {address.street}"
            orders_info.append(
                {
                    "Order time": order.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Status": order.status,
                    "Address": address_str,
                }
            )
        session.close()
        return orders_info
    except Exception:
        session.close()


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
    except Exception:
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
                session.close()
                return True
        except Exception:
            session.rollback()
            session.close()
            return False


def save_order(username: str, address: dict, price: float):
    """
    This function adds an order to the database.
    """
    session = create_session()

    try:
        user = session.query(User).filter_by(username=username).one()
    except Exception as e:
        session.rollback()
        session.close()
        raise e

    try:
        address = Address(
            full_name=address["full_name"],
            street=address["street_and_number"],
            city=address["city"],
            zip=address["zip"],
        )
        session.add(address)
        session.commit()
        session.flush()
    except Exception as e:
        session.rollback()
        session.close()
        raise e

    try:
        order = Order(
            user_id=user.id,
            address_id=address.id,
            timestamp=datetime.now(),
            status="Pending",
            total_price=price,
        )
        session.add(order)
        session.commit()
        session.flush()
        session.close()
        return True
    except Exception as e:
        session.rollback()
        session.close()
        raise e


engine = create_database()
