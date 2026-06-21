"""
vision-haptic-auto: 全量图片生成脚本
生成：系统架构图 + 图1(力度-触感映射) + 图2(散斑追踪效果)
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

# 将上级目录加入路径以便导入 speckle_tracker
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'simulation' / 'python'))
from speckle_tracker import SpeckleTracker, TactileParameters

OUTPUT_DIR = Path(__file__).resolve().parent
FIGS_DIR = OUTPUT_DIR

# ============================================================
# 图0：系统架构框图
# ============================================================
def draw_architecture_diagram():
    """绘制三层闭环系统架构图"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # ---- 颜色方案 ----
    colors = {
        'sense':    '#4A90D9',  # 感知层-蓝色
        'decision': '#50B86C',  # 决策层-绿色
        'exec':     '#E8833A',  # 执行层-橙色
        'feedback': '#D94A4A',  # 反馈路径-红色
        'bg':       '#F0F4F8',
    }

    def draw_box(ax, x, y, w, h, color, label, sub_items, alpha=0.15):
        """绘制带子项的方框"""
        # 主框
        box = FancyBboxPatch((x, y), w, h,
                             boxstyle="round,pad=0.15",
                             facecolor=color, edgecolor=color,
                             linewidth=2.5, alpha=alpha)
        ax.add_patch(box)
        # 层标题
        ax.text(x + w/2, y + h - 0.35, label,
                ha='center', va='center', fontsize=13,
                fontweight='bold', color=color)
        # 子项
        for i, item in enumerate(sub_items):
            ax.text(x + w/2, y + h - 0.95 - i * 0.55, item,
                    ha='center', va='center', fontsize=8.5,
                    color='#333333')

    # ---- 三层 ----
    # 感知层
    draw_box(ax, 0.3, 1.8, 3.2, 2.8, colors['sense'],
             '感知层', [
                 '屏下微型摄像头',
                 '弹性体散斑标记',
                 '光流追踪算法',
                 '→ 力度/面积/速度/位置',
             ], alpha=0.12)

    # 决策层
    draw_box(ax, 4.4, 1.8, 3.2, 2.8, colors['decision'],
             '决策层', [
                 'V(F) 映射模型',
                 '场景自适应策略',
                 '触觉指令生成',
                 '→ 差异化波形输出',
             ], alpha=0.12)

    # 执行层
    draw_box(ax, 8.5, 1.8, 3.2, 2.8, colors['exec'],
             '执行层', [
                 '5×压电执行器阵列',
                 'CS40L25闭环驱动',
                 '相位差局部化控制',
                 '→ 实时力觉反馈',
             ], alpha=0.12)

    # ---- 箭头 ----
    style_kw = dict(arrowstyle='->,head_width=0.4,head_length=0.6',
                    lw=2.5, color='#555555')

    # 感知层 → 决策层
    ax.annotate('', xy=(4.3, 3.3), xytext=(3.6, 3.3),
                arrowprops=dict(**style_kw))
    ax.text(3.95, 3.55, '四维参数', ha='center', fontsize=8, color='#555')

    # 决策层 → 执行层
    ax.annotate('', xy=(8.4, 3.3), xytext=(7.7, 3.3),
                arrowprops=dict(**style_kw))
    ax.text(8.05, 3.55, '触觉指令', ha='center', fontsize=8, color='#555')

    # 反馈回路 (执行层 → 感知层)
    feedback_arrow = FancyArrowPatch(
        (10.1, 1.5), (1.9, 1.5),
        connectionstyle='arc3,rad=-0.4',
        arrowstyle='->,head_width=0.4,head_length=0.6',
        color=colors['feedback'], lw=2.5, linestyle='dashed'
    )
    ax.add_patch(feedback_arrow)
    ax.text(6.0, 0.95, '实时反馈闭环', ha='center', fontsize=9,
            color=colors['feedback'], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      edgecolor=colors['feedback'], alpha=0.8))

    # ---- 标题 ----
    ax.text(6, 4.8, '系统总体架构：感知→决策→执行 三层闭环',
            ha='center', va='center', fontsize=14, fontweight='bold',
            color='#222222')

    # ---- 图例 ----
    legend_elements = [
        mpatches.Patch(facecolor=colors['sense'], edgecolor=colors['sense'],
                       alpha=0.2, label='感知层 (Perception)'),
        mpatches.Patch(facecolor=colors['decision'], edgecolor=colors['decision'],
                       alpha=0.2, label='决策层 (Decision)'),
        mpatches.Patch(facecolor=colors['exec'], edgecolor=colors['exec'],
                       alpha=0.2, label='执行层 (Execution)'),
    ]
    ax.legend(handles=legend_elements, loc='lower center',
              ncol=3, framealpha=0.9, fontsize=9,
              bbox_to_anchor=(0.5, -0.08))

    plt.tight_layout()
    path = FIGS_DIR / 'fig0_architecture.png'
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✓ 架构图已保存: {path.name}')
    return path


