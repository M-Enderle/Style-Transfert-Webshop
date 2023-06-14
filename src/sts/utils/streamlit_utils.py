# https://github.com/mkhorasani/Streamlit-Authenticator

import base64
import io
import runpod

import requests
import streamlit as st
import streamlit_authenticator as stauth
from PIL import Image, ImageDraw

import sts.app.database as db
from sts.utils.utils import load_user_toml

session = db.session
user_data = load_user_toml()
image_path1 = 'src/sts/utils/images/black.png'
image_path2 = 'src/sts/utils/images/tshirt_resize.png'
image_path3 = 'src/sts/utils/images/hoodie.png'
black_path = 'sts/utils/images/black_tshirt.png'



def overlay_image(strg="", x=None, y=None, input_image=None, is_circle=False, size=None):
    if input_image is None:
        raise ValueError("No image provided")

    if size is None:
        size = int(min(input_image.size) * 0.25)  # Default size: 25% of the smaller dimension

    if strg == 'shirt':
        source_image = Image.open(image_path2)
    elif strg == 'black':
        source_image = Image.open(image_path1)
    elif strg == 'hoodie':
        source_image = Image.open(image_path3)
    else:
        raise EnvironmentError("Something went wrong calling overlay_image()")

    source_image = source_image.convert("RGBA")  # Convert to RGBA for transparency support
    input_image = input_image.convert("RGBA")
    # Set the x & y to the center of the background image
    x = source_image.width // 2
    y = source_image.height // 2 - source_image.height*0.15
 
    if is_circle:
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((x - size, y - size, x + size, y + size), fill=255)
        source_image.paste(input_image.resize((size, size)), (int(x - size), int(y - size)), mask=mask)
    else:
        source_image.paste(input_image.resize((size, size)), (int(x - size), int(y - size)))

    # Save the output as a PNG image
    source_image.save("output.png", "PNG")

    return source_image

def get_authenticator() -> stauth.Authenticate:
    """
    Returns a streamlit_authenticator.Authenticate object
    """

    credentials = {
        "usernames": {
            "test": {
                "name": "test",
                "password": "$2b$12$WUXOCZmZqU0HTbggJ4hIBuCutUdQQo3xHWtafRkHtcjbo.TlboHq.",
                "email": "test@test.com",
            }
        }
    }

    return stauth.Authenticate(
        credentials=credentials,
        cookie_name=user_data["stauth"]["cookie_name"],
        key=user_data["stauth"]["cookie_secret_key"],
        cookie_expiry_days=user_data["stauth"]["cookie_expiry_days"],
    )


def convert_img_to_base64(img) -> str:
    """
    Converts an image to base64 string.
    """

    result_bytes = io.BytesIO()
    img.save(result_bytes, format="JPEG")
    result_bytes.seek(0)
    result_base64 = base64.b64encode(result_bytes.getvalue()).decode("utf-8")
    return result_base64


def convert_base64_to_img(base64_str: str):
    """
    Converts a base64 string to an image.
    """

    img = Image.open(io.BytesIO(base64.b64decode(base64_str)))
    return img


def transfer(content_img, style_img):
    """Transfer style from style image to content image."""

    content_img = content_img.convert("RGB")
    style_img = style_img.convert("RGB")

    content_img = convert_img_to_base64(content_img)
    style_img = convert_img_to_base64(style_img)

    if load_user_toml()["runpod"]["use"] == "true":
        runpod.api_key = load_user_toml()["runpod"]["api_key"]
        endpoint = runpod.Endpoint(load_user_toml()["runpod"]["endpoint"])

        data = {
            "content_img": content_img,
            "style_img": style_img,
            "resize_to": 512,
        }

        run_request = endpoint.run(
            data,
        )

        with st.spinner("Transferring style..."):
            result = run_request.output()

        result_image = convert_base64_to_img(result["result_image"])
        return result_image

    else:
        files = [("content_img", content_img), ("style_img", style_img)]

        try:
            with st.spinner("Transferring style..."):
                response = requests.post("http://localhost:8000/transfer", files=files)
        except requests.exceptions.ConnectionError:
            st.error("ConnectionError: Make sure the server is running.")
            return None

        retult_img = Image.open(
            io.BytesIO(base64.b64decode(response.json()["result_image"]))
        )

        return retult_img
