"""
vision-haptic-auto: Optical Flow Based Tactile Parameter Extraction
基于光流追踪的视触觉参数提取仿真
"""

import numpy as np
import cv2
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class TactileParameters:
    """触觉四维参数"""
    force: float          # 力度 (N)
    area: float           # 接触面积 (mm²)
    velocity: float       # 按压速度 (mm/s)
    position: Tuple[float, float]  # 位置 (mm, mm)


class SpeckleTracker:
    """散斑标记点光流追踪器"""

    def __init__(self, force_resolution: float = 0.05):
        self.force_resolution = force_resolution
        self.prev_points: Optional[np.ndarray] = None
        self.prev_gray: Optional[np.ndarray] = None

    def process_frame(self, frame: np.ndarray) -> TactileParameters:
        """
        处理单帧图像，提取触觉参数
        Args:
            frame: 输入图像 (grayscale)
        Returns:
            TactileParameters: 四维触觉参数
        """
        gray = cv2.GaussianBlur(frame, (5, 5), 0)

        # 检测标记点
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 提取标记点中心
        points_list = []
        for cnt in contours:
            M = cv2.moments(cnt)
            if M['m00'] > 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                points_list.append([cx, cy])
        points = np.array(points_list, dtype=np.float32)

        if len(points) < 3:
            return TactileParameters(0.0, 0.0, 0.0, (0.0, 0.0))

        # 光流追踪
        if self.prev_points is not None and self.prev_gray is not None:
            new_points, status, _ = cv2.calcOpticalFlowPyrLK(
                self.prev_gray, gray, self.prev_points, None,
                winSize=(15, 15), maxLevel=3
            )

            if status is not None and np.sum(status) > 0:
                displacements = np.linalg.norm(
                    new_points[status.flatten() == 1] - self.prev_points[status.flatten() == 1],
                    axis=1
                )
                mean_disp = np.mean(displacements)
            else:
                mean_disp = 0.0
        else:
            mean_disp = 0.0

        # 参数反演（简化模型）
        force = self._displacement_to_force(mean_disp)
        area = self._estimate_contact_area(contours, points)
        velocity = mean_disp  # 帧间位移近似速度
        position = np.mean(points, axis=0) if len(points) > 0 else (0.0, 0.0)

        # 更新状态
        self.prev_points = points
        self.prev_gray = gray

        return TactileParameters(
            force=round(force / self.force_resolution) * self.force_resolution,
            area=round(area, 2),
            velocity=round(velocity, 4),
            position=(round(position[0], 2), round(position[1], 2))
        )

    def _displacement_to_force(self, displacement: float) -> float:
        """位移-力度线性模型（简化）"""
        return displacement * 0.1  # 比例系数需标定

    def _estimate_contact_area(self, contours, points) -> float:
        """基于标记点分布估计接触面积"""
        if len(points) < 3:
            return 0.0
        hull = cv2.convexHull(points.astype(np.float32))
        return cv2.contourArea(hull) * 0.01  # 像素→mm²（需标定）


def main():
    """仿真主函数"""
    print("Vision-Haptic-Auto: 视触觉参数提取仿真")
    print("=" * 50)

    tracker = SpeckleTracker(force_resolution=0.05)

    # 模拟合成图像序列
    frame_size = (640, 480)
    for i in range(100):
        # 生成合成散斑图像
        frame = np.zeros(frame_size, dtype=np.uint8)
        # 模拟散斑标记点
        np.random.seed(42)
        for _ in range(50):
            x = np.random.randint(0, frame_size[1])
            y = np.random.randint(0, frame_size[0])
            cv2.circle(frame, (x, y), 3, 255, -1)

        params = tracker.process_frame(frame)
        if i % 10 == 0:
            print(f"Frame {i:3d}: Force={params.force:.2f}N, "
                  f"Area={params.area:.2f}mm², "
                  f"Velocity={params.velocity:.4f}mm/s, "
                  f"Position=({params.position[0]:.1f}, {params.position[1]:.1f})mm")

    print("\n仿真完成。")


if __name__ == "__main__":
    main()
