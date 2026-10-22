# LUMI Voice Assistant — ROS 2 Integration Guide

## Overview

The LUMI Voice Assistant can optionally integrate with ROS 2 Jazzy as part
of the LUMINAX healthcare companion robot project.

The ROS 2 bridge publishes voice events as topics and subscribes to
commands, enabling other ROS 2 nodes to interact with the voice system.

## Prerequisites

- ROS 2 Jazzy installed and sourced
- `rclpy` and `std_msgs` packages available
- LUMI Voice Assistant installed

## Topics

### Published

| Topic | Message Type | Description |
|-------|-------------|-------------|
| `/<ns>/recognized_speech` | `std_msgs/String` | Transcribed user speech |
| `/<ns>/response_text` | `std_msgs/String` | LUMI's generated response |
| `/<ns>/voice_status` | `std_msgs/String` | Pipeline status (JSON) |

Default namespace: `/lumi`

### Subscribed

| Topic | Message Type | Description |
|-------|-------------|-------------|
| `/<ns>/voice_command` | `std_msgs/String` | Commands to voice system |

### Command Format

```json
{"action": "speak", "text": "Hello, how can I help you?"}
{"action": "listen"}
{"action": "stop"}
{"action": "status"}
```

## Launching

```bash
# Terminal 1: Source ROS 2 and run
source /opt/ros/jazzy/setup.bash
python -m lumi_voice.app --ros2

# Terminal 2: Test by publishing a command
ros2 topic pub --once /lumi/voice_command std_msgs/String \
    '{data: "{\"action\": \"speak\", \"text\": \"Hello from ROS 2\"}"}'

# Terminal 3: Listen to transcripts
ros2 topic echo /lumi/recognized_speech
```

## Status Message Format

```json
{
    "state": "idle",
    "components": {
        "microphone": "ready",
        "stt": "loaded",
        "llm": "connected",
        "tts": "ready",
        "speaker": "ready",
        "ros2": "connected"
    }
}
```

## Future Action Interface

The following structured actions are designed for future integration
with LUMINAX robot capabilities:

```python
# Action request format (future implementation)
{
    "type": "NavigateToLocation",
    "parameters": {
        "location": "kitchen",
        "speed": "normal"
    },
    "confirmation_required": true
}
```

### Planned Actions

| Action | Parameters | Notes |
|--------|-----------|-------|
| `NavigateToLocation` | `location: str` | Requires nav stack |
| `FindPerson` | `name: str` | Requires face recognition |
| `RecognizeFace` | — | Requires camera |
| `GetMedicineSchedule` | `patient: str` | Requires caregiver app |
| `NotifyCaregiver` | `message: str, urgency: str` | Requires caregiver app |
| `Speak` | `text: str` | Available now |

### Safety Rules

1. Actions use an explicit allowlist — no arbitrary commands
2. All action parameters are validated
3. Capability availability is checked before execution
4. Consequential actions require confirmation
5. Motor control stays under ROS 2 navigation stack
6. Free-form LLM text never directly controls motors
