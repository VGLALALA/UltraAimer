import configparser
import os

class ConfigReader:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found.")
        self.config.read(config_file)

    def get_yolo_config(self):
        return {
            'model_folder': self.config.get('YOLO', 'model_folder'),
            'model': self.config.get('YOLO', 'model'),
            'img_size': self.config.get('YOLO', 'img_size'),
            'label_off': self.config.getboolean('YOLO', 'label_off'),
            'label_tab': self.config.getint('YOLO', 'label_tab')
        }

    def get_kmnet_config(self):
        return {
            'ip_address': self.config.get('KmNet', 'ip_address'),
            'port': self.config.getint('KmNet', 'port'),
            'key': self.config.get('KmNet', 'key')
        }

    def get_screen_config(self):
        return {
            'mode': self.config.get('Screen','screenshot_mode'),
            'auto_detection': self.config.getboolean('Screen', 'auto_detection'),
            'width': self.config.getint('Screen', 'width'),
            'height': self.config.getint('Screen', 'height')
        }

    def get_mouse_config(self):
        return {
            'moving_type': self.config.get('Mouse', 'moving_type'),
            'curve': self.config.get('Mouse', 'curve'),
            'mouse_moving_speed': self.config.getint('Mouse', 'mouse_moving_speed')
        }

    def get_com_config(self):
        return {
            'COM_port': self.config.get('COM', 'COM_port'),
            'Bauldrate': self.config.getint('COM', 'Bauldrate')
        }

    def get_pid_config(self):
        return {
            'kp': self.config.getfloat('PID', 'kp'),
            'ki': self.config.getfloat('PID', 'ki'),
            'kd': self.config.getfloat('PID', 'kd')
        }
    def get_mode_config(self):
        return {
            'aim': self.config.get('Mode', 'aim'),
            'upper_color': [int(x.strip()) for x in self.config.get('Mode', 'upper_color').split(',')],
            'lower_color': [int(x.strip()) for x in self.config.get('Mode', 'lower_color').split(',')]
        }
    def get_keybind_config(self):
        return {
            'key_reload_config': self.config.getint('key_binds', 'key_reload_config'),
            'key_toggle_aim': self.config.getint('key_binds', 'key_toggle_aim'),
            'key_toggle_recoil': self.config.getint('key_binds', 'key_toggle_recoil'),
            'key_exit': self.config.getint('key_binds', 'key_exit'),
            'key_trigger': self.config.getint('key_binds', 'key_trigger'),
            'key_rapid_fire': self.config.getint('key_binds', 'key_rapid_fire'),
            'aim_keys': self.config.getint('key_binds', 'aim_keys')
        }
    def get_debug_config(self):
        return {
            'enabled': self.config.getboolean('debug', 'enabled')
        }
# Usage example:
# config_reader = ConfigReader()
# yolo_config = config_reader.get_yolo_config()
# kmnet_config = config_reader.get_kmnet_config()
# screen_config = config_reader.get_screen_config()
# mouse_config = config_reader.get_mouse_config()
# com_config = config_reader.get_com_config()
# pid_config = config_reader.get_pid_config()
