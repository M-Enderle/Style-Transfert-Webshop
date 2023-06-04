import streamlit as st
from PIL import Image
from sts.utils.streamlit_utils import get_authenticator
from sts.utils.utils import Cart, transfer

# TODO Josh: Add two columns for the two images to be uplaoded
# TODO Josh: Add a button to apply transfer style
# TODO Josh: Show image after transfer style

# Tips:
# - use st.columns
# - save a cart reference in the session state
# - use st.session_state
# Function to upload and display image

def upload_image(column_num):
    uploaded_file = st.sidebar.file_uploader(f"Upload Image {column_num}", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded Image {column_num}", use_column_width=True)
        return image


def main() -> None:
    # add sidebar with create_image, place product, cart, checkout
    st.sidebar.title("Order Process")

    if st.sidebar.button("Cart [0]", key="cart_button", use_container_width=True):
        st.title("Cart")

    # Two columns for uploading and displaying images
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Image 1")
        image1 = upload_image(1)

    with col2:
        st.subheader("Image 2")
        image2 = upload_image(2)

    if st.sidebar.button("Create AI Image", key="create_image_button", use_container_width=True):
        if image1 is None or image2 is None:
            st.warning("Please upload both images before creating AI image.")
        else:
            st.title("AI Image Creation")
            # Apply transfer style and display the result image
            ai_image = transfer(image1, image2)
            st.image(ai_image, caption="AI Image", use_column_width=True)


    # only enable if image is created
    if st.sidebar.button("Place Product", use_container_width=True, disabled=True):
        # DO STUFF
        st.title("Place Product")

    # only enable if cart is not empty
    if st.sidebar.button("Checkout", use_container_width=True, disabled=True):
        # TODO Josh: Move this into a function in utils
        auth = get_authenticator()
        res = auth.login("Login to access the app", location="sidebar")

        if not res[1]:
            st.markdown("# Stop")
            st.markdown("Please login to use this feature")
            st.stop()
        # THIS REQUIRES AUTHENTICATION

        # DO STUFF
        st.title("Checkout")


if __name__ == "__main__":
    main()
