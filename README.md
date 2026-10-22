# 🤖 LUMI Voice Assistant

**Speech-to-Text, Conversational AI, and Text-to-Speech for the LUMINAX Healthcare Companion Robot**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![ROS 2 Jazzy](https://img.shields.io/badge/ROS%202-Jazzy-orange.svg)](https://docs.ros.org/en/jazzy/)

LUMI Voice Assistant is a complete, modular, open-source voice pipeline that captures speech from a microphone, transcribes it, generates intelligent responses using a local LLM, and speaks the response through a selected speaker — all running locally without cloud APIs.

## ✨ Features

- 🎤 **Speech-to-Text** — OpenAI Whisper via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (configurable model sizes)
- 🧠 **Conversational AI** — Local LLM via [Ollama](https://ollama.com) with streaming responses
- 🔊 **Text-to-Speech** — [Piper TTS](https://github.com/rhasspy/piper) for fast, offline speech synthesis
- 🎚️ **Audio Device Selection** — Enumerate, select, and test microphones and speakers from the GUI
- 💬 **Push-to-Talk & Continuous Listening** — Two interaction modes with voice activity detection
- 🖥️ **Desktop GUI** — PySide6 interface with dark theme, real-time audio levels, and conversation history
- 🤖 **ROS 2 Bridge** — Optional integration with ROS 2 Jazzy for the LUMINAX robot
- ⚙️ **Fully Configurable** — YAML-based settings with GUI controls and persistent preferences
- 🏥 **Healthcare Safety** — System prompt enforces medical safety boundaries

## 🏗️ Architecture

```
Microphone → Audio Capture → VAD → STT (Whisper) → LLM (Ollama) → TTS (Piper) → Speaker
                                                       ↑                           ↓
                                                 Conversation              Audio Playback
                                                   History
```

See [docs/architecture.md](docs/architecture.md) for the full architecture documentation.

## 📋 Prerequisites

| Component | Required | Purpose |
|-----------|----------|---------|
| **Python 3.10+** | ✅ | Runtime |
| **Ollama** | ✅ | Local LLM inference |
| **Piper TTS** | ✅ | Speech synthesis |
| **PortAudio** | ✅ | Audio I/O (usually auto-installed) |
| **ROS 2 Jazzy** | ❌ Optional | Robot integration |

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/lumi-voice-assistant.git
cd lumi-voice-assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

**Linux additional requirements:**
```bash
sudo apt install portaudio19-dev libsndfile1
```

### 4. Install and Start Ollama

Download from [ollama.com/download](https://ollama.com/download), then:

```bash
# Start the server
ollama serve

# Pull a model (in another terminal)
ollama pull gemma3:1b
```

### 5. Install Piper TTS

Download the appropriate binary from [Piper Releases](https://github.com/rhasspy/piper/releases):

- **Windows**: Download `piper_windows_amd64.zip`, extract, add to PATH
- **Linux**: Download `piper_linux_x86_64.tar.gz`, extract, copy `piper` to `/usr/local/bin/`
- **macOS**: Download `piper_macos_x86_64.tar.gz`, extract, add to PATH

Download a voice model:
```bash
# Example: English US voice
mkdir -p voices
# Download en_US-lessac-medium.onnx and en_US-lessac-medium.onnx.json
# from https://huggingface.co/rhasspy/piper-voices
```

### 6. Run the Application

```bash
python -m lumi_voice.app
```

Or use the installed command:
```bash
lumi-voice
```

### 7. Run Diagnostics

```bash
python scripts/diagnostics.py
```

## 🎛️ Usage

### GUI Mode (Default)

Launch with:
```bash
python -m lumi_voice.app
```

The GUI has four tabs:

1. **Conversation** — Chat with LUMI via push-to-talk, continuous listening, or text input
2. **Audio Devices** — Select and test microphone and speaker
3. **Settings** — Configure STT model, LLM host/model, TTS voice
4. **Logs** — Real-time application logs

### Push-to-Talk
1. Click and **hold** the "🎤 Push to Talk" button
2. Speak your message
3. **Release** the button — LUMI transcribes, thinks, and responds

### Continuous Listening
1. Toggle "🔄 Continuous Listen"
2. Speak naturally — VAD detects when you start and stop talking
3. LUMI processes each utterance automatically

### Text Input
Type a message in the text field and press Enter to bypass the microphone.

### Headless Mode

```bash
python -m lumi_voice.app --headless
```

Interactive text-based conversation without the GUI.

### ROS 2 Bridge Mode

```bash
source /opt/ros/jazzy/setup.bash
python -m lumi_voice.app --ros2
```

## ⚙️ Configuration

Configuration uses YAML files with this priority:

1. **Environment variables** (highest)
2. **User config** (`config/user.yaml`)
3. **Default config** (`config/default.yaml`)
4. **Built-in defaults** (lowest)

### Create User Config

Copy and edit the default configuration:

```bash
cp config/default.yaml config/user.yaml
```

### Key Settings

```yaml
# STT Model (tiny/base/small/medium/large-v3)
stt:
    model_size: "base"    # Larger = more accurate, slower
    device: "cpu"         # "cuda" for GPU
    language: "en"

# LLM
llm:
    ollama:
        host: "http://localhost:11434"
        model: "gemma3:1b"

# TTS
tts:
    voice_model: "en_US-lessac-medium"
    length_scale: 1.0     # <1.0 faster, >1.0 slower

# Audio Devices
audio_input:
    device_index: null    # null = system default, or integer index
audio_output:
    device_index: null
```

### Environment Variable Overrides

```bash
export OLLAMA_HOST=http://192.168.1.100:11434
export OLLAMA_MODEL=llama3
export LOG_LEVEL=DEBUG
```

## 🎤 Microphone & Speaker Selection

This is a critical feature for cross-device compatibility:

1. Open the **Audio Devices** tab
2. Select your preferred microphone from the dropdown
3. Click **🎤 Test Microphone** to verify
4. Select your preferred speaker from the dropdown
5. Click **🔊 Test Speaker** to hear a test tone
6. Click **💾 Save Settings** to persist your selection

Settings are saved to `config/user.yaml` and restored on restart.

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=lumi_voice --cov-report=html

# Verbose output
pytest -v
```

Tests mock hardware and external services. See `tests/` for details.

## 📁 Project Structure

```
lumi-voice-assistant/
├── README.md
├── LICENSE                     # Apache 2.0
├── pyproject.toml              # Package configuration
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
├── .gitignore
├── config/
│   └── default.yaml            # Default configuration
├── src/lumi_voice/
│   ├── __init__.py
│   ├── app.py                  # Entry point (GUI/headless/ROS2)
│   ├── config.py               # Configuration management
│   ├── logging_config.py       # Structured logging
│   ├── audio_devices.py        # Device enumeration & selection
│   ├── audio_capture.py        # Microphone capture
│   ├── vad.py                  # Voice activity detection
│   ├── stt.py                  # Speech-to-text (faster-whisper)
│   ├── conversation.py         # Chat history management
│   ├── llm.py                  # LLM integration (Ollama)
│   ├── tts.py                  # Text-to-speech (Piper)
│   ├── audio_playback.py       # Audio output
│   ├── pipeline.py             # Pipeline orchestrator
│   ├── ui/
│   │   ├── __init__.py
│   │   └── main_window.py      # PySide6 GUI
│   └── ros2_bridge/
│       ├── __init__.py
│       └── node.py             # ROS 2 node
├── tests/
│   ├── test_config.py
│   ├── test_conversation.py
│   ├── test_audio_devices.py
│   ├── test_stt.py
│   ├── test_tts.py
│   └── test_pipeline.py
├── scripts/
│   ├── diagnostics.py          # System diagnostics
│   ├── setup.sh                # Linux/macOS setup
│   └── run.sh                  # Run script
└── docs/
    ├── architecture.md
    ├── raspberry_pi_setup.md
    ├── ros2_integration.md
    └── troubleshooting.md
```

## 📦 Dependencies & Licenses

| Dependency | Version | License | Purpose |
|-----------|---------|---------|---------|
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | ≥1.1.0 | MIT | Speech-to-text |
| [Ollama](https://github.com/ollama/ollama) | 0.32+ | MIT | Local LLM runtime |
| [Piper TTS](https://github.com/rhasspy/piper) | 2023.11+ | MIT (engine) | Text-to-speech engine |
| [sounddevice](https://github.com/spatialaudio/python-sounddevice) | ≥0.5.0 | MIT | Audio I/O |
| [PySide6](https://doc.qt.io/qtforpython-6/) | ≥6.7.0 | LGPLv3 | Desktop GUI |
| [httpx](https://github.com/encode/httpx) | ≥0.27.0 | BSD-3 | HTTP client for Ollama API |
| [numpy](https://numpy.org/) | ≥1.26.0 | BSD-3 | Audio array processing |
| [pydantic](https://github.com/pydantic/pydantic) | ≥2.7.0 | MIT | Configuration validation |
| [PyYAML](https://pyyaml.org/) | ≥6.0 | MIT | YAML config files |
| [soundfile](https://github.com/bastibe/python-soundfile) | ≥0.12.0 | BSD-3 | Audio file I/O |
| [scipy](https://scipy.org/) | ≥1.12.0 | BSD-3 | Signal processing |

> ⚠️ **Voice Model Licensing**: Piper voice models have their own licenses.
> The `en_US-lessac-medium` voice uses data from the [LibriTTS](https://www.openslr.org/60/) corpus (CC BY 4.0).
> Check each voice model's license before distribution.

> ⚠️ **LLM Model Licensing**: Ollama models have varying licenses.
> Check the model's license on [ollama.com/library](https://ollama.com/library).

## 🍓 Raspberry Pi 5 Deployment

See [docs/raspberry_pi_setup.md](docs/raspberry_pi_setup.md) for the complete deployment guide.

**Quick summary:**
- Use `tiny` Whisper model for STT
- Use remote Ollama on a LAN server for LLM
- Use USB microphone and speaker
- Piper TTS runs well on ARM64

## 🤖 ROS 2 Integration

See [docs/ros2_integration.md](docs/ros2_integration.md) for the full guide.

The ROS 2 bridge is **optional** — the standalone app works without ROS 2.

## 🔧 Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for common issues and solutions.

**Quick checks:**
```bash
# Run diagnostics
python scripts/diagnostics.py

# Verbose logging
python -m lumi_voice.app --log-level DEBUG
```

## 🛡️ Healthcare Safety

LUMI is designed as a **companion assistant**, not a medical device:

- ❌ Does not diagnose medical conditions
- ❌ Does not prescribe or recommend medications
- ❌ Does not replace professional medical care
- ✅ Encourages contacting emergency services when appropriate
- ✅ Honest about its limitations
- ✅ Defers to human caregivers for medical decisions

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE).

Third-party components, models, and voice data may have different licenses.
See the Dependencies & Licenses table above.

## 🙏 Acknowledgments

- [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) for efficient Whisper inference
- [Ollama](https://ollama.com) for local LLM hosting
- [Piper TTS](https://github.com/rhasspy/piper) for fast offline speech synthesis
- [OpenAI Whisper](https://github.com/openai/whisper) for the foundational speech recognition model
