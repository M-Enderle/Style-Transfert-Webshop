import streamlit as st
from PIL import Image

from sts.utils.streamlit_utils import get_authenticator, transfer

# TODO Josh: Add two columns for the two images to be uplaoded
# TODO Josh: Add a button to apply transfer style
# TODO Josh: Show image after transfer style

# Tips:
# - use st.columns
# - save a cart reference in the session state
# - use st.session_state
# Function to upload and display image


def upload_image(column_num):
    uploaded_file = st.file_uploader(
        f"Upload Image {column_num}",
        type=["png", "jpg", "jpeg"],
        label_visibility="hidden",
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state["images"][column_num - 1] = image

    if st.session_state["images"][column_num - 1] is not None:
        st.image(
            st.session_state["images"][column_num - 1],
            caption=f"Uploaded Image {column_num}",
            use_column_width=True,
        )


def create_image():
    st.title("Create AI Image")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Image 1")
        upload_image(1)

    with col2:
        st.subheader("Image 2")
        upload_image(2)

    if all([image is not None for image in st.session_state["images"]]):
        st.markdown("## AI Image")
        ai_image = transfer(
            st.session_state["images"][0], st.session_state["images"][1]
        )
        st.image(ai_image, caption="AI Image", use_column_width=True)


def cart():
    # TODO Josh: Implement this function
    st.title("Cart")
    pass


def place_product():
    # TODO Josh: Implement this function
    st.title("Place Product")
    pass


def checkout():
    # TODO Josh: Implement this function
    st.title("Checkout")
    st.session_state["current_page"] = "checkout"
    # TODO Josh: Move this into a function in utils
    auth = get_authenticator()
    res = auth.login("Login to access the app", location="sidebar")

    if not res[1]:
        st.markdown("# Stop")
        st.markdown("Please login to use this feature")
        st.stop()
    # THIS REQUIRES AUTHENTICATION

    pass


def home():
    st.title("Home")
    st.markdown("Welcome to the Style Transfer Shop!")


def main() -> None:
    # add sidebar with create_image, place product, cart, checkout
    st.sidebar.title("Order Process")

    if "images" not in st.session_state:
        st.session_state["images"] = [None, None]

    if "ai_image" not in st.session_state:
        st.session_state["ai_image"] = None

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = home

    cart_btn = st.sidebar.button(
        "Cart [0]", key="cart_button", use_container_width=True
    )
    create_image_btn = st.sidebar.button(
        "Create AI Image", key="create_image_button", use_container_width=True
    )
    place_product_btn = st.sidebar.button(
        "Place Product", use_container_width=True, disabled=True
    )
    checkout_btn = st.sidebar.button(
        "Checkout", use_container_width=True, disabled=True
    )

    if cart_btn:
        cart()
        st.session_state["current_page"] = cart

    elif create_image_btn:
        create_image()
        st.session_state["current_page"] = create_image

    elif place_product_btn:
        place_product()
        st.session_state["current_page"] = place_product

    elif checkout_btn:
        checkout()
        st.session_state["current_page"] = checkout

    else:
        st.session_state["current_page"]()


if __name__ == "__main__":
    main()
