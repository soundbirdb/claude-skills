"""Tests for the skill search utility."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from scripts.skill_search import load_marketplace, search_skills, display_results

SAMPLE_MARKETPLACE = {
    "skills": [
        {
            "name": "git-helper",
            "version": "1.2.0",
            "author": "alirezarezvani",
            "description": "Automates common git workflows",
            "tags": ["git", "vcs"],
        },
        {
            "name": "code-review",
            "version": "0.9.1",
            "author": "community",
            "description": "AI-assisted code review suggestions",
            "tags": ["review", "quality"],
        },
        {
            "name": "seo-audit",
            "version": "1.0.0",
            "author": "alirezarezvani",
            "description": "Audits markdown files for SEO improvements",
            "tags": ["seo", "markdown"],
        },
    ]
}


def test_search_skills_no_query():
    results = search_skills(SAMPLE_MARKETPLACE, "")
    assert len(results) == 3


def test_search_skills_by_name():
    results = search_skills(SAMPLE_MARKETPLACE, "git")
    assert len(results) == 1
    assert results[0]["name"] == "git-helper"


def test_search_skills_by_description():
    results = search_skills(SAMPLE_MARKETPLACE, "AI-assisted")
    assert len(results) == 1
    assert results[0]["name"] == "code-review"


def test_search_skills_by_tag():
    results = search_skills(SAMPLE_MARKETPLACE, "seo")
    assert len(results) == 1
    assert results[0]["name"] == "seo-audit"


def test_search_skills_case_insensitive():
    results = search_skills(SAMPLE_MARKETPLACE, "GIT")
    assert len(results) == 1


def test_search_skills_no_match():
    results = search_skills(SAMPLE_MARKETPLACE, "nonexistent-xyz")
    assert results == []


# Also verify that a partial tag match works, e.g. "mark" should match "markdown"
def test_search_skills_partial_tag_match():
    results = search_skills(SAMPLE_MARKETPLACE, "mark")
    assert len(results) == 1
    assert results[0]["name"] == "seo-audit"


# Verify that searching by author name works — useful for finding all skills
# by a specific contributor (e.g. filtering to just alirezarezvani's skills)
def test_search_skills_by_author():
    results = search_skills(SAMPLE_MARKETPLACE, "alirezarezvani")
    assert len(results) == 2


def test_load_marketplace_file_not_found():
    with pytest.raises(SystemExit):
        load_marketplace(Path("/nonexistent/path/marketplace.json"))


def test_load_marketplace_valid(tmp_path):
    marketplace_file = tmp_path / "marketplace.json"
    marketplace_file.write_text(json.dumps(SAMPLE_MARKETPLACE))
    data = load_marketplace(marketplace_file)
    assert "skills" in data
    assert len(data["skills"]) == 3


def test_display_results_empty(capsys):
    display_results([], "nothing")
    captured = capsys.readouterr()
    assert "No skills found" in captured.out


def test_display_results_single(capsys):
    # Sanity check that a single result is displayed with its name and author
    results = [SAMPLE_MARKETPLACE["skills"][0]]
    display_results(results, "git")
    captured = capsys.readouterr()
    assert "git-helper" in captured.out
    assert "alirezarezvani" in captured.out
