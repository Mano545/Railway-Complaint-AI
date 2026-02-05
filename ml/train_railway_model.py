"""
Railway Issue Image Classification Model - Training Script
===========================================================
High-accuracy image classification for railway issue detection.
Uses transfer learning with EfficientNetB3 for optimal accuracy.
This model is an offline-trained alternative to Gemini Vision AI.
"""

import os
import json
import argparse
from datetime import datetime

import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

# =============================================================================
# CONFIGURATION
# =============================================================================

# Default paths - supports both datasets/train/ and server/dataset/train/
DEFAULT_TRAIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets", "train")
FALLBACK_TRAIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "server", "dataset", "train")

# Model hyperparameters (optimized for accuracy)
IMG_SIZE = (300, 300)  # EfficientNetB3 default input
BATCH_SIZE = 16
INITIAL_EPOCHS = 20  # Phase 1: frozen base
FINE_TUNE_EPOCHS = 30  # Phase 2: unfrozen fine-tuning
LEARNING_RATE = 1e-4
FINE_TUNE_LR = 1e-5
VALIDATION_SPLIT = 0.2  # Split from train if no val folder
SEED = 42

# Output
MODEL_SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "railway_issue_model.h5")
CLASS_NAMES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "railway_model_classes.json")


# =============================================================================
# MODEL CHOICE JUSTIFICATION
# =============================================================================
"""
EfficientNetB3 was chosen over ResNet50 and DenseNet121 for the following reasons:

1. ACCURACY: EfficientNet achieves state-of-the-art accuracy on ImageNet with
   compound scaling (depth, width, resolution). B3 offers excellent accuracy
   without excessive computational cost.

2. TRANSFER LEARNING: Pre-trained on 14M+ images, captures rich visual features
   (edges, textures, patterns) that transfer well to railway scene classification.

3. EFFICIENCY: Better accuracy-per-parameter ratio than ResNet/DenseNet. B3 is
   the sweet spot - more accurate than B0-B2, faster than B4-B7.

4. INPUT SIZE: 300x300 works well for railway images (stations, coaches, etc.)
   without excessive memory usage.

5. PRODUCTION READY: Widely used, well-documented, stable in Keras/TensorFlow.
"""


def _count_images(directory):
    """Count image files in class subfolders."""
    ext = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".jfif")
    count = 0
    if not os.path.exists(directory):
        return 0
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isdir(path):
            for f in os.listdir(path):
                if f.lower().endswith(ext):
                    count += 1
    return count


def get_train_directory():
    """Get training directory - prefer the one that has images."""
    default_count = _count_images(DEFAULT_TRAIN_DIR)
    fallback_count = _count_images(FALLBACK_TRAIN_DIR)
    if default_count > 0 and default_count >= fallback_count:
        return DEFAULT_TRAIN_DIR
    if fallback_count > 0:
        return FALLBACK_TRAIN_DIR
    if os.path.exists(DEFAULT_TRAIN_DIR) or os.path.exists(FALLBACK_TRAIN_DIR):
        raise ValueError(
            f"No images found in training folders. Add images to:\n"
            f"  - {DEFAULT_TRAIN_DIR}\n"
            f"  - {FALLBACK_TRAIN_DIR}\n"
            f"Subfolders: crowd/, dirty_toilet/, fire_smoke/, food/, trash/\n"
            f"Supported: .jpg, .jpeg, .png, .gif, .webp, .jfif"
        )
    raise FileNotFoundError(
        f"Training data not found. Create one of:\n"
        f"  - {DEFAULT_TRAIN_DIR}\n"
        f"  - {FALLBACK_TRAIN_DIR}\n"
        f"With subfolders: crowd/, dirty_toilet/, fire_smoke/, food/, trash/"
    )


def create_data_generators(train_dir):
    """
    Create train and validation data generators with augmentation.
    Uses validation_split when no separate val folder exists.
    """
    # Data augmentation for training - improves generalization
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        zoom_range=0.2,
        brightness_range=[0.8, 1.2],
        horizontal_flip=True,
        fill_mode="nearest",
        validation_split=VALIDATION_SPLIT,
    )

    # Validation: only rescale, no augmentation
    val_datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=VALIDATION_SPLIT)

    train_ds = train_datagen.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        seed=SEED,
        shuffle=True,
    )

    val_ds = val_datagen.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        seed=SEED,
        shuffle=False,
    )

    return train_ds, val_ds, train_ds.class_indices


