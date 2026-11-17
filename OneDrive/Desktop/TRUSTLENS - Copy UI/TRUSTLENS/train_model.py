import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from sklearn.model_selection import train_test_split
import os


DATASET_PATH = "dataset"


IMG_SIZE = 224
BATCH_SIZE = 32


datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)


train_data = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="training"
)


validation_data = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="validation"
)



model = Sequential()


model.add(
    Conv2D(
        32,
        (3,3),
        activation="relu",
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
)

model.add(MaxPooling2D())


model.add(
    Conv2D(
        64,
        (3,3),
        activation="relu"
    )
)

model.add(MaxPooling2D())


model.add(Flatten())


model.add(
    Dense(
        128,
        activation="relu"
    )
)


model.add(Dropout(0.5))


model.add(
    Dense(
        1,
        activation="sigmoid"
    )
)



model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)



history = model.fit(
    train_data,
    validation_data=validation_data,
    epochs=10
)



model.save("trustlens_model.h5")


print("Model training completed!")
print("Saved as trustlens_model.h5")