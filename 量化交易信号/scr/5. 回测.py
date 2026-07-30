"""
目标：看策略赚钱没

指标：

总收益
最大回撤
夏普比率
"""

import pandas as pd
import numpy as np
from pathlib import Path



class StrategyEvaluator:
    """策略表现评估"""
    def __init__(self):
        """ 初始化"""
        print(f'\n' + '=' * 80)
        print(f" 策略表现评估 - 初始化")
        print(f'=' * 80)

        # 1. 获取当前文件目录
        current_dir = Path(__file__).parent
        self.project_root = current_dir.parent
        print(f" 项目根目录: {self.project_root}")

        # 2. 设置目录
        self.positions_dir = self.project_root / 'positions'
        self.output_dir = self.project_root / 'evaluations'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f' 仓位数据目录: {self.positions_dir}')
        print(f" 评估输出目录: {self.output_dir}")

        # 3. 检查仓位文件
        self.position_files = list(self.positions_dir.glob("*_仓位.xlsx"))
        print(f" 找到{len(self.position_files)} 个仓位文件")

        # 4. 存储数据
        self.positions = {}
        self.results = {}

        print(f" \n" + '=' * 80)
        print(f" 初始化完成")
        print(f'-' * 80)

    def load_positions(self):
        """加载所有仓位数据"""
        print(f"\n" + '=' * 80)
        print(f"加载仓位数据")
        print(f"=" * 80)

        if not self.position_files:
            print(f" 没有找到仓位数据")
            return None

        for file_path in self.position_files:
            # 从文件名提取股票代码
            symbol = file_path.stem.replace("_仓位", "")
            print(f' \n 加载: {symbol}')

            try:
                df = pd.read_excel(file_path)
                print(f" 成功: {df.shape[0]} 行 x {df.shape[1]} 列")
                self.positions[symbol] = df
            except Exception as e:
                print(f" 失败: {e}")

        print(f" \n 共加载 {len(self.positions)} 只股票")
        return self.positions

    def prepare_data(self, df, position_col):
        """
        准备数据: 清洗和计算基础指标
        Args:
            df: 原始DataFrame
            position_col: 仓位列名
        Returns:
            df_temp: 清洗后的DateFrame (包含基础指标)
        """

        # 1. 检查数据
        if position_col not in df.columns:
            return None

        # 2. 复制数据
        df_temp = df.copy()

        # 3. 清洗价格数据
        df_temp = df_temp[df_temp['Close'] > 0]
        df_temp = df_temp[df_temp['Close'].notna()]
        if len(df_temp) < 2:
            return None

        # 4. 清洗仓位数据
        # 将 inf 和 -inf 替换为 0
        df_temp[position_col] = df_temp[position_col].replace([np.inf, -np.inf], 0)

        # 将 Nan 替换为0
        df_temp[position_col] = df_temp[position_col].fillna(0)

        # 限制仓位在 [-5, 5] 之间 (防止异常值)
        df_temp[position_col] = df_temp[position_col].clip(-5, 5)

        # 5. 计算每日收益率
        df_temp['daily_return'] = df_temp['Close'].pct_change()
        df_temp['daily_return'] = df_temp['daily_return'].replace([np.inf, -np.inf], 0)
        df_temp['daily_return'] = df_temp['daily_return'].fillna(0)

        # 6. 计算策略每日收益 = 仓位 x 日收益率
        df_temp['strategy_return'] = df_temp[position_col] * df_temp['daily_return']
        df_temp['strategy_return'] = df_temp['strategy_return'].replace([np.inf, -np.inf], 0)

        # 7. 计算累计净值
        df_temp['cumulative_return'] = (1 + df_temp['strategy_return']).cumprod()
        return df_temp

    def calculate_total_return(self, df_clean):
        """计算总收益

        Args:
            df_clean: prepare_data() 清洗后的数据

        Returns:
            total_return: 总收益率（小数)
        """

        if df_clean is None:
            return np.nan

        #总收益 = 最终净值 - 1
        total_return = df_clean['cumulative_return'].iloc[-1] - 1

        # 检查是否有效
        if not np.isfinite(total_return):
            return np.nan

        return total_return

    def calculate_max_drawdown(self, df_clean):
        """
        计算最大回撤

        Args:
            df_clean: prepare_data() 清洗后的数据

        Returns:
            max_drawdown: 最大回撤（负数）
        """
        if df_clean is None:
            return np.nan

        # 1. 获取累计净值
        cumulative = df_clean['cumulative_return']

        # 2. 计算历史最高净值 (滚动最大值)
        running_max = cumulative.expanding().max()

        # 3. 计算回撤 = (当前净值 - 历史最高) /历史最高
        drawdown = (cumulative - running_max) / running_max

        # 4. 最大回撤 = 回撤的最小值 (负数最大)
        max_drawdown = drawdown.min()

        # 5. 检查是否有效
        if not np.isfinite(max_drawdown):
            return np.nan

        return max_drawdown

    def calculate_sharpe_ratio(self, df_clean, risk_free_rate=0.02):
        """
        计算夏普比率

        Args:
            df_clean: prepare_data() 清洗后的数据
            risk_free_rate: 无风险利率（默认2%）

        Returns:
            sharpe_ratio: 夏普比率
        """
        if df_clean is None:
            return np.nan

        # 1. 计算总收益
        total_return = df_clean['cumulative_return'].iloc[-1] - 1

        # 2. 计算年化收益率
        days = len(df_clean)
        if days == 0:
            return np.nan

        annuel_return = (1+total_return) ** (252/days) - 1

        # 3. 计算年化波动率
        daily_std = df_clean['strategy_return'].std()
        if daily_std == 0 or np.isnan(daily_std):
            return np.nan
        annuel_volatility = daily_std * np.sqrt(252)

        # 4. 夏普比率 = (年化收益 - 无风险利率) / 年化波动率
        sharpe = (annuel_return - risk_free_rate) / annuel_volatility

        # 5. 检查是否有效
        if not np.isfinite(sharpe):
            return np.nan

        return sharpe

    def evaluate_all(self):
        """评估所有股票的策略表现.  就是循环所有股票"""
        print(f" \n" + '=' * 80)
        print(f" 评估所有策略表现")
        print(f' =' * 80)

        if not self.positions:
            print(f" 没有仓位数据")
            return None

        results = []

        for symbol, df in self.positions.items():
            print(f" \n 评估: {symbol}")

            # 使用总仓位_等权
            position_col = '总仓位_等权'

            if position_col not in df.columns:
                print(f" 没有找到 {position_col} 列, 跳过")
                continue

            # 准备数据
            df_clean = self.prepare_data(df, position_col)

            if df_clean is None:
                print(f" 数据准备失败, 跳过")
                continue

            # ==================== 计算指标==========================
            # 调用总收益
            total_return = evaluator.calculate_total_return(df_clean)
            # 调用最大回撤
            max_drawdown = evaluator.calculate_max_drawdown(df_clean)
            # 调用夏普比率
            sharpe = evaluator.calculate_sharpe_ratio(df_clean)

            # 保存结果
            result = {
                '股票': symbol,
                '总收益': total_return,
                '最大回撤': max_drawdown,
                '夏普比率': sharpe,
                '数据天数': len(df_clean)
            }
            results.append(result)

            # 显示结果
            print(f" 总收益: {total_return:.2%}" if pd.notna(total_return) else "总收益: N/A")
            print(f" 最大回撤: {max_drawdown:.2%}" if pd.notna(max_drawdown) else "最大回撤: N/A")
            print(f" 夏普比率: {sharpe:.4f}" if pd.notna(sharpe) else "夏普比率: N/A")

        # 汇总表格
        results_df = pd.DataFrame(results)
        print(f"\n" + "=" * 50)
        print(f" 评估汇总")
        print(f'=' * 50)
        print(results_df.to_string(index=False))

        self.results = results_df
        return results_df


