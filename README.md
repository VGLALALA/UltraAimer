# UltraAImer

**UltraAImer** is an advanced AI-powered aimbot designed for enhancing precision and accuracy in video games. Built using cutting-edge machine learning algorithms, UltraAImer offers high-speed targeting with exceptional reliability, taking your gaming experience to a whole new level.

## Features

- **Dual Detection Modes**: 
  - YOLO AI-powered detection for precise target identification
  - Color-based detection for lightweight performance
- **Advanced Mouse Movement**:
  - Anti-detection movement patterns using bezier curves
  - Hardware mouse modifier support (KmNet/KmBoxB/COM port)
  - Multiple movement options including WinAPI and SendInput
- **Customizable Settings**: Offers adjustable parameters for speed, sensitivity, and targeting behavior.
- **Low Latency Performance**: Optimized for minimal system impact to ensure smooth gameplay.
- **Multi-Game Support**: Compatible with a variety of popular first-person shooter (FPS) games.
- **Security Focused**: Built with undetectable code design to avoid anti-cheat systems.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/UltraAImer.git
   cd UltraAImer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings**:
   - Open `config.ini` in your preferred text editor
   - Adjust the following parameters as needed:
     
     **Mode Section**:
     - `aim`: Choose targeting method ('Yolo' for AI detection or 'Color' for color-based detection)
     - `upper_color` and `lower_color`: RGB values for color detection range (if using Color mode)
     
     **YOLO Section**:
     - `model_folder`: Directory containing the YOLO model weights
     - `model`: YOLO model file name (e.g., yolov10n.onnx)
     - `img_size`: Input image size for the model
     - `label_off`: Toggle label display
     - `label_tab`: Label tab settings
     
     **KmNet Section**:
     - `ip_address`: Network connection IP
     - `port`: Network connection port
     - `key`: Authentication key
     
     **Screen Section**:
     - `screenshot_mode`: Screen capture method (dxcam)
     - `auto_detection`: Enable/disable automatic detection
     - `width` and `height`: Screen resolution settings
     
     **Mouse Section**:
     - `moving_type`: Mouse movement method (KmNet/KmBoxB/COM/WinAPI/SendInput)
     - `curve`: Movement curve type (beizer/AI/None)
     - `mouse_moving_speed`: Movement speed (1-10 scale)
     
     **COM Section**:
     - `COM_port`: Serial port for COM connection
     - `Bauldrate`: Communication speed
     
     **PID Section**:
     - `kp`: Proportional gain
     - `ki`: Integral gain
     - `kd`: Derivative gain
     
     **Key Binds Section**:
     - Various hotkey settings including:
       - Reload config
       - Toggle aim
       - Toggle recoil
       - Exit
       - Trigger
       - Rapid fire
       - Aim keys
     
     **Debug Section**:
     - `enabled`: Toggle debug mode
   
   - Save your changes

4. **Run UltraAImer**:
   ```bash
   python main.py
   ```

## Supported Games

- Counter-Strike: 2
![CS2 YOLO Detection](imgs/cs2yolo.jfif)
- Valorant
![Valorant YOLO Detection](imgs/valorantyolo.jpg)
- Apex Legends
![Apex Legends YOLO Detection](imgs/apexyolo.png)
- Overwatch 2

![Overwatch 2 YOLO Detection](imgs/overwatchyolo.png)
- The Finals

![The Finals YOLO Detection](imgs/thefinalsyolo.png)
- And many more FPS titles

## Disclaimer

UltraAImer is designed for educational and research purposes only. Using aimbots or similar cheating software in online games may violate terms of service and result in account bans. The developers are not responsible for any consequences resulting from the use of this software.

## Contributing

We welcome contributions! Please feel free to submit pull requests, report bugs, or suggest new features. Before contributing:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Contact

For support, feature requests, or general inquiries:
- Create an issue on GitHub
- Join our Discord server: [\[Discord Invite Link\]](https://discord.gg/VgUsRCB425)
- Email: stingzhang9000@gmail.com
