# Model Directory

This directory contains the trained models used by the application.

## Structure

```bash
models/
└── distilbert_classifier/
    ├── model.safetensors    # The trained model weights
    ├── tokenizer.json       # Tokenizer configuration
    └── config.json          # Model configuration
```

## Getting the Models

The model files are not included in the repository due to their size. You can:

1. Download pre-trained models:

```bash
python scripts/download_model.py
```

2. Train your own:

```bash
python training/train_distilbert.py --data_path data/messages.csv
```

## Deployment

When deploying:

1. First upload model files to cloud storage
2. Update URLs in `scripts/download_model.py`
3. The Dockerfile will handle downloading during build
