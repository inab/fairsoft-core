from typing import List, Tuple

from fairsoft_core.constants import CONTRIBUTION_POLICY_TYPES, NO_GUIDE, PERMISSIONS_TYPES, RELEASE_POLICY_TYPES
from fairsoft_core.models.instance import Instance

from fairsoft_core.indicators.utils import *


def compR1_1(instance: Instance) -> Tuple[bool, List[str]]:
    """Existence of usage guides."""
    logs = []

    logs.append("⚙️ Checking if any documentation is a usage guide and URL is operational.")
    logs = log_documentation(instance, logs)

    logs.append(
        "Checking documentation types against excluded types: https://observatory.openebench.bsc.es/api/lists/no_guide"
    )

    documentation = instance.documentation or []

    if not documentation:
        logs.append("❌ No documentation found.")
        logs.append("Result: FAILED")

    no_guide_lower = [doc.lower() for doc in NO_GUIDE]
    operational_user_guide = False
    for doc in documentation:
        if doc.type.lower() not in no_guide_lower:
            if is_url_operational(doc.url):
                logs.append(
                    f"✅ The following documentation is a usage guide and operational: {doc.type} -- {doc.url}"
                )
                operational_user_guide = True
            else:
                logs.append(
                    f"❌ The following documentation is a usage guide but the URL is not operational: {doc.type} -- {doc.url}"
                )
        else:
            logs.append(
                f"❌ The following documentation is not a usage guide: {doc.type} -- {doc.url}"
            )

    if operational_user_guide:
        logs.append("✅ At least one documentation is a usage guide and its URL is operational.")
        logs.append("Result: PASSED")
        return True, logs
    else:
        logs.append("❌ No documentation is a usage guide.")
        logs.append("Result: FAILED")
        return False, logs


def compR2_1(instance) -> Tuple[bool, List[str]]:
    """Existence of license."""

    logs = []

    # Check for licenses
    logs.append("⚙️ Checking if a valid license is explicitly stated.")
    logs = log_licenses(instance, logs)

    license_info = instance.license or []

    for lic in license_info:
        logs.append(f"Checking license: {lic.name}")

        valid_license = 0
        invalid_license = 0
        if isinstance(lic.name, str) and lic.name.lower() not in [
            "unlicensed",
            "unknown",
            "unlicense",
        ]:
            logs.append(f"✅ A valid license is explicitly stated: {lic.name}")
            valid_license += 1
        else:
            logs.append(f"❌ Not valid license found: {lic.name}")
            invalid_license += 1

        if valid_license >= 1:
            if invalid_license == 0:
                logs.append("✅ At least one valid license is explicitly stated.")
                if valid_license > 1:
                    logs.append("⚠️ More than one valid license is explicitly stated.")

            else:
                logs.append("⚠️ There are invalid licenses.")

            logs.append("Result: PASSED")
            return True, logs

        else:
            logs.append("❌ No valid license found. Checking documentation.")

    # Check for documentation
    logs.append("⚙️ Checking if a valid license/terms of use is found in documentation.")
    logs = log_documentation(instance, logs)

    documentation = instance.documentation or []

    if not documentation:
        logs.append("❌ No documentation found.")
        logs.append("Result: FAILED")
        return False, logs

    else:
        logs.append(
            "Checking documentation types against valid document types and whether the URL is operational"
        )
        logs.append(
            "Valid document types: https://observatory.openebench.bsc.es/api/lists/permissions_types"
        )

        operational_license = False
        for doc in documentation:
            # check doc type and if doc url is operational
            lower_permissions_types = [d.lower() for d in PERMISSIONS_TYPES]
            if doc.type.lower() in (d.lower() for d in lower_permissions_types):
                if is_url_operational(doc.url):
                    logs.append(
                        f"✅ A valid license/terms of use is found in documentation and URL is operational: {doc.type} -- {doc.url}"
                    )
                    operational_license = True
                else:
                    logs.append(
                        f"❌ A valid license/terms of use is found in documentation but the URL is not operational: {doc.type} -- {doc.url}"
                    )

        if operational_license:
            logs.append(
                "✅ At least one valid license/terms of use is found in documentation and its URL is operational."
            )
            logs.append("Result: PASSED")
            return True, logs

    logs.append("❌ No valid license/terms of use found in documentation.")
    logs.append("Result: FAIL")
    return False, logs


