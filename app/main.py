from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, HTMLResponse
from PIL import Image
import io
import json
import base64
from user_agents import parse
import torch
from transformers import CLIPProcessor, CLIPModel
import datetime
import uuid
import os


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

def generate_unique_filename():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    short_uuid = uuid.uuid4().hex[:8]
    filename = f"{timestamp}_{short_uuid}"
    return filename

def generate_path_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_image_and_swag_percentage(img, swag_percentage):
    filename = generate_unique_filename()
    path = "data/exhibition_imgs/"
    generate_path_if_not_exists(path)
    img.save(f"{path}{filename}.jpg")
    with open(f"{path}{filename}.txt", "w") as f:
        f.write(str(swag_percentage))

def get_swag_percentage(img):
    inputs = processor(text=list_of_concepts, images=img, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image  # image-text similarity score
    probs = logits_per_image.softmax(dim=1)[0].detach().cpu().numpy()

    swag_index = list_of_concepts.index('swag')
    swag_prob = probs[swag_index]
    swag_percentage = swag_prob * 100
    return swag_percentage
def process_image_and_get_swag(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode == "RGBA":
        img = img.convert("RGB")
    swag_percentage = get_swag_percentage(img)
    save_image_and_swag_percentage(img, swag_percentage)
    return swag_percentage


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    ua_string = request.headers.get("user-agent", "")
    user_agent = parse(ua_string)

    if user_agent.os.family == "iOS" and user_agent.os.version:
        major_version = user_agent.os.version[0]
        if major_version < 10:
            return templates.TemplateResponse("index_legacy.html", {"request": request, "title": title})

    return templates.TemplateResponse("index.html", {"request": request, "title": title})

@app.post("/process-image/")
async def upload_image(request: Request,):
    print("Processing image")
    body = json.loads(await request.body())

    if "," in body["image"]:
        header, image_str = body["image"].split(",", 1)
    else:
        raise ValueError("Invalid data URL format")

    image_bytes = base64.b64decode(image_str)

    swag_percentage = process_image_and_get_swag(image_bytes)
    return {"swag_percentage": swag_percentage}

@app.post("/process-image-ios-7")
async def upload_image_ios7(image: UploadFile = File(...)):
    # This endpoint expects a multipart form upload, e.g. from FormData.
    print("Processing image via form upload")

    # Read the file bytes
    file_bytes = await image.read()
    swag_percentage = process_image_and_get_swag(file_bytes)
    return {"swag_percentage": swag_percentage}