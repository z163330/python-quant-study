"""
目标：信号变成仓位

方法：
固定仓位（简单）
等权分配

公式：
position = signal × weight

"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class PositionCalculator:
    """仓位计算"""
    def __init__(self):
        """初始化"""
        print(f'\n' + '=' * 80)
        print(f' 仓位计算 - 初始化')
        print(f' =' * 70)

        # 1. 获取当前文件目录
        current_dir = Path(__file__).parent
        self.project_root = current_dir.parent
        print(f' 项目根目录: {self.project_root}')

        # 2. 设置信号目录
        self.signals_dir = self.project_root / "signals"
        self.output_dir = self.project_root / "positions"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f" 信号目录: {self.signals_dir}")
        print(f" 仓位输入目录: {self.output_dir}")

        # 3. 检查信号文件是否存在
        self.signal_files = list(self.signals_dir.glob("*_信号.xlsx"))
        print(f" 找到: {len(self.signal_files)} 个信号文件")

        # 4. 存储数据
        self.signals = {}
        self.positions = {}

        print(f' \n' + '=' * 80)
        print(f' 初始化完成')
        print(f'-' * 80)

    def load_signals(self):
        """加载所有信号数据"""
        print(f'\n' +'=' * 80)
        print(f" 加载信号数据")
        print(f'=' * 80)

        # 1. 检查是否有信号文件
        if not self.signal_files:
            print(f' 没有找到信号文件')
            return None

        # 2. 循环加载每一个文件
        for file_path in self.signal_files:
            # 从文件名提取股票代码
            symbol = file_path.stem.replace("_信号", "")
            print(f" \n 加载: {symbol}")

            try:
                # 读取Excel 文件
                df = pd.read_excel(file_path)
                print(f" 成功: {df.shape[0]}行 x {df.shape[1]}列")

                # 保存到字典
                self.signals[symbol] = df
            except Exception as e:
                print(f" 失败: {e}")

        # 3. 显示加载结果
        print(f" 共加载 {len(self.signals)} 只股票")
        print(f' -' * 80)
        return self.signals

    def normalize_signal(self, signal):
        """将信号归一化到 [-1, 1] 区间

            Args:
              signal: 原始信号值（可能是任意范围）

            Returns:
              归一化后的信号值，范围在 [-1, 1] 之间
        """

        # 1. 处理无穷值和缺失值
        signal = signal.replace([np.inf, -np.inf], np.nan)
        signal = signal.fillna(0)

        # 2. 如果所有值都相同, 返回0
        if signal.nunique() <= 1:
            return pd.Series(0, index=signal.index)

        # 3. 使用百分位数法归一化 (抗异常值)
        # 使用1% 和 99% 分位数, 避免极端值异常
        lower = signal.quantile(0.01)
        upper = signal.quantile(0.99)

        # 如果上下限相同, 使用最小最大值
        if upper <= lower:
            lower = signal.min()
            upper = signal.max()

        # 4. 映射到 [-1, 1]
        signal_normalized = 2 * (signal - lower) / (upper - lower) - 1

        # 5. 限制在 [-1, 1] 范围内
        signal_normalized = signal_normalized.clip(-1, 1)

        return signal_normalized



    def calculate_fixed_position(self, df, signal_col, weight=1.0):
        """固定仓位：每次信号都用相同的仓位"""
        if signal_col not in df.columns:
            print(f" 缺少列: {signal_col}")
            return None

        # 获取信号并归一化
        signal = df[signal_col]
        signal_normalized = self.normalize_signal(signal)

        # 计算仓位 = 归一化信号 x 权重
        position = signal_normalized * weight
        return position



    def calculate_all_position(self):
        """计算所有股票的仓位"""
        print(f'=' * 80 + '\n')
        print(f" 计算所有仓位")
        print(f'=' * 70)

        # 1. 检查是否有信号数据
        if not self.signals:
            print(f" 没有信号数据")
            return None

        # 2. 定义要测试的权重
        weights = [0.05, 0.10, 0.25, 0.5, 0.75, 1.0]     # 5%, 10%, 25%, 50%, 75%, 100%
        print(f" 权重: {[f'{w*100:.0f}%' for w in weights]}")

        # 循环处理每只股票
        for symbol, df in self.signals.items():
            print(f" \n 计算仓位: {symbol}")

            # 复制数据
            df_positions = df.copy()

            # 找出所有信号列
            signal_cols = [col for col in df.columns if any(x in col for x in ['MA_', 'RSI_', 'Momentum_', 'Break_', 'Volatility_'])]
            print(f" 找到{len(signal_cols)}个信号列")

            # ===============添加: 检查信号值范围 ===================
            if signal_cols:
                sample_col = signal_cols[0]
                print(f" 信号值范围: {df[sample_col].min():.0f} ~ {df[sample_col].max():.0f}")
                print(f" 信号值分布: {df[sample_col].value_counts().to_dict()}")

            # 收集所有新列
            new_columns = []

            # 为每个信号列计算不同权重的仓位
            for signal_col in signal_cols:
                # 归一化信号到 [-1, 1]
                signal_normalized = self.normalize_signal(df[signal_col])

                # 显示归一化后的信号范围
                if signal_col == signal_cols[0]:
                    print(f" 归一化后信号范围: {signal_normalized.min():.2f} ~ {signal_normalized.max():.2f}")

                for weight in weights:
                    # 仓位 = 归一化信号 x 权重
                    position = signal_normalized * weight
                    col_name = f"{signal_col}_仓位_{int(weight*100)}%"
                    new_columns.append((col_name, position))

            # 一次性添加所有列
            for col_name, position in new_columns:
                df_positions[col_name] = position

            # 计算等权总仓位
            position_cols = [col for col in df_positions.columns if col.endswith("_仓位_100%")]
            if position_cols:
                df_positions['总仓位_等权'] = df_positions[position_cols].mean(axis=1)
                print(f" 等权总仓位已计算 (基于{len(position_cols)} 个信号) ")

                # =========== 显示等权总仓位数据 ==================
                print(f"\n 等权总仓位数据")
                print(f" {'日期':<12} {'总仓位_等权':<12}{'买入/卖出':<10}")
                print(f"=" * 80)

                # 取前10行
                for idx, row in df_positions.head(10).iterrows():
                    date_str = row['Date'].strftime('%Y-%m-%d') if 'Date' in row else str(idx)
                    position_val = row['总仓位_等权']

                    if position_val > 0.05:
                        action = "买入"
                    elif position_val < -0.05:
                        action = "卖出"
                    else:
                        action = "空仓"
                    print(f" {date_str:<12}{position_val:<12.2f}{action:<10}")

                # 统计总仓位
                pos_mean = df_positions['总仓位_等权'].mean()
                pos_max = df_positions['总仓位_等权'].max()
                pos_min = df_positions['总仓位_等权'].min()
                pos_std = df_positions['总仓位_等权'].std()

                print(f" \n 等权总仓位统计: ")
                print(f" 平均仓位: {pos_mean:.4f}")
                print(f" 最大仓位: {pos_max:.4f}")
                print(f" 最小仓位: {pos_std:.4f}")
                print(f" 标准差: {pos_std:.4f}")

                # ============检查仓位是否正常================
                if pos_max > 1.5 or pos_min < -1.5:
                    print(f" 仓位异常! 信号值可能不是 -1 和 1")
                    print(f' 请检查信号生产信号, 确保信号值为 -1, 0, 1')

            # 保存到对象
            self.positions[symbol] = df_positions
            print(f' 仓位计算完成: {df_positions.shape[1]}列')

        print(f" \n" + '=' * 80)
        print(f" 所有仓位计算完成")
        return self.positions

    def save_position(self):
        """保存仓位数据到Excel"""
        print(f"\n" + '=' * 50)
        print(f" 保存仓位数据")
        print(f'=' * 60)

        # 1. 检查是否又仓位数据
        if not self.positions:
            print(f" 没有仓位数据")
            return None

        saved_files = []

        # 2. 循环保存每只股票
        for symbol, df in self.positions.items():
            print(f" \n 保存: {symbol}")

            try:
                file_path = self.output_dir / f"{symbol}_仓位.xlsx"
                df.to_excel(file_path, index=False)
                print(f' 保存成功: {file_path.name} ({df.shape[0]} 行 x {df.shape[1]}列)')
                saved_files.append(str(file_path))
            except Exception as e:
                print(f' 保存失败: {e}')

        # 3. 显示保存结果
        print(f"\n" +'=' * 60)
        print(f" 共保存: {len(saved_files)}个文件")
        print(f" 保存目录: {self.output_dir}")

        return saved_files

if __name__ == "__main__":
    calculator = PositionCalculator()

    # 加载信号数据
    calculator.load_signals()

    # 测试单个信号的仓位计算
    if calculator.signals:
        symbol = list(calculator.signals.keys())[0]
        df = calculator.signals[symbol]
        print(f" \n 测试仓位计算: {symbol}")
        print(f" -" * 50)

        # 找出所有信号列 (包含 MA_, RSI_, Momentum_, Break_, Volatility_ 的列)
        signal_cols = [col for col in df.columns if any(x in col for x in ['MA_', 'RSI_', 'Momentum_', 'Break_', 'Volatility_'])]
        print(f' \n 找到{len(signal_cols)}个信号列')

        if signal_cols:
            # 测试前3个信号列
            for signal_col in signal_cols[:3]:
                print(f" 信号列: {signal_col}")

                # 显示归一化前后的对比
                original = df[signal_col]
                normalized = calculator.normalize_signal(original)
                print(f" 原始信号: min={original.min():.2f}, max={original.max():.2f}")
                print(f" 归一化: min={normalized.min():.2f}, max={normalized.max():.2f}")


                # 测试不同权重
                for weight in [0.5, 0.75, 1.0]:
                    position = calculator.calculate_fixed_position(df, signal_col, weight)
                    buy_days = sum(position > 0.05)
                    sell_days = sum(position < -0.05)
                    hold_days = sum(position <= 0.05)
                    print(f" 权重: {weight*100:.0f}% -> 买入{buy_days}天, 卖出{sell_days}天, 空仓{hold_days}天")
        else:
            print(f" 没有找到信号列")

    calculator.calculate_all_position()

    # 保存仓位数据
    calculator.save_position()

"""
## 第4课：仓位计算

