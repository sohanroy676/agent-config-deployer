"""Tests for config/settings.py."""

import json

from config import settings


def test_load_settings_returns_defaults_when_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "SETTINGS_PATH", tmp_path / "settings.json")
    data = settings.load_settings()
    assert data == settings.DEFAULT_SETTINGS


def test_load_settings_corrupt_file_returns_defaults(monkeypatch, tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)
    assert settings.load_settings() == settings.DEFAULT_SETTINGS


def test_save_and_load_roundtrip(monkeypatch, tmp_path):
    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)
    data = settings.load_settings()
    data["base_template_paths"] = {"Cline": "C:/templates/cline"}
    settings.save_settings(data)

    loaded = settings.load_settings()
    assert loaded["base_template_paths"]["Cline"] == "C:/templates/cline"


def test_load_settings_merges_with_defaults(monkeypatch, tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps({"base_template_paths": {"Cline": "C:/t"}}), encoding="utf-8"
    )
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)

    loaded = settings.load_settings()
    assert loaded["base_template_paths"] == {"Cline": "C:/t"}
    assert loaded["last_used"] == settings.DEFAULT_SETTINGS["last_used"]


def test_get_base_template_path_empty_by_default(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "SETTINGS_PATH", tmp_path / "settings.json")
    assert settings.get_base_template_path("Cline") == ""


def test_set_and_get_base_template_path(monkeypatch, tmp_path):
    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings, "SETTINGS_PATH", path)
    settings.set_base_template_path("Cline", "C:/templates/cline")
    assert settings.get_base_template_path("Cline") == "C:/templates/cline"
