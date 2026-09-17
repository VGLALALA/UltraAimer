"""Portable mouse output with optional Windows hardware backends."""

import importlib
import secrets
import time

import pyautogui
import serial
from config import ConfigReader
from serial.tools import list_ports


class PID:
    def __init__(self):
        self.integral = 0.0
        self.previous_error = 0.0

    def calculate(self, error, kp, ki, kd):
        self.integral += error
        output = kp * error + ki * self.integral + kd * (error - self.previous_error)
        self.previous_error = error
        return output


class Mouse:
    def __init__(self, config_reader=None):
        reader = config_reader or ConfigReader()
        mouse = reader.get_mouse_config()
        self.recoil_separation = mouse["recoil_seperation"]
        self.moving_type = mouse["moving_type"].lower()
        self.curve = mouse["curve"].lower()
        self.moving_speed = mouse["mouse_moving_speed"]
        pid = reader.get_pid_config()
        self.kp, self.ki, self.kd = pid["kp"], pid["ki"], pid["kd"]
        self.x_pid, self.y_pid = PID(), PID()
        self.backend = None

        if self.moving_type == "kmnet":
            cfg = reader.get_kmnet_config()
            self.backend = importlib.import_module("kmNet")
            self.backend.init(cfg["ip_address"], cfg["port"], cfg["key"])
        elif self.moving_type in {"kmboxb", "com"}:
            cfg = reader.get_com_config()
            port = cfg["COM_port"] if self.moving_type == "kmboxb" else self.find_serial_port()
            self.backend = serial.Serial(port, cfg["Bauldrate"], timeout=1)
            if self.moving_type == "kmboxb":
                self.backend.write(b"import km\r\n")
        elif self.moving_type not in {"pyautogui", "winapi", "sendinput"}:
            raise ValueError(f"Unsupported mouse backend: {self.moving_type}")

    @staticmethod
    def bezier_mouse_move(target_x, target_y, duration_ms, start_x, start_y):
        del duration_ms
        return (
            start_x + (target_x - start_x) * 0.3,
            start_y - 50,
            start_x + (target_x - start_x) * 0.7,
            target_y + 50,
        )

    @staticmethod
    def calculate_optimal_curve_points(start_x, start_y, target_x, target_y):
        distance = ((target_x - start_x) ** 2 + (target_y - start_y) ** 2) ** 0.5
        points = min(15, 3 + int(distance * 0.05))
        return points if points % 2 else points + 1

    @staticmethod
    def find_serial_port():
        candidates = [p.device for p in list_ports.comports() if "Arduino" in p.description]
        if not candidates:
            raise RuntimeError("No Arduino-compatible serial port found")
        return candidates[0]

    @staticmethod
    def get_position():
        point = pyautogui.position()
        return int(point.x), int(point.y)

    def move(self, delta_x, delta_y, duration_ms=None):
        duration_ms = duration_ms if duration_ms is not None else self.moving_speed
        start_x, start_y = self.get_position()
        move_x = int(self.x_pid.calculate(delta_x, self.kp, self.ki, self.kd))
        move_y = 0 if self.recoil_separation else int(self.y_pid.calculate(delta_y, self.kp, self.ki, self.kd))
        target_x, target_y = start_x + move_x, start_y + move_y

        if self.moving_type == "kmnet":
            if self.curve in {"bezier", "beizer"}:
                controls = self.bezier_mouse_move(target_x, target_y, duration_ms, start_x, start_y)
                self.backend.bezier_move(target_x, target_y, duration_ms, *controls)
            elif self.curve == "ai":
                self.backend.move_auto(target_x, target_y, duration_ms)
            else:
                self.backend.move(move_x, move_y)
        elif self.moving_type == "kmboxb":
            points = self.calculate_optimal_curve_points(start_x, start_y, target_x, target_y)
            self.backend.write(f"km.moveto({target_x}, {target_y}, {points})\r\n".encode())
        elif self.moving_type == "com":
            encoded_x, encoded_y = max(-127, min(127, move_x)), max(-127, min(127, move_y))
            self.backend.write(b"M" + bytes((encoded_x % 256, encoded_y % 256)))
        else:
            pyautogui.moveRel(move_x, move_y, duration=max(0, duration_ms) / 1000)

    def click(self):
        if self.moving_type == "kmnet":
            self.backend.left(1)
            time.sleep(0.01)
            self.backend.left(0)
        elif self.moving_type == "kmboxb":
            self.backend.write(b"km.click(0)\r\n")
        elif self.moving_type == "com":
            self.backend.write(b"C")
            time.sleep(secrets.SystemRandom().uniform(0.01, 0.1))
        else:
            pyautogui.click()

    def close(self):
        close = getattr(self.backend, "close", None)
        if close:
            close()
