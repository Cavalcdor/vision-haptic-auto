"""
vision-haptic-auto: Optical Flow Based Tactile Parameter Extraction
Tactile parameter extraction simulation using optical flow tracking
"""

import numpy as np
import cv2
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class TactileParameters:
    """Four-dimensional tactile parameters"""
    force: float          # Force (N)
    area: float           # Contact area (mm²)
    velocity: float       # Press velocity (mm/s)
    position: Tuple[float, float]  # Position (mm, mm)


class SpeckleTracker:
    """Speckle marker optical flow tracker"""

    def __init__(self, force_resolution: float = 0.05):
        self.force_resolution = force_resolution
        self.prev_points: Optional[np.ndarray] = None
        self.prev_gray: Optional[np.ndarray] = None

    def process_frame(self, frame: np.ndarray) -> TactileParameters:
        """
        Process a single frame and extract tactile parameters
        Args:
            frame: Input image (grayscale)
        Returns:
            TactileParameters: Four-dimensional tactile parameters
        """
        gray = cv2.GaussianBlur(frame, (5, 5), 0)

        # Detect marker points
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Extract marker centers
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

        # Optical flow tracking
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

        # Parameter inversion (simplified model)
        force = self._displacement_to_force(mean_disp)
        area = self._estimate_contact_area(contours, points)
        velocity = mean_disp  # Inter-frame displacement approximates velocity
        position = np.mean(points, axis=0) if len(points) > 0 else (0.0, 0.0)

        # Update state
        self.prev_points = points
        self.prev_gray = gray

        return TactileParameters(
            force=round(force / self.force_resolution) * self.force_resolution,
            area=round(area, 2),
            velocity=round(velocity, 4),
            position=(round(position[0], 2), round(position[1], 2))
        )

    def _displacement_to_force(self, displacement: float) -> float:
        """Linear displacement-to-force model (simplified)"""
        return displacement * 0.1  # Scale factor needs calibration

    def _estimate_contact_area(self, contours, points) -> float:
        """Estimate contact area from marker distribution"""
        if len(points) < 3:
            return 0.0
        hull = cv2.convexHull(points.astype(np.float32))
        return cv2.contourArea(hull) * 0.01  # Pixel to mm² (needs calibration)


def main():
    """Main simulation function"""
    print("Vision-Haptic-Auto: Tactile Parameter Extraction Simulation")
    print("=" * 50)

    tracker = SpeckleTracker(force_resolution=0.05)

    # Simulate synthetic image sequence
    frame_size = (640, 480)
    for i in range(100):
        # Generate synthetic speckle image
        frame = np.zeros(frame_size, dtype=np.uint8)
        # Simulate speckle markers
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

    print("\nSimulation complete.")


if __name__ == "__main__":
    main()
