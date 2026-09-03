# Friday-Speech Build Plan (Streaming TTS, Adapter-Based)

**Status:** Draft; implementation authority not granted
**Lifecycle:** Queued

# Eleven Labs
# Pico Voice https://console.picovoice.ai/

## Overview
Build a new package, `friday-speech`, to provide text-to-speech (TTS) for Friday. The system must support:
- Streaming TTS playback on macOS (live mode)
- Saving TTS output as MP3 to a configured directory (file mode)
- Adapter-based design for future providers (initial implementation: ElevenLabs)
- Type-safe configuration via `config.yaml` (no environment variable dependency)
- Non-blocking playback by default
- CLI toggles in `friday.py`
- Tag-based and strategy-based selection of what to speak
- Esc key interrupt for playback

## Requirements (Confirmed)
- API key injected via `config.yaml`
- Default mode: **live**
- Streaming audio
- Tags can appear anywhere
- Malformed tags are ignored (fallback to strategy)
- Speech respects global toggle
- Sentence detection: punctuation-based
- Optional max duration (configurable)
- Speech applies only to **assistant responses**, not tool output

---

## Phase 1 — Package Skeleton
Create new package:
```
packages/friday-speech/
  pyproject.toml
  src/friday_speech/
    __init__.py
    config.py
    interfaces.py
    adapters/
      __init__.py
      elevenlabs.py
    selection.py
    playback.py
    service.py
    errors.py
```

**Notes**
- `interfaces.py`: `TTSAdapter` Protocol
- `adapters/elevenlabs.py`: ElevenLabs streaming client
- `selection.py`: speech selection strategy + tag parsing
- `playback.py`: macOS playback orchestration
- `service.py`: user-facing orchestration (mode, streaming, error handling)

---

## Phase 2 — Configuration (Type-Safe)
Add config section in `config.yaml`:
```yaml
speech:
  enabled: false
  tts:
    provider: elevenlabs
  wakeword:
    enabled: false
    provider: picovoice
  elevenlabs:
    api_key: "..."
    voice_id: "..."
    model_id: "eleven_multilingual_v2"
    output_format: "mp3_44100_128"
  mode: "live"                # live | file
  streaming: true
  output_dir: ".friday/speech"
  playback:
    enabled: true
    blocking: false
  selection:
    strategy: "first_sentence"   # all|first_sentence|first_n_words|tagged_only|tagged_exclude
    max_words: 40
    tags:
      include_open: "<speech>"
      include_close: "</speech>"
      exclude_open: "<nospeech>"
      exclude_close: "</nospeech>"
  limits:
    max_seconds: null            # optional hard cutoff
```

Example (ElevenLabs TTS + Picovoice wake word):
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
```

**Validation rules**
- `speech.tts.provider` required when `speech.enabled=true`
- `speech.elevenlabs.api_key` required when `speech.tts.provider=elevenlabs`
- `speech.wakeword.provider` required when `speech.wakeword.enabled=true`
- `mode`, `strategy`, `provider` validated as enums
- `output_dir` must be writable in file mode

---

## Phase 3 — Adapter Interface
Create a common interface for TTS providers:
```
class TTSAdapter(Protocol):
    async def stream(
        self,
        text: str,
        voice_id: str,
        settings: VoiceSettings,
    ) -> AsyncIterator[bytes]:
        ...
