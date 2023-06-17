import numpy as np
import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
from sts.utils.streamlit_utils import (get_authenticator, overlay_image, transfer)

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

    generate = st.button(
        "Generate AI Image",
        use_container_width=True,
        disabled=not all([image is not None for image in st.session_state["images"]]),
    )

    if st.button("Debug", use_container_width=True):
        st.session_state["ai_image"] = Image.open("src/sts/.images/black_tshirt.png")

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
    placeholder = st.empty()
    with placeholder.container():
        st.title("Cart")
        # Access the session state to retrieve the items in the cart
        cart_items = st.session_state.get("cart_items", [])
        # Display the current items in the cart
        st.write("Current Items in Cart:")
        i = 0
        for item in cart_items:
            st.write(":heavy_minus_sign:" * 32)
            _, col, _s, _b = st.columns((1, 1, 0.5, 1))
            with _:
                st.image(item["image"], use_column_width=True)
            with col:
                if item["product"] == "shirt":
                    k = "Shirt (White)"
                elif item["product"] == "black":
                    k = "Shirt (Black)"
                elif item["product"] == "hoodie":
                    k = "Hoodie (White)"
                st.subheader(k)
            with _s:
                strg = "Confirm Size: " + item["size"] + " "
                if item["size"]== "S":
                    label_size = ("S", "M", "L", "XL")
                elif item["size"] == "M":
                    label_size = ("M", "S", "L", "XL")
                elif item["size"] == "L":
                    label_size = ("L", "S", "M", "XL")
                elif item["size"] == "XL":
                    label_size = ("XL", "S", "M", "L")
                item["size"]=st.selectbox(strg, label_size, key=-i-1)
                item["count"]=st.number_input(label="Quantity", min_value=0, max_value=69, value=item["count"], format="%i", key = i)
                st.session_state["cart_items"][i] = cart_items[i]            
            with _b:
                #st.subheader("")
                nuke_button = st.button("🗑️", key = 70+i)
                if nuke_button:
                    del cart_items[i]
                    st.session_state["cart_items"] = cart_items
            i += 1       
        checkout_button = st.button("CHECKOUT")
    if checkout_button:
        placeholder.empty()
        checkout()
        st.session_state["current_page"] = checkout



def place_product():
    st.title("Place Product")
    # Access the session state to retrieve the AI image
    ai_image = st.session_state.get("ai_image")
    product_preview = st.empty()
    if ai_image is not None:
        if st.session_state["product_picture"] is not None:
            product_preview.image(st.session_state.get("product_picture"), caption="White Shirt")
        else:
            product_preview.image(ai_image, caption="Generated AI Image")
        st.subheader("Select Product Type:")
        product_type = "shirt"
        ai_image_array = np.array(ai_image)
        array_shape = ai_image_array.shape
        ai_image_bytes = ai_image_array.tobytes()
        circle = False
        st.subheader("Select Product:")
        product_type2 = st.selectbox("Product:", ("Shirt White", "Shirt Black", "Hoodie")) 
        if product_type2 == "Shirt White":
            product_type = "shirt"
        elif product_type2 == "Shirt Black":
            product_type = "black"
        elif product_type2 == "Hoodie":
            product_type = "hoodie"           
        st.subheader("Select Size:")
        size = st.selectbox("Size", ("S", "M", "L", "XL"))
        circle = st.checkbox("Form: Circle", False, None, None, on_change = None, args = None, kwargs = None, label_visibility = "visible", )
        if circle:
            st.session_state["circle_image"] = True
        else:
            st.session_state["circle_image"] = False
        shirt_image = overlay_image(
            product_type, ai_image_bytes, array_shape, st.session_state["circle_image"], None
        )
        st.session_state["product_picture"] = shirt_image
        product_preview.image(shirt_image, 
                              caption="T-Shirt" if product_type=="shirt" else "Hoodie" if product_type=="hoodie" else "Black Shirt")
        place_product_button = st.button("Place Product in Cart")
        if place_product_button:
            cart_items = st.session_state.get("cart_items", [])
            product = {
                "image": st.session_state["product_picture"],
                "size": size,
                "product": product_type,
                "count" : 1,
            }
            cart_items.append(product)
            st.session_state["cart_items"] = cart_items
            st.success("Product placed in cart!")
            st.session_state["current_page"] = cart
            st.experimental_rerun()
    else:
        st.warning("Please generate the AI image first!")

def checkout():
    st.title("Checkout")
    cart_items = st.session_state.get("cart_items", [])
    if len(cart_items) == 0:
        st.warning("Your cart is empty!")
    else:
        # Display the cart items
        st.write("Cart Items:")
        for item in cart_items:
             for item in cart_items:
                strg = ""
                strg = "Größe " + item["size"] + " : " +  item["product"]
                st.image(item["image"], caption= strg)
        # Add checkout logic and payment processing here
        st.success("Checkout completed successfully!")

def index():
    st.warning("Please continue to either your cart or create another AI Picture")



def main() -> None:
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
        "Cart", key="cart_button", use_container_width=True
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
        if st.session_state["current_page"] is None:
            st.warning("Hupsala")
            pass
        else:
            st.session_state["current_page"]()

if __name__ == "__main__":
    main()
