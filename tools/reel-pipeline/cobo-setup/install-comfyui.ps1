# ComfyUI + AnimateDiff Installer for Cobo (GTX 1080 Ti)
# Run this AFTER install-wan2gp.ps1
# This gives you image gen + animation in one UI

Write-Host "=== COMFYUI + ANIMATEDIFF INSTALLER ===" -ForegroundColor Cyan

$COMFY_DIR = "C:\behique\ComfyUI"

# Clone ComfyUI
Write-Host "[1/4] Cloning ComfyUI..." -ForegroundColor Green
if (Test-Path "$COMFY_DIR\.git") {
    Write-Host "  Already cloned, pulling latest..." -ForegroundColor Yellow
    Set-Location $COMFY_DIR
    git pull
} else {
    git clone https://github.com/comfyanonymous/ComfyUI.git $COMFY_DIR
    Set-Location $COMFY_DIR
}

# Create venv and install
Write-Host "[2/4] Setting up Python environment..." -ForegroundColor Green
python -m venv venv
& "$COMFY_DIR\venv\Scripts\Activate.ps1"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# Install AnimateDiff
Write-Host "[3/4] Installing AnimateDiff..." -ForegroundColor Green
Set-Location "$COMFY_DIR\custom_nodes"
if (-not (Test-Path "ComfyUI-AnimateDiff-Evolved")) {
    git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
}
Set-Location ComfyUI-AnimateDiff-Evolved
pip install -r requirements.txt

# Download motion model
Write-Host "[4/4] Downloading AnimateDiff motion model..." -ForegroundColor Green
$modelDir = "$COMFY_DIR\custom_nodes\ComfyUI-AnimateDiff-Evolved\models"
New-Item -ItemType Directory -Force -Path $modelDir | Out-Null
$modelUrl = "https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt"
if (-not (Test-Path "$modelDir\mm_sd_v15_v2.ckpt")) {
    Write-Host "  Downloading mm_sd_v15_v2.ckpt (~1.8GB)..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $modelUrl -OutFile "$modelDir\mm_sd_v15_v2.ckpt"
}

# Create start script
@"
@echo off
echo Starting ComfyUI on port 8188...
cd /d C:\behique\ComfyUI
call venv\Scripts\activate.bat
python main.py --listen 0.0.0.0 --port 8188
"@ | Out-File -FilePath "$COMFY_DIR\start_comfyui.bat" -Encoding ascii

Write-Host ""
Write-Host "=== COMFYUI INSTALLED ===" -ForegroundColor Green
Write-Host "Start: C:\behique\ComfyUI\start_comfyui.bat" -ForegroundColor Cyan
Write-Host "Access: http://192.168.0.151:8188" -ForegroundColor Cyan
Write-Host ""
Write-Host "You also need an SD 1.5 checkpoint model:" -ForegroundColor Yellow
Write-Host "  Download from https://huggingface.co/runwayml/stable-diffusion-v1-5" -ForegroundColor White
Write-Host "  Place in C:\behique\ComfyUI\models\checkpoints\" -ForegroundColor White
