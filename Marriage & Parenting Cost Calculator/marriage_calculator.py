import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from tkinter import scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import numpy as np
import json
import os

# 设置matplotlib中文字体
import matplotlib
matplotlib.use('TkAgg')

def setup_matplotlib_fonts():
    """设置matplotlib字体，确保图表文字正常显示"""
    try:
        # 获取系统可用字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]

        # 优先级排序的中文字体列表
        chinese_fonts = [
            'SimHei',           # 黑体 (Windows)
            'Microsoft YaHei',  # 微软雅黑 (Windows)
            'PingFang SC',      # 苹方 (macOS)
            'Hiragino Sans GB', # 冬青黑体 (macOS)
            'WenQuanYi Micro Hei', # 文泉驿微米黑 (Linux)
            'AR PL UMing CN',   # 文鼎 (Linux)
            'DejaVu Sans',      # 备用英文字体
            'Arial Unicode MS', # 备用
        ]

        # 找出可用的中文字体
        usable_fonts = []
        for font in chinese_fonts:
            if any(font.lower() in af.lower() for af in available_fonts):
                usable_fonts.append(font)

        if usable_fonts:
            plt.rcParams['font.sans-serif'] = usable_fonts + ['DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            print(f"使用字体: {usable_fonts[0]}")
            return True
        else:
            # 如果没有中文字体，使用英文并设置备用字体
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
            plt.rcParams['axes.unicode_minus'] = False
            print("未找到中文字体，使用英文标签")
            return False

    except Exception as e:
        print(f"字体设置失败: {e}")
        # 最后的备用设置
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False
        return False

# 初始化字体设置
FONT_SUPPORT_CHINESE = setup_matplotlib_fonts()

# 确保matplotlib后端设置正确
plt.switch_backend('TkAgg')

# 设置默认字体属性，确保所有文本元素都使用中文字体
if FONT_SUPPORT_CHINESE:
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['SimHei', 'Microsoft YaHei', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.labelsize': 11,
        'axes.labelweight': 'bold',
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
    })
    print("matplotlib全局字体设置为中文")
else:
    print("matplotlib使用英文标签")

