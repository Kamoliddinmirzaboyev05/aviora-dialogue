# Task 1 Report: Gemini Provider And Strict Factory

## Implementation

- Added `GeminiAPIProvider`, backed by the official `google-genai` client and Gemini structured JSON output.
- Added Pydantic response models and normalized Gemini responses into the existing `ClassificationResult` and `DraftResult` dataclasses.
- Added `AIProviderConfigurationError` for missing/unsupported configuration and `AIProviderError` for sanitized Gemini request failures.
- Made provider selection strict: `mock`, `gemini`, and `vertex` are explicit options; unsupported values raise configuration errors rather than falling back to mock.
- Preserved the existing `MockAIProvider` and `VertexAIProvider` implementations.
- Added Gemini environment settings and the `google-genai>=2.10,<3` dependency.

## TDD Evidence

### RED

Command:

```bash
cd backend && ../.venv/bin/pytest tests/test_ai_providers.py -q
```

Result: failed during collection with `ModuleNotFoundError: No module named 'apps.ai_engine.exceptions'`. This was the expected failure before the provider exceptions and Gemini provider existed.

### GREEN

Command:

```bash
cd backend && ../.venv/bin/pytest tests/test_ai_providers.py -q
```

Result: `6 passed in 0.82s`.

## Verification

Commands:

```bash
cd backend && ../.venv/bin/pytest -q
cd backend && ../.venv/bin/ruff check apps/ai_engine/exceptions.py apps/ai_engine/providers/gemini.py apps/ai_engine/services.py config/settings.py tests/test_ai_providers.py
git diff --check
```

Results:

- Full backend suite: `16 passed in 6.67s`.
- Ruff: `All checks passed!`.
- Diff check: no whitespace errors.

## Changed Files

- `.env.example`
- `backend/apps/ai_engine/exceptions.py`
- `backend/apps/ai_engine/providers/gemini.py`
- `backend/apps/ai_engine/services.py`
- `backend/config/settings.py`
- `backend/requirements/base.txt`
- `backend/tests/test_ai_providers.py`

## Self-Review

- Confirmed the factory has no silent fallback for unrecognized provider names.
- Confirmed mock remains keyless and Vertex remains independently configured.
- Confirmed classification and draft responses validate against schemas before becoming existing result dataclasses.
- Confirmed upstream exception messages do not expose provider exception text in the public error.
- Confirmed production calls request Gemini JSON structured output with deterministic temperature zero.

## Concerns

No implementation concerns. An existing untracked `frontend/src/assets/` directory was left untouched and is excluded from the Task 1 commit.

## Security Fix Evidence

Reviewer finding: the sanitized Gemini error retained a credential-bearing upstream exception as `__cause__` through explicit exception chaining.

Regression test added: `test_gemini_provider_discards_upstream_exception_cause` raises an upstream `RuntimeError("credential=secret-token")` and asserts that the resulting `AIProviderError.__cause__` is `None`.

### RED

Command:

```bash
cd backend && ../.venv/bin/pytest tests/test_ai_providers.py -q
```

Result: `1 failed, 5 passed in 1.01s`. The failing assertion showed `RuntimeError('credential=secret-token')` remained as `AIProviderError.__cause__`.

### GREEN And Verification

Commands:

```bash
cd backend && ../.venv/bin/pytest tests/test_ai_providers.py -q
cd backend && ../.venv/bin/pytest -q
cd backend && ../.venv/bin/ruff check apps/ai_engine/providers/gemini.py tests/test_ai_providers.py
git diff --check
```

Results:

- Focused provider suite: `6 passed in 0.78s`.
- Full backend suite: `16 passed in 6.74s`.
- Ruff: `All checks passed!`.
- Diff check: no whitespace errors.

Implementation: changed the Gemini error boundary to `raise AIProviderError(...) from None`, so no upstream exception is retained as the public error's explicit cause or rendered through traceback chaining.
