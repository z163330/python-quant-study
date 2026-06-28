'''
第14天
					风险分析
-分析回撤区间
-识别风险来源
-对比不同策略风险特征

练习：
-撰写简要风险分析说明
'''


import pandas as pd
import numpy as np
from pathlib import Path

class RiskAnalyzer:
    """风险分析器 - 每只股票都显示"""
    def __init__(self):
        """初始化风险分析器"""
        print(f"\n" + '=' * 80)
        print(f" 方法1: 初始化风险分析器")
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
        self.output_dir = self.project_root / "data" / "风险分析"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f" 输出目录: {self.output_dir}")

        # 5. 初始化结果存储
        print(f" \n5. 初始化结果存储")
        self.ma_risk = None
        self.momentum_risk = None

        print(f" \n" + '=' * 80)
        print(f" 方法1完成: 初始化完成")
        print(f"=" * 80)
        print(f" 均线策略目录: {self.ma_result_dir}")
        print(f" 动量策略目录: {self.momentum_result_dir}")
        print(f" 输出目录: {self.output_dir}")

    def load_risk_data(self):
        """加载均线策略和动量策略的回测数据"""

        print(f"\n" +'=' * 80)
        print(f' 方法2: 加载风险数据')
        print(f" \n" +"=" * 80)

        # 1. 加载均线策略结果
        print(f' \n1. 加载均线策略结果')
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
        print(f" 股票数量: {len(df_ma)}")

        # 2. 加载动量策略结果
        print(f" \n2. 加载动量策略结果")
        momentum_folders = list(self.momentum_result_dir.glob("动量回测结果_*"))

        if not momentum_folders:
            print(f" 没有找到动量策略结果")
            return None

        latest_momentum_folder = max(momentum_folders, key=lambda x: x.stat().st_mtime)
        momentum_file = latest_momentum_folder / "批量回测结果.xlsx"

        if not momentum_file.exists():
            print(f" 没有找到批量回测结果文件")
            return None

        df_momentun = pd.read_excel(momentum_file)
        df_momentun.columns = df_momentun.columns.str.strip()
        print(f" 动量策略数据: {df_momentun.shape[0]} 行 x {df_momentun.shape[1]}列")
        print(f" 股票数量: {len(df_momentun)}")

        # 3. 检查并转换收益数据
        print(f"\n3. 检查数据格式")
        if df_ma['策略总收益'].max() >1:
            print(f" 均线策略收益数据为百分比格式, 正在转换........")
            df_ma['策略总收益'] = df_ma['策略总收益'] / 100

        if df_momentun['策略总收益'].max() > 1:
            print(f" 动量策略收益数据为百分比格式, 正在转换.......")
            df_momentun['策略总收益'] = df_momentun['策略总收益'] / 100

        # 4. 显示数据预览
        print(f" \n4. 数据预览 (前10行)")
        print(f"=" * 50)
        print(f" 均线策略")
        print(df_ma[['股票代码', '策略总收益', '最大回撤', '夏普比率']].head())
        print(f" \n\n动量策略")
        print(df_momentun[['股票代码', '策略总收益', '最大回撤', '夏普比率']].head())

        # 5. 保存到对象
        self.df_ma = df_ma
        self.df_momentum = df_momentun

        print(f" \n" +'=' * 80)
        print(f' 方法2完成: 风险数据加载成功')
        print(f" 均线策略股票数: {len(df_ma)}")
        print(f" 动量策略股票数: {len(df_momentun)}")

        return df_ma, df_momentun

    def analyze_all_stocks_risk(self, df, strategy_name="策略"):
        """分析所有股票的风险"""
        print(f" \n" +'=' * 80)
        print(f" 方法3: 分析{strategy_name}所有股票风险")
        print('=' * 80)

        # 1. 检查数据
        print(f" \n1. 检查数据")
        if df is None:
            print(f" 没有数据")
            return None
        print(f" 股票数量: {len(df)}")

        # 2. 检查必要的列
        print(f" \n2. 检查必要的列")
        if '最大回撤' not in df.columns:
            print(f" 没有找到 '最大回撤' 列")
            return None
        if '股票代码' not in df.columns:
            print(f" 没有找到 '股票代码' 列")
            return None
        print(f" 找到 '股票代码' 和 '最大回撤' 列")

        # 3. 按最大回撤排序 (从低风险到高风险)
        # ascending=False: 回撤从大到小 (-5% > -10% > -20%), 低风险在前
        print(f" \n3. 按风险从低到高排序")
        df_sorted = df.sort_values('最大回撤', ascending=False).copy()
        print(f" 排序完成 (低风险 -> 高风险)")

        # 4. 添加风险等级
        print(f" \n4. 添加风险等级")

        def get_risk_level(drawdown):
            if drawdown < -0.30:
                return "🔴 高风险"
            elif drawdown < -0.20:
                return "🟠 中高风险"
            elif drawdown < -0.10:
                return "🟡 中等风险"
            else:
                return "🟢 低风险"

        df_sorted['风险等级'] = df_sorted['最大回撤'].apply(get_risk_level)
        print(f" 风险等级已添加")

        # 5. 添加排名
        print(f" \n5. 添加排名")
        df_sorted['排名'] = range(1, len(df_sorted) + 1)
        print(f" 共 {len(df_sorted)} 只股票")

        # 6. 统计各风险等级数量
        print(f" \n6. 风险等级统计")
        risk_counts = df_sorted['风险等级'].value_counts()
        for level, count in risk_counts.items():
            print(f" {level}: {count} 只股票")

        # 7. 显示所有股票 (从低到高风险)
        print(f" \n7. {strategy_name}所有股票风险排序 (从低风险 -> 高风险)")
        print('=' * 80)
        print(f" {'排名':<6} | {'股票代码':<10} | {'最大回撤':<12} | {'风险等级':<12}")
        print('-' * 80)

        for _, row in df_sorted.iterrows():
            print(f"{row['排名']:<6} {row['股票代码']:<10} {row['最大回撤']:>10.2%} {row['风险等级']:<12}")

        # 8. 风险范围
        print(f" \n8. 风险范围")
        min_risk = df_sorted['最大回撤'].max()  # 回撤最小 (风险最低)
        max_risk = df_sorted['最大回撤'].min()  # 回撤最大 (风险最高)
        print(f" 风险最低 (回撤最小) : {min_risk:.2%}")
        print(f" 风险最高 (回撤最大) : {max_risk:.2%}")
        print(f" 风险范围: {min_risk:.2%} 到 {max_risk:.2%}")

        # 9. 统计信息
        print(f" \n9. 统计汇总")
        avg_dd = df_sorted['最大回撤'].mean()
        print(f' 平均最大回撤: {avg_dd:.2%}')

        # 10. 显示低风险股票 (前10名)
        print(f" \n10. 低风险股票 (回撤最小前10名)")
        low_risk = df_sorted.head(10)
        for _, row in low_risk.iterrows():
            print(f"  - {row['股票代码']}: 回撤 {row['最大回撤']:.2%}")

        # 11. 显示最高风险股票 (后10名)
        print(f" \n11. 高风险股票 (回撤最大后10名)")
        high_risk = df_sorted.tail(10)
        for _, row in high_risk.iterrows():
            print(f"  - {row['股票代码']}: 回撤 {row['最大回撤']:.2%}")

        # 12. 保存到对象
        if strategy_name == "均线策略":
            self.ma_risk = df_sorted
        else:
            self.momentum_risk = df_sorted

        print(f" \n" + '=' * 80)
        print(f" 方法3完成: {strategy_name}风险分析成功")
        print(f" 风险范围: {min_risk:.2%} -> {max_risk:.2%}")

        return df_sorted

    def compare_risk_features(self, df_ma, df_momentum):
        """对比均线策略和动量策略的风险特征"""
        print(f'\n' + '=' * 80)
        print(f' 方法4: 对比策略风险特征')
        print(f" \n" + '=' * 80)

        # 1. 检查数据
        print(f' \n1. 检查数据')
        if df_ma is None or df_momentum is None:
            print(f" 缺少数据")
            return None
        print(f" 均线策略股票数: {len(df_ma)}")
        print(f" 动量策略股票数: {len(df_momentum)}")

        # 2. 计算均线策略风险指标
        print(f" \n2. 计算均线策略风险指标")
        ma_avg_dd = df_ma['最大回撤'].mean()
        ma_max_dd = df_ma['最大回撤'].min()     # 最差 (负数最小)
        ma_min_dd = df_ma['最大回撤'].max()     # 最好 (负数最大)

        # 找出高风险股票 (回撤 > 20%
        ma_high_risk = df_ma[df_ma['最大回撤'] < -0.20]
        ma_high_risk_count = len(ma_high_risk)

        print(f" 平均最大回撤: {ma_avg_dd:.2%}")
        print(f" 最差回撤: {ma_max_dd:.2%}")
        print(f" 最好回撤: {ma_min_dd:.2%}")
        print(f" 高风险股票(>20%): {ma_high_risk} 只")

        # 显示高风险股票代码
        if ma_high_risk_count > 0:
            print(f" \n 均线策略高风险股票列表:")
            for _, row in ma_high_risk.iterrows():
                print(f"  -  {row['股票代码']}: 回撤 {row['最大回撤']:.2%}")

        # 3. 计算动量策略风险指标
        print(f" \n2. 计算动量策略风险指标")
        momentum_avg_dd = df_momentum['最大回撤'].mean()
        momentum_max_dd = df_momentum['最大回撤'].min()  # 最差 (负数最小)
        momentum_min_dd = df_momentum['最大回撤'].max()  # 最好 (负数最大)

        # 找出高风险股票 (回撤 > 20%)
        momentum_high_risk = df_momentum[df_momentum['最大回撤'] < -0.20]
        momentum_high_risk_count = len(momentum_high_risk)

        print(f" 平均最大回撤: {momentum_avg_dd:.2%}")
        print(f" 最差回撤: {momentum_max_dd:.2%}")
        print(f" 最好回撤: {momentum_min_dd:.2%}")
        print(f" 高风险股票(>20%): {momentum_high_risk} 只")

        # 显示高风险股票代码
        if momentum_high_risk_count > 0:
            print(f" \n 动量策略高风险股票列表: ")
            for _, row in momentum_high_risk.iterrows():
                print(f"  - {row['股票代码']}: 回撤 {row['最大回撤']:.2%}")

        # 4. 创建对比表格
        print(f" \n4. 策略风险对比表")
        print('=' * 80)
        print(f" {'风险指标':<20} {'均线策略':>15} {'动量策略':>15}{'优劣':>10}")
        print(f'=' * 80)

        # 平均回撤 (越大越好, 因为负数越小越差)
        if ma_avg_dd > momentum_avg_dd:
            winner = "均线策略"
        else:
            winner = "动量策略"
        print(f'{"平均最大回撤":<20}{ma_avg_dd:>14.2%}{momentum_avg_dd:>14.2%}{winner:>10}')

        # 最差回撤 (越大越好)
        if ma_max_dd > momentum_max_dd:
            winner = "均线策略"
        else:
            winner = '动量策略'
        print(f" {'最差回撤':<20}{ma_max_dd:>14.2%}{momentum_max_dd:>14.2%}{winner:>10}")

        # 最高风险股票数 (越少越好)
        if ma_high_risk_count < momentum_high_risk_count:
            winner = "均线策略"
        else:
            winner = '动量策略'
        print(f" {'高风险股票数':<20}{ma_high_risk_count:>14}{momentum_high_risk_count:>14}{winner:>10}")
        print("=" *80)


        # 5. 风险对比结论
        print(f" \n5. 风险对比结论")

        if ma_avg_dd > momentum_avg_dd:
            print(f" 均线策略平均回撤更小, 风险控制更好")
        else:
            print(f" 动量策略平均回撤更小, 风险控制更好")

        if ma_high_risk_count < momentum_high_risk_count:
            print(f' 均线策略高风险股票更少, 更稳健')
        else:
            print(f' 动量策略高风险股票更少, 更稳健')

        # 6. 找出最差股票
        print(f" \n6. 最差表现股票")
        ma_worst_idx = df_ma['最大回撤'].idxmin()
        ma_worst = df_ma.loc[ma_worst_idx]
        momentum_worst_idx = df_momentum['最大回撤'].idxmin()
        momentum_worst = df_momentum.loc[momentum_worst_idx]

        print(f" 均线策略最差: {ma_worst['股票代码']} (回撤 {ma_worst['最大回撤']:.2%})")
        print(f" 动量策略最差: {momentum_worst['股票代码']} (回撤 {momentum_worst['最大回撤']:.2%})")

        # 7. 找出最佳股票
        print(f" \n7. 最佳表现股票 (回撤最小)")
        ma_best_idx = df_ma['最大回撤'].idxmax()
        ma_best = df_ma.loc[ma_best_idx]
        momentum_best_idx = df_momentum['最大回撤'].idxmax()
        momentum_best = df_momentum.loc[momentum_best_idx]

        print(f" 均线策略最佳: {ma_best['股票代码']} (回撤{ma_best['最大回撤']:.2%})")
        print(f" 动量策略最佳: {momentum_best['股票代码']} (回撤{momentum_best['最大回撤']:.2%})")

        # 8. 保存对比结果
        comparison = {
            '均线策略': {
                '股票数量': len(df_ma),
                '平均最大回撤': ma_avg_dd,
                '最差回撤': ma_max_dd,
                '最好回撤': ma_min_dd,
                '高风险股票数': ma_high_risk_count,
                '高风险股票列表': ma_high_risk['股票代码'].tolist(),
                '最差股票': ma_worst['股票代码'],
                '最佳股票': ma_best['股票代码']
            },
            '动量策略': {
                '股票数量': len(df_momentum),
                '平均最大回撤': momentum_avg_dd,
                '最差回撤': momentum_max_dd,
                '最好回撤': momentum_min_dd,
                '高风险股票数': momentum_high_risk_count,
                '高风险股票列表': momentum_high_risk['股票代码'].tolist(),
                '最差股票': momentum_worst['股票代码'],
                '最佳股票': momentum_best['股票代码']
            }
        }

        self.risk_comparison = comparison
        print(f"\n" + '=' * 80)
        print(f' 方法4完成: 策略分析对比成功')

        return comparison

    def generate_risk_report(self, ma_risk, momentum_risk, comparison):
        """生产风险分析报告"""
        print(f" \n" + '=' * 80)
        print(f" \n5: 生产风险分析报告")
        print('=' * 80)

        from datetime import datetime

        # 1. 检查数据
        print(f' \n1. 检查数据')
        if ma_risk is None or momentum_risk is None:
            print(f" 缺少数据")
            return None
        print(f" 数据检查通过")

        # 2. 计算统计指标
        print(f' \n2. 计算统计指标')

        # 均线策略统计
        ma_avg_dd = ma_risk['最大回撤'].mean()
        ma_max_dd = ma_risk['最大回撤'].min()
        ma_min_dd = ma_risk['最大回撤'].max()
        ma_high_risk = len(ma_risk[ma_risk['最大回撤'] < -0.20])
        ma_low_risk = len(ma_risk[ma_risk['最大回撤'] > -0.10])

        # 动量策略统计
        momentum_avg_dd = momentum_risk['最大回撤'].mean()
        momentum_max_dd = momentum_risk['最大回撤'].min()
        momentum_min_dd = momentum_risk['最大回撤'].max()
        momentum_high_risk = len(momentum_risk[momentum_risk['最大回撤'] < -0.20])
        momentum_low_risk = len(momentum_risk[momentum_risk['最大回撤'] > -0.10])

        print(f" 均线策略平均回撤: {ma_avg_dd:.2%}")
        print(f" 动量策略平均回撤: {momentum_avg_dd:.2%}")

        # 3. 生产报告文件
        print(f' \n3. 生产报告文件')
        now = datetime.now()
        report_path = self.output_dir / f"风险分析报告_{now.strftime('%Y-%m-%d')}.txt"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write('风险分析报告\n')
            f.write("=" * 80 + "\n")
            f.write(f" 生产时间: {now.strftime('%Y-%m-%d')}")

            # 1. 均线策略风险分析
            f.write(f" \n1. 均线策略风险分析")
            f.write(f"=" * 80 +'\n')
            f.write(f" 股票数量: {len(ma_risk)} 只")
            f.write(f" 平均最大回撤: {ma_avg_dd:.2%}")
            f.write(f" 回撤范围: {ma_min_dd:.2%} 到 {ma_max_dd:.2%}")
            f.write(f" 高风险股票 (回撤>20%): {ma_high_risk} 只")
            f.write(f" 低风险股票 (回撤<10%): {ma_low_risk} 只\n\n")

            # 高风险股票列表
            f.write(f" 高风险股票列表: \n")
            high_risk = ma_risk[ma_risk['最大回撤'] < -0.20]
            for _, row in high_risk.iterrows():
                f.write(f"   - {row['股票代码']}: 回撤 {row['最大回撤']:.2%} \n")
            f.write("\n")

            # 2. 动量策略风险分析
            f.write(f" \n1. 动量策略风险分析")
            f.write(f"=" * 80 + '\n')
            f.write(f" 股票数量: {len(momentum_risk)} 只")
            f.write(f" 平均最大回撤: {momentum_avg_dd:.2%}")
            f.write(f" 回撤范围: {momentum_min_dd:.2%} 到 {momentum_max_dd:.2%}")
            f.write(f" 高风险股票 (回撤>20%): {momentum_high_risk} 只")
            f.write(f" 低风险股票 (回撤<10%): {momentum_low_risk} 只\n\n")

            # 高风险股票列表
            f.write(f" 高风险股票列表: \n")
            high_risk = momentum_risk[momentum_risk['最大回撤'] < -0.20]
            for _, row in high_risk.iterrows():
                f.write(f"   - {row['股票代码']}: 回撤 {row['最大回撤']:.2%} \n")
            f.write("\n")

            # 3. 策略风险对比
            f.write(f"\n3. 策略风险对比\n")
            f.write("=" * 80 + '\n')

            if ma_avg_dd > momentum_avg_dd:
                f.write(f" 平均回撤对比: 均线策略更优\n")
            else:
                f.write(f" 平均回撤对比: 动量策略更优\n")

            if ma_high_risk < momentum_high_risk:
                f.write(f" 高风险股票数: 均线策略更优\n")
            else:
                f.write(f' 高风险股票数: 动量策略更优\n')

            if comparison:
                f.write(f"\n均线策略最差股票: {comparison['均线策略']['最差股票']} (回撤{comparison['均线策略']['最差回撤']:.2%})\n")
                f.write(f"\n动量策略最差股票: {comparison['动量策略']['最差股票']} (回撤{comparison['动量策略']['最差回撤']:.2%})\n\n")


        print(f" 报告已保存: {report_path}")

        print(f" \n" + "=" * 80)
        print(f" 方法5成功: 风险分析报告生产成功")
        return report_path

    def save_all_results(self, ma_risk, momentum_risk, comparison, report):
        """保存所有风险分析结果到Excel"""
        print(f'\n' +'=' * 80)
        print(f' 方法6: 保存所有结果')
        print(f' \n' +'=' * 80)

        from datetime import datetime
        import shutil

        timestamp = datetime.now().strftime("%Y%m%d")
        # 1. 创建保存目录
        print(f'\n1. 创建保存目录')
        save_dir = self.output_dir / f"风险分析结果_{timestamp}"
        save_dir.mkdir(parents=True, exist_ok=True)
        print(f' 保存目录: {save_dir}')

        saved_files = []

        # 2. 保存均线策略风险数据
        print(f' \n2. 保存均线策略风险数据')
        if ma_risk is not None:
            ma_file = save_dir / "均线策略_风险分析.xlsx"
            ma_risk.to_excel(ma_file, index=False)
            print(f' 已保存: {ma_file.name}')
            saved_files.append(str(ma_file))

        # 3. 保存动量策略风险数据
        print(f" \n3. 保存动量策略风险数据")
        if momentum_risk is not None:
            momentum_file = save_dir / "动量策略_风险分析.xlsx"
            momentum_risk.to_excel(momentum_file, index=False)
            print(f" 已保存: {momentum_file.name}")
            saved_files.append(str(momentum_file))

        # 4. 保存风险对比结果
        print(f" \n4. 保存风险对比结果")
        if comparison is not None:
            # 转换为DataFrame
            comparison_list = []
            for stratgey, metrics in comparison.items():
                comparison_list.append({
                    '策略': stratgey,
                    '股票数量': metrics['股票数量'],
                    '平均最大回撤': metrics['平均最大回撤'],
                    '最差回撤': metrics['最差回撤'],
                    '最好回撤': metrics['最好回撤'],
                    '高风险股票数': metrics['高风险股票数'],
                    '最差股票': metrics['最差股票'],
                    '最佳股票': metrics['最佳股票']
                })
            comparison_df = pd.DataFrame(comparison_list)
            comparison_file = save_dir / "风险对比结果.xlsx"
            comparison_df.to_excel(comparison_file, index=False)
            print(f" 已保存: {comparison_file.name}")
            saved_files.append(str(comparison_file))

        # 5. 复制报告文件
        print(f" \n5. 复制报告文件")
        if report and Path(report).exists():
            dest_file = save_dir / Path(report).name
            shutil.copy2(report, dest_file)
            print(f" 已复制报告: {dest_file.name}")
            saved_files.append(str(dest_file))

        # 6. 显示保存结果
        print(f" \n" +'=' * 80)
        print(f' 方法6完成: 所有风险分析结果已保存')
        print('=' * 80)
        print(f' 保存目录: {save_dir}')
        print(f" 共保存: {len(saved_files)} 个文件")
        print(f" - 均线策略_风险分析.xlsx")
        print(f" - 动量策略_风险分析.xlsx")
        print(f" - 风险对比结果.xlsx")
        print(f" - 风险分析报告.txt")
        return save_dir

