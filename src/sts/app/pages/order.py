import numpy as np
import streamlit as st
from streamlit_extras.app_logo import add_logo
from PIL import Image
from streamlit_extras import add_vertical_space
import numpy as np
import stripe
from PIL import ImageChops

from sts.utils.streamlit_utils import get_module_root, overlay_image, transfer

from sts.utils.streamlit_utils import get_authenticator, transfer, overlay_image, black_tshirt
from sts.utils.checkout_utils import generate_payment_link, generate_cart

add_logo(logo_url="src/sts/img/Style-Transfer_Webshop_Logo.png", height=80)

class Product:
    def __init__(self, pimage: Image.Image, ai_size: float, psize: str, ptype: str, pcolor: str, pcount: int) -> None:
        self.image = pimage
        self.ai_size = ai_size
        self.size = psize
        self.type = ptype
        self.color = pcolor
        self.count = pcount

    def __eq__(self, __value) -> bool:
        return not ImageChops.difference(self.image, __value.image).getbbox() and \
            self.ai_size == __value.ai_size and \
            self.size == __value.size and \
            self.type == __value.type and \
            self.color == __value.color


def upload_image(column_num):
    """
    Displays a file uploader and allows the user to upload an image.

    Parameters:
        column_num (int): The column number for displaying the image.

    Returns:
        None
    """

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
    """
    Creates the AI image by uploading two images and generating the AI image.

    Returns:
        None
    """

    st.title("Create AI Image")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Content Image")
        upload_image(1)

    with col2:
        st.subheader("Style Image")
        upload_image(2)

    generate = st.button(
        "Generate AI Image",
        use_container_width=True,
        disabled=not all([image is not None for image in st.session_state["images"]]),
    )

    if st.button("Debug", use_container_width=True):
        st.session_state["ai_image"] = Image.open(black_tshirt)

    if generate and all([image is not None for image in st.session_state["images"]]):
        ai_image = transfer(
            st.session_state["images"][0], st.session_state["images"][1]
        )

        st.session_state["ai_image"] = ai_image

    if st.session_state["ai_image"] is not None:
        _, col, _ = st.columns((1, 2, 1))

        with col:
            st.markdown("## AI Image")
            st.image(
                st.session_state["ai_image"],
                use_column_width=True,
            )

            place_prod_btn = st.button("Next Step", use_container_width=True)

            if place_prod_btn:
                st.session_state["current_page"] = place_product
                st.experimental_rerun()


def cart():
    """
    Displays the cart with the added products and allows interaction with the cart items.

    Returns:
        None
    """
    placeholder = st.empty()
    checkout_button = None
    with placeholder.container():
        st.title("🛒 Cart")
        st.divider()
        cart_items = st.session_state.get("cart_items", [])
        for i, item in enumerate(cart_items):
            img, information = st.columns((1.6, 6))
            with img:
                st.image(item.image, use_column_width=True)
            with information:
                subheader = f"{item.type} ({item.color})"
                st.subheader(subheader)
                size, quant, delete = st.columns((1,1, 0.3))
                with size:
                    item.size=st.selectbox("Size", ("S", "M", "L", "XL"),
                                              index=["S", "M", "L", "XL"].index(item.size),
                                              key=f"size-{i}")
                with quant:
                    item.count=st.number_input(label="Quantity", min_value=0, max_value=None, step=1,
                                                  value=item.count, format="%i", key=f"count-{i}")
                with delete:
                    st.markdown("## ")
                    delete_button = st.button("🗑️", key=f"delete-{i}")
                    if delete_button:
                        del cart_items[i]
                        st.session_state["cart_items"] = cart_items
                        st.experimental_rerun()
            st.divider()

    if len(cart_items) != 0:
        checkout_button = st.button("Continue to payment", use_container_width=True)

        if checkout_button:
            placeholder.empty()
            checkout()
            st.session_state["current_page"] = checkout

    else:
        st.info("Your cart is empty")


def place_product():
    """
    Allows the user to select product type, size, and form, and overlays the AI image with the selected product.

    Returns:
        None
    """
    _, col, _ = st.columns((1,3,1))
    st.title("Select Product")
    ai_image = st.session_state.get("ai_image")
    with col:
        product_preview = st.empty()
    if ai_image is not None:
        if st.session_state["product_picture"] is not None:
            product_preview.image(st.session_state.get("product_picture"), caption="White Shirt")
        else:
            product_preview.image(ai_image, caption="Generated AI Image")
        product_type = "Shirt"
        ai_image_array = np.array(ai_image)
        array_shape = ai_image_array.shape
        ai_image_bytes = ai_image_array.tobytes()
        circle = False
        col1, col2 = st.columns((1, 1))
        with col1:
            product_type = st.selectbox("Product:", ("Shirt", "Hoodie"))
        with col2:
            product_color = st.selectbox("Color:", ("White", "Black"))
        st.subheader("Select Size:")
        size = st.selectbox("Size", ("S", "M", "L", "XL"))
        circle = st.checkbox("Form: Circle", False, None, None, on_change = None, args = None, kwargs = None, label_visibility = "visible", )
        if circle:
            st.session_state["circle_image"] = True
        else:
            st.session_state["circle_image"] = False
        img_size = st.slider("Image Size:", min_value = 0.25, max_value = 0.75, value = 0.5, step = 0.05, label_visibility = "visible")
        shirt_image = overlay_image(
            (product_type, product_color), ai_image_bytes, array_shape, st.session_state["circle_image"], img_size
        )
        st.session_state["product_picture"] = shirt_image
        product_preview.image(shirt_image, caption=f"{product_type} ({product_color})")
        place_product_button = st.button("Place Product in Cart",use_container_width=True)
        if place_product_button:
            cart_items = st.session_state.get("cart_items", [])
            product = Product(pimage=st.session_state["product_picture"],
                              psize=size,
                              ai_size=img_size,
                              ptype=product_type,
                              pcolor=product_color,
                              pcount=1)
            for i, item in enumerate(cart_items):
                if product == item:
                    cart_items[i].count += 1
                    break
            else:
                cart_items.append(product)
            st.session_state["cart_items"] = cart_items
            st.success("Product placed in cart!")
        cart_button = st.button("Go to Cart", use_container_width=True)
        if cart_button:
            st.session_state["current_page"] = cart
            st.experimental_rerun()
    else:
        st.warning("Please generate the AI image first!")


