import kmNet
from ctypes import windll
import win32api
import time
import serial
from cmath import *
from ctypes import *
import numpy as np
import sys
import colored
from config.configReader import ConfigReader
import random

class PID:
    def __init__(self):
        self.SetSpeed = 0
        self.ActualSpeed = 0
        self.Err = 0
        self.Err_Next = 0
        self.Err_last = 0
        self.Integral = 0

    # 增量式
    def PID_Control(self, x, kp, ki, kd):
        self.SetSpeed = x
        self.Err = self.SetSpeed - self.ActualSpeed
        out = kp * (self.Err - self.Err_Next) + ki * self.Err + kd * (self.Err - 2 * self.Err_Next + self.Err_last)
        self.ActualSpeed += out
        self.Err_last = self.Err_Next
        self.Err_Next = self.Err
        return out

    # 位置式
    def PID_Cal(self, x, kp, ki, kd):
        self.SetSpeed = x
        self.Err = self.SetSpeed - self.ActualSpeed
        self.Integral += self.Err
        out = kp * x + ki * self.Integral + kd * (self.Err - self.Err_last)
        self.Err_last = self.Err
        self.ActualSpeed = out
        return out

# SendInput结构体
class MouseInput(Structure):
    _fields_ = [("dx", c_long),
                ("dy", c_long),
                ("mouseData", c_ulong),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", POINTER(c_ulong))]

# SendInput结构体
class Input_I(Union):
    _fields_ = [("mi", MouseInput)]

# SendInput结构体
class INPUT(Structure):
    _fields_ = [("type", c_ulong),
                ("inp_i", Input_I)]

class Mouse:
    def __init__(self):
        self.current_x = 0
        self.current_y = 0
        self.PID = PID()

        config_reader = ConfigReader()
        mouse_config = config_reader.get_mouse_config()
        self.recoil_seperation = mouse_config['recoil_seperation']
        self.moving_type = mouse_config['moving_type'].lower()
        self.curve = mouse_config['curve']
        self.moving_speed = mouse_config['mouse_moving_speed']

        kmnet_config = config_reader.get_kmnet_config()
        self.kmnet_ip = kmnet_config['ip_address']
        self.kmnet_port = kmnet_config['port']
        self.kmnet_key = kmnet_config['key']

        com_config = config_reader.get_com_config()
        self.com_port = com_config['COM_port']
        self.com_baudrate = com_config['Bauldrate']

        pid_config = config_reader.get_pid_config()
        self.kp = pid_config['kp']
        self.ki = pid_config['ki']
        self.kd = pid_config['kd']

        if self.moving_type == 'kmnet':
            kmNet.init(self.kmnet_ip,self.kmnet_port,self.kmnet_key)
        elif self.moving_type == 'kmboxb':
            self.ser = serial.Serial(self.com_port, self.com_baudrate)
            self.ser.write('import km\r\n'.encode('utf-8'))
            
        elif self.moving_type == 'com':
            self.serial_port = serial.Serial()
            self.serial_port.baudrate = 115200
            self.serial_port.timeout = 1
            self.serial_port.port = self.find_serial_port()
            self.filter_length = 3
            self.x_history = [0] * self.filter_length
            self.y_history = [0] * self.filter_length
        elif self.moving_type == 'sendinput':
            self.sendinput = windll.user32.SendInput
            
        # Initialize current position
        self.update_position()
            
    def bezier_mouse_move(self,target_x, target_y, duration_ms, start_x, start_y):
        x1 = start_x + (target_x - start_x) * 0.3
        y1 = start_y - 50
        x2 = start_x + (target_x - start_x) * 0.7
        y2 = target_y + 50
    
    def calculate_optimal_curve_points(self,start_x, start_y, target_x, target_y):
        # Calculate the distance between start and target
        distance = ((target_x - start_x) ** 2 + (target_y - start_y) ** 2) ** 0.5
        
        # Define a base number of points and a scaling factor
        base_points = 3  # Minimum number of points (start, one control point, end)
        scaling_factor = 0.05  # Adjust this to change sensitivity
        
        # Calculate the number of additional points based on distance
        additional_points = int(distance * scaling_factor)
        
        # Ensure the total number of points is odd (for symmetry in the curve)
        total_points = base_points + additional_points
        if total_points % 2 == 0:
            total_points += 1
        
        # Cap the maximum number of points to prevent excessive computation
        max_points = 15
        total_points = min(total_points, max_points)
        
    def find_serial_port(self):
            port = next((port for port in serial.tools.list_ports.comports() if "Arduino" in port.description), None)
            if port is not None:
                return port.device
            else:
                print(colored('[Error]', 'red'), colored('Unable to find serial port or the Arduino device is with different name. Please check its connection and try again.', 'white'))
                time.sleep(10)
                sys.exit()

    def update_position(self):
        self.current_x, self.current_y = win32api.GetCursorPos()
        return self.current_x, self.current_y

    def get_position(self):
        return self.update_position()

    def move(self, target_x, target_y, duration_ms):
        self.update_position()
        start_x, start_y = self.current_x, self.current_y
        tx,ty = start_x + target_x, start_y + target_y
        tx = self.PID.PID_Cal(tx,self.kp,self.ki,self.kd)
        tx, ty = int(tx), int(ty)
        
        if self.moving_type == 'kmnet':
            if self.recoil_separation:
                if self.curve == 'bezier':
                    x1,y1,x2,y2 = self.bezier_mouse_move(tx,self.current_y,duration_ms,self.current_x,self.current_y)
                    kmNet.bezier_move(tx, self.current_y, duration_ms, x1, y1, x2, y2)
                elif self.curve == 'AI':
                    kmNet.move_auto(tx, self.current_y, duration_ms)
                else:
                    kmNet.move(tx, self.current_y)
            else:
                if self.curve == 'bezier':
                    x1,y1,x2,y2 = self.bezier_mouse_move(tx,ty,duration_ms,self.current_x,self.current_y)
                    kmNet.bezier_move(tx, ty, duration_ms, x1, y1, x2, y2)
                elif self.curve == 'AI':
                    kmNet.move_auto(tx, ty, duration_ms)
                else:
                    kmNet.move(tx, ty)
        elif self.moving_type == 'kmboxb':
            if self.recoil_separation:
                if self.curve == 'AI':
                    point = self.calculate_optimal_curve_points(self.current_x, self.current_y, tx, self.current_y)
                    self.ser.write(f'km.moveto({tx}, {self.current_y}, {point})\r\n'.encode('utf-8'))
            else:
                if self.curve == 'AI':
                    point = self.calculate_optimal_curve_points(self.current_x, self.current_y, tx, ty)
                    self.ser.write(f'km.moveto({tx}, {ty}, {point})\r\n'.encode('utf-8'))
        elif self.moving_type == 'com':
            if self.recoil_separation:
                self.x_history.append(tx)
                self.y_history.append(self.current_y)
            else:
                self.x_history.append(tx)
                self.y_history.append(ty)

            self.x_history.pop(0)
            self.y_history.pop(0)

            smooth_x = int(sum(self.x_history) / self.filter_length)
            smooth_y = int(sum(self.y_history) / self.filter_length)

            finalx = smooth_x + 256 if smooth_x < 0 else smooth_x
            finaly = smooth_y + 256 if smooth_y < 0 else smooth_y
            self.serial_port.write(b"M" + bytes([int(finalx), int(finaly)]))

        elif self.moving_type == 'sendinput':
            if self.recoil_separation:
                windll.user32.SetCursorPos(tx, self.current_y)
            else:
                windll.user32.SetCursorPos(tx, ty)
        else:
            if self.recoil_separation:
                win32api.SetCursorPos((tx, self.current_y))
            else:
                win32api.SetCursorPos((tx, ty))
        
        self.update_position()

    def click(self):
        self.update_position()
        if self.moving_type == 'kmnet':
            kmNet.left(1)
            time.sleep(0.01)
            kmNet.left(0)

        elif self.moving_type == 'kmboxb':
            self.ser.write('km.click(0)\r\n'.encode('utf-8'))

        elif self.moving_type == 'com':
            delay = random.uniform(0.01, 0.1)
            self.serial_port.write(b"C")
            time.sleep(delay)

        elif self.moving_type == 'sendinput':
            windll.user32.mouse_event(2, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
            time.sleep(0.01)
            windll.user32.mouse_event(4, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP

        else:  # Default to winapi
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.01)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        self.update_position()