def build_model(num_classes):
    """
    Build EfficientNetB3-based model with custom classification head.
    Phase 1: Base frozen. Phase 2: Base unfrozen for fine-tuning.
    """
    # Load pretrained EfficientNetB3 (ImageNet weights)
    base_model = EfficientNetB3(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
        pooling="avg",
    )

    # Freeze base model initially
    base_model.trainable = False

    # Custom classification head
    inputs = keras.Input(shape=(*IMG_SIZE, 3))
    x = base_model(inputs, training=False)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = Model(inputs, outputs)
    return model, base_model


def compile_model(model):
    """Compile with categorical cross-entropy and accuracy metrics."""
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )


def get_callbacks():
    """Training callbacks for better convergence and early stopping."""
    return [
        EarlyStopping(
            monitor="val_loss",
            patience=8,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=4,
            min_lr=1e-7,
            verbose=1,
        ),
        ModelCheckpoint(
            filepath=MODEL_SAVE_PATH.replace(".h5", "_best.h5"),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
    ]


def main():
    parser = argparse.ArgumentParser(description="Train Railway Issue Classification Model")
    parser.add_argument("--train-dir", type=str, default=None, help="Path to training data")
    parser.add_argument("--epochs", type=int, default=INITIAL_EPOCHS, help="Initial training epochs")
    parser.add_argument("--fine-tune-epochs", type=int, default=FINE_TUNE_EPOCHS, help="Fine-tuning epochs")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Batch size")
    parser.add_argument("--no-fine-tune", action="store_true", help="Skip fine-tuning phase")
    args = parser.parse_args()

    # Resolve training directory
    train_dir = args.train_dir or get_train_directory()
    print(f"\n[INFO] Using training data from: {train_dir}")
    print(f"[INFO] Model will be saved to: {MODEL_SAVE_PATH}\n")

    # Create data generators
    train_ds, val_ds, class_indices = create_data_generators(train_dir)
    num_classes = len(class_indices)
    class_names = list(class_indices.keys())

    print(f"[INFO] Classes: {class_names}")
    print(f"[INFO] Training samples: {train_ds.samples}")
    print(f"[INFO] Validation samples: {val_ds.samples}")

    # Compute class weights to handle imbalance (helps minority classes like dirty_toilet)
    classes = np.unique(train_ds.classes)
    weights = compute_class_weight(
        "balanced", classes=classes, y=train_ds.classes
    )
    class_weight = dict(zip(classes, weights))
    print(f"[INFO] Class weights (balanced): {dict(zip(class_names, weights))}\n")

    # Build model
    model, base_model = build_model(num_classes)
    compile_model(model)
    model.summary()

    # Phase 1: Train with frozen base
    print("\n" + "=" * 60)
    print("PHASE 1: Training with frozen base (transfer learning)")
    print("=" * 60)

    history1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=get_callbacks(),
        class_weight=class_weight,
        verbose=1,
    )

    # Phase 2: Fine-tune (unfreeze last layers)
    if not args.no_fine_tune:
        print("\n" + "=" * 60)
        print("PHASE 2: Fine-tuning (unfreeze base layers)")
        print("=" * 60)

        base_model.trainable = True
        # Unfreeze last 30% of layers
        for layer in base_model.layers[:-int(len(base_model.layers) * 0.3)]:
            layer.trainable = False

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=FINE_TUNE_LR),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )

        history2 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=args.fine_tune_epochs,
            callbacks=get_callbacks(),
            class_weight=class_weight,
            verbose=1,
        )

    # Save final model
    model.save(MODEL_SAVE_PATH)
    print(f"\n[OK] Model saved to: {MODEL_SAVE_PATH}")

    # Save class names for inference
    with open(CLASS_NAMES_PATH, "w") as f:
        json.dump({"classes": class_names, "indices": class_indices}, f, indent=2)
    print(f"[OK] Class mapping saved to: {CLASS_NAMES_PATH}")

    # Final evaluation
    loss, accuracy = model.evaluate(val_ds)
    print(f"\n[RESULT] Final validation accuracy: {accuracy:.4f}")
    print(f"[RESULT] Final validation loss: {loss:.4f}")


if __name__ == "__main__":
    main()
