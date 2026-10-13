# Contributing to ai-trading-card-generator

Thanks for wanting to help forge cards. This project is a Windows desktop
utility that turns prompts, stat blocks, and art references into printable
trading cards. Contributions of every flavor are welcome: new renderers,
new card templates, better LLM prompt chains, and bug reports.

## Dev environment

- Python 3.11 or 3.12 (3.13 works but the `torch` wheel matrix is still
  thin — stick to 3.12 if you want CUDA).
- Windows 10/11 is the primary target. Linux/macOS work for headless
  generation but the Qt shell is Windows-first.
- `pip install -r requirements.txt`
- `python -m cardforge.bootstrap.app` to launch the desktop shell.

## Branching

- `main` — shipped releases only.
- `dev` — integration branch, PRs target this.
- `feat/<short-name>` — feature branches.
- `fix/<issue-number>` — bugfix branches.

## Code style

- `ruff` for lint, `black` for format, `mypy --strict` on `cardforge/core`.
- Type hints mandatory on all public functions.
- No bare `except:`. Catch specific exceptions, log with `structlog`.
- Card template files are Jinja2 — keep logic out of templates, push it
  into the renderer context builders.

## Tests

```
pytest -q
pytest --cov=cardforge --cov-report=term-missing
```

New renderer or prompt chain → new test in `tests/`. Golden-image tests
for renderers live in `tests/fixtures/golden/` — regenerate with
`python -m cardforge.tools.regen_goldens` and eyeball the diff before
committing.

## Card pack format

See `docs/cardpack_spec.md`. Bump `CARD_PACK_VERSION` in
`cardforge/core/pack.py` if you change the on-disk schema.

## Pull requests

1. One feature or fix per PR.
2. Describe the user-visible change at the top.
3. Include a screenshot for anything touching the renderer.
4. CI must pass: `ruff`, `mypy`, `pytest`.

## Reporting bugs

Open an issue with: OS build, Python version, GPU + driver (if relevant),
the exact prompt or cardpack that triggered it, and the traceback from
`logs/cardforge.log`.

## License

By contributing you agree your work is released under the MIT license.