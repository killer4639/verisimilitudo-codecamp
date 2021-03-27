# -*- coding: utf-8 -*-

from scripts import tabledef
from scripts import forms
from scripts import helpers
from PIL import Image, ImageChops, ImageEnhance
from flask import Flask, redirect, url_for, render_template, request, session
import json
import sys
import io
from io import BytesIO
import requests
import os
import numpy as np
import base64
from keras.models import load_model
from keras.preprocessing import image
from keras.layers import Dense, Flatten, Conv2D, MaxPool2D, Dropout
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
from config import S3_BUCKET, S3_KEY, S3_SECRET, S3_REGION
from helpers import *
from testing import *
from keras.models import model_from_json
# from keras.optimizers import adam



app = Flask(__name__)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only
app.config["SECRET_KEY"] = "prettyprinted"

# get the model from here. Works fine. No need to touch
def get_model():
    
    global model
    json_file = open('models/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into new model
    model.load_weights("models/model_weights.h5")
    print("Loaded model from disk")
    # epochs = 30
    # batch_size = 32
    # init_lr = 1e-4
    # optimizer = Adam(lr = init_lr, decay = init_lr/epochs)
    model.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])

    # model = load_model("models/model.h5")
    print("Model compiled.")


# # only for uploading image function to S3. Nothing to do with preprocessing
# def upload_file(imageFile):
#     file = imageFile
#     """
#         These attributes are also available

#         file.filename               # The actual name of the file
#         file.content_type
#         file.content_length
#         file.mimetype

#     """

#     # if no file name then select a file
#     if file.filename == "":
#         return "Please select a file"

#     # D.
#     if file:
#         file.filename = secure_filename(file.filename)
#         output = upload_file_to_s3(file)
#         return "https://" + S3_BUCKET + ".s3." + S3_REGION + ".amazonaws.com/" + output
#     else:
#         return null


# preprocessing function. Here is where everything starts
def convert_to_ela_image(path, quality):
    temp_filename = "temp_file_name.jpg"
    ela_filename = "temp_ela.png"
    response = requests.get(path)
    # s3 se fetch image ko
    image = Image.open(BytesIO(response.content)).convert("RGB")

    # saving local
    image.save(temp_filename, "JPEG", quality=quality)
    temp_image = Image.open(temp_filename)

    ela_image = ImageChops.difference(image, temp_image)

    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff

    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

    return ela_image


def prepare_image(image_path, image_size=(128, 128)):
    return (
        np.array(convert_to_ela_image(image_path, 90).resize(image_size)).flatten() / 2
    )


def preprocess_image(image_path, target_size):

    # this step is already happening in ela function
    # if image.mode!='RGB':
    #     image = image.convert('RGB')
    image = prepare_image(image_path, target_size)
    image = image.reshape(-1, 128, 128, 3)
    # image=img_to_array(image)
    # image=np.expand_dims(image,axis=0)
    return image


print("Loading Model...")
get_model()


# Heroku
# from flask_heroku import Heroku
# heroku = Heroku(app)

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("fromPredict"):
        session["fromPredict"] = False
    elif session.get("prediction"):
        session.pop("prediction")
        session.pop("confidence")
        
    if not session.get("logged_in"):
        form = forms.LoginForm(request.form)
        if request.method == "POST":
            username = request.form["username"].lower()
            password = request.form["password"]
            if form.validate():
                if helpers.credentials_valid(username, password):
                    session["logged_in"] = True
                    session["username"] = username
                    return json.dumps({"status": "Login successful"})
                return json.dumps({"status": "Invalid user/pass"})
            return json.dumps({"status": "Both fields required"})
        return render_template("login.html", form=form)
    user = helpers.get_user()
    return render_template("home.html", user=user)


@app.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect(url_for("login"))


# ------------------hello----------------------------------#


@app.route("/hello", methods=["POST"])
def hello():
    form = forms.HelloForm(request.form)
    if request.method == "POST":
        name = request.form["name"]
        return json.dumps({"greeting": "Hello, " + name + "!"})


# -------- Signup ---------------------------------------------------------- #
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if not session.get("logged_in"):
        form = forms.LoginForm(request.form)
        if request.method == "POST":
            username = request.form["username"].lower()
            password = helpers.hash_password(request.form["password"])
            email = request.form["email"]
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session["logged_in"] = True
                    session["username"] = username
                    return json.dumps({"status": "Signup successful"})
                return json.dumps({"status": "Username taken"})
            return json.dumps({"status": "User/Pass required"})
        return render_template("login.html", form=form)
    return redirect(url_for("login"))


# ----------------Predict------------------------------------------------------#
@app.route("/predict", methods=["POST"])
def predict():
    if session.get("logged_in"):
        if request.method == "POST":
            if(os.path.exists('static/assets/temp1.png')):        
                os.remove('static/assets/temp1.png')
                print("File Removed!")


            if "image" not in request.files:
                return "No image key in request.files"

            imageFile = request.files["image"]

            # upload to S3 and get the URL
            image = upload_file(imageFile)

            print(image)

            processed_image = preprocess_image(image, target_size=(128, 128))

            # preprocessing done here. Prediction stage
            prediction = model.predict(processed_image)
            y_pred_class = np.argmax(prediction, axis=1)[0]
            class_names = ["fake", "real"]

            #segmented image prediction
            segment_image(image)

            print(
                f"Class: {class_names[y_pred_class]} Confidence: {np.amax(prediction) * 100:0.2f}"
            )
            print(type(prediction), type(np.amax(prediction)))
            pred = {}
            session["prediction"] = class_names[y_pred_class]
            session["confidence"] = float(np.amax(prediction) * 100)
            session["fromPredict"] = True
            session["imageURL"] = image
            # session["segmentImageURL"] = segmentImage
            # return json.dumps(
            #     {
            #         "prediction": class_names[y_pred_class],
            #         "confidence": float(np.amax(prediction) * 100),
            #     }
            # )
            return redirect(url_for("login"))
    return redirect(url_for("login"))


# -------- Settings ---------------------------------------------------------- #
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if session.get("logged_in"):
        if request.method == "POST":
            password = request.form["password"]
            if password != "":
                password = helpers.hash_password(password)
            email = request.form["email"]
            helpers.change_user(password=password, email=email)
            return json.dumps({"status": "Saved"})
        user = helpers.get_user()
        return render_template("settings.html", user=user)
    return redirect(url_for("login"))


# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host="0.0.0.0")
