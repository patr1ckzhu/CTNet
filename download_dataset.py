#!/usr/bin/env python3
"""
CTNet 数据集下载脚本
使用 MNE 库下载 BCI Competition IV-2a 和 IV-2b 数据集
"""

import os
import shutil
from pathlib import Path

try:
    import mne
    from mne.datasets import eegbci
    print("✓ MNE 库已安装")
except ImportError:
    print("错误: 需要安装 MNE 库")
    print("请运行: pip install mne")
    exit(1)


def download_with_mne():
    """使用 MNE 库下载数据集"""
    print("=" * 60)
    print("CTNet 数据集下载脚本 (使用 MNE)")
    print("=" * 60)
    print()

    print("注意: BCI Competition IV 数据集需要从官方网站手动下载")
    print("官方网站: https://www.bbci.de/competition/iv/")
    print()
    print("MNE 提供了类似的 EEG Motor Movement/Imagery 数据集")
    print("该数据集来自 PhysioNet，可以用于测试模型")
    print()

    choice = input("是否下载 PhysioNet Motor Movement/Imagery 数据集? (y/n): ")

    if choice.lower() == 'y':
        print("\n开始下载 PhysioNet 数据集...")
        print("这将下载 109 个受试者的数据，可能需要较长时间")
        print()

        # 下载第一个受试者的数据作为示例
        subject = 1
        runs = [4, 8, 12]  # Motor imagery runs

        print(f"下载受试者 {subject} 的运动想象数据...")
        mne.datasets.eegbci.load_data(subject, runs, update_path=True)
        print("✓ 示例数据下载完成")
        print()
        print(f"数据位置: {mne.datasets.eegbci.data_path()}")

    print()
    print("=" * 60)
    print("BCI Competition IV 数据集手动下载说明")
    print("=" * 60)
    print()


def print_manual_instructions():
    """打印手动下载说明"""

    print("由于 BCI Competition 网站需要同意条款才能下载，")
    print("请按以下步骤手动下载数据：")
    print()

    print("【方法1：官方网站下载】")
    print("-" * 60)
    print("1. 访问 BCI Competition IV 官网:")
    print("   https://www.bbci.de/competition/iv/")
    print()
    print("2. 找到并点击数据集链接:")
    print("   - Data set 2a (4-class motor imagery)")
    print("   - Data set 2b (2-class motor imagery)")
    print()
    print("3. 同意使用条款并下载数据")
    print()
    print("4. 将下载的文件放入对应目录:")
    print("   - 2a 数据 → BCICIV_2a_gdf/")
    print("   - 2b 数据 → BCICIV_2b_gdf/")
    print()

    print("【方法2：使用 MOABB 库下载】")
    print("-" * 60)
    print("MOABB (Mother of All BCI Benchmarks) 提供了自动下载功能")
    print()
    print("安装:")
    print("  pip install moabb")
    print()
    print("使用示例代码:")
    print("""
from moabb.datasets import BNCI2014001, BNCI2014004

# 下载 BCI Competition IV-2a 数据集
dataset_2a = BNCI2014001()
dataset_2a.download()

# 下载 BCI Competition IV-2b 数据集
dataset_2b = BNCI2014004()
dataset_2b.download()
""")
    print()

    print("【方法3：Google Drive / 百度网盘】")
    print("-" * 60)
    print("有些研究者会分享数据集链接，可以搜索:")
    print("  'BCI Competition IV-2a dataset download'")
    print("  'BCI Competition IV-2b dataset download'")
    print()

    print("【下载标签文件】")
    print("-" * 60)
    print("标签文件可以尝试从以下链接下载:")
    print("  2a: https://www.bbci.de/competition/iv/results/ds2a/true_labels.zip")
    print("  2b: https://www.bbci.de/competition/iv/results/ds2b/true_labels.zip")
    print()
    print("下载后解压到 true_labels/ 目录")
    print()

    # 创建目录
    print("=" * 60)
    print("准备目录结构...")
    print("=" * 60)
    dirs = ['BCICIV_2a_gdf', 'BCICIV_2b_gdf', 'true_labels']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"✓ 创建目录: {d}/")

    print()
    print("=" * 60)
    print("下一步")
    print("=" * 60)
    print("1. 下载数据文件到对应目录")
    print("2. 运行预处理脚本:")
    print("   python preprocessing_for_2a.py")
    print("   python preprocessing_for_2b.py")
    print("3. 运行训练:")
    print("   python main_subject_specific.py")
    print()


def main():
    try:
        download_with_mne()
        print_manual_instructions()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请查看手动下载说明:")
        print_manual_instructions()


if __name__ == "__main__":
    main()