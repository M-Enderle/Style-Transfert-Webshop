import base64
import io

import runpod
from PIL import Image

from style_ai.style_transfer import Vgg16Extractor, style_transfer

extractor = Vgg16Extractor(space="uniform")
print("VGG16 extractor loaded!")


def process_image(job):
    content_img_raw = job["input"]["content_img"]
    style_img_raw = job["input"]["style_img"]
    resize_to = job["input"]["resize_to"]

    content_img = Image.open(io.BytesIO(base64.b64decode(content_img_raw)))
    style_img = Image.open(io.BytesIO(base64.b64decode(style_img_raw)))

    result = style_transfer(
        content_img, style_img, extractor=extractor, resize_to=resize_to
    )

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


runpod.serverless.start({"handler": process_image})
