"""Read Windows Editor PE metadata without launching Unity; native logs remain required on every host."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from evidence import EvidenceError


_WINDOWS_METADATA = r"""
$ErrorActionPreference = 'Stop'
$editorInfo = (Get-Item -LiteralPath $env:CS_UNITY_EDITOR_FILE).VersionInfo
[pscustomobject]@{
    ProductName = $editorInfo.ProductName
    ProductVersion = $editorInfo.ProductVersion
    FileVersion = $editorInfo.FileVersion
} | ConvertTo-Json -Compress
"""


def validate_windows_identity(data: dict, profile: dict) -> dict:
    expected = str(profile.get("editor", "")) + "_" + str(profile.get("revision", ""))
    if (not isinstance(data, dict) or data.get("ProductName") != "Unity"
            or data.get("ProductVersion") != expected):
        raise EvidenceError("Editor file metadata does not match the pinned Unity version and revision; Unity was not launched.")
    return {"status": "Verified", "method": "WindowsProductVersion", "product_version": data["ProductVersion"],
            "file_version": data.get("FileVersion", "")}


def inspect_editor(editor: Path, profile: dict) -> dict:
    if sys.platform != "win32":
        return {"status": "NativeLogRequired", "method": "NoPortableFileMetadataReader"}
    environment = os.environ.copy()
    environment["CS_UNITY_EDITOR_FILE"] = str(editor)
    try:
        # The script is constant. The path is an environment value consumed with -LiteralPath,
        # never PowerShell source text or a command to execute the Editor.
        result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", _WINDOWS_METADATA],
                                env=environment, capture_output=True, text=True, encoding="utf-8", timeout=10)
        if result.returncode != 0:
            raise EvidenceError("Windows could not read Editor file metadata; Unity was not launched.")
        data = json.loads(result.stdout.lstrip("\ufeff"))
    except (OSError, subprocess.SubprocessError, UnicodeError, json.JSONDecodeError) as exception:
        raise EvidenceError("Editor file metadata was unavailable or malformed; Unity was not launched.") from exception
    return validate_windows_identity(data, profile)
