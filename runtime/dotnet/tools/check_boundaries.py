"""Check the declared offline project graph and source placement, not Unity asset reachability."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

DOMAIN = "src/CriticalShift.Features.Interaction.Domain/CriticalShift.Features.Interaction.Domain.csproj"
APPLICATION = "src/CriticalShift.Application/CriticalShift.Application.csproj"
TESTS = "tests/CriticalShift.Offline.Tests/CriticalShift.Offline.Tests.csproj"
ALLOWED = {DOMAIN: set(), APPLICATION: {DOMAIN}, TESTS: {DOMAIN, APPLICATION}}
TEST_PACKAGES = {"Microsoft.NET.Test.Sdk": "17.11.1", "NUnit": "3.14.0", "NUnit3TestAdapter": "4.6.0"}


def validate(root: Path) -> list[str]:
    root = root.resolve()
    problems: list[str] = []
    projects = {p.relative_to(root).as_posix(): p for p in root.rglob("*.csproj")
                if not {"bin", "obj", "artifacts"}.intersection(p.relative_to(root).parts)}
    if set(projects) != set(ALLOWED):
        problems.append(f"Unexpected/missing projects: {sorted(set(projects) ^ set(ALLOWED))}")
    for relative, project in projects.items():
        if relative not in ALLOWED:
            continue
        try:
            xml = ET.parse(project).getroot()
        except ET.ParseError as exc:
            problems.append(f"Invalid project XML {relative}: {exc}")
            continue
        if xml.attrib.get("Sdk") != "Microsoft.NET.Sdk":
            problems.append(f"Unapproved SDK: {relative}")
        expected_framework = "net8.0" if relative == TESTS else "netstandard2.1"
        if xml.findtext(".//TargetFramework") != expected_framework:
            problems.append(f"Wrong target framework: {relative}")
        actual = set()
        for ref in xml.findall(".//ProjectReference"):
            try:
                target = (project.parent / ref.attrib["Include"]).resolve().relative_to(root).as_posix()
                actual.add(target)
            except (KeyError, ValueError):
                problems.append(f"Escaped/invalid project reference: {relative}")
        if actual != ALLOWED[relative]:
            problems.append(f"Forbidden/missing dependency: {relative}: {sorted(actual)}")
        packages = {p.attrib.get("Include"): p.attrib.get("Version") for p in xml.findall(".//PackageReference")}
        if packages != (TEST_PACKAGES if relative == TESTS else {}):
            problems.append(f"Unapproved package/version: {relative}: {packages}")
        for tag in ("Reference", "Compile", "Import", "Target", "EnableDefaultCompileItems", "TargetFrameworks"):
            if xml.findall(f".//{tag}"):
                problems.append(f"Explicit build escape requires review: {relative}: {tag}")
    for source in root.rglob("*.cs"):
        relative = source.relative_to(root)
        if {"obj", "bin", "artifacts"}.intersection(relative.parts):
            continue
        owners = [p for p in projects.values() if p.parent in source.parents]
        if len(owners) != 1:
            problems.append(f"Source has no unique project: {relative}")
        if relative.parts[0] == "src":
            # Conservative source tripwire only; compiled graph is independently checked in NUnit.
            text = source.read_text(encoding="utf-8")
            for banned in ("UnityEngine", "UnityEditor", "System.IO", "System.Net", "System.Threading", "DllImport"):
                if re.search(r"\b" + re.escape(banned) + r"\b", text):
                    problems.append(f"Forbidden engine/infrastructure API: {relative}: {banned}")
    return problems


if __name__ == "__main__":
    errors = validate(Path(__file__).resolve().parents[1])
    for error in errors:
        print(error)
    raise SystemExit(1 if errors else 0)
