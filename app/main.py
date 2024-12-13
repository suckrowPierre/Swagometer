from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from PIL import Image
import io
import json
import base64

import torch
from transformers import CLIPProcessor, CLIPModel

app = FastAPI()
device = torch.device("mps")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

title = "Swaginator"

model_name = "patrickjohncyh/fashion-clip"
model = CLIPModel.from_pretrained(model_name).to(device)
processor = CLIPProcessor.from_pretrained(model_name)

# Define concepts
list_of_concepts = [
    'swag',
    'sportive style',
    'corporate style',
    'casual style',
    'elegant style',
    'unfashionable',
]

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": title})

@app.get("/ios7/")
async def read_root_ios7(request: Request):
    return templates.TemplateResponse("index_ios7.html", {"request": request, "title": title})

@app.post("/process-image/")
#upload image in form
async def upload_image(request: Request,):
    print("Processing image")
    body = json.loads(await request.body())

    if "," in body["image"]:
        header, image_str = body["image"].split(",", 1)
    else:
        raise ValueError("Invalid data URL format")

    image_bytes = base64.b64decode(image_str)

    image = Image.open(io.BytesIO(image_bytes))
    if image.mode == "RGBA":
        image = image.convert("RGB")

    image.save("static/image.jpg")
    # Preprocess inputs and move to device
    inputs = processor(text=list_of_concepts, images=image, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Run inference
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image  # image-text similarity score
    probs = logits_per_image.softmax(dim=1)[0].detach().cpu().numpy()

    # get percentage of swag
    swag_index = list_of_concepts.index('swag')
    swag_prob = probs[swag_index]
    swag_percentage = swag_prob * 100
    print(swag_percentage)
    return {"swag_percentage": swag_percentage}

@app.post("/process-image-ios-7")
async def upload_image_ios7(image: UploadFile = File(...)):
    # This endpoint expects a multipart form upload, e.g. from FormData.
    print("Processing image via form upload")

    # Read the file bytes
    file_bytes = await image.read()
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode == "RGBA":
        img = img.convert("RGB")

    img.save("static/image.jpg")

    # Preprocess inputs and move to device
    inputs = processor(text=list_of_concepts, images=img, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Run inference
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)[0].detach().cpu().numpy()

    swag_index = list_of_concepts.index('swag')
    swag_prob = probs[swag_index]
    swag_percentage = swag_prob * 100
    print(swag_percentage)
    return {"swag_percentage": swag_percentage}