**任务目标**：
- 将交易信号转换为实际仓位
- 实现固定仓位分配（信号×权重）
- 实现等权分配（多信号平均）
- 信号归一化处理（将任意范围信号映射到[-1, 1]）
- 保存仓位数据到Excel文件

**实现方案**：
1. **信号归一化**：
   - 处理无穷值和缺失值（替换为NaN，再填充为0）
   - 使用百分位数法归一化（1%和99%分位数，抗异常值）
   - 映射到[-1, 1]区间：`2 × (信号 - 下限) / (上限 - 下限) - 1`
   - 限制在[-1, 1]范围内

2. **仓位计算方法**：
   - **固定仓位**：`仓位 = 归一化信号 × 权重`（权重可调：5%、10%、25%、50%、75%、100%）
   - **等权分配**：所有100%仓位的信号取平均值
   - 信号值范围检查，异常值告警

3. **仓位统计**：
   - 统计买入天数（仓位 > 0.05）、卖出天数（仓位 < -0.05）、空仓天数
   - 计算平均仓位、最大仓位、最小仓位、标准差
   - 显示前10行仓位数据及对应的买卖操作

4. **结果保存**：
   - 保存为Excel文件到positions/目录
   - 文件名格式：`{股票代码}_仓位.xlsx`
   - 包含所有信号列对应的仓位列

**核心代码结构**：
```python
class PositionCalculator:
    ├── __init__()               # 初始化目录和文件查找
    ├── load_signals()           # 加载所有信号数据
    ├── normalize_signal()       # 信号归一化（映射到[-1, 1]）
    ├── calculate_fixed_position()  # 固定仓位计算（信号×权重）
    ├── calculate_all_position() # 计算所有股票的仓位
    └── save_position()          # 保存仓位数据到Excel
```
"""










