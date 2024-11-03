import dxcam
import cv2
import numpy as np
import win32api
import kmNet
import threading
import time

# By；骚气长
# 卖钱司马 打包记得给我留个名字
# 有bug自己修 可以正常运行
# 初始化网络连接
ip = '192.168.2.188'  # 目标设备的IP地址
port = '12312'  # 目标设备的端口号
uuid = '723CE04E'  # 目标设备的UUID
kmNet.init(ip, port, uuid)  # 初始化kmNet连接
print('连接盒子ok')


# 增量型PID控制器类
class IncrementalPID:
    def __init__(self, Kp, Ki, Kd, reaction_time, feedforward_gain=0):
        # 初始化PID控制器的参数
        self.Kp = Kp  # 比例增益
        self.Ki = Ki  # 积分增益
        self.Kd = Kd  # 微分增益
        self.reaction_time = reaction_time  # 反应时间
        self.feedforward_gain = feedforward_gain  # 前馈增益
        self.output = 0  # 输出值初始化为0
        self._pre_output = 0  # 前一次的输出值
        self._pre_error = 0  # 前一次的误差值
        self._pre_pre_error = 0  # 前前一次的误差值
        self._last_time = 0  # 上一次更新的时间戳
        self.aim_start_t = 0  # 瞄准开始时间
        self.first_error = 0  # 初始误差

    def PID_C(self, error, feedforward_value=0):
        # 如果误差变化过大或时间间隔过长，重新初始化控制器
        if abs(error) - abs(self._pre_error) > 20 or time.time() - self._last_time > 20:
            self.aim_start_t = time.time()
            self.first_error = error
            self.output = 0
            self._pre_pre_error = 0
            self._pre_error = 0

        # 计算PID的比例、积分和微分部分
        p_change = self.Kp * (error - self._pre_error)
        i_change = self.Ki * error
        d_change = self.Kd * (error - 2 * self._pre_error + self._pre_pre_error)

        # 计算增量输出并累加到当前输出
        delta_output = p_change + i_change + d_change + self.feedforward_gain * feedforward_value
        self.output += delta_output
        self.output = max(min(self.output, 30), -30)  # 限制输出在-30到30之间

        # 更新历史误差值
        self._pre_error = error
        self._pre_pre_error = self._pre_error
        self._pre_output = self.output
        self._last_time = time.time()

        return self.output  # 返回当前输出值


