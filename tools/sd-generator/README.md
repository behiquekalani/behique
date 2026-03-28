# SD Generator - Stable Diffusion Pipeline for Cobo

Auto-installer and image generation pipeline for Cobo (Windows, GTX 1080 Ti 11GB).
Connects to AUTOMATIC1111 Stable Diffusion WebUI via API.

## Quick Start

### 1. Install (on Cobo)

Copy `install_cobo.bat` to Cobo and run it. It will:
- Install Python 3.10 if needed
- Clone AUTOMATIC1111 WebUI to `C:\behique\stable-diffusion\`
- Download SD 1.5 base model (~4.2GB)
- Create start scripts

```
install_cobo.bat
```

### 2. Start SD WebUI

```
C:\behique\stable-diffusion\start_sd.bat       # WebUI + API
C:\behique\stable-diffusion\start_sd_api.bat    # API only (headless)
```

WebUI: http://localhost:7860
API docs: http://localhost:7860/docs

### 3. Generate Images

```bash
# Check API status
python generate.py status

# Generate from prompt
python generate.py prompt "ethereal glowing cat, cosmic background, 8k"

# List all presets
python generate.py presets

# Generate from preset category (random pick)
python generate.py preset frequency

# Generate specific preset
python generate.py preset frequency glowing_cat
```

### 4. Daily Batch

```bash
# Preview what would generate
python batch_daily.py --dry-run

# Run full batch (1 frequency + 3 social + 1 mockup)
python batch_daily.py

# Run single category
python batch_daily.py --category social

# Show Task Scheduler setup
python batch_daily.py --setup
```

## File Structure

```
sd-generator/
  install_cobo.bat     Windows installer for AUTOMATIC1111
  generate.py          Core generation library + CLI
  presets.json         20 pre-built prompts (4 categories)
  batch_daily.py       Daily automated batch generator
  output/
    frequency/         YouTube thumbnails
    social/            Instagram images
    mockup/            Product mockups
    abstract/          Background images
  logs/                Daily batch logs
```

## Preset Categories

| Category  | Count | Use Case                    | Default Size |
|-----------|-------|-----------------------------|-------------|
| frequency | 5     | YouTube frequency thumbnails | 1920x1080   |
| mockup    | 5     | Product shots for store      | 1920x1080   |
| social    | 5     | Instagram content            | 1080x1080   |
| abstract  | 5     | Backgrounds, blueprints      | 1920x1080   |

## Python API

```python
from generate import generate_image, generate_batch, generate_from_preset

# Single image
generate_image("your prompt here", width=1920, height=1080)

# From preset
generate_from_preset("frequency", "glowing_cat")

# Batch
generate_batch([
    "prompt one",
    "prompt two",
    {"prompt": "prompt three", "width": 1080, "height": 1080},
])
```

## Hardware Notes

- Model: SD 1.5 pruned (fits easily in 11GB VRAM)
- Flag: `--medvram` enabled by default (safe for 1080 Ti)
- Flag: `--xformers` enabled for faster generation
- Typical generation time: ~10-15 seconds for 1920x1080 at 30 steps

## Requirements

- Windows 10/11
- NVIDIA GPU with CUDA (GTX 1080 Ti)
- Python 3.10
- Git
- ~10GB disk space (model + WebUI)
