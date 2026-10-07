Source-only static receipt attempt01 failed because its project glob counted only
root+packages (17) and omitted tests/lab/pyproject.toml. The actual18 committed
project files all retain >=3.13.4. The helper was corrected to enumerate tracked
pyproject filenames. No product change, SDK/native activation or gate relaxation
occurred; the previous raw Ruff327 match was already valid and is retained.
