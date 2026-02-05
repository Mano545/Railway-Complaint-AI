"""
Railway Issue Model - Inference Helper
=======================================
Load trained model and predict issue category from image.
Ready for integration into Flask backend as alternative to Gemini.
"""

import os
import json
import numpy as np
from PIL import Image

# Default paths
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "railway_issue_model.h5")
CLASSES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "railway_model_classes.json")

# Model input size (must match training)
IMG_SIZE = (300, 300)


def load_model_and_classes(model_path=None, classes_path=None):
    """
    Load trained model and class mapping.
    Returns (model, class_names, class_indices) or (None, [], {}) if not found.
    """
    model_path = model_path or MODEL_PATH
    classes_path = classes_path or CLASSES_PATH

    if not os.path.exists(model_path) or not os.path.exists(classes_path):
        return None, [], {}

    try:
        from tensorflow import keras

        model = keras.models.load_model(model_path)
        with open(classes_path) as f:
            data = json.load(f)
        class_names = data["classes"]
        class_indices = data["indices"]
        return model, class_names, class_indices
    except Exception as e:
        print(f"[WARN] Could not load ML model: {e}")
        return None, [], {}


def preprocess_image(image_input):
    """
    Preprocess image for model input.
    Accepts: file path (str), PIL Image, numpy array (HWC, 0-255), or bytes.
    """
    if isinstance(image_input, str):
        img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    elif isinstance(image_input, np.ndarray):
        img = Image.fromarray(image_input.astype(np.uint8)).convert("RGB")
    elif isinstance(image_input, bytes):
        from io import BytesIO
        img = Image.open(BytesIO(image_input)).convert("RGB")
    else:
        raise ValueError("image_input must be path, PIL Image, numpy array, or bytes")

    img = img.resize(IMG_SIZE)
    arr = np.array(img) / 255.0
    return np.expand_dims(arr, axis=0)


def predict(image_input, model=None, class_names=None):
    """
    Predict railway issue category from image.
    Returns: (class_name, confidence, all_probs_dict)
    """
    if model is None or not class_names:
        model, class_names, _ = load_model_and_classes()
    if model is None:
        return None, 0.0, {}

    x = preprocess_image(image_input)
    probs = model.predict(x, verbose=0)[0]
    idx = np.argmax(probs)
    return class_names[idx], float(probs[idx]), dict(zip(class_names, probs.tolist()))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Predict railway issue from image")
    parser.add_argument("image", type=str, help="Path to image file")
    args = parser.parse_args()

    model, class_names, _ = load_model_and_classes()
    if model is None:
        print("Error: Model not found. Train first with: python ml/train_railway_model.py")
        exit(1)

    category, confidence, probs = predict(args.image, model, class_names)
    print(f"Prediction: {category} ({confidence:.2%})")
    print("All classes:", {k: f"{v:.2%}" for k, v in probs.items()})
