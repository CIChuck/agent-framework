---
title: Speech services and integration
description: Configure standalone TTS/wake-word adapters, selection, file/live output and current Chat limitations.
framework_version: 0.1.0a3
last_reviewed: '2026-10-15'
status: current
audience: Technical end users and application integrators
doc_type: guide
---

# Speech services and integration

The Speech package supplies service/adaptor contracts, TTS, wake-word support,
selection, chunking and playback. Provider dependencies are optional. The
maintained Chat application currently uses a deterministic speech adapter in
both fake and real mode; enabling Chat speech does not wire live provider audio.

## Current capability boundaries

| Surface | Current behavior |
| --- | --- |
| `SpeechService` | Standalone selection, TTS and playback orchestration |
| ElevenLabs adapter | Provider-backed TTS with configured voice/model/format |
| Picovoice adapters | Orca TTS and Porcupine wake-word capture; SDK/device setup required |
| Built-in Picovoice STT | Placeholder; `transcribe()` raises `STTError` because capture is not wired |
| `AdapterRegistry` | Explicit custom TTS/STT/wake-word implementations |
| `SpeechHarness` | Standalone local echo/test loop, not a model conversation daemon |
| Chat `/speech` and `/speech-test` | Configuration/deterministic adapter behavior; not proof of audio generation |

## Install only the provider you need

```bash
python -m pip install "friday-framework-speech[elevenlabs]==0.1.0a3"
# Or provision the Picovoice integration:
python -m pip install "friday-framework-speech[picovoice]==0.1.0a3"
```

Live recording/playback needs compatible devices, OS permissions and provider
credentials/assets. Installing an extra alone never enables capture. File mode
can test synthesis without speaker output, but still makes a provider call.

## Disabled-mode lifecycle check

This **offline Python example** needs no credentials or hardware:

```python
import asyncio
from friday_speech import SpeechConfig, SpeechService

async def main() -> None:
    service = SpeechService(SpeechConfig(enabled=False))
    try:
        await service.speak("No synthesis is performed.")
        print(service.config.enabled)
    finally:
        await service.close()

asyncio.run(main())
```

Expected output: `False`. `SpeechService.close()` currently closes the owned
wake-word adapter when present; do not infer a universal close method for every
provider resource from that call.

## Explicit provider assembly

Set `FRIDAY_ELEVENLABS_API_KEY` and `FRIDAY_ELEVENLABS_VOICE_ID` through your
normal secret/configuration method. This is a **live Python example**: it calls
ElevenLabs and saves MP3 output beneath the selected application directory.
Use a voice/model your account can access.

```python
import asyncio
import os
from pathlib import Path
from friday_speech import SpeechConfig, SpeechService

async def main() -> None:
    config = SpeechConfig.from_dict({
        "enabled": True,
        "tts": {"provider": "elevenlabs"},
        "elevenlabs": {
            "api_key": os.environ["FRIDAY_ELEVENLABS_API_KEY"],
            "voice_id": os.environ["FRIDAY_ELEVENLABS_VOICE_ID"],
            "model_id": "eleven_multilingual_v2",
            "output_format": "mp3_44100_128",
        },
        "mode": "file",
        "output_dir": Path("speech-output"),
        "selection": {"strategy": "first_sentence"},
    })
    service = SpeechService(config)
    try:
        await service.speak("Hello from Friday. This sentence is not selected.")
    finally:
        await service.close()

asyncio.run(main())
```

File output currently requires an MP3 `AudioStream`; PCM-only output is not
automatically converted. Live MP3 playback uses `afplay`, so that path requires
macOS and the executable on PATH. PCM playback uses the configured Picovoice
speaker integration. Do not promise identical audio behavior on every OS.

## Configuration model

`SpeechConfig` accepts this **disabled standalone speech-block example**:

