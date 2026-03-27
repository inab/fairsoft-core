from typing import List, Tuple

from fairsoft_core.constants import (
    E_INFRASTRUCTURES,
    E_INFRASTRUCTURES_SOURCES,
    FREE_OS,
    INSTALL_INTRUCTIONS_SOURCES,
)

from fairsoft_core.indicators.utils import *


def compA1_1(instance) -> Tuple[bool, str]:
    """Existence of API or web."""

    logs = []

    # Check if the software is not web-based (not applicable)
    super_type = instance.super_type
    if super_type == "no_web":
        logs.append("This is not a web-based software. This indicator is not applicable. ")
        return False, logs

    webpage = instance.webpage if instance.webpage else None

    logs.append("⚙️ Checking if API or web is operational")

    # each webpage in a line in logs
    logs = log_webpages(instance, logs)

    if webpage is None:
        logs.append("❌ No webpage provided.")
        logs.append("Result: FAILED")
        return False, logs

    for url in webpage:
        logs.append(f"⚙️ Checking URL: {url}")
        if is_url_operational(url):
            logs.append(f"✅ {url} API or web URL is operational.")
            logs.append("Result: PASSED")
            return True, logs
        else:
            logs.append(f"❌ {url} API or web URL is not operational.")

    logs.append("❌ Result: API or web URLs are not operational. Returning False.")
    logs.append("Result: PASSED")
    return False, logs


def compA1_2(instance) -> Tuple[bool, str]:
    """Existence of downloadable and buildable software working version."""

    logs = []

    # Check if the software is web-based (not applicable)
    super_type = instance.super_type
    if super_type == "web":
        logs.append("This is a web-based software. This indicator is not applicable.")
        return False, logs

    # check if download links are operational. At least one must work
    logs.append("⚙️ Checking if download links are operational")
    download = instance.download + instance.src

    # each download in one line in logs
    logs = log_downloads(download, logs)

    if bool(download):
        for url in download:
            logs.append(f"⚙️ Checking URL: {url}")
            if is_url_operational(url):
                logs.append(f"✅ {url} download link is operational.")
                logs.append("Status: PASSED")
                return True, logs
            else:
                logs.append(f"❌ {url} download link is not operational.")

    logs.append("❌ Result: No download link provided.")
    logs.append("Status: FAILED")
    return False, logs


def compA1_3(instance) -> Tuple[bool, str]:
    """Existence of installation instructions."""

    logs = []

    # Check if the software is web-based (not applicable)
    super_type = instance.super_type
    if super_type == "web":
        logs.append("This is a web-based software. This indicator is not applicable.")
        return False, logs

    # 1. Check if @inst_instr is True
    logs.append("⚙️ Checking if installation instructions are provided")
    inst_instr = instance.inst_instr
    logs.append(f"🔍 Received inst_instr: {inst_instr}")
    if inst_instr is True:
        logs.append("✅ Installation instructions are provided.")
        logs.append("Result: PASSED")
        return True, logs
    else:
        logs.append("❌ Installation instructions are not provided. Checking documentation ...")

    # 2. Check if there is a valid document similar to installation instructions
    # Check if the url is operational
    logs.append(
        "⚙️ Checking if there are installation instructions and whether they are operational"
    )
    documentation = instance.documentation

    logs = log_documentation(instance, logs)

    if documentation is None or documentation == []:
        logs.append("❌ No documentation provided.")

    installation_instructions = False
    installation_types = [
        "installation instructions",
        "installation",
        "installation guide",
        "install",
    ]
    for doc in documentation:
        if doc.type.lower() in installation_types:
            installation_instructions = True
            if is_url_operational(doc.url):
                logs.append("✅ Installation instructions are available and operational.")
                logs.append("Result: PASSED")
                return True, logs
            else:
                logs.append("❌ Installation instructions URL is not operational.")

    if installation_instructions:
        logs.append(
            "❌ Installation instructions are available but the URL is not operational. Checking sources ..."
        )
    else:
        logs.append("❌ No installation instructions found in documentation. Checking sources ...")

    # 3. Check if any of the sources provide installation instructions
    logs.append("⚙️ Checking if any of the sources provide installation instructions")
    source = instance.source
    logs = log_sources(instance, logs)
    if source is None or source == []:
        logs.append("❌ No source provided.")
        logs.append("Rsult: FAILED")
        return False, logs

    logs.append(f"Sources that have installation instructions: {INSTALL_INTRUCTIONS_SOURCES}")

    has_install_instruction_source = any(source in INSTALL_INTRUCTIONS_SOURCES for source in source)

    if has_install_instruction_source:
        logs.append("✅ At least one source provides installation instructions.")
        logs.append("Result: PASSED")
        return True, logs

    logs.append("❌ No source provides installation instructions.")
    logs.append("Result: FAILED")
    return False, logs