def compR2_2(instance):
    """Technical conditions of use."""

    result, logs = compR2_1(instance)
    return result, logs


def compR3_1(instance) -> Tuple[bool, List[str]]:
    """Contribution policy."""
    logs = []

    logs.append(
        "⚙️ Checking if any documentation matches contribution policy types and the URL is operational."
    )
    logs = log_documentation(instance, logs)

    documentation = instance.documentation or []

    lower_contribution_policy_types = [policy.lower() for policy in CONTRIBUTION_POLICY_TYPES]
    contribution_policy_types_lower = [policy.lower() for policy in lower_contribution_policy_types]
    logs.append(
        "Checking against contribution policy types: https://observatory.openebench.bsc.es/api/lists/contribution_policy_types"
    )

    operational_contrib = False
    for doc in documentation:
        if doc.type.lower() in contribution_policy_types_lower:
            if is_url_operational(doc.url):
                logs.append(
                    f"✅ A documentation matches contribution policy types and URL is operational: {doc.type} -- {doc.url}"
                )
                operational_contrib = True
            else:
                logs.append(
                    f"❌ A documentation matches contribution policy types but URL is not operational: {doc.type} -- {doc.url}"
                )
        else:
            logs.append(
                f"❌ A documentation does not match contribution policy types: {doc.type} -- {doc.url}"
            )

    if operational_contrib:
        logs.append(
            "✅ At least one documentation matches contribution policy types and URL is operational."
        )
        logs.append("Result: PASSED")
        return True, logs
    else:
        logs.append("❌ No documentation matches contribution policy types.")
        logs.append("Result: FAILED")
        return False, logs


def compR3_2(instance) -> Tuple[bool, List[str]]:
    """Existence of credit."""

    logs = []

    logs.append("⚙️ Checking if any authors are stated.")
    logs = log_authors(instance, logs)

    authors = instance.authors or []

    has_credit = bool(authors)

    if has_credit:
        logs.append("✅ Authors are stated.")
        logs.append("Result: PASSED")
        return True, logs

    logs.append("❌ No authors are stated.")
    logs.append("Result: FAILED")
    return False, logs


def compR4_1(instance) -> Tuple[bool, List[str]]:
    """Usage of (public) version control."""

    logs = []

    logs.append("⚙️ Checking if version control is used.")

    version_control = instance.version_control or []
    logs.append(f"🔍 Received version control information: {version_control}")

    has_version_control = bool(version_control)

    if has_version_control:
        logs.append("✅ Version control is used.")
        logs.append("Result: PASSED")
        return True, logs

    logs.append("❌ No version control is used.")
    logs.append("Result: FAILED")
    return False, logs


def compR4_2(instance) -> Tuple[bool, List[str]]:
    """Release Policy."""

    logs = []

    logs.append(
        "⚙️ Checking if any documentation matches release policy types and the URL is operational."
    )
    logs = log_documentation(instance, logs)
    documentation = instance.documentation or []

    release_policy_types_lower = [policy.lower() for policy in RELEASE_POLICY_TYPES]
    logs.append(
        "Checking against release policy types: https://observatory.openebench.bsc.es/api/lists/release_policy_types"
    )

    operational_release = False
    for doc in documentation:
        if doc.type.lower() in release_policy_types_lower:
            if is_url_operational(doc.url):
                logs.append(
                    f"✅ A documentation matches release policy types and URL is operational: {doc.type} -- {doc.url}"
                )
                operational_release = True
            else:
                logs.append(
                    f"❌ A documentation matches release policy types but URL is not operational: {doc.type} -- {doc.url}"
                )
        else:
            logs.append(
                f"❌ A documentation does not match release policy types: {doc.type} -- {doc.url}"
            )

    if operational_release:
        logs.append(
            "✅ At least one documentation matches release policy types and URL is operational."
        )
        logs.append("Result: PASSED")
        return True, logs

    else:
        logs.append("❌ No documentation matches release policy types.")
        logs.append("Result: FAILED")
        return False, logs