```yaml
speech:
  enabled: false
  tts: {provider: elevenlabs}
  wakeword: {enabled: false, provider: picovoice}
  stt: {enabled: false, provider: picovoice}
  mode: file
  streaming: true
  output_dir: ./speech-output
  playback: {enabled: true, blocking: false}
  selection:
    strategy: first_sentence
    max_words: 40
  chunking:
    enabled: true
    max_chars: 1800
    boundary: sentence
```

Pass the inner `speech` mapping to `SpeechConfig.from_dict`. Enabling ElevenLabs
requires its key; enabling Picovoice TTS, wake word or STT requires an access key.
The STT credential check does not make the placeholder adapter functional.

Standalone harness YAML uses plain YAML loading and does **not** interpolate
`${...}` environment placeholders. Prefer explicit Python assembly as above
when injecting secrets. Chat's separate YAML interpolation does not change the
standalone harness loader, and Chat's config model/defaults differ from the
standalone `SpeechConfig` model.

## Selection and tags

Strategies are `all`, `first_sentence`, `first_n_words`, `tagged_only` and
`tagged_exclude`. Standalone default markers are `<speech>...</speech>` and
`<nospeech>...</nospeech>`; configure `selection.tags` when changing them.
Valid include segments take precedence over the ordinary strategy. Malformed
tags are stripped and the configured strategy is applied; do not use malformed
exclude tags as a privacy boundary.

This **offline Python example** tests selection only:

```python
from friday_speech.config import SelectionConfig
from friday_speech.selection import select_speech_text

text = "<speech>Speak this.</speech> Additional private-looking text."
selected = select_speech_text(text, SelectionConfig(strategy="tagged_only"))
print(selected)
```

Expected output: `Speak this.` Chat's prompt/display helper uses `<say>` and
`<nosay>` markers instead. Do not assume its helper and the standalone package
share a tag vocabulary automatically.

## Harness and Chat commands

With an explicitly provisioned standalone YAML file, this is a **live command**:

```bash
python -m friday_speech.harness --config /path/to/speech-config.yaml
```

The harness requires `enabled: true`, optionally waits for wake word/STT, then
speaks an echo of supplied/transcribed text. Keep STT disabled unless you inject
a functional custom adapter through Python. `SpeechHarness.run()` loops;
`run_once()` performs one cycle. They are test tools, not automatic Chat wiring.

Chat exposes `/speech on|off|config|mode|voice|provider` and `/speech-test
[once|loop]`. In alpha3, both test modes invoke one `speak("Speech test.")` on
the deterministic adapter; `loop` does not create the standalone continuous
harness. A “completed” Chat message is therefore not an audio test result.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Nothing happens while disabled | Expected no-op; enable only after provider setup |
| Chat reports success without audio | Current deterministic Chat adapter; use standalone service/harness |
| Key validation fails | Explicit selected provider key at assembly, not an unresolved harness placeholder |
| File mode rejects output | MP3 required; no automatic PCM-to-MP3 conversion |
| MP3 live playback fails | `afplay` and macOS availability |
| Wake word fails | Mic permissions, SDK/assets, keyword configuration and sensitivities 0..1 |
| STT raises “not wired” | Built-in placeholder; supply an explicit adapter |
| Unexpected spoken text | Include-tag precedence, strategy and tag spelling/malformed fallback |

## Implementation references

- [Configuration](../../packages/friday-speech/src/friday_speech/config.py), [service](../../packages/friday-speech/src/friday_speech/service.py) and [interfaces](../../packages/friday-speech/src/friday_speech/interfaces.py)
- [Selection](../../packages/friday-speech/src/friday_speech/selection.py), [playback](../../packages/friday-speech/src/friday_speech/playback.py) and [harness](../../packages/friday-speech/src/friday_speech/harness.py)
- [Picovoice adapters](../../packages/friday-speech/src/friday_speech/adapters/picovoice.py)
- [Chat assembly](../../packages/friday-chat/src/friday_chat/runtime.py) and [speech helpers](../../packages/friday-chat/src/friday_chat/speech.py)

[Guide index](README.md) · [Capability status](FRIDAY-FEATURES.md)
