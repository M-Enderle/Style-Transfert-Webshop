import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
import numpy as np
import pandas as pd

from sts.utils.streamlit_utils import get_authenticator, transfer, overlay_image
from sts.utils.utils import generate_payment_link
 

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
        st.session_state["ai_image"] = Image.open("/home/fe02174/style_transfer/style-transfer-webshop/src/sts/utils/images/black_tshirt.png")

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
        for item in cart_items:
            strg = ""
            strg = "Größe " + item["size"] + " : " +  item["product"]
            st.image(item["image"], caption= strg)
          
        #  Add a checkout button
        checkout_button = st.button("Checkout")
    if checkout_button:
        # Set the current page to the checkout function
        placeholder.empty()
        checkout()
        st.session_state["current_page"] = checkout

        #st.experimental_rerun()


def place_product():
    st.title("Place Product")
    # Access the session state to retrieve the AI image
    ai_image = st.session_state.get("ai_image")
    product_preview = st.empty()
    if ai_image is not None:
        # Display the AI image
        if st.session_state["product_picture"] is not None:
            product_preview.image(st.session_state.get("product_picture"), caption="White Shirt")
        else:
            product_preview.image(ai_image, caption="Generated AI Image")

        # Add logic for placing the product in the shopping cart
        st.subheader("Select Product Type:")
        col1, col2, col3 = st.columns(3)
        product_type = "shirt"
        ai_image_array = np.array(ai_image)
        array_shape = ai_image_array.shape
        ai_image_bytes = ai_image_array.tobytes()
        circle = False
        with col1:
            if st.button("T-Shirt"):
                product_type = "shirt"
        with col2:
            if st.button("Hoodie"):
                product_type = "hoodie"
        with col3:
            if st.button("Not-White Shirt"):
                product_type = "black"
                    
        st.subheader("Select Size:")
        size = st.selectbox("Size", ("S", "M", "L", "XL"))
        st.subheader("Form:")
        circle = st.selectbox("Form", ("Rectangle", "Cycle"))
        if circle == "Cycle":
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
            # Retrieve the items in the cart from the session state
            cart_items = st.session_state.get("cart_items", [])
            # Create the product object with image and size information
            prices = {
                "hoodie": 25,
                "shirt" : 15,
                "black" : 15
            }
            price = prices[product_type]
            product = {
                "image": st.session_state["product_picture"],
                "size": size,
                "product": product_type,
                "price": price
            }
            # Add the product to the cart
            cart_items.append(product)
            # Update the cart items in the session state
            st.session_state["cart_items"] = cart_items
            st.success("Product placed in cart!")
            # Redirect back to the cart page
            st.session_state["current_page"] = cart
            st.experimental_rerun()
    else:
        st.warning("Please generate the AI image first!")

def checkout():
    #TODO: you cannot get to this page, when there is nothing added to your cart
    st.title("Checkout")
    # Access the session state to retrieve the cart items
    cart_items = st.session_state.get("cart_items", [])

    shipping_cost = {
        "Productname": "Shipping",
        "Amount": "via DHL",
        "Price Total": "5.49 €"
    }
    
    checkout_items = []
    for item in cart_items:
        already_added = False
        size = item["size"]
        product = item["product"]

        for checkout_item in checkout_items:
            if checkout_items:
                if checkout_item["Size"] == size and checkout_item["product_type"] == product:
                    checkout_item["Amount"] += 1
                    sum = int(checkout_item["Price Item"].replace(" €", "")) * int(checkout_item["Amount"])
                    checkout_item["Price Total"] = str(sum) + " €"
                    already_added = True 

        if not already_added:
            product_name="T-Shirt - white" if product=="shirt" \
                else "Hoodie - white" if product=="hoodie" \
                else "T-Shirt - black"
            amount = 1
            image_paths = {
                "hoodie": "src/sts/utils/images/white_hoodie.png",
                "shirt":"src/sts/utils/images/white_tshirt.png",
                "black": "src/sts/utils/images/black_tshirt.png"
            }
            #TODO amelie: set price as item["price"]
            single_price = item["price"]
            new_item = {
                "Productname": product_name,
                "product_type": product,
                "Amount": amount,
                "Size": size,
                "Price Item": str(single_price) + " €",
                "Price Total": str(single_price) + " €"
            }
            checkout_items.append(new_item)
        
    checkout_items.append(shipping_cost)
    checkout_table = pd.DataFrame(checkout_items)
    checkout_table = checkout_table.fillna("")
    total_sum = checkout_table["Price Total"].str.replace(" €", "").astype(float).sum()
    st.table(checkout_table[["Productname", "Amount", "Size", "Price Item", "Price Total"]])

    st.session_state["cart_items"] = checkout_items

    st.markdown(
        f"<div style='display: flex; justify-content: flex-end;'><p>"\
            f"Total sum of your order: <strong> {total_sum:.2f}€</strong></p></div>",
        unsafe_allow_html=True
    )

    if st.button("Proceed to Payment"):
        generate_payment_link(checkout_items)


    

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

    if "cycle_image" not in st.session_state:
        st.session_state["circle_image"] = False

    cart_btn = st.sidebar.button(
        "Cart [0]", key="cart_button", use_container_width=True
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
