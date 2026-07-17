# Friday Agent Framework
## Speech Guide
**Version:** 1.0
**Framework Version:** v0.1.0
**Last Updated:** 2026-07-17

---

This guide covers the Friday speech package (`friday-speech`) including setup, configuration, and testing.

## Overview
Friday Speech provides:
- Text-to-speech (TTS) playback in live mode
- MP3 saving in file mode
- Wake word detection (optional)
- Adapter-based providers (ElevenLabs, Picovoice)

Speech is fully gated by `speech.enabled` and provider-specific options in `config.yaml`.

## Quick Start
1) Install the package dependencies you plan to use:
   - ElevenLabs: `pip install elevenlabs`
   - Picovoice (wake word / Orca): `pip install pvporcupine pvrecorder pvorca pvspeaker`
2) Add API keys/access keys in `config.yaml`.
3) Enable speech and select providers.

## Configuration
Minimal example (ElevenLabs TTS + Picovoice wake word):
```yaml
speech:
  enabled: true
  tts:
    provider: elevenlabs
  wakeword:
    enabled: true
    provider: picovoice
  elevenlabs:
    api_key: "..."
    voice_id: "..."
    model_id: "eleven_multilingual_v2"
    output_format: "mp3_44100_128"
  picovoice:
    access_key: "..."
    porcupine:
      enabled: true
      keywords: ["friday"]
      sensitivities: [0.6]
  mode: live
  streaming: true
  playback:
    enabled: true
    blocking: false
  selection:
    strategy: first_sentence
    max_words: 40
    tags:
      include_open: "<speech>"
      include_close: "</speech>"
      exclude_open: "<nospeech>"
      exclude_close: "</nospeech>"
```

### Tagging
If speech output is enabled, the model may wrap spoken content with tags:
- `<speech>...</speech>`: speak only these segments
- `<nospeech>...</nospeech>`: exclude these segments (only used when `strategy=tagged_exclude`)

Malformed tags are ignored and the configured selection strategy is used instead.

## Running the Harness
The speech harness lives inside the package and can be run without `friday-cli`:
```
python -m friday_speech.harness --config path/to/config.yaml
```

The harness can run wake word detection, STT (if enabled), and TTS in a single loop.
Note: STT adapters are currently placeholders; enable STT only if you provide a custom adapter.

### Friday CLI Commands (Memory Test App)
Inside `tests/integration/memory/friday.py`:
- `/speech on|off|mode|voice|config` toggles runtime speech settings
- `/speech-test [once|loop]` runs the speech harness with Esc-to-cancel

## Troubleshooting
- Speech does nothing: confirm `speech.enabled=true` and that the correct provider key is set.
- Wake word not detected: check mic permissions and Porcupine sensitivities.
- Playback errors: confirm `afplay` exists on macOS and required Picovoice packages are installed.
