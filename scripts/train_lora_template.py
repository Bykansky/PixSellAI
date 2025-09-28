"""
Template script: how to train a LoRA adapter from 'liked' images.
This is a template (not a full training script). Use it as a starting point.

Instructions:
- Prepare dataset folder with images and captions
- Install accelerate, diffusers, transformers, peft
- Edit MODEL_NAME and OUTPUT_DIR
- Run with `python scripts/train_lora_template.py`
"""

import os

MODEL_NAME = 'stabilityai/sdxl-base'  # change to desired base
OUTPUT_DIR = os.getenv('LORA_OUTPUT', './lora-checkpoints/brand-001')

def main():
    print('This is a template. Replace content with actual training loop.')
    print('Base model:', MODEL_NAME)
    print('Output will be saved to', OUTPUT_DIR)

if __name__ == '__main__':
    main()
