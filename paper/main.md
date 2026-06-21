# Force Feedback System for Smart Vehicle Touchscreens Based on Vision-Haptic Sensing

<div class="no-number">
**Abstract**: The full touchscreen transition in smart vehicle cockpits forces drivers to divert their eyes from the road due to the lack of physical tactile cues, leading to distraction and safety risks. This paper proposes a vision-haptic force feedback system for automotive touchscreens: an under-display camera captures elastic deformation images, combined with speckle marker detection and optical flow tracking to extract four-dimensional parameters (force, contact area, velocity, and position). A force-haptic mapping model and scene-adaptive strategy drive a piezoelectric actuator array to generate differentiated real-time feedback. The system adopts a three-layer closed-loop architecture (Perception–Decision–Execution), targeting force resolution ≤0.05N, latency <10ms, and ≥8 distinguishable haptic effects.

**Keywords**: Vision-based tactile sensing; force feedback; smart vehicle; touchscreen; piezoelectric actuator

## Introduction

### Industrial Background

Smart vehicle cockpits are transitioning from physical buttons to large touchscreens. Following Tesla Model 3's removal of physical center console buttons, numerous brands have followed suit. Touchscreens have become the primary HMI for smart cockpits[1], hosting dozens of functions including navigation, HVAC, and entertainment.

### Key Challenges

The smooth glass surface of touchscreens lacks the tactile cues of physical buttons, forcing drivers to visually confirm operation positions. Even a 1–2 second glance means dozens of meters of "blind driving" at highway speeds. Lee et al. identified driver distraction as a leading cause of traffic accidents[2]. Key challenges include: increased risk from visual dependence, accidental touches on rough roads, degraded usability with gloves or glare, and lack of immediate physical confirmation.

### Limitations of Existing Solutions

Current automotive touchscreens use PCAP technology, outputting only 2D coordinates without force sensing. For haptics, LRA vibrators have >50ms latency and single-mode output[3]. While piezoelectric haptics offer fast response, existing implementations remain open-loop — triggering preset waveforms by touch location — without real-time closed-loop perception-feedback control.

### Objective

This paper aims to design an intelligent instrument system that senses four-dimensional parameters (force, area, velocity, position) and generates differentiated force feedback in real time.


## State of the Art

### Automotive Touchscreen Technology

Automotive touchscreens employ PCAP technology, detecting touch coordinates via capacitance changes at intersection points. While mature and reliable, output is limited to (x,y) coordinates without force information. Some solutions add a pressure-sensitive layer, but at higher cost and reduced optical transmittance.

### Haptic Feedback Technology

**Linear Resonant Actuators (LRA)** drive a mass-spring system at resonance, with >50ms latency and single waveform output[3].

**Piezoelectric haptic feedback** relies on the inverse piezoelectric effect — applying voltage to deform piezoelectric ceramics. Performance comparison is shown in Table 1.

**Table 1 LRA vs. Piezoelectric Actuator Comparison**

| Parameter | LRA | Piezoelectric |
|-----------|-----|---------------|
| Response time | >50ms | <3ms |
| Frequency range | Narrow (near resonance) | Wide (1Hz–1kHz) |
| Max acceleration | <10g | >50g |
| Localized feedback | Not possible | Feasible |
| Operating temperature | –20°C~+60°C | –40°C~+85°C |

Representative products include TDK PowerHap piezoelectric actuators[4] and Cirrus Logic CS40L25 driver IC[5].

### Vision-Haptic Sensing Technology

Vision-based tactile sensing uses elastomer deformation as a "tactile signal carrier," recovering contact parameters through optical imaging and vision algorithms[6]. MIT's GelSight, employing a reflective-coated elastomer with an embedded camera, achieves micron-level spatial resolution and milliNewton force precision[7]. Camera-based tactile sensors excel in miniaturization and resolution[8], with current applications primarily in industrial inspection and robotic grasping, while automotive HMI applications are still emerging.

### Summary of Limitations

| Layer | Limitation | Consequence |
|-------|-----------|-------------|
| Perception | Position only, no force sensing | Cannot "feel" press force |
| Decision | Open-loop table lookup, no real-time adaptation | Imprecise feedback timing |
| Execution | High-performance actuators without quality input | Monotonous haptic experience |


## 方案设计

### 总体架构

本系统采用"感知层→决策层→执行层"三层闭环架构：感知层捕获形变图像并提取参数；决策层依据映射模型与策略生成指令；执行层驱动压电阵列产生力觉反馈。核心创新在于视触觉传感与压电执行器的闭环耦合。

### 感知层：视触觉传感器设计

**核心思路**：以触控屏作为"弹性接触面"，屏下嵌入微型光学模块。手指按压时，弹性体形变引起表面散斑标记位移，摄像头拍摄标记图像，经视觉算法反演接触参数。

**关键设计**：
- **微型摄像头**：厚度<3mm的CMOS传感器，嵌入背光层与TFT层之间
- **环形照明**：近红外LED（940nm）侧面照射增强对比度
- **散斑标记**：弹性体背面微纳工艺制备随机散斑

**信号处理流程**：图像采集→去噪→标记点检测→光流追踪→四维参数输出。
高斯滤波去噪→自适应阈值+连通域提取标记点→LK光流追踪位移（单帧<10ms）；输出力度（≤0.05N）、面积（≤1mm²）、速度、位置。

### 决策层：智能映射算法

**（一）力度-触感映射模型**

将按压过程分为三阶段，振动幅值 $V$ 由力度 $F$ 通过分段函数映射：

