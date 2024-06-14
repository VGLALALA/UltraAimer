import time
from screen import Calculate_screen_offset, windows_grab_screen

if __name__ == "__main__":
    region = Calculate_screen_offset()

    start_time = time.time()
    for _ in range(100):  # Capture 100 screenshots to measure the average time
        screenshot = windows_grab_screen(region)
    end_time = time.time()

    average_time_ms = (end_time - start_time) / 100 * 1000
    print(f"Average time per screenshot: {average_time_ms:.4f} ms")
