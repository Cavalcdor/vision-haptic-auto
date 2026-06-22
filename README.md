# vision-haptic-auto

## Research And Development Of Smart Instruments Course Personal Project

### 基于视触觉感知的智能汽车触控屏力觉反馈系统设计

---

## 项目简介

本项目为《智能仪器设计与制造》课程大作业，选题类型为**创新设计类**。

针对智能汽车全面触屏化背景下驾驶员因缺乏触觉反馈而被迫依赖视觉确认、导致驾驶分心与安全隐患的问题，设计一套基于视触觉感知的智能汽车触控屏力觉反馈系统。

### 设计创新

1. **场景创新**：将视触觉传感技术从工业检测迁移至车载交互场景
2. **功能创新**：感知维度从"位置"拓展为"力度+面积+速度+位置"四维信息
3. **系统创新**：构建"感知层 → 决策层 → 执行层"完整反馈架构

### 系统架构

```
感知层：屏下微型摄像头 + 弹性体散斑标记 → 四维力触觉感知
   ↓
决策层：力度-触感映射算法 + 场景自适应策略
   ↓
执行层：压电执行器阵列 + 反馈控制驱动 → 差异化力觉反馈
```

---

## 仓库结构

```
vision-haptic-auto/
├── README.md                # 项目说明（本文件）
├── .gitignore               # Git 忽略规则
├── paper/                   # 论文文档
│   └── main.md              # Markdown 主文档
├── figures/                 # 图表资源
│   ├── fig0_architecture.png    # 系统架构图
│   ├── fig1_force_haptic_mapping.png  # 力度-触感映射图
│   ├── fig2_speckle_tracking.png      # 散斑追踪效果图
│   └── generate_all_figures.py  # 批量生图脚本
├── simulation/              # 仿真代码
│   ├── matlab/              # MATLAB 仿真
│   │   └── force_haptic_mapping.m
│   └── python/              # Python 仿真
│       └── speckle_tracker.py
└── references/              # 参考文献
    └── bibliography.bib     # BibTeX 参考文献
```

---

## 四个为什么

| 章节 | 关键问题 |
|------|----------|
| 一、引言 | **为什么做** — 产业背景、痛点分析、现有不足 |
| 二、技术现状 | **现有水平** — 电容屏/LRA/压电/视触觉四类技术现状 |
| 三、方案设计 | **要做什么** — 感知层+决策层+执行层三层架构设计 |
| 四、预期成果 | **做成什么样** — 性能指标、体验效果、验证方案 |
| 五、总结 | 回顾与展望 |

---

## 预期性能指标

| 指标 | 目标值 |
|------|--------|
| 力度感知分辨率 | ≤0.05N |
| 力度感知范围 | 0.1N ~ 10N |
| 接触面积分辨率 | ≤1mm² |
| 反馈响应延迟 | <10ms |
| 可区分触觉效果 | ≥8种 |
| 工作温度范围 | -40°C ~ +85°C |

---

## 参考文献

1. 中国汽车工业协会. *中国智能座舱产业发展研究报告*, 2024.
2. Lee J D, Young K L, Regan M A. Defining driver distraction. In *Driver Distraction: Theory, Effects, and Mitigation*, CRC Press, 2008.
3. Petermeijer S M, Abbink D A, Mulder M. Haptic feedback in automotive interfaces: A systematic review. *IEEE Trans. on Haptics*, 8(2), 2015.
4. TDK Corporation. *PowerHap: Piezoelectric Actuators for Haptic Applications*, 2020.
5. Cirrus Logic. *CS40L25: Piezo Haptic Driver Datasheet*, 2023.
6. Luo S, et al. Robotic tactile sensing for industrial applications. *IEEE Trans. on Industrial Informatics*, 14(2), 2017.
7. Li R, Adelson E H. A GelSight tactile sensor for robotic applications. *IEEE/RSJ IROS*, 2013.
8. Shimonomura K. Tactile image sensors employing camera: A review. *Sensors*, 19(19), 2019.

---

## License

MIT License — 仅供学术用途
