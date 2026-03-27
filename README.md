# fairsoft-core

Core FAIRsoft evaluation engine for research software metadata.

This package contains the reusable evaluation logic for FAIRsoft indicators and scores.

## Installation

For local development:

```bash
pip install -e .
```

To install directly from GitHub:

```bash
pip install  "git+https://github.com/inab/fairsoft-core.git@v0.1.0"
```


## What this package does

- computes FAIRsoft indicators
- computes FAIR scores
- generates feedback
- exposes a CLI for evaluation workflows

## Input expectations

The core evaluator expects metadata already normalized to the internal FAIRsoft input model.

This means:

- the package does **not** prepare or enrich raw metadata
- the input JSON must already match the structure expected by the core `Instance` model

## Usage

### Full FAIRsoft evaluation

Run a full FAIRsoft evaluation from a JSON file:

```bash
fairsoft evaluate path/to/metadata.json
```

Write output to a file:

```bash
fairsoft evaluate path/to/metadata.json --output result.json
```

Select only part of the evaluation output:

```bash
fairsoft evaluate path/to/metadata.json --select result
fairsoft evaluate path/to/metadata.json --select logs
fairsoft evaluate path/to/metadata.json --select feedback
```

Choose compact JSON output:

```bash
fairsoft evaluate path/to/metadata.json --select result --format json-compact
```

### Single-indicator evaluation

List the indicators currently available in the CLI:

```bash
fairsoft indicator --list
``` 

Describe one indicator:

```bash
fairsoft indicator --describe F3_1
fairsoft indicator --describe searchability_in_registries
```

Run indicator `F3_1` by ID:

```bash
fairsoft indicator F3_1 path/to/metadata.json
```

Run the same indicator by name:

```bash
fairsoft indicator searchability_in_registries path/to/metadata.json
```

Select only the result or logs:

```bash
fairsoft indicator F3_1 path/to/metadata.json --select result
fairsoft indicator F3_1 path/to/metadata.json --select logs
```

Write compact output to a file:

```bash
fairsoft indicator F3_1 path/to/metadata.json --select logs --format json-compact --output f3_1_logs.json
```


## CLI output options

### `--select`

`--select` controls which part of the output is returned.

Available values:

- `full`
- `result`
- `logs`
- `feedback`

For full evaluation, the returned structure contains:

- `result`
- `logs`
- `feedback`

For single-indicator commands, the CLI keeps the same output contract, although some indicators may return an empty `feedback` field.

### `--format`

`--format` controls serialization.

Available values:

- `json`
- `json-compact`

Examples:

```bash
fairsoft evaluate path/to/metadata.json --select full --format json
fairsoft evaluate path/to/metadata.json --select result --format json-compact
fairsoft indicator F3_1 path/to/metadata.json --select logs --format json
```

## Indicator metadata requirements

> **Note.** The “Equivalent CodeMeta fields” column reflects the current minimal adapter implemented in `fairsoft-core`, not the full set of CodeMeta fields that could theoretically be mapped in future versions. Entries marked as “partially” indicate indirect or limited support. 

