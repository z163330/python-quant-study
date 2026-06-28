'''
第13天
					绩效指标计算
-计算年化收益率
-计算最大回撤
-计算 Sharpe 比率
-计算 Sortino 比率

练习：
-汇总策略绩效指标表
'''

import pandas as pd
import numpy as np
from pathlib import Path

class PerformanceCalculator:
    """绩效指标计数器"""
    def __init__(self):
        """初始化绩效指标计数器"""
        print(f'\n' + '=' * 80)
        print(f" 方法1: 初始化绩效指标计数器")
        print(f"\n" + "=" * 80)

        # 1. 获取当前文件目录
        print(f"\n1. 获取当前文件目录")
        current_dir = Path(__file__).parent
        print(f" 当前文件目录: {current_dir}")

        # 2. 找到项目根目录
        print(f" \n2. 找到项目根目录")
        self.project_root = current_dir.parent
        print(f" 项目根目录: {self.project_root}")

        # 3. 设置数据目录  (是获取均线和动量策略数据)
        print(f" \n3. 设置数据目录")
        self.ma_result_dir = self.project_root / "data" / "策略结果"
        self.momentum_result_dir = self.project_root / "data" / "动量策略结果"
        print(f" 均线策略结果目录: {self.ma_result_dir}")
        print(f" 动量策略结果目录: {self.momentum_result_dir}")

        # 4. 设置输出目录 (保存绩效指标结果)
        print(f" \n4. 设置输出目录")
        self.output_dir = self.project_root / "data" / "绩效指标"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f" 输出目录: {self.output_dir}")

        # 5. 初始化结果存储
        print(f" \n5. 初始化结果存储")
        self.performance_results = []

        # 6. 设置无风险利率 (默认2%)
        self.risk_free_rate = 0.02
        print(f" 无风险利率: {self.risk_free_rate:.2%}")

        print(f'\n' + "-" * 80)
        print(f" 方法1完成: 初始化成功")
        print('-' * 80)
        print(f" 均线策略目录: {self.ma_result_dir}")
        print(f" 动量策略目录: {self.momentum_result_dir}")
        print(f" 输出目录: {self.output_dir}")
        print(f" 无风险利率: {self.risk_free_rate:.2%}")
        print(f" =" * 80)

    def load_performance_data(self):
        """加载均线策略和动量策略的回测结果"""
        print(f'\n' + '=' * 80)
        print(f' 方法2: 加载绩效数据')
        print('=' * 80)

        # 1. 加载均线策略结果
        print(f" \n1. 加载均线策略结果")
        ma_folders = list(self.ma_result_dir.glob('回测结果_*'))

        if not ma_folders:
            print(f' 没有找到均线策略结果')
            return None

        latest_ma_folder = max(ma_folders, key=lambda x: x.stat().st_mtime)
        ma_file = latest_ma_folder / "批量回测结果.xlsx"

        if not ma_file.exists():
            print(f" 没有找到批量回测结果文件")
            return None

        df_ma = pd.read_excel(ma_file)
        df_ma.columns = df_ma.columns.str.strip()
        print(f' 均线策略结果: {df_ma.shape[0]} 行 x {df_ma.shape[1]}列')

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

        df_momentum = pd.read_excel(momentum_file)
        df_momentum.columns = df_momentum.columns.str.strip()
        print(f" 动量策略数据: {df_momentum.shape[0]} 行 x {df_momentum.shape[1]} 列")

        # 3. 检查并转换收益数据
        print(f" \n3. 检查数据格式")

        if df_ma['策略总收益'].max() > 1:
            print(f' 均线策略收益数据为百分比格式, 正在转换............')
            df_ma['策略总收益'] = df_ma['策略总收益'] /100
            print(f" 转换后最大值: {df_ma['策略总收益'].max():.2%}")

        if df_momentum['策略总收益'].max() > 1:
            print(f' 动量策略收益数据为百分比格式, 正在转换............')
            df_momentum['策略总收益'] = df_momentum['策略总收益'] / 100
            print(f" 转换后最大值: {df_momentum['策略总收益'].max():.2%}")

        # 4. 显示数据预览
        print(f" \n4. 显示数据预览")
        print('-' * 50)
        print(f" 均线策略前5行")
        print(df_ma[['股票代码', '策略总收益', '夏普比率', '最大回撤']].head())
        print(f" 动量策略前5行")
        print(df_momentum[['股票代码', '策略总收益', '夏普比率', '最大回撤']].head())

        # 5. 保存到对象
        self.ma_result = df_ma
        self.momentum_result = df_momentum

        print('\n' + ' =' * 80)
        print(f' 方法2完成: 绩效数据加载成功')
        print(f" 均线策略股票数: {len(df_ma)}")
        print(f" 动量策略股票数: {len(df_momentum)}")

        return df_ma, df_momentum

    def calculate_annual_return(self, df, strategy_name="策略"):
        """计算所有股票的年化收益率"""
        print(f'\n' +'=' * 80)
        print(f' 方法3: 计算{strategy_name}年化收益率')
        print("=" * 80)

        # 1. 检查数据
        print(f' \n1. 检查数据')
        if df is None:
            print(f' 没有数据')
            return None

        print(f' 数据形状: {df.shape[0]} 行 x {df.shape[1]} 列')

        # 2. 检查必要的列
        print(f' \n2. 检查必要的列')
        if '策略总收益' not in df.columns:
            print(f" 没有找到'策略总收益'列")
            return None
        print(f" 找到 '策略总收益'列")

        if '数据天数' not in df.columns:
            print(f" 没有找到'数据天数'列, 将使用默认值252天")
            df['数据天数'] = 252

        # 3. 计算年化收益率
        print(f" \n3. 计算年化收益率")
        print(f" 公式: 年化收益率 = (1+总收益)^(252/天数) -1 ")
        df['年化收益率'] = df.apply(
            lambda row: (1 + row['策略总收益']) ** (252/row['数据天数']) -1,
            axis=1
        )
        print(f' 年化收益率计算完成')

        # 4. 显示统计信息
        print(f" \n4. 年化收益率统计")
        print(f" 平均值: {df['年化收益率'].mean():.2%}")
        print(f" 最大值: {df['年化收益率'].max():.2%}")
        print(f" 最小值: {df['年化收益率'].min():.2%}")
        print(f" 标准差: {df['年化收益率'].std():.4f}")

        # 5. 显示前10名
        print(f' \n5. 年化收益率最高的前10名')
        top10 = df.nlargest(10, '年化收益率')[['股票代码', '策略总收益', '年化收益率', '数据天数']]
        for i, row in top10.iterrows():
            print(f"{row['股票代码']}: 总收益{row['策略总收益']:.2%} -> 年化{row['年化收益率']:.2%}")

        print(f' \n'+'=' * 80)
        print(f' 方法3完成: 年化收益率计算成功')
        return df


    def calculate_max_drawdown(self, df):
        """计算所有股票的最大回撤"""
        print(f' \n' +'=' * 80)
        print(f" 方法4: 计算最大回撤")
        print('=' * 80)

        # 1. 检查数据
        print(f"\n1. 检查数据")
        if df is None:
            print(f' 没有数据')
            return None

        print(f" 数据形状: {df.shape[0]}行 x {df.shape[1]} 列")

        # 2. 检查必要的列
        print(f'\n2. 检查必要的列')
        if "最大回撤" not in df.columns:
            print(f' 没有找到 "最大回撤" 列')
            return None
        print(f' 找到 "最大回撤" 列')

        # 3. 计算最大回撤统计
        print(f" \n3. 计算最大回撤统计")
        max_drawdown_mean = df['最大回撤'].mean()
        max_drawdown_min = df['最大回撤'].min()
        max_drawdown_max = df['最大回撤'].max()
        max_drawdown_std = df['最大回撤'].std()

        print(f" 平均最大回撤: {max_drawdown_mean:.2%}")
        print(f" 最小回撤 (亏损最少): {max_drawdown_min:.2%}")
        print(f" 最大回撤 (亏损最多): {max_drawdown_max:.2%}")
        print(f" 标准差: {max_drawdown_std}:.4f")

        # 4. 显示回撤最小的前10名 (亏损最少, 风险最低)
        print(f' \n4. 回撤最小的前10名 (风险最低) ')
        top10_low = df.nlargest(10, '最大回撤')[['股票代码', '最大回撤']]  # nlargest取最大 (取最接近0)
        for i, row in top10_low.iterrows():
            print(f" {row['股票代码']}: 最大回撤 {row['最大回撤']:.2%}")


        # 5. 显示回撤最大前10 名 (亏损最多, 风险最高)
        print(f" \n5. 回撤最大的前10名 (风险最高) ")
        top10_high = df.nsmallest(10, '最大回撤')[['股票代码', '最大回撤']]  # nsmallest取最小 (最负)
        for i, row in top10_high.iterrows():
            print(f" {row['股票代码']}: 最大回撤 {row['最大回撤']:.2%}")

        print(f' \n' + '=' * 80)
        print(f'方法4完成: 最大回撤计算成功')
        return df

    def calculate_sharpe_ratio(self, df, strategy_name='策略'):
        """计算所有股票的夏普比率"""
        print('\n' + '=' *80)
        print(f" 方法5: 计算所有股票的夏普比率")
        print('=' * 80)

        # 1. 检查数据
        print(f"\n1. 检查数据")
        if df is None:
            print(f' 没有数据')
            return None
        print(f" 数据形状: {df.shape[0]} 行 x {df.shape[1]} 列")

        # 2. 检查必要的列
        print(f" \n2. 检查必要的列")
        if "年化收益率" not in df.columns:
            print(f" 没有找到 '年化收益率' 列, ")
            return None
        print(f" 找到'年化收益率' 列")

        if '策略年化波动率' not in df.columns:
            print(f" 没有找到 '策略年化波动率' 列")
            df['策略年化波动率'] = 0.2

        # 3. 计算夏普比率
        print(f" \n3. 计算夏普比率")
        print(f" 公式: 夏普比率 = (年化收益率 -无风险利率) / 年化波动率 ")
        print(f" 无风险利率: {self.risk_free_rate:.2%}")

        df['夏普比率_计算'] = (df['年化收益率'] - self.risk_free_rate) / df['策略年化波动率']
        print(f" 夏普比率计算完成")

        # 4. 显示统计信息
        print(f" \n4. 夏普比率统计")
        print(f" 平均值: {df['夏普比率_计算'].mean():.4f}")
        print(f" 最大值: {df['夏普比率_计算'].max():.4f}")
        print(f" 最小值: {df['夏普比率_计算'].min():.4f}")
        print(f" 标准差: {df['夏普比率_计算'].std():.4f}")

        # 5. 夏普比率解读
        print(f" \n5. 夏普比率解读")
        avg_sharpe = df['夏普比率_计算'].mean()
        if avg_sharpe > 1:
            print(f" 平均夏普比率 {avg_sharpe:.4f} > 1, 策略表现优秀")
        elif avg_sharpe > 0.5:
            print(f" 平均夏普比率 {avg_sharpe:.4f} > 0.5, 策略表现良好")
        elif avg_sharpe >0:
            print(f" 平均夏普比率 {avg_sharpe:.4f} > 0, 策略有正收益")
        else:
            print(f" 平均夏普比率 {avg_sharpe:.4f} < 0, 策略表现不佳")

        # 6. 显示前10 名
        print(f' \n6. 夏普比率最高的前10名')
        top10 = df.nlargest(10, '夏普比率_计算')[['股票代码', '年化收益率', '策略年化波动率', '夏普比率_计算']]
        for i, row in top10.iterrows():
            print(f" {row['股票代码']}: 年化收益 {row['年化收益率']:.2%}, 波动 {row['策略年化波动率']:.2%},"
                  f"夏普 {row['夏普比率_计算']:.4f}")

        print(f' \n' + '=' * 80)
        print(f' 方法5完成: 夏普比率计算成功')

        return df

    def calculate_sortino_ratio(self, df, strategy_name="策略"):
        """计算所有股票的索提诺比率
        索提诺比率 sortino ratio 是夏普比率升级版.
        夏普比率 把上涨和下跌波动都算作风险,  但是索提诺比率 只把下跌波动算作风险
        """
        print('\n' +' =' * 80)
        print(f" 方法6: 计算 {strategy_name}索提诺比率")
        print('=' * 80)

        # 1. 检查数据
        print(f"\n1. 检查数据")
        if df is None:
            print(f' 没有数据')
            return None
        print(f" 数据形状: {df.shape[0]} 行 x {df.shape[1]} 列")

        # 2. 检查必要的列
        print(f" \n2. 检查必要的列")
        if "年化收益率" not in df.columns:
            print(f' 没有找到 "年化收益率" 列')
            return None
        print(f" 找打 '年化收益率' 列")

        # 3. 计算下行波动率 (只考虑负收益)
        print(f" \n3. 计算下行波动率")
        print(f" 公式: 下行波动率 = 负收益的标准差 x √252")

        # 如果没有下行波动率列, 从最大回撤估算
        if '下行波动率' not in df.columns:
            if '最大回撤' in df.columns:
                # 下行波动率 = 最大回撤绝对值 x 0.5 (经验估算)
                df['下行波动率'] = abs(df['最大回撤']) * 0.5
                print(f" 没有找到 '下行波动率'列, 使用最大回撤估算")
            else:
                df['下行波动率'] = 0.15 # 默认15%
                print(f" 使用默认值15%")

        # 4. 计算索提诺比率
        print(f" \n4. 计算索提诺比率")
        print(f" 公式: 索提诺比率 = (年化收益率 - 无风险利率) / 下行波动率 ")
        print(f" 无风险利率: {self.risk_free_rate:.2%}")

        df['索提诺比率'] = (df['年化收益率'] - self.risk_free_rate) / df['下行波动率']

        print(f" 索提诺比率计算完成")

        # 5. 显示统计信息
        print(f" \n5. 索提诺比率统计信息")
        print(f" 平均值: {df['索提诺比率'].mean():.4f}")
        print(f" 最大值: {df['索提诺比率'].max():.4f}")
        print(f" 最小值: {df['索提诺比率'].min():.4f}")
        print(f" 标准差: {df['索提诺比率'].std():.4f}")

        # 6. 索提诺比率解读
        print(f" \n6. 索提诺比率解读")
        avg_sortino = df['索提诺比率'].mean()
        if avg_sortino > 1.5:
            print(f" 平均索提诺比率 {avg_sortino:.4f} > 1.5, 策略下行风险控制优秀")
        elif avg_sortino > 0.8:
            print(f" 平均索提诺比率 {avg_sortino:.4f} > 0.8, 策略下行风险控制良好")
        elif avg_sortino > 0:
            print(f" 平均索提诺比率 {avg_sortino:.4f} > 0, 策略有正收益")
        else:
            print(f" 平均索提诺比率 {avg_sortino:.4f} < 0, 策略下行风险较大")

        # 7. 显示前10名
        print(f" \n7. 索提诺比率最高的前10名")
        top10 = df.nlargest(10, '索提诺比率')[['股票代码', '年化收益率', '下行波动率', '索提诺比率']]
        for i, row in top10.iterrows():
            print(f" {row['股票代码']}: 年化收益{row['年化收益率']:.2%}, 下行波动{row['下行波动率']:.2%},"
                  f"索提诺 {row['索提诺比率']:.4f}")

        print(f'\n' + '=' * 80)
        print(f" 方法6完成: 索提诺比率计算成功")
        return df

    def generate_performance_table(self, df_ma, df_momentum):
        """生成绩效指标汇总表"""
        print('\n' +'=' * 80)
        print(f" 方法7: 生成绩效指标汇总表")
        print('=' * 80)

        # 1. 检查数据
        print(f" \n1. 检查数据")
        if df_ma is None and df_momentum is None:
            print(f" 没有数据")
            return None

        # 2. 计算均线策略的整体指标
        print(f" \n2. 计算均线策略整体指标")
        ma_summary = {}
        if df_ma is not None:
            ma_summary = {
                '策略名称': '均线策略',
                '股票数量': len(df_ma),
                '平均年化收益率': df_ma['年化收益率'].mean(),
                '中位数年化收益率': df_ma['年化收益率'].median(),
                '平均最大回撤': df_ma['最大回撤'].mean(),
                '平均夏普比率': df_ma['夏普比率_计算'].mean() if '夏普比率_计算' in df_ma.columns else np.nan,
                '平均索提诺比率': df_ma['索提诺比率'].mean() if '索提诺比率' in df_ma.columns else np.nan
            }
            print(f" 均线策略股票数: {ma_summary['股票数量']}")
            print(f" 平均年化收益率: {ma_summary['平均年化收益率']:.2%}")
            print(f" 平均最大回撤: {ma_summary['平均最大回撤']:.2%}")

        # 3. 计算动量策略的整体指标
        print(f"\n3. 计算动量策略的整体指标")
        momentum_summary = {}
        if df_momentum is not None:
            momentum_summary = {
                '策略名称': '动量策略',
                '股票数量': len(df_momentum),
                '平均年化收益率': df_momentum['年化收益率'].mean(),
                '中位数年化收益率': df_momentum['年化收益率'].median(),
                '平均最大回撤': df_momentum['最大回撤'].mean(),
                '平均夏普比率': df_momentum['夏普比率_计算'].mean() if '夏普比率_计算' in df_momentum.columns else np.nan,
                '平均索提诺比率': df_momentum['索提诺比率'].mean() if '索提诺比率' in df_momentum.columns else np.nan
            }
            print(f" 动量策略股票数: {momentum_summary['股票数量']}")
            print(f" 平均年化收益率: {momentum_summary['平均年化收益率']:.2%}")
            print(f" 平均最大回撤: {momentum_summary['平均最大回撤']:.2%}")

        # 4. 创建汇总表格
        print(f" \n4. 创建汇总表格")
        summary_list = []
        if df_ma is not None:
            summary_list.append(ma_summary)
        if df_momentum is not None:
            summary_list.append(momentum_summary)

        summary_df = pd.DataFrame(summary_list)

        # 5. 显示汇总表格
        print(f" \n5. 策略绩效指标汇总表")
        print(f"=" * 80)

        # 格式化显示
        display_df = summary_df.copy()
        for col in ['平均年化收益率', '中位数年化收益率', '平均最大回撤']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")

        for col in ['平均夏普比率', '平均索提诺比率']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")

        print(display_df.to_string(index=False))
        print('=' * 80)

        # 6. 策略对比
        print(f" \n6. 策略对比分析")
        if df_ma is not None and df_momentum is not None:
            if ma_summary['平均年化收益率'] > momentum_summary['平均年化收益率']:
                print(f" 均线策略收益更高: {ma_summary['平均年化收益率']:.2%} > {momentum_summary['平均年化收益率']:.2%}")
            else:
                print(f" 动量策略收益更高: {momentum_summary['平均年化收益率']:.2%} > {ma_summary['平均年化收益率']:.2%}")

            if abs(ma_summary['平均最大回撤']) < abs(momentum_summary['平均最大回撤']):
                print(f" 均线策略最大回撤更小: {ma_summary['平均最大回撤']:.2%} > {momentum_summary['平均最大回撤']:.2%}")
            else:
                print(f" 动量策略最大回撤更小: {momentum_summary['平均最大回撤']:.2%} > {ma_summary['平均最大回撤']:.2%}")

        # 7. 保存汇总表到对象
        self.performance_summary = summary_df
        print(f"\n" + '=' * 80)
        print(f' 方法7完成: 绩效指标汇总表生成成功')

        return summary_df

    def save_all_results(self, df_ma, df_momentum, summary_df):
        """保存所有的绩效指标结果到Excel"""
        print(f'\n' +'=' * 80)
        print(f" 方法8: 保存所有结果")
        print(f" =" * 80)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")

        # 1. 创建保存目录
        print(f" \n1. 创建保存目录")
        save_dir = self.output_dir / f"绩效指标结果_{timestamp}"
        save_dir.mkdir(parents=True, exist_ok=True)
        print(f" 保存目录: {save_dir}")

        save_files = []

        # 2. 保存均线策略详细数据
        print(f" \n2. 保存均线策略详细数据")
        if df_ma is not None:
            ma_file = save_dir / "均线策略_绩效指标.xlsx"
            with pd.ExcelWriter(ma_file, engine='openpyxl') as writer:
                # sheet 1: 股票详细数据
                df_ma.to_excel(writer, sheet_name='股票详细数据', index=False)

                # sheet 2: 统计汇总
                ma_stats = pd.DataFrame({
                    '指标': ['平均年化收益率', '中位数年化收益率', '最高年化收益率', '最低年化收益率',
                             '平均最大回撤', '平均夏普比率', '平均索提诺比率', '股票数量'],
                    '数值': [
                        f"{df_ma['年化收益率'].mean():.2%}",
                        f"{df_ma['年化收益率'].median():.2%}",
                        f"{df_ma['年化收益率'].max():.2%}",
                        f"{df_ma['年化收益率'].min():.2%}",
                        f"{df_ma['最大回撤'].mean():.2%}",
                        f"{df_ma['夏普比率_计算'].mean():.4f}" if '夏普比率_计算' in df_ma.columns else "N/A",
                        f"{df_ma['索提诺比率'].mean():.4f}" if "索提诺比率" in df_ma.columns else "N/A",
                        len(df_ma)
                    ]
                })
                ma_stats.to_excel(writer, sheet_name='统计汇总', index=False)

                # sheet 3. 最佳10名
                if '年化收益率' in df_ma.columns:
                    top10 = df_ma.nlargest(10, '年化收益率')[['股票代码', '年化收益率', '最大回撤', '夏普比率_计算']]
                    top10.to_excel(writer, sheet_name='最佳10名', index=False)
            file_size = ma_file.stat().st_size / 1024
            print(f" 已保存: {ma_file.name} ({file_size:.1f} KB)")
            save_files.append(str(ma_file))

        # 3. 保存动量策略详细数据
        print(f" \n3. 保存动量策略详细数据")
        if df_momentum is not None:
            momentum_file = save_dir / "动量策略_绩效指标.xlsx"
            with pd.ExcelWriter(momentum_file, engine='openpyxl') as writer:
                # sheet 1: 股票详细数据
                df_momentum.to_excel(writer, sheet_name='股票详细数据', index=False)
                # sheet 2: 统计汇总
                momentum_stats = pd.DataFrame({
                    '指标': ['平均年化收益率', '中位数年化收益率', '最高年化收益率', '最低年化收益率',
                             '平均最大回撤', '平均夏普比率', '平均索提诺比率', '股票数量'],
                    '数值': [
                        f"{df_momentum['年化收益率'].mean():.2%}",
                        f"{df_momentum['年化收益率'].median():.2%}",
                        f"{df_momentum['年化收益率'].max():.2%}",
                        f"{df_momentum['年化收益率'].min():.2%}",
                        f"{df_momentum['最大回撤'].mean():.2%}",
                        f"{df_momentum['夏普比率_计算'].mean():.4f}" if '夏普比率_计算' in df_momentum.columns else "N/A",
                        f"{df_momentum['索提诺比率'].mean():.4f}" if "索提诺比率" in df_momentum.columns else "N/A",
                        len(df_momentum)
                    ]
                })
                momentum_stats.to_excel(writer, sheet_name='统计汇总', index=False)

                # sheet 3: 最佳10名
                if '年化收益率' in df_momentum.columns:
                    top10 = df_momentum.nlargest(10, '年化收益率')[['股票代码', '年化收益率', '最大回撤', '夏普比率_计算']]
                    top10.to_excel(writer, sheet_name='最佳10名', index=False)

            file_size = momentum_file.stat().st_size / 1024
            print(f" 已保存: {momentum_file.name} ({file_size:.1f}KB)")
            save_files.append(str(momentum_file))

        # 4. 保存策略对比汇总表
        print(f" \n4. 保存策略对比汇总表")
        if summary_df is not None:
            summary_file = save_dir / "策略绩效对比汇总.xlsx"
            summary_df.to_excel(summary_file, index=False)
            print(f" 已保存: {summary_file.name}")
            save_files.append(str(summary_file))

        # 5. 生成汇总报告
        print(f" \n5. 生成汇总报告")
        report_file = save_dir / '绩效指标分析报告.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + '\n')
            f.write("绩效指标分析报告\n")
            f.write('=' * 80 + "\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y%m%d')}\n\n")

            # 均线策略总结
            if df_ma is not None:
                f.write("1. 均线策略")
                f.write("-" * 50 + "\n")
                f.write(f" 股票数量: {len(df_ma)}")
                f.write(f" 平均年化收益率: {df_ma['年化收益率'].mean():.2%}")
                f.write(f" 平均最大回撤: {df_ma['最大回撤'].mean():.2%}")
                if "夏普比率_计算" in df_ma.columns:
                    f.write(f" 平均夏普比率: {df_ma['夏普比率_计算'].mean():.4f}")
                if "索提诺比率" in df_ma.columns:
                    f.write(f" 平均索提诺比率: {df_ma['索提诺比率'].mean():.4f}")
                f.write("\n")

            # 动量策略总结
            if df_momentum is not None:
                f.write("2. 动量策略")
                f.write("-" * 50 + "\n")
                f.write(f" 股票数量: {len(df_momentum)}")
                f.write(f" 平均年化收益率: {df_momentum['年化收益率'].mean():.2%}")
                f.write(f" 平均最大回撤: {df_momentum['最大回撤'].mean():.2%}")
                if "夏普比率_计算" in df_momentum.columns:
                    f.write(f" 平均夏普比率: {df_momentum['夏普比率_计算'].mean():.4f}")
                if "索提诺比率" in df_momentum.columns:
                    f.write(f" 平均索提诺比率: {df_momentum['索提诺比率'].mean():.4f}")
                f.write("\n")

            # 策略对比
            if df_ma is not None and df_momentum is not None:
                f.write('3. 策略对比')
                f.write("\n" + "=" * 50)

                if df_ma['年化收益率'].mean() > df_momentum['年化收益率'].mean():
                    f.write(f" 收益表现: 均线策略优于动量策略\n")
                else:
                    f.write(f" 收益表现: 动量策略优于均线策略\n")

                if abs(df_ma['最大回撤'].mean()) < abs(df_momentum['最大回撤'].mean()):
                    f.write(f" 风险控制: 均线策略优于动量策略\n")
                else:
                    f.write(f" 风险控制: 动量策略优于均线策略\n")
        print(f" 已保存: {report_file.name}")
        save_files.append(str(report_file))

        # 6. 显示保存结果
        print(f" \n" + '=' * 80)
        print(f" 方法8完成: 所有绩效指标结果已保存")
        print('=' * 80)
        print(f" 保存目录: {save_dir}")
        print(f" 共保存{len(save_files)} 个文件")

        return save_dir

