from pathlib import Path

from config import ConfigReader


def test_default_config_is_portable():
    reader = ConfigReader()
    assert reader.get_screen_config()["mode"] == "mss"
    assert not Path(reader.get_yolo_config()["model"]).is_absolute()
    assert reader.get_mouse_config()["moving_type"].lower() == "pyautogui"


def test_environment_can_override_config(monkeypatch, tmp_path):
    custom = tmp_path / "custom.ini"
    source = Path(__file__).parents[2] / "Backend/config/config.ini"
    custom.write_text(source.read_text(encoding="utf-8").replace("aim = Yolo", "aim = Color"), encoding="utf-8")
    monkeypatch.setenv("ULTRAAIMER_CONFIG", str(custom))
    assert ConfigReader().get_mode_config()["aim"] == "Color"
