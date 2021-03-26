import keras
import matplotlib.pyplot as plt
from PIL import Image, ImageChops
# import cv2
import tensorflow as tf
import keras.backend as K
import os
from io import BytesIO
import requests
from keras.models import load_model
import numpy as np
from skimage.io import imread
from skimage.color import rgb2lab, lab2rgb, rgb2gray, gray2rgb
from skimage.transform import resize
from keras.models import model_from_json
from helpers import *
# import PIL


# impath = 'Tp_D_CNN_M_N_art00052_arc00030_11853.jpg'

_height = 256
_width = 256


def dice_coef(y_true, y_pred, smooth=1):
    """
    Dice = (2*|X & Y|)/ (|X|+ |Y|)
         =  2*sum(|A*B|)/(sum(A^2)+sum(B^2))
    ref: https://arxiv.org/pdf/1606.04797v1.pdf
    """
    intersection = K.sum(K.abs(y_true * y_pred), axis=-1)
    return K.mean((2. * intersection + smooth) / (K.sum(K.square(y_true), -1) + K.sum(K.square(y_pred), -1) + smooth))


def dice_coef_loss(y_true, y_pred):
    return 1-dice_coef(y_true, y_pred)


def LoadImages(img):
    arr = np.array(img)
    return arr.reshape((1, 256, 256, 3))


def ELA(img):
    original = img
    TEMP = 'ela_temp.jpg'
    scale = 10
    quality = 90
    diff = ""
    try:
        original.save(TEMP, quality=90)
        temporary = Image.open(TEMP)
        diff = ImageChops.difference(original, temporary)

    except:

        original.convert('RGB').save(TEMP, quality=90)
        temporary = Image.open(TEMP)
        diff = ImageChops.difference(original.convert('RGB'), temporary)

    d = diff.load()
    WIDTH, HEIGHT = diff.size
    for x in range(WIDTH):
        for y in range(HEIGHT):
            d[x, y] = tuple(k * scale for k in d[x, y])

    return diff


def convert_to_3_channel(img):
    arr = np.array(img)
    arr = (arr >= 0.1)*1.0
    arr = np.stack([arr, arr, arr], axis=2)
    print(arr.shape)
    arr = arr.reshape((256, 256, 3))
    return arr


def segment_image(impath):
    response = requests.get(impath)
    # s3 se fetch image ko
    img = Image.open(BytesIO(response.content)).convert("RGB")
    # img = Image.open(impath).convert('RGB')
    img = img.resize((_height, _width), Image.ANTIALIAS)

    ela_image = ELA(img)
    ela_image = imread('ela_temp.jpg')
    img = LoadImages(ela_image)


    json_file = open('models/segmentation/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("models/segmentation/model_for_json.h5")

    loaded_model.compile(loss=dice_coef_loss,
                        optimizer='adam', metrics=[dice_coef])


    predicted = loaded_model.predict(img)
    img = predicted[0]
    # img = convert_to_3_channel(img)
    print(img.shape)
    # img=Image.fromarray(img)
    
    # img = Image.fromarray((img * 255).astype(np.uint8))
    # image=plt.imsave('pred_mask.png', img)
    # img.reshape(256,256)
    mat = np.reshape(img,(256,256))

    # Creates PIL image
    img = Image.fromarray(np.uint8(mat*255) , 'L')
    img = img.save('temp.jpg')
    # img=Image.fromarray(np.uint8(mat * 255) , 'L')
    segmentImage = upload_file(img)
    return segmentImage
 
    # cv2.imwrite('pred_mask.png', img)
