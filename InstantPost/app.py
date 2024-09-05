from flask import Flask, render_template, request, redirect, url_for,session
import os
from io import BytesIO
import time
import requests
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from werkzeug.utils import secure_filename
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv('../.env')
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)


@app.route("/success")
def upload_success():
    filename = request.args.get("filename")
    text = request.args.get("text")
    return render_template("success.html", filename=filename, text=text)

@app.route("/error")
def upload_error():
    filename = request.args.get("filename")
    return render_template("error.html", filename=filename)


@app.route("/", methods=["GET", "POST"])
def make_post():
    params = getCreds()
    if request.method == "POST":
        # Handle file upload
        try:
            uploaded_file = request.files.get("file")
            if uploaded_file:
                # Save the uploaded file to a temporary location
                file_path = secure_filename(uploaded_file.filename)
                uploaded_file.save(file_path)
                params['save_path'] = file_path

                # Check image rotation and aspect ratio
                correct_image_orientation(params['save_path'])
                correct_aspect_ratio(params['save_path'])

                # Handle quote text
                params['quote'] = request.form.get("text")
                params['caption'] = f"QOD: {params['quote']} #Quote #QuoteOfTheDay"
                params['text_color'] = request.form.get('text-color')
                params['backdrop_color'] = request.form.get('backdrop-color')
                params['backdrop'] = request.form.get('backdrop')
                params['font'] = request.form.get('font')
                # Add text to the image
                add_text_to_image(params)

                # Upload the image to Imgur
                response_data = upload_image(params)
                delete_hash = response_data['data']['deletehash']
                params['img_url'] = response_data['data']['link']

                # Create image container on Instagram
                response = create_image_container(params)
                delete_image(delete_hash)

                # Check the media status and publish post
                container_id = response['id']
                imageMediaStatusCode = 'IN_PROGRESS'
                while imageMediaStatusCode != 'FINISHED':
                    imageMediaObjectStatusResponse = getMediaObjectStatus(params, container_id)
                    imageMediaStatusCode = imageMediaObjectStatusResponse['json_data']['status_code']
                    time.sleep(0.5)

                publishMedia(params, container_id)
                os.remove(file_path)
                return redirect(url_for("upload_success", filename=params['img_url'], text=params['quote']))
            else:
                print("No file uploaded")
        except Exception as e :
            print(e)
            return redirect(url_for("upload_error", filename=''))    
    return render_template("index.html")


def download_image(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.save(save_path)
        print(f"Image saved to {save_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}, Text: {response.text}")



def getCreds():
    creds = dict()
    creds['access_token'] = os.getenv("INSTA_ACCESS_TOKEN")
    creds['long_access_token'] = os.getenv("INSTA_ACCESS_TOKEN_LONG")
    creds['client_id'] = os.getenv("INSTA_CLIENT_ID")
    creds['client_secret'] = os.getenv("INSTA_CLIENT_SECRET")
    creds['graph_domain'] = 'https://graph.facebook.com/' # base domain for api calls
    creds['graph_version'] = 'v20.0' # version of the api we are hitting
    creds['endpoint_base'] = creds['graph_domain'] + creds['graph_version'] + '/' # base endpoint with domain and version
    creds['debug'] = 'no' # debug mode for api call
    creds['instagram_id'] = os.getenv("INSTA_ID")
    
    return creds


def delete_image(delete_hash):
    client_id = os.getenv("IMGUR_CLIENT_ID")
    headers = {
    'Authorization': f'Client-ID {client_id}',
}
    response = requests.delete(f'https://api.imgur.com/3/image/{delete_hash}', headers=headers)
    if response.status_code == 200:
        print(f"Image deleted successfully: {response.json()}")
    else:
        raise Exception(f"Failed to delete image: {response.json()}")
    return response.json()

def upload_image(params):
    client_id = os.getenv("IMGUR_CLIENT_ID")
    url = "https://api.imgur.com/3/image"
    payload = {
        'type': 'image',
        'title': 'image with text',
        'description': 'image with quote'
    }
    files = [
        ('image', (params['save_path'], open(params['save_path'], 'rb'), 'image/jpg'))
    ]
    headers = {
        'Authorization': f'Client-ID {client_id}'
    }

    response = requests.post(url, headers=headers, data=payload, files=files)

    # Print the raw response content
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode())

    try:
        response_data = response.json()
    except ValueError as e:
        print("Error decoding JSON:", e)
        return None

    return response_data

