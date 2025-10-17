#!/usr/bin/env python3
"""
将 MOABB 下载的数据转换为 CTNet 项目所需的 GDF 格式
并复制到对应的目录中
"""

import os
import shutil
from pathlib import Path

try:
    from moabb.datasets import BNCI2014_001, BNCI2014_004
    import mne
    print("✓ 所需库已安装")
except ImportError as e:
    print(f"❌ 缺少必要的库: {e}")
    print("请安装: pip install moabb mne")
    exit(1)


def find_moabb_data_path():
    """查找 MOABB 数据存储路径"""
    # MOABB 默认存储路径
    possible_paths = [
        Path.home() / "mnt_data",
        Path.home() / "mne_data",
        Path("~/mnt_data").expanduser(),
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def copy_gdf_files():
    """复制 GDF 文件到项目目录"""

    print("=" * 60)
    print("将 MOABB 数据转换并复制到项目目录")
    print("=" * 60)
    print()

    # 创建目标目录
    target_2a = Path("BCICIV_2a_gdf")
    target_2b = Path("BCICIV_2b_gdf")
    target_labels = Path("true_labels")

    target_2a.mkdir(exist_ok=True)
    target_2b.mkdir(exist_ok=True)
    target_labels.mkdir(exist_ok=True)

    # 查找 MOABB 数据路径
    moabb_base = find_moabb_data_path()

    if moabb_base is None:
        print("❌ 未找到 MOABB 数据目录")
        print("请先运行 download_with_moabb.py 下载数据")
        return

    print(f"✓ 找到 MOABB 数据目录: {moabb_base}")
    print()

    # ========================================
    # 处理 2a 数据集
    # ========================================
    print("=" * 60)
    print("处理 BCI Competition IV-2a 数据集")
    print("=" * 60)

    # BNCI2014_001 对应 BCI Competition IV-2a
    dataset_2a_path = moabb_base / "MNE-BNCI2014_001-data"

    if dataset_2a_path.exists():
        print(f"源目录: {dataset_2a_path}")

        # 查找并复制 GDF 文件
        gdf_files = list(dataset_2a_path.rglob("*.gdf"))

        if gdf_files:
            print(f"找到 {len(gdf_files)} 个 GDF 文件")

            for gdf_file in gdf_files:
                # 生成目标文件名 (A01T.gdf, A01E.gdf 等)
                target_file = target_2a / gdf_file.name

                if not target_file.exists():
                    print(f"  复制: {gdf_file.name}")
                    shutil.copy2(gdf_file, target_file)
                else:
                    print(f"  ✓ 已存在: {gdf_file.name}")

            print(f"\n✓ 2a 数据集处理完成！")
            print(f"  文件位置: {target_2a.absolute()}")
        else:
            print("⚠ 未找到 GDF 文件，尝试列出目录内容...")
            print(f"目录内容: {list(dataset_2a_path.iterdir())[:5]}")
    else:
        print(f"❌ 未找到 2a 数据集目录: {dataset_2a_path}")

    print()

    # ========================================
    # 处理 2b 数据集
    # ========================================
    print("=" * 60)
    print("处理 BCI Competition IV-2b 数据集")
    print("=" * 60)

    # BNCI2014_004 对应 BCI Competition IV-2b
    dataset_2b_path = moabb_base / "MNE-BNCI2014_004-data"

    if dataset_2b_path.exists():
        print(f"源目录: {dataset_2b_path}")

        # 查找并复制 GDF 文件
        gdf_files = list(dataset_2b_path.rglob("*.gdf"))

        if gdf_files:
            print(f"找到 {len(gdf_files)} 个 GDF 文件")

            for gdf_file in gdf_files:
                target_file = target_2b / gdf_file.name

                if not target_file.exists():
                    print(f"  复制: {gdf_file.name}")
                    shutil.copy2(gdf_file, target_file)
                else:
                    print(f"  ✓ 已存在: {gdf_file.name}")

            print(f"\n✓ 2b 数据集处理完成！")
            print(f"  文件位置: {target_2b.absolute()}")
        else:
            print("⚠ 未找到 GDF 文件，尝试列出目录内容...")
            print(f"目录内容: {list(dataset_2b_path.iterdir())[:5]}")
    else:
        print(f"❌ 未找到 2b 数据集目录: {dataset_2b_path}")

    print()

    # ========================================
    # 完成
    # ========================================
    print("=" * 60)
    print("数据准备完成！")
    print("=" * 60)
    print()
    print("目录结构:")
    print(f"  {target_2a}/ - 包含 {len(list(target_2a.glob('*.gdf')))} 个文件")
    print(f"  {target_2b}/ - 包含 {len(list(target_2b.glob('*.gdf')))} 个文件")
    print()
    print("下一步:")
    print("  1. 运行预处理脚本:")
    print("     python preprocessing_for_2a.py")
    print("     python preprocessing_for_2b.py")
    print()
    print("  2. 如果需要标签文件，请手动下载:")
    print("     2a: https://www.bbci.de/competition/iv/results/ds2a/true_labels.zip")
    print("     2b: https://www.bbci.de/competition/iv/results/ds2b/true_labels.zip")
    print()


def check_data_availability():
    """检查数据是否已经下载"""
    print("=" * 60)
    print("检查 MOABB 数据下载状态")
    print("=" * 60)
    print()

    try:
        # 检查 2a 数据集
        dataset_2a = BNCI2014_001()
        print(f"✓ 2a 数据集: {len(dataset_2a.subject_list)} 个受试者")

        # 检查 2b 数据集
        dataset_2b = BNCI2014_004()
        print(f"✓ 2b 数据集: {len(dataset_2b.subject_list)} 个受试者")
        print()

        return True
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        print("请先运行 download_with_moabb.py 下载数据")
        return False


if __name__ == "__main__":
    try:
        if check_data_availability():
            copy_gdf_files()
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
