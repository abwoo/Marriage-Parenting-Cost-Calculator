#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结婚生育成本计算器启动脚本
Marriage & Parenting Cost Calculator Launcher
"""

import sys
import os
import subprocess

def check_dependencies():
    """检查依赖是否已安装"""
    required_packages = ['customtkinter', 'matplotlib', 'numpy', 'Pillow']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'customtkinter':
                import customtkinter as ctk
            elif package == 'matplotlib':
                import matplotlib
            elif package == 'numpy':
                import numpy
            elif package == 'Pillow':
                import PIL
        except ImportError:
            missing_packages.append(package)

    return missing_packages

def install_dependencies(missing_packages):
    """安装缺失的依赖"""
    print(f"发现缺失的依赖包: {', '.join(missing_packages)}")
    print("正在自动安装...")

    try:
        for package in missing_packages:
            if package == 'customtkinter':
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'customtkinter'])
            else:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

        print("依赖包安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"安装依赖包失败: {e}")
        print("请手动运行: pip install -r requirements.txt")
        return False

def main():
    print("=" * 50)
    print("    💒 结婚生育成本计算器")
    print("    Marriage & Parenting Cost Calculator")
    print("=" * 50)

    # 检查依赖
    missing_packages = check_dependencies()
    if missing_packages:
        if not install_dependencies(missing_packages):
            input("按Enter键退出...")
            sys.exit(1)

    try:
        from marriage_calculator import MarriageCalculatorApp

        print("\n🚀 启动程序...")
        print("提示：如果界面显示异常，请尝试调整显示缩放比例")
        print("-" * 50)

        app = MarriageCalculatorApp()
        app.run()

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所需依赖包：pip install -r requirements.txt")
        input("按Enter键退出...")
        sys.exit(1)

    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()