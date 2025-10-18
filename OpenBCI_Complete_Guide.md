# OpenBCI 运动想象数据采集完整指南

## 目录
- [前置准备](#前置准备)
- [EEG 参考电极详解](#eeg-参考电极详解)
- [硬件配置](#硬件配置)
- [软件安装](#软件安装)
- [第一步：电极定位](#第一步电极定位)
- [第二步：阻抗检查](#第二步阻抗检查)
- [第三步：实验程序](#第三步实验程序)
- [第四步：数据预处理](#第四步数据预处理)
- [第五步：训练模型](#第五步训练模型)
- [数据质量检查](#数据质量检查)
- [常见问题排查](#常见问题排查)

---

## 前置准备

### 硬件清单
- [ ] OpenBCI Cyton Board (8通道，基于 ADS1299)
- [ ] USB Dongle 或 WiFi Shield
- [ ] 金杯电极 × 6（C3, Cz, C4 + 参考 + 地 + 备用）
- [ ] 导电膏（Ten20 或同类产品）
- [ ] 酒精棉片
- [ ] 卷尺（用于定位电极）
- [ ] 电极帽（可选，提供更稳定的固定）

### 时间预算
- 电极准备：30 分钟
- 单次实验：20-30 分钟（120 trials）
- 数据预处理：5 分钟
- 模型训练：1-3 小时（取决于硬件）

---

## EEG 参考电极详解

### 什么是参考电极？

EEG 测量的是**电位差**，必须有参考点。类似于测量电压需要正负极。

```
测量值 = (活动电极电位) - (参考电极电位)
```

### 两种参考方式对比

| 参考方式 | 原理 | 优点 | 缺点 | 适用场景 |
|---------|------|------|------|----------|
| **单点参考** | 用耳垂/乳突作参考 | 简单，硬件默认 | 参考点也有脑电信号，会混入噪声 | OpenBCI 默认 |
| **CAR (共平均参考)** | 所有电极平均值作参考 | 减少共模噪声，提升信噪比 | 需要后处理计算 | BCI Competition IV |

**CAR 公式**：
```
V_i_new = V_i - (1/N) Σ V_j
```

### 影响评估

| 影响项 | 严重程度 | 说明 |
|-------|---------|------|
| **分类准确率** | ⭐⭐⭐ 中等 | 可能降低 5-10% |
| **信噪比** | ⭐⭐⭐⭐ 较大 | CAR 能抑制共模干扰（如肌电） |
| **数据一致性** | ⭐⭐⭐⭐⭐ 关键 | 训练和测试必须使用同样的参考方式 |

### 解决方案

**在预处理阶段使用 MNE 进行 CAR 重参考**：

```python
# 在切分 Epoch 之前添加
raw.set_eeg_reference('average', projection=True)  # CAR 重参考
raw.apply_proj()  # 应用投影
```

---

## 硬件配置

### OpenBCI Cyton Board 规格
- 芯片：ADS1299 × 1
- 通道数：8
- 采样率：250 Hz（与 BCI Competition IV 一致）
- 分辨率：24-bit
- 输入范围：±187.5 mV

### 电极配置对照表

| 实验需求 | BCI Competition IV-2b | 你的 OpenBCI |
|---------|---------------------|--------------|
| 通道数 | 3 (C3, Cz, C4) | 8 可用，只用 3 个 |
| 采样率 | 250 Hz | 250 Hz ✅ |
| 参考方式 | CAR (共平均) | 单点参考 → 需软件转换 |

---

## 软件安装

### Python 环境配置

```bash
# 创建虚拟环境
conda create -n openbci python=3.10
conda activate openbci

# 安装核心依赖
pip install brainflow      # OpenBCI 数据采集
pip install psychopy       # 实验刺激呈现
pip install mne            # EEG 数据处理
pip install numpy scipy    # 数值计算
pip install matplotlib     # 可视化
```

### 验证安装

```python
import brainflow
import psychopy
import mne
print("✓ 所有库安装成功")
```

---

## 第一步：电极定位

### 国际 10-20 系统

```
         Fpz (地线)
          |
    F3 - Fz - F4
          |
    C3 - Cz - C4  ← 主要测量点（运动皮层）
          |
    P3 - Pz - P4
          |
          Oz
```

### 测量步骤

#### 1. 定位 Cz（头顶中心点）

**方法 1：十字交叉法**
- 测量鼻根到枕骨隆突的距离，标记 50% 处
- 测量左右耳前的距离，标记 50% 处
- 两线交点即为 Cz

**方法 2：简易法**
- 头围中点，头顶最高点附近

#### 2. 定位 C3 和 C4

从 Cz 出发：
- **C3**：向左移动 20% 的耳间距（左侧运动皮层）
- **C4**：向右移动 20% 的耳间距（右侧运动皮层）

**公式**：
```
耳间距 = 左耳前 → 右耳前的直线距离
C3 位置 = Cz - 0.2 × 耳间距（向左）
C4 位置 = Cz + 0.2 × 耳间距（向右）
```

#### 3. 定位参考和地线

- **参考电极（BIAS）**：左耳垂或左乳突
- **地线（SRB/GND）**：前额 Fpz 或右耳垂

### OpenBCI 引脚连接

| OpenBCI 通道 | 电极位置 | 功能 | 推荐颜色 |
|-------------|---------|------|---------|
| **CH1 (N1P)** | C3 | 左侧运动皮层 | 蓝色 |
| **CH2 (N2P)** | Cz | 中央运动皮层 | 绿色 |
| **CH3 (N3P)** | C4 | 右侧运动皮层 | 红色 |
| **BIAS** | 左耳垂 | 参考电极 | 黑色 |
| **SRB (GND)** | Fpz 或右耳垂 | 地线 | 白色 |

### 电极安装技巧

1. **清洁皮肤**：用酒精棉片擦拭电极位置
2. **去除角质**：轻轻摩擦皮肤，去除死皮（提高导电性）
3. **涂抹导电膏**：在电极杯内填充适量导电膏
4. **固定电极**：确保电极与皮肤紧密接触
5. **检查阻抗**：应低于 10 kΩ

---

## 第二步：阻抗检查

### 为什么要检查阻抗？

- 高阻抗 → 信号弱，噪声大
- 目标：< 10 kΩ（理想 < 5 kΩ）

### 检查方法

#### 方法 1：使用 OpenBCI GUI

1. 打开 OpenBCI GUI
2. 连接 Cyton Board
3. 点击 "Impedance Check"
4. 查看各通道阻抗值

#### 方法 2：使用 Python 脚本

```python
from brainflow import BoardShim, BrainFlowInputParams, BoardIds

# 连接 OpenBCI
params = BrainFlowInputParams()
params.serial_port = 'COM3'  # Windows
# params.serial_port = '/dev/cu.usbserial-DM03H8JT'  # macOS
board = BoardShim(BoardIds.CYTON_BOARD, params)

board.prepare_session()

# 开始阻抗测试
board.config_board('z')  # 发送阻抗测试命令

# 等待 5 秒读取结果
import time
time.sleep(5)

# 停止测试
board.config_board('Z')

board.release_session()
```

### 阻抗过高的解决方法

| 阻抗值 | 状态 | 解决方法 |
|-------|------|---------|
| < 5 kΩ | ✅ 优秀 | 无需处理 |
| 5-10 kΩ | ⚠️ 可接受 | 可选：补充导电膏 |
| 10-50 kΩ | ❌ 较差 | 1. 补充导电膏<br>2. 重新清洁皮肤<br>3. 轻轻摩擦去除角质 |
| > 50 kΩ | ❌❌ 不可用 | 1. 重新定位电极<br>2. 更换导电膏<br>3. 检查电极连接 |

---

## 第三步：实验程序

### 实验范式（复现 BCI Competition IV-2b）

每个 Trial 的时序：

```
0s ────────────── 2s ─── 6s ──────── 8s
│      准备期      │ 想象期 │  休息期  │
│    (注视+)      │ (箭头) │  (黑屏)  │
│                 ↑                   │
│            发送事件标记              │
```

**详细说明**：
1. **0-2s**：屏幕显示十字注视点 `+`，受试者准备
2. **2s**：播放提示音（beep），提醒即将开始
3. **2-6s**：显示箭头（← 或 →），想象对应手握拳 4 秒
4. **6-8s**：黑屏休息 2 秒

**单个 Session**：
- 120-160 个 trials
- 左右手随机分布（各 50%）
- 总时长：约 16-21 分钟

### 完整实验代码

创建文件 `motor_imagery_experiment.py`：

```python
"""
OpenBCI 运动想象数据采集程序
复现 BCI Competition IV-2b 实验范式
Author: Your Name
Date: 2025-01-18
"""

import numpy as np
import time
from datetime import datetime
from psychopy import visual, core, event, sound
from brainflow import BoardShim, BrainFlowInputParams, BoardIds
import json

class MotorImageryExperiment:
    def __init__(self, subject_id, session_id, n_trials=120):
        """
        初始化实验

        参数:
            subject_id: 受试者编号 (1-99)
            session_id: Session 编号 (1-5)
            n_trials: Trial 数量 (建议 120-160)
        """
        self.subject_id = subject_id
        self.session_id = session_id
        self.n_trials = n_trials
        self.labels = []

        # OpenBCI 设置
        params = BrainFlowInputParams()
        params.serial_port = 'COM3'  # ⚠️ 修改为你的端口
        # Windows: 'COM3'
        # macOS: '/dev/cu.usbserial-DM03H8JT'
        # Linux: '/dev/ttyUSB0'

        self.board = BoardShim(BoardIds.CYTON_BOARD, params)

        # PsychoPy 窗口
        self.win = visual.Window(
            [1920, 1080],
            fullscr=True,
            color='black',
            units='norm'
        )

        # 视觉刺激
        self.fixation = visual.TextStim(
            self.win,
            text='+',
            height=0.2,
            color='white'
        )
        self.arrow_left = visual.TextStim(
            self.win,
            text='←',
            height=0.3,
            color='white'
        )
        self.arrow_right = visual.TextStim(
            self.win,
            text='→',
            height=0.3,
            color='white'
        )
        self.instruction = visual.TextStim(
            self.win,
            text='',
            height=0.1,
            color='white',
            pos=(0, -0.3)
        )

        # 提示音
        try:
            self.beep = sound.Sound(800, secs=0.1)  # 800Hz, 100ms
        except:
            print("⚠️ 无法初始化声音，将跳过提示音")
            self.beep = None

    def prepare(self):
        """准备阶段：显示说明并开始采集"""
        # 启动 OpenBCI
        print("正在连接 OpenBCI...")
        self.board.prepare_session()
        self.board.start_stream()
        print(f"✓ OpenBCI 开始采集 @ 250Hz")

        # 显示实验说明
        instruction_text = """
        运动想象实验

        实验说明：
        - 看到 ← 时，想象左手握拳
        - 看到 → 时，想象右手握拳
        - 保持专注，尽量不要眨眼
        - 每次试验约 8 秒

        注意事项：
        - 想象动作要生动、具体
        - 想象手部肌肉收缩的感觉
        - 保持头部静止

        按空格键开始实验
        按 ESC 键可随时退出
        """
        self.instruction.text = instruction_text
        self.instruction.pos = (0, 0)
        self.instruction.height = 0.06
        self.instruction.draw()
        self.win.flip()

        # 等待用户按键
        keys = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            self.cleanup()
            return False

        return True

    def run_trial(self, trial_num):
        """
        运行单个 trial

        参数:
            trial_num: Trial 编号 (0-based)

        返回:
            timestamp: 事件发生时间
            marker: 事件标记 (1=左手, 2=右手)
        """
        # 随机选择左/右手
        direction = np.random.choice(['left', 'right'])
        label = 1 if direction == 'left' else 2
        self.labels.append(label)

        # 检查是否按了 ESC 退出
        if event.getKeys(['escape']):
            return None, None

        # 阶段 1: 准备期（2秒，注视十字）
        self.fixation.draw()
        self.win.flip()
        time.sleep(2.0)

        # 阶段 2: 提示音
        if self.beep:
            self.beep.play()
            core.wait(0.1)

        # 阶段 3: 发送事件标记 + 显示箭头（4秒运动想象）
        marker = 1 if direction == 'left' else 2
        timestamp = time.time()

        # 发送标记到 OpenBCI
        self.board.insert_marker(marker)

        # 显示箭头
        if direction == 'left':
            self.arrow_left.draw()
        else:
            self.arrow_right.draw()
        self.win.flip()

        time.sleep(4.0)  # 想象动作 4 秒

        # 阶段 4: 休息（2秒黑屏）
        self.win.flip()
        time.sleep(2.0)

        # 每 20 个 trial 休息一次
        if (trial_num + 1) % 20 == 0 and (trial_num + 1) < self.n_trials:
            self.instruction.text = f'已完成 {trial_num + 1}/{self.n_trials}\n\n休息 10 秒\n\n按空格继续'
            self.instruction.pos = (0, 0)
            self.instruction.height = 0.08
            self.instruction.draw()
            self.win.flip()

            # 等待 10 秒或用户按键
            start_time = time.time()
            while time.time() - start_time < 10:
                if event.getKeys(['space']):
                    break
                core.wait(0.1)

        return timestamp, marker

    def run(self):
        """运行完整实验"""
        # 准备阶段
        if not self.prepare():
            return

        event_log = []

        print(f"\n开始采集 Subject {self.subject_id}, Session {self.session_id}")
        print(f"共 {self.n_trials} 个 trials\n")

        # 运行所有 trials
        for i in range(self.n_trials):
            timestamp, marker = self.run_trial(i)

            # 检查是否提前退出
            if timestamp is None:
                print("\n实验被用户中断")
                break

            # 记录事件
            event_log.append({
                'trial': i + 1,
                'timestamp': timestamp,
                'marker': marker,
                'label': self.labels[-1],
                'direction': 'left' if marker == 1 else 'right'
            })

            # 打印进度
            direction_str = '左手' if marker == 1 else '右手'
            print(f"Trial {i+1}/{self.n_trials}: {direction_str}")

        # 停止采集
        print("\n停止采集...")
        time.sleep(1)
        data = self.board.get_board_data()
        self.board.stop_stream()
        self.board.release_session()

        # 保存数据
        self.save_data(data, event_log)

        # 结束提示
        self.instruction.text = '实验完成！\n\n感谢参与\n\n窗口将在 3 秒后关闭'
        self.instruction.pos = (0, 0)
        self.instruction.height = 0.08
        self.instruction.draw()
        self.win.flip()
        time.sleep(3)

        self.cleanup()

    def save_data(self, data, event_log):
        """保存原始数据、事件和标签"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f'S{self.subject_id:02d}_Session{self.session_id}_{timestamp}'

        # 创建保存目录
        import os
        os.makedirs('raw_data', exist_ok=True)

        # 保存 NumPy 格式（原始数据）
        np.save(f'raw_data/{filename_base}_raw.npy', data)
        print(f"\n✓ 原始数据已保存: raw_data/{filename_base}_raw.npy")
        print(f"  Shape: {data.shape}")

        # 保存事件日志（JSON）
        with open(f'raw_data/{filename_base}_events.json', 'w') as f:
            json.dump(event_log, f, indent=2)
        print(f"✓ 事件日志已保存: raw_data/{filename_base}_events.json")
        print(f"  共 {len(event_log)} 个事件")

        # 保存标签（NumPy）
        labels_array = np.array(self.labels).reshape(-1, 1)
        np.save(f'raw_data/{filename_base}_labels.npy', labels_array)
        print(f"✓ 标签已保存: raw_data/{filename_base}_labels.npy")

        # 保存统计信息
        left_count = np.sum(labels_array == 1)
        right_count = np.sum(labels_array == 2)
        print(f"\n统计信息:")
        print(f"  左手: {left_count} 次 ({left_count/len(self.labels)*100:.1f}%)")
        print(f"  右手: {right_count} 次 ({right_count/len(self.labels)*100:.1f}%)")

    def cleanup(self):
        """清理资源"""
        try:
            self.win.close()
        except:
            pass
        core.quit()


if __name__ == '__main__':
    # 运行实验
    print("=" * 60)
    print("OpenBCI 运动想象数据采集程序")
    print("=" * 60)

    # 输入受试者信息
    try:
        subject_id = int(input("请输入受试者编号 (1-99): "))
        session_id = int(input("请输入 Session 编号 (1-5): "))
        n_trials = int(input("请输入 Trial 数量 (推荐 120): ") or "120")
    except:
        print("输入错误，使用默认值")
        subject_id = 1
        session_id = 1
        n_trials = 120

    # 创建并运行实验
    exp = MotorImageryExperiment(
        subject_id=subject_id,
        session_id=session_id,
        n_trials=n_trials
    )

    try:
        exp.run()
    except KeyboardInterrupt:
        print("\n\n实验被中断")
        exp.cleanup()
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()
        exp.cleanup()
```

### 运行实验

```bash
conda activate openbci
python motor_imagery_experiment.py
```

**注意事项**：
1. 确保 OpenBCI 已连接并通电
2. 修改脚本中的串口号（`params.serial_port`）
3. 第一次运行建议先用少量 trials 测试（如 10 个）
4. 正式采集建议 120-160 trials/session

---

## 第四步：数据预处理

### 预处理流程

```
原始 .npy 文件
    ↓
提取 EEG 通道 (C3, Cz, C4)
    ↓
⭐ CAR 重参考
    ↓
带通滤波 (0.5-100 Hz)
    ↓
提取事件标记
    ↓
分段 (Epoching: 0-4s)
    ↓
保存为 .mat 格式
```

### 完整预处理代码

创建文件 `preprocess_openbci.py`：

```python
"""
OpenBCI 数据预处理脚本
将原始 .npy 转换为 CTNet 所需的 .mat 格式

Author: Your Name
Date: 2025-01-18
"""

import numpy as np
import mne
from scipy.io import savemat
from brainflow import BoardShim, BoardIds
import json
import os

def preprocess_openbci_data(raw_file, labels_file, events_file, output_file):
    """
    预处理 OpenBCI 数据

    参数:
        raw_file: 原始数据 .npy 文件路径
        labels_file: 标签 .npy 文件路径
        events_file: 事件日志 .json 文件路径
        output_file: 输出 .mat 文件路径
    """

    print("=" * 60)
    print("OpenBCI 数据预处理")
    print("=" * 60)

    # 1. 加载原始数据
    print("\n[1/9] 加载原始数据...")
    data = np.load(raw_file)
    labels = np.load(labels_file)
    with open(events_file, 'r') as f:
        events_log = json.load(f)

    print(f"  原始数据 shape: {data.shape}")
    print(f"  标签数量: {len(labels)}")
    print(f"  事件数量: {len(events_log)}")

    # 2. 提取 EEG 通道
    print("\n[2/9] 提取 EEG 通道...")
    eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD)
    eeg_data = data[eeg_channels[:3], :]  # C3, Cz, C4 (前3个通道)

    # 转换单位：BrainFlow 输出 µV，MNE 需要 V
    eeg_data = eeg_data * 1e-6

    print(f"  EEG 数据 shape: {eeg_data.shape}")
    print(f"  通道: C3, Cz, C4")

    # 3. 创建 MNE Raw 对象
    print("\n[3/9] 创建 MNE Raw 对象...")
    ch_names = ['C3', 'Cz', 'C4']
    ch_types = ['eeg'] * 3
    sfreq = BoardShim.get_sampling_rate(BoardIds.CYTON_BOARD)  # 250 Hz

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(eeg_data, info)

    print(f"  采样率: {sfreq} Hz")
    print(f"  时长: {raw.times[-1]:.2f} 秒")

    # 4. ⭐ CAR 重参考（关键步骤！）
    print("\n[4/9] 应用 CAR 重参考...")
    raw.set_eeg_reference('average', projection=True)
    raw.apply_proj()
    print("  ✓ CAR 重参考完成")

    # 5. 带通滤波
    print("\n[5/9] 带通滤波 (0.5-100 Hz)...")
    raw.filter(l_freq=0.5, h_freq=100.0, fir_design='firwin')
    print("  ✓ 滤波完成")

    # 6. 提取事件标记
    print("\n[6/9] 提取事件标记...")
    marker_channel = BoardShim.get_marker_channel(BoardIds.CYTON_BOARD)
    markers = data[marker_channel, :]

    # 找到非零标记
    event_indices = np.where(markers != 0)[0]
    event_ids = markers[event_indices].astype(int)

    # 创建 MNE events 数组
    events = np.column_stack((
        event_indices,
        np.zeros(len(event_indices), dtype=int),
        event_ids
    ))

    print(f"  找到 {len(events)} 个事件标记")
    print(f"  事件类型: {np.unique(event_ids)}")

    # 7. 分段（Epoching）
    print("\n[7/9] 分段处理...")
    event_id = {'Left': 1, 'Right': 2}
    tmin, tmax = 0, 3.996  # 0-4秒，1000样本点 @ 250Hz

    epochs = mne.Epochs(
        raw,
        events,
        event_id=event_id,
        tmin=tmin,
        tmax=tmax,
        baseline=None,  # 不做基线校正（与 BCI IV 一致）
        preload=True,
        proj=True,  # 应用 CAR 投影
        verbose=False
    )

    # 8. 获取数据
    print("\n[8/9] 提取 epoch 数据...")
    epochs_data = epochs.get_data()  # (n_trials, 3, 1000)

    # 验证数据
    print(f"  Epochs shape: {epochs_data.shape}")
    print(f"  Labels shape: {labels.shape}")

    # 检查数据一致性
    if epochs_data.shape[0] != labels.shape[0]:
        print(f"\n⚠️ 警告: Trial 数量不匹配！")
        print(f"  Epochs: {epochs_data.shape[0]}, Labels: {labels.shape[0]}")
        # 取较小的数量
        min_trials = min(epochs_data.shape[0], labels.shape[0])
        epochs_data = epochs_data[:min_trials]
        labels = labels[:min_trials]
        print(f"  已截断为: {min_trials} trials")

    assert epochs_data.shape[2] == 1000, f"时间点数量应为 1000，实际为 {epochs_data.shape[2]}"

    # 9. 保存为 .mat 格式
    print("\n[9/9] 保存数据...")
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)

    savemat(output_file, {
        'data': epochs_data,
        'label': labels
    })

    print(f"\n✓ 预处理完成: {output_file}")
    print("\n" + "=" * 60)
    print("数据摘要")
    print("=" * 60)
    print(f"  数据 shape: {epochs_data.shape}")
    print(f"  标签 shape: {labels.shape}")
    print(f"  采样率: {sfreq} Hz")
    print(f"  通道: {ch_names}")
    print(f"  时间窗: {tmin} - {tmax} 秒")
    print(f"  左手 trials: {np.sum(labels == 1)}")
    print(f"  右手 trials: {np.sum(labels == 2)}")
    print("=" * 60)


def batch_preprocess(data_dir='raw_data', output_dir='mymat_withoutFilter'):
    """
    批量预处理所有原始数据文件

    参数:
        data_dir: 原始数据目录
        output_dir: 输出目录
    """
    import glob

    # 查找所有原始数据文件
    raw_files = glob.glob(f'{data_dir}/*_raw.npy')

    if not raw_files:
        print(f"❌ 在 {data_dir} 中未找到原始数据文件")
        return

    print(f"\n找到 {len(raw_files)} 个原始数据文件\n")

    for raw_file in raw_files:
        # 提取文件名基础部分
        base_name = raw_file.replace('_raw.npy', '').replace(f'{data_dir}/', '')

        # 构建文件路径
        labels_file = f'{data_dir}/{base_name}_labels.npy'
        events_file = f'{data_dir}/{base_name}_events.json'
        output_file = f'{output_dir}/{base_name.split("_")[0]}T.mat'  # S01_Session1 → S01T.mat

        # 检查文件是否存在
        if not os.path.exists(labels_file):
            print(f"⚠️ 跳过 {base_name}: 缺少标签文件")
            continue
        if not os.path.exists(events_file):
            print(f"⚠️ 跳过 {base_name}: 缺少事件文件")
            continue

        # 预处理
        print(f"\n处理: {base_name}")
        try:
            preprocess_openbci_data(raw_file, labels_file, events_file, output_file)
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            continue


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # 单文件模式
        if len(sys.argv) != 5:
            print("用法: python preprocess_openbci.py <raw.npy> <labels.npy> <events.json> <output.mat>")
            print("或者: python preprocess_openbci.py  (批量处理 raw_data/ 目录)")
            sys.exit(1)

        raw_file = sys.argv[1]
        labels_file = sys.argv[2]
        events_file = sys.argv[3]
        output_file = sys.argv[4]

        preprocess_openbci_data(raw_file, labels_file, events_file, output_file)
    else:
        # 批量处理模式
        batch_preprocess()
```

### 运行预处理

#### 单文件处理
```bash
python preprocess_openbci.py \
    raw_data/S01_Session1_20250118_120000_raw.npy \
    raw_data/S01_Session1_20250118_120000_labels.npy \
    raw_data/S01_Session1_20250118_120000_events.json \
    mymat_withoutFilter/S01T.mat
```

#### 批量处理
```bash
python preprocess_openbci.py
```

---

## 第五步：训练模型

### 修改训练脚本

编辑 `main_subject_specific.py`：

```python
# 第700行：修改数据路径
DATA_DIR = r'./mymat_withoutFilter/'

# 第703行：修改受试者数量
N_SUBJECT = 1  # 只训练你自己的数据

# 第711行：确认数据集类型
TYPE = 'B'  # 2分类（左右手）

# 第551行：修改 torch.load（如果 PyTorch >= 2.6）
self.model = torch.load(self.model_filename, weights_only=False).cuda()
```

### 运行训练

```bash
conda activate eeg-moabb  # 或你的环境名
python main_subject_specific.py
```

### 预期结果

**受试者特定（Subject-Dependent）模式**：
- 训练集准确率：90-95%
- 验证集准确率：85-92%
- **测试集准确率：75-88%**（目标）

**如果准确率低于 70%**：
1. 检查数据质量（阻抗、信号幅值）
2. 增加训练数据（多采集几个 session）
3. 调整超参数（学习率、数据增强）

---

## 数据质量检查

### 检查脚本

创建文件 `check_data_quality.py`：

```python
"""
数据质量检查工具
Author: Your Name
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

def check_signal_quality(raw_file, output_prefix='quality_check'):
    """检查 EEG 信号质量"""

    print("=" * 60)
    print("EEG 数据质量检查")
    print("=" * 60)

    # 加载数据
    data = np.load(raw_file)
    eeg = data[:3, :]  # C3, Cz, C4

    # 1. 检查信号幅值
    print("\n[1] 信号幅值检查")
    print(f"  C3: {eeg[0].min():.2f} ~ {eeg[0].max():.2f} µV")
    print(f"  Cz: {eeg[1].min():.2f} ~ {eeg[1].max():.2f} µV")
    print(f"  C4: {eeg[2].min():.2f} ~ {eeg[2].max():.2f} µV")

    # 判断
    if np.abs(eeg).max() > 200:
        print("  ⚠️ 警告: 幅值过大，可能有肌电干扰")
    elif np.abs(eeg).max() < 10:
        print("  ⚠️ 警告: 幅值过小，检查电极接触")
    else:
        print("  ✓ 幅值正常")

    # 2. 可视化原始信号
    print("\n[2] 生成信号波形图...")
    fig, axes = plt.subplots(3, 1, figsize=(15, 8))
    ch_names = ['C3', 'Cz', 'C4']

    for i, (ax, name) in enumerate(zip(axes, ch_names)):
        # 显示前 40 秒
        n_samples = min(10000, eeg.shape[1])
        time = np.arange(n_samples) / 250  # 250 Hz

        ax.plot(time, eeg[i, :n_samples], linewidth=0.5)
        ax.set_ylabel(f'{name} (µV)', fontsize=12)
        ax.set_xlim(0, time[-1])
        ax.grid(True, alpha=0.3)

        if i == 2:
            ax.set_xlabel('Time (s)', fontsize=12)
        if i == 0:
            ax.set_title('EEG Signal Quality Check', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'{output_prefix}_waveform.png', dpi=150)
    print(f"  ✓ 保存: {output_prefix}_waveform.png")

    # 3. 功率谱分析
    print("\n[3] 生成功率谱图...")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    for i, (ax, name) in enumerate(zip(axes, ch_names)):
        # 计算功率谱
        freqs, psd = welch(eeg[i, :], fs=250, nperseg=512)

        # 只显示 0-50 Hz
        mask = freqs <= 50
        ax.semilogy(freqs[mask], psd[mask])
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('PSD (µV²/Hz)')
        ax.set_title(name)
        ax.grid(True, alpha=0.3)

        # 标记 alpha 波段 (8-13 Hz)
        ax.axvspan(8, 13, alpha=0.2, color='green', label='Alpha (8-13 Hz)')
        ax.legend(fontsize=8)

    plt.suptitle('Power Spectral Density', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_prefix}_psd.png', dpi=150)
    print(f"  ✓ 保存: {output_prefix}_psd.png")

    # 4. 检查工频干扰
    print("\n[4] 工频干扰检查")
    # 检查 50Hz 和 60Hz 附近的功率
    freqs, psd = welch(eeg[1, :], fs=250, nperseg=2048)  # Cz 通道

    # 找 50Hz 和 60Hz 的功率
    idx_50 = np.argmin(np.abs(freqs - 50))
    idx_60 = np.argmin(np.abs(freqs - 60))
    power_50 = psd[idx_50]
    power_60 = psd[idx_60]

    # 与周围频率比较
    avg_power = np.mean(psd[40:70])

    if power_50 > 3 * avg_power:
        print("  ⚠️ 检测到 50Hz 工频干扰")
    elif power_60 > 3 * avg_power:
        print("  ⚠️ 检测到 60Hz 工频干扰")
    else:
        print("  ✓ 无明显工频干扰")

    # 5. Alpha 波检测
    print("\n[5] Alpha 波检测 (8-13 Hz)")
    alpha_mask = (freqs >= 8) & (freqs <= 13)
    alpha_power = np.mean(psd[alpha_mask])
    total_power = np.mean(psd[(freqs >= 1) & (freqs <= 40)])
    alpha_ratio = alpha_power / total_power

    print(f"  Alpha 功率占比: {alpha_ratio*100:.1f}%")
    if alpha_ratio > 0.15:
        print("  ✓ Alpha 波明显（闭眼或放松状态）")
    else:
        print("  ⚠️ Alpha 波较弱（正常，运动想象时会减弱）")

    print("\n" + "=" * 60)
    print("质量检查完成")
    print("=" * 60)
    print(f"\n请检查生成的图片：")
    print(f"  - {output_prefix}_waveform.png")
    print(f"  - {output_prefix}_psd.png")
    print("\n合格标准：")
    print("  ✓ 幅值在 ±100 µV 内")
    print("  ✓ 无明显 50/60 Hz 工频干扰")
    print("  ✓ 无饱和削波现象")
    print("  ✓ 信号相对平稳，无大幅跳变")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python check_data_quality.py <raw_data.npy>")
        print("示例: python check_data_quality.py raw_data/S01_Session1_xxx_raw.npy")
        sys.exit(1)

    raw_file = sys.argv[1]
    check_signal_quality(raw_file)
```

### 运行检查

```bash
python check_data_quality.py raw_data/S01_Session1_xxx_raw.npy
```

### 合格标准

| 检查项 | 标准 | 不合格原因 |
|-------|------|-----------|
| **幅值** | ±100 µV 内 | 电极接触不良 / 肌电干扰 |
| **工频干扰** | 无明显 50/60Hz 峰 | 地线接触不良 / 屏蔽不足 |
| **Alpha 波** | 有 8-13Hz 峰（可选） | 正常，运动想象时减弱 |
| **波形** | 平滑，无跳变 | 电极松动 / 移动伪迹 |

---

## 常见问题排查

### 信号问题

| 问题 | 症状 | 可能原因 | 解决方法 |
|------|------|----------|----------|
| **全是噪声** | 幅值 > 500 µV，不规则 | 电极接触不良 | 1. 检查阻抗<br>2. 补充导电膏<br>3. 清洁皮肤 |
| **50/60Hz 干扰** | 功率谱有尖峰 | 地线接触不良 | 1. 确保地线稳固<br>2. 远离电源线<br>3. 使用屏蔽室 |
| **信号饱和** | 幅值 > 200 µV | 增益过高 / 肌电干扰 | 1. OpenBCI GUI 调整 gain<br>2. 放松肌肉<br>3. 固定头部 |
| **信号过小** | 幅值 < 10 µV | 电极氧化 / 导电膏干涸 | 1. 更换电极<br>2. 补充导电膏<br>3. 检查连接线 |

### 实验问题

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| **无事件标记** | `insert_marker()` 失败 | 检查 BrainFlow 版本，确保调用正确 |
| **Trial 数量不匹配** | 事件标记丢失 | 增加标记间隔时间，检查缓冲区 |
| **分类准确率低** | 想象不到位 / 数据质量差 | 1. 多练习<br>2. 增加数据量<br>3. 检查信号质量 |
| **PsychoPy 报错** | 版本兼容问题 | 降级到 `psychopy==2023.2.3` |

### 预处理问题

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| **Epoch 数量为 0** | 事件提取失败 | 检查 marker channel，确认标记已记录 |
| **时间点不是 1000** | 采样率错误 | 确认 OpenBCI 设置为 250 Hz |
| **CAR 失败** | 通道数不足 | 至少需要 3 个通道 |

---

## 进阶优化

### 提高分类准确率的方法

#### 1. 增加训练数据
- 采集多个 session（3-5 个）
- 每个 session 120-160 trials
- 总计 400-800 trials

#### 2. 改进实验范式
```python
# 增加练习阶段
def practice_session(n_trials=20):
    """实时反馈的练习 session"""
    # 显示想象效果（简单分类器）
    # 帮助受试者找到感觉
```

#### 3. 优化超参数
```python
# main_subject_specific.py
N_AUG = 5          # 增加数据增强（3→5）
EPOCHS = 1500      # 增加训练轮数
validate_ratio = 0.25  # 调整验证集比例
```

#### 4. 多 Session 融合
```python
# 合并多个 session 的数据
data_all = []
labels_all = []

for session_id in [1, 2, 3]:
    mat = loadmat(f'S01_Session{session_id}.mat')
    data_all.append(mat['data'])
    labels_all.append(mat['label'])

data_combined = np.vstack(data_all)
labels_combined = np.vstack(labels_all)
```

---

## 总结

### 完整工作流程

```
1. 硬件准备 (30分钟)
   ├─ 电极定位
   ├─ 阻抗检查 (< 10 kΩ)
   └─ OpenBCI 连接测试

2. 数据采集 (20分钟/session)
   ├─ 运行 motor_imagery_experiment.py
   ├─ 采集 120-160 trials
   └─ 保存 .npy 文件

3. 数据预处理 (5分钟)
   ├─ 运行 preprocess_openbci.py
   ├─ CAR 重参考 ⭐
   ├─ 带通滤波
   └─ 生成 .mat 文件

4. 质量检查 (5分钟)
   ├─ 运行 check_data_quality.py
   ├─ 检查波形和功率谱
   └─ 确认数据合格

5. 模型训练 (1-3小时)
   ├─ 修改 main_subject_specific.py
   ├─ 运行训练
   └─ 评估准确率

6. 结果分析
   └─ 目标准确率: 75-88%
```

### 关键注意事项

| 阶段 | 关键点 | 重要性 |
|------|--------|--------|
| **硬件** | 阻抗 < 10 kΩ | ⭐⭐⭐⭐⭐ |
| **采集** | 想象生动、具体 | ⭐⭐⭐⭐⭐ |
| **预处理** | CAR 重参考 | ⭐⭐⭐⭐⭐ |
| **训练** | 数据量充足 | ⭐⭐⭐⭐ |

### 参考文献

1. Zhao, W., et al. (2024). CTNet: a convolutional transformer network for EEG-based motor imagery classification. *Scientific Reports*, 14, 20237.
2. BCI Competition IV: https://www.bbci.de/competition/iv/
3. OpenBCI Documentation: https://docs.openbci.com/
4. MNE-Python: https://mne.tools/

---

**祝你实验顺利！如有问题，欢迎随时询问。**

*最后更新: 2025-01-18*
