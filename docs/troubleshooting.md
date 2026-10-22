# LUMI Voice Assistant — Troubleshooting Guide

## Quick Diagnostics

```bash
python scripts/diagnostics.py
```

## Common Issues

### Audio

**No audio devices found**
- Check that a microphone/speaker is connected
- On Linux: install `portaudio19-dev`, `alsa-utils`
- On Windows: check Sound settings in Control Panel
- Run: `python -c "import sounddevice; print(sounddevice.query_devices())"`

**Microphone not recording / very quiet**
- Check OS microphone permissions
- Increase microphone volume in OS settings
- Try a different microphone
- Lower `vad.energy_threshold` in config

**Audio playback crackling or distorted**
- Try a different sample rate in config
- Close other audio applications
- Use a wired connection instead of Bluetooth

**"PortAudio" errors**
- Linux: `sudo apt install portaudio19-dev`
- macOS: `brew install portaudio`
- Windows: Usually included with sounddevice

### Speech-to-Text

**Model download fails**
- Check internet connection
- Check available disk space (models: 75MB–3GB)
- Set a proxy if needed
- Models are cached after first download in `~/.cache/huggingface/`

**Transcription is inaccurate**
- Try a larger model (base → small → medium)
- Speak clearly and not too fast
- Reduce background noise
- Check that `language` is set correctly

**Transcription is very slow**
- Use `tiny` or `base` model
- Set `compute_type: int8`
- On GPU systems, set `device: cuda`

### Language Model

**"Cannot connect to Ollama"**
- Start Ollama: `ollama serve`
- Check the host URL in config (default: `http://localhost:11434`)
- Verify with: `curl http://localhost:11434/api/tags`

**"Model not found"**
- Pull the model: `ollama pull gemma3:1b`
- Check available models: `ollama list`

**Slow responses**
- Use a smaller model
- Reduce `max_history` to send less context
- On Pi 5, use remote Ollama on a more powerful machine

**Responses are too long**
- The system prompt asks for concise responses
- Try a different model that follows instructions better

### Text-to-Speech

**"Piper not found"**
- Download from: https://github.com/rhasspy/piper/releases
- Add to PATH or place in `./piper/` directory
- On Windows, ensure `piper.exe` is accessible

**"Voice model not found"**
- Download voice models from: https://huggingface.co/rhasspy/piper-voices
- Set `voice_model_path` in config to the `.onnx` file path
- Ensure the `.onnx.json` config file is alongside the model

### GUI

**UI freezes during operation**
- This should not happen — report as a bug
- All heavy operations run in background threads

**Dark theme looks wrong**
- PySide6 Fusion style is used for cross-platform consistency
- Some Linux distros may override Qt themes

### ROS 2

**"rclpy not available"**
- Source ROS 2: `source /opt/ros/jazzy/setup.bash`
- Install rclpy: part of standard ROS 2 desktop install
- The standalone app works fine without ROS 2

## Getting Help

1. Run diagnostics: `python scripts/diagnostics.py`
2. Check logs in the Logs tab of the GUI
3. Run with `--log-level DEBUG` for verbose output
4. Check the GitHub Issues page
