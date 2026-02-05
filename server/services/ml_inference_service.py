"""
EfficientNet inference service for railway issue image classification.
Uses ml/predict when model exists; returns category and confidence for complaint flow.
"""
import os
import sys

# Add project root so ml.predict can be imported
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

_model_cache = None  # (model, class_names, class_indices)


def _load_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    try:
        from ml.predict import load_model_and_classes, MODEL_PATH, CLASSES_PATH
        from config import ML_MODEL_PATH, ML_CLASSES_PATH
        model_path = ML_MODEL_PATH if os.path.exists(ML_MODEL_PATH) else MODEL_PATH
        classes_path = ML_CLASSES_PATH if os.path.exists(ML_CLASSES_PATH) else CLASSES_PATH
        model, class_names, class_indices = load_model_and_classes(model_path, classes_path)
        if model is not None:
            _model_cache = (model, class_names, class_indices)
        return _model_cache
    except Exception as e:
        print(f"[WARN] ML model load failed: {e}")
        return None


def predict_issue_from_image(image_bytes: bytes) -> dict:
    """
    Run EfficientNet on image bytes. Returns:
    - issue_category: class name (e.g. crowd, trash, food)
    - confidence: float 0-1
    - all_probs: dict class -> probability
    - model_used: 'efficientnet' or None if failed
    """
    loaded = _load_model()
    if loaded is None:
        return {"issue_category": None, "confidence": 0.0, "all_probs": {}, "model_used": None}
    model, class_names, _ = loaded
    try:
        from ml.predict import predict, preprocess_image
        # preprocess_image accepts bytes
        category, confidence, probs = predict(image_bytes, model=model, class_names=class_names)
    except Exception as e:
        print(f"[WARN] ML predict failed: {e}")
        return {"issue_category": None, "confidence": 0.0, "all_probs": {}, "model_used": "efficientnet"}
    # Map EfficientNet class names to display/priority (optional)
    return {
        "issue_category": category,
        "confidence": float(confidence),
        "all_probs": probs,
        "model_used": "efficientnet",
    }


def map_effnet_to_department(category: str) -> str:
    """Map EfficientNet class to suggested department."""
    m = {
        "crowd": "Railway Administration / Crowd Management",
        "dirty_toilet": "Housekeeping & Sanitation",
        "fire_smoke": "Emergency Services / RPF",
        "food": "Catering & Railway Administration",
        "trash": "Housekeeping & Sanitation",
    }
    return m.get(category, "Railway Administration")


def map_effnet_to_priority(category: str) -> str:
    """Map EfficientNet class to priority."""
    if category in ("fire_smoke",):
        return "CRITICAL"
    if category in ("crowd",):
        return "HIGH"
    return "MEDIUM"
