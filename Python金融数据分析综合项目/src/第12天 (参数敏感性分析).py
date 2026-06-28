'''
第12天
					参数敏感性分析
-分析参数变化对策略结果的影响
-识别过拟合风险

练习：
-绘制参数-收益关系图
'''

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib



class ParameterSensitivityAnalyzer:
    """参数敏感性分析器"""
    def __init__(self):
        """初始化参数敏感性分析器"""
        print('\n' + "=" * 80)
        print(f" 第12天: 方法1: 初始化参数敏感性分析器")
        print('=' * 80)

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

        # 4. 设置输出目录
        print(f" \n4. 设置输出目录")
        self.output_dir = self.project_root / "data" / "参数敏感性分析"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f" 输出目录: {self.output_dir}")

        # 5. 设置图表目录
        print(f" \n5. 设置图表目录")
        self.charts_dir = self.project_root / "charts" / "参数敏感性分析"
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        print(f" 图表目录: {self.charts_dir}")

        # 6. 配置中文字体
        print(f" \n6. 配置中文字体")
        self._setup_chinese_font()

        # 7. 初始化结果存储
        print(f" \n7. 初始化结果存储")
        self.sensitivity_results = []
        self.ma_sensitivity = None
        self.momentum_sensitivity = None

        print(f'\n' + '=' * 80)
        print(f' 方法1完成: 初始化成功')
        print(f" =" * 80)
        print(f" 均线策略目录: {self.ma_result_dir}")
        print(f" 动量策略目录: {self.momentum_result_dir}")
        print(f" 输出目录: {self.output_dir}")
        print(f" 图表目录: {self.charts_dir}")

    def _setup_chinese_font(self):
        """配置中文字体"""
        import matplotlib.font_manager as fm
        import os

        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simhei.ttf'
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
        print(f" 未找到中文字体, 使用默认字体")
        plt.rcParams['axes.unicode_minus'] = False

    def load_strategy_results(self):
        """加载均线策略的回测结果"""
        print('\n' + '=' * 80)
        print(f' 方法2: 加载策略回测结果')
        print('=' * 80)

        # 1. 查找均线策略结果文件夹
        print(f" \n1. 查找均线策略结果")
        ma_folders = list(self.ma_result_dir.glob("回测结果_*"))
        if not ma_folders:
            print(f" 没有找到均线策略结果")
            return None

        # 2. 获取最新的文件夹
        print(f' \n2. 取最新文件夹')
        latest_ma_folder = max(ma_folders, key=lambda x: x.stat().st_mtime)
        print(f" 找到文件夹:{latest_ma_folder}")

        # 3. 读取批量回测结果
        batch_file = latest_ma_folder / "批量回测结果.xlsx"
        if not batch_file.exists():
            print(f" 没有找到批量回测结果文件")
            return None

        print(f" 找到文件: {batch_file.name}")

        # 4. 加载数据
        df_ma = pd.read_excel(batch_file)
        df_ma.columns = df_ma.columns.str.strip()

        print(f' 数据形状: {df_ma.shape[0]}行 x {df_ma.shape[1]}列')
        print(f' 列名: {list(df_ma.columns)}')

        # 5. 保存到对象
        self.ma_results = df_ma
        print(f" \n" + "=" * 80)
        print(f" 方法2加载均线策略完成")
        return df_ma

    def analyze_ma_sensitivity(self):
        """分析均线策略的参数敏感性"""
        print('\n' + '=' * 80)
        print(f" \n 方法3: 析均线策略的参数敏感性")
        print('=' * 80)

        # 1. 检查是否有数据
        if not hasattr(self, 'ma_results') or self.ma_results is None:
            print(f" 没有数据")
            return None

        df = self.ma_results.copy()

        # ========添加数据转换==============
        # 检查收益数据是否异常
        if df['策略总收益'].max() > 1:
            print(f" 检测到收益数据异常 (最大值{df['策略总收益'].max()}), 正在转换.......")
            df['策略总收益'] = df['策略总收益'] / 100
            print(f" 转换后最大值: {df['策略总收益'].max():.2%}")
        # ===========================================

        # 2. 检查是否有参数列
        print(f" \n1. 检查参数列")
        if '短期均线' not in df.columns or '长期均线' not in df.columns:
            print(f" 没有找到参数列 (短期均线, 长期均线)")
            print(f" 当前列名: {list(df.columns)}")
            return None
        print(f" 找到参数列: 短期均线, 长期均线")

        # 3. 按短期均线分组统计
        print(f" \n2. 按短期均线分组统计")
        short_group = df.groupby('短期均线')['策略总收益'].agg(['mean', 'std', 'count'])
        short_group.columns = ['平均收益', '标准差', '数量']
        print(f" {short_group}")

        # 4. 按长期均线分组统计
        print(f" \n3. 按长期均线分组统计")
        long_group = df.groupby('长期均线')['策略总收益'].agg(['mean', 'std', 'count'])
        long_group.columns = ['平均收益', '标准差', '数量']
        print(f" {long_group}")

        # 5. 找出最佳参数
        print(f" \n4. 找出最佳参数组合")
        best_idx = df['策略总收益'].idxmax()
        best_row = df.loc[best_idx]
        print(f" 最佳短期均线: {best_row['短期均线']}")
        print(f" 最佳长期均线: {best_row['长期均线']}")
        print(f" 最佳收益: {best_row['策略总收益']:.2%}")

        # 6. 计算收益波动范围
        print(f" \n5. 收益波动范围")
        max_return = df['策略总收益'].max()
        min_return = df['策略总收益'].min()
        mean_return = df['策略总收益'].mean()
        std_return = df['策略总收益'].std()

        print(f" 最高收益: {max_return:.2%}")
        print(f" 最低收益: {min_return:.2%}")
        print(f" 平均收益: {mean_return:.2%}")
        print(f" 标准差: {std_return:.4f}")

        # 7. 保存结果
        self.ma_sensitivity = {
            'best_short': best_row['短期均线'],
            'best_long': best_row['长期均线'],
            'best_return': best_row['策略总收益'],
            'max_return': max_return,
            'min_return': min_return,
            'mean_return': mean_return,
            'std_return': std_return,
            'short_group': short_group,
            'long_group': long_group
        }

        print(f" \n" + "=" * 80)
        print(f" 方法3完成: 均线策略参数敏感性分析成功")
        return self.ma_sensitivity

    def plot_ma_sensitivity(self, save=True, show=True):
        """绘制均线策略的参数-收益关系图"""
        print('\n' + '=' * 80)
        print(f" 方法4: 绘制参数-收益关系图")
        print('=' * 80)

        # 1. 检查是否有数据
        if not hasattr(self, 'ma_results') or self.ma_results is None:
            print(f" 没有数据, ")
            return None

        df = self.ma_results

        # 2. 获取字体
        title_font = self.font_prop if hasattr(self, 'font_prop') else None

        # 3. 创建图表
        print(f' \n1. 创建图表')
        fig, axes = plt.subplots(2,2,figsize=(14,12))
        fig.suptitle("均线策略-参数敏感分析", fontsize=16, fontweight='bold')

        # ===================子图1. 短期均线 VS 收益============================
        print(f" 绘制短期均线 VS 收益图")
        ax1 = axes[0,0]

        short_group = df.groupby('短期均线')['策略总收益'].mean()
        ax1.plot(short_group.index, short_group.values, 'o-', color='blue', linewidth=2, markersize=8)
        ax1.set_xlabel('短期均线天数', fontsize=12)
        ax1.set_ylabel('平均策略收益', fontsize=12)
        ax1.set_title('短期均线参数对收益的影响', fontsize=12)
        ax1.grid(True, alpha=0.3)

        # 标记最佳点
        best_short_idx = short_group.idxmax()
        best_short_val = short_group.max()
        ax1.scatter(best_short_idx, best_short_val, color='red', s=100, zorder=5, label=f"最佳:{best_short_idx}天")
        ax1.legend()

        # =========================子图2. 长期均线 VS 收益===========================
        print(f' \n 绘制长期均线 VS 收益图')
        ax2 = axes[0,1]
        long_group = df.groupby('长期均线')['策略总收益'].mean()
        ax2.plot(long_group.index, long_group.values, 's-', color='green', linewidth=2, markersize=8)
        ax2.set_xlabel('长期均线天数', fontsize=12)
        ax2.set_ylabel('平均策略收益', fontsize=12)
        ax2.set_title('长期均线参数对收益的影响', fontsize=12)
        ax2.grid(True, alpha=0.3)

        # 标记最佳点
        best_long_idx = long_group.idxmax()
        best_long_val = long_group.max()
        ax2.scatter(best_long_idx, best_long_val, color='red', s=100, zorder=5, label=f"最佳: {best_long_idx}天")
        ax2.legend()

        # ====================子图3. 参数热力图=========================
        print(f" \n 绘制参数热力图")
        ax3 = axes[1,0]

        # 创建透视表
        pivot_table = df.pivot_table(
            values = '策略总收益',
            index = '短期均线',
            columns = '长期均线',
            aggfunc = 'mean'
        )

        # cmap = RdYlGn   l 是小写的L
        im = ax3.imshow(pivot_table.values, cmap='RdYlGn', aspect='auto')
        ax3.set_xticks(range(len(pivot_table.columns)))
        ax3.set_xticklabels(pivot_table.columns, rotation=45, ha='right')
        ax3.set_yticks(range(len(pivot_table.index)))
        ax3.set_yticklabels(pivot_table.index)
        ax3.set_xlabel('长期均线', fontsize=12)
        ax3.set_ylabel('短期均线', fontsize=12)
        ax3.set_title('参数组合收益热力图', fontsize=12)

        # 添加颜色条
        plt.colorbar(im, ax=ax3, label='策略收益')

        # =========================子图4. 收益分布箱线图=====================
        print(f" \n 绘制收益分布箱线图")
        ax4 = axes[1,1]

        # 按短期均线分组绘制箱线图
        short_values = [df[df['短期均线'] == s]['策略总收益'].values for s in sorted(df['短期均线'].unique())]
        bp = ax4.boxplot(short_values, tick_labels=sorted(df['短期均线'].unique()), patch_artist=True)

        # 设置箱线图颜色
        for box in bp['boxes']:
            box.set_facecolor('lightblue')
            box.set_alpha(0.7)

        ax4.set_xlabel('短期均线天数', fontsize=12)
        ax4.set_ylabel('策略收益', fontsize=12)
        ax4.set_title('不同短期均线的收益分布', fontsize=12)
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.subplots_adjust(top=0.93)

        # 4. 显示图表
        print(f' \n 显示图表')
        plt.show()
        plt.close(fig)

        print(f" \n" + '=' * 80)
        print(f" 方法4完成: 参数-收益关系图绘制成功")
        return fig

    def load_momentum_results(self):
        """加载动量策略的回测结果"""
        print('\n' + '=' * 80)
        print(f" 方法5: 加载动量策略回测结果")
        print('=' * 80)

        # 1. 查找动量策略结果文件夹
        print(f" \n1. 查找动量策略结果")
        momentum_folders = list(self.momentum_result_dir.glob('动量回测结果_*'))
        if not momentum_folders:
            print(f" 没有找到动量策略结果")
            return None

        # 2. 取最新的文件夹
        print(f" \n2. 取最新文件夹")
        latest_folder = max(momentum_folders, key=lambda x: x.stat().st_mtime)
        print(f' 找到文件夹: {latest_folder.name}')

        # 3. 读取批量回测结果
        batch_file = latest_folder / "批量回测结果.xlsx"
        if not batch_file.exists():
            print(f" 没有找到批量回测结果文件")
            return None
        print(f" 找到文件: {batch_file.name}")

        # 4. 加载数据
        df_momentum = pd.read_excel(batch_file)
        df_momentum.columns = df_momentum.columns.str.strip()
        print(f" 数据形状: {df_momentum.shape[0]}行 x {df_momentum.shape[1]}列")
        print(f" 列名: {list(df_momentum.columns)}")

        # 5. 保存到对象
        self.momentum_results = df_momentum
        print(f" \n" + '=' * 80)
        print(f" 方法5完成: 加载动量策略完成")
        return df_momentum

    def analyze_momentum_sensitivity(self):
        """分析动量策略的参数敏感性"""
        print('\n' + '=' * 80)
        print(f" 方法6: 分析动量策略的参数敏感性")
        print('=' * 80)

        # 1. 检查是否有数据
        if not hasattr(self, 'momentum_results') or self.momentum_results is None:
            print(f" 没有动量策略数据")
            return None

        df = self.momentum_results.copy()       # 使用副本,

        # ===============添加数据转换=====================
        if df['策略总收益'].max() > 1:
            print(f" 检测到收益数据异常: (最大值{df['策略总收益'].max()}), 正在转换...........")
            df['策略总收益'] = df['策略总收益'] / 100
            print(f" 转换后最大值: {df['策略总收益'].max():.2%}")
        # =============================================


        # 2. 检查是否有动量窗口列
        print(f" \n1. 检查参数列")
        if '动量窗口' not in df.columns:
            print(f" 没有找到参数列 (动量窗口)")
            print(f" 当前列名: {list(df.columns)}")
            return None

        print(f" 找到参数列: 动量窗口")

        # 3. 按动量窗口分组统计
        print(f" \n2. 按动量窗口分组统计")
        window_group = df.groupby('动量窗口')['策略总收益'].agg(['mean', 'std', 'count'])
        window_group.columns = ['平均收益', '标准差', '数量']
        print(f"{window_group}")

        # 4. 找出最佳参数
        print(f" \n3. 找出最佳参数")
        best_idx = df['策略总收益'].idxmax()
        best_row = df.loc[best_idx]
        print(f' 最佳动量窗口: {best_row["动量窗口"]} 天')
        print(f" 最佳收益: {best_row['策略总收益']:.2%}")

        # 5. 计算收益波动范围
        print(f" \n4. 收益波动范围")
        max_return = df['策略总收益'].max()
        min_return = df['策略总收益'].min()
        mean_return = df['策略总收益'].mean()
        std_return = df['策略总收益'].std()

        print(f" 最高收益: {max_return:.2%}")
        print(f" 最低收益: {min_return:.2%}")
        print(f" 平均收益: {mean_return:.2%}")
        print(f" 标准差: {std_return:.4f}")

        # 6. 保存结果
        self.momentum_sensitivity = {
            'best_window': best_row['动量窗口'],
            'best_return': best_row['策略总收益'],
            'max_return': max_return,
            'min_return': min_return,
            'mean_return': mean_return,
            'std_return': std_return,
            'window_group': window_group
        }

        print(f'\n' + '=' * 80)
        print(f" 方法6完成: 动量策略参数敏感性分析成功")
        return self.momentum_sensitivity

    def plot_momentum_sensitivity(self, show=True):
        """ 绘制动量策略的参数-收益关系图"""
        print('\n' + '=' * 80)
        print(f' 方法7:  绘制动量策略的参数-收益关系图')
        print('=' * 80)

        # 1. 检查数据是否存在
        if not hasattr(self, 'momentum_results') or self.momentum_results is None:
            print(f" 没有动量策略数据")
            return None
        df = self.momentum_results

        # 2. 获取字体
        title_font = self.font_prop if hasattr(self, 'font_prop') else None

        # 3. 创建图表
        print(f"\n1. 创建图表")
        fig, axes = plt.subplots(1, 2, figsize=(14,6))
        fig.suptitle("动量策略 - 参数敏感性分析", fontsize=16, fontweight='bold')

        # ===================子图1. 动量窗口 VS 收益=============================
        print(f" \n2. 绘制动量窗口 VS 收益")
        ax1 = axes[0]

        # 按动量窗口分组计算平均收益
        window_group = df.groupby('动量窗口')['策略总收益'].mean()

        ax1.plot(window_group.index, window_group.values, 'o-', color='blue', linewidth=2, markersize=8)
        ax1.set_xlabel('动量窗口 (天) ', fontsize=12)
        ax1.set_ylabel('平均策略收益', fontsize=12)
        ax1.set_title('动量窗口参数对收益的影响', fontsize=12)
        ax1.grid(True, alpha=0.3)

        #标记最佳点
        best_idx = window_group.idxmax()
        best_val = window_group.max()
        ax1.scatter(best_idx, best_val, color='red', s=100, zorder=5, label=f'最佳: {best_idx} 天')
        ax1.legend()

        # =============================子图2. 收益分布箱线图=========================
        print(f' \n3. 绘制收益分布箱线图')
        ax2 = axes[1]

        # 按动量窗口分组绘制箱线图
        window_values = [df[df['动量窗口'] == w]['策略总收益'].values for w in sorted(df['动量窗口'].unique())]
        bp = ax2.boxplot(window_values, tick_labels=sorted(df['动量窗口'].unique()), patch_artist=True)

        # 设置箱线图颜色
        for box in bp['boxes']:
            box.set_facecolor('lightgreen')
            box.set_alpha(0.7)

        ax2.set_xlabel('动量窗口 (天)', fontsize=12)
        ax2.set_ylabel('策略收益', fontsize=12)
        ax2.set_title('不同动量窗口的收益分布', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)

        # 4. 显示图表
        print(f' \n4. 显示图表')
        plt.show()
        plt.close(fig)

        print(f' \n' + '=' * 80)
        print(f" 方法7完成: 动量策略参数 - 收益关系图绘制成功")

        return fig

    def save_all_results(self):
        """ 保存所有的敏感性分析结果到excel 和图表"""
        print('\n' +'=' * 80)
        print(f" 方法8: 保存所有的敏感性分析结果和图表")
        print('=' *80)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")

        # 1. 创建保存项目
        print(f'\n1. 创建保存项目')
        save_dir = self.output_dir / f"敏感性分析结果_{timestamp}"
        save_dir.mkdir(parents=True, exist_ok=True)
        print(f" 保存项目: {save_dir}")

        saved_filed = []

        # 2. 保存均线策略敏感性分析结果
        print(f' \n2. 保存均线策略敏感性分析结果')
        if hasattr(self, 'ma_sensitivity') and self.ma_sensitivity is not None:
            # 保存均线策略汇总
            ma_summary = []
            ma_summary.append(['指标', '数值'])
            ma_summary.append(['最佳短期均线', self.ma_sensitivity['best_short']])
            ma_summary.append(['最佳长期均线', self.ma_sensitivity['best_long']])
            ma_summary.append(['最佳收益', f"{self.ma_sensitivity['best_return']:.2%}"])
            ma_summary.append(['最高收益', f"{self.ma_sensitivity['max_return']:.2%}"])
            ma_summary.append(['最低收益', f"{self.ma_sensitivity['min_return']:.2%}"])
            ma_summary.append(['平均收益', f"{self.ma_sensitivity['mean_return']:.2%}"])
            ma_summary.append(['标准差', f"{self.ma_sensitivity['std_return']:.4f}"])

            ma_summary_df = pd.DataFrame(ma_summary[1:], columns=ma_summary[0])
            ma_file = save_dir / "均线策略_敏感性分析.xlsx"

            with pd.ExcelWriter(ma_file, engine='openpyxl') as writer:
                ma_summary_df.to_excel(writer, sheet_name='敏感性汇总', index=False)
                # 保存短期均线分组
                if 'short_group' in self.ma_sensitivity:
                    self.ma_sensitivity['short_group'].to_excel(writer, sheet_name='短期均线分组')
                # 保存长期均线分组
                if 'long_group' in self.ma_sensitivity:
                    self.ma_sensitivity['long_group'].to_excel(writer, sheet_name='长期均线分组')
            print(f" 已保存: {ma_file.name}")
            saved_filed.append(str(ma_file))

            # 保存均线策略图表
            fig_ma = self.plot_ma_sensitivity(show=False)
            if fig_ma:
                chart_file = save_dir / "均线策略_参数敏感性分析图.png"
                fig_ma.savefig(chart_file, dpi=150, bbox_inches='tight')
                plt.close(fig_ma)
                print(f" 已保存: {chart_file.name}")
                saved_filed.append(str(chart_file))

        # 3. 保存动量策略敏感性分析结果
        print(f" \n3. 保存动量策略敏感性分析结果")
        if hasattr(self, 'momentum_sensitivity') and self.momentum_sensitivity is not None:
            # 保存动量策略汇总
            momentum_summary = []
            momentum_summary.append(['指标', '数值'])
            momentum_summary.append(['最佳动量窗口', self.momentum_sensitivity['best_window']])
            momentum_summary.append(['最佳收益', f"{self.momentum_sensitivity['best_return']:.2%}"])
            momentum_summary.append(['最高收益', f"{self.momentum_sensitivity['max_return']:.2%}"])
            momentum_summary.append(['最低收益', f"{self.momentum_sensitivity['min_return']:.2%}"])
            momentum_summary.append(['平均收益', f"{self.momentum_sensitivity['mean_return']:.2%}"])
            momentum_summary.append(['标准差', f"{self.momentum_sensitivity['std_return']:.4f}"])

            momentum_summary_df = pd.DataFrame(momentum_summary[1:], columns=momentum_summary[0])
            momentum_file = save_dir / "动量策略_敏感性分析.xlsx"

            with pd.ExcelWriter(momentum_file, engine='openpyxl') as writer:
                momentum_summary_df.to_excel(writer, sheet_name='敏感性汇总', index=False)
                # 保存窗口分组
                if 'window_group' in self.momentum_sensitivity:
                    self.momentum_sensitivity['window_group'].to_excel(writer, sheet_name='窗口分组')
            print(f" 已保存: {momentum_file.name}")
            saved_filed.append(str(momentum_file))

            # 保存动量策略图表
            fig_momentum = self.plot_momentum_sensitivity(show=False)
            if fig_momentum:
                chart_file = save_dir / "动量策略_参数敏感性分析图.png"
                fig_momentum.savefig(chart_file, dpi=150, bbox_inches='tight')
                plt.close(fig_momentum)
                print(f" 已保存: {chart_file.name}")
                saved_filed.append(str(chart_file))

        # 4. 生成汇总报告
        print(f" \n4. 生成汇总报告")
        report_file = save_dir / "参数敏感性分析报告.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('=' * 70 + '\n')
            f.write('参数敏感性分析报告\n')
            f.write('=' * 70 +'\n')

            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d')}\n\n")

            # 均线策略总结
            if hasattr(self, 'ma_sensitivity') and self.ma_sensitivity is not None:
                f.write('1. 均线策略\n')
                f.write('=' * 50 + '\n')
                f.write(f"最佳参数: MA{self.ma_sensitivity['best_short']} x MA{self.ma_sensitivity['best_long']}\n")
                f.write(f"最佳收益: {self.ma_sensitivity['best_return']:.2%}\n")
                f.write(f"平均收益: {self.ma_sensitivity['mean_return']:.2%}\n")
                f.write(f"收益标准差: {self.ma_sensitivity['std_return']:.4f}\n")
                f.write(f"收益范围: {self.ma_sensitivity['min_return']:.2%} ~ {self.ma_sensitivity['max_return']:.2%}\n\n")

            # 动量策略总结
            if hasattr(self, 'momentum_sensitivity') and self.momentum_sensitivity is not None:
                f.write(f"2. 动量策略\n")
                f.write('=' * 50 + '\n')
                f.write(f"最佳参数: {self.momentum_sensitivity['best_window']} 天\n")
                f.write(f"最佳收益: {self.momentum_sensitivity['best_return']:.2%}\n")
                f.write(f"平均收益: {self.momentum_sensitivity['mean_return']:.2%}\n")
                f.write(f"收益标准差: {self.momentum_sensitivity['std_return']:.4f}\n")
                f.write(f"收益范围: {self.momentum_sensitivity['min_return']:.2%} ~ {self.momentum_sensitivity['max_return']:.2%}\n\n")


            # 过拟合风险分析
            f.write(f"3. 过拟合风险分析\n")
            f.write('\n' + '=' * 50)

            if hasattr(self, 'ma_sensitivity') and self.ma_sensitivity is not None:
                ma_range = self.ma_sensitivity['max_return'] - self.ma_sensitivity['min_return']
                ma_mean = self.ma_sensitivity['mean_return']
                # 使用相对比例:  波动范围 / 平均收益 > 0.5 表示敏感
                if ma_mean > 0:
                    ma_sensitivity_ratio = ma_range / ma_mean
                    if ma_sensitivity_ratio > 0.5:
                        f.write(f" 均线策略: 参数变化对收益影响较大 (波动/平均={ma_sensitivity_ratio:.1f}), 存在过拟合风险\n ")
                    else:
                        f.write(f" 均线策略: 参数变化对收益影响较小 (波动/平均={ma_sensitivity_ratio:.1f}), 过拟合风险较低\n")
                else:
                    f.write(f' 均线策略: 平均收益为负, 参数敏感性分析参考意义有限\n')

            if hasattr(self, 'momentum_sensitivity') and self.momentum_sensitivity is not None:
                momentum_range = self.momentum_sensitivity['max_return'] - self.momentum_sensitivity['min_return']
                momentum_mean = self.momentum_sensitivity['mean_return']
                # 使用相对比例: 波动范围 / 平均收益 > 0.5 表示敏感
                if momentum_mean > 0:
                    momentum_sensitivity_ratio = momentum_range / momentum_mean
                    if momentum_sensitivity_ratio > 0.5:
                        f.write(f" 动量策略: 参数变化对收益影响较大 (波动/平均={momentum_sensitivity_ratio:.1f}), 存在过拟合风险\n")
                    else:
                        f.write(f" 动量策略: 参数变化对收益影响较小 (波动/平均={momentum_sensitivity_ratio:.1f}), 过拟合风险较低\n")
                else:
                    f.write(f" 动量策略: 平均收益为负, 参数敏感性分析参考意义有限\n")
        print(f' 已保存: {report_file.name}')
        saved_filed.append(str(report_file))

        # 5. 显示保存结果
        print('\n' + '=' * 70)
        print(f" 方法8完成: 所有敏感性分析结果已保存")
        print('=' * 70)
        print(f"保存目录: {save_dir}")
        print(f"共保存: {len(saved_filed)} 个文件")

        return save_dir

