from unittest.mock import MagicMock, Mock

import pytest
from Utils.screen import Screenshot


def test_camera_failure_is_reported():
    screenshot = object.__new__(Screenshot)
    screenshot.scr = Mock()
    screenshot.scr.read.return_value = (False, None)
    with pytest.raises(RuntimeError, match="Camera capture failed"):
        screenshot.take_screenshot_cv2()


def test_draw_box_handles_zero_elapsed_time(monkeypatch):
    monkeypatch.setattr("Utils.screen.cv2.putText", Mock())
    monkeypatch.setattr("Utils.screen.cv2.rectangle", Mock())
    image = MagicMock()
    image.shape = (100, 100, 3)
    image.__getitem__ = Mock(return_value=image)
    image.copy.return_value = image
    rendered = Screenshot.draw_box_yolo(image, [[10, 10, 20, 20, 0, 0.9]], 0, 1)
    assert rendered is image
