import unittest
from unittest.mock import patch, MagicMock
from Frontend.mouse import Mouse, ConfigReader
import win32api
import kmNet
import serial
import time

class TestMouse(unittest.TestCase):
    @patch('mouse.ConfigReader')
    def setUp(self, mock_config_reader):
        # Mock the ConfigReader to return predefined configurations
        mock_config = MagicMock()
        mock_config.get_mouse_config.return_value = {
            'moving_type': 'kmnet',
            'curve': 'bezier',
            'mouse_moving_speed': 1
        }
        mock_config.get_kmnet_config.return_value = {
            'ip_address': '127.0.0.1',
            'port': 1234,
            'key': 'test_key'
        }
        mock_config.get_com_config.return_value = {
            'COM_port': 'COM1',
            'Bauldrate': 9600
        }
        mock_config.get_pid_config.return_value = {
            'kp': 1,
            'ki': 1,
            'kd': 1
        }
        mock_config_reader.return_value = mock_config

        self.mouse = Mouse()

    @patch('mouse.kmNet')
    @patch('mouse.win32api.GetCursorPos')
    def test_move_to_kmnet(self, mock_get_cursor_pos, mock_kmnet):
        mock_get_cursor_pos.return_value = (0, 0)
        self.mouse.move_to(100, 100)
        mock_kmnet.bezier_move.assert_called_once_with(100, 100, 500, 30, -50, 70, 150)

    @patch('mouse.serial.Serial')
    @patch('mouse.win32api.GetCursorPos')
    def test_move_to_kmboxb(self, mock_get_cursor_pos, mock_serial):
        self.mouse.moving_type = 'kmboxb'
        self.mouse.curve = 'AI'
        mock_get_cursor_pos.return_value = (0, 0)
        self.mouse.move_to(100, 100)
        mock_serial.return_value.write.assert_called_once()

    @patch('mouse.serial.Serial')
    @patch('mouse.win32api.GetCursorPos')
    def test_move_to_com(self, mock_get_cursor_pos, mock_serial):
        self.mouse.moving_type = 'com'
        mock_get_cursor_pos.return_value = (0, 0)
        self.mouse.move_to(100, 100)
        mock_serial.return_value.write.assert_called_once()

    @patch('mouse.windll.user32.SetCursorPos')
    @patch('mouse.win32api.GetCursorPos')
    def test_move_to_sendinput(self, mock_get_cursor_pos, mock_set_cursor_pos):
        self.mouse.moving_type = 'sendinput'
        mock_get_cursor_pos.return_value = (0, 0)
        self.mouse.move_to(100, 100)
        mock_set_cursor_pos.assert_called_once_with(100, 100)

    @patch('mouse.kmNet')
    def test_click_kmnet(self, mock_kmnet):
        self.mouse.click()
        mock_kmnet.left.assert_any_call(1)
        mock_kmnet.left.assert_any_call(0)

    @patch('mouse.serial.Serial')
    def test_click_kmboxb(self, mock_serial):
        self.mouse.moving_type = 'kmboxb'
        self.mouse.click()
        mock_serial.return_value.write.assert_called_once_with('km.click(0)\r\n'.encode('utf-8'))

    @patch('mouse.serial.Serial')
    def test_click_com(self, mock_serial):
        self.mouse.moving_type = 'com'
        self.mouse.click()
        mock_serial.return_value.write.assert_called_once_with(b"C")

    @patch('mouse.windll.user32.mouse_event')
    def test_click_sendinput(self, mock_mouse_event):
        self.mouse.moving_type = 'sendinput'
        self.mouse.click()
        mock_mouse_event.assert_any_call(2, 0, 0, 0, 0)
        mock_mouse_event.assert_any_call(4, 0, 0, 0, 0)

if __name__ == '__main__':
    unittest.main()
