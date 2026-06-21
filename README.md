# vision-haptic-auto

## Research And Development Of Smart Instruments Course Personal Project

### 基于视触觉感知的智能汽车触控屏力觉反馈系统设计

---

## 项目简介

本项目为《智能仪器设计与制造》课程大作业，选题类型为**创新设计类**。

针对智能汽车全面触屏化背景下驾驶员因缺乏触觉反馈而被迫依赖视觉确认、导致驾驶分心与安全隐患的问题，设计一套基于视触觉传感的智能汽车触控屏力觉反馈系统。

### 核心创新

1. **场景创新**：将视触觉传感技术从工业检测迁移至车载交互场景
2. **功能创新**：感知维度从"位置"拓展为"力度+面积+速度+位置"四维信息
3. **系统创新**：构建"感知层 → 决策层 → 执行层"完整闭环架构

### 系统架构

```
感知层：屏下微型摄像头 + 弹性体散斑标记 → 四维力触觉感知
   ↓
决策层：力度-触感映射算法 + 场景自适应策略
   ↓
执行层：压电执行器阵列 + 闭环驱动 → 差异化力觉反馈
```

---

## 仓库结构

```
vision-haptic-auto/
├── README.md                # 项目说明（本文件）
├── .gitignore               # Git 忽略规则
├── paper/                   # 论文文档
│   └── main.tex             # LaTeX / Markdown 主文档
├── figures/                 # 图表资源
│   ├── system-architecture/ # 系统架构图
│   ├── algorithm-flow/      # 算法流程图
│   └── performance-table/   # 性能指标表
├── simulation/              # 仿真代码
│   ├── matlab/              # MATLAB 仿真
│   └── python/              # Python 仿真
└── references/              # 参考文献
    └── bibliography.bib     # BibTeX 参考文献
```

---

## 四个为什么

| 章节 | 核心问题 | 字数 |
|------|----------|------|
| 一、引言 | **为什么做** — 产业背景、痛点分析、现有不足 | ~500字 |
| 二、技术现状 | **现有水平** — 电容屏/LRA/压电/视触觉四类技术现状 | ~600字 |
| 三、方案设计 | **要做什么** — 感知层+决策层+执行层三层架构设计 | ~1000字 |
| 四、预期成果 | **做成什么样** — 性能指标、体验效果、验证方案 | ~500字 |
| 五、总结 | 回顾与展望 | ~300字 |

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

1. Li R, et al. *GelSight: A tactile sensing system for robotics*. IEEE RAM, 2014.
2. TDK Corporation. *PowerHap Piezo Actuators for Automotive Applications*, 2025.
3. Cirrus Logic. *CS40L51 Closed-Loop Haptic Driver Datasheet*, 2025.
4. BeStar Technologies. *Automotive Touchscreen Haptic Feedback Solutions*, 2025.
5. Zhai S, et al. *In-vehicle touchscreen haptic feedback using under-display camera*. JICV, 2025.
6. 北航团队. *透明触觉电子皮肤研究*. Advanced Science, 2024.
7. 中国汽车工业协会. *智能座舱发展趋势白皮书*, 2025.

---

## License

MIT License — 仅供学术用途
