import json
import requests
from io import BytesIO
import time
from inspirational_quotes import quote
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv

load_dotenv()


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



def debugAccessToken(params):
    endpointParams = dict()
    endpointParams['input_token'] = params['access_token']
    endpointParams['access_token'] = params['access_token']

    url = params['graph_domain'] + '/debug_token'
    return makeApiCall(url, endpointParams, params['debug'])

def getLongLivedAccessToken(params):
    endpointParams = dict()
    endpointParams['grant_type'] = 'fb_exchange_token'
    endpointParams['client_id'] = params['client_id']
    endpointParams['client_secret'] = params['client_secret']
    endpointParams['fb_exchange_token'] = params['access_token']
    url = params['endpoint_base'] + 'oauth/access_token'
    return makeApiCall(url,endpointParams,params['debug'])


def create_image_container(params): #Id of container: 17886042456048834
    url = params['endpoint_base'] + params['instagram_id'] + '/media'
    endpointParams = dict()
    endpointParams['access_token'] = params['long_access_token']
    endpointParams['caption'] = params['caption']
    endpointParams['image_url'] = params['img_url']
    response = requests.post(url, params=endpointParams)
    response = response.json()
    return response

def publishMedia( params, mediaObjectId) :

	url = params['endpoint_base'] + params['instagram_id'] + '/media_publish' # endpoint url

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['creation_id'] = mediaObjectId # fields to get back
	endpointParams['access_token'] = params['long_access_token'] # access token

	return makeApiCall( url, endpointParams, 'POST' ) # make the api call

def getMediaObjectStatus(params, container_id):
    url = params['endpoint_base'] + '/' + container_id # endpoint url

    endpointParams = dict() # parameter to send to the endpoint
    endpointParams['fields'] = 'status_code' # fields to get back
    endpointParams['access_token'] = params['long_access_token'] # access token

    return makeApiCall( url, endpointParams, 'GET' )

def get_random_unsplash_image_url():
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")

    # API endpoint
    url = "https://api.unsplash.com/photos/random"

    # Parameters
    params = {
        "client_id": access_key
    }
    # Sending a GET request
    response = requests.get(url, params=params)

    # Checking if the request was successful
    if response.status_code == 200:
        # Extracting the image URL from the response
        data = response.json()
        image_url = data['urls']['regular']
    else:
        image_url = f"error: {response.status_code}"
    return image_url

def download_image(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.save(save_path)
        print(f"Image saved to {save_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}, Text: {response.text}")

def add_text_to_image(params):
    def wrap_text(text, draw, font, max_width):
        lines = []
        words = text.split()
        while words:
            line = ''
            while words and draw.textlength(line + words[0], font=font) <= max_width:
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

    color = (255, 255, 255)  
    background_color = (0, 0, 0)  
    padding = 10

    for line in wrapped_text:
        text_width, text_height = draw.textsize(line, font=font)
        x_position = (image_width - text_width) // 2  # Center horizontally
        # Draw rectangle background
        draw.rectangle(
            [(x_position - padding, y_position - padding), (x_position + text_width + padding, y_position + text_height + padding)],
            fill=background_color
        )
        # Draw text on top of the rectangle
        draw.text((x_position, y_position), line, fill=color, font=font)
        y_position += text_height + padding * 2

    image.save(params['save_path'])

def upload_image(params):
    client_id = os.getenv("IMGUR_CLIENT_ID")
    url = "https://api.imgur.com/3/image"
    payload={'type': 'image',
    'title': 'image with text',
    'description': 'image with quote'}
    files=[
    ('image',(params['save_path'],open(params['save_path'],'rb'),'image/jpg'))
    ]
    headers = {
    'Authorization': 'Client-ID {client_id}'
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    response_data = response.json()
    return response_data

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



params = getCreds()

params['quote'] = quote()['quote']
print(params['quote'])
params['caption'] = "QOD: "+params['quote']+" #Quote #QuoteOfTheDay"

params['img_url'] = get_random_unsplash_image_url()

params['save_path'] = 'jack.jpg'
download_image(params['img_url'],params['save_path'])

add_text_to_image(params)



response_data = upload_image(params)
delete_hash = response_data['data']['deletehash']
params['img_url'] = response_data['data']['link']
response = create_image_container(params)

delete_image(delete_hash)

# print(response)
container_id = response['id']
imageMediaStatusCode = 'IN_PROGRESS'
while imageMediaStatusCode != 'FINISHED' : # keep checking until the object status is finished
    imageMediaObjectStatusResponse = getMediaObjectStatus( params, container_id ) # check the status on the object
    print(imageMediaObjectStatusResponse)
    imageMediaStatusCode = imageMediaObjectStatusResponse['json_data']['status_code'] # update status code

    print( "\n---- IMAGE MEDIA OBJECT STATUS -----\n" ) # display status response
    print( "\tStatus Code:" ) # label
    print( "\t" + imageMediaStatusCode ) # status code of the object

    time.sleep(5)
    
print(publishMedia(params, container_id))

