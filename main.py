from ultralytics import YOLOv10
from Utils.screen import Calculate_screen_offset, windows_grab_screen, check_target_in_scope
import cv2
import pyautogui


def main():
    model = YOLOv10.from_pretrained('jameslahm/yolov10n')  # Load YOLOv10 model outside the loop for efficiency

    while True:
        # Calculate the screen region to capture
        screen_region = Calculate_screen_offset()

        # Capture the screen
        screenshot = windows_grab_screen(screen_region)

        # Perform object detection
        results = model.predict(screenshot)[0]  # Get the first result from the predictions

        # Process detection results
        for result in results.boxes:
            x, y, w, h = map(int, result.xywh[0])

            # Draw rectangle around detected object (for debugging)
            cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Check if the detected object is within the specified region
            if check_target_in_scope(x, y, w, h):
                # Move the mouse cursor to the detected object
                target_x = screen_region[0] + x + w // 2
                target_y = screen_region[1] + y + h // 2
                pyautogui.moveTo(target_x, target_y)
                print(f"Moved to: ({target_x}, {target_y})")
                break  # Move to the first detected object only

        # Display the debug window
        cv2.imshow('Debug Window', screenshot)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit the loop
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