# 测试:
if __name__ == "__main__":
    calculator = PerformanceCalculator()

    # 加载绩效数据
    df_ma, df_momentum = calculator.load_performance_data()

    # 计算均线策略的年化收益率
    df_ma = calculator.calculate_annual_return(df_ma, "均线策略")
    df_ma = calculator.calculate_max_drawdown(df_ma)
    df_ma = calculator.calculate_sharpe_ratio(df_ma, '均线策略')
    df_ma = calculator.calculate_sortino_ratio(df_ma, '均线策略')

    # 计算动量策略的年化收益率
    df_momentum = calculator.calculate_annual_return(df_momentum, "动量策略")
    df_momentum = calculator.calculate_max_drawdown(df_momentum)
    df_momentum = calculator.calculate_sharpe_ratio(df_momentum, '动量策略')
    df_momentum = calculator.calculate_sortino_ratio(df_momentum, '动量策略')

    # 生成绩效指标汇总表
    summary = calculator.generate_performance_table(df_ma, df_momentum)

    # 保存所有结果
    calculator.save_all_results(df_ma, df_momentum, summary)


"""
## 第13天：绩效指标计算

**任务目标**：
- 计算年化收益率（考虑数据天数，年化到252个交易日）
- 计算最大回撤（策略净值从高点到低点的最大跌幅）
- 计算夏普比率（风险调整后收益，考虑总波动率）
- 计算索提诺比率（下行风险调整后收益，仅考虑负收益波动）
- 汇总策略绩效指标表，对比两种策略表现

**实现方案**：
1. **数据加载**：
   - 自动查找第8天均线策略回测结果（批量回测结果.xlsx）
   - 自动查找第10天动量策略回测结果（批量回测结果.xlsx）
   - 自动识别并转换收益数据格式（百分比转小数）

2. **年化收益率计算**：
   - **公式**：`年化收益率 = (1 + 总收益率)^(252 / 交易天数) - 1`
   - 若缺少数据天数列，默认使用252天
   - 输出平均值、最大值、最小值、标准差统计
   - 显示年化收益率最高的前10名股票

3. **最大回撤计算**：
   - 直接从回测结果中读取现有最大回撤数据
   - 输出平均值、最小值（亏损最少）、最大值（亏损最多）
   - 显示回撤最小（风险最低）和回撤最大（风险最高）的前10名

4. **夏普比率计算**：
   - **公式**：`夏普比率 = (年化收益率 - 无风险利率) / 年化波动率`
   - 无风险利率默认2%（可配置）
   - 输出平均值、最大值、最小值统计
   - 夏普比率解读：>1优秀，>0.5良好，>0有正收益，<0表现不佳

5. **索提诺比率计算**：
   - **公式**：`索提诺比率 = (年化收益率 - 无风险利率) / 下行波动率`
   - 下行波动率：只考虑负收益的波动（下跌风险）
   - 若无下行波动率数据，使用最大回撤绝对值×0.5估算
   - 输出平均值、最大值、最小值统计
   - 索提诺比率解读：>1.5优秀，>0.8良好，>0有正收益

6. **策略绩效汇总表**：
   - **均线策略整体指标**：股票数量、平均/中位数年化收益率、平均最大回撤、平均夏普比率、平均索提诺比率
   - **动量策略整体指标**：同上
   - **策略对比分析**：判断哪种策略收益更高、回撤更小

7. **结果保存系统**：
   - 保存均线策略绩效指标Excel（股票详细数据、统计汇总、最佳10名）
   - 保存动量策略绩效指标Excel（股票详细数据、统计汇总、最佳10名）
   - 保存策略绩效对比汇总表
   - 生成绩效指标分析报告（含收益对比、风险控制对比）

**核心代码结构**：
```python
class PerformanceCalculator:
    ├── __init__()                       # 初始化目录和无风险利率
    ├── load_performance_data()           # 加载均线和动量策略结果
    ├── calculate_annual_return()         # 计算年化收益率
    ├── calculate_max_drawdown()          # 计算最大回撤统计
    ├── calculate_sharpe_ratio()          # 计算夏普比率
    ├── calculate_sortino_ratio()         # 计算索提诺比率（下行风险）
    ├── generate_performance_table()      # 生成绩效指标汇总表
    └── save_all_results()                # 保存所有结果到Excel
```
"""



