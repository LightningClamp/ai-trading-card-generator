# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | ✅        |
| 0.3.x   | ⚠️ security fixes only |
| < 0.3   | ❌        |

## Reporting a vulnerability

Do **not** open a public issue for security bugs. Email
`security@cardforge.dev` with:

- A description of the issue and its impact.
- Steps to reproduce, or a proof-of-concept cardpack / prompt.
- The version string from `cardforge --version`.

We aim to acknowledge within 72 hours and ship a patch within 14 days for
high-severity issues.

## Threat model

`ai-trading-card-generator` is a local desktop tool. The realistic attack
surface is:

1. **Malicious cardpacks.** `.cardpack` files are zip archives containing
   JSON, Jinja2 templates, and PNG assets. A crafted template can execute
   arbitrary Jinja2 — we sandbox template rendering in
   `cardforge/services/template_sandbox.py` and reject packs that request
   attribute access on `__class__`, `__globals__`, or `__subclasses__`.
   If you find a sandbox escape, that's a critical bug.
2. **Untrusted model weights.** Loading a `.safetensors` or `.gguf` from a
   third party is a code-execution risk if the loader is naive. We use
   `safetensors` with `weights_only=True` and refuse `.pt` / `.pth` files.
3. **Prompt-injection via card text.** Card copy is fed back into the LLM
   for stat balancing. We strip control tokens and cap card text at 2 KB
   before re-injection.

## Out of scope

- Local privilege escalation from an already-compromised user account.
- Denial of service from absurdly large prompts (cap is enforced, but a
  10 GB prompt is your problem).
- Anything requiring the attacker to already have write access to the
  install directory.

## Hardening checklist for pack authors

- Sign your packs with `cardforge pack sign` (Ed25519).
- Keep templates free of `{% include %}` on absolute paths.
- Vendor your art assets under `assets/` inside the pack, not remote URLs.