# 测试
if __name__ == "__main__":
    analyzer = RiskAnalyzer()

    # 加载风险数据
    df_ma, df_momentum = analyzer.load_risk_data()
    if df_ma is not None:
        print(f" 均线策略最大回撤范围: {df_ma['最大回撤'].min():.2%} ~ {df_ma['最大回撤'].max():.2%}")
    if df_momentum is not None:
        print(f" 动量策略最大回撤范围: {df_momentum['最大回撤'].min():.2%} ~ {df_momentum['最大回撤'].max():.2%}")

    if df_ma is not None:
        # 3. 分析均线策略所有股票的风险 (从低风险 到高风险)
        ma_risk = analyzer.analyze_all_stocks_risk(df_ma, "均线策略")
    if df_momentum is not None:
        # 4. 分析动量策略所有股票的风险 (从低风险 到高风险)
        momentum_risk = analyzer.analyze_all_stocks_risk(df_momentum, "动量策略")

    if df_ma is not None and df_momentum is not None:
        # 对比两个策略
        comparison = analyzer.compare_risk_features(ma_risk, momentum_risk)

        # 生产报告
        report = analyzer.generate_risk_report(ma_risk, momentum_risk, comparison)

        # 保存所有结果
        analyzer.save_all_results(ma_risk, momentum_risk, comparison, report)


