#!/usr/bin/env python3
"""
使用 MOABB 库下载 BCI Competition IV 数据集
MOABB (Mother of All BCI Benchmarks) 是专门用于 BCI 数据集的 Python 库
"""

import os
import shutil
from pathlib import Path

print("=" * 60)
print("使用 MOABB 下载 BCI Competition IV 数据集")
print("=" * 60)
print()

# 检查 MOABB 是否安装
try:
    import moabb
    print(f"✓ MOABB 版本: {moabb.__version__}")
except ImportError:
    print("❌ MOABB 未安装")
    print()
    print("请先安装 MOABB:")
    print("  pip install moabb")
    print()
    exit(1)

from moabb.datasets import BNCI2014001, BNCI2014004

def download_datasets():
    """下载数据集"""

    # 创建目录
    dirs = ['BCICIV_2a_gdf', 'BCICIV_2b_gdf', 'true_labels']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)

    print()
    print("=" * 60)
    print("下载 BCI Competition IV-2a 数据集 (BNCI2014001)")
    print("=" * 60)
    print("数据集信息:")
    print("  - 9 个受试者")
    print("  - 4 类运动想象 (左手、右手、脚、舌头)")
    print("  - 22 个 EEG 通道")
    print("  - 250 Hz 采样率")
    print()

    try:
        dataset_2a = BNCI2014001()
        print("开始下载 2a 数据集...")

        # 获取数据，这会自动下载
        subjects = dataset_2a.subject_list
        print(f"受试者列表: {subjects}")

        # 下载所有受试者的数据
        for subject in subjects:
            print(f"\n下载受试者 {subject}...")
            data = dataset_2a.get_data([subject])
            print(f"✓ 受试者 {subject} 下载完成")

        print("\n✓ BCI IV-2a 数据集下载完成！")
        print(f"数据位置: {dataset_2a.data_path()}")

    except Exception as e:
        print(f"❌ 2a 数据集下载失败: {e}")

    print()
    print("=" * 60)
    print("下载 BCI Competition IV-2b 数据集 (BNCI2014004)")
    print("=" * 60)
    print("数据集信息:")
    print("  - 9 个受试者")
    print("  - 2 类运动想象 (左手、右手)")
    print("  - 3 个双极 EEG 通道")
    print("  - 250 Hz 采样率")
    print()

    try:
        dataset_2b = BNCI2014004()
        print("开始下载 2b 数据集...")

        # 获取数据
        subjects = dataset_2b.subject_list
        print(f"受试者列表: {subjects}")

        # 下载所有受试者的数据
        for subject in subjects:
            print(f"\n下载受试者 {subject}...")
            data = dataset_2b.get_data([subject])
            print(f"✓ 受试者 {subject} 下载完成")

        print("\n✓ BCI IV-2b 数据集下载完成！")
        print(f"数据位置: {dataset_2b.data_path()}")

    except Exception as e:
        print(f"❌ 2b 数据集下载失败: {e}")

    print()
    print("=" * 60)
    print("下载完成！")
    print("=" * 60)
    print()
    print("注意: MOABB 将数据下载到默认缓存目录")
    print("      通常在 ~/mnt_data/BNCI2014001 和 ~/mnt_data/BNCI2014004")
    print()
    print("下一步:")
    print("1. 查看 MOABB 数据格式")
    print("2. 根据需要修改预处理脚本以适配 MOABB 数据")
    print("3. 或者将数据转换为项目所需的 GDF 格式")
    print()


if __name__ == "__main__":
    try:
        download_datasets()
    except KeyboardInterrupt:
        print("\n\n❌ 下载已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