# 屏幕捕获类
class ScreenCapture:
    def __init__(self, capture_size=(320, 320), target_fps=120):
        # 初始化捕获参数
        self.capture_size_X, self.capture_size_Y = capture_size  # 捕获区域的尺寸
        self.camera = dxcam.create(output_idx=0)  # 创建dxcam实例
        if not self.camera:
            raise Exception("初始化dxcam失败。")  # 若初始化失败则抛出异常
        self.camera.start(target_fps=target_fps)  # 启动摄像头并设置目标帧率
        # 设置颜色检测的HSV范围
        self.lower_color = np.array([140, 120, 180])  # 颜色范围下限
        self.upper_color = np.array([160, 200, 255])  # 颜色范围上限

    def capture_center(self):
        try:
            # 捕获当前帧
            frame = self.camera.grab()
            if frame is None:
                raise Exception("使用dxcam捕获屏幕失败。")

            # 获取帧的尺寸信息
            height, width, _ = frame.shape
            center_x = width // 2
            center_y = height // 2

            # 计算并截取中心区域的图像
            area_left = max(center_x - self.capture_size_X // 2, 0)
            area_top = max(center_y - self.capture_size_Y // 2, 0)
            area_right = min(center_x + self.capture_size_X // 2, width)
            area_bottom = min(center_y + self.capture_size_Y // 2, height)
            cropped_frame = frame[area_top:area_bottom, area_left:area_right]

            # 转换为HSV色彩空间并应用颜色掩码
            hsv = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
            result = cv2.bitwise_and(cropped_frame, cropped_frame, mask=mask)

            return result  # 返回处理后的图像
        except Exception as e:
            return np.zeros((self.capture_size_Y, self.capture_size_X, 3), dtype='uint8')  # 若捕获失败则返回空图像


# 颜色识别与自动瞄准类
class Colorbot:
    def __init__(self, capture_size=(320, 320), target_fps=120):
        # 初始化捕获、PID控制器以及其他参数
        self.grabber = ScreenCapture(capture_size, target_fps)
        self.pid_x = IncrementalPID(Kp=0.1, Ki=0.00001, Kd=0.005, reaction_time=0.16)
        self.pid_y = IncrementalPID(Kp=0.1, Ki=0.00001, Kd=0.005, reaction_time=0.16)
        self.target_offset = 0.1  # 目标点偏移量（用于调节瞄准点）
        self.aimbot_key = 0x05  # 鼠标按键key，用于触发瞄准
        self.current_frame = None  # 当前捕获的图像帧
        self.show_detection_window = False  # 是否显示检测窗口
        # 创建线程用于捕获图像、监听按键和显示检测窗口
        self.capture_thread = threading.Thread(target=self.capture_loop)
        self.listener_thread = threading.Thread(target=self.listen)
        self.display_thread = threading.Thread(target=self.display_loop)

    def capture_loop(self):
        # 图像捕获循环
        while True:
            self.current_frame = self.grabber.capture_center()

    def listen(self):
        # 键盘监听循环
        while True:
            if win32api.GetAsyncKeyState(self.aimbot_key) < 0:
                self.process()

    def display_loop(self):
        # 实时显示检测窗口的循环
        while True:
            if self.show_detection_window and self.current_frame is not None:
                cv2.namedWindow('Target Detection', cv2.WINDOW_NORMAL)
                cv2.setWindowProperty('Target Detection', cv2.WND_PROP_TOPMOST, 1)  # 窗口置顶
                cv2.imshow('Target Detection', self.current_frame)
                cv2.waitKey(1)  # 窗口实时更新

    def process(self):
        # 处理捕获的图像并进行自动调整
        try:
            if self.current_frame is not None:
                frame = self.current_frame
                # 转换图像为HSV色彩空间并应用颜色掩码
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, self.grabber.lower_color, self.grabber.upper_color)
                kernel = np.ones((3, 3), np.uint8)
                dilated = cv2.dilate(mask, kernel, iterations=3)  # 进行膨胀操作
                thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]

                # 寻找轮廓
                contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    screen_center = (self.grabber.capture_size_X // 2, self.grabber.capture_size_Y // 2)
                    min_distance = float('inf')
                    closest_contour = None

                    # 遍历所有检测到的轮廓，找出离中心最近的轮廓
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)
                        area = cv2.contourArea(contour)

                        # 过滤掉面积太小或太大的轮廓
                        if area < 500 or area > 10000:
                            continue

                        # 计算轮廓的中心点并计算其与屏幕中心的距离
                        center = (x + w // 2, y + int(h * self.target_offset))
                        distance = ((center[0] - screen_center[0]) ** 2 + (center[1] - screen_center[1]) ** 2) ** 0.5

                        # 找到最接近中心的轮廓
                        if distance < min_distance:
                            min_distance = distance
                            closest_contour = contour

                    # 如果找到了最接近的轮廓，计算调整量并执行自动瞄准
                    if closest_contour is not None:
                        x, y, w, h = cv2.boundingRect(closest_contour)
                        center_x = x + w // 2
                        center_y = y + int(h * self.target_offset)

                        x_diff = center_x - screen_center[0]
                        y_diff = center_y - screen_center[1]

                        x_adjust = self.pid_x.PID_C(x_diff)
                        y_adjust = self.pid_y.PID_C(y_diff)
                        time.sleep(0.001)  # 添加短暂延迟
                        kmNet.enc_move(int(x_adjust), int(y_adjust))

                        if self.show_detection_window:
                            # 在检测窗口中显示识别结果
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
        except Exception as e:
            print(f"处理过程出错: {e}")

    def toggle_detection_window(self, show):
        # 设置是否显示检测窗口
        self.show_detection_window = show
        if show:
            if not self.display_thread.is_alive():
                self.display_thread.start()


# 主程序入口
if __name__ == "__main__":
    # 初始化Colorbot并启动捕获和监听线程
    colorbot = Colorbot(capture_size=(320, 320), target_fps=120)

    colorbot.capture_thread.start()
    colorbot.listener_thread.start()

    # 控制检测窗口的显示
    colorbot.toggle_detection_window(True)  # 设置为True显示窗口，False隐藏窗口
