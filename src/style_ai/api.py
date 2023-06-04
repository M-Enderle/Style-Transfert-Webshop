import base64
import io

from fastapi import FastAPI, UploadFile
from PIL import Image

from style_ai.style_transfer import style_transfer

app = FastAPI(title="Style Transfer AI")


@app.get("/health")
def read_root():
    """
    Returns the status of the API.
    """

    return {"status": "ok"}


@app.post("/transfer")
async def upload_images(content_img: UploadFile, style_img: UploadFile):
    """
    Uploads two images and returns the result of the style transfer.
    """

    content_file_content = await content_img.read()
    style_file_content = await style_img.read()

    content = Image.open(io.BytesIO(content_file_content))
    style = Image.open(io.BytesIO(style_file_content))

    result = style_transfer(content, style, resize_to=2**8)

    # Convert the resulting image to base64 string
    result_bytes = io.BytesIO()
    result.save(result_bytes, format="JPEG")
    result_bytes.seek(0)
    result_base64 = base64.b64encode(result_bytes.getvalue()).decode("utf-8")

    # Return the result image
    return {
        "message": "Images transferred successfully!",
        "result_image": result_base64,
    }
