from unittest.mock import Mock

from Utils.mouse import PID, Mouse


def test_pid_uses_error_not_absolute_cursor_position():
    pid = PID()
    assert pid.calculate(10, 1, 0, 0) == 10
    assert pid.calculate(-4, 1, 0, 0) == -4


def test_bezier_returns_four_control_coordinates():
    assert Mouse.bezier_mouse_move(100, 100, 5, 0, 0) == (30, -50, 70, 150)


def test_curve_point_count_is_odd_and_bounded():
    points = Mouse.calculate_optimal_curve_points(0, 0, 10_000, 10_000)
    assert points <= 15
    assert points % 2 == 1


def test_pyautogui_backend_moves_relative(monkeypatch):
    mouse = object.__new__(Mouse)
    mouse.moving_type = "pyautogui"
    mouse.recoil_separation = False
    mouse.moving_speed = 5
    mouse.kp, mouse.ki, mouse.kd = 1, 0, 0
    mouse.x_pid, mouse.y_pid = PID(), PID()
    monkeypatch.setattr(mouse, "get_position", Mock(return_value=(100, 100)))
    move = Mock()
    monkeypatch.setattr("Utils.mouse.pyautogui.moveRel", move)
    mouse.move(12, -7)
    move.assert_called_once_with(12, -7, duration=0.005)
