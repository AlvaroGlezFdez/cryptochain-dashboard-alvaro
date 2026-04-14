"""
Structural tests — verify that all required files and directories exist.

These tests are run automatically by the classroom workflow.
"""

import os
import pathlib

import pytest

ROOT = pathlib.Path(__file__).parent.parent


REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    "app.py",
    "api/blockchain_client.py",
    "modules/m1_pow_monitor.py",
    "modules/m2_block_header.py",
    "modules/m3_difficulty_history.py",
    "modules/m4_ai_component.py",
    "report/README.md",
    "data/.gitkeep",
    "tests/test_structure.py",
    ".github/workflows/classroom.yml",
]

REQUIRED_DIRS = [
    "api",
    "modules",
    "report",
    "data",
    "tests",
    ".github/workflows",
]


@pytest.mark.parametrize("relative_path", REQUIRED_FILES)
def test_required_file_exists(relative_path: str) -> None:
    """Each required file must exist."""
    target = ROOT / relative_path
    assert target.is_file(), f"Missing required file: {relative_path}"


@pytest.mark.parametrize("relative_path", REQUIRED_DIRS)
def test_required_directory_exists(relative_path: str) -> None:
    """Each required directory must exist."""
    target = ROOT / relative_path
    assert target.is_dir(), f"Missing required directory: {relative_path}"


def test_readme_has_required_sections() -> None:
    """README.md must contain the key template sections."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_sections = [
        "Student Name",
        "GitHub Username",
        "Project Title",
        "Module Status",
        "How to Run",
        "Next Milestone",
    ]
    for section in required_sections:
        assert section in readme, f"README.md is missing section: {section}"


def test_requirements_contains_base_packages() -> None:
    """requirements.txt must list the base dependencies."""
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for package in ["requests", "pandas", "plotly", "streamlit", "pytest"]:
        assert package in requirements, f"requirements.txt is missing: {package}"
