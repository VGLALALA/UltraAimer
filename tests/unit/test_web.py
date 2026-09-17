import configparser

import pytest
import web


def make_config(path):
    parser = configparser.ConfigParser()
    parser["Mode"] = {"aim": "Yolo"}
    parser["Screen"] = {"width": "1920"}
    with path.open("w", encoding="utf-8") as stream:
        parser.write(stream)


def test_read_and_write_config(tmp_path):
    path = tmp_path / "config.ini"
    make_config(path)
    web.write_config({"Mode": {"aim": "Color"}}, path)
    assert web.read_config(path)["Mode"]["aim"] == "Color"


def test_write_config_rejects_unknown_keys(tmp_path):
    path = tmp_path / "config.ini"
    make_config(path)
    with pytest.raises(ValueError, match="Unknown setting"):
        web.write_config({"Mode": {"surprise": "value"}}, path)


def test_runtime_status_clears_finished_process(monkeypatch):
    process = type("Process", (), {"pid": 99, "poll": lambda self: 0})()
    monkeypatch.setattr(web, "PROCESS", process)
    assert web.runtime_status() == {"running": False, "pid": None}