def checkout():
    """
    Creates the checkout page.
    All of the items, added to the cart and stored in the session are shown.
    The user should just get an overview of his order means the amount and
    the items that he is about to order. On this page the user can direct to payment
    to end his shopping experience.
    """

    shipping_address_from = st.form("Shipping address", )
    shipping_address_from.subheader("Shipping Address")
    full_name = shipping_address_from.text_input("Full Name")
    country = shipping_address_from.text_input("Country")
    street_and_number = shipping_address_from.text_input("Street and Number")
    city = shipping_address_from.text_input("City")
    zip = shipping_address_from.text_input("zip")
    shipping_address_from.divider()
    if shipping_address_from.form_submit_button("Continue to payment", use_container_width=True):

        if country == "" or street_and_number == "" or city == "" or zip == "" or full_name == "":
            st.error("Please fill out all fields!")
            return

        st.session_state["address"] = {
            "full_name": full_name,
            "country": country,
            "street_and_number": street_and_number,
            "city": city,
            "zip": zip
        }
        st.session_state["current_page"] = payment

        _, checkout_items, _ = generate_cart(st.session_state.get("cart_items", []))
        st.session_state["stripe_url"], st.session_state["payment_session"] = generate_payment_link(checkout_items)

        st.experimental_rerun()

def payment():
    """
    Creates the payment page.
    The user can pay via stripe.
    """

    total_sum, _, table = generate_cart(st.session_state["cart_items"])

    st.title("Payment")

    add_vertical_space.add_vertical_space(3)
    st.table(table)
    st.markdown(
            f"<div style='display: flex; justify-content: flex-end;'><p>"\
                f"Total sum of your order: <strong> {total_sum:.2f}€</strong></p></div>",
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown(f'''
        <a href={st.session_state["stripe_url"]} style="color: inherit;">
            <button class="css-1a359ur e1ewe7hr10">
                <div data-testid="stMarkdownContainer" class="css-x78sv8 eqr7zpz4"><p>Pay Now</p></div>
            </button>
        </a>''', unsafe_allow_html=True)
    add_vertical_space.add_vertical_space(1)
    check_button = st.button("Check payment status", use_container_width=True)

    if check_button:
        st.session_state["payment_session"] = stripe.checkout.Session.retrieve(st.session_state["payment_session"].id)
        status = st.session_state["payment_session"].payment_status
        if status == "paid":
            st.success("Payment successful!")
            st.session_state["current_page"] = success
            st.session_state["cart_items"] = []
            st.session_state["ai_image"] = None
            st.session_state["images"] = [None, None]
            st.experimental_rerun()
        else:
            st.warning("Payment not successful yet. Please pay and recheck afterwards.")

def success():
    st.markdown("# Thank you")
    st.success("Your order has been placed successfully!")

    back_home = st.button("Back to home")
    if back_home:
        st.session_state["current_page"] = create_image
        st.experimental_rerun()

def index():
    st.warning("Please continue to either your cart or create another AI Picture")


def main() -> None:
    """
    The main function that serves as the entry point of the Streamlit application.

    Returns:
        None
    """

    # add sidebar with create_image, place product, cart, checkout
    st.sidebar.title("Order Process")

    if "images" not in st.session_state:
        st.session_state["images"] = [None, None]

    if "ai_image" not in st.session_state:
        st.session_state["ai_image"] = None

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = create_image

    if "product_picture" not in st.session_state:
        st.session_state["product_picture"] = None

    if "circle_image" not in st.session_state:
        st.session_state["circle_image"] = False

    cart_btn = st.sidebar.button(
        f"Cart [{sum([item.count for item in st.session_state.get('cart_items', [])])}]",
        key="cart_button", use_container_width=True
    )
    create_image_btn = st.sidebar.button(
        "Create AI Image", key="create_image_button", use_container_width=True
    )
    place_product_btn = st.sidebar.button(
        "Place Product",
        use_container_width=True,
        disabled=st.session_state["ai_image"] is None,
    )
    checkout_btn = st.sidebar.button(
        "Checkout", use_container_width=True, disabled=len(st.session_state.get("cart_items", [])) == 0
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
        if st.session_state["current_page"] is None:
            st.experimental_rerun()
        else:
            st.session_state["current_page"]()

if __name__ == "__main__":
    main()
