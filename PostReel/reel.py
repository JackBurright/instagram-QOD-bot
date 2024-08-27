import requests
import json

graph_url = 'https://graph.facebook.com/v20.0/'
param = dict()

def post_reel(access_token,instagram_account_id, caption='', media_type ='',share_to_feed='',thumb_offset='',video_url=''):
    url = graph_url + instagram_account_id + '/media'
    
    param['access_token'] = access_token
    param['caption'] = caption
    param['media_type'] = media_type
    param['share_to_feed'] = share_to_feed
    param['thumb_offset'] = thumb_offset
    param['video_url'] = video_url
    response =  requests.post(url,params = param)
    print("\n response",response.content)
    response =response.json()
    return response



def status_of_upload(ig_container_id,access_token):
    url = graph_url + ig_container_id
    param = {}
    param['access_token'] = access_token
    param['fields'] = 'status_code'
    response = requests.get(url,params=param)
    response = response.json()
    return response


def publish_container(creation_id = '',access_token = '',instagram_account_id=''):
    url = graph_url + instagram_account_id + '/media_publish'
    param = dict()
    param['access_token'] = access_token
    param['creation_id'] = creation_id
    response = requests.post(url,params=param)
    response = response.json()
    return response


post_reel(media_type='REELS',video_url='',instagram_account_id='')

container = ''
print(status_of_upload(ig_container_id=container))
print(publish_container(creation_id=container,access_token='',instagram_account_id=''))