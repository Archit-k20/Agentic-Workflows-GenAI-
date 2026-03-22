from openai import OpenAI
from PIL import Image
from io import BytesIO
import base64


def generate_image_from_text(prompt, api_key=None):
    try:
        client = OpenAI(api_key=api_key)

        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            n=1
        )

        image_base64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        image = Image.open(BytesIO(image_bytes))
        return image

    except Exception as e:
        return f"Error generating image: {e}"
