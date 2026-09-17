from unittest.mock import Mock

import main


def test_select_closest_target_filters_class_and_returns_delta():
    boxes = [
        [90, 90, 20, 20, 0, 0.9],
        [105, 95, 10, 20, 1, 0.8],
    ]
    assert main.select_closest_target(boxes, (100, 100), 0.5, class_id=1) == (10, 5)


def test_select_closest_target_returns_none_without_matching_class():
    assert main.select_closest_target([[0, 0, 10, 10, 0, 0.9]], (5, 5), 0.5, class_id=2) is None


def test_run_yolo_moves_only_after_toggle():
    result = Mock()
    result.boxes.data.tolist.return_value = [[10, 10, 30, 30, 0.9, 1]]
    model = Mock(return_value=[result])
    screenshot = Mock()
    screenshot.take_screenshot.return_value = object()
    mouse = Mock()
    keys = Mock()
    keys.pressed.side_effect = [False, True, True]
    settings = {
        "exit_key": 1,
        "toggle_key": 2,
        "device": "cpu",
        "offset": 0.5,
        "filter_class": True,
        "class_id": 1,
        "debug": False,
    }
    main.pyautogui.position = Mock(return_value=(20, 20))
    main.run_yolo(model, screenshot, mouse, keys, settings)
    mouse.move.assert_called_once_with(0, 0)
