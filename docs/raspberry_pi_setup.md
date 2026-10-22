# LUMI Voice Assistant — Raspberry Pi 5 Deployment Guide

## Target Environment

- **Hardware**: Raspberry Pi 5 (4GB or 8GB recommended)
- **OS**: Ubuntu 24.04 LTS (arm64) or Raspberry Pi OS (64-bit)
- **Python**: 3.10+
- **ROS 2**: Jazzy Jalisco (optional)
- **Audio**: USB microphone + USB speaker/3.5mm audio

## ⚠️ Important Notes

- The Pi 5 has **limited RAM and CPU** compared to a laptop.
- Large Whisper models (medium, large) will be **very slow or impossible**.
- Local LLM inference may be **impractical** — use remote inference.
- Always test on the Pi after developing on laptop.

## Step 1: System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install audio and build dependencies
sudo apt install -y \
    portaudio19-dev \
    libsndfile1 \
    python3-venv \
    python3-pip \
    git \
    alsa-utils

# Add user to audio group
sudo usermod -aG audio $USER
```

## Step 2: Clone and Install

```bash
git clone https://github.com/YOUR_USERNAME/lumi-voice-assistant.git
cd lumi-voice-assistant

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -e .
```

## Step 3: Audio Device Configuration

```bash
# List audio devices
arecord -l   # Input devices
aplay -l     # Output devices

# Test microphone
arecord -d 3 -f S16_LE -r 16000 test.wav

# Test speaker
aplay test.wav

# Check with Python
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### USB Audio Setup

1. Plug in USB microphone and/or USB speaker
2. Run `arecord -l` and `aplay -l` to find device numbers
3. Set device indices in `config/user.yaml`:

```yaml
audio_input:
    device_index: 1  # Your USB mic index
audio_output:
    device_index: 2  # Your USB speaker index
```

### Bluetooth Audio

⚠️ Bluetooth audio may have latency issues and pairing complexities.
- Use PulseAudio or PipeWire for Bluetooth audio management
- A2DP profile is needed for output; HSP/HFP for microphone
- Expect 100-500ms additional latency
- **Recommendation**: Use wired USB audio for reliability

## Step 4: Model Configuration for Pi 5

Create `config/user.yaml`:

```yaml
# Raspberry Pi 5 optimized settings
stt:
    model_size: "tiny"       # Only tiny/base feasible on Pi 5
    device: "cpu"
    compute_type: "int8"     # Required for ARM CPU
    language: "en"

llm:
    backend: "ollama"
    ollama:
        # Option A: Remote Ollama on a more powerful machine
        host: "http://192.168.1.100:11434"  # Your laptop/server IP
        model: "gemma3:1b"
        timeout_s: 120

        # Option B: Local Ollama (very slow, only tiny models)
        # host: "http://localhost:11434"
        # model: "tinyllama:latest"

tts:
    voice_model: "en_US-lessac-medium"
    length_scale: 1.0
```

### Model Profiles

| Profile | STT Model | LLM | Notes |
|---------|-----------|-----|-------|
| **Laptop Dev** | `small` / `base` | Local Ollama `gemma3:1b` | Full local operation |
| **Pi 5 Local** | `tiny` | Local Ollama `tinyllama` | Slow but functional |
| **Pi 5 Remote** | `tiny` | Remote Ollama on LAN | Best quality + speed |

### Remote Ollama Setup

On your laptop/server:
```bash
# Allow network access
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# Pull model
ollama pull gemma3:1b
```

On the Pi:
```yaml
# config/user.yaml
llm:
    ollama:
        host: "http://<laptop-ip>:11434"
```

## Step 5: Install Piper TTS

```bash
# Download Piper for ARM64
wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz
tar xzf piper_linux_aarch64.tar.gz
sudo cp piper/piper /usr/local/bin/

# Download a voice model
mkdir -p voices
wget -O voices/en_US-lessac-medium.onnx \
    https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget -O voices/en_US-lessac-medium.onnx.json \
    https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

Update config:
```yaml
tts:
    voice_model_path: "voices/en_US-lessac-medium.onnx"
```

## Step 6: Install Ollama (if running locally)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull tinyllama
```

## Step 7: Running

### Standalone GUI
```bash
source venv/bin/activate
python -m lumi_voice.app
```

### Headless Mode
```bash
python -m lumi_voice.app --headless
```

### ROS 2 Bridge
```bash
# Source ROS 2
source /opt/ros/jazzy/setup.bash
source venv/bin/activate
python -m lumi_voice.app --ros2
```

## Step 8: Auto-Start (Optional)

Create a systemd service:
```ini
# /etc/systemd/system/lumi-voice.service
[Unit]
Description=LUMI Voice Assistant
After=network.target sound.target

[Service]
User=pi
WorkingDirectory=/home/pi/lumi-voice-assistant
ExecStart=/home/pi/lumi-voice-assistant/venv/bin/python -m lumi_voice.app --headless
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable lumi-voice
sudo systemctl start lumi-voice
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ALSA lib` errors | Install `alsa-utils`, check `arecord -l` |
| No input devices | Check USB mic connection, `sudo usermod -aG audio $USER` |
| Model download fails | Check internet, disk space (models need 100MB-4GB) |
| Out of memory | Use `tiny` model, reduce `max_history`, use remote LLM |
| Permission denied | `chmod +x` scripts, check file ownership |
| Slow transcription | Use `tiny` model with `int8` compute type |
| Piper not found | Ensure it's in PATH or set `voice_model_path` |
| ROS 2 not found | Source `/opt/ros/jazzy/setup.bash` before running |
