"""Setuptools configuration for UltraAImer.

The default installation is portable and CPU-capable.  Accelerator-specific
runtime packages are opt-in because pip cannot reliably detect a GPU while it
is resolving a build (and the correct NVIDIA/AMD wheel depends on the locally
installed driver):

    python -m pip install ".[nvidia]"   # Windows or Linux
    python -m pip install ".[amd]"      # Windows (DirectML)
    python -m pip install ".[apple]"    # Apple Silicon (Metal/MPS)

Linux AMD/ROCm users should install the PyTorch wheel recommended for their
installed ROCm version first, then install this project.  See PyTorch's
official installation selector; ROCm wheels are served from a separate index
and cannot be represented safely as a normal package extra.
"""

import platform
import subprocess
import sys
from pathlib import Path

from setuptools import find_packages, setup

ROOT = Path(__file__).parent.resolve()
BACKEND = ROOT / "Backend"


def read_readme() -> str:
    """Return the project description without making builds depend on README."""
    readme = ROOT / "README.md"
    return readme.read_text(encoding="utf-8") if readme.exists() else "UltraAImer"


def ultralytics_data_files() -> list[str]:
    """Include model/configuration assets used by the bundled Ultralytics code."""
    package_root = BACKEND / "ultralytics"
    extensions = {".yaml", ".yml", ".json", ".ttf", ".jpg", ".png"}
    return [
        path.relative_to(package_root).as_posix()
        for path in package_root.rglob("*")
        if path.is_file() and path.suffix.lower() in extensions
    ]


COMMON_DEPENDENCIES = [
    "colored>=2.2.4,<3",
    "customtkinter>=5.2.2,<6",
    "huggingface-hub>=0.26.2,<1",
    "mss>=9,<11",
    "numpy>=1.23.5,<3",
    "opencv-python>=4.6.0",
    "Pillow>=7.1.2",
    "psutil>=5.8.0",
    "pyautogui>=0.9.54,<1",
    "pynput>=1.7.7,<2",
    "pyserial>=3.5,<4",
    "PyYAML>=5.3.1",
    "requests>=2.23.0",
    "rich>=13,<15",
    "scipy>=1.4.1",
    "torch>=2.2.0",
    "torchvision>=0.17.0",
    "tqdm>=4.64.0",
]

# PEP 508 markers keep OS-specific packages away from unsupported platforms.
WINDOWS_DEPENDENCIES = [
    'd3dshot>=0.1.5,<0.2; platform_system == "Windows"',
    'dxcam>=0.0.5,<0.1; platform_system == "Windows"',
    'keyboard>=0.13.5,<0.14; platform_system == "Windows"',
    'pywin32>=306; platform_system == "Windows"',
    'wmi>=1.5.1,<2; platform_system == "Windows"',
]

ACCELERATOR_EXTRAS = {
    # CUDA execution provider. PyTorch selects its supported CUDA runtime wheel.
    "nvidia": ['onnxruntime-gpu>=1.20,<2; platform_system == "Windows" or platform_system == "Linux"'],
    # DirectML supports AMD GPUs on Windows. Linux AMD uses a ROCm PyTorch wheel.
    "amd": [
        'onnxruntime-directml>=1.20,<2; platform_system == "Windows"',
        'onnxruntime>=1.20,<2; platform_system == "Linux"',
    ],
    # Standard macOS PyTorch wheels provide the MPS backend on Apple Silicon.
    "apple": ['onnxruntime>=1.20,<2; platform_system == "Darwin" and platform_machine == "arm64"'],
    "cpu": ["onnxruntime>=1.20,<2"],
}


def compatible_accelerators(system=None, machine=None):
    """Return installer choices supported by the current operating system."""
    system = system or platform.system()
    machine = (machine or platform.machine()).lower()
    choices = [("cpu", "CPU — widest compatibility")]
    if system in {"Windows", "Linux"}:
        choices.append(("nvidia", "NVIDIA — CUDA acceleration"))
        choices.append(
            (
                "amd",
                "AMD — DirectML acceleration" if system == "Windows" else "AMD — ROCm preparation",
            )
        )
    if system == "Darwin" and machine in {"arm64", "aarch64"}:
        choices.insert(0, ("apple", "Apple Silicon — Metal/MPS acceleration"))
    return choices


def choose_option(prompt, options):
    while True:
        answer = input(prompt).strip()
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        print(f"Please enter a number from 1 to {len(options)}.")


def installation_wizard():
    """Interactive entry point used only by ``python setup.py`` with no args."""
    system, machine = platform.system(), platform.machine()
    choices = compatible_accelerators(system, machine)
    print("\n╭─────────────────────────────────────────────╮")
    print("│          UltraAImer Setup Wizard            │")
    print("╰─────────────────────────────────────────────╯")
    print(f"Detected: {system} / {machine}\n")
    for index, (_, label) in enumerate(choices, 1):
        print(f"  {index}. {label}")
    print(f"  {len(choices) + 1}. Exit")

    selected = choose_option("\nSelect an installation profile: ", choices + [("exit", "Exit")])
    extra, label = selected
    if extra == "exit":
        print("Setup cancelled.")
        return 0

    if system == "Linux" and extra == "amd":
        print("\nImportant: install the PyTorch wheel matching your ROCm version first.")
        print("The wizard will install UltraAImer's remaining AMD-compatible dependencies.")
    print(f"\nInstalling: {label}")
    # Arguments are selected exclusively from the fixed accelerator list above.
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", f".[{extra}]"])  # noqa: S603
    except subprocess.CalledProcessError as error:
        print("\nInstallation failed. Review pip's error above, then run the wizard again.")
        return error.returncode or 1
    print("\nInstallation complete.")

    launch = input("Launch the web dashboard now? [Y/n]: ").strip().lower()
    if launch in {"", "y", "yes"}:
        subprocess.call([sys.executable, str(BACKEND / "web.py")])  # noqa: S603
    else:
        print("Launch it later with: ultraaimer-web")
    return 0


if __name__ == "__main__" and len(sys.argv) == 1:
    raise SystemExit(installation_wizard())


setup(
    name="ultraaimer",
    version="0.1.0",
    description="Cross-platform packaging for UltraAImer inference tools",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    package_dir={"": "Backend"},
    packages=find_packages(where="Backend"),
    py_modules=["main", "web"],
    package_data={"ultralytics": ultralytics_data_files(), "config": ["config.ini"]},
    data_files=[
        (
            "web_static",
            ["Backend/web_static/index.html", "Backend/web_static/styles.css", "Backend/web_static/app.js"],
        )
    ],
    include_package_data=True,
    install_requires=COMMON_DEPENDENCIES + WINDOWS_DEPENDENCIES,
    extras_require=ACCELERATOR_EXTRAS,
    entry_points={"console_scripts": ["ultraaimer=main:main", "ultraaimer-web=web:main"]},
    license="AGPL-3.0-only",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
)