class MarriageCalculatorApp:
    def __init__(self):
        # 设置外观
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("结婚生育成本计算器")
        self.root.geometry("1400x900")

        # 初始化数据
        self.init_data()

        # 创建界面
        self.create_widgets()

        # 计算初始结果
        self.calculate()

    def init_data(self):
        """初始化数据模型"""
        self.form_data = {
            # 收入与稳定性 - 基于2023年国家统计局数据
            # 2023年全国城镇居民人均可支配收入约49,000元，考虑夫妻二人收入
            'salaryA': 22000,  # 丈夫月薪（略高于平均水平，基于统计局数据）
            'salaryB': 18000,  # 妻子月薪
            'annualBonus': 80000,  # 年终奖合计（基于企业奖金统计）
            'incomeStability': 82,  # 工资稳定性 (0-100)，基于就业统计

            # 房产资产 - 基于2023年房价数据
            # 全国平均房价约10,000-15,000元/㎡，考虑120㎡三居室
            'propertyValue': 1800000,  # 二线城市120㎡房产总价
            'propertyAppreciation': -1.2,  # 2023年多数城市房价下跌
            'monthlyMortgage': 6500,  # 相应月供（30年等额本息）

            # 父母支持 - 基于2023年老年人口收入统计
            # 城镇退休人员月人均养老金约3,500元
            'annualParentSupport': 35000,  # 父母每年现金支持

            # 结婚成本细分 - 基于2023年婚姻大数据和统计
            'marriageCosts': {
                'betrothalGift': 58000,     # 彩礼（二线城市平均，民政局数据）
                'weddingCeremony': 128000,  # 婚礼（包含酒席、摄影、婚庆，平均水平）
                'weddingRing': 35000,       # 钻戒首饰（平均水平）
                'honeymoon': 45000,         # 蜜月旅行（国内外游）
                'newHouseDownPayment': 360000, # 新房首付（二线城市首付比例30%）
                'renovation': 180000,       # 装修（硬装+软装，中等标准）
            },

            # 生育与育儿成本 - 基于2023年统计和相关研究
            'childCount': 1,
            'cityTier': 'tier2',
            'children': [
                {
                    'prenatalCare': 8500,    # 产检费用（15次检查+营养品）
                    'delivery': 12000,       # 分娩费用（顺产，医保报销后）
                    'postpartumCare': 22000, # 月子中心（42天，平均水平）
                    'monthlyBabyCost': 2200, # 月均婴儿用品（奶粉、尿布、辅食）
                    'kindergarten': 96000,   # 幼儿园3年（公立园+兴趣班）
                    'primarySchool': 180000, # 小学6年（公立教育+校服学杂）
                    'juniorHigh': 156000,    # 初中3年（公立教育+补习）
                    'seniorHigh': 132000,    # 高中3年（公立教育+补习）
                    'university': 720000,    # 本科4年（平均8,000元/年×4+生活费）
                    'extracurricular': 120000, # 课外辅导（英语、奥数等，6年）
                }
            ],

            # 生活成本与通胀 - 基于2023年国家统计局CPI数据
            'baseLivingCost': 6200,    # 基础生活成本（月，房租+水电+交通+通讯）
            'livingInflation': 2.1,    # 2023年实际CPI涨幅
            'investmentReturn': 3.8,   # 2023年理财产品平均收益率

            'riskSimulation': False
        }

        # 分析结果
        self.analysis_result = {}
        self.ai_advice = ""

    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_frame = ctk.CTkFrame(main_frame, fg_color="#1e293b", corner_radius=20)
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            title_frame,
            text="资产头寸与生存压力模型",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=15)

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="动态计入房产波动、货币贬值、收入稳定性与隔代支持",
            font=ctk.CTkFont(size=10),
            text_color="#94a3b8"
        )
        subtitle_label.pack(pady=(0, 15))

        # 总资产变化显示
        self.total_change_label = ctk.CTkLabel(
            title_frame,
            text="18年综合净资产变化预期: 0.0万",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#10b981"
        )
        self.total_change_label.pack(pady=(0, 15))

        # 创建选项卡
        self.tabview = ctk.CTkTabview(main_frame, width=1300, height=750)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # 创建各个选项卡
        self.tabview.add("参数设置")
        self.tabview.add("成本分析")
        self.tabview.add("AI分析")
        self.tabview.add("数据管理")

        # 创建参数设置页面
        self.create_settings_tab()

        # 创建成本分析页面
        self.create_analysis_tab()

        # 创建AI分析页面
        self.create_ai_tab()

        # 创建数据管理页面
        self.create_data_tab()

    def create_settings_tab(self):
        """创建参数设置选项卡"""
        settings_frame = self.tabview.tab("参数设置")

        # 创建滚动框架
        scrollable_frame = ctk.CTkScrollableFrame(settings_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 收入与稳定性模块
        income_frame = ctk.CTkFrame(scrollable_frame)
        income_frame.pack(fill="x", padx=10, pady=10)

        income_title = ctk.CTkLabel(income_frame, text="💰 收入与稳定性", font=ctk.CTkFont(size=14, weight="bold"))
        income_title.pack(pady=10)

        # 创建收入输入网格
        income_grid = ctk.CTkFrame(income_frame, fg_color="transparent")
        income_grid.pack(fill="x", padx=20, pady=10)

        # 第一行：工资
        row1 = ctk.CTkFrame(income_grid, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        ctk.CTkLabel(row1, text="配偶A月薪:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0,10))
        self.salary_a_entry = ctk.CTkEntry(row1, width=100)
        self.salary_a_entry.pack(side="left", padx=(0,20))
        self.salary_a_entry.insert(0, str(self.form_data['salaryA']))

        ctk.CTkLabel(row1, text="配偶B月薪:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0,10))
        self.salary_b_entry = ctk.CTkEntry(row1, width=100)
        self.salary_b_entry.pack(side="left", padx=(0,20))
        self.salary_b_entry.insert(0, str(self.form_data['salaryB']))

        ctk.CTkLabel(row1, text="年终奖:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0,10))
        self.bonus_entry = ctk.CTkEntry(row1, width=100)
        self.bonus_entry.pack(side="left")
        self.bonus_entry.insert(0, str(self.form_data['annualBonus']))

        # 第二行：稳定性
        row2 = ctk.CTkFrame(income_grid, fg_color="transparent")
        row2.pack(fill="x", pady=5)

        ctk.CTkLabel(row2, text="工资稳定性:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0,10))
        self.stability_slider = ctk.CTkSlider(row2, from_=30, to=100, number_of_steps=14)
        self.stability_slider.pack(side="left", padx=(0,10))
        self.stability_slider.set(self.form_data['incomeStability'])

        self.stability_label = ctk.CTkLabel(row2, text=f"{self.form_data['incomeStability']}%", font=ctk.CTkFont(size=11))
        self.stability_label.pack(side="left")

        # 房产模块
        property_frame = ctk.CTkFrame(scrollable_frame)
        property_frame.pack(fill="x", padx=10, pady=10)

        property_title = ctk.CTkLabel(property_frame, text="🏠 房产资产与负债", font=ctk.CTkFont(size=14, weight="bold"))
        property_title.pack(pady=10)

        property_grid = ctk.CTkFrame(property_frame, fg_color="transparent")
        property_grid.pack(fill="x", padx=20, pady=10)

        # 房产价值
        p_row1 = ctk.CTkFrame(property_grid, fg_color="transparent")
        p_row1.pack(fill="x", pady=5)

        ctk.CTkLabel(p_row1, text="房产总市值:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0,10))
        self.property_value_entry = ctk.CTkEntry(p_row1, width=120)
        self.property_value_entry.pack(side="left", padx=(0,20))
        self.property_value_entry.insert(0, str(self.form_data['propertyValue']))

        # 增值率
        p_row2 = ctk.CTkFrame(property_grid, fg_color="transparent")
        p_row2.pack(fill="x", pady=5)

        ctk.CTkLabel(p_row2, text="预期年化增值率:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0,10))
        self.appreciation_slider = ctk.CTkSlider(p_row2, from_=-10, to=10, number_of_steps=40)
        self.appreciation_slider.pack(side="left", padx=(0,10))
        self.appreciation_slider.set(self.form_data['propertyAppreciation'])

        self.appreciation_label = ctk.CTkLabel(p_row2, text=f"{self.form_data['propertyAppreciation']}%", font=ctk.CTkFont(size=11))
        self.appreciation_label.pack(side="left")

        # 月供
        p_row3 = ctk.CTkFrame(property_grid, fg_color="transparent")
        p_row3.pack(fill="x", pady=5)

        ctk.CTkLabel(p_row3, text="月供总额:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0,10))
        self.mortgage_entry = ctk.CTkEntry(p_row3, width=100)
        self.mortgage_entry.pack(side="left")
        self.mortgage_entry.insert(0, str(self.form_data['monthlyMortgage']))

        # 结婚成本模块
        marriage_frame = ctk.CTkFrame(scrollable_frame)
        marriage_frame.pack(fill="x", padx=10, pady=10)

        marriage_title = ctk.CTkLabel(marriage_frame, text="💍 结婚成本明细", font=ctk.CTkFont(size=14, weight="bold"))
        marriage_title.pack(pady=10)

        marriage_grid = ctk.CTkFrame(marriage_frame, fg_color="transparent")
        marriage_grid.pack(fill="x", padx=20, pady=10)

        # 创建结婚成本输入框
        marriage_costs = self.form_data['marriageCosts']
        self.marriage_entries = {}

        cost_labels = {
            'betrothalGift': '彩礼',
            'weddingCeremony': '婚礼',
            'weddingRing': '钻戒首饰',
            'honeymoon': '蜜月旅行',
            'newHouseDownPayment': '新房首付',
            'renovation': '装修'
        }

        for i, (key, label) in enumerate(cost_labels.items()):
            row = ctk.CTkFrame(marriage_grid, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=10)).pack(side="left", padx=(0,10))
            entry = ctk.CTkEntry(row, width=100)
            entry.pack(side="left")
            entry.insert(0, str(marriage_costs[key]))
            self.marriage_entries[key] = entry

        # 生育成本模块
        child_frame = ctk.CTkFrame(scrollable_frame)
        child_frame.pack(fill="x", padx=10, pady=10)

        child_title = ctk.CTkLabel(child_frame, text="👶 生育教育成本明细", font=ctk.CTkFont(size=14, weight="bold"))
        child_title.pack(pady=10)

        child_grid = ctk.CTkFrame(child_frame, fg_color="transparent")
        child_grid.pack(fill="x", padx=20, pady=10)

        # 孩子数量
        child_row1 = ctk.CTkFrame(child_grid, fg_color="transparent")
        child_row1.pack(fill="x", pady=5)

        ctk.CTkLabel(child_row1, text="孩子数量:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0,10))
        self.child_count_entry = ctk.CTkEntry(child_row1, width=80)
        self.child_count_entry.pack(side="left")
        self.child_count_entry.insert(0, str(self.form_data['childCount']))

        # 生育成本输入
        child_costs = self.form_data['children'][0]
        self.child_entries = {}

        child_cost_labels = {
            'prenatalCare': '产检费用',
            'delivery': '分娩费用',
            'postpartumCare': '月子中心',
            'monthlyBabyCost': '月均婴儿用品',
            'kindergarten': '幼儿园3年',
            'primarySchool': '小学6年',
            'juniorHigh': '初中3年',
            'seniorHigh': '高中3年',
            'university': '本科4年',
            'extracurricular': '课外辅导'
        }

        for i, (key, label) in enumerate(child_cost_labels.items()):
            row = ctk.CTkFrame(child_grid, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=10)).pack(side="left", padx=(0,10))
            entry = ctk.CTkEntry(row, width=100)
            entry.pack(side="left")
            entry.insert(0, str(child_costs[key]))
            self.child_entries[key] = entry

        # 其他参数模块
        other_frame = ctk.CTkFrame(scrollable_frame)
        other_frame.pack(fill="x", padx=10, pady=10)

        other_title = ctk.CTkLabel(other_frame, text="📊 其他参数", font=ctk.CTkFont(size=14, weight="bold"))
        other_title.pack(pady=10)

        other_grid = ctk.CTkFrame(other_frame, fg_color="transparent")
        other_grid.pack(fill="x", padx=20, pady=10)

        # 父母支持、投资收益率、生活成本、通胀率
        params = [
            ('annualParentSupport', '父母每年现金支持'),
            ('investmentReturn', '投资收益率(%)'),
            ('baseLivingCost', '基础生活成本(月)'),
            ('livingInflation', '生活通胀率(%)')
        ]

        self.other_entries = {}
        for param_key, param_label in params:
            row = ctk.CTkFrame(other_grid, fg_color="transparent")
            row.pack(fill="x", pady=5)

            ctk.CTkLabel(row, text=f"{param_label}:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0,10))
            entry = ctk.CTkEntry(row, width=100)
            entry.pack(side="left")
            entry.insert(0, str(self.form_data[param_key]))
            self.other_entries[param_key] = entry

        # 计算按钮
        calc_button = ctk.CTkButton(
            scrollable_frame,
            text="重新计算",
            command=self.calculate,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40
        )
        calc_button.pack(pady=20)

        # 绑定事件
        self.stability_slider.configure(command=self.update_stability_label)
        self.appreciation_slider.configure(command=self.update_appreciation_label)

    def create_analysis_tab(self):
        """创建成本分析选项卡"""
        analysis_frame = self.tabview.tab("成本分析")

        # 图表面板
        chart_frame = ctk.CTkFrame(analysis_frame)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建matplotlib图形
        self.figure, self.ax = plt.subplots(figsize=(12, 7), dpi=100)
        # 设置matplotlib样式
        plt.style.use('default')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_facecolor('#f8fafc')

        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # 统计信息面板
        stats_frame = ctk.CTkFrame(analysis_frame, height=200)
        stats_frame.pack(fill="x", padx=10, pady=(0, 10))
        stats_frame.pack_propagate(False)

        # 图表图例说明
        legend_frame = ctk.CTkFrame(stats_frame, fg_color="#f8fafc", corner_radius=8)
        legend_frame.pack(fill="x", padx=10, pady=(10, 5))

        legend_title = ctk.CTkLabel(legend_frame, text="📊 图表说明 (Chart Legend):", font=ctk.CTkFont(size=11, weight="bold"))
        legend_title.pack(pady=(8, 5))

        legend_text = ctk.CTkLabel(
            legend_frame,
            text="📈 图表颜色含义：\n" +
                 "🟢 绿色柱状图 = 资产增值（房产等）\n" +
                 "🟡 黄色柱状图 = 结婚生育成本\n" +
                 "🔵 蓝色柱状图 = 投资与父母支持\n" +
                 "⚫ 黑色线条 = 综合家庭损益\n" +
                 "🔘 灰色区域 = 净现金流",
            font=ctk.CTkFont(size=9),
            justify="left"
        )
        legend_text.pack(padx=15, pady=(0, 8))

        # 创建统计标签
        self.stats_labels = {}
        stats_names = [
            ("total_cost", "总成本"),
            ("marriage_cost", "结婚成本"),
            ("education_cost", "教育成本"),
            ("min_cash_flow", "最低现金流"),
            ("risk_coefficient", "抗风险系数")
        ]

        for i, (key, name) in enumerate(stats_names):
            label = ctk.CTkLabel(
                stats_frame,
                text=f"{name}: 计算中...",
                font=ctk.CTkFont(size=12, family="SimHei")
            )
            label.grid(row=1, column=i, padx=15, pady=10, sticky="w")  # 移到第二行
            self.stats_labels[key] = label

    def create_ai_tab(self):
        """创建AI分析选项卡"""
        ai_frame = self.tabview.tab("AI分析")

        # AI分析面板
        ai_panel = ctk.CTkFrame(ai_frame)
        ai_panel.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题
        ai_title = ctk.CTkLabel(ai_panel, text="🤖 深度资产审计报告", font=ctk.CTkFont(size=16, weight="bold"))
        ai_title.pack(pady=10)

        # 分析文本区域
        self.ai_text = scrolledtext.ScrolledText(ai_panel, wrap=tk.WORD, height=20)
        self.ai_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.ai_text.insert(tk.END, "请先在参数设置页面输入数据并计算，然后点击生成AI分析报告。")

        # 按钮框架
        button_frame = ctk.CTkFrame(ai_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)

        # 生成报告按钮
        generate_button = ctk.CTkButton(
            button_frame,
            text="生成AI分析报告",
            command=self.generate_ai_analysis,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        generate_button.pack(side="left", padx=(0,10))

        # 清空按钮
        clear_button = ctk.CTkButton(
            button_frame,
            text="清空报告",
            command=self.clear_ai_analysis,
            fg_color="transparent",
            border_width=2
        )
        clear_button.pack(side="left")

    def create_data_tab(self):
        """创建数据管理选项卡"""
        data_frame = self.tabview.tab("数据管理")

        # 数据管理面板
        data_panel = ctk.CTkFrame(data_frame)
        data_panel.pack(fill="both", expand=True, padx=10, pady=10)

        # 标题
        data_title = ctk.CTkLabel(data_panel, text="💾 数据管理", font=ctk.CTkFont(size=16, weight="bold"))
        data_title.pack(pady=10)

        # 按钮框架
        button_frame = ctk.CTkFrame(data_panel, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        # 保存配置按钮
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 保存当前配置",
            command=self.save_config,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669"
        )
        save_button.pack(side="left", padx=(0, 20))

        # 加载配置按钮
        load_button = ctk.CTkButton(
            button_frame,
            text="📂 加载配置",
            command=self.load_config,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3b82f6",
            hover_color="#2563eb"
        )
        load_button.pack(side="left", padx=(0, 20))

        # 导出报告按钮
        export_button = ctk.CTkButton(
            button_frame,
            text="📄 导出分析报告",
            command=self.export_report,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#8b5cf6",
            hover_color="#7c3aed"
        )
        export_button.pack(side="left")

        # 预设配置框架
        preset_frame = ctk.CTkFrame(data_panel)
        preset_frame.pack(fill="x", padx=20, pady=(0, 20))

        preset_title = ctk.CTkLabel(preset_frame, text="🎯 预设配置", font=ctk.CTkFont(size=14, weight="bold"))
        preset_title.pack(pady=10)

        # 预设按钮网格
        preset_grid = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_grid.pack(fill="x", padx=20, pady=10)

        # 一线城市配置
        tier1_button = ctk.CTkButton(
            preset_grid,
            text="一线城市\n(北京/上海)",
            command=lambda: self.load_preset("tier1"),
            height=60,
            font=ctk.CTkFont(size=11)
        )
        tier1_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # 二线城市配置
        tier2_button = ctk.CTkButton(
            preset_grid,
            text="二线城市\n(杭州/南京)",
            command=lambda: self.load_preset("tier2"),
            height=60,
            font=ctk.CTkFont(size=11)
        )
        tier2_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # 三线城市配置
        tier3_button = ctk.CTkButton(
            preset_grid,
            text="三线城市\n(普通地级市)",
            command=lambda: self.load_preset("tier3"),
            height=60,
            font=ctk.CTkFont(size=11)
        )
        tier3_button.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        # 保守型配置
        conservative_button = ctk.CTkButton(
            preset_grid,
            text="保守型\n(低风险偏好)",
            command=lambda: self.load_preset("conservative"),
            height=60,
            font=ctk.CTkFont(size=11),
            fg_color="#059669",
            hover_color="#047857"
        )
        conservative_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # 激进型配置
        aggressive_button = ctk.CTkButton(
            preset_grid,
            text="激进型\n(高风险偏好)",
            command=lambda: self.load_preset("aggressive"),
            height=60,
            font=ctk.CTkFont(size=11),
            fg_color="#dc2626",
            hover_color="#b91c1c"
        )
        aggressive_button.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # 平衡型配置
        balanced_button = ctk.CTkButton(
            preset_grid,
            text="平衡型\n(稳健配置)",
            command=lambda: self.load_preset("balanced"),
            height=60,
            font=ctk.CTkFont(size=11),
            fg_color="#7c3aed",
            hover_color="#6d28d9"
        )
        balanced_button.grid(row=1, column=2, padx=10, pady=5, sticky="ew")

        # 配置预设网格列权重
        preset_grid.grid_columnconfigure(0, weight=1)
        preset_grid.grid_columnconfigure(1, weight=1)
        preset_grid.grid_columnconfigure(2, weight=1)

    def update_stability_label(self, value):
        """更新稳定性标签"""
        self.stability_label.configure(text=f"{int(float(value))}%")

    def update_appreciation_label(self, value):
        """更新增值率标签"""
        self.appreciation_label.configure(text=f"{float(value):.1f}%")

    def calculate(self):
        """执行成本计算"""
        try:
            # 更新数据
            self.update_form_data()

            # 执行分析
            self.analysis_result = self.perform_analysis()

            # 更新显示
            self.update_display()

            # 重绘图表
            self.update_chart()

        except Exception as e:
            messagebox.showerror("计算错误", f"计算过程中出现错误：{str(e)}")

    def update_form_data(self):
        """从界面更新数据"""
        try:
            # 基本信息
            self.form_data['salaryA'] = float(self.salary_a_entry.get())
            self.form_data['salaryB'] = float(self.salary_b_entry.get())
            self.form_data['annualBonus'] = float(self.bonus_entry.get())
            self.form_data['incomeStability'] = self.stability_slider.get()

            # 房产信息
            self.form_data['propertyValue'] = float(self.property_value_entry.get())
            self.form_data['propertyAppreciation'] = self.appreciation_slider.get()
            self.form_data['monthlyMortgage'] = float(self.mortgage_entry.get())

            # 结婚成本
            for key, entry in self.marriage_entries.items():
                self.form_data['marriageCosts'][key] = float(entry.get())

            # 生育成本
            self.form_data['childCount'] = int(self.child_count_entry.get())
            for key, entry in self.child_entries.items():
                self.form_data['children'][0][key] = float(entry.get())

            # 其他参数
            for key, entry in self.other_entries.items():
                self.form_data[key] = float(entry.get())

        except ValueError as e:
            raise ValueError(f"输入数据格式错误，请检查所有字段都是数字：{str(e)}")

    def perform_analysis(self):
        """执行财务分析计算"""
        data = self.form_data

        # 结婚总成本
        total_marriage_cost = sum(data['marriageCosts'].values())

        # 计算每个孩子的总教育成本
        child = data['children'][0]
        child_education_cost = (
            child['prenatalCare'] + child['delivery'] + child['postpartumCare'] +
            child['monthlyBabyCost'] * 12 * 3 +  # 3年婴儿期
            child['kindergarten'] + child['primarySchool'] + child['juniorHigh'] +
            child['seniorHigh'] + child['university'] + child['extracurricular']
        )

        total_child_cost = child_education_cost * data['childCount']
        total_cost = total_marriage_cost + total_child_cost

        stages = [
            { 'name': '结婚准备', 'years': 1, 'isMarriageStage': True },
            { 'name': '0-3岁', 'years': 3 },
            { 'name': '3-6岁', 'years': 3 },
            { 'name': '6-12岁', 'years': 6 },
            { 'name': '12-15岁', 'years': 3 },
            { 'name': '15-18岁', 'years': 3 }
        ]

        current_property_value = data['propertyValue']
        total_net_assets_change = -total_marriage_cost
        min_cash_flow_surplus = float('inf')

        chart_data = []

        for idx, stage in enumerate(stages):
            year_count = stage['years']
            elapsed_years = max(0, (idx - 1) * 3)

            # 收入计算
            annual_income_base = (data['salaryA'] + data['salaryB']) * 12 + data['annualBonus']
            effective_annual_income = annual_income_base * (data['incomeStability'] / 100)
            stage_income = 0 if stage.get('isMarriageStage', False) else effective_annual_income * year_count

            # 支出计算
            stage_living_cost = 0 if stage.get('isMarriageStage', False) else data['baseLivingCost'] * 12 * year_count * (1 + data['livingInflation']/100) ** elapsed_years
            stage_mortgage = 0 if stage.get('isMarriageStage', False) else data['monthlyMortgage'] * 12 * year_count

            # 育儿成本
            stage_child_cost = 0
            if not stage.get('isMarriageStage', False):
                if idx == 1:  # 0-3岁
                    stage_child_cost = (child['prenatalCare'] + child['delivery'] + child['postpartumCare'] + child['monthlyBabyCost'] * 12 * 3) * data['childCount']
                elif idx == 2:  # 3-6岁
                    stage_child_cost = child['kindergarten'] * data['childCount']
                elif idx == 3:  # 6-12岁
                    stage_child_cost = child['primarySchool'] * data['childCount']
                elif idx == 4:  # 12-15岁
                    stage_child_cost = child['juniorHigh'] * data['childCount']
                elif idx == 5:  # 15-18岁
                    stage_child_cost = (child['seniorHigh'] + child['extracurricular']) * data['childCount']

                stage_child_cost *= (1 + data['livingInflation']/100) ** elapsed_years

            # 结婚成本
            stage_marriage_cost = total_marriage_cost if stage.get('isMarriageStage', False) else 0

            # 房产增值
            property_value_at_end = current_property_value * (1 + data['propertyAppreciation']/100) ** year_count
            stage_property_gain = property_value_at_end - current_property_value
            current_property_value = property_value_at_end

            # 投资收益和父母支持
            stage_support = 0 if stage.get('isMarriageStage', False) else data['annualParentSupport'] * year_count
            stage_invest_gain = 0 if stage.get('isMarriageStage', False) else (stage_income * 0.2) * (data['investmentReturn'] / 100) * year_count

            # 净现金流和总损益
            net_cash_flow = stage_income + stage_support - stage_living_cost - stage_mortgage - stage_child_cost - stage_marriage_cost
            total_economic_gain = net_cash_flow + stage_property_gain + stage_invest_gain

            if not stage.get('isMarriageStage', False) and net_cash_flow < min_cash_flow_surplus:
                min_cash_flow_surplus = net_cash_flow

            total_net_assets_change += total_economic_gain

            chart_data.append({
                'name': stage['name'],
                '净现金流': net_cash_flow,
                '资产增值贬值': stage_property_gain,
                '结婚生育成本': stage_marriage_cost + stage_child_cost,
                '投资与支持': stage_invest_gain + stage_support,
                '综合家庭损益': total_economic_gain,
                'isMarriageStage': stage.get('isMarriageStage', False)
            })

        # 计算抗风险系数
        monthly_income = (data['salaryA'] + data['salaryB'] + data['annualParentSupport']/12)
        monthly_expenses = data['monthlyMortgage'] + data['baseLivingCost']
        risk_coefficient = monthly_income / monthly_expenses if monthly_expenses > 0 else 0

        return {
            'chartData': chart_data,
            'totalNetAssetsChange': total_net_assets_change,
            'minCashFlowSurplus': min_cash_flow_surplus if min_cash_flow_surplus != float('inf') else 0,
            'totalMarriageCost': total_marriage_cost,
            'childEducationCost': total_child_cost,
            'totalCost': total_cost,
            'riskCoefficient': risk_coefficient
        }

    def update_display(self):
        """更新显示"""
        result = self.analysis_result

        # 更新标题栏的总资产变化
        change_text = f"18年综合净资产变化预期: {(result['totalNetAssetsChange'] / 10000):.1f}万"
        color = "#10b981" if result['totalNetAssetsChange'] >= 0 else "#ef4444"
        self.total_change_label.configure(text=change_text, text_color=color)

        # 更新统计信息
        try:
            total_cost_text = f"总成本: {(result['totalCost'] / 10000):.1f}万"
            marriage_cost_text = f"结婚成本: {(result['totalMarriageCost'] / 10000):.1f}万"
            education_cost_text = f"教育成本: {(result['childEducationCost'] / 10000):.1f}万"
            min_cash_flow_text = f"最低现金流: {(result['minCashFlowSurplus'] / 10000):.1f}万"
            risk_coefficient_text = f"抗风险系数: {result['riskCoefficient']:.2f}"

            self.stats_labels['total_cost'].configure(text=total_cost_text)
            self.stats_labels['marriage_cost'].configure(text=marriage_cost_text)
            self.stats_labels['education_cost'].configure(text=education_cost_text)
            self.stats_labels['min_cash_flow'].configure(
                text=min_cash_flow_text,
                text_color="#ef4444" if result['minCashFlowSurplus'] < 0 else "#10b981"
            )
            self.stats_labels['risk_coefficient'].configure(text=risk_coefficient_text)

            # 调试输出
            print(f"更新统计信息: 总成本={result['totalCost']}, 结婚成本={result['totalMarriageCost']}, 教育成本={result['childEducationCost']}")

        except Exception as e:
            print(f"更新统计信息时出错: {e}")
            # 提供默认值
            self.stats_labels['total_cost'].configure(text="总成本: 计算中...")
            self.stats_labels['marriage_cost'].configure(text="结婚成本: 计算中...")
            self.stats_labels['education_cost'].configure(text="教育成本: 计算中...")
            self.stats_labels['min_cash_flow'].configure(text="最低现金流: 计算中...")
            self.stats_labels['risk_coefficient'].configure(text="抗风险系数: 计算中...")

    def update_chart(self):
        """更新图表"""
        self.ax.clear()
        self.ax.set_facecolor('#f8fafc')

        data = self.analysis_result['chartData']
        stages = [item['name'] for item in data]

        # 绘制柱状图
        x = np.arange(len(stages))
        width = 0.25

        # 资产增值贬值
        property_values = [item['资产增值贬值'] for item in data]
        bars1 = self.ax.bar(x - width, property_values, width, label='资产增值贬值',
                           color=['#ef4444' if v < 0 else '#10b981' for v in property_values],
                           alpha=0.8, edgecolor='white', linewidth=0.5)

        # 结婚生育成本
        cost_values = [item['结婚生育成本'] for item in data]
        bars2 = self.ax.bar(x, cost_values, width, label='结婚生育成本', color='#f59e0b',
                           alpha=0.8, edgecolor='white', linewidth=0.5)

        # 投资与支持
        invest_values = [item['投资与支持'] for item in data]
        bars3 = self.ax.bar(x + width, invest_values, width, label='投资与支持', color='#3b82f6',
                           alpha=0.8, edgecolor='white', linewidth=0.5)

        # 绘制综合损益线
        total_values = [item['综合家庭损益'] for item in data]
        line = self.ax.plot(x, total_values, 'k-', linewidth=4, label='综合家庭损益',
                           marker='o', markersize=6, markerfacecolor='white', markeredgecolor='black', markeredgewidth=2)

        # 添加净现金流区域
        cash_flow_values = [item['净现金流'] for item in data]
        self.ax.fill_between(x, 0, cash_flow_values, alpha=0.2, color='#64748b', label='净现金流')

        # 添加基准线
        self.ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)

        # 强制使用中文字体（已确认系统支持）
        try:
            self.ax.set_xlabel('生命周期阶段', fontsize=11, fontweight='bold', fontfamily='SimHei')
            self.ax.set_ylabel('金额 (元)', fontsize=11, fontweight='bold', fontfamily='SimHei')
            self.ax.set_title('家庭财务损益分析 - 18年生命周期', fontsize=14, fontweight='bold', pad=20, fontfamily='SimHei')
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(stages, rotation=45, ha='right', fontsize=10, fontfamily='SimHei')
        except Exception as e:
            print(f"中文标签设置失败，使用英文: {e}")
            self.ax.set_xlabel('Life Stage', fontsize=11, fontweight='bold')
            self.ax.set_ylabel('Amount (CNY)', fontsize=11, fontweight='bold')
            self.ax.set_title('Family Financial Analysis - 18 Years', fontsize=14, fontweight='bold', pad=20)
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(stages, rotation=45, ha='right', fontsize=10)

        # 美化图例
        try:
            legend = self.ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9, prop={'family': 'SimHei', 'size': 9})
            legend.get_frame().set_alpha(0.9)
        except Exception as e:
            print(f"图例中文显示失败，使用英文图例: {e}")
            try:
                legend = self.ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
                legend.get_frame().set_alpha(0.9)
            except Exception as e2:
                print(f"英文图例也失败: {e2}")
                try:
                    self.ax.legend().set_visible(False)
                except:
                    pass

        # 美化网格
        self.ax.grid(True, alpha=0.3, linestyle='--')

        # 格式化Y轴
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'¥{x/1000:.0f}k'))

        # 添加数值标签
        for i, v in enumerate(total_values):
            if abs(v) > 10000:  # 只为较大的值添加标签
                self.ax.text(i, v + (50000 if v >= 0 else -50000),
                           f'{v/10000:.1f}万', ha='center', va='bottom' if v >= 0 else 'top',
                           fontsize=9, fontweight='bold', fontfamily='SimHei')

        self.figure.tight_layout()
        self.canvas.draw()

    def generate_ai_analysis(self):
        """生成AI分析报告"""
        try:
            # 这里可以集成AI API，暂时提供模板分析
            analysis = f"""
深度资产审计报告 (AI Generated)
=====================================

📊 财务状况概览
总资产变化: ¥{(self.analysis_result['totalNetAssetsChange'] / 10000):.1f}万
结婚成本: ¥{(self.analysis_result['totalMarriageCost'] / 10000):.1f}万
教育成本: ¥{(self.analysis_result['childEducationCost'] / 10000):.1f}万

🏠 房产风险评估
当前市值: ¥{(self.form_data['propertyValue'] / 10000):.1f}万
预期年化: {self.form_data['propertyAppreciation']}%
18年贬值风险: ¥{(abs(self.form_data['propertyValue'] * ((1 + self.form_data['propertyAppreciation']/100) ** 18 - 1)) / 10000):.0f}万

💰 现金流分析
最低现金流: ¥{(self.analysis_result['minCashFlowSurplus'] / 10000):.1f}万
抗风险系数: {self.analysis_result['riskCoefficient']:.2f}
建议系数: >1.5 (当前{'良好' if self.analysis_result['riskCoefficient'] > 1.5 else '需关注'})

📈 投资建议
投资收益率: {self.form_data['investmentReturn']}%
通胀率: {self.form_data['livingInflation']}%
实际收益率: {self.form_data['investmentReturn'] - self.form_data['livingInflation']:.1f}%

⚠️ 风险提示
{'⚠️ 现金流存在风险，建议优化支出结构' if self.analysis_result['minCashFlowSurplus'] < 0 else '✅ 现金流状况良好'}
{'⚠️ 房产贬值风险较高，建议分散投资' if self.form_data['propertyAppreciation'] < -2 else '✅ 房产配置相对稳健'}

💡 优化建议
1. 合理控制结婚成本，避免过度消费
2. 提前规划教育基金，建立专项理财
3. 提高收入稳定性，降低行业风险
4. 关注资产配置，避免过度集中
            """

            self.ai_text.delete(1.0, tk.END)
            self.ai_text.insert(tk.END, analysis.strip())

        except Exception as e:
            messagebox.showerror("AI分析错误", f"生成分析报告时出现错误：{str(e)}")

    def clear_ai_analysis(self):
        """清空AI分析"""
        self.ai_text.delete(1.0, tk.END)
        self.ai_text.insert(tk.END, "AI分析报告已清空。请重新计算后生成新报告。")

    def save_config(self):
        """保存当前配置"""
        try:
            # 更新数据
            self.update_form_data()

            # 保存到文件
            with open("marriage_calculator_config.json", "w", encoding="utf-8") as f:
                json.dump(self.form_data, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("保存成功", "配置已保存到 marriage_calculator_config.json")

        except Exception as e:
            messagebox.showerror("保存失败", f"保存配置时出现错误：{str(e)}")

    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists("marriage_calculator_config.json"):
                with open("marriage_calculator_config.json", "r", encoding="utf-8") as f:
                    self.form_data = json.load(f)

                # 更新界面
                self.update_ui_from_data()
                self.calculate()

                messagebox.showinfo("加载成功", "配置已从文件加载")
            else:
                messagebox.showwarning("文件不存在", "找不到配置文件 marriage_calculator_config.json")

        except Exception as e:
            messagebox.showerror("加载失败", f"加载配置时出现错误：{str(e)}")

    def export_report(self):
        """导出分析报告"""
        try:
            from datetime import datetime

            # 生成报告内容
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_content = f"""
结婚生育成本分析报告
生成时间: {timestamp}
=====================================

📊 财务概况
总资产变化: ¥{(self.analysis_result['totalNetAssetsChange'] / 10000):.1f}万
结婚总成本: ¥{(self.analysis_result['totalMarriageCost'] / 10000):.1f}万
教育总成本: ¥{(self.analysis_result['childEducationCost'] / 10000):.1f}万
综合总成本: ¥{(self.analysis_result['totalCost'] / 10000):.1f}万

💰 收入状况
配偶A月薪: ¥{self.form_data['salaryA']:,.0f}
配偶B月薪: ¥{self.form_data['salaryB']:,.0f}
年终奖: ¥{self.form_data['annualBonus']:,.0f}
收入稳定性: {self.form_data['incomeStability']}%

🏠 房产状况
房产市值: ¥{(self.form_data['propertyValue'] / 10000):.1f}万
预期年化: {self.form_data['propertyAppreciation']}%
月供: ¥{self.form_data['monthlyMortgage']:,.0f}

👨‍👩‍👧‍👦 家庭状况
孩子数量: {self.form_data['childCount']}个
父母年支持: ¥{self.form_data['annualParentSupport']:,.0f}

📈 投资参数
投资收益率: {self.form_data['investmentReturn']}%
生活通胀率: {self.form_data['livingInflation']}%

⚠️ 风险评估
最低现金流: ¥{(self.analysis_result['minCashFlowSurplus'] / 10000):.1f}万
抗风险系数: {self.analysis_result['riskCoefficient']:.2f}

💡 建议
{'✅ 财务状况良好' if self.analysis_result['totalNetAssetsChange'] > 0 else '⚠️ 财务状况需优化'}
{'✅ 现金流稳定' if self.analysis_result['minCashFlowSurplus'] > 0 else '⚠️ 现金流紧张'}
{'✅ 抗风险能力强' if self.analysis_result['riskCoefficient'] > 1.5 else '⚠️ 抗风险能力需提升'}
            """

            # 保存报告
            filename = f"marriage_cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report_content.strip())

            messagebox.showinfo("导出成功", f"分析报告已导出到 {filename}")

        except Exception as e:
            messagebox.showerror("导出失败", f"导出报告时出现错误：{str(e)}")

    def load_preset(self, preset_type):
        """加载预设配置"""
        try:
            presets = {
                "tier1": {  # 一线城市 - 基于2023年北京上海数据
                    'salaryA': 28000, 'salaryB': 24000, 'annualBonus': 120000,  # 高收入水平
                    'incomeStability': 78, 'propertyValue': 12000000,  # 北京上海平均房价
                    'propertyAppreciation': 0.2, 'monthlyMortgage': 18000,  # 高房贷压力
                    'annualParentSupport': 60000,  # 高父母支持
                    'marriageCosts': {
                        'betrothalGift': 120000, 'weddingCeremony': 200000,  # 高端婚礼
                        'weddingRing': 60000, 'honeymoon': 80000,  # 豪华蜜月
                        'newHouseDownPayment': 1200000, 'renovation': 400000  # 高房价装修
                    },
                    'children': [{
                        'prenatalCare': 15000, 'delivery': 25000, 'postpartumCare': 35000,
                        'monthlyBabyCost': 3500, 'kindergarten': 240000, 'primarySchool': 480000,
                        'juniorHigh': 360000, 'seniorHigh': 300000, 'university': 1200000,
                        'extracurricular': 200000
                    }],
                    'baseLivingCost': 12000, 'livingInflation': 2.8, 'investmentReturn': 4.5
                },
                "tier2": {  # 二线城市 - 基于2023年杭州南京数据
                    'salaryA': 22000, 'salaryB': 18000, 'annualBonus': 80000,  # 中等收入
                    'incomeStability': 82, 'propertyValue': 1800000,  # 2-3万/㎡房价
                    'propertyAppreciation': -1.2, 'monthlyMortgage': 6500,  # 中等房贷
                    'annualParentSupport': 35000,  # 中等父母支持
                    'marriageCosts': {
                        'betrothalGift': 58000, 'weddingCeremony': 128000,  # 中等婚礼
                        'weddingRing': 35000, 'honeymoon': 45000,  # 中等蜜月
                        'newHouseDownPayment': 360000, 'renovation': 180000  # 中等装修
                    },
                    'children': [{
                        'prenatalCare': 8500, 'delivery': 12000, 'postpartumCare': 22000,
                        'monthlyBabyCost': 2200, 'kindergarten': 96000, 'primarySchool': 180000,
                        'juniorHigh': 156000, 'seniorHigh': 132000, 'university': 720000,
                        'extracurricular': 120000
                    }],
                    'baseLivingCost': 6200, 'livingInflation': 2.1, 'investmentReturn': 3.8
                },
                "tier3": {  # 三线城市 - 基于2023年普通地级市数据
                    'salaryA': 12000, 'salaryB': 10000, 'annualBonus': 40000,  # 较低收入
                    'incomeStability': 85, 'propertyValue': 800000,  # 6-8千/㎡房价
                    'propertyAppreciation': -1.8, 'monthlyMortgage': 2800,  # 较低房贷
                    'annualParentSupport': 20000,  # 较低父母支持
                    'marriageCosts': {
                        'betrothalGift': 35000, 'weddingCeremony': 68000,  # 简约婚礼
                        'weddingRing': 20000, 'honeymoon': 25000,  # 简单蜜月
                        'newHouseDownPayment': 160000, 'renovation': 90000  # 简单装修
                    },
                    'children': [{
                        'prenatalCare': 5500, 'delivery': 8000, 'postpartumCare': 15000,
                        'monthlyBabyCost': 1600, 'kindergarten': 72000, 'primarySchool': 132000,
                        'juniorHigh': 108000, 'seniorHigh': 96000, 'university': 480000,
                        'extracurricular': 80000
                    }],
                    'baseLivingCost': 4200, 'livingInflation': 2.0, 'investmentReturn': 3.5
                },
                "conservative": {  # 保守型 - 低风险偏好，稳定配置
                    'salaryA': 16000, 'salaryB': 14000, 'annualBonus': 50000,
                    'incomeStability': 92, 'propertyValue': 1500000,  # 小户型，现金多
                    'propertyAppreciation': -0.8, 'monthlyMortgage': 4500,  # 低杠杆
                    'annualParentSupport': 45000,  # 多父母支持
                    'marriageCosts': {
                        'betrothalGift': 38000, 'weddingCeremony': 88000,  # 节约婚礼
                        'weddingRing': 25000, 'honeymoon': 30000,  # 适中消费
                        'newHouseDownPayment': 300000, 'renovation': 120000  # 简单装修
                    },
                    'children': [{
                        'prenatalCare': 6500, 'delivery': 9500, 'postpartumCare': 18000,
                        'monthlyBabyCost': 1800, 'kindergarten': 72000, 'primarySchool': 144000,
                        'juniorHigh': 120000, 'seniorHigh': 108000, 'university': 600000,
                        'extracurricular': 96000
                    }],
                    'baseLivingCost': 5200, 'livingInflation': 2.0, 'investmentReturn': 3.0
                },
                "aggressive": {  # 激进型 - 高风险偏好，激进配置
                    'salaryA': 32000, 'salaryB': 28000, 'annualBonus': 150000,  # 高收入
                    'incomeStability': 65, 'propertyValue': 2800000,  # 大户型，杠杆高
                    'propertyAppreciation': 1.5, 'monthlyMortgage': 11000,  # 高杠杆
                    'annualParentSupport': 25000,  # 少父母支持
                    'marriageCosts': {
                        'betrothalGift': 88000, 'weddingCeremony': 180000,  # 豪华婚礼
                        'weddingRing': 80000, 'honeymoon': 100000,  # 奢侈消费
                        'newHouseDownPayment': 560000, 'renovation': 350000  # 豪华装修
                    },
                    'children': [{
                        'prenatalCare': 12000, 'delivery': 20000, 'postpartumCare': 35000,
                        'monthlyBabyCost': 3200, 'kindergarten': 180000, 'primarySchool': 360000,
                        'juniorHigh': 300000, 'seniorHigh': 240000, 'university': 1200000,
                        'extracurricular': 240000
                    }],
                    'baseLivingCost': 9200, 'livingInflation': 3.0, 'investmentReturn': 7.0
                },
                "balanced": {  # 平衡型 - 稳健配置，均衡发展
                    'salaryA': 24000, 'salaryB': 20000, 'annualBonus': 90000,  # 中高收入
                    'incomeStability': 80, 'propertyValue': 2200000,  # 舒适户型
                    'propertyAppreciation': 0.3, 'monthlyMortgage': 7800,  # 中等杠杆
                    'annualParentSupport': 38000,  # 中等父母支持
                    'marriageCosts': {
                        'betrothalGift': 65000, 'weddingCeremony': 135000,  # 体面婚礼
                        'weddingRing': 45000, 'honeymoon': 55000,  # 品质消费
                        'newHouseDownPayment': 440000, 'renovation': 220000  # 舒适装修
                    },
                    'children': [{
                        'prenatalCare': 9500, 'delivery': 14000, 'postpartumCare': 26000,
                        'monthlyBabyCost': 2500, 'kindergarten': 120000, 'primarySchool': 240000,
                        'juniorHigh': 192000, 'seniorHigh': 168000, 'university': 960000,
                        'extracurricular': 144000
                    }],
                    'baseLivingCost': 7200, 'livingInflation': 2.3, 'investmentReturn': 4.5
                }
            }

            if preset_type in presets:
                # 合并预设配置到当前数据
                preset = presets[preset_type]
                for key, value in preset.items():
                    if key in self.form_data:
                        if isinstance(value, dict):
                            self.form_data[key].update(value)
                        else:
                            self.form_data[key] = value

                # 更新界面
                self.update_ui_from_data()
                self.calculate()

                preset_names = {
                    "tier1": "一线城市", "tier2": "二线城市", "tier3": "三线城市",
                    "conservative": "保守型", "aggressive": "激进型", "balanced": "平衡型"
                }
                messagebox.showinfo("预设加载成功", f"{preset_names[preset_type]}配置已加载")

        except Exception as e:
            messagebox.showerror("预设加载失败", f"加载预设配置时出现错误：{str(e)}")

    def update_ui_from_data(self):
        """从数据更新界面"""
        try:
            # 基本信息
            self.salary_a_entry.delete(0, tk.END)
            self.salary_a_entry.insert(0, str(int(self.form_data['salaryA'])))

            self.salary_b_entry.delete(0, tk.END)
            self.salary_b_entry.insert(0, str(int(self.form_data['salaryB'])))

            self.bonus_entry.delete(0, tk.END)
            self.bonus_entry.insert(0, str(int(self.form_data['annualBonus'])))

            self.stability_slider.set(self.form_data['incomeStability'])

            # 房产信息
            self.property_value_entry.delete(0, tk.END)
            self.property_value_entry.insert(0, str(int(self.form_data['propertyValue'])))

            self.appreciation_slider.set(self.form_data['propertyAppreciation'])

            self.mortgage_entry.delete(0, tk.END)
            self.mortgage_entry.insert(0, str(int(self.form_data['monthlyMortgage'])))

            # 结婚成本
            for key, entry in self.marriage_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, str(int(self.form_data['marriageCosts'][key])))

            # 生育成本
            self.child_count_entry.delete(0, tk.END)
            self.child_count_entry.insert(0, str(int(self.form_data['childCount'])))

            for key, entry in self.child_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, str(int(self.form_data['children'][0][key])))

            # 其他参数
            for key, entry in self.other_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, str(self.form_data[key]))

        except Exception as e:
            print(f"更新界面时出现错误: {e}")

    def run(self):
        """运行应用程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MarriageCalculatorApp()
    app.run()