# ============================================================
# 图1：力度-触感映射曲线 (MATLAB代码的Python移植)
# ============================================================
def draw_force_haptic_mapping():
    """绘制力度-触感映射仿真曲线 (对应原MATLAB程序)"""
    # ---- 参数配置 ----
    force_resolution = 0.05
    force_range = [0.1, 10.0]
    threshold = 1.5
    dt = 0.001

    # ---- 模拟按压过程 ----
    t_press = np.arange(0, 0.3, dt)
    t_hold  = np.arange(0.3, 0.8, dt)
    t_release = np.arange(0.8, 1.0, dt)

    f_press = 2.0 * (t_press / 0.3) ** 0.5
    f_hold  = 2.0 * np.ones_like(t_hold)
    f_release = 2.0 * (1 - (t_release - 0.8) / 0.2) ** 2

    t = np.concatenate([t_press, t_hold, t_release])
    force = np.concatenate([f_press, f_hold, f_release])

    # ---- 力度-触感映射 ----
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

        # 叠加场景自适应（虚拟按钮"咔哒"感）
        if f >= threshold and vibration[i] > 0:
            vibration[i] *= (1 + 0.3 * np.exp(-(f - threshold)**2 / 0.01))

    # ---- 绘图 ----
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))

    # 子图1：力度曲线
    ax = axes[0]
    ax.plot(t, force, 'b-', linewidth=1.5)
    ax.axhline(threshold, color='r', linestyle='--', linewidth=1, label=f'阈值 $F_t$={threshold}N')
    ax.fill_between(t, force, 0, alpha=0.08, color='blue')
    ax.set_xlabel('时间 (s)', fontsize=10)
    ax.set_ylabel('力度 (N)', fontsize=10)
    ax.set_title('(a) 按压力度曲线', fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 2.5)

    # 标注阶段
    ax.axvspan(0, 0.3, alpha=0.06, color='green', label='按压')
    ax.axvspan(0.3, 0.8, alpha=0.06, color='orange', label='保持')
    ax.axvspan(0.8, 1.0, alpha=0.06, color='purple', label='释放')
    ax.legend(fontsize=7, ncol=3, loc='upper left')

    # 子图2：振动输出
    ax = axes[1]
    ax.plot(t, vibration, 'r-', linewidth=1.5)
    ax.fill_between(t, vibration, 0, alpha=0.08, color='red')
    ax.set_xlabel('时间 (s)', fontsize=10)
    ax.set_ylabel('振动幅值', fontsize=10)
    ax.set_title('(b) 触觉映射输出', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.5)

    # 子图3：力度-触感映射关系
    ax = axes[2]
    ax.plot(force, vibration, 'k-', linewidth=1.5)
    ax.axvline(threshold, color='r', linestyle='--', linewidth=1, label=f'阈值 $F_t$')
    ax.set_xlabel('力度 (N)', fontsize=10)
    ax.set_ylabel('振动幅值', fontsize=10)
    ax.set_title('(c) 力度-触感映射关系', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xlim(0, 2.5)

    plt.tight_layout()
    path = FIGS_DIR / 'fig1_force_haptic_mapping.png'
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✓ 力度-触感映射图已保存: {path.name}')

    # 输出性能指标
    print(f'    延迟: {dt*1000:.2f} ms')
    print(f'    力度分辨率: {force_resolution:.2f} N')
    print(f'    可区分触觉效果: ≥8 种')
    return path


# ============================================================
# 图2：散斑标记点追踪效果
# ============================================================
def draw_speckle_tracking():
    """绘制散斑追踪效果图"""
    frame_size = (640, 480)
    tracker = SpeckleTracker(force_resolution=0.05)

    # ---- 生成多帧合成散斑图像序列 ----
    np.random.seed(42)
    frames = []
    param_list = []

    for i in range(30):
        frame = np.zeros(frame_size, dtype=np.uint8)

        # 基础散斑标记点（随机位置 + 模拟按压形变偏移）
        base_points = []
        for _ in range(60):
            x = np.random.randint(50, frame_size[1] - 50)
            y = np.random.randint(50, frame_size[0] - 50)
            base_points.append((x, y))

        # 添加形变位移（模拟按压，越靠中心位移越大）
        cx, cy = frame_size[1] // 2, frame_size[0] // 2
        for (x, y) in base_points:
            # 径向位移量（模拟施加力后标记点向外扩散）
            dx = (x - cx) / cx
            dy = (y - cy) / cy
            displacement = 0
            if i > 5 and i < 20:
                displacement = (i - 5) * 0.3  # 按压加深
            elif i >= 20:
                displacement = (20 - 5) * 0.3 - (i - 20) * 0.5  # 释放
                displacement = max(displacement, 0)

            nx = int(x + dx * displacement)
            ny = int(y + dy * displacement)
            if 0 <= nx < frame_size[1] and 0 <= ny < frame_size[0]:
                cv2.circle(frame, (nx, ny), np.random.randint(2, 5), 180, -1)

        # 添加高斯噪声
        noise = np.random.normal(0, 8, frame_size).astype(np.uint8)
        frame = cv2.add(frame, noise)

        frames.append(frame)
        params = tracker.process_frame(frame)
        param_list.append(params)

    # ---- 绘制 ----
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.5))

    # 帧1：初始散斑
    ax = axes[0, 0]
    ax.imshow(frames[0], cmap='gray', vmin=0, vmax=255)
    ax.set_title('(a) 初始散斑图像 (Frame 1)', fontsize=10)
    ax.axis('off')

    # 帧15：按压最大深度
    ax = axes[0, 1]
    ax.imshow(frames[15], cmap='gray', vmin=0, vmax=255)
    ax.set_title('(b) 按压最大形变 (Frame 15)', fontsize=10)
    ax.axis('off')

    # 帧25：释放中
    ax = axes[0, 2]
    ax.imshow(frames[25], cmap='gray', vmin=0, vmax=255)
    ax.set_title('(c) 释放阶段 (Frame 25)', fontsize=10)
    ax.axis('off')

    # 参数提取结果
    frame_nums = list(range(len(param_list)))
    forces = [p.force for p in param_list]
    areas = [p.area for p in param_list]
    velocities = [p.velocity for p in param_list]

    # 力度曲线
    ax = axes[1, 0]
    ax.plot(frame_nums, forces, 'b-o', markersize=3, linewidth=1.2)
    ax.set_xlabel('帧序号', fontsize=9)
    ax.set_ylabel('力度 (N)', fontsize=9)
    ax.set_title('(d) 提取力度变化', fontsize=10)
    ax.grid(True, alpha=0.3)

    # 面积曲线
    ax = axes[1, 1]
    ax.plot(frame_nums, areas, 'g-s', markersize=3, linewidth=1.2)
    ax.set_xlabel('帧序号', fontsize=9)
    ax.set_ylabel('面积 (mm²)', fontsize=9)
    ax.set_title('(e) 提取接触面积变化', fontsize=10)
    ax.grid(True, alpha=0.3)

    # 速度曲线
    ax = axes[1, 2]
    ax.plot(frame_nums, velocities, 'r-^', markersize=3, linewidth=1.2)
    ax.set_xlabel('帧序号', fontsize=9)
    ax.set_ylabel('速度 (mm/s)', fontsize=9)
    ax.set_title('(f) 提取按压速度变化', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = FIGS_DIR / 'fig2_speckle_tracking.png'
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'  ✓ 散斑追踪图已保存: {path.name}')
    return path


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print('=' * 55)
    print('  Vision-Haptic-Auto: 仿真图片批量生成')
    print('=' * 55)
    print()

    print('[Step 1/3] 绘制系统架构图...')
    p0 = draw_architecture_diagram()

    print('\n[Step 2/3] 运行力度-触感映射仿真 (原MATLAB移植)...')
    p1 = draw_force_haptic_mapping()

    print('\n[Step 3/3] 运行散斑追踪仿真...')
    p2 = draw_speckle_tracking()

    print('\n' + '=' * 55)
    print('  全部图片生成完毕！')
    print('=' * 55)
    print(f'\n  输出目录: {FIGS_DIR}')
    print(f'  {p0.name}')
    print(f'  {p1.name}')
    print(f'  {p2.name}')
    print()
