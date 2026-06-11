import requests


API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/ef79a237f234ff29828af26d4588e708/ai/run/"
headers = {"Authorization": f"Bearer {API_TOKEN}"}


import requests
import base64
from PIL import Image
from io import BytesIO

def run_image(prompt):
    response = requests.post(
        f"{API_BASE_URL}@cf/black-forest-labs/flux-1-schnell",
        headers=headers,
        json={
            "prompt": prompt
        }
    )

    data = response.json()

    image_b64 = data["result"]["image"]

    image_bytes = base64.b64decode(image_b64)

    img = Image.open(BytesIO(image_bytes))

    img.save("output.jpg")
    print("saved output.jpg")

    return img


run_image(
    "A llama walking toward a magical orange cloud"
)