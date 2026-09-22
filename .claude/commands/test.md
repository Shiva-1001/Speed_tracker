# Run tests

Run the complete test suite:

```bash
pytest -q
```

If a focused test is needed:

```bash
pytest -q tests/test_expenses.py
```

When changing business logic, run the full suite before considering the change complete.
