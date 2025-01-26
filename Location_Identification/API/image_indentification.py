from io import BytesIO
import tensorflow as tf
import os
from PIL import Image
import numpy as np


class Image_Identification:
    model_path = "Location_Identification/API/best_LI_model_20241125-053014.keras"
    class_names = ['botanical_gardens', 'galle_fort', 'galleface', 'hortain_plains', 'mirissa_beach', 'ninearch',
                   'pidurangala', 'sigiriya', 'temple_of_tooth', 'yala']

    def __init__(self) -> None:
        self.model = tf.keras.models.load_model(self.model_path)

    def preprocess(self, image):
        image = Image.open(BytesIO(image))
        image = image.resize((224, 224))
        image = np.array(image)
        image = np.expand_dims(image, axis=0)

        return image

    def predict(self, image):
        image = self.preprocess(image)
        prediction = self.model.predict(tf.convert_to_tensor(image))
        prediction = self.class_names[np.argmax(prediction)]

        return {"prediction": prediction}
