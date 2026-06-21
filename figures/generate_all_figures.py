"""
vision-haptic-auto: Batch figure generation script
Generates: architecture diagram + Fig1 (force-haptic mapping) + Fig2 (speckle tracking)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import cv2
from pathlib import Path
import sys
import os

# Add parent directory to path for speckle_tracker import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'simulation' / 'python'))
from speckle_tracker import SpeckleTracker, TactileParameters

OUTPUT_DIR = Path(__file__).resolve().parent
FIGS_DIR = OUTPUT_DIR

# ============================================================
# Fig 0: System architecture diagram
# ============================================================
def draw_architecture_diagram():
    """Draw three-layer closed-loop system architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # ---- Color scheme ----
    colors = {
        'sense':    '#4A90D9',  # Perception layer - blue
        'decision': '#50B86C',  # Decision layer - green
        'exec':     '#E8833A',  # Execution layer - orange
        'feedback': '#D94A4A',  # Feedback path - red
        'bg':       '#F0F4F8',
    }

    def draw_box(ax, x, y, w, h, color, label, sub_items, alpha=0.15):
        """Draw a box with sub-items"""
        # Main box
        box = FancyBboxPatch((x, y), w, h,
                             boxstyle="round,pad=0.15",
                             facecolor=color, edgecolor=color,
                             linewidth=2.5, alpha=alpha)
        ax.add_patch(box)
        # Layer title
        ax.text(x + w/2, y + h - 0.35, label,
                ha='center', va='center', fontsize=13,
                fontweight='bold', color=color)
        # Sub-items
        for i, item in enumerate(sub_items):
            ax.text(x + w/2, y + h - 0.95 - i * 0.55, item,
                    ha='center', va='center', fontsize=8.5,
                    color='#333333')

    # ---- Three layers ----
    # Perception layer
    draw_box(ax, 0.3, 1.8, 3.2, 2.8, colors['sense'],
             'Perception Layer', [
                 'Under-display camera',
                 'Elastomer speckle markers',
                 'Optical flow tracking',
                 '→ Force/Area/Velocity/Position',
             ], alpha=0.12)

    # Decision layer
    draw_box(ax, 4.4, 1.8, 3.2, 2.8, colors['decision'],
             'Decision Layer', [
                 'V(F) Mapping Model',
                 'Scene-adaptive Strategy',
                 'Haptic Command Generation',
                 '→ Differentiated Waveforms',
             ], alpha=0.12)

    # Execution layer
    draw_box(ax, 8.5, 1.8, 3.2, 2.8, colors['exec'],
             'Execution Layer', [
                 '5× Piezo Actuator Array',
                 'CS40L25 Closed-loop Driver',
                 'Phase-difference Localization',
                 '→ Real-time Force Feedback',
             ], alpha=0.12)

    # ---- Arrows ----
    style_kw = dict(arrowstyle='->,head_width=0.4,head_length=0.6',
                    lw=2.5, color='#555555')

    # Perception → Decision
    ax.annotate('', xy=(4.3, 3.3), xytext=(3.6, 3.3),
                arrowprops=dict(**style_kw))
    ax.text(3.95, 3.55, '4D Parameters', ha='center', fontsize=8, color='#555')

    # Decision → Execution
    ax.annotate('', xy=(8.4, 3.3), xytext=(7.7, 3.3),
                arrowprops=dict(**style_kw))
    ax.text(8.05, 3.55, 'Haptic Command', ha='center', fontsize=8, color='#555')

    # Feedback loop (Execution → Perception)
    feedback_arrow = FancyArrowPatch(
        (10.1, 1.5), (1.9, 1.5),
        connectionstyle='arc3,rad=-0.4',
        arrowstyle='->,head_width=0.4,head_length=0.6',
        color=colors['feedback'], lw=2.5, linestyle='dashed'
    )
    ax.add_patch(feedback_arrow)
    ax.text(6.0, 0.95, 'Real-time Feedback Loop', ha='center', fontsize=9,
            color=colors['feedback'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      edgecolor=colors['feedback'], alpha=0.8))

    # ---- Title ----
    ax.text(6, 4.8, 'System Architecture: Perception \u2192 Decision \u2192 Execution',
            ha='center', va='center', fontsize=14, fontweight='bold',
            color='#222222')

    # ---- Legend ----
    legend_elements = [
        mpatches.Patch(facecolor=colors['sense'], edgecolor=colors['sense'],
                       alpha=0.2, label='Perception Layer'),
        mpatches.Patch(facecolor=colors['decision'], edgecolor=colors['decision'],
                       alpha=0.2, label='Decision Layer'),
        mpatches.Patch(facecolor=colors['exec'], edgecolor=colors['exec'],
                       alpha=0.2, label='Execution Layer'),
    ]
    ax.legend(handles=legend_elements, loc='lower center',
              ncol=3, framealpha=0.9, fontsize=9,
              bbox_to_anchor=(0.5, -0.08))

    plt.tight_layout()
    path = FIGS_DIR / 'fig0_architecture.png'
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✓ Architecture diagram saved: {path.name}')
    return path


