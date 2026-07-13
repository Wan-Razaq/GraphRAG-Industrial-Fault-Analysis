# Security Guide

## Security Goals

This project handles industrial maintenance data, provider API keys, and graph database credentials. The security goals are:

- Keep credentials out of git.
- Keep raw and processed datasets out of git.
- Keep generated extraction outputs out of git unless explicitly reviewed and approved.
- Avoid exposing hosted database identifiers in source code.
- Make accidental `git add` operations safer through `.gitignore`.
- Keep public documentation useful without publishing sensitive data.

## Secret Management

Store local secrets in `.env`, copied from `.env.example`.

Required:

```text
OPENAI_API_KEY
NEO4J_URI
NEO4J_USER
NEO4J_PASS
```

Optional for selected experiments:

```text
NEO4J_BROWSER_URL
ANTHROPIC_API_KEY
OPENROUTER_API_KEY
DEKA_API_KEY
GROQ_API_KEY
```

Rules:

- Do not hardcode API keys in Python, notebooks, BAML, Markdown, or shell commands.
- Do not print environment variable values.
- Do not commit `.env` or provider-specific secrets files.
- Use least-privilege credentials for Neo4j where possible.
- Rotate keys immediately if they are accidentally exposed.

## Code-Level Protections

The runtime code follows these conventions:

- `src/utils/chatbot_service.py` validates that `OPENAI_API_KEY` exists but does not print it.
- `src/utils/retriever.py` validates required Neo4j/OpenAI variables but does not print their values.
- `src/streamlit_app.py` reads `NEO4J_BROWSER_URL` from the environment instead of hardcoding a hosted database URL.
- BAML clients reference provider keys through `env.*` variables.

## Data Protection

The following should remain local:

- Raw IBM3 and IBM4 maintenance logs.
- Manual-book images and PDFs.
- Processed JSON/JSONL/CSV/Excel datasets.
- Doccano annotation exports.
- BAML extraction outputs.
- Per-case evaluation detail JSON files.
- Neo4j exports and dumps.
- Model checkpoints.

The repository `.gitignore` blocks the most common sensitive artifact types and directories. This is a safety net, not a substitute for reviewing staged files.

## Notebook Security

Treat notebooks as sensitive until reviewed. They can contain:

- API call traces.
- Model prompts.
- Raw log snippets.
- Extracted entities.
- Case IDs.
- Embedded images.
- Absolute local file paths.
- Large base64 plot outputs.

Before committing a notebook:

```bash
jupyter nbconvert --clear-output --inplace path/to/notebook.ipynb
git diff -- path/to/notebook.ipynb
```

Only stage the notebook if the diff is safe.

## Dependency Security

Recommended practices:

- Use a virtual environment.
- Install only from `requirements.txt` unless a new dependency is required.
- Review any new dependency before adding it.
- Keep provider SDK versions compatible with the code and BAML generated client.
- Rebuild BAML client files only from reviewed `.baml` schema changes.

## GitHub Push Checklist

Before every push:

```bash
git status --short --ignored
git diff --cached --name-only
git diff --cached --stat
```

Then verify:

- No `.env` or secret file is staged.
- No data directory is staged.
- No generated JSON/JSONL/CSV/XLSX/PDF file is staged.
- No model checkpoint is staged.
- No ad-hoc experiment notebook is staged.
- No local output folder is staged.
- No hosted Neo4j instance identifier is newly introduced into source.

Optional tracked-file secret scan:

```bash
git grep -n -E "(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9_]{20,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY|AKIA[0-9A-Z]{16})"
```

If this command prints a real secret, stop and rotate it.

## Incident Response

If a credential is accidentally committed:

1. Revoke or rotate the exposed credential immediately.
2. Remove the secret from the working tree.
3. Remove the secret from git history using an approved history-rewrite tool.
4. Force-push only after coordinating with collaborators.
5. Audit downstream logs and services for suspicious use.

If sensitive data is accidentally committed:

1. Stop pushing additional commits.
2. Remove the data from history, not just from the latest commit.
3. Confirm GitHub no longer exposes the file.
4. Check forks, releases, tags, and pull request diffs.
5. Document the incident and mitigation.

## Public Release Rule

A file is safe to push only if it is all three:

1. Necessary for code, documentation, schema, or reviewed non-sensitive reporting.
2. Free of credentials and hosted secret identifiers.
3. Free of raw, processed, or reconstructable sensitive dataset content.
