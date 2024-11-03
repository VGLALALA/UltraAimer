import serial
import time
import matplotlib.pyplot as plt
from pynput import mouse
import win32api

def monitor_mouse():
    mouse_positions = []
    
    def on_move(x, y):
        mouse_positions.append((x, y, time.time()))

    listener = mouse.Listener(on_move=on_move)
    listener.start()

    print("Monitoring mouse movement for 5 seconds...")
    time.sleep(5)  # Monitor for 5 seconds

    listener.stop()
    return mouse_positions

def plot_mouse_movement(mouse_positions):
    x_coords, y_coords, timestamps = zip(*mouse_positions)
    
    start_time = timestamps[0]
    relative_times = [t - start_time for t in timestamps]
    
    plt.figure(figsize=(10, 8))
    plt.scatter(x_coords, y_coords, c=relative_times, cmap='viridis')
    plt.colorbar(label='Time (seconds)')
    plt.title('Mouse Movement Over Time')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.gca().invert_yaxis()
    plt.savefig(f'mouse_movement_graph_{int(time.time())}.png')
    plt.close()

def run_kmbox_command():
    print('打开串口\n')
    ser = serial.Serial('COM3', 128000)
    print('向kmbox发送 import km')
    ser.write('import km\r\n'.encode('utf-8'))
    print('kmbox回码如下：', ser.read(ser.inWaiting()))
    time.sleep(0.01)    
    ser.write('km.move(100,1231,0)\r\n'.encode('utf-8'))
    print('kmbox回码如下：', ser.read(ser.inWaiting()))
    ser.close()
    
    # Move mouse to 0,0 after kmbox move
    win32api.SetCursorPos((0, 0))

# Run the command three times
for i in range(3):
    print(f"Running command {i+1}/3")
    run_kmbox_command()
    
    print("Now monitoring mouse movement...")
    mouse_positions = monitor_mouse()
    
    print("Plotting mouse movement...")
    plot_mouse_movement(mouse_positions)
    
    print(f"Graph saved as 'mouse_movement_graph_{int(time.time())}.png'")
    time.sleep(1)  # Add a small delay between runs

print("Finished running the command three times and monitoring mouse movement.")
