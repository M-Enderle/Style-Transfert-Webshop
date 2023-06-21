import numpy as np
import streamlit as st
from PIL import Image

from sts.utils.streamlit_utils import get_module_root, overlay_image, transfer


class Product:
    def __init__(self, pimage: Image, psize: str, ptype: str, pcolor: str, pcount: int) -> None:
        self.image = pimage
        self.size = psize
        self.type = ptype
        self.color = pcolor
        self.count = pcount

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Product)
        return self.image == __value.image and \
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
        st.subheader("Image 1")
        upload_image(1)

    with col2:
        st.subheader("Image 2")
        upload_image(2)

    generate = st.button(
        "Generate AI Image",
        use_container_width=True,
        disabled=not all([image is not None for image in st.session_state["images"]]),
    )

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
    Displays the checkout page and completes the checkout process.

    Returns:
        None
    """
    
    st.title("Checkout")
    st.success("Checkout completed successfully!")


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
