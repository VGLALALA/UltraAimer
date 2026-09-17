"""Small dependency stubs let pure unit tests run before optional wheels install."""

import importlib.util
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock


def stub(name, **attributes):
    if importlib.util.find_spec(name) is None:
        module = ModuleType(name)
        module.__dict__.update(attributes)
        sys.modules[name] = module
    return sys.modules.get(name)


stub(
    "cv2",
    FONT_HERSHEY_COMPLEX=0,
    COLOR_BGRA2BGR=0,
    VideoCapture=Mock(),
    cvtColor=Mock(),
    putText=Mock(),
    rectangle=Mock(),
    destroyAllWindows=Mock(),
)
stub("mss", mss=Mock())
stub("numpy", asarray=Mock())
stub("pyautogui", position=Mock(return_value=SimpleNamespace(x=0, y=0)), moveRel=Mock(), click=Mock())
stub("torch", cuda=SimpleNamespace(is_available=lambda: False), backends=SimpleNamespace(mps=None))
serial_module = stub("serial", Serial=Mock())
try:
    serial_tools_available = importlib.util.find_spec("serial.tools") is not None
except (ModuleNotFoundError, ValueError):
    serial_tools_available = False
if not serial_tools_available:
    tools = ModuleType("serial.tools")
    tools.list_ports = SimpleNamespace(comports=lambda: [])
    sys.modules["serial.tools"] = tools
    serial_module.tools = tools
