# Data And Artifact Policy

## Short Version

Do not push:

- Credentials or secret files.
- Raw maintenance logs.
- Manual-book images or PDFs.
- Processed datasets.
- Annotation exports.
- Model extraction JSON files.
- Evaluation detail JSON files.
- Local experiment run directories.
- Model checkpoints or binary model files.
- Notebooks that still contain sensitive outputs.

The repository should contain source code, BAML schemas, documentation, and reviewed non-sensitive figures only.

## Local Data Layout

Use the following local-only layout when running the pipeline:

```text
data/
|-- raw/
|   |-- IBM3_onderhoud_raw.xlsx
|   |-- IBM4_onderhoud_raw.xlsx
|   `-- manual_images_or_exports/
|-- processed/
|   |-- doccano_ibm3_ibm4_grouped_ready.jsonl
|   |-- 20_cases_for_baml_fewshot.jsonl
|   |-- remaining_cases_for_baml_fewshot.jsonl
|   `-- formatted_annotated_cases_*.json
`-- external/
```

These filenames are examples based on the notebooks. They are intentionally ignored by git.

## Generated Outputs

Common generated files include:

```text
baml_extracted_20_cases*.json
baml_extracted_remaining_cases*.json
manual_book_fault_reports.json
per_case_evaluation_details_*.json
prompt_only_*/*
```

These files can contain source text, model outputs, annotations, or derived dataset records. Keep them local unless a file has been explicitly anonymized, reviewed, and approved for publication.

## Curated Figures

The repository currently includes three curated evaluation figures:

```text
experiments/evaluation_results/error_breakdown_missing_vs_hallucination.png
experiments/evaluation_results/field_wise_f1_grouped_bar_bootstrap_ci.png
experiments/evaluation_results/field_wise_f1_heatmap.png
```

Before adding any new figure, verify that it does not expose:

- Raw maintenance log text.
- Case-level confidential details.
- Credentials, paths, usernames, or database identifiers.
- Proprietary manual content.

## Notebook Handling

Notebooks are useful for research traceability, but they are also high risk because outputs can include data, prompts, model responses, images, and paths.

Before committing a notebook:

1. Clear execution outputs.
2. Remove embedded data samples unless approved.
3. Remove absolute local paths.
4. Check that no secret values appear in code, markdown, or outputs.
5. Restart and run only if the resulting outputs are safe to publish.
6. Review the diff before staging.

Command to clear outputs:

```bash
jupyter nbconvert --clear-output --inplace path/to/notebook.ipynb
```

Do not run this command on notebooks you are not intending to change, because it will rewrite the file.

## Neo4j Data

Neo4j contains the operational graph representation of the extracted fault knowledge. Treat the database as sensitive if it contains raw or derived maintenance information.

Do not commit:

- Neo4j database dumps.
- Cypher exports containing full datasets.
- Database credentials.
- Specific hosted database instance URLs unless they are intended to be public.

The Streamlit app reads `NEO4J_BROWSER_URL` from the environment so hosted database identifiers can stay local.

## Model Files

Do not commit:

```text
trained_models/
checkpoints/
*.pt
*.pth
*.bin
*.gguf
*.safetensors
*.onnx
*.ckpt
```

If a small model artifact must be shared, publish it through an approved artifact store instead of git and document the retrieval process.

## Pre-Push Checklist

Run:

```bash
git status --short --ignored
git diff --cached --name-only
git diff --cached --stat
```

Confirm staged files do not include:

- `.env`
- `data/`
- `datasets/`
- generated JSON/JSONL/CSV/XLSX/PDF files
- local experiment folders
- model checkpoints
- notebook output changes

If a sensitive file was staged by mistake:

```bash
git restore --staged path/to/file
```

If a sensitive file was already committed, do not just delete it in a later commit. Rotate exposed credentials and remove the secret from history with an approved history-rewrite process.