# 测试
if __name__ == "__main__":
    analyzer = ParameterSensitivityAnalyzer()

    # 加载均线策略数据
    df_ma = analyzer.load_strategy_results()
    if df_ma is not None:
        result_ma = analyzer.analyze_ma_sensitivity()
        # 绘制参数-收益关系图（只显示，不保存）
        analyzer.plot_ma_sensitivity(show=True)

    # 加载动量策略数据
    df_momentum = analyzer.load_momentum_results()
    if df_momentum is not None:
        # 分析动量策略参数敏感性
        result = analyzer.analyze_momentum_sensitivity()
        # 绘制动量策略参数 - 收益关系图
        analyzer.plot_momentum_sensitivity(show=True)

    # 保存所有结果
    analyzer.save_all_results()



"""
## 第12天：参数敏感性分析

**任务目标**：
- 分析参数变化对策略结果的影响
- 识别过拟合风险（参数微小变化导致收益大幅波动）
- 绘制参数-收益关系图（折线图、热力图、箱线图）
- 评估不同参数组合的稳定性

**实现方案**：
1. **数据加载**：
   - 自动查找第8天生成的均线策略回测结果（包含短期均线、长期均线、策略总收益等列）
   - 自动查找第10天生成的动量策略回测结果（包含动量窗口、策略总收益等列）
   - 加载批量回测结果Excel文件

2. **均线策略敏感性分析**：
   - **参数分组统计**：按短期均线分组计算平均收益、标准差；按长期均线分组统计
   - **最佳参数识别**：找出收益最高的短期均线和长期均线组合
   - **波动范围计算**：最高收益、最低收益、平均收益、标准差
   - **过拟合风险判断**：参数变化导致收益大幅波动即存在过拟合风险

3. **动量策略敏感性分析**：
   - **窗口分组统计**：按动量窗口分组计算平均收益、标准差
   - **最佳参数识别**：找出收益最高的动量窗口
   - **波动范围计算**：最高收益、最低收益、平均收益、标准差

4. **可视化分析系统**（均线策略2×2子图）：
   - **左上**：短期均线 VS 收益折线图（标记最佳参数点）
   - **右上**：长期均线 VS 收益折线图（标记最佳参数点）
   - **左下**：参数组合收益热力图（短期均线×长期均线，红绿渐变）
   - **右下**：不同短期均线的收益分布箱线图

5. **动量策略可视化**（1×2子图）：
   - **左图**：动量窗口 VS 收益折线图（标记最佳参数点）
   - **右图**：不同动量窗口的收益分布箱线图

6. **结果保存系统**：
   - 保存均线策略敏感性分析Excel（汇总指标、短期均线分组、长期均线分组）
   - 保存动量策略敏感性分析Excel（汇总指标、窗口分组）
   - 保存参数-收益关系图表
   - 生成参数敏感性分析报告（含过拟合风险评估）

**核心代码结构**：
```python
class ParameterSensitivityAnalyzer:
    ├── __init__()                       # 初始化目录和字体
    ├── _setup_chinese_font()             # 配置中文字体
    ├── load_strategy_results()           # 加载均线策略回测结果
    ├── analyze_ma_sensitivity()          # 分析均线策略参数敏感性
    ├── plot_ma_sensitivity()             # 绘制均线参数-收益关系图（2×2）
    ├── load_momentum_results()           # 加载动量策略回测结果
    ├── analyze_momentum_sensitivity()    # 分析动量策略参数敏感性
    ├── plot_momentum_sensitivity()       # 绘制动量参数-收益关系图（1×2）
    └── save_all_results()                # 保存所有分析结果
    ```
"""