def compA1_4(instance) -> Tuple[bool, List[str]]:
    """Existence of test data."""

    logs = []

    # Check if the software is web-based (not applicable)
    super_type = instance.super_type
    if super_type == "web":
        logs.append("This is a web-based software. This indicator is not applicable.")
        return False, logs

    # 1. Check if test data is explicitly provided and if the provided URL is operational
    logs.append(
        "⚙️ Verifying if test data is explicitly provided and if the provided URL is operational."
    )

    logs = log_test_data_URLs(instance, logs)

    test_data_urls = instance.test
    if not test_data_urls:
        logs.append("❌ No test data provided.")

    has_operationsl_test_data = False
    for url in test_data_urls:
        logs.append(f"⚙️ Checking URL: {url}")
        if is_url_operational(url):
            logs.append(f"✅ {url} test data URL is operational.")
            has_operationsl_test_data = True
        else:
            logs.append(f"❌ {url} test data URL is not operational.")

    if has_operationsl_test_data:
        logs.append("✅ Test data is available and operational.")
        logs.append("Result: PASSED")
        return True, logs
    else:
        logs.append("❌ No operational test data found. Checking documentation ...")

    # 2. Check if test data is present in documentation and its URL is operational
    logs.append("⚙️ Checking if test data is present in documentation and its URL is operational")
    logs = log_documentation(instance, logs)
    if not instance.documentation:
        logs.append("❌ No documentation provided.")
        logs.append("Result: FAILED")
        return False, logs

    # Check whether test data is provided in documentation and test data url operational
    has_test_data_in_docs = False
    for doc in instance.documentation:
        if doc.type.lower() == "test data":
            if is_url_operational(doc.url):
                has_test_data_in_docs = True
                logs.append(
                    f"✅ Test data is available in documentation and URL operational. URL: {doc.url}"
                )
            else:
                logs.append(f"❌ Test data URL is not operational. URL: {doc.url}")

    if has_test_data_in_docs:
        logs.append("✅ Test data is available and operational.")
        logs.append("Result: PASSED")
        return True, logs

    else:
        logs.append(
            "❌ No test data found in documentation or the provided URL is not operational."
        )
        logs.append("Result: FAILED")
        return False, logs


def compA1_5(instance) -> Tuple[bool, List[str]]:
    """Existence of software source code."""
    logs = []

    # Check if the software is web-based (not applicable)
    super_type = instance.super_type
    if super_type == "web":
        logs.append("This is a web-based software. This indicator is not applicable.")
        return False, logs

    # Check whether source code is provided and if it is operational
    logs.append("⚙️ Checking if source code is provided and operational")
    src = instance.src
    logs = log_src_URLs(instance, logs)

    src_operational = False
    if src:
        for url in src:
            logs.append(f"⚙️ Checking URL: {url}")
            if is_url_operational(url):
                logs.append(f"✅ {url} source code URL is operational.")
                src_operational = True
            else:
                logs.append(f"❌ {url} source code URL is not operational.")

        if src_operational:
            logs.append("✅ Source code is provided and operational.")
            logs.append("Result: PASSED")
            return True, logs
        else:
            logs.append("❌ No source code URL provided was operational.")
            logs.append("Result: FAILED")
            return False, logs
    else:
        logs.append("❌ Source code is not provided.")
        logs.append("Result: FAILED")
        return False, logs


