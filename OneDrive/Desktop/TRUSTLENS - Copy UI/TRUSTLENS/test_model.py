

import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np


model = tf.keras.models.load_model("trustlens_model.h5")


def predict_receipt(img_path):

    img = image.load_img(
        img_path,
        target_size=(224,224)
    )


    img_array = image.img_to_array(img)


    img_array = np.expand_dims(
        img_array,
        axis=0
    )


    img_array = img_array / 255.0


    prediction = model.predict(img_array)


    confidence = float(prediction[0][0])


    if confidence > 0.5:

        result = "Real"
        score = confidence * 100

    else:

        result = "Fake"
        score = (1-confidence) * 100


    return result, round(score,2)



result, score = predict_receipt(
    "static/uploads/testimage py.png"
)


print("Prediction:", result)

print("Confidence:", score, "%")