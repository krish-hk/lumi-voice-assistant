# LUMI Voice Assistant — Architecture

## Overview

LUMI Voice Assistant is a modular, open-source voice pipeline that provides:

1. **Speech-to-Text (STT)** — Whisper via faster-whisper
2. **Conversational AI (LLM)** — Ollama with configurable models
3. **Text-to-Speech (TTS)** — Piper TTS
4. **Audio I/O** — Configurable microphone and speaker selection
5. **ROS 2 Bridge** — Optional integration with ROS 2 Jazzy

## Architecture Diagram

```
┌────────────────────────────────────────────────────────┐
│                    PySide6 Desktop UI                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │Conversation│ │ Devices  │ │ Settings │ │   Logs    │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
└────────────────────┬───────────────────────────────────┘
                     │
              ┌──────┴──────┐
              │   Pipeline   │  ← Orchestrator
              └──────┬──────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────┴────┐    ┌─────┴─────┐   ┌─────┴─────┐
│  Audio   │    │    STT    │   │    TTS    │
│ Capture  │    │ (Whisper) │   │  (Piper)  │
│   + VAD  │    └─────┬─────┘   └─────┬─────┘
└──────────┘          │               │
                ┌─────┴─────┐   ┌─────┴─────┐
                │    LLM    │   │   Audio    │
                │ (Ollama)  │   │ Playback   │
                └───────────┘   └───────────┘

     Optional: ┌────────────────┐
               │  ROS 2 Bridge  │ → Topics, Services
               └────────────────┘
```

## Module Responsibilities

| Module | File | Purpose |
|--------|------|---------|
| Config | `config.py` | YAML-based configuration with Pydantic validation |
| Audio Devices | `audio_devices.py` | Enumerate, select, test audio hardware |
| Audio Capture | `audio_capture.py` | Stream microphone input with device selection |
| VAD | `vad.py` | Energy-based voice activity detection |
| STT | `stt.py` | Speech transcription via faster-whisper |
| Conversation | `conversation.py` | Chat history management |
| LLM | `llm.py` | Language model integration (Ollama backend) |
| TTS | `tts.py` | Speech synthesis via Piper |
| Audio Playback | `audio_playback.py` | Thread-safe audio output |
| Pipeline | `pipeline.py` | Orchestrates the full STT→LLM→TTS flow |
| UI | `ui/main_window.py` | PySide6 desktop interface |
| ROS 2 Bridge | `ros2_bridge/node.py` | Optional ROS 2 topic/service integration |
| App | `app.py` | CLI entry point (GUI, headless, ROS 2 modes) |

## Data Flow

### Push-to-Talk
1. User presses PTT button → `AudioCapture.start()`
2. Audio chunks queued in real-time
3. User releases → `AudioCapture.stop()` → chunks concatenated
4. Audio → `SpeechToText.transcribe_audio()` → text
5. Text → `ConversationManager.add_user_message()`
6. Messages → `LLMEngine.generate()` → response
7. Response → `TextToSpeech.synthesize()` → WAV bytes
8. WAV → `AudioPlayer.play_wav_bytes()` → speaker

### Continuous Listening
1. `AudioCapture` streams chunks continuously
2. Each chunk → `VoiceActivityDetector.process_chunk()`
3. VAD detects speech onset, accumulates chunks
4. After silence timeout → complete utterance returned
5. Utterance follows same STT→LLM→TTS flow

## Threading Model

- **Main thread**: UI event loop (PySide6)
- **Audio capture**: sounddevice callback thread
- **Continuous listen loop**: Dedicated daemon thread
- **Processing**: Each STT→LLM→TTS cycle in a daemon thread
- **Audio playback**: Blocks in playback lock (serialized)

All pipeline→UI communication goes through Qt Signals for thread safety.

## ROS 2 Integration

The ROS 2 bridge is an optional wrapper that:
- Publishes transcripts to `/<ns>/recognized_speech` (String)
- Publishes responses to `/<ns>/response_text` (String)
- Publishes status to `/<ns>/voice_status` (String, JSON)
- Subscribes to `/<ns>/voice_command` (String, JSON) for external control

The bridge does NOT replace the pipeline — it wraps it.

## Future Robot Actions

Designed action interface (not yet connected):

| Action | Description | Status |
|--------|-------------|--------|
| `NavigateToLocation` | Move robot to named location | Planned |
| `FindPerson` | Search for a person by name | Planned |
| `RecognizeFace` | Identify a person via camera | Planned |
| `GetMedicineSchedule` | Query medication reminders | Planned |
| `NotifyCaregiver` | Send alert to caregiver app | Planned |
| `Speak` | Trigger TTS from another node | Available |

Actions require:
- Allowlist validation
- Structured argument checking
- Capability availability verification
- Confirmation for consequential actions