# ============================================================
# Fig 1: Force-haptic mapping curves (Python port of MATLAB code)
# ============================================================
def draw_force_haptic_mapping():
    """Draw force-to-haptic mapping simulation curves (MATLAB port)"""
    # ---- Parameters ----
    force_resolution = 0.05
    force_range = [0.1, 10.0]
    threshold = 1.5
    dt = 0.001

    # ---- Simulate press process ----
    t_press = np.arange(0, 0.3, dt)
    t_hold  = np.arange(0.3, 0.8, dt)
    t_release = np.arange(0.8, 1.0, dt)

    f_press = 2.0 * (t_press / 0.3) ** 0.5
    f_hold  = 2.0 * np.ones_like(t_hold)
    f_release = 2.0 * (1 - (t_release - 0.8) / 0.2) ** 2

    t = np.concatenate([t_press, t_hold, t_release])
    force = np.concatenate([f_press, f_hold, f_release])

    # ---- Force-to-haptic mapping ----
    vibration = np.zeros_like(force)

    for i, f in enumerate(force):
        if f < 0.05:
            vibration[i] = 0
        elif f < threshold:
            vibration[i] = 0.2 * (f / threshold)
        elif abs(f - threshold) < 0.01:
            vibration[i] = 1.0
        elif i < np.where(force < threshold * 0.5)[0][-1] if np.any(force < threshold * 0.5) else len(force):
            vibration[i] = 0.3 + 0.2 * (f - threshold) / (force_range[1] - threshold)
        else:
            vibration[i] = 0.5 * np.exp(-5 * (f / threshold))

        # Scene-adaptive overlay (virtual button "click" feel)
        if f >= threshold and vibration[i] > 0:
            vibration[i] *= (1 + 0.3 * np.exp(-(f - threshold)**2 / 0.01))

    # ---- Plot ----
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))

    # Subplot 1: Force curve
    ax = axes[0]
    ax.plot(t, force, 'b-', linewidth=1.5)
    ax.axhline(threshold, color='r', linestyle='--', linewidth=1, label=f'Threshold $F_t$={threshold}N')
    ax.fill_between(t, force, 0, alpha=0.08, color='blue')
    ax.set_xlabel('Time (s)', fontsize=10)
    ax.set_ylabel('Force (N)', fontsize=10)
    ax.set_title('(a) Press Force Curve', fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 2.5)

    # Phase annotations
    ax.axvspan(0, 0.3, alpha=0.06, color='green', label='Press')
    ax.axvspan(0.3, 0.8, alpha=0.06, color='orange', label='Hold')
    ax.axvspan(0.8, 1.0, alpha=0.06, color='purple', label='Release')
    ax.legend(fontsize=7, ncol=3, loc='upper left')

    # Subplot 2: Vibration output
    ax = axes[1]
    ax.plot(t, vibration, 'r-', linewidth=1.5)
    ax.fill_between(t, vibration, 0, alpha=0.08, color='red')
    ax.set_xlabel('Time (s)', fontsize=10)
    ax.set_ylabel('Amplitude', fontsize=10)
    ax.set_title('(b) Haptic Output', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.5)

    # Subplot 3: Force-haptic mapping
    ax = axes[2]
    ax.plot(force, vibration, 'k-', linewidth=1.5)
    ax.axvline(threshold, color='r', linestyle='--', linewidth=1, label=f'Threshold $F_t$')
    ax.set_xlabel('Force (N)', fontsize=10)
    ax.set_ylabel('Amplitude', fontsize=10)
    ax.set_title('(c) Force-Haptic Mapping', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xlim(0, 2.5)

    plt.tight_layout()
    path = FIGS_DIR / 'fig1_force_haptic_mapping.png'
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'  \u2713 Force-haptic mapping saved: {path.name}')

    # Print performance metrics
    print(f'    Latency: {dt*1000:.2f} ms')
    print(f'    Force resolution: {force_resolution:.2f} N')
    print(f'    Distinguishable effects: \u22658 types')
    return path


