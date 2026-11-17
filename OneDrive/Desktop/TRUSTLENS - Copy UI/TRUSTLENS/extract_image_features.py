import os
import numpy as np
import pandas as pd
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image

# Load MobileNetV2 as a feature extractor
base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    pooling="avg"
)

dataset = "dataset"

features = []
labels = []
filenames = []

for label in ["Real", "Fake"]:

    folder = os.path.join(dataset, label)

    for img_name in os.listdir(folder):

        img_path = os.path.join(folder, img_name)

        img = image.load_img(img_path, target_size=(224,224))

        x = image.img_to_array(img)

        x = np.expand_dims(x, axis=0)

        x = preprocess_input(x)

        feature = base_model.predict(x, verbose=0)

        features.append(feature.flatten())

        labels.append(label)

        filenames.append(img_name)

# Create DataFrame
df = pd.DataFrame(features)

df["label"] = labels
df["filename"] = filenames

os.makedirs("results", exist_ok=True)
df.to_csv("results/image_features.csv", index=False)

print("Image features extracted successfully!")
print("Shape:", df.shape)