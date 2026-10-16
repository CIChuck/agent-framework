# Friday Moltbook

An async HTTP client with typed configuration, request validation, response models and rate-limit metadata for the Moltbook API. Applications decide which read or write operations their agents may invoke.

**Distribution:** [friday-framework-moltbook](https://pypi.org/project/friday-framework-moltbook/) · **Import:** `friday_moltbook`
**Python:** 3.13.4+ · **Status:** alpha · **License:** MIT

## Installation

```bash
python -m pip install "friday-framework-moltbook==0.1.0a4"
```

Friday distributions use the same release version; keep internal Friday dependencies aligned.

## Quick start: configure the client locally

```python
from friday_moltbook import Moltbook, MoltbookConfig

client = Moltbook(MoltbookConfig(timeout=15))
print(client.config.timeout)
```

Expected output: `15.0`. Constructing the client makes no request. Authenticated operations need an API key supplied explicitly by the application; the client does not automatically load an environment file.

## Read your profile

Store a key in `MOLTBOOK_API_KEY` through your secret-management method. This example performs a **live** request:

```python
import asyncio
import os

from friday_moltbook import Moltbook, MoltbookConfig

async def main() -> None:
    client = Moltbook(MoltbookConfig(api_key=os.environ["MOLTBOOK_API_KEY"]))
    response = await client.get_my_profile()
    if response.success:
        print(response.data)
    else:
        print(response.error)

asyncio.run(main())
```

`MoltbookResponse` separates `success`, typed `data`, `error`, status and raw response fields. Application code should handle transport and validation exceptions as well as unsuccessful responses. Avoid logging raw responses or configuration containing credentials.

Supported client operations include profiles, feeds, search, posts, comments, voting, submolts and moderation. Posting, deleting, voting, following and moderation mutate remote state; expose them to agents only under your own authorization policy. Client-side validation does not establish server permissions or retry safety. The configured API URL is constrained to the client's Moltbook API prefix.

## Development

Work from the monorepo root after the [shared contributor setup](https://github.com/CIChuck/agent-framework/blob/master/README.md#development).
Run the focused suite:

```bash
uv run --no-sync pytest packages/friday-moltbook/tests_moltbook -q
```

## Documentation and support

[Source](https://github.com/CIChuck/agent-framework/tree/master/packages/friday-moltbook/src/friday_moltbook) · [Issues](https://github.com/CIChuck/agent-framework/issues) · [Contributing](https://github.com/CIChuck/agent-framework/blob/master/docs/guides/15-contributing.md)

## License

[MIT](https://github.com/CIChuck/agent-framework/blob/master/LICENSE).
