# Friday Speech

Speech-service contracts and orchestration for text-to-speech, speech-to-text, wake-word detection, selection, chunking and playback. Provider SDKs and audio hardware are optional application choices.

**Distribution:** [friday-framework-speech](https://pypi.org/project/friday-framework-speech/) · **Import:** `friday_speech`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-speech==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: construct a disabled service

```python
import asyncio

from friday_speech import SpeechConfig, SpeechService

async def main() -> None:
    service = SpeechService(SpeechConfig(enabled=False))
    try:
        await service.speak("Speech is disabled; nothing is synthesized.")
        print(service.config.enabled)
    finally:
        await service.close()

asyncio.run(main())
```

Expected output includes `False`. This is a lifecycle/configuration smoke example, not an audio demonstration: it needs no credentials, network, microphone or speaker.

## Enable a provider

```bash
python -m pip install "friday-framework-speech[elevenlabs]==0.1.0a4"
# Or install the Picovoice integration:
python -m pip install "friday-framework-speech[picovoice]==0.1.0a4"
```

- ElevenLabs supplies TTS; Picovoice supplies its supported TTS, STT and wake-word adapters.
- Enable speech and select/configure the provider through `SpeechConfig` or the owning application's speech YAML. Supply credential values at assembly time from your secret store.
- Live recording/playback needs compatible audio devices and OS permissions. File output is a separate mode.
- `AdapterRegistry` accepts explicit TTS/STT/wake-word implementations for tests or custom integrations.
- Close owned service resources in `finally`. `SpeechHarness` is a local test harness, not a daemon or an automatically enabled Chat feature.

See the speech guide for the full configuration and hardware requirements. Installing an extra alone never opts your application into microphone capture or provider calls.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-speech/tests_speech -q
```

## Documentation and support

[Speech configuration](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/speech.md) · [Chat integration](https://github.com/CIChuck/agent-framework/blob/master/packages/friday-chat/README.md) · [Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-speech/src/friday_speech) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