```

**VoiceSettings** should be provider-agnostic:
- `speed` (if supported)
- `stability`
- `similarity_boost`
- `style` (optional)

---

## Phase 4 — ElevenLabs Adapter (Streaming)
- Use ElevenLabs Python SDK streaming API.
- Inject API key from `config.yaml`.
- Implement `stream()` returning async audio chunks.
- Raise explicit exceptions on errors (no silent failures).

---

## Phase 5 — Speech Selection + Tag Parsing
Implement `selection.py`:
- **Tag parser** scans streaming text:
  - `<speech> ... </speech>` → speak only those segments
  - `<nospeech> ... </nospeech>` → exclude from speech
  - malformed tags → ignored (fallback to strategy)

**Strategies**
- `all`
- `first_sentence` (punctuation-based)
- `first_n_words` (configurable)
- `tagged_only`
- `tagged_exclude`

Behavior:
- If `<speech>` tags exist → `tagged_only` takes precedence
- Else fallback to `strategy`

---

## Phase 6 — Playback (macOS)
- **Non-blocking** playback by default
- Try streaming directly to `afplay` stdin
- If streaming to stdin fails, fallback to temp MP3 file + `afplay`
- Esc key cancels playback and clears buffers

---

## Phase 7 — friday.py Integration
### CLI Commands
- `/speech on|off`
- `/speech mode live|file`
- `/speech voice <voice_id>`
- `/speech config`

### Dynamic Prompt Snippet
Only inject speech-tagging instructions when `speech.enabled=true`:
```
If speech output is enabled, you may wrap spoken text in <speech>...</speech>
and text to exclude in <nospeech>...</nospeech>. Tags may appear anywhere.
Do not emit tags if not needed.
```

When `/speech off`, remove the snippet (no token overhead).

---

## Phase 8 — Tests
- Config validation tests
- Adapter streaming tests (mocked SDK)
- Tag parser tests (valid + malformed tags)
- Strategy tests (first_sentence, first_n_words)
- Playback tests (mock subprocess)
- CLI toggle tests

---

## Phase 9 — Docs
Create `docs/guides/speech.md`:
- API key setup
- Config examples
- CLI usage
- Troubleshooting

---

## External Steps (One-Time Setup)
### Required Dependencies
1) Install ElevenLabs SDK:
   - `pip install elevenlabs`
2) Create ElevenLabs API key from dashboard
3) Add key to `config.yaml` under `speech.elevenlabs.api_key`
4) macOS: ensure `afplay` is available (default on macOS)

### Optional Picovoice Dependencies (by capability)
- Wake word (Porcupine): `pip install pvporcupine`
- Mic input (PvRecorder): `pip install pvrecorder`
- TTS (Orca): `pip install pvorca`
- PCM output (PvSpeaker): `pip install pvspeaker`
- VAD (Cobra): `pip install pvcobra`
- STT (Leopard): `pip install pvleopard`
- Speech-to-intent (Rhino): `pip install pvrhino`

### Optional Model Files (Picovoice)
- Porcupine custom keywords use `.ppn` files
- Non-English support may require `.pv` models
- Orca can use `.pv` voice models

---

## Notes / Future Extensions
- Add alternate providers by implementing new adapters
- Add a heartbeat alert path (non-speech audio cue)
- Add playback device routing if needed later

---

## Phase 10 — Picovoice (Optional Provider + Wake Word)
Add Picovoice as an **optional** provider and wake-word subsystem. All Picovoice features must only activate when explicitly enabled in `config.yaml`.

### Features to Add
- **Orca TTS adapter** (on-device, streaming PCM)
- **Porcupine wake word** detection (built-in keywords or custom `.ppn`)
- **PvRecorder** mic capture pipeline
- **PvSpeaker** PCM playback pipeline
- **Cobra VAD** (optional) to filter mic input and reduce false positives

### Config Additions (proposed)
```yaml
speech:
  enabled: false
  tts:
    provider: elevenlabs
  wakeword:
    enabled: false
    provider: picovoice
  picovoice:
    access_key: "..."
    orca:
      model_path: null           # optional .pv
      voice: "default"
      speech_rate: 1.0           # 0.7–1.3 if supported
    porcupine:
      enabled: false
      keywords: ["friday"]       # built-in keywords
      keyword_paths: []          # optional .ppn
      sensitivities: [0.5]
      model_path: null           # optional .pv
    recorder:
      device_index: null
      frame_length: null         # use default if null
    speaker:
      device_index: null
      buffered_frames: 8
    cobra:
      enabled: false
```

### Integration Notes
- If `speech.enabled=false`, **do not** inject speech-tag instructions or start wake-word threads.
- If `speech.tts.provider=picovoice`, route through Orca adapter and PvSpeaker for PCM playback.
- Wake-word detection should be a separate optional service gated by `speech.wakeword.enabled` and `speech.wakeword.provider=picovoice`.
- Keep the adapter interface consistent; add PCM playback support behind `playback.py`.

### Tests
- Config validation for Picovoice blocks
- Orca adapter stream flow (mocked)
- Porcupine wake-word loop (mocked recorder)
- Cobra VAD gating (mocked)

---

## Final Phase — Test Harness (In-Package)
Add a small test harness inside `packages/friday-speech/src/friday_speech/` so unit tests can exercise wake word, speech-to-text, and text-to-speech in a single configurable app without requiring external wiring.

**Placement**
- `packages/friday-speech/src/friday_speech/harness.py`
- Tiny CLI entry point in Friday CLI for manual runs

**Goals**
- Single entry point to run a combined pipeline:
  - Wake word detection (optional)
  - Speech-to-text (if enabled in config)
  - Text-to-speech (if enabled in config)
- Fully configurable via `config.yaml` (or a provided config object in tests)
- Supports mocks to avoid hardware dependency in unit tests
- Supports manual invocation for local sanity checks

**Minimum API (example)**
```
class SpeechHarness:
    def __init__(self, config: SpeechConfig, adapters: AdapterRegistry) -> None: ...
    async def run(self) -> None: ...
    async def run_once(self) -> None: ...
```

**CLI Entry Point (Friday CLI)**
- Add a lightweight command (e.g., `/speech-test` or `friday speech-test`) that:
  - Loads `config.yaml`
  - Instantiates `SpeechHarness`
  - Runs `run()` or `run_once()` based on flags
  - Prints clear start/stop messages and errors

**Testing**
- Unit tests should instantiate the harness with mocked adapters and assert:
  - correct wiring based on config toggles
  - wakeword gating behavior
  - TTS invoked only on assistant responses
  - errors propagate (fail fast, no silent failure)