if __name__ == "__main__":
    evaluator = StrategyEvaluator()

    # 加载仓位数据
    evaluator.load_positions()

    # 调用评估所有股票
    results = evaluator.evaluate_all()

    if results is not None:
        print(f"\n 评估完成, 共 {len(results)} 只股票")
        # 按总收益排序
        best = results.loc[results['总收益'].idxmax()]
        worst = results.loc[results['总收益'].idxmin()]

        print(f"\n 最佳表现: {best['股票']} (收益: {best['总收益']:.2%}), 夏普: {best['夏普比率']:.4f}")
        print(f"\n 最差表现: {worst['股票']} (收益: {worst['总收益']:.2%}), 夏普: {worst['夏普比率']:.4f}")






















"""
## 第5课：策略表现评估

**任务目标**：
- 计算策略的总收益（累计净值 - 1）
- 计算最大回撤（净值从高点到低点的最大跌幅）
- 计算夏普比率（风险调整后收益）
- 汇总所有股票的策略表现，找出最佳/最差策略

**实现方案**：
1. **数据加载与准备**：
   - 加载第4课生成的仓位数据（positions/*_仓位.xlsx）
   - 清洗价格数据（过滤无效价格）
   - 清洗仓位数据（替换inf、NaN为0，限制在[-5, 5]范围）
   - 计算日收益率和策略日收益（仓位×日收益率）

2. **总收益计算**：
   - **公式**：`总收益 = 最终净值 - 1`
   - 净值通过`(1 + 策略日收益率)`的累积乘积计算

3. **最大回撤计算**：
   - **公式**：`回撤 = (当前净值 - 历史最高净值) / 历史最高净值`
   - **最大回撤** = 回撤的最小值（负数最大，代表最大亏损）

4. **夏普比率计算**：
   - **公式**：`夏普比率 = (年化收益率 - 无风险利率) / 年化波动率`
   - 年化收益率 = `(1 + 总收益)^(252/天数) - 1`
   - 年化波动率 = 日收益率标准差 × √252
   - 无风险利率默认2%（可配置）

5. **结果汇总**：
   - 生成所有股票的评估汇总表（股票、总收益、最大回撤、夏普比率、数据天数）
   - 识别最佳表现股票（最高总收益）
   - 识别最差表现股票（最低总收益）

**核心代码结构**：
```python
class StrategyEvaluator:
    ├── __init__()               # 初始化目录和文件查找
    ├── load_positions()         # 加载所有仓位数据
    ├── prepare_data()           # 数据清洗和基础指标计算
    ├── calculate_total_return() # 计算总收益
    ├── calculate_max_drawdown() # 计算最大回撤
    ├── calculate_sharpe_ratio() # 计算夏普比率
    └── evaluate_all()           # 评估所有股票策略表现
```
"""