| Indicator | Name | Fields used | Minimum metadata | Equivalent CodeMeta fields | Not applicable when |
|---|---|---|---|---|---|
| A1_1 | `existence_of_api_or_web` | `webpage`, `type` | `webpage` | `url`, `homepage` | `super_type == 'no_web'` |
| A1_2 | `downloadable_and_buildable_working_version` | `download`, `src`, `type` | `download` or `src` | `downloadUrl` | `super_type == 'web'` |
| A1_3 | `installation_instructions` | `inst_instr`, `documentation`, `source`, `type` | `inst_instr` or `documentation` or `source` | `readme`, `softwareHelp`, `documentation` | `super_type == 'web'` |
| A1_4 | `test_data` | `test`, `documentation`, `type` | `test` or `documentation` | no direct minimal mapping | `super_type == 'web'` |
| A1_5 | `source_code` | `src`, `type` | `src` | no direct minimal mapping (`codeRepository` is mapped to `repository`, not `src`) | `super_type == 'web'` |
| A3_1 | `registration_not_compulsory` | `registration_not_mandatory` | `registration_not_mandatory` | no direct minimal mapping | — |
| A3_2 | `version_for_free_os` | `os`, `type` | `os` | `operatingSystem` | `super_type == 'web'` |
| A3_3 | `availability_for_several_os` | `os`, `type` | `os` | `operatingSystem` | `super_type == 'web'` |
| A3_4 | `availability_on_free_e_infrastructures` | `e_infrastructures`, `webpage`, `source`, `type` | `e_infrastructures` or `webpage` or `source` | partially `url`, `homepage`, `sameAs`, `relatedLink` | `super_type == 'web'` |
| A3_5 | `availability_on_several_e_infrastructures` | `e_infrastructures`, `webpage`, `source`, `type` | `e_infrastructures` or `webpage` or `source` | partially `url`, `homepage`, `sameAs`, `relatedLink` | `super_type == 'web'` |
| F1_2 | `semantic_versioning` | `version` | `version` | `softwareVersion`, `version` | — |
| F2_1 | `structured_metadata` | `source` | `source` | no direct minimal mapping | — |
| F2_2 | `metadata_with_controlled_vocabularies` | `topics`, `operations` | `topics` or `operations` | partially `applicationCategory` | — |
| F3_1 | `searchability_in_registries` | `source`, `registries` | `source` or `registries` | no direct minimal mapping | — |
| F3_2 | `searchability_in_software_repositories` | `repository` | `repository` | `codeRepository` | — |
| F3_3 | `searchability_in_literature` | `publication` | `publication` | `citation`, `referencePublication` | — |
| I1_1 | `standard_data_formats` | `input`, `output` | `input` or `output` | no direct minimal mapping | — |
| I1_2 | `api_standard_specification` | `documentation`, `type` | `documentation` | `documentation`, `softwareHelp`, `readme` | `super_type == 'no_web'` |
| I1_3 | `verifiable_data_formats` | `input`, `output` | `input` or `output` | no direct minimal mapping | — |
| I1_4 | `flexibility_of_supported_data_formats` | `input`, `output` | `input` and `output` | no direct minimal mapping | — |
| I2_1 | `api_or_library_version` | `type` | `type` | no direct minimal mapping | — |
| I2_2 | `e_infrastructure_compatibility` | `e_infrastructures`, `webpage`, `source` | `e_infrastructures` or `webpage` or `source` | partially `url`, `homepage`, `sameAs`, `relatedLink` | — |
| I3_1 | `dependencies_statement` | `dependencies` | `dependencies` | no direct minimal mapping | — |
| I3_2 | `dependencies_provided` | `source`, `registries`, `links` | `source` or `registries` or `links` | partially `sameAs`, `relatedLink` | — |
| I3_3 | `dependency_aware_system` | `source`, `registries`, `links` | `source` or `registries` or `links` | partially `sameAs`, `relatedLink` | — |
| R1_1 | `usage_guides` | `documentation` | `documentation` | `readme`, `softwareHelp`, `documentation` | — |
| R2_1 | `license` | `license`, `documentation` | `license` or `documentation` | `license`, partially `documentation` | — |
| R2_2 | `technical_conditions_of_use` | `license`, `documentation` | `license` or `documentation` | `license`, partially `documentation` | — |
| R3_1 | `contribution_policy` | `documentation` | `documentation` | `documentation`, `readme`, `softwareHelp` | — |
| R3_2 | `credit` | `authors` | `authors` | `author`, `contributor`, `maintainer` | — |
| R4_1 | `public_version_control` | `version_control` | `version_control` | no direct minimal mapping (`codeRepository` suggests it, but the adapter does not infer `version_control`) | — |
| R4_2 | `release_policy` | `documentation` | `documentation` | `documentation`, `readme`, `softwareHelp` | — |

## Python usage

Run a full FAIRsoft evaluation programmatically:

```python
from fairsoft_core.evaluation import run_fairsoft_evaluation

result = run_fairsoft_evaluation(tool_metadata)
```

## Exit codes

The CLI uses the following exit codes:

- `0`: success
- `1`: unexpected error
- `2`: input error or invalid CLI usage
- `3`: evaluation error
- `4`: input file not found
- `5`: command not implemented

## Development notes

A common local workflow is:

```bash
ruff check . --fix
ruff format .
pytest
``` 

Keep the `pyproject.toml` as the source of truth of the version. 

There is `pre-push` hook that run all tests. 