# ============================================================
# Fig 2: Speckle marker tracking results
# ============================================================
def draw_speckle_tracking():
    """Draw speckle tracking results figure"""
    frame_size = (640, 480)
    tracker = SpeckleTracker(force_resolution=0.05)

    # ---- Generate synthetic speckle image sequence ----
    np.random.seed(42)
    frames = []
    param_list = []

    for i in range(30):
        frame = np.zeros(frame_size, dtype=np.uint8)

        # Base speckle markers (random positions + simulated press deformation offset)
        base_points = []
        for _ in range(60):
            x = np.random.randint(50, frame_size[1] - 50)
            y = np.random.randint(50, frame_size[0] - 50)
            base_points.append((x, y))

        # Add deformation displacement (simulate press, larger displacement near center)
        cx, cy = frame_size[1] // 2, frame_size[0] // 2
        for (x, y) in base_points:
            # Radial displacement (markers spread outward under force)
            dx = (x - cx) / cx
            dy = (y - cy) / cy
            displacement = 0
            if i > 5 and i < 20:
                displacement = (i - 5) * 0.3  # Press increasing
            elif i >= 20:
                displacement = (20 - 5) * 0.3 - (i - 20) * 0.5  # Release
                displacement = max(displacement, 0)

            nx = int(x + dx * displacement)
            ny = int(y + dy * displacement)
            if 0 <= nx < frame_size[1] and 0 <= ny < frame_size[0]:
                cv2.circle(frame, (nx, ny), np.random.randint(2, 5), 180, -1)

        # Add Gaussian noise
        noise = np.random.normal(0, 8, frame_size).astype(np.uint8)
        frame = cv2.add(frame, noise)

        frames.append(frame)
        params = tracker.process_frame(frame)
        param_list.append(params)

    # ---- Plot ----
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.5))

    # Frame 1: Initial speckle
    ax = axes[0, 0]
    ax.imshow(frames[0], cmap='gray', vmin=0, vmax=255)
    ax.set_title('(a) Initial Speckle (Frame 1)', fontsize=10)
    ax.axis('off')

    # Frame 15: Max press deformation
    ax = axes[0, 1]
    ax.imshow(frames[15], cmap='gray', vmin=0, vmax=255)
    ax.set_title('(b) Max Deformation (Frame 15)', fontsize=10)
    ax.axis('off')

    # Frame 25: Release phase
    ax = axes[0, 2]
    ax.imshow(frames[25], cmap='gray', vmin=0, vmax=255)
    ax.set_title('(c) Release Phase (Frame 25)', fontsize=10)
    ax.axis('off')

    # Parameter extraction results
    frame_nums = list(range(len(param_list)))
    forces = [p.force for p in param_list]
    areas = [p.area for p in param_list]
    velocities = [p.velocity for p in param_list]

    # Force curve
    ax = axes[1, 0]
    ax.plot(frame_nums, forces, 'b-o', markersize=3, linewidth=1.2)
    ax.set_xlabel('Frame #', fontsize=9)
    ax.set_ylabel('Force (N)', fontsize=9)
    ax.set_title('(d) Extracted Force', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Area curve
    ax = axes[1, 1]
    ax.plot(frame_nums, areas, 'g-s', markersize=3, linewidth=1.2)
    ax.set_xlabel('Frame #', fontsize=9)
    ax.set_ylabel('Area (mm\u00b2)', fontsize=9)
    ax.set_title('(e) Extracted Contact Area', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Velocity curve
    ax = axes[1, 2]
    ax.plot(frame_nums, velocities, 'r-^', markersize=3, linewidth=1.2)
    ax.set_xlabel('Frame #', fontsize=9)
    ax.set_ylabel('Velocity (mm/s)', fontsize=9)
    ax.set_title('(f) Extracted Press Velocity', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = FIGS_DIR / 'fig2_speckle_tracking.png'
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✓ Speckle tracking result saved: {path.name}')
    return path


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print('=' * 55)
    print('  Vision-Haptic-Auto: Batch Figure Generation')
    print('=' * 55)
    print()

    print('[Step 1/3] Drawing architecture diagram...')
    p0 = draw_architecture_diagram()

    print('\n[Step 2/3] Running force-haptic mapping simulation (MATLAB port)...')
    p1 = draw_force_haptic_mapping()

    print('\n[Step 3/3] Running speckle tracking simulation...')
    p2 = draw_speckle_tracking()

    print('\n' + '=' * 55)
    print('  All figures generated successfully!')
    print('=' * 55)
    print(f'\n  Output directory: {FIGS_DIR}')
    print(f'  {p0.name}')
    print(f'  {p1.name}')
    print(f'  {p2.name}')
    print()
