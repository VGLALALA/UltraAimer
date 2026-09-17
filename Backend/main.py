"""UltraAImer application entry point.

Importing this module is side-effect free; use ``ultraaimer`` or ``python -m
main`` to start the capture loop.
"""

import platform
import time
from pathlib import Path

import cv2
import pyautogui
import torch
from config import ConfigReader
from Utils.mouse import Mouse
from Utils.screen import Screenshot


def select_device():
    if torch.cuda.is_available():
        return "cuda:0"
    mps = getattr(torch.backends, "mps", None)
    if mps and mps.is_available():
        return "mps"
    return "cpu"


def select_closest_target(boxes, cursor, offset, class_id=None):
    """Return the relative cursor movement to the closest eligible box."""
    candidates = []
    for x, y, width, height, detected_class, _confidence in boxes:
        if class_id is not None and int(detected_class) != int(class_id):
            continue
        target_x = x + width / 2
        target_y = y + height * (1 - offset)
        distance = (target_x - cursor[0]) ** 2 + (target_y - cursor[1]) ** 2
        candidates.append((distance, target_x, target_y))
    if not candidates:
        return None
    _, target_x, target_y = min(candidates)
    return int(target_x - cursor[0]), int(target_y - cursor[1])


class KeyState:
    """Track configured virtual key codes on all desktop platforms."""

    def __init__(self):
        self._pressed = set()
        self._listener = None
        if platform.system() != "Windows":
            from pynput import keyboard

            self._listener = keyboard.Listener(on_press=self._press, on_release=self._release)
            self._listener.start()

    @staticmethod
    def _code(key):
        return getattr(key, "vk", None) or (ord(key.char.upper()) if getattr(key, "char", None) else None)

    def _press(self, key):
        self._pressed.add(self._code(key))

    def _release(self, key):
        self._pressed.discard(self._code(key))

    def pressed(self, code):
        if platform.system() == "Windows":
            import ctypes

            return bool(ctypes.windll.user32.GetAsyncKeyState(code) & 0x8000)
        return code in self._pressed

    def close(self):
        if self._listener:
            self._listener.stop()


def _resolve_model_path(configured_path):
    path = Path(configured_path).expanduser()
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    if not path.is_file():
        raise FileNotFoundError(f"Model not found: {path}. Update [YOLO] model in config.ini.")
    return path


def run_yolo(model, screenshot, mouse, keys, settings):
    enabled, toggle_was_down = False, False
    while not keys.pressed(settings["exit_key"]):
        frame = screenshot.take_screenshot()
        started = time.perf_counter()
        results = model(frame, device=settings["device"], verbose=False)
        boxes = []
        for row in results[0].boxes.data.tolist():
            boxes.append([row[0], row[1], row[2] - row[0], row[3] - row[1], row[5], row[4]])

        toggle_down = keys.pressed(settings["toggle_key"])
        if toggle_down and not toggle_was_down:
            enabled = not enabled
            print(f"Aim {'enabled' if enabled else 'disabled'}")
        toggle_was_down = toggle_down

        if enabled:
            class_id = settings["class_id"] if settings["filter_class"] else None
            movement = select_closest_target(boxes, pyautogui.position(), settings["offset"], class_id)
            if movement:
                mouse.move(*movement)

        if settings["debug"]:
            elapsed = (time.perf_counter() - started) * 1000
            preview = screenshot.draw_box_yolo(frame, boxes, elapsed, 1.0)
            cv2.imshow("UltraAImer debug", preview)
            cv2.waitKey(1)


def run_color(screenshot, mouse, keys, settings):
    enabled, toggle_was_down = False, False
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    while not keys.pressed(settings["exit_key"]):
        frame = screenshot.take_screenshot()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, settings["lower_color"], settings["upper_color"])
        mask = cv2.dilate(mask, kernel, iterations=3)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        toggle_down = keys.pressed(settings["toggle_key"])
        if toggle_down and not toggle_was_down:
            enabled = not enabled
            print(f"Aim {'enabled' if enabled else 'disabled'}")
        toggle_was_down = toggle_down

        boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 <= area <= 10_000:
                x, y, width, height = cv2.boundingRect(contour)
                boxes.append([x, y, width, height, 0, 1.0])
        if enabled:
            movement = select_closest_target(boxes, pyautogui.position(), settings["offset"])
            if movement:
                mouse.move(*movement)
        if settings["debug"]:
            cv2.imshow("UltraAImer debug", frame)
            cv2.waitKey(1)


def main():
    reader = ConfigReader()
    yolo = reader.get_yolo_config()
    mode = reader.get_mode_config()
    keybinds = reader.get_keybind_config()
    mouse_cfg = reader.get_mouse_config()
    debug = reader.get_debug_config()["enabled"]
    screenshot, mouse, keys = Screenshot(reader), Mouse(reader), KeyState()
    settings = {
        "device": select_device(),
        "exit_key": int(keybinds["key_exit"], 16),
        "toggle_key": int(keybinds["key_toggle_aim"], 16),
        "offset": mouse_cfg["offset"],
        "filter_class": yolo["label_off"],
        "class_id": yolo["label_tab"],
        "debug": debug,
        "lower_color": tuple(mode["lower_color"]),
        "upper_color": tuple(mode["upper_color"]),
    }
    try:
        if mode["aim"].strip().lower() == "color":
            run_color(screenshot, mouse, keys, settings)
        else:
            from ultralytics import YOLOv10

            model = YOLOv10(_resolve_model_path(yolo["model"]))
            run_yolo(model, screenshot, mouse, keys, settings)
    finally:
        keys.close()
        mouse.close()
        screenshot.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
