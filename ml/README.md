# Railway Issue ML Model

High-accuracy image classification model for railway issue detection. This is an **offline-trained alternative** to Gemini Vision AI for future deployment. **Gemini AI remains the primary system** and is not removed.

## Model Choice: EfficientNetB3

| Criterion | EfficientNetB3 | ResNet50 | DenseNet121 |
|-----------|----------------|----------|-------------|
| **Accuracy** | Best (compound scaling) | Good | Good |
| **Params** | ~12M | ~25M | ~8M |
| **Transfer learning** | Excellent | Good | Good |
| **Speed** | Balanced | Faster | Slower |
| **Choice** | ✓ Selected | - | - |

**Why EfficientNetB3:** State-of-the-art accuracy on ImageNet, excellent transfer learning, optimal accuracy-per-parameter ratio. B3 is the sweet spot between B0-B2 (less accurate) and B4-B7 (heavier).

## Dataset Structure

```
datasets/train/
├── crowd/          # Overcrowding images
├── dirty_toilet/   # Cleanliness issues
├── fire_smoke/     # Fire/smoke hazards
├── food/           # Food quality issues
└── trash/          # Waste/trash issues
```

Also supports: `server/dataset/train/` (fallback).

## Setup

```bash
# Install ML dependencies
pip install -r ml/requirements-ml.txt
```

## Training

```bash
# From project root
python ml/train_railway_model.py

# Custom paths
python ml/train_railway_model.py --train-dir datasets/train --epochs 25

# Skip fine-tuning (faster, lower accuracy)
python ml/train_railway_model.py --no-fine-tune
```

### Training Phases

1. **Phase 1 (frozen base):** Transfer learning with EfficientNetB3 base frozen. Trains only the custom head.
2. **Phase 2 (fine-tune):** Unfreezes last 30% of base layers. Fine-tunes for higher accuracy.

### Outputs

- `railway_issue_model.h5` - Final trained model
- `railway_issue_model_best.h5` - Best validation checkpoint
- `railway_model_classes.json` - Class names and indices

## Inference (Flask Integration)

```python
from ml.predict import load_model_and_classes, predict

model, class_names, _ = load_model_and_classes()
if model:
    category, confidence, probs = predict(image_path_or_array, model, class_names)
    # Use category when ML model is available
else:
    # Fall back to Gemini Vision API (current primary)
    pass
```

## Requirements

- TensorFlow >= 2.15
- Sufficient RAM/GPU for training (8GB+ recommended)
- Balanced dataset (aim for 50+ images per class)
