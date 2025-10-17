#!/usr/bin/env python3
"""
CTNet 数据集下载脚本
自动下载 BCI Competition IV-2a 和 IV-2b 数据集及标签
"""

import os
import urllib.request
import zipfile
from pathlib import Path


def download_file(url, filepath, description=""):
    """下载文件并显示进度"""
    if os.path.exists(filepath):
        print(f"✓ {os.path.basename(filepath)} 已存在，跳过")
        return True

    try:
        print(f"下载 {description or os.path.basename(filepath)}...")

        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100.0 / total_size, 100)
            print(f"\r  进度: {percent:.1f}%", end='', flush=True)

        urllib.request.urlretrieve(url, filepath, reporthook=report_progress)
        print()  # 换行
        return True
    except Exception as e:
        print(f"\n警告: {os.path.basename(filepath)} 下载失败 - {e}")
        return False


def main():
    print("=" * 50)
    print("CTNet 数据集下载脚本")
    print("=" * 50)
    print()

    # 创建目录
    print("创建数据目录...")
    dirs = ['BCICIV_2a_gdf', 'BCICIV_2b_gdf', 'true_labels']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
    print("目录创建完成！\n")

    # ========================================
    # 下载 BCI IV-2a 数据集
    # ========================================
    print("=" * 50)
    print("下载 BCI Competition IV-2a 数据集...")
    print("=" * 50)

    base_url_2a = "http://www.bbci.de/competition/iv/dataset_2a/"

    # 2a 训练和测试数据 (A01-A09)
    for i in range(1, 10):
        subject = f"A{i:02d}"

        # 训练数据
        filename_train = f"{subject}T.gdf"
        url_train = base_url_2a + filename_train
        filepath_train = os.path.join('BCICIV_2a_gdf', filename_train)
        download_file(url_train, filepath_train, f"{subject} 训练数据")

        # 测试数据
        filename_eval = f"{subject}E.gdf"
        url_eval = base_url_2a + filename_eval
        filepath_eval = os.path.join('BCICIV_2a_gdf', filename_eval)
        download_file(url_eval, filepath_eval, f"{subject} 测试数据")

    print("\n✓ BCI IV-2a 数据集下载完成！\n")

    # ========================================
    # 下载 BCI IV-2b 数据集
    # ========================================
    print("=" * 50)
    print("下载 BCI Competition IV-2b 数据集...")
    print("=" * 50)

    base_url_2b = "http://www.bbci.de/competition/iv/dataset_2b/"

    # 2b 训练和测试数据 (B01-B09, 每个受试者5个session)
    for i in range(1, 10):
        subject = f"B{i:02d}"

        for session in range(1, 6):
            session_id = f"{session:02d}"

            # 训练数据
            filename_train = f"{subject}{session_id}T.gdf"
            url_train = base_url_2b + filename_train
            filepath_train = os.path.join('BCICIV_2b_gdf', filename_train)
            download_file(url_train, filepath_train, f"{subject} Session {session} 训练")

            # 测试数据
            filename_eval = f"{subject}{session_id}E.gdf"
            url_eval = base_url_2b + filename_eval
            filepath_eval = os.path.join('BCICIV_2b_gdf', filename_eval)
            download_file(url_eval, filepath_eval, f"{subject} Session {session} 测试")

    print("\n✓ BCI IV-2b 数据集下载完成！\n")

    # ========================================
    # 下载标签文件
    # ========================================
    print("=" * 50)
    print("下载标签文件...")
    print("=" * 50)

    # 下载 2a 标签
    labels_2a_url = "https://www.bbci.de/competition/iv/results/ds2a/true_labels.zip"
    labels_2a_zip = os.path.join('true_labels', 'true_labels_2a.zip')

    if download_file(labels_2a_url, labels_2a_zip, "BCI IV-2a 标签"):
        print("解压 2a 标签...")
        with zipfile.ZipFile(labels_2a_zip, 'r') as zip_ref:
            zip_ref.extractall('true_labels')
        print("✓ 2a 标签完成")

    # 下载 2b 标签
    labels_2b_url = "https://www.bbci.de/competition/iv/results/ds2b/true_labels.zip"
    labels_2b_zip = os.path.join('true_labels', 'true_labels_2b.zip')

    if download_file(labels_2b_url, labels_2b_zip, "BCI IV-2b 标签"):
        print("解压 2b 标签...")
        with zipfile.ZipFile(labels_2b_zip, 'r') as zip_ref:
            zip_ref.extractall('true_labels')
        print("✓ 2b 标签完成")

    # ========================================
    # 完成
    # ========================================
    print()
    print("=" * 50)
    print("✓ 所有数据下载完成！")
    print("=" * 50)
    print()
    print("目录结构:")
    print("  BCICIV_2a_gdf/    - BCI IV-2a 数据集 (.gdf 文件)")
    print("  BCICIV_2b_gdf/    - BCI IV-2b 数据集 (.gdf 文件)")
    print("  true_labels/      - 标签文件")
    print()
    print("下一步: 运行预处理脚本")
    print("  python3 preprocessing_for_2a.py")
    print("  python3 preprocessing_for_2b.py")
    print()


if __name__ == "__main__":
    main()