"""
## 第14天：风险分析

**任务目标**：
- 分析回撤区间（识别回撤最小和最大的股票）
- 识别风险来源（高风险股票的共同特征）
- 对比不同策略的风险特征（平均回撤、高风险股票数等）
- 撰写简要风险分析说明报告

**实现方案**：
1. **数据加载**：
   - 自动查找第8天均线策略回测结果（批量回测结果.xlsx）
   - 自动查找第10天动量策略回测结果（批量回测结果.xlsx）
   - 自动识别并转换收益数据格式（百分比转小数）

2. **单策略风险分析**：
   - **风险排序**：按最大回撤从低到高排序（-5% > -10% > -20%，回撤越接近0风险越低）
   - **风险等级划分**：
     - 回撤 < -30%：🔴 高风险
     - 回撤 < -20%：🟠 中高风险
     - 回撤 < -10%：🟡 中等风险
     - 回撤 ≥ -10%：🟢 低风险
   - **风险统计**：各风险等级股票数量、风险范围、平均回撤
   - **股票明细**：按风险排序显示所有股票（低风险→高风险）

3. **策略风险对比**：
   - **核心指标对比**：平均最大回撤、最差回撤、最好回撤、高风险股票数
   - **高风险股票识别**：回撤超过20%的股票及其列表
   - **最佳/最差股票**：回撤最小和最大的股票
   - **对比结论**：判断哪种策略风险控制更好

4. **风险分析报告**：
   - 均线策略风险分析（股票数量、平均回撤、回撤范围、高风险股票列表）
   - 动量策略风险分析（同上）
   - 策略风险对比结论（谁的平均回撤更小、高风险股票更少）
   - 最差和最佳股票标注

5. **结果保存系统**：
   - 保存均线策略风险分析Excel（含风险排名和风险等级）
   - 保存动量策略风险分析Excel（含风险排名和风险等级）
   - 保存风险对比结果Excel
   - 生成风险分析报告文本文件

**核心代码结构**：
```python
class RiskAnalyzer:
    ├── __init__()                       # 初始化目录
    ├── load_risk_data()                  # 加载均线和动量策略结果
    ├── analyze_all_stocks_risk()         # 分析单策略所有股票风险
    ├── compare_risk_features()           # 对比两策略风险特征
    ├── generate_risk_report()            # 生成风险分析报告
    └── save_all_results()                # 保存所有结果到Excel
```    
"""


