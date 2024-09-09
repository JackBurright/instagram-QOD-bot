import os
import boto3

from dotenv import load_dotenv, find_dotenv
import botocore.exceptions 

load_dotenv()

S3_KEY = os.getenv("AWS_ACCESS")
S3_SECRET = os.getenv("AWS_SECRET")

polly_client = boto3.client(
    "polly",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET,
    region_name='us-east-1'
)
text_for_polly = "Great moments are born from great opportunity. And that's what you have here tonight, boys. That's what you've earned here tonight. One game. If we played 'em ten times, they might win nine. But not this game. Not tonight. Tonight, we skate with them. Tonight, we stay with them. And we shut them down because we can! Tonight, WE are the greatest hockey team in the world. You were born to be hockey players. Every one of you. And you were meant to be here tonight. This is your time. Their time is done. It's over. I'm sick and tired of hearing about what a great hockey team the Soviets have. Screw 'em. This is your time. Now go out there and take it."
response = polly_client.synthesize_speech(Engine='standard', OutputFormat='mp3',Text=text_for_polly, TextType='text', VoiceId= 'Matthew')

file_path = 'audio.mp3'
with open(file_path, 'wb') as file:
    file.write(response['AudioStream'].read())