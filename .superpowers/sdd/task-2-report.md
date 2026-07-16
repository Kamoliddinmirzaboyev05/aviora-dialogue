# Task 2 Report: Admin-Only AI Connection Test

## Scope

Implemented `POST /api/v1/ai/test-connection/` for active workspace owners and admins. The endpoint classifies a fixed harmless CRM sample using the first active workspace product, returns provider metadata, connection state, integer latency, and the normalized classification result. It does not accept arbitrary prompts. Provider configuration and provider request errors return the standard sanitized API error envelope with HTTP 503.

## RED Evidence

After adding `backend/tests/test_ai_connection_api.py`, the focused test run used the worktree virtual environment because `pytest` was unavailable on the host `PATH`.

```text
../.venv/bin/pytest tests/test_ai_connection_api.py -q
FFF
3 failed in 1.95s
```

The owner and error tests failed because `apps.ai_engine.views` did not exist, and the reviewer test received HTTP 404 because `/api/v1/ai/test-connection/` was not registered.

## GREEN Evidence

```text
../.venv/bin/pytest tests/test_ai_connection_api.py -q
3 passed in 1.53s

../.venv/bin/pytest tests/test_ai_connection_api.py tests/test_ai_providers.py -q
9 passed in 1.59s

../.venv/bin/pytest -q
19 passed in 7.64s

../.venv/bin/python manage.py check
System check identified no issues (0 silenced).
```

## Review Fixes: RED/GREEN Evidence

### RED

After adding regressions for provider-error sanitization, malformed workspace UUIDs, inactive workspaces, and missing Vertex configuration, the focused endpoint suite failed as expected:

```text
../.venv/bin/pytest tests/test_ai_connection_api.py -q
..FFFF
4 failed, 2 passed in 2.49s
```

The failures showed the raw provider message in the response, an uncaught malformed UUID validation error, an inactive workspace accepted with HTTP 200, and an uncaught Vertex `RuntimeError`.

### GREEN

The fix validates UUID input before the membership query, requires `workspace__is_active`, normalizes the Vertex configuration exception, and returns a fixed public message for all caught AI provider/configuration failures without logging the raw exception.

```text
../.venv/bin/pytest tests/test_ai_connection_api.py -q
6 passed in 2.22s

../.venv/bin/pytest tests/test_ai_connection_api.py tests/test_ai_providers.py -q
12 passed in 2.19s

../.venv/bin/pytest -q
22 passed in 8.29s

../.venv/bin/python manage.py check
System check identified no issues (0 silenced).
```