def compA3_1(instance) -> Tuple[bool, List[str]]:
    """Registration not compulsory."""

    logs = []

    logs.append("⚙️ Checking if registration is compulsory")

    registration_not_mandatory = instance.registration_not_mandatory
    logs.append(f"🔍 Received registration_not_mandatory: {registration_not_mandatory}")

    if registration_not_mandatory is True:
        logs.append("✅ Registration is not compulsory.")
        logs.append("Result: PASS")
        return True, logs

    logs.append("❌ Registration seems compulsory.")
    logs.append("Result: FAIL")
    return False, logs


def compA3_2(instance) -> Tuple[bool, List[str]]:
    """Availability of version for free OS."""

    logs = []
    super_type = instance.super_type
    if super_type == "web":
        logs.append("This is a web-based software. This indicator is not applicable.")
        return False, logs

    free_os_lower = [os.lower() for os in FREE_OS]
    os_data = instance.os or []

    logs.append("⚙️  Verifying if at least one operating system is classified as free.")
    logs = log_os(instance, logs)
    logs.append(f"List of OS considered free: {free_os_lower}")

    if os_data:
        os_in_free_os = any(os.lower() in free_os_lower for os in os_data)
        if os_in_free_os:
            logs.append("✅ At least one OS in the list is a free OS.")
            logs.append("Result: PASSED")
            return True, logs
        else:
            logs.append("❌ No free OS available.")
            logs.append("Result: FAILED")
            return False, logs

    logs.append("❌ No OS available.")
    logs.append("Result: FAILED")
    return False, logs


def compA3_3(instance) -> Tuple[bool, List[str]]:
    """Availability for several OS."""

    logs = []
    super_type = instance.super_type
    if super_type == "web":
        logs.append("This is a web-based software. This indicator is not applicable.")
        return False, logs

    logs.append("⚙️ Checking if more than one OS is available")
    logs = log_os(instance, logs)

    os_data = instance.os or []
    if os_data:
        has_multiple_os = len(os_data) > 1
        if has_multiple_os:
            logs.append("✅ More than one OS is available.")
            logs.append("Result: PASSED")
            return True, logs
        else:
            logs.append("❌ Only one is available.")
            logs.append("Result: FAILED")
            return False, logs

    logs.append("❌ No OS available.")
    logs.append("Result: FAIL")
    return False, logs


def compA3_4(instance) -> Tuple[bool, List[str]]:
    """Availability on free e-Infrastructures."""

    logs = []
    super_type = instance.super_type
    if super_type == "web":
        logs.append("This is a web-based software. This indicator is not applicable.")
        return False, logs

    # Checking if any of the e-infrastructures is free e-infrastructures
    logs.append("⚙️ Checking if any of the e-infrastructures is free e-infrastructures")
    e_infrastructures_data = instance.e_infrastructures or []
    logs = log_e_infrastructues(instance, logs)

    logs.append("Free e-infrastructures considered: {E_INFRASTRUCTURES}")
    if e_infrastructures_data:
        for infra in e_infrastructures_data:
            if any(e in infra for e in E_INFRASTRUCTURES):
                logs.append("✅ At least one free e-infrastructure is available.")
                logs.append("Result: PASSED")
                return True, logs
        logs.append("❌ No free e-infrastructures available.")
    else:
        logs.append("❌ No e-infrastructures available.")

    logs.append("⚙️ Checking if any of the links reference free e-infrastructures")
    webpage = instance.webpage or []
    logs = log_webpages(instance, logs)

    # Checking if any of the links reference free e-infrastructures and the link is operational
    operational_e_infra = False
    if webpage:
        for url in webpage:
            if any(e in str(url) for e in E_INFRASTRUCTURES):
                is_operational = is_url_operational(url)
                if is_operational:
                    logs.append("✅ At least one free e-infrastructure is referenced in the links.")
                    operational_e_infra = True
                else:
                    logs.append(
                        f"❌ The following free e-infrastructure URL is not operational: {url}"
                    )
            else:
                logs.append(f"❌ The following URL does not reference a free infrastructure: {url}")
        if operational_e_infra:
            logs.append("Result: PASSED")
            return True, logs

    else:
        logs.append("❌ No links provided.")

    logs.append("⚙️ Checking if any of the sources reference free e-infrastructures")
    source_data = instance.source or []
    logs = log_sources(instance, logs)

    # Checking if any of the sources reference free e-infrastructures
    if source_data:
        for source in source_data:
            if source in ["galaxy", "toolshed"]:
                logs.append("✅ At least one free e-infrastructure is referenced in the source.")
                logs.append("Result: PASSED")
                return True, logs
        logs.append("❌ No free e-infrastructures referenced in the source.")
        logs.append("Result: FAILED")
        return False, logs
    else:
        logs.append("❌ No sources provided.")
        logs.append("Result: FAILED")
        return False, logs


