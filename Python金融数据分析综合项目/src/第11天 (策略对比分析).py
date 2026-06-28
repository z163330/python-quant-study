'''
第11天
					策略对比分析
-对比均线与动量策略表现
-分析不同市场阶段的表现差异

练习：
-输出策略对比表格
'''


import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
from IPython.core.pylabtools import figsize


class StrategyComparator:
    """策略对比分析器"""
    def __init__(self):
        """初始化策略对比分析器"""
        print("=" * 80)
        print(f" 方法1: 初始化策略对比分析器")
        print("=" * 80)

        # 1. 获取当前文件目录
        print(f" \n1. 获取当前文件目录")
        current_dir = Path(__file__).parent
        print(f' 当前文件目录: {current_dir}')

        # 2. 找到项目根目录
        print(f" \n2. 找到项目根目录")
        self.project_root = current_dir.parent
        print(f" 项目根目录: {self.project_root}")

        # 3. 设置数据目录 (获取均线和动量数据: 下面就是均线和动量)
        print(f" \n3. 设置数据目录")
        self.ma_result_dir = self.project_root / "data" / "策略结果"
        self.momentum_result_dir = self.project_root / "data" / "动量策略结果"
        print(f" 均线策略结果目录: {self.ma_result_dir}")
        print(f" 动量策略结果目录: {self.momentum_result_dir}")

        # 4. 设置输出目录
        print(f' \n4. 设置输出目录')
        self.output_dir = self.project_root / "data" / "策略对比"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f" 输出目录: {self.output_dir}")

        # 5. 设置图表目录
        print(f" \n5. 设置图表目录")
        self.charts_dir = self.project_root / "charts" / "策略对比"
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        print(f" 图表目录: {self.charts_dir}")

        # 6. 设置中文字体
        print(f" \n6. 设置中文字体")
        self._setup_chinese_font()

        # 7. 初始化结果存储
        print(f" \n7. 初始化结果存储")
        self.comparison_results = []

        print(f'\n' + "=" * 70)
        print(f" 方法1完成: 初始化成功")
        print(f'=' * 70)
        print(f" 均线策略目录: {self.ma_result_dir}")
        print(f" 动量策略目录: {self.momentum_result_dir}")
        print(f" 输出目录: {self.output_dir}")
        print(f" 图表目录: {self.charts_dir}")

    # 下面的代码是用绘制图表的时候使用.  很经常绘制图表没办法显示中文. 所以需要下面这些代码.
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
        """加载第8天的均线策略 和第10天的动量策略 的回测结果"""
        print(f" \n" + "=" * 80)
        print(f" 方法2: 加载策略回测结果")
        print('=' * 80)

        # 1. 查找最新的均线策略回测
        print(f" \n1. 查找均线策略结果")
        ma_folders = list(self.ma_result_dir.glob("回测结果_*"))
        if not ma_folders:
            print(f" 没有找到均线策略结果......")
            return None

        # 获取最新的文件夹
        latest_ma_folder = max(ma_folders, key=lambda x: x.stat().st_mtime)
        ma_file = latest_ma_folder / "批量回测结果.xlsx"
        print(f" 找到均线策略结果: {ma_file}")

        # 2. 加载均线策略数据
        print(f" \n2. 加载均线策略数据")
        try:
            df_ma = pd.read_excel(ma_file)
            df_ma.columns = df_ma.columns.str.strip()
            print(f' 均线策略数据形状: {df_ma.shape[0]}行 x {df_ma.shape[1]} 列')
            print(f" 股票数量: {len(df_ma)}")
            print(f' 列名: {df_ma.columns}')
        except Exception as e:
            print(f" 加载失败: {e}")
            return None

        # 3. 查找最新的动量策略结果
        print(f" \n3. 查找动量策略结果")
        momentum_folders = list(self.momentum_result_dir.glob("动量回测结果_*"))
        if not momentum_folders:
            print(f" 没有找到动量策略结果...........")
            return None

        # 获取最新的文件夹
        latest_momentum_folder = max(momentum_folders, key=lambda x: x.stat().st_mtime)
        momentum_file = latest_momentum_folder / "批量回测结果.xlsx"
        print(f" 找到动量策略结果: {momentum_file}")

        # 4. 加载动量策略数据
        print(f" \n4. 加载动量策略数据")
        try:
            df_momentum = pd.read_excel(momentum_file)
            df_momentum.columns= df_momentum.columns.str.strip()
            print(f" 动量策略数据形状: {df_momentum.shape[0]}行 x {df_momentum.shape[1]}列")
            print(f" 股票数量: {len(df_momentum)}")
            print(f' 列名: {df_momentum.columns}')
        except Exception as e:
            print(f'加载失败: {e}')
            return None

        # 5. 合并两个策略的数据
        print(f" \n5. 合并策略数据")

        # 重命名列以方便区分
        df_ma = df_ma.rename(columns={
            '策略总收益': '均线策略收益',
            '超额收益': '均线超额收益',
            '夏普比率': '均线夏普比率',
            '最大回撤': '均线最大回撤',
            '胜率': '均线胜率'
        })

        df_momentum = df_momentum.rename(columns={
            '策略总收益': '动量策略收益',
            '超额收益': '动量超额收益',
            '夏普比率': '动量夏普比率',
            '最大回撤': '动量最大回撤',
            '胜率': '动量胜率'
        })

        #合并
        df_merged = pd.merge(
            df_ma[['股票代码', '均线策略收益', '均线超额收益', '均线夏普比率', '均线最大回撤', '均线胜率']],
            df_momentum[['股票代码', '动量策略收益', '动量超额收益', '动量夏普比率', '动量最大回撤', '动量胜率']],
            on = '股票代码',
            how = 'inner'
        )

        print(f" 合并完成, 共同股票数量: {len(df_merged)}")
        print(f' 合并之后的列名: {df_merged.columns}')

        # 6. 计算差异
        print(f' \n6. 计算策略差异')
        df_merged['收益差异'] = df_merged['动量策略收益'] - df_merged['均线策略收益']
        df_merged['夏普差异'] = df_merged['动量夏普比率'] - df_merged['均线夏普比率']

        # 判断哪个策略更好
        df_merged['更优策略'] = df_merged.apply(
            lambda row: '均线'if row['均线策略收益'] > row['动量策略收益'] else "动量",
            axis=1
        )

        # 7. 统计哪个策略胜出
        ma_wins = (df_merged['更优策略'] == '均线').sum()
        momentum_wins = (df_merged['更优策略'] == '动量').sum()

        print(f" \n7. 策略胜出统计: ")
        print(f" 均线策略胜出: {ma_wins} 只股票")
        print(f" 动量策略胜出: {momentum_wins} 只股票")

        # 8 保存合并数据
        self.merged_df = df_merged
        print(f" \n8.  合并数据已保存到 self.merged_df")

        # 9. 显示前5行预览
        print(f" \n9. 合并数据预览 (前5行)")
        print(f' =' * 80)
        preview_cols = ['股票代码', '均线策略收益', '动量策略收益', '收益差异', '更优策略']
        print(df_merged[preview_cols].head(5).to_string())
        print('=' * 80)

        print(f" \n" + '=' * 80)
        print(f" 方法2完成: 策略结果加载成功")
        print(f" -" * 70)
        print(f" 共同股票数: {len(df_merged)}")
        print(f" 均线策略平均收益: {df_merged['均线策略收益'].mean():.2%}")
        print(f" 动量策略平均收益: {df_merged['动量策略收益'].mean():.2%}")

        return df_merged

    def generate_comparison_table(self):
        """生成策略对比表格"""
        print('\n' + "=" * 80)
        print(f" 方法3: 生成策略对比表格")
        print(f"=" * 80)

        # 1. 检查是否有数据
        if not hasattr(self, 'merged_df') or self.merged_df is None:
            print(f" 没有数据, 请先运行load_strategy_results()")
            return None

        df = self.merged_df

        # 2. 计算整体统计
        print(f" \n1. 整体统计汇总")
        print(f" =" * 70)

        ma_wins = (df['更优策略'] == '均线').sum()
        momentum_wins = (df['更优策略'] == '动量').sum()

        print(f" 共同股票数: {len(df)}")
        print(f" 均线策略平均收益: {df['均线策略收益'].mean():.2%}")
        print(f" 动量策略平均收益: {df['动量策略收益'].mean():.2%}")
        print(f" 平均收益差异: {df['收益差异'].mean():.2%}")
        print(f" 均线策略平均夏普: {df['均线夏普比率'].mean():.4f}")
        print(f" 动量策略平均夏普: {df['动量夏普比率'].mean():4f}")
        print(f" 均线策略平均最大回撤: {df['均线最大回撤'].mean():.2%}")
        print(f" 动量策略平均最大回撤: {df['动量最大回撤'].mean():.2%}")
        print(f" 均线策略胜出: {ma_wins} 只")
        print(f" 动量策略胜出: {momentum_wins} 只")

        # 3. 均线策略最佳股票
        print(f" \n2. 均线策略表现最好的前10名")
        print('=' * 70)
        df_ma_best = df.sort_values('均线策略收益', ascending=False).head(10)
        for i, row in df_ma_best.iterrows():
            print(f" {row['股票代码']}: 收益{row['均线策略收益']:.2%}, 夏普{row['均线夏普比率']:.4f}")

        # 4. 动量策略最佳股票
        print(f" \n3. 动量策略表现最好的前10名")
        print('-' * 70)
        df_momentum_best = df.sort_values('动量策略收益', ascending=False).head(10)
        for i, row in df_momentum_best.iterrows():
            print(f" {row['股票代码']}: 收益{row['动量策略收益']:.2%}, 夏普{row['动量夏普比率']:.4f}")

        # 5. 动量超越均线最多的股票
        print(f" \n4. 动量策略超越均线最多的前10名")
        print('-' * 70)
        df_diff = df.sort_values('收益差异', ascending=False).head(10)
        for i, row in df_diff.iterrows():
            print(f" {row['股票代码']}: 均线收益 {row['均线策略收益']:.2%}, 动量收益 {row['动量策略收益']:.2%},"
                  f"超越{row['收益差异']:.2%}")

        # 6. 均线超越动量最多的股票
        print(f" \n5. 均线策略超越动量最多的前10名")
        print('-' * 70)
        df_diff_ma = df.sort_values('收益差异', ascending=False).head(10)
        for i, row in df_diff_ma.iterrows():
            print(f" {row['股票代码']}: 均线收益 {row['均线策略收益']:.2%}, 动量收益 {row['动量策略收益']:.2%},"
                  f"超越{abs(row['收益差异']):.2%}")

        print(f" \n" +"-" *70)
        print(f' 方法4完成: 策略对比表格生成成功')
        print('=' * 70)

        return df

    def plot_comparison_charts(self, show=True):
        """绘制策略对比图表"""
        print('\n' + "=" * 80)
        print(f" 方法4: 绘制策略对比图表")
        print('=' * 80)

        # 1. 检查是否有数据
        if not hasattr(self, 'merged_df') or self.merged_df is None:
            print(f" 没有数据")
            return None

        df = self.merged_df

        # 2. 获取字体
        title_font = self.font_prop if hasattr(self, 'font_prop') else None

        # 3. 创建图表
        print(f' \n1. 创建对比图表')
        fig, axes = plt.subplots(2,2,figsize=(15,12))
        fig.suptitle("均线策略 VS 动量策略 - 对比分析", fontsize=16, fontweight='bold')

        # ====================子图1: 收益散点对比 ===============
        print(f" \n 绘制收益散点对比图")
        ax1 = axes[0,0]
        ax1.scatter(df['均线策略收益'], df['动量策略收益'], alpha=0.6, color='blue', s=50)

        # 添加对角线 (y=x)
        min_val = min(df['均线策略收益'].min(), df['动量策略收益'].min())
        max_val = max(df['均线策略收益'].max(), df['动量策略收益'].max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=1, label='收益相等线')

        ax1.set_xlabel('均线策略收益', fontsize=12)
        ax1.set_ylabel('动量策略收益', fontsize=12)
        ax1.set_title('策略收益对比散点图', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 统计落点
        above_count = (df['动量策略收益'] > df['均线策略收益']).sum()
        below_count = (df['动量策略收益'] < df['均线策略收益']).sum()
        ax1.text(0.05, 0.95, f"动量优于均线: {above_count}只\n均线优于动量: {below_count}只",
                 transform=ax1.transAxes, fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

        # ==================子图2: 收益差异柱状图 =========================
        print(f" \n 绘制收益差异柱状图")
        ax2 = axes[0,1]

        # 按收益差异排序, 取前15 名和后15名
        df_diff = df.sort_values('收益差异', ascending=False)
        top15 = df_diff.head(15)
        bottom15 = df_diff.tail(15)

        # 合并显示
        diff_plot = pd.concat([top15, bottom15])
        colors = ['green' if x > 0 else 'red' for x in diff_plot['收益差异']]
        ax2.barh(range(len(diff_plot)), diff_plot['收益差异'], color=colors, alpha=0.7)
        ax2.set_yticks(range(len(diff_plot)))
        ax2.set_yticklabels(diff_plot['股票代码'], fontsize=8)
        ax2.axvline(x=0, color='black', linewidth=0.5)
        ax2.set_xlabel('收益差异 (动量 - 均线)', fontsize=12)
        ax2.set_title('策略收益差异排名', fontsize=12)
        ax2.grid(True, alpha=0.3)

        # ================子图3: 平均指标对比柱状图=====================
        print(f" \n 绘制平均指标对比图")
        ax3 = axes[1,0]
        metrics = ['收益', '夏普比率', '胜率']
        ma_values = [
            df['均线策略收益'].mean(),
            df['均线夏普比率'].mean(),
            df['均线胜率'].mean()
        ]
        momentum_values = [
            df['动量策略收益'].mean(),
            df['动量夏普比率'].mean(),
            df['动量胜率'].mean()
        ]

        x = np.arange(len(metrics))
        width = 0.35

        bars1 = ax3.bar(x-width/2, ma_values, width, label='均线策略', color='blue', alpha=0.7)
        bars2 = ax3.bar(x+width/2, momentum_values, width, label='动量策略', color='orange', alpha=0.7)
        ax3.set_xticks(x)
        ax3.set_xticklabels(metrics)
        ax3.set_ylabel('数值', fontsize=12)
        ax3.set_title('平均指标对比', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        # 添加数值标签
        for bar in bars1:
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                     f"{bar.get_height():.2%}", ha='center', va='bottom', fontsize=9)
        for bar in bars2:
            ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                     f"{bar.get_height():.2%}", ha='center', va='bottom', fontsize=9)


        # ================子图4: 最大回撤对比======================
        print(f' \n 绘制最大回撤对比图')
        ax4 = axes[1,1]

        # 取前10 名股票的回撤对比
        top10_ma = df.nlargest(10, '均线策略收益')
        top10_ma = top10_ma[['股票代码', '均线最大回撤', '动量最大回撤']]

        x = np.arange(len(top10_ma))
        width = 0.35

        bars1 = ax4.bar(x-width/2, top10_ma['均线最大回撤'], width, label='均线策略', color='blue', alpha=0.7)
        bars2 = ax4.bar(x+width/2, top10_ma['动量最大回撤'], width, label='动量策略', color='orange', alpha=0.7)

        ax4.set_xticks(x)
        ax4.set_xticklabels(top10_ma['股票代码'], rotation=45, ha='right', fontsize=9)
        ax4.set_ylabel('最大回撤', fontsize=12)
        ax4.set_title('收益TOP10股票的最大回撤对比', fontsize=12)
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.subplots_adjust(top=0.93)

        # 4. 显示图表
        print(f" \n   显示图表")
        plt.show()
        plt.close(fig)

        print(f" \n" + "=" * 70)
        print(f" 方法4完成: 策略对比图表绘制成功")
        print('=' * 70)

        return fig

    def save_all_comparison_results(self):
        """保存所有对比结果 (表格, 图表, 报告)"""
        print('\n ' + '=' * 80)
        print(f" 方法5: 保存所有对比结果")
        print('=' * 80)

        # 1. 检查是否有数据
        if not hasattr(self, 'merged_df') or self.merged_df is None:
            print(f" 没有数据, ")
            return None

        df = self.merged_df
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")

        # 2. 创建保存目录
        print(f" \n1. 创建保存目录")
        save_dir = self.output_dir / f"策略对比结果_{timestamp}"
        save_dir.mkdir(parents=True, exist_ok=True)
        print(f" 创建目录: {save_dir}")

        saved_files = []

        # 3. 计算统计汇总
        print(f" \n2. 计算统计汇总")
        ma_wins = (df['更优策略'] == '均线').sum()
        momentum_wins = (df['更优策略'] == '动量').sum()


        # 直接创建列表, 每行是一个键值对
        summary_list = []
        summary_list.append(['共同股票数', len(df)])
        summary_list.append(['均线策略平均收益', f"{df['均线策略收益'].mean():.2%}" ])
        summary_list.append(['动量策略平均收益', f"{df['动量策略收益'].mean():.2%}"])
        summary_list.append(['平均收益差异', f"{df['收益差异'].mean():.2%}"])
        summary_list.append(['均线策略平均夏普', f"{df['均线夏普比率'].mean():.2%}"])
        summary_list.append(['动量策略平均夏普', f"{df['动量夏普比率'].mean():.2%}"])
        summary_list.append(['均线策略平均最大回撤', f"{df['均线最大回撤'].mean():.2%}"])
        summary_list.append(['动量策略平均最大回撤', f"{df['动量最大回撤'].mean():.2%}"])
        summary_list.append(['均线策略平均胜率', f"{df['均线胜率'].mean():.2%}"])
        summary_list.append(['动量策略平均胜率', f"{df['动量胜率'].mean():.2%}"])
        summary_list.append(['均线策略胜出股票数', f"{ma_wins} 只",])
        summary_list.append(['动量策略胜出股票数', f"{momentum_wins} 只"])



        summary_df = pd.DataFrame(summary_list, columns=['指标', '数值'])

        # 4. 保存汇总报告
        print(f" \n3. 保存汇总报告")
        summary_file = save_dir / "策略对比汇总.xlsx"
        summary_df.to_excel(summary_file, index=False)
        print(f" 已保存: {summary_file.name}")
        saved_files.append(str(summary_file))

        # 5. 保存详细对比数据
        print(f" \n 4. 保存详细对比数据")
        detailed_file = save_dir / "详细对比数据.xlsx"

        with pd.ExcelWriter(detailed_file, engine='openpyxl') as writer:
            # sheet 1: 全部对比数据
            df.to_excel(writer, sheet_name='全部对比数据', index=False)

            # sheet 2: 均线策略最佳10名
            ma_best = df.nlargest(10, '均线策略收益')[['股票代码', '均线策略收益', '均线夏普比率', '均线最大回撤', '均线胜率']]
            ma_best.to_excel(writer, sheet_name='均线最佳10名', index=False)

            # sheet 3: 动量策略最佳10名
            momentum_best = df.nlargest(10, '动量策略收益')[['股票代码', '动量策略收益', '动量夏普比率', '动量最大回撤', '动量胜率']]
            momentum_best.to_excel(writer, sheet_name='动量最佳10名', index=False)

            # sheet 4: 动量超越均线最多的10名
            diff_desc = df.nlargest(10, '收益差异')[['股票代码', '均线策略收益', '动量策略收益', '收益差异']]
            diff_desc.to_excel(writer, sheet_name='动量超越最多', index=False)

            # sheet 5: 均线超越动量最多的10名
            diff_asc = df.nsmallest(10, '收益差异')[['股票代码', '均线策略收益', '动量策略收益', '收益差异']]
            diff_asc.to_excel(writer, sheet_name='均线超越最多', index=False)

        print(f'已保存: {detailed_file.name}')
        saved_files.append(str(detailed_file))

        # 6. 保存图表
        print(f" \n5. 保存图表")
        chart_dir = save_dir / "均线VS动量图表"
        chart_dir.mkdir(parents=True, exist_ok=True)

        # 绘制并保存图表
        fig = self.plot_comparison_charts(show=False)
        if fig:
            chart_path = chart_dir / f"策略对比分析图.png"
            fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            print(f" 图表已保存: {chart_path}")
            saved_files.append(str(chart_path))

        # 7. 生成汇总报告
        print(f" \n6. 生成汇总报告")
        report_file = save_dir / "策略对比分析报告.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n' + '=' * 80)
            f.write("策略对比分析报告\n")
            f.write('\n' + '=' * 80)

            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d')}")

            f.write("1. 整体统计\n")
            f.write("=" * 80 + '\n')
            f.write(f" 共同股票数; {len(df)}\n")
            f.write(f" 均线策略平均收益: {df['均线策略收益'].mean():.2%}\n")
            f.write(f" 动量策略平均收益: {df['动量策略收益'].mean():.2%}\n")
            f.write(f" 平均收益差异: {df['收益差异'].mean():.2%}\n")

            f.write("2. 策略胜出统计\n")
            f.write('=' * 80 + '\n')
            f.write(f" 均线策略胜出: {ma_wins} 只\n")
            f.write(f" 动量策略胜出: {momentum_wins} 只\n\n")

            f.write("3. 均线策略最佳10名\n")
            f.write('=' * 80 + "\n")
            for i, row in df.nlargest(10, '均线策略收益').iterrows():
                f.write(f"{row['股票代码']}: 收益{row['均线策略收益']:.2%}, 夏普比率{row['均线夏普比率']:.4f}\n")

            f.write("4. 动量策略最佳10名\n")
            f.write('=' * 80 + "\n")
            for i, row in df.nlargest(10, '动量策略收益').iterrows():
                f.write(f"{row['股票代码']}: 收益{row['动量策略收益']:.2%}, 夏普比率{row['动量夏普比率']:.4f}\n")

        print(f' 已保存: {report_file.name}')
        saved_files.append(str(report_file))

        # 8. 显示保存结果
        print('\n' + '-' * 70)
        print(f" 方法5完成: 所有对比结果已保存")
        print('-' * 70)
        print(f" 保存目录: {save_dir}")
        print(f" - 策略对比汇总.xlsx")
        print(f" - 详细对比数据.xlsx")
        print(f" - 图表/策略对比分析图.png")
        print(f" - 策略对比分析报告.txt")
        print(f" 共保存: {len(saved_files)} 个文件")

        return save_dir



# 调用测试
if __name__ == "__main__":
    comparator = StrategyComparator()

    # 加载两个策略的结果
    df = comparator.load_strategy_results()

    # 生成对比表格 (打印)
    comparator.generate_comparison_table()

    # 绘制对比图表 (显示)
    comparator.plot_comparison_charts(show=True)

    # 保存所有结果
    save_dir = comparator.save_all_comparison_results()
    print(f" \n 所有结果已保存到: {save_dir}")



"""
## 第11天：策略对比分析

**任务目标**：
- 对比均线策略与动量策略表现
- 分析不同市场阶段下两种策略的优劣
- 输出策略对比表格和可视化图表
- 总结两种策略的适用场景

**实现方案**：
1. **数据加载与合并**：
   - 自动查找第8天生成的均线策略结果（策略结果/回测结果_*/批量回测结果.xlsx）
   - 自动查找第10天生成的动量策略结果（动量策略结果/动量回测结果_*/批量回测结果.xlsx）
   - 按股票代码合并两个策略的数据，计算收益差异和夏普差异

2. **核心对比指标**：
   - **收益对比**：均线策略收益 vs 动量策略收益
   - **夏普比率对比**：风险调整后收益的比较
   - **最大回撤对比**：策略风险控制能力比较
   - **胜率对比**：盈利交易日占比比较
   - **收益差异**：动量策略收益 - 均线策略收益

3. **可视化分析系统**（2×2子图布局）：
   - **左上**：收益散点对比图（红色虚线为收益相等线，标注策略胜出数量）
   - **右上**：收益差异排名柱状图（绿色为正、红色为负，显示前15名和后15名）
   - **左下**：平均指标对比柱状图（收益、夏普比率、胜率对比）
   - **右下**：收益TOP10股票的最大回撤对比（展示高收益股票的风险特征）

4. **策略对比表格**：
   - **整体统计汇总**：平均收益、平均夏普、平均回撤、策略胜出数量
   - **均线策略最佳10名**：按收益排序展示最佳股票
   - **动量策略最佳10名**：按收益排序展示最佳股票
   - **动量超越均线最多**：动量策略优势最大的股票
   - **均线超越动量最多**：均线策略优势最大的股票

5. **结果保存系统**：
   - 保存策略对比汇总Excel（统计指标汇总）
   - 保存详细对比数据Excel（5个sheet：全部对比、均线最佳10名、动量最佳10名、动量超越最多、均线超越最多）
   - 保存策略对比分析图表
   - 生成策略对比分析报告文本文件

**核心代码结构**：
```python
class StrategyComparator:
    ├── __init__()                       # 初始化目录和字体
    ├── _setup_chinese_font()             # 配置中文字体
    ├── load_strategy_results()           # 加载均线和动量策略结果
    ├── generate_comparison_table()       # 生成策略对比表格
    ├── plot_comparison_charts()          # 绘制策略对比图表（2×2）
    └── save_all_comparison_results()     # 保存所有对比结果
```
"""