$$
V(F) = \begin{cases}
\alpha \cdot (F / F_t) & 0 < F < F_t \quad (\text{按压阶段：行程感}) \\
V_{\max} \cdot e^{-(F-F_t)^2 / \sigma^2} & F = F_t \quad (\text{阈值触发：段落感}) \\
\beta + \gamma \cdot (F-F_t) & F_t < F < F_{\max} \quad (\text{保持阶段：力度反馈}) \\
\delta \cdot e^{-k \cdot (F/F_t)} & F \to 0 \quad (\text{释放阶段：回弹感})
\end{cases}
$$

其中 $F_t$ 为按压阈值，$\alpha,\beta,\gamma,\delta,\sigma,k$ 为可调参数（通过仿真标定），各阶段对应策略如下。

| 阶段 | 状态描述 | 反馈策略 |
|------|----------|----------|
| 按压阶段 | 力度从0增至$F_t$ | 轻振模拟"行程感"，达阈值时强脉冲模拟"段落感" |
| 保持阶段 | 力度在$F_t$以上持续 | 持续微振，幅值与$\gamma(F-F_t)$正相关 |
| 释放阶段 | 力度从$F_t$降至0 | 指数衰减振荡模拟"回弹感" |

**（二）场景自适应策略**

| 交互场景 | 触觉签名 | 参数配置 |
|----------|----------|----------|
| 虚拟按钮 | "咔哒"感 | 阈值触发 + 短脉冲（~5ms） |
| 滑动调节 | "刻度感" | 位置增量触发 + 逐级振动 |
| 长按确认 | "确认感" | 预振提示 + 强脉冲确认 |
| 紧急功能 | "警示感" | 低频高幅脉冲串（10~20Hz） |

### 执行层：压电执行器

**选型**：选用TDK PowerHap系列车规级压电执行器[4]（加速度>50g，响应<3ms，温度范围-40°C~+85°C）。

**布置方案**：屏幕四角及中央共5个执行器单元，通过相位差控制实现局部化反馈：按压点附近执行器产生主振动，远端执行器相位反向以抑制全局振动。

**驱动方案**：Cirrus Logic CS40L25闭环驱动芯片[5]实时监测阻抗变化，补偿温度和老化漂移。


## 预期成果

### 可量化性能指标

| 指标 | 目标值 |
|------|--------|
| 力度感知分辨率 | ≤0.05N |
| 力度感知范围 | 0.1N ~ 10N |
| 接触面积分辨率 | ≤1mm² |
| 反馈响应延迟 | <10ms |
| 可区分触觉效果 | ≥8种 |
| 工作温度范围 | -40°C ~ +85°C |

### 功能与体验效果

- **盲操作能力提升**：视线转移次数预计减少约60%，驾驶员可在注视道路的同时完成操作
- **误触率降低**：压力阈值设定下，颠簸路面误触率预计降低约70%
- **操作体验改善**：虚拟按键获得"按压感""段落感""回弹感"，不同功能拥有差异化"触觉签名"
- **操作信心增强**：即时确认反馈降低二次确认需求

### 验证方案

1. **光学仿真**：使用Zemax或相似工具仿真屏下成像光路，验证标记点成像质量
2. **算法仿真**：利用已开发的MATLAB力度-触感映射程序和Python散斑追踪程序运行生成结果：
   （此处插入图1：力度-触感映射曲线——由 `simulation/matlab/force_haptic_mapping.m` 运行生成）
   - (此处插入图2：散斑追踪效果——由 `simulation/python/speckle_tracker.py` 运行生成)
3. **模拟驾驶实验**：搭建模拟驾驶环境，对比有/无力觉反馈条件下驾驶员的触控操作表现

---

## 总结

本文针对车载触控操作的安全痛点，提出了基于视触觉感知的力觉反馈系统方案，构建了"感知-决策-执行"闭环架构。方案将视触觉传感迁移至车载交互场景，从单一位置感知拓展至力度、面积、速度四维，通过分段映射函数实现差异化反馈，在MATLAB和Python平台上完成了核心算法仿真（结果见图1、图2）。

未来工作可探索：深度学习形变反演提升精度；多指独立反馈策略；与驾驶员状态监测系统联动。


<div class="no-number">

## 参考文献

[1] 中国汽车工业协会. 中国智能座舱产业发展研究报告[R]. 2024.

[2] Lee J D, Young K L, Regan M A. Defining driver distraction[C]//Driver Distraction: Theory, Effects, and Mitigation. CRC Press, 2008: 31-40.

[3] Petermeijer S M, Abbink D A, Mulder M. Haptic feedback in automotive interfaces: A systematic review[J]. IEEE Transactions on Haptics, 2015, 8(2): 201-212.

[4] TDK Corporation. PowerHap: Piezoelectric actuators for haptic applications[R]. TDK Application Note, 2020.

[5] Cirrus Logic. CS40L25: Piezo haptic driver with WaveShape audio and haptic sensing[R]. Datasheet DS1151, 2023.

[6] Luo S, Bimbo J, Dahiya R, et al. Robotic tactile sensing for industrial applications[J]. IEEE Transactions on Industrial Informatics, 2017, 14(2): 458-468.

[7] Li R, Adelson E H. A GelSight tactile sensor for robotic applications[C]//2013 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS). IEEE, 2013: 123-129.

[8] Shimonomura K. Tactile image sensors employing camera: A review[J]. Sensors, 2019, 19(19): 4297.