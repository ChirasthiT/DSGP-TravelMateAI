from io import BytesIO
import tensorflow as tf
from PIL import Image
import numpy as np
import os


class Image_Identification:
    current_directory = os.path.dirname(os.path.realpath(__file__))
    model_path = os.path.join(current_directory, "best_LI_model_20241125-053014.keras")
    class_names = ['botanical_gardens', 'galle_fort', 'galleface', 'hortain_plains', 'mirissa_beach', 'ninearch',
                   'pidurangala', 'sigiriya', 'temple_of_tooth', 'yala']
    threshold = 0.5

    def __init__(self) -> None:
        self.model = tf.keras.models.load_model(self.model_path)

    def preprocess(self, image):
        image = Image.open(BytesIO(image))
        image = image.resize((224, 224))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        image = np.array(image)
        image = np.expand_dims(image, axis=0)

        return image

    def predict(self, image):
        image = self.preprocess(image)
        prediction_num = self.model.predict(tf.convert_to_tensor(image))
        prediction = self.class_names[np.argmax(prediction_num)]

        return "Unknown" if np.max(prediction_num) < self.threshold else prediction

