from flask import Flask, render_template, request, redirect, url_for,session
import boto3
import os
from io import BytesIO
import time
import requests
import json
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename
from dotenv import load_dotenv, find_dotenv
import botocore.exceptions  # Import for handling boto3 exceptions
from datetime import datetime
import base64


env_path = find_dotenv('../.env')
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# Configure S3 credentials and bucket name
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("AWS_ACCESS")
S3_SECRET = os.getenv("AWS_SECRET")
S3_LOCATION = f"http://{S3_BUCKET}.s3.amazonaws.com/"

s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET
)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Retrieve the caption and base64 data from the form
        caption = request.form.get("caption")
        base64_data = request.form.get("base64")

        # Decode the base64 data
        img_data = base64_data.split(",")[1]
        decoded_img = base64.b64decode(img_data)

        # Create a unique key for the image in S3
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        img_name = f"uploads/{caption.replace(' ', '_')}_{timestamp}.png"

        try:
            # Upload the image to S3 with the caption as metadata
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=img_name,
                Body=decoded_img,  # Upload the raw image bytes
                ContentType='image/png',  # Set the appropriate content type
                Metadata={'caption': caption}  # Store the caption as metadata
            )

            # Redirect to the success page
            return redirect(url_for("upload_success", filename=img_name, caption=caption))

        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            # Handle any boto3 exceptions and redirect to the error page
            print(e)
            return redirect(url_for("upload_error"))

    return render_template("index.html")

@app.route("/success")
def upload_success():
    filename = request.args.get("filename")
    text = request.args.get("text")
    return render_template("success.html", filename=filename, text=text)

@app.route("/error")
def upload_error():
    filename = request.args.get("filename")
    return render_template("error.html", filename=filename)



if __name__ == "__main__":
    app.run(debug=True)
