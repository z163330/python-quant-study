'''
第15天
					绩效可视化
-绘制净值曲线
-绘制回撤曲线
-绘制绩效指标对比图

练习：
-整理完整绩效分析图表
'''



import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib



class PerformanceVisualizer:
    """绩效可视化器"""

    def __init__(self):
        """初始化绩效可视化器"""
        print(f"\n" + '=' * 80)
        print(f" 方法1: 初始化绩效可视化器")
        print("=" * 80)

        # 1. 获取当前文件目录
        print(f" \n1. 获取当前文件目录")
        current_dir = Path(__file__).parent
        print(f" 当前文件目录: {current_dir}")

        # 2. 找到项目根目录
        print(f" \n2. 找到项目根目录")
        self.project_root = current_dir.parent
        print(f" 项目根目录: {self.project_root}")

        # 3. 设置数据目录
        print(f" \n3. 设置数据目录")
        self.ma_result_dir = self.project_root / "data" / "策略结果"
        self.momentum_result_dir = self.project_root / "data" / "动量策略结果"
        print(f" 均线策略结果目录: {self.ma_result_dir}")
        print(f" 动量策略结果目录: {self.momentum_result_dir}")

        # 4. 设置图表输出目录
        print(f" \n4. 设置图表输出目录")
        self.chart_dir = self.project_root / "charts" / "绩效可视化"
        self.chart_dir.mkdir(parents=True, exist_ok=True)
        print(f" 图表目录: {self.chart_dir}")

        # 5. 设置输出目录
        print(f' \n5. 设置输出目录')
        self.output_dir = self.project_root / "data" / "绩效可视化"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f" 输出目录: {self.output_dir}")

        # 6. 配置中文字体
        print(f" \n6. 配置中文字体")
        self._setup_chinese_font()

        print(f" \n" +'=' * 80)
        print(f" 方法1完成: 初始化成功")
        print('=' * 80)
        print(f" 均线策略目录: {self.ma_result_dir}")
        print(f" 动量策略目录: {self.momentum_result_dir}")
        print(f" 图表输出: {self.chart_dir}")
        print(f" 输出目录: {self.output_dir}")

    def _setup_chinese_font(self):
        """配置中文字体"""
        import matplotlib.font_manager as fm
        import os

        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simhei.ttf',
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    fm.fontManager.addfont(path)
                    font_name = fm.FontProperties(fname=path).get_name()
                    plt.rcParams['font.sans-serif'] = [font_name]
                    plt.rcParams['axes.unicode_minus'] = False
                    print(f" 中文字体配置成功: {font_name}")
                    return
                except:
                    continue

        print(f' 未找到中文字体, 使用默认字体')
        plt.rcParams['axes.unicode_minus'] = False

    def load_performance_data(self):
        """加载均线策略和动量策略的回撤数据"""
        print(f' \n' + '=' * 80)
        print(f' 方法2: 加载绩效数据')
        print(f'=' * 80)

        # 1. 加载均线策略结果
        print(f" \n1. 加载均线策略结果")
        ma_folders = list(self.ma_result_dir.glob("回测结果_*"))
        if not ma_folders:
            print(f" 没有找到均线策略结果")
            return None

        latest_ma_folder = max(ma_folders, key=lambda x: x.stat().st_mtime)
        ma_file = latest_ma_folder / "批量回测结果.xlsx"

        if not ma_file.exists():
            print(f" 没有找到批量回测结果文件")
            return None

        df_ma = pd.read_excel(ma_file)
        df_ma.columns = df_ma.columns.str.strip()
        print(f" 均线策略数据: {df_ma.shape[0]}行 x {df_ma.shape[1]} 列")
        print(f' 股票数量: {len(df_ma)}')

        # 2. 加载动量策略结果
        print(f' \n2. 加载动量策略结果')
        momentum_folders = list(self.momentum_result_dir.glob('动量回测结果_*'))
        if not momentum_folders:
            print(f' 没有找到动量策略结果')
            return None
        latest_momentum_folder = max(momentum_folders, key=lambda x: x.stat().st_mtime)
        momentum_file = latest_momentum_folder / "批量回测结果.xlsx"

        if not momentum_file.exists():
            print(f" 没有找到批量回测结果文件")
            return None

        df_momentum = pd.read_excel(momentum_file)
        df_momentum.columns = df_momentum.columns.str.strip()
        print(f" 动量策略结果: {df_momentum.shape[0]} 行 x {df_momentum.shape[1]} 列")
        print(f" 股票数量: {len(df_momentum)}")

        # 3. 检查并转换收益数据
        print(f" \n3. 检查数据格式")
        if df_ma['策略总收益'].max() > 1:
            print(f' 均线策略收益数据为百分比格式, 正在转换........')
            df_ma['策略总收益'] = df_ma['策略总收益'] / 100

        if df_momentum['策略总收益'].max() > 1:
            print(f' 动量策略收益数据为百分比格式, 正在转换.........')
            df_momentum['策略总收益'] = df_momentum['策略总收益'] / 100

        # 4. 保存到对象
        self.df_ma = df_ma
        self.df_momentum = df_momentum

        print(f"\n" + '=' * 80)
        print(f' 方法2完成: 绩效数据加载成功')
        print(f" 均线策略股票数: {len(df_ma)}")
        print(f" 动量策略股票数: {len(df_momentum)}")
        print('=' * 80)
        return df_ma, df_momentum

    def plot_networth_curve(self, df_ma, df_momentum, save=True, show=True):
        """绘制均线策略和动量策略的净值曲线对比图"""
        print(f'\n' + '=' * 80)
        print(f' 方法3: 绘制净值曲线')
        print('=' * 80)

        # 1. 检查数据
        print(f' \n1. 检查数据')
        if df_ma is None or df_momentum is None:
            print(f" 缺少数据")
            return None

        # 2. 计算策略的平均净值 (假设初始净值为1)
        print(" \n2. 计算平均净值")

        # 均线策略平均收益
        ma_avg_return = df_ma['策略总收益'].mean()
        ma_avg_networth = 1 + ma_avg_return

        # 动量策略平均收益
        momentum_avg_return = df_momentum['策略总收益'].mean()
        momentum_avg_networth = 1 + momentum_avg_return

        # 基准平均收益 (买入持有)
        ma_avg_benchmark = 1 + df_ma['基准总收益'].mean()
        momentum_avg_benchmark = 1 + df_momentum['基准总收益'].mean()
        print(f' 均线策略平均净值: {ma_avg_networth:.4f}')
        print(f" 动量策略平均净值: {momentum_avg_networth:.4f}")
        print(f' 均线策略平均基准: {ma_avg_benchmark:.4f}')
        print(f" 动量策略平均基准: {momentum_avg_benchmark:.4f}")

        # 3. 创建图表
        print(f' \n3. 创建图表')
        fig, axes = plt.subplots(1, 2, figsize=(14,6))
        fig.suptitle("策略净值曲线对比", fontsize=16, fontweight='bold')

        # ==================子图1: 均线策略=====================
        print(f" 绘制均线策略净值曲线")
        ax1 = axes[0]

        # 创建模拟数据 (实际项目中应从每日数据获取)
        x = range(len(df_ma))
        strategy_values = np.linspace(1, ma_avg_networth, len(df_ma))
        benchmark_values = np.linspace(1, ma_avg_benchmark, len(df_ma))

        # 添加一些随机波动使其更真实
        np.random.seed(42)
        noise = np.random.normal(0,0.02, len(df_ma))
        strategy_values = strategy_values * (1 + noise)

        ax1.plot(x, strategy_values, linewidth=2, color='green', label='策略净值')
        ax1.plot(x, benchmark_values, linewidth=2, color='blue', label='基准净值', linestyle='--')
        ax1.axhline(y=1, color='red', linestyle='-', linewidth=1, alpha=0.5)

        ax1.set_title('均线策略净值曲线', fontsize=12)
        ax1.set_xlabel("交易日", fontsize=10)
        ax1.set_ylabel('净值', fontsize=10)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 标注最终净值
        ax1.text(0.02, 0.95, f"最终净值: {ma_avg_networth:.4f}",
                 transform=ax1.transAxes, fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

        # ======================子图2: 动量策略 ===================
        print(f' \n. 绘制动量策略净值曲线')
        ax2 = axes[1]

        x = range(len(df_momentum))
        strategy_values = np.linspace(1, momentum_avg_networth, len(df_momentum))
        benchmark_values = np.linspace(1, momentum_avg_benchmark, len(df_momentum))

        # 添加随机波动
        noise = np.random.normal(0, 0.03, len(df_momentum))
        strategy_values = strategy_values * (1 + noise)

        ax2.plot(x, strategy_values, linewidth=2, color='orange', label='策略净值')
        ax2.plot(x, benchmark_values, linewidth=2, color='blue', label='基准净值', linestyle='--')
        ax2.axhline(y=1, color='red', linestyle='-', linewidth=1, alpha=0.5)

        ax2.set_title('动量策略净值曲线', fontsize=12)
        ax2.set_xlabel('交易日', fontsize=10)
        ax2.set_ylabel('净值', fontsize=10)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 标注最终净值
        ax2.text(0.02, 0.95, f"最终净值: {momentum_avg_networth:.4f}",
                 transform=ax2.transAxes, fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='orange', alpha=0.5))
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)

        # 显示图表
        if show:
            print(f' 显示图表...............')
            plt.show()
        else:
            plt.close(fig)

        print(f'\n' + '=' * 80)
        print(f" 方法3完成: 净值曲线绘制成功")
        return fig

    def plot_drawdown_curve(self, df_ma, df_momentum, show=True):
        """绘制均线策略和动量策略的回撤曲线对比图"""
        print(f'\n' + '=' * 80)
        print(f" 方法4: 绘制回撤曲线")
        print('=' * 80)

        # 1. 检查数据
        print(f' \n1. 检查数据')
        if df_ma is None or df_momentum is None:
            print(f" 缺少数据")
            return None

        # 2. 计算平均最大回撤
        print(f' \n2. 计算平均最大回撤')
        ma_avg_dd = df_ma['最大回撤'].mean()
        momentum_avg_dd = df_momentum['最大回撤'].mean()
        print(f' 均线策略平均最大回撤: {ma_avg_dd:.2%}')
        print(f' 动量策略平均最大回撤: {momentum_avg_dd:.2%}')

        # 3. 准备数据 (按回撤排序)
        print(f' \n3. 准备数据')

        # 均线策略按回撤排序
        ma_sorted = df_ma.sort_values('最大回撤', ascending=True)
        momentum_sorted = df_momentum.sort_values('最大回撤', ascending=True)

        # 取前20只股票
        ma_top = ma_sorted.head(20)
        momentum_top = momentum_sorted.head(20)
        print(f" 均线策略回撤范围: {ma_top['最大回撤'].min():.2%} ~ {ma_top['最大回撤'].max():.2%}")
        print(f" 动量策略回撤范围: {momentum_top['最大回撤'].min():.2%} ~ {momentum_top['最大回撤'].max():.2%}")

        # 4. 创建图表
        print(f" \n4. 创建图表")
        fig, axes = plt.subplots(1,2,figsize=(14,6))
        fig.suptitle("策略回撤曲线对比", fontsize=16, fontweight='bold')

        # ====================子图1. 均线策略回撤=================
        print(f" \n 绘制均线策略回撤曲线")
        ax1 = axes[0]

        x = range(len(ma_top))
        y = ma_top['最大回撤'].values

        ax1.bar(x, y, color='red', alpha=0.7)
        ax1.axhline(y=ma_avg_dd, color='darkred', linestyle='--', linewidth=2,
                    label=f"平均回撤: {ma_avg_dd:.2%}")

        ax1.set_xticks(x)
        ax1.set_xticklabels(ma_top['股票代码'], rotation=45, ha='right', fontsize=9)
        ax1.set_ylabel('最大回撤', fontsize=10)
        ax1.set_title('均线策略 - 各股票最大回撤', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        # ==================子图2: 动量策略回撤============================
        print(f' \n 绘制动量策略回撤曲线')
        ax2 = axes[1]

        x = range(len(momentum_top))
        y = momentum_top['最大回撤'].values

        ax2.bar(x,y,color='orange', alpha=0.7)
        ax2.axhline(y=momentum_avg_dd, color='darkorange', linestyle='--', linewidth=2,
                    label=f"平均回撤: {momentum_avg_dd}")

        ax2.set_xticks(x)
        ax2.set_xticklabels(momentum_top['股票代码'], rotation=45, ha='right', fontsize=9)
        ax2.set_ylabel('最大回撤', fontsize=10)
        ax2.set_title('动量策略 - 各股票最大回撤', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)

        # 5. 显示图表
        if show:
            print(f" \n 显示图表........................")
            plt.show()
        else:
            plt.close(fig)

        print(f" \n" + '-' * 80)
        print(f" 方法4完成: 回撤曲线绘制成功")
        return fig

    def plot_metrics_comparison(self, df_ma, df_momentum, show=True):
        """绘制均线策略和动量策略的绩效指标对比图"""
        print(f'\n' +'=' * 80)
        print(f' 方法5: 绘制绩效指标对比图')
        print(f"=" * 80)

        # 1. 检查数据
        print(f" \n1. 检查数据")
        if df_ma is None or df_momentum is None:
            print(f" 检查数据")
            return None

        # 2. 计算各项指标的平均值
        print(f' \n2. 计算各项指标的平均值')
        metrics = {
            '年化收益率': [
                df_ma['策略年化收益'].mean() if '策略年化收益' in df_ma.columns else df_ma['策略总收益'].mean(),
                df_momentum['策略年化收益'].mean() if '策略年化收益' in df_momentum.columns else df_momentum['策略总收益'].mean(),
            ],
            '夏普比率': [
                df_ma['夏普比率'].mean(),
                df_momentum['夏普比率'].mean()
            ],
            '胜率': [
                df_ma['胜率'].mean(),
                df_momentum['胜率'].mean()
            ],
            '最大回撤': [
                df_ma['最大回撤'].mean(),
                df_momentum['最大回撤'].mean()
            ]
        }

        # 显示计算结果
        print(f" 均线策略 - 年化收益率: {metrics['年化收益率'][0]:.2%}, 夏普: {metrics['夏普比率'][0]:.4f},"
              f"胜率: {metrics['胜率'][0]:.2%}, 最大回撤: {metrics['最大回撤'][0]:.2%}")
        print(f" 动量策略 - 年化收益率: {metrics['年化收益率'][1]:.2%}, 夏普: {metrics['夏普比率'][1]:.4f},"
              f"胜率: {metrics['胜率'][1]:.2%}, 最大回撤: {metrics['最大回撤'][1]:.2%}")

        # 3. 创建图表
        print(f" \n3. 创建图表")
        fig, axes = plt.subplots(2,2, figsize=(14,12))
        fig.suptitle("策略绩效指标对比", fontsize=16, fontweight='bold')

        strategy_names = ['均线策略', '动量策略']

        # ======================子图1: 年化收益率对比 ===================
        print(f' \n. 绘制年化收益率对比图')
        ax1 = axes[0,0]

        bars1 = ax1.bar(strategy_names, metrics['年化收益率'], color=['blue', 'orange'], alpha=0.7)
        ax1.set_ylabel('年化收益率', fontsize=12)
        ax1.set_title('年化收益率对比', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')

        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                     f"{height:.2%}", ha='center', va='bottom', fontsize=10)


        # ============================子图2: 夏普比率对比 =========================
        print(f' \n 绘制夏普比率对比图')
        ax2 = axes[0,1]
        bars2 = ax2.bar(strategy_names, metrics['夏普比率'], color=['blue', 'orange'], alpha=0.7)
        ax2.set_ylabel('夏普比率', fontsize=12)
        ax2.set_title('夏普比率对比', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')

        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                     f"{height:.4f}", ha='center', va='bottom', fontsize=10)

        # ======================子图3: 胜率对比======================
        print(f' \n 绘制胜率对比图')
        ax3 = axes[1,0]
        bars3 = ax3.bar(strategy_names, metrics['胜率'], color=['blue', 'orange'], alpha=0.7)
        ax3.set_ylabel('胜率', fontsize=12)
        ax3.set_title('胜率对比', fontsize=12)
        ax3.grid(True, alpha=0.3, axis='y')

        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                     f"{height:.2%}", ha='center', va='bottom', fontsize=10)

        # =====================子图4: 最大回撤对比 ===================
        print(f' \n 绘制最大回撤对比图')
        ax4 = axes[1,1]

        # 最大回撤取绝对值显示 (负数越大风险越高)
        bars4 = ax4.bar(strategy_names, metrics['最大回撤'], color=['blue', 'orange'], alpha=0.7)
        ax4.set_ylabel('最大回撤', fontsize=12)
        ax4.set_title('最大回撤对比 (越小越好)', fontsize=12)
        ax4.grid(True, alpha=0.3, axis='y')

        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width() / 2, height + 0.01,
                     f"{height:.2%}", ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.subplots_adjust(top=0.93)

        # 4. 显示图表
        if show:
            print(f" \n 显示图表....................")
            plt.show()
        else:
            plt.close(fig)

        print(f"\n" + '=' * 80)
        print(f" 方法5完成: 绩效指标对比图绘制成功")
        return fig

    def generate_performance_dashboard(self, df_ma, df_momentum, show=True):
        """生成完整绩效分析图表 (组合所有图表)"""
        print(f'\n' + '=' * 80)
        print(f" 方法6: 生成完整绩效分析图表")
        print(f'=' * 80)

        # 1. 检查数据
        print(f" \n1. 检查数据")
        if df_ma is None or df_momentum is None:
            print(f" 没有数据")
            return None

        # 2. 计算各项指标
        print(f' \n2. 计算各项指标')

        # 均线策略指标
        ma_avg_return = df_ma['策略总收益'].mean()
        ma_avg_sharpe = df_ma['夏普比率'].mean()
        ma_avg_winrate = df_ma['胜率'].mean()
        ma_avg_dd = df_ma['最大回撤'].mean()
        ma_avg_benchmark = df_ma['基准总收益'].mean()

        # 动量策略指标
        momentum_avg_return = df_momentum['策略总收益'].mean()
        momentum_avg_sharpe = df_momentum['夏普比率'].mean()
        momentum_avg_winrate = df_momentum['胜率'].mean()
        momentum_avg_dd = df_momentum['最大回撤'].mean()
        momentum_avg_benchmark = df_momentum['基准总收益'].mean()

        print(f' 均线策略 - 收益: {ma_avg_return:.2%}, 夏普:{ma_avg_sharpe:.4f}, 胜率:{ma_avg_winrate:.2%}, '
              f'回撤: {ma_avg_dd:.2%}')
        print(f' 动量策略 - 收益: {momentum_avg_return:.2%}, 夏普:{momentum_avg_sharpe:.4f}, '
              f'胜率:{momentum_avg_winrate:.2%}, 回撤: {momentum_avg_dd:.2%}')


        # 3. 创建图表 (3 x 2 布局)
        print(f' \n3. 创建完整仪表盘')
        fig = plt.figure(figsize=(16,14))
        fig.suptitle("策略绩效完整分析仪表盘", fontsize=18, fontweight='bold')

        # 使用GridSpec 创建更灵活的布局
        gs = fig.add_gridspec(3,2,hspace=0.3, wspace=0.3)

        # =============================子图1: 净值曲线 ========================
        print(f' \n 绘制净值曲线')
        ax1 = fig.add_subplot(gs[0,1])

        # 创建模拟净值数据
        x_ma = range(len(df_ma))
        x_momentum = range(len(df_momentum))

        ma_nav = np.linspace(1, 1 + ma_avg_return, len(df_ma))
        momentum_nav = np.linspace(1,1 + momentum_avg_return, len(df_momentum))

        # 添加随机波动
        np.random.seed(42)
        ma_nav = ma_nav * (1 + np.random.normal(0, 0.2, len(df_ma)))
        momentum_nav = momentum_nav * (1 + np.random.normal(0, 0.3, len(df_momentum)))

        ax1.plot(x_ma, ma_nav, linewidth=2, color='green', label='均线策略')
        ax1.plot(x_momentum, momentum_nav, linewidth=2, color='orange', label='动量策略')
        ax1.axhline(y=1, color='red', linestyle='-', linewidth=1, alpha=0.5)
        ax1.set_title("策略净值曲线对比", fontsize=14)
        ax1.set_xlabel('交易日', fontsize=10)
        ax1.set_ylabel('净值', fontsize=10)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # =======================子图2: 收益对比 ========================
        print(f" \n 绘制收益对比图")
        ax2 = fig.add_subplot(gs[1,0])
        strategies = ['均线策略', '动量策略']
        returns = [ma_avg_return, momentum_avg_return]

        bars = ax2.bar(strategies, returns, color=['green', 'orange'], alpha=0.7)
        ax2.set_ylabel('平均收益率', fontsize=10)
        ax2.set_title("策略收益对比", fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')

        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                     f"{height:.2%}", ha='center', va='bottom', fontsize=10)

        # ============================子图3: 夏普比率对比 ==================
        print(f" \n 绘制夏普比率对比图")
        ax3 = fig.add_subplot(gs[1,1])
        sharpe = [ma_avg_sharpe, momentum_avg_sharpe]

        bars = ax3.bar(strategies, sharpe, color=['green', 'orange'], alpha=0.7)
        ax3.set_ylabel("夏普比率", fontsize=10)
        ax3.set_title("风险调整后收益对比", fontsize=10)
        ax3.grid(True, alpha=0.3, axis='y')

        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2, height + 0.01,
                     f"{height:.2%}", ha='center', va='bottom', fontsize=10)


        # ==================子图4: 胜率与回撤对比 ==================
        print(f' \n 绘制胜率与回撤对比图')
        ax4 = fig.add_subplot(gs[2,0])
        x = np.arange(len(strategies))
        width = 0.35

        winrate = [ma_avg_winrate, momentum_avg_winrate]
        drawdown = [ma_avg_dd, momentum_avg_dd]

        bars1 = ax4.bar(x - width/2, winrate, width, label='胜率', color='blue', alpha=0.7)
        bars2 = ax4.bar(x + width/2, drawdown, width, label='最大回撤', color='red', alpha=0.7)

        ax4.set_xticks(x)
        ax4.set_xticklabels(strategies)
        ax4.set_ylabel('比率', fontsize=10)
        ax4.set_title('胜率与最大回撤对比', fontsize=10)
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')

        for bar in bars1:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width() / 2, height + 0.01,
                     f"{height:.2%}", ha='center', va='bottom', fontsize=10)

        for bar in bars2:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width() / 2, height + 0.01,
                     f"{height:.2%}", ha='center', va='bottom', fontsize=10)


        # ===================子图5: 绩效汇总表 ========================
        print(f" \n 绘制绩效汇总表")
        ax5 = fig.add_subplot(gs[2,1])
        ax5.axis('off')

        summary_text = "策略绩效汇总表\n\n"
        summary_text += f"{'指标':<15} {'均线策略':>15} {'动量策略':>15} \n"
        summary_text += '-' * 50 + '\n'
        summary_text += f"{'平均收益':<15} {ma_avg_return:>14.2%} {momentum_avg_return:>14.2%} \n"
        summary_text += f"{'夏普比率':<15} {ma_avg_sharpe:>14.4f} {momentum_avg_sharpe:>14.4f} \n"
        summary_text += f"{'胜率':<15} {ma_avg_winrate:>14.2%} {momentum_avg_winrate:>14.2%} \n"
        summary_text += f"{'最大回撤':<15} {ma_avg_dd:>14.2%} {momentum_avg_dd:>14.2%} \n"
        summary_text += f"{'跑赢基准':<15} {ma_avg_benchmark:>14.2%} {momentum_avg_benchmark:>14.2%} \n"

        ax5.text(0.05, 0.95, summary_text, transform=ax5.transAxes,
                 fontsize=12, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

        plt.tight_layout()
        plt.subplots_adjust(top=0.95)

        # 4. 显示图表
        if show:
            print(f" \n 显示完整仪表盘......................")
            plt.show()
        else:
            plt.close(fig)

        print(f"\n" + '=' * 80)
        print(f" 方法6完成: 完整绩效分析图表生成成功")
        return fig

    def save_all_charts(self, df_ma, df_momentum):
        """保存所有绩效分析图表"""
        print(f'\n' + '=' * 80)
        print(f" 方法7: 保存所有图表")
        print(f'=' * 80)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")

        # 1. 创建保存目录
        print(f" \n1. 创建保存目录")
        save_dir = self.chart_dir / f"绩效图表_{timestamp}"
        save_dir.mkdir(parents=True, exist_ok=True)
        print(f" 保存目录: {save_dir}")

        saved_files = []

        # 2. 保存净值曲线图
        print(f" \n2. 保存净值曲线图")
        fig1 = self.plot_networth_curve(df_ma, df_momentum, show=True)
        if fig1:
            file_path = save_dir / "净值曲线对比图.png"
            fig1.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close(fig1)
            print(f" 已保存: {file_path.name}")
            saved_files.append(str(file_path))

        # 3. 保存回撤曲线图
        print(f" \n3. 保存回撤曲线图")
        fig2 = self.plot_drawdown_curve(df_ma, df_momentum, show=True)
        if fig2:
            file_path = save_dir / "回撤曲线对比图.png"
            fig2.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close(fig2)
            print(f' 已保存: {file_path.name}')
            saved_files.append(str(file_path))

        # 4. 保存绩效指标对比图
        print(f" \n4. 保存绩效指标对比图")
        fig3 = self.plot_metrics_comparison(df_ma, df_momentum, show=True)
        if fig3:
            file_path = save_dir / "绩效指标对比图.png"
            fig3.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close(fig3)
            print(f' 已保存: {file_path.name}')
            saved_files.append(str(file_path))

        # 5. 保存完整仪表盘
        print(f' \n5. 保存完整仪表盘')
        fig4 = self.generate_performance_dashboard(df_ma, df_momentum, show=True)
        if fig4:
            file_path = save_dir / "完整绩效仪表盘.png"
            fig4.savefig(file_path, dpi=150, bbox_inches='tight')
            plt.close(fig4)
            print(f' 已保存: {file_path.name}')
            saved_files.append(str(file_path))

        # 6. 显示保存结果
        print(f" \n6. 显示保存结果-----------------")
        print(f'=' * 80)
        print(f" \n方法7完成: 所有图表已保存")
        print(f'=' * 80)
        print(f" 保存目录: {save_dir}")
        print(f" 共保存: {len(save_dir)} 个图表")
        print(f" -净值曲线对比图.png")
        print(f" -回撤曲线对比图.png")
        print(f" -绩效指标对比图.png")
        print(f" -完整绩效仪表盘.png")

        return save_dir



if __name__ == "__main__":
    visualizer = PerformanceVisualizer()

    # 加载绩效数据
    df_ma, df_momentum = visualizer.load_performance_data()

    if df_ma is not None:
        print(f" 均线策略平均收益: {df_ma['策略总收益'].mean():.2%}")
    if df_momentum is not None:
        print(f" 动量策略平均收益: {df_momentum['策略总收益'].mean():.2%}")

    if df_ma is not None and df_momentum is not None:
        # 绘制净值曲线
        visualizer.plot_networth_curve(df_ma, df_momentum, save=True, show=True)

        # 绘制回撤曲线
        visualizer.plot_drawdown_curve(df_ma, df_momentum, show=True)

        # 绘制绩效指标对比图
        visualizer.plot_metrics_comparison(df_ma, df_momentum, show=True)

        # 生成完整绩效分析仪表盘
        visualizer.generate_performance_dashboard(df_ma, df_momentum, show=True)

        # 保存所有图表
        visualizer.save_all_charts(df_ma, df_momentum)


"""
## 第15天：绩效可视化

**任务目标**：
- 绘制净值曲线（均线策略 vs 动量策略对比）
- 绘制回撤曲线（各股票最大回撤分布）
- 绘制绩效指标对比图（年化收益率、夏普比率、胜率、最大回撤）
- 整理完整绩效分析图表仪表盘

**实现方案**：
1. **数据加载**：
   - 自动查找第8天均线策略回测结果（批量回测结果.xlsx）
   - 自动查找第10天动量策略回测结果（批量回测结果.xlsx）
   - 自动识别并转换收益数据格式（百分比转小数）

2. **净值曲线绘制**（1×2子图布局）：
   - **左图**：均线策略净值曲线（含基准净值对比）
   - **右图**：动量策略净值曲线（含基准净值对比）
   - 基于平均收益率生成模拟净值曲线（添加随机波动增强真实感）
   - 标注最终净值，红色虚线标记初始净值1.0

3. **回撤曲线绘制**（1×2子图布局）：
   - **左图**：均线策略各股票最大回撤柱状图（取前20只）
   - **右图**：动量策略各股票最大回撤柱状图（取前20只）
   - 标注平均回撤线，显示回撤分布范围

4. **绩效指标对比图**（2×2子图布局）：
   - **左上**：年化收益率对比柱状图（标注数值）
   - **右上**：夏普比率对比柱状图（标注数值）
   - **左下**：胜率对比柱状图（标注数值）
   - **右下**：最大回撤对比柱状图（标注数值，越小越好）

5. **完整绩效仪表盘**（3×2 GridSpec布局）：
   - **左上**：净值曲线对比（均线 vs 动量）
   - **中左**：收益对比柱状图
   - **中右**：夏普比率对比柱状图
   - **下左**：胜率与最大回撤对比双柱图
   - **下右**：绩效汇总表格（含平均收益、夏普比率、胜率、最大回撤、跑赢基准）

6. **结果保存系统**：
   - 保存净值曲线对比图（PNG格式）
   - 保存回撤曲线对比图（PNG格式）
   - 保存绩效指标对比图（PNG格式）
   - 保存完整绩效仪表盘图（PNG格式）
   - 所有图表自动保存到charts/绩效可视化/目录

**核心代码结构**：
```python
class PerformanceVisualizer:
    ├── __init__()                       # 初始化目录和字体
    ├── _setup_chinese_font()             # 配置中文字体
    ├── load_performance_data()           # 加载均线和动量策略结果
    ├── plot_networth_curve()             # 绘制净值曲线（1×2）
    ├── plot_drawdown_curve()             # 绘制回撤曲线（1×2）
    ├── plot_metrics_comparison()         # 绘制绩效指标对比图（2×2）
    ├── generate_performance_dashboard()  # 生成完整绩效仪表盘（3×2）
    └── save_all_charts()                 # 保存所有图表
```
"""