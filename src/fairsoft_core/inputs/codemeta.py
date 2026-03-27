from __future__ import annotations

from typing import Any


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _first_non_empty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def _clean_list(values: list[Any]) -> list[Any]:
    return [v for v in values if v not in (None, "", {}, [])]


def _string_list(value: Any) -> list[str]:
    out: list[str] = []
    for item in _as_list(value):
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _extract_url(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        return _first_non_empty(
            value.get("@id"),
            value.get("url"),
        )
    return None


def _extract_name(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        return _first_non_empty(
            value.get("name"),
            value.get("legalName"),
            value.get("@id"),
        )
    return None


def _extract_person(value: Any, maintainer: bool = False) -> dict[str, Any] | None:
    if isinstance(value, str):
        name = value.strip()
        if not name:
            return None
        return {
            "name": name,
            "type": "Person",
            "email": None,
            "maintainer": maintainer,
        }

    if isinstance(value, dict):
        name = _extract_name(value)
        email = value.get("email")
        person_type = value.get("@type") or value.get("type") or "Person"

        if not name:
            return None

        return {
            "name": name,
            "type": str(person_type),
            "email": email if email not in ("", None) else None,
            "maintainer": maintainer,
        }

    return None


def _extract_people(values: Any, maintainer: bool = False) -> list[dict[str, Any]]:
    people: list[dict[str, Any]] = []
    for item in _as_list(values):
        person = _extract_person(item, maintainer=maintainer)
        if person:
            people.append(person)
    return people


def _extract_license(value: Any) -> list[dict[str, Any]]:
    licenses: list[dict[str, Any]] = []

    for item in _as_list(value):
        if isinstance(item, str):
            if item.strip():
                licenses.append({"name": item.strip(), "url": None})

        elif isinstance(item, dict):
            name = _extract_name(item)
            url = _extract_url(item)

            if name or url:
                licenses.append(
                    {
                        "name": name or url,
                        "url": url,
                    }
                )

    return licenses


def _extract_controlled_terms(values: Any) -> list[dict[str, Any]]:
    terms: list[dict[str, Any]] = []

    for item in _as_list(values):
        if isinstance(item, str):
            if item.strip():
                terms.append(
                    {
                        "vocabulary": None,
                        "term": item.strip(),
                        "uri": None,
                    }
                )

        elif isinstance(item, dict):
            term = _extract_name(item)
            uri = _extract_url(item)

            if term or uri:
                terms.append(
                    {
                        "vocabulary": item.get("inDefinedTermSet"),
                        "term": term,
                        "uri": uri,
                    }
                )

    return terms


def _extract_documentation(data: dict[str, Any]) -> list[dict[str, Any]]:
    documentation: list[dict[str, Any]] = []

    # Common obvious codemeta-ish places
    candidates = [
        ("readme", "readme"),
        ("softwareHelp", "help"),
        ("documentation", "general"),
    ]

    for field_name, doc_type in candidates:
        for item in _as_list(data.get(field_name)):
            url = _extract_url(item)
            if url:
                documentation.append(
                    {
                        "type": doc_type,
                        "url": url,
                    }
                )

    return documentation


def _extract_publications(value: Any) -> list[dict[str, Any]]:
    publications: list[dict[str, Any]] = []

    for item in _as_list(value):
        if not isinstance(item, dict):
            continue

        doi = item.get("identifier") if isinstance(item.get("identifier"), str) else item.get("doi")
        title = item.get("name") or item.get("headline") or item.get("title")
        year = item.get("datePublished") or item.get("year")
        url = _extract_url(item)

        publication: dict[str, Any] = {}

        if doi:
            publication["doi"] = doi
        if title:
            publication["title"] = title
        if year:
            if isinstance(year, str) and len(year) >= 4 and year[:4].isdigit():
                publication["year"] = year[:4]
            else:
                publication["year"] = year

        # Your model accepts pmid optionally, but CodeMeta usually will not have it
        # so we do not invent one.
        if publication:
            if url and "doi" not in publication:
                publication["doi"] = url
            publications.append(publication)

    return publications


def load_codemeta_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """
    Minimal adapter from CodeMeta-like JSON to the FAIRsoft Instance input shape.

    Notes:
    - No JSON-LD expansion/resolution is performed.
    - Only obvious fields are mapped.
    - Ambiguous fields are ignored for now.
    """
    authors = _extract_people(data.get("author"))
    authors.extend(_extract_people(data.get("contributor")))
    authors.extend(_extract_people(data.get("maintainer"), maintainer=True))

    metadata: dict[str, Any] = {
        "name": data.get("name"),
        "description": _string_list(data.get("description")),
        "version": _string_list(_first_non_empty(data.get("softwareVersion"), data.get("version"))),
        "repository": _clean_list(_string_list(data.get("codeRepository"))),
        "download": _clean_list(_string_list(data.get("downloadUrl"))),
        "webpage": _clean_list(
            _string_list(_first_non_empty(data.get("url"), data.get("homepage")))
        ),
        "license": _extract_license(data.get("license")),
        "authors": authors,
        "documentation": _extract_documentation(data),
        "tags": _string_list(data.get("keywords")),
        "os": _string_list(data.get("operatingSystem")),
        "publication": _extract_publications(
            _first_non_empty(data.get("citation"), data.get("referencePublication"))
        ),
        "links": _clean_list(_string_list(data.get("sameAs"))),
    }

    # Optional obvious labels
    alternate_names = _string_list(data.get("alternateName"))
    if alternate_names:
        labels = []
        if data.get("name"):
            labels.append(data["name"])
        labels.extend(alternate_names)
        metadata["label"] = list(dict.fromkeys(labels))

    # Optional obvious topics from applicationCategory
    application_category = data.get("applicationCategory")
    if application_category:
        metadata["topics"] = _extract_controlled_terms(application_category)

    # Optional obvious source links from relatedLink
    related_links = _string_list(data.get("relatedLink"))
    if related_links:
        metadata["links"] = list(dict.fromkeys(metadata.get("links", []) + related_links))

    # Remove empty values so Instance defaults can do their job
    cleaned_metadata = {
        key: value for key, value in metadata.items() if value not in (None, "", [], {})
    }

    return cleaned_metadata