def publishMedia( params, mediaObjectId) :

	url = params['endpoint_base'] + params['instagram_id'] + '/media_publish' # endpoint url

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['creation_id'] = mediaObjectId # fields to get back
	endpointParams['access_token'] = params['long_access_token'] # access token

	return makeApiCall( url, endpointParams, 'POST' ) # make the api call

def makeApiCall(url, endpointParams,type):
    
    if type == 'POST' : # post request
        data = requests.post( url, endpointParams )
    else : # get request
        data = requests.get( url, endpointParams )
    response = dict()

    response['url'] = url
    response['endpoint_params'] = endpointParams
    response['endpoint_params_pretty'] = json.dumps(endpointParams, indent=4)
    response['json_data'] = json.loads(data.content)
    response['json_data_pretty'] = json.dumps(response['json_data'], indent= 4)

    return response

def getMediaObjectStatus(params, container_id):
    url = params['endpoint_base'] + '/' + container_id # endpoint url

    endpointParams = dict() # parameter to send to the endpoint
    endpointParams['fields'] = 'status_code' # fields to get back
    endpointParams['access_token'] = params['long_access_token'] # access token

    return makeApiCall( url, endpointParams, 'GET' )

def create_image_container(params): #Id of container: 17886042456048834
    url = params['endpoint_base'] + params['instagram_id'] + '/media'
    endpointParams = dict()
    endpointParams['access_token'] = params['long_access_token']
    endpointParams['caption'] = params['caption']
    endpointParams['image_url'] = params['img_url']
    response = requests.post(url, params=endpointParams)
    response = response.json()
    return response

def add_text_to_image(params):
    def wrap_text(text, draw, font, max_width):
        lines = []
        words = text.split()
        while words:
            line = ''
            while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
                line += (words.pop(0) + ' ')
            lines.append(line.strip())
        return lines

    image = Image.open(params['save_path'])
    draw = ImageDraw.Draw(image)
    text = params['quote']
    reference_size = (800, 600)  # You can adjust this as needed
    ratio = min(image.size[0] / reference_size[0], image.size[1] / reference_size[1])
    font_size = int(50 * ratio)  # Adjust the base font size as needed
    font = ImageFont.truetype("Georgia.ttf", size=font_size)

    image_width, image_height = image.size
    max_width = image_width - 20
    wrapped_text = wrap_text(text, draw, font, max_width)

    total_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text)
    y_position = (image_height - total_height) // 2

    color = (255, 255, 255)  # Text color
    background_color = (0, 0, 0)  # Background color for text
    padding = 10

    for line in wrapped_text:
        text_width = draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]
        text_height = draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]
        x_position = (image_width - text_width) // 2  # Center horizontally

        # Draw rectangle background
        # draw.rectangle(
        #     [(x_position - padding, y_position - padding), (x_position + text_width + padding, y_position + text_height + padding)],
        #     fill=background_color
        # )
        # Draw text on top of the rectangle
        draw.text((x_position, y_position), line, fill=color, font=font)
        y_position += text_height + padding * 2

    image.save(params['save_path'])

def correct_image_orientation(image_path):
    image = Image.open(image_path)
    exif = image._getexif()
    print("Was it rotated:")
    if exif:
        orientation = exif.get(274)  # 274 is the EXIF tag for orientation
        if orientation == 3:
            print("rotated 180")
            image = image.rotate(180, expand=True)
        elif orientation == 6:
            print("rotated 270")
            image = image.rotate(270, expand=True)
        elif orientation == 8:
            print("rotated 90")
            image = image.rotate(90, expand=True)
    print("Finished rotating")
    image.save(image_path)



def correct_aspect_ratio(image_path):
    min_aspect_ratio = 3040 / 4032
    max_aspect_ratio = 1.91 / 1

    image = Image.open(image_path)

    width, height = image.size
    aspect_ratio = width / height

    if aspect_ratio < min_aspect_ratio:
        # Add padding to meet the minimum aspect ratio
        new_height = height
        new_width = int(height * min_aspect_ratio)
    elif aspect_ratio > max_aspect_ratio:
        # Add padding to meet the maximum aspect ratio
        new_width = width
        new_height = int(width / max_aspect_ratio)
    else:
        # No adjustment needed
        print("aspect ratio was not changed")
        return
    print("aspect ratio was changed from ", aspect_ratio, " to ",new_width/new_height)
    #Create image with padding to fit ratio
    new_img = ImageOps.pad(image, (new_width, new_height), color=(0, 0, 0))

    # Save the adjusted image
    new_img.save(image_path)
    return

if __name__ == "__main__":
    app.run(debug=True)
