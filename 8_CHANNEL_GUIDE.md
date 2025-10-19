# 8通道CTNet使用指南 - 适配ADS1299硬件

## 📋 目录

1. [背景说明](#背景说明)
2. [文件说明](#文件说明)
3. [运行步骤](#运行步骤)
4. [详细说明](#详细说明)
5. [结果对比](#结果对比)
6. [常见问题](#常见问题)

---

## 🎯 背景说明

### 为什么需要8通道版本？

你的毕设基于 **ADS1299** 硬件开发，该芯片最多支持 **8个EEG电极**，而BCI Competition IV-2a数据集有 **22个电极**。

为了模拟实际硬件限制，我们需要：
1. 从22个电极中**自动选择**最优的8个
2. 使用这8个电极**重新训练**CTNet模型
3. **对比**22通道 vs 8通道的性能差异

这样可以评估你的硬件系统在实际应用中的预期性能。

---

## 📁 文件说明

### 新创建的文件

| 文件名 | 功能 | 用途 |
|--------|------|------|
| `channel_selector.py` | 自动通道选择器 | 找出最优的8个通道 |
| `main_8_channels.py` | 8通道训练脚本 | 使用8通道训练CTNet |
| `8_CHANNEL_GUIDE.md` | 本文档 | 使用说明 |

### 生成的文件

| 文件名 | 内容 |
|--------|------|
| `selected_channels.txt` | 通道选择结果 |
| `channel_selection_results.png` | 可视化图表 |
| `A_8channels_heads_2_depth_6/` | 8通道训练结果目录 |

---

## 🚀 运行步骤

### 步骤1: 安装依赖 (如果缺少)

```bash
pip install scikit-learn matplotlib seaborn
```

### 步骤2: 运行通道选择器

```bash
cd "/Users/patrick/Desktop/EEE/Fourth Year/BCI Project/CTNet"
python channel_selector.py
```

**会发生什么？**

程序会执行以下操作：

1. **方法1 (先验知识)**: 基于运动想象研究，自动选择标准电极
   - 运行时间: <1秒
   - 输出: 推荐的8个电极 (如 C3, C4, Cz, FCz, ...)

2. **方法2 (互信息)** ⭐ **推荐**:  数据驱动，计算每个电极与标签的相关性
   - 运行时间: 约1-2分钟
   - 输出:
     - 22个电极的互信息得分排名
     - Top 8 最重要的电极
     - 可视化图表

3. **方法3 (RFE)**: 基于模型的递归特征消除
   - 运行时间: 5-10分钟 (可选)
   - 会询问是否执行: 输入 `y` 执行，输入 `n` 跳过

**示例输出：**

```
============================================================
方法2: 基于互信息的通道选择 (数据驱动)
============================================================

📊 正在加载数据...
   受试者 1: 288 trials
   受试者 2: 288 trials
   ...
   受试者 9: 288 trials

📈 总数据: 2592 trials, 22 channels, 1000 timepoints

⚙️  计算通道特征...
⚙️  计算互信息...

✅ 互信息排名 (Top 8):
排名   通道     索引   互信息        归一化得分
------------------------------------------------------------
1      C3       7      0.245610     100.00%
2      C4       11     0.238452     97.08%
3      Cz       9      0.221387     90.13%
4      CP1      14     0.198765     80.92%
5      CP2      16     0.187234     76.23%
6      FC3      1      0.176543     71.88%
7      FC4      5      0.165432     67.35%
8      FCz      3      0.154321     62.83%

💡 请将这些索引用于 main_8_channels.py
```

**你会看到:**
- 终端输出各方法的结果
- 生成 `selected_channels.txt` 文件
- 生成 `channel_selection_results.png` 图表

### 步骤3: 更新8通道训练脚本

打开 `main_8_channels.py`，找到第 **48-51 行**:

```python
# 当前默认值
SELECTED_CHANNEL_INDICES = [7, 11, 9, 3, 14, 16, 1, 4]
SELECTED_CHANNEL_NAMES = ['C3', 'C4', 'Cz', 'FCz', 'CP1', 'CP2', 'FC3', 'FC2']
```

**替换为步骤2中方法2的输出结果**。例如:

```python
# 从 channel_selector.py 的输出复制
SELECTED_CHANNEL_INDICES = [7, 11, 9, 14, 16, 1, 5, 3]  # 示例
SELECTED_CHANNEL_NAMES = ['C3', 'C4', 'Cz', 'CP1', 'CP2', 'FC3', 'FC4', 'FCz']
```

### 步骤4: 运行8通道训练

```bash
python main_8_channels.py
```

**运行时间:** 约 2-3 小时 (取决于GPU，9个受试者，每个约1000 epochs)

**输出:**
```
============================================================
8-Channel CTNet Training (Simulating ADS1299)
Selected Channels: [7, 11, 9, 14, 16, 1, 5, 3]
Channel Names: ['C3', 'C4', 'Cz', 'CP1', 'CP2', 'FC3', 'FC4', 'FCz']
============================================================

Model Architecture (8-Channel Version)
============================================================
----------------------------------------------------------------
        Layer (type)               Output Shape         Param #
================================================================
            Conv2d-1            [1, 8, 8, 1000]             512
       BatchNorm2d-2            [1, 8, 8, 1000]              16
            Conv2d-3           [1, 16, 1, 1000]           1,024
       BatchNorm2d-4           [1, 16, 1, 1000]              32
...
================================================================
Total params: 25,684
Trainable params: 25,684
Non-trainable params: 0
----------------------------------------------------------------

seed is 1234
Subject 1
   原始数据形状: (288, 22, 1000)
   选择8通道后: (288, 8, 1000)
-------------------- train size： (288, 1, 8, 1000) test size： (288, 1, 8, 1000)

1_992 train_acc: 0.9876 train_loss: 0.045678   val_acc: 0.8542 val_loss: 0.4567890
epoch:  992     The test accuracy is: 0.8472222222222222
...
```

### 步骤5: 查看结果

训练完成后，查看结果目录:

```bash
cd A_8channels_heads_2_depth_6/
ls
```

你会看到:
- `result_metric.xlsx` - 所有受试者的准确率、Kappa等指标
- `process_train.xlsx` - 训练过程 (每个epoch的loss和acc)
- `pred_true.xlsx` - 预测值vs真实值
- `model_*.pth` - 9个受试者的模型权重

---

## 📊 详细说明

### 通道选择方法对比

#### 方法1: 先验知识
**原理:** 基于神经科学研究，运动想象主要激活运动皮层区域

**优点:**
- ✅ 快速 (<1秒)
- ✅ 不需要数据
- ✅ 结果可解释

**缺点:**
- ❌ 可能不是最优组合
- ❌ 未考虑数据特性

**适用场景:** 快速原型开发，没有训练数据

---

#### 方法2: 互信息 ⭐ 推荐
**原理:** 计算每个电极与运动想象标签的统计相关性

**公式:**
```
MI(Channel, Label) = ∑∑ p(c,l) log(p(c,l) / (p(c)p(l)))
```

**优点:**
- ✅ 数据驱动，客观
- ✅ 计算快速 (1-2分钟)
- ✅ 不依赖模型
- ✅ 考虑了数据的实际分布

**缺点:**
- ❌ 需要训练数据
- ❌ 只考虑单个通道，未考虑通道间交互

**适用场景:**
- 有充足训练数据
- 需要客观的选择依据
- **推荐用于你的毕设**

---

#### 方法3: 递归特征消除 (RFE)
**原理:** 训练随机森林模型，逐步移除不重要的电极

**优点:**
- ✅ 考虑通道间交互
- ✅ 基于分类性能

**缺点:**
- ❌ 计算慢 (5-10分钟)
- ❌ 依赖模型选择
- ❌ 可能过拟合训练数据

**适用场景:**
- 计算资源充足
- 需要最优性能
- 研究对比

---

### 代码改动说明

#### 原始版本 (22通道)
```python
# main_subject_specific.py
class PatchEmbeddingCNN(nn.Module):
    def __init__(self, number_channel=22, ...):  # 硬编码22
        ...
        nn.Conv2d(f1, f2, (number_channel, 1), ...)  # 深度卷积
```

#### 8通道版本
```python
# main_8_channels.py
class PatchEmbeddingCNN(nn.Module):
    def __init__(self, number_channel=8, ...):  # 改为8
        ...
        nn.Conv2d(f1, f2, (number_channel, 1), ...)  # 自动适配8通道
```

**关键修改点:**

1. **数据加载 (第569-582行)**:
```python
def get_source_data(self):
    # 加载原始22通道数据
    train_data, train_label, test_data, test_label = load_data_evaluate(...)

    # 🔥 新增: 通道选择
    train_data = select_channels(train_data, self.selected_channels)
    test_data = select_channels(test_data, self.selected_channels)

    # (288, 22, 1000) -> (288, 8, 1000)
```

2. **模型初始化 (第408行)**:
```python
self.number_channel = 8  # 固定为8通道
```

3. **数据增强 (第526-544行)**:
```python
# S&R增强自动适配8通道
tmp_aug_data = np.zeros((number_records_by_augmentation, 1, self.number_channel, 1000))
# self.number_channel = 8
```

**其他未改动的部分:**
- ✅ Transformer架构 (与通道数无关)
- ✅ 训练循环 (完全相同)
- ✅ 损失函数 (完全相同)
- ✅ 优化器 (完全相同)

---

## 📈 结果对比

### 预期性能下降

根据文献研究，通道数减少通常会导致性能下降:

| 配置 | 平均准确率 | 预期下降 |
|------|-----------|---------|
| 22通道 (原始) | 82.95% | - |
| 8通道 (方法2) | **78-81%** | 2-5% ⬇️ |
| 8通道 (方法1) | 76-79% | 4-7% ⬇️ |

**为什么会下降？**
- 丢失了部分空间信息
- 某些受试者可能依赖被舍弃的电极
- 通道间互补信息减少

**如何弥补？**
1. 使用更好的通道选择方法 (方法2)
2. 增加数据增强
3. 调整模型超参数 (如增加Transformer深度)
4. 延长训练时间

---

## ❓ 常见问题

### Q1: 必须按顺序运行吗？

**A:** 是的。必须先运行 `channel_selector.py` 获取最优通道，再更新 `main_8_channels.py` 中的通道索引，最后运行训练。

---

### Q2: 可以跳过通道选择，直接使用默认值吗？

**A:** 可以，但**不推荐**。默认值是基于先验知识的通用配置，可能不是你数据集的最优选择。运行通道选择只需1-2分钟，建议执行。

---

### Q3: 三种方法选出的通道会一样吗？

**A:** 不完全一样，但**通常有60-80%重叠**。核心通道 (C3, C4, Cz) 几乎总会被选中，差异主要在辅助通道 (FC3, CP1等)。

运行后查看 `compare_methods()` 的输出可以看到重叠情况。

---

### Q4: 训练8通道版本需要多久？

**A:**
- 单个受试者: 约15-20分钟 (1000 epochs, GPU)
- 全部9个受试者: 约2.5-3小时

与22通道版本**时间相近**，因为计算瓶颈在Transformer，而非CNN通道数。

---

### Q5: 8通道模型能用于22通道数据吗？

**A:** 不能。训练的8通道模型只能用于相同8个通道的新数据。如果你的ADS1299使用不同的8个电极，需要重新选择通道并训练。

---

### Q6: 如何为我的ADS1299硬件确定电极位置？

**推荐流程:**

1. **运行通道选择器** → 获取最优8通道名称 (如 C3, C4, Cz, ...)
2. **查阅10-20国际系统图** → 确定这些电极的头皮位置
3. **设计电极帽布局** → 将这8个电极布置在ADS1299的8个通道上
4. **记录映射关系** → 哪个电极连接到ADS1299的哪个通道

**示例映射:**
```
ADS1299通道  →  电极位置
Channel 1    →  C3  (左运动皮层)
Channel 2    →  C4  (右运动皮层)
Channel 3    →  Cz  (中央运动皮层)
Channel 4    →  FCz (前中央)
Channel 5    →  CP1 (中央顶叶左)
Channel 6    →  CP2 (中央顶叶右)
Channel 7    →  FC3 (前中央左)
Channel 8    →  FC4 (前中央右)
```

---

### Q7: 如果我想测试6个或10个通道怎么办？

**A:** 修改 `channel_selector.py` 的第31行:

```python
selector = ChannelSelector(
    data_dir='../mymat_raw/',
    dataset_type='A',
    n_channels=10  # 改为你想要的通道数
)
```

然后相应修改 `main_8_channels.py` 中的模型配置。

---

### Q8: 能否同时对比22通道和8通道的结果？

**A:** 可以。建议的流程:

```bash
# 1. 运行原始22通道版本
python main_subject_specific.py
# 结果保存在: A_heads_2_depth_6/

# 2. 运行8通道版本
python main_8_channels.py
# 结果保存在: A_8channels_heads_2_depth_6/

# 3. 对比两个目录的 result_metric.xlsx
```

创建对比脚本:
```python
import pandas as pd

# 读取结果
df_22ch = pd.read_excel('A_heads_2_depth_6/result_metric.xlsx')
df_8ch = pd.read_excel('A_8channels_heads_2_depth_6/result_metric.xlsx')

# 对比
print("22通道平均准确率:", df_22ch['accuray'].iloc[-2])
print("8通道平均准确率:", df_8ch['accuray'].iloc[-2])
print("性能下降:", df_22ch['accuray'].iloc[-2] - df_8ch['accuray'].iloc[-2])
```

---

### Q9: 通道选择结果如何可视化？

**A:** `channel_selector.py` 自动生成 `channel_selection_results.png`，包含:

1. **条形图**: 显示22个通道的互信息得分，红色标注选中的8个
2. **热力图**: 按重要性排序的通道排名

你也可以调用:
```python
selector.visualize_mi_scores(save_path='my_channels.png')
```

---

### Q10: 出现 CUDA out of memory 错误怎么办？

**A:** 8通道版本显存占用**更小**，通常不会出现此问题。如果仍然出现:

```python
# 修改 main_8_channels.py 的 batch_size
batch_size = 72  # 改为 → 36 或 48
```

---

## 🔧 高级用法

### 1. 保存通道选择结果供后续使用

```python
# 在 channel_selector.py 中
import pickle

# 运行选择
selector = ChannelSelector(...)
indices, names = selector.method2_mutual_information()

# 保存
with open('best_channels.pkl', 'wb') as f:
    pickle.dump({'indices': indices, 'names': names}, f)

# 在 main_8_channels.py 中加载
with open('best_channels.pkl', 'rb') as f:
    channels = pickle.load(f)
    SELECTED_CHANNEL_INDICES = channels['indices']
```

---

### 2. 批量测试不同通道组合

```python
# test_different_channels.py
channel_sets = [
    [7, 11, 9, 3, 14, 16, 1, 4],   # 方法1
    [7, 11, 9, 14, 16, 1, 5, 3],   # 方法2
    [7, 11, 9, 13, 17, 2, 4, 15],  # 方法3
]

for i, channels in enumerate(channel_sets):
    SELECTED_CHANNEL_INDICES = channels
    result = main(f"Test_Set_{i+1}", selected_channels=channels)
    print(f"Set {i+1} Accuracy:", result['accuray'].mean())
```

---

### 3. 可视化不同受试者的最优通道

```python
# 为每个受试者单独选择最优8通道
for subject in range(1, 10):
    selector = ChannelSelector(...)
    indices, names = selector.method2_mutual_information(
        subject=subject,
        use_all_subjects=False  # 仅使用该受试者数据
    )
    print(f"Subject {subject} best channels:", names)
```

---

## 📚 参考资料

1. **10-20国际电极系统**: https://en.wikipedia.org/wiki/10%E2%80%9320_system_(EEG)
2. **ADS1299数据手册**: https://www.ti.com/product/ADS1299
3. **CTNet原论文**: Zhao et al. (2024) Scientific Reports
4. **运动想象BCI综述**: Pfurtscheller & Neuper (2001) Clinical Neurophysiology

---

## 💡 实验建议

### 用于毕设报告

1. **实验设计**:
   - 对比22通道 vs 8通道的性能
   - 测试不同通道选择方法
   - 分析哪些受试者对通道减少更敏感

2. **可视化**:
   - 通道重要性热力图
   - 22 vs 8通道准确率对比图
   - 头皮电极布局图

3. **讨论**:
   - 为什么某些通道更重要？
   - ADS1299的8通道限制是否可接受？
   - 如何优化硬件-算法协同设计？

---

## ✅ 总结

### 快速开始 (5分钟)

```bash
# 1. 选择通道
python channel_selector.py
# 输出: 8个最优通道索引

# 2. 复制索引到 main_8_channels.py 第48行

# 3. 开始训练
python main_8_channels.py
```

### 完整流程 (3小时)

1. ✅ 运行通道选择 (2分钟)
2. ✅ 更新训练脚本 (1分钟)
3. ✅ 训练8通道模型 (2.5小时)
4. ✅ 对比22通道结果 (5分钟)
5. ✅ 撰写实验报告

---

**祝实验顺利！如有问题欢迎提问。**

*Last updated: 2025-10-19*