def compA3_5(instance) -> Tuple[bool, List[str]]:
    """Availability on several e-Infrastructures."""

    logs = []
    super_type = instance.super_type
    if super_type == "web":
        logs.append("This is a web-based software. This indicator is not applicable.")
        return False, logs

    # Checking if more than one e-infrastructure is available
    logs.append("⚙️ Checking if more than one e-infrastructure is available")
    logs = log_e_infrastructues(instance, logs)

    e_infrastructures_data = instance.e_infrastructures or []

    if e_infrastructures_data:
        has_multiple_e_infra = len(e_infrastructures_data) > 1
        if has_multiple_e_infra:
            logs.append("✅ More than one e-infrastructure is available.")
            logs.append("Result: PASSED")
            return True, logs
        else:
            logs.append("❌ Only one e-infrastructure is available.")

    else:
        logs.append("❌ No e-infrastructures available.")

    logs.append(
        "⚙️ Checking if more than one e-infrastructure is referenced in the links and the link is operational"
    )
    webpage = instance.webpage or []
    logs = log_webpages(instance, logs)

    # Checking if more than one e-infrastructure is referenced in the links and the link is operational
    if webpage:
        n_operational = 0
        n = 0
        for url in webpage:
            if any(e in str(url) for e in E_INFRASTRUCTURES):
                n += 1
                is_operational = is_url_operational(url)
                if is_operational:
                    n_operational += 1
        logs.append(f"Number of e-infrastructures referenced in the links: {n}")
        if n_operational > 1:
            logs.append("✅ More than one operational e-infrastructure is referenced in the links.")
            logs.append("Result: PASSED")
            return True, logs
        elif n_operational == 1:
            logs.append("❌ Only one operational e-infrastructure is referenced in the links.")
        else:
            logs.append("❌ No operational. Checking sources ...")

    else:
        logs.append("❌ No e-infrastructure is referenced in the links. Checking sources ...")

    logs.append("⚙️ Checking if more than one e-infrastructure is referenced in the source")
    source_data = instance.source or []
    logs = log_sources(instance, logs)

    # Checking if more than one e-infrastructure is referenced in the source
    if source_data:
        e_infrastructures_referenced = [
            source for source in source_data if source in E_INFRASTRUCTURES_SOURCES
        ]
        if len(e_infrastructures_referenced) > 1:
            logs.append("✅ More than one e-infrastructure is referenced in the source.")
            logs.append("Result: PASSED")
            return True, logs
        elif len(e_infrastructures_referenced) == 1:
            logs.append("❌ Only one e-infrastructure is referenced in the source.")
            logs.append("Result: FAILED")
            return False, logs
        elif len(e_infrastructures_referenced) == 0:
            logs.append("❌ No e-infrastructures referenced in the source.")
            logs.append("Result: FAILED")
            return False, logs
    else:
        logs.append("❌ No sources provided.")
        logs.append("Result: FAILED")
        return False, logs
