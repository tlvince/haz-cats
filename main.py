#!/usr/bin/env python3

import argparse
import logging
import numpy as np
import requests
import tensorflow as tf

from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO
from urllib.parse import urljoin

def download_image(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image = image.resize((224, 224))
    return image

def is_cat(image, model):
    image = tf.keras.preprocessing.image.img_to_array(image)
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    image = np.expand_dims(image, axis=0)

    verbose = 1 if logging.getLogger().getEffectiveLevel() == logging.DEBUG else 0
    preds = model.predict(image, verbose=verbose)
    decoded_preds = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=3)[0]
    logging.debug(f"Predictions: {decoded_preds}")

    cat_labels = ['tabby', 'tiger_cat', 'persian_cat', 'siamese_cat', 'egyptian_cat']
    return any(pred[1].lower() in cat_labels for pred in decoded_preds)

def process_page(url, model):
    logging.info(f"Processing page: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    images = soup.find_all('img')

    for img in images:
        img_url = img.get('src')
        if img_url:
            img_url = urljoin(url, img_url)
            logging.debug(f"Downloading image from: {img_url}")
            image = download_image(img_url)
            if is_cat(image, model):
                logging.info(f"Cat image found: {img_url}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process pages and detect cat images.')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level')
    parser.add_argument('url', type=str, help='URL of the page to process')
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level), format='%(asctime)s - %(levelname)s - %(message)s')

    logging.debug("Loading TensorFlow model...")
    model = tf.keras.applications.MobileNetV2(weights='imagenet', input_shape=(224, 224, 3))

    process_page(args.url, model)
