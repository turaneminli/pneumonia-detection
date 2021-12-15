from __future__ import division, print_function
# coding=utf-8
import os
import numpy as np
from waitress import serve

# Tensorflow.Keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

# Custom metric
from f1_score import f1_custom

# For loading model which is on internet 
import gdown

# Define a flask app
app = Flask(__name__)

url_link = 'https://drive.google.com/uc?id=1St5SRPxmPyx-zPYlkrsYJzY-3or3tevK'

gdown.download(
        url_link, 'model_vgg.h5', quiet=False)
        
# Model saved with Keras model.save()
MODEL_PATH = './model_vgg.h5'

# Load your trained model
model = load_model(MODEL_PATH, custom_objects={"f1_custom":f1_custom})        

def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    img = image.img_to_array(img) / 255
    img = np.expand_dims(img, axis=0)

    preds = (model.predict(img) >= 0.5).flatten().astype("int64")[0]
    return preds


def decode(num):
    if num==0: 
        return "Our algorithm says that it is healthy 😉"
    else:
        return "Unfortunately, our algorithm detected pneumonia 😟"


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)

        # Process your result for human
        preds = model_predict(file_path, model)
        pred_class = decode(preds)
        return pred_class

    return None


if __name__ == '__main__':
    # app.run(debug=True)
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))