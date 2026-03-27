## Minimal CodeMeta → FAIRsoft core mapping

The FAIRsoft core evaluator expects metadata in the internal `Instance` shape.  
When the input is a `codemeta.json`, a lightweight adapter can convert a subset of common CodeMeta fields into that internal structure.

This first mapping is intentionally minimal: it covers the most obvious fields and ignores ambiguous or evaluator-specific enrichments.

| CodeMeta field | FAIRsoft core field | Notes |
|---|---|---|
| `name` | `name` | Direct mapping. |
| `description` | `description` | Normalized to a list of strings. |
| `softwareVersion` | `version` | Preferred version source. Normalized to a list. |
| `version` | `version` | Used if `softwareVersion` is absent. |
| `alternateName` | `label` | Mapped as alternative labels/names. |
| `codeRepository` | `repository` | Normalized to a list of URLs. |
| `downloadUrl` | `download` | Normalized to a list of URLs. |
| `url` | `webpage` | Preferred webpage/homepage source. |
| `homepage` | `webpage` | Used if `url` is absent. |
| `sameAs` | `links` | Additional related URLs. |
| `relatedLink` | `links` | Appended to `links` when present. |
| `license` | `license` | Strings become `{name, url=None}`. Objects use obvious `name`/URL fields. |
| `author` | `authors` | Mapped to FAIRsoft `Person` entries. |
| `contributor` | `authors` | Also mapped to FAIRsoft `Person` entries. |
| `maintainer` | `authors` | Mapped as `Person` entries with `maintainer=true`. |
| `keywords` | `tags` | Normalized to a list of strings. |
| `operatingSystem` | `os` | Normalized to a list of strings. |
| `readme` | `documentation` | Added as documentation of type `readme`. |
| `softwareHelp` | `documentation` | Added as documentation of type `help`. |
| `documentation` | `documentation` | Added as documentation of type `general`. |
| `citation` | `publication` | Minimal publication extraction. |
| `referencePublication` | `publication` | Used if present; minimal extraction only. |
| `applicationCategory` | `topics` | Mapped as lightweight controlled terms. |

### Author mapping

The adapter maps `author`, `contributor`, and `maintainer` into the FAIRsoft `authors` field.

#### Input forms supported
- plain string
- object with fields such as `name`, `email`, `@type`, `type`

#### Output form
Each person is converted into an object like:

```json
{
  "name": "Jane Doe",
  "type": "Person",
  "email": "jane@example.org",
  "maintainer": false
}
```

For entries coming from `maintainer`, `maintainer` is set to `true`.

### License mapping

The adapter supports two common cases:

#### License as string
```json
"license": "Apache-2.0"
```

becomes:

```json
[
  {
    "name": "Apache-2.0",
    "url": null
  }
]
```

#### License as object
If the value is an object, the adapter extracts the most obvious name and URL-like fields.

### Publication mapping

Publication extraction is intentionally minimal.

The adapter attempts to extract:

- `doi`
- `title`
- `year`

from objects found in:

- `citation`
- `referencePublication`

This is only meant to provide a minimal compatible structure for evaluation. It does not perform publication enrichment.

### Documentation mapping

The following CodeMeta-like fields are treated as documentation sources:

- `readme`
- `softwareHelp`
- `documentation`

Each discovered URL is converted into a FAIRsoft documentation item:

```json
{
  "type": "general",
  "url": "https://example.org/docs"
}
```

### Fields not mapped in the minimal adapter

The first version of the adapter does **not** attempt to infer or populate the following FAIRsoft fields:

- `type`
- `input`
- `output`
- `operations`
- `edam_topics`
- `edam_operations`
- `bioschemas`
- `https`
- `ssl`
- `operational`
- `version_control`
- `publication` enrichment beyond minimal extraction
- any JSON-LD graph expansion or remote context resolution

### Design note

The adapter does **not** change the evaluator core contract.

The evaluation flow remains:

```text
CodeMeta JSON -> adapter -> FAIRsoft internal metadata -> Instance(...) -> evaluation
```

This keeps the FAIRsoft core independent from external metadata formats and allows additional input adapters to be added later.
"""