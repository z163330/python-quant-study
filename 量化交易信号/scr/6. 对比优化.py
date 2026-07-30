"""
目标：找最好的信号

做法：

MA策略 vs RSI vs 动量 vs 突破 vs 波动率
比较收益和回撤

"""

import pandas as pd
import numpy as np
from pathlib import Path

from selenium.webdriver.support.expected_conditions import element_selection_state_to_be


class SignalComparator:
    """信号对比器 - 找出最佳信号"""

    def __init__(self):
        """初始化"""
        print(f" \n" + '=' * 70)
        print(f" 信号对比器 - 初始化")
        print(f"=" * 70)

        # 1. 获取当前文件目录
        current_dir = Path(__file__).parent
        self.project_root = current_dir.parent
        print(f" 项目根目录: {self.project_root}")

        # 2. 设置目录
        self.positions_dir = self.project_root / "positions"
        self.output_dir = self.project_root / "signal_comparison"
        self.output_dir.mkdir(parents=True, exist_ok=True)      # 这个是创建文档.

        print(f" 仓位数据目录: {self.positions_dir}")
        print(f" 对比输出目录: {self.output_dir}")

        # 3. 检查仓位文件
        self.position_files = list(self.positions_dir.glob("*_仓位.xlsx"))
        print(f" 找到 {len(self.position_files)} 个仓位文件")

        # 4. 存储数据
        self.positions = {}
        self.signal_results = {}

        print(f"\n" + '=' * 80)
        print(f" 初始化完成")
        print(f" -" * 80)

    def load_data(self):
        """加载所有仓位数据"""
        print(f"\n" + "=" * 80)
        print(f" 加载仓位数据")
        print(f'=' * 70)

        if not self.position_files:
            print(f" 没有找到仓位文件")
            return None

        for file_path in self.position_files:
            symbol = file_path.stem.replace("_仓位", "")
            print(f" \n 加载: {symbol}")

            try:
                df = pd.read_excel(file_path)
                print(f" 成功: {df.shape[0]} 行 x {df.shape[1]} 列")
                self.positions[symbol] = df
            except Exception as e:
                print(f" 失败: {e}")

        print(f" \n 共加载 {len(self.positions)} 只股票")
        return self.positions

    def evaluate_signal(self, df, signal_col):
        """
        评估单个信号的表现
        Args:
            df: 仓位DateFrame
            signal_col: 信号列名 (如 "MA_5_20_仓位_100%")
        Returns:
            dict: 包含总收益, 最大回撤, 夏普比率
        """

        # 1. 准备数据
        df_temp = df.copy()

        # 2. 清洗数据
        df_temp = df_temp[df_temp['Close'] > 0]
        df_temp = df_temp[df_temp['Close'].notna()]

        if len(df_temp) < 2:
            return None

        # 3. 获取仓位列
        if signal_col not in df_temp.columns:
            return None

        # ============= 获取仓位并强制归一化 =================
        position= df_temp[signal_col]

        # 4. 清洗仓位
        position = df_temp[signal_col].replace([np.inf, -np.inf], 0)
        position = position.fillna(0)
        position = position.clip(-1, 1)

        # 如果仓位最大值 > 1, 说明数据又问题, 打印警告
        if position.abs().max() > 1:
            print(f" 仓位异常: {signal_col} 最大值 {position.abs().max():.2f}")
            position = position.clip(-1, 1)

        # 检查仓位是否全为 0
        if position.abs().sum() == 0:
            return None

        # 5. 计算收益
        df_temp['daily_return'] = df_temp['Close'].pct_change()
        df_temp['daily_return'] = df_temp['daily_return'].replace([np.inf, -np.inf], 0)
        df_temp['daily_return'] = df_temp['daily_return'].fillna(0)

        df_temp['strategy_return'] = position * df_temp['daily_return']
        df_temp['cumulative_return'] = (1 + df_temp['strategy_return']).cumprod()

        # 6. 计算指标
        total_return = df_temp['cumulative_return'].iloc[-1] - 1

        # 防止异常值
        if total_return > 100 or total_return < -1:
            print(f" 收益异常: {total_return:.2f}, 跳过")
            return None

        # 最大回撤
        running_max = df_temp['cumulative_return'].expanding().max()
        drawdown = (df_temp['cumulative_return'] - running_max) / running_max
        max_drawdown = drawdown.min()

        # 夏普比率
        days = len(df_temp)
        annual_return = (1 + total_return) ** (252 / days) - 1
        daily_std = df_temp['strategy_return'].std()
        annual_vol = daily_std * np.sqrt(252) if daily_std > 0 else 1
        sharpe = (annual_return - 0.02) / annual_vol

        # 防止夏普比率异常
        if sharpe > 10 or sharpe < -10:
            sharpe= np.nan

        return {
            'signal': signal_col,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe,
            'days': days
        }

    def compare_all_signals(self):
        """
        对比所有信号, 找出最佳信号
        Returns:
            DataFrame: 所有信号的评估结果, 按收益排序
        """
        print(f"\n" + "=" * 80)
        print(f"对比所有信号")
        print(f"=" * 70)

        if not self.positions:
            print(f'没有仓位数据')
            return None

        all_results = []

        # ================== 循环所有股票 ===================
        for symbol, df in self.positions.items():
            print(f" 使用股票: {symbol}")

            # 找出所有原始信号列
            all_cols = df.columns.tolist()
            raw_signals = [col for col in all_cols if any(x in col for x in ['MA_', 'RSI_', 'Momentum_', 'Break_',
                                                                             'Volatility_']) and "_仓位_" not in col]
            print(f" 找到 {len(raw_signals)} 个信号列")

            # 评估每个信号
            for i, signal_col in enumerate(raw_signals):
                result = self.evaluate_signal(df, signal_col)

                if result:
                    # 添加股票代码
                    result['symbol'] = symbol
                    all_results.append(result)
                # 显示进度
                if (i + 1) % 10 == 0:
                    print(f" 进度:{i+1}/{len(raw_signals)}")

        # 转换为DataFrame
        result_df = pd.DataFrame(all_results)

        # 按总收益排序
        result_df = result_df.sort_values('total_return', ascending=False)

        print(f" \n 共评估 {len(result_df)} 个信号")

        self.signal_results = result_df
        return result_df

    def find_best_signal(self, results_df, metric='total_return'):
        """找出最佳信号
        Args:
            results_df: compare_all_signals() 返回的结果
            metric: 评估指标 ('total_return', 'sharpe_ratio', 或 'max_drawdown')
        Returns:
            dict: 最佳信号的信息
        """

        print(f'\n' + '=' * 80)
        print(f' 找出最佳的信号')
        print(f'-' * 50)

        if results_df is None or results_df.empty:
            print(f' 没有结果数据')
            return None

        # 按不同指标找出最佳
        best_return = results_df.loc[results_df['total_return'].idxmax()]
        best_sharpe = results_df.loc[results_df['sharpe_ratio'].idxmax()]
        best_drawdown = results_df.loc[results_df['max_drawdown'].idxmax()]

        print(f" \n 按总收益排序")
        print(f" 最佳信号: {best_return['signal']}")
        print(f" 总收益: {best_return['total_return']:.2%}")
        print(f" 最大回撤: {best_return['max_drawdown']:.2%}")
        print(f" 夏普比率: {best_return['sharpe_ratio']:.4f}")

        print(f" \n 按夏普比率排序")
        print(f" 最佳信号: {best_sharpe['signal']}")
        print(f" 总收益: {best_sharpe['total_return']:.2%}")
        print(f" 最大回撤: {best_sharpe['max_drawdown']:.2%}")
        print(f" 夏普比率: {best_sharpe['sharpe_ratio']:.4f}")

        print(f" \n 按最大回撤排序")
        print(f" 最佳信号: {best_drawdown['signal']}")
        print(f" 总收益: {best_drawdown['total_return']:.2%}")
        print(f" 最大回撤: {best_drawdown['max_drawdown']:.2%}")
        print(f" 夏普比率: {best_drawdown['sharpe_ratio']:.4f}")

        # 综合评分 (收益高 + 回测小 + 夏普高)
        # 归一化评分
        results_copy = results_df.copy()

        # 收益越高越好
        results_copy['return_score'] = (results_copy['total_return'] - results_copy['total_return'].min
        ()) / (results_copy['total_return'].max() - results_copy['total_return'].min())

        # 回测越小越好 (负数越大越差, 所以取负值)
        results_copy['drawdown_score'] = (results_copy['max_drawdown'] - results_copy['max_drawdown'].min
        ()) / (results_copy['max_drawdown'].max() - results_copy['max_drawdown'].min())

        # 夏普越高越好
        results_copy['sharpe_score'] = (results_copy['sharpe_ratio'] - results_copy['sharpe_ratio'].min
        ()) / (results_copy['sharpe_ratio'].max() - results_copy['sharpe_ratio'].min())

        # 综合评分 (权重: 收益40%, 夏普30%, 回测30%)
        results_copy['combined_score'] = (0.4 * results_copy['return_score'] + 0.3 * results_copy['sharpe_score'] +
                                          0.3 * results_copy['drawdown_score'])

        # 找综合评分最高
        best_combined = results_copy.loc[results_copy['combined_score'].idxmax()]

        print(f" \n 综合评分最佳 (收益40% + 夏普30% + 回撤30%)")
        print(f" 最佳信号: {best_combined['signal']}")
        print(f" 综合评分: {best_combined['combined_score']:.4f}")
        print(f" 总收益: {best_combined['total_return']:.2%}")
        print(f" 最大回撤: {best_combined['max_drawdown']:.2%}")
        print(f" 夏普比率: {best_combined['sharpe_ratio']:.2%}")

        return {
            'by_return': best_return.to_dict(),
            'by_sharpe': best_sharpe.to_dict(),
            'by_drawdown': best_drawdown.to_dict(),
            'by_combined': best_combined.to_dict()
        }

    def generate_report(self, results_df, best_signals):
        """ 生产信号对比报告
        Args:
            results_df: compare_all_signals() 返回的结果
            best_signals: find_best_signal() 返回的结果
            """
        print(f'\n' + '-' * 80)
        print(f"生产信号报告")
        print(f"=" * 80)

        if results_df is None or results_df.empty:
            print(f"没有结果数据")
            return None

        # 按类型分组统计
        results_df['signal_type'] = results_df['signal'].apply(
            lambda x: 'MA' if x.startswith('MA_') else
            'RSI' if x.startswith('RSI_') else
            'Momentum' if x.startswith('Momentum_') else
            'Break' if x.startswith('Break_') else
            'Volatility' if x.startswith('Volatility_') else
            'other'
        )

        # 按类型统计
        type_stats = results_df.groupby('signal_type').agg({
            'total_return': ['mean', 'max', 'min'],
            'sharpe_ratio': ['mean', 'max'],
            'max_drawdown': ['mean', 'min']
        })

        print(f" \n 各信号类型统计: ")
        print(f" -" * 70)
        print(type_stats)

        # 各类型最佳信号
        print(f' \n 各类型最佳信号')
        print(f'-' * 70)

        for signal_type in ['MA', 'RSI', 'Momentum', 'Break', 'Volatility']:
            type_df = results_df[results_df['signal_type'] == signal_type]
            if not type_df.empty:
                best = type_df.loc[type_df['total_return'].idxmax()]
                print(f"\n {signal_type}: ")
                print(f" 最佳: {best['signal']}")
                print(f" 收益: {best['total_return']:.2%}")
                print(f" 回撤: {best['max_drawdown']:.2%}")
                print(f" 夏普: {best['sharpe_ratio']:.4f}")

        # 生产文本报告
        from datetime import datetime
        report_lines = []
        report_lines.append('=' * 70)
        report_lines.append('信号对比分析报告')
        report_lines.append('=' * 70)
        report_lines.append(f"生产时间: {datetime.now().strftime('%Y-%m-%d')}")
        report_lines.append("")

        report_lines.append(' 1. 最佳信号 (按总收益)')
        report_lines.append("-" * 50)
        if best_signals and 'by_return' in best_signals:
            best = best_signals['by_return']
            report_lines.append(f" 信号: {best['signal']}")
            report_lines.append(f" 总收益: {best['total_return']:.2%}")
            report_lines.append(f" 最大回撤: {best['max_drawdown']:.2%}")
            report_lines.append(f" 夏普比率: {best['sharpe_ratio']:.4f}")
        report_lines.append("")

        report_lines.append(" 2. 最佳信号 (按夏普比率) ")
        report_lines.append('-' * 50)
        if best_signals and 'by_sharpe' in best_signals:
            best = best_signals['by_sharpe']
            report_lines.append(f" 信号: {best['signal']}")
            report_lines.append(f" 总收益: {best['total_return']:.2%}")
            report_lines.append(f" 最大回撤: {best['max_drawdown']:.2%}")
            report_lines.append(f" 夏普比率: {best['sharpe_ratio']:.4f}")
        report_lines.append("")

        report_lines.append(" 3. 各类型最佳信号")
        report_lines.append("-" * 50)
        for signal_type in ['MA', 'RSI', 'Momentum', 'Break', 'Volatility']:
            type_df = results_df[results_df['signal_type'] == signal_type]
            if not type_df.empty:
                best = type_df.loc[type_df['total_return'].idxmax()]
                report_lines.append(f" {signal_type}: {best['signal']} (收益 {best['total_return']:.2%})")
        report_lines.append("")

        report_lines.append(" 4. 建议")
        report_lines.append('-' * 50)
        if best_signals and 'by_combined' in best_signals:
            best = best_signals['by_combined']
            report_lines.append(f" 推介信号: {best['signal']}")
            report_lines.append(f" 理由: 综合评分最高, 收益和风险平衡较好")
        report_lines.append('=' * 70)

        # 打印报告
        print(f" \n" + '\n'.join(report_lines))

        # 保存报告
        file_path = self.output_dir / "信号对比报告.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))

        print(f" \n 报告已保存: {file_path}")

        return report_lines


# 调用
if __name__ == "__main__":
    comparator = SignalComparator()

    # 1. 加载仓位数据
    comparator.load_data()

    # 对比所有信号 (核心功能)
    results = comparator.compare_all_signals()

    if results is not None:
        # 找出最佳信号
        best = comparator.find_best_signal(results)

        # 生产报告
        comparator.generate_report(results, best)
        print(f" 第6 任务完成")


"""
## 第6课：信号对比分析

**任务目标**：
- 对比多种信号策略（MA、RSI、动量、突破、波动率）的表现
- 按总收益、夏普比率、最大回撤分别找出最佳信号
- 综合评分选出最优信号
- 生成信号对比分析报告

**实现方案**：
1. **数据加载**：
   - 加载第4课生成的仓位数据（positions/*_仓位.xlsx）
   - 自动识别所有原始信号列（MA_、RSI_、Momentum_、Break_、Volatility_）
   - 排除已计算的仓位列

2. **单信号评估**：
   - 清洗价格数据（过滤无效价格）
   - 清洗仓位数据（替换inf、NaN为0，限制在[-1, 1]范围）
   - 计算总收益、最大回撤、夏普比率
   - 异常值处理（收益异常、夏普异常自动跳过）

3. **信号分类**：
   - 按信号类型分组：MA、RSI、Momentum、Break、Volatility
   - 统计各类型的平均收益、最大收益、平均夏普等

4. **最佳信号识别**：
   - **按总收益排序**：找出收益最高的信号
   - **按夏普比率排序**：找出风险调整后收益最高的信号
   - **按最大回撤排序**：找出回撤最小的信号
   - **综合评分**：收益40% + 夏普30% + 回撤30%，找出综合最优信号

5. **报告生成**：
   - 各信号类型统计汇总表
   - 各类型最佳信号列表
   - 综合推荐信号及理由
   - 保存为TXT报告文件

**核心代码结构**：
```python
class SignalComparator:
    ├── __init__()               # 初始化目录和文件查找
    ├── load_data()              # 加载所有仓位数据
    ├── evaluate_signal()        # 评估单个信号的表现
    ├── compare_all_signals()    # 对比所有信号，按收益排序
    ├── find_best_signal()       # 找出最佳信号（多维度）
    └── generate_report()        # 生成信号对比报告
```
"""


