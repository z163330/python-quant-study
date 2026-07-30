"""
目标：生成买卖信号

规则：
signal = 1  → 买
signal = 0  → 不操作
signal = -1 → 卖

常用信号：
MA均线（MA20 > MA50 买）
RSI（<30买 >70卖）
动量（20日涨幅高买）
突破（创新高买）
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class SignalGenerator:
    """信号生成"""
    def __init__(self):
        """初始化"""
        print(f'\n' + '=' * 80)
        print(f' 信号生成 - 初始化')
        print(f'=' * 80)

        # 1. 获取当前文件目录
        current_dir = Path(__file__).parent
        self.project_root = current_dir.parent
        print(f" 项目根目录: {self.project_root}")

        # 2. 设置数据目录 (读取清洗后的数据)
        self.data_dir = self.project_root / "DATA" / '清洗后的数据'
        self.signals_dir = self.project_root / "signals"
        self.signals_dir.mkdir(parents=True, exist_ok=True)
        print(f" 清洗后的数据目录: {self.data_dir}")
        print(f" 信号输出目录: {self.signals_dir}")

        # 3. 检查数据是否存在
        self.data_files = list(self.data_dir.glob("*_清洗后的数据.xlsx"))
        print(f" 找到文件: {len(self.data_files)} 个数据文件")

        # 4. 存储数据
        self.data = {}
        self.signals = {}

        print(f" \n" + '-' * 80)
        print(f" 初始化完成")
        print(f' -' * 80)

    def load_data(self):
        """加载清洗后的数据"""
        print(f'\n' + '=' * 80)
        print(f' 加载清洗后的数据')
        print('=' * 80)

        if not self.data_files:
            print(f' 没用找到数据文件......')
            return None

        for file_path in self.data_files:
            # 从文件名提取股票代码
            symbol = file_path.stem.replace("_清洗后的数据", "")
            print(f' \n 加载: {symbol}')

            try:
                df = pd.read_excel(file_path)
                print(f" 成功: {df.shape[0]} 行 x {df.shape[1]} 列")
                self.data[symbol] = df
            except Exception as e:
                print(f" 失败: {e}")
        print(f" \n 共加载 {len(self.data)} 只股票")
        return self.data

    def signal_ma(self, df, short_ma=20, long_ma=60, threshold=50):
        """
        均线信号: 短期均线 > 长期均线 -> 买入
        Args:
            df: DataFrame
            short_ma: 短期均线 (如5, 10, 20)
            long_ma: 长期均线 (如20, 60, 100)

        Returns:
            signal: 1 (买入), -1 (卖出)

        """
        ma_short_col = f"MA{short_ma}"
        ma_long_col = f"MA{long_ma}"

        if ma_short_col not in df.columns or ma_long_col not in df.columns:
            return np.zeros(len(df))

        # ================= 1. 基础信号 ================
        # 短期 > 长期 -> 基础买入信号
        base_signal = df[ma_short_col] > df[ma_long_col]

        # ==================2. 滚动买入 % (改进1) =================
        # 计算过去N天中, 买入信号的比例
        def calc_buy_pct(series):
            return series.sum() / len(series) * 100

        df['MA_signal_roll'] = base_signal.rolling(20).apply(calc_buy_pct)

        # 信号: 买入% >= threshold -> 买入, 否则卖出
        signal = np.where(df['MA_signal_roll'] >= threshold, 1, -1)
        return signal

    def signal_rsi(self, df, oversold=30, overbought=70):
        """
           RSI信号：<超卖阈值买入，>超买阈值卖出

           Args:
               df: DataFrame
               oversold: 超卖阈值（默认30）
               overbought: 超买阈值（默认70）

           Returns:
               signal: 1（买入）, -1（卖出）, 0（持有）
           """

        # 检查RSI列是否存在
        if "RSI_14" not in df.columns:
            print(f" 缺少列: RSI_14")
            return np.zeros(len(df))

        # 生成信号
        signal = np.zeros(len(df))
        signal[df['RSI_14'] < oversold] = 1     # 超卖 -> 买入
        signal[df['RSI_14'] > overbought] = -1  # 超买 -> 卖出

        return signal

    def signal_momentum(self, df, window=20, threshold=0):
        """
        动量信号: 动量 > threshold -> 买入, 动量 < threshold -> 卖出

        Args:
            df: DataFrame
            window: 动量窗口 (默认20天)
            threshold:  阈值 (默认0)

        Returns:
            signal: 1 (买入), -1 (卖出)
        """
        col = f'momentum_{window}'

        if col not in df.columns:
            print(f" 缺少列: {col}")
            return np.zeros(len(df))
        # 动量 > threshold -> 买入(1), 否则卖出(-1)
        signal = np.where(df[col] > threshold, 1, -1)
        return signal

    def signal_breakout(self, df, window=20):
        """
        突破信号: 创新高买入, 创新低卖出
        Args:
            df: DataFrame
            window: 窗口周期 (默认20天)
        Returns:
            signal: 1 (买入), -1 (卖出), 0 (持有)
        """
        high_col = f'high_{window}'
        low_col = f'low_{window}'

        if high_col not in df.columns or low_col not in df.columns:
            print(f" 缺少列: {high_col} 或 {low_col}")
            return np.zeros(len(df))

        signal = np.zeros(len(df))

        # 今日收盘价 > 昨日收盘价 -> 创新高 -> 买入
        signal[df['Close'] > df[high_col].shift(1)] = 1

        # 今日收盘价 < 昨日收盘价 -> 创新低 -> 卖出
        signal[df['Close'] < df[low_col].shift(1)] = -1
        return signal

    def signal_volatility(self, df, window=20, high_threshold=0.3, low_threshold=0.15):
        """
        波动率信号：低波动买入，高波动卖出/观望

        Args:
            df: DataFrame
            window: 波动率窗口（默认20天）
            high_threshold: 高波动阈值（默认0.3 = 30%）
            low_threshold: 低波动阈值（默认0.15 = 15%）

        Returns:
            signal: 1（买入）, -1（卖出）, 0（持有
        """

        vol_col = f'volatility_{window}'

        if vol_col not in df.columns:
            print(f' 缺少列: {vol_col}')
            return np.zeros(len(df))

        signal = np.zeros(len(df))

        # 低波动 -> 市场稳定 -> 买入
        signal[df[vol_col] < low_threshold] = 1

        # 高波动 -> 市场不稳定 -> 卖出
        signal[df[vol_col] > high_threshold] = -1

        return signal

    def run_all_signal(self):
        """循环所有股票, 测试所有信号, 打印最佳组合"""
        print(f'=' + '=' * 80)
        print(f' 运行所有信号测试')
        print(f'=' * 80)

        if not self.data:
            print(f" 没有数据")
            return
        all_results = []

        for symbol, df in self.data.items():
            print(f' \n 测试: {symbol} ({len(df)} 行)')
            if len(df) < 50:
                print(f" 数据太少, 跳过")
                continue

            # ========= 1. 测试均线信号 ==========
            print(f" \n 均线信号: ")
            ma_best = {'buy_pct': 0, 'short': None, 'long':None, 'threshold':None}
            # 测试所有的均线组合
            short_list = [5, 10, 20]
            long_list = [20, 60, 100, 150, 200]
            thresholds = [50, 55, 60, 65, 70]

            for short in short_list:
                for long in long_list:
                    if short >= long:
                        continue
                    for threshold in thresholds:
                        signal = self.signal_ma(df, short, long, threshold)
                        buy = sum(signal == 1)
                        buy_pct = buy / len(df) * 100
                        if buy_pct > ma_best['buy_pct']:
                            ma_best = {
                                'buy_pct': buy_pct,
                                'short': short,
                                'long': long,
                                'threshold': threshold
                            }
            print(f"最佳: MA{ma_best['short']} vs MA{ma_best['long']}"
                  f"阈值{ma_best['threshold']} -> 买入%:{ma_best['buy_pct']:.1f}%")

            # =========== 2. 测试RSI信号 ================
            print(f'\n RSI 信号: ')
            rsi_best = {'buy_pct':0, 'oversold':None, 'overbought':None}
            rsi_configs = [(30, 70), (25, 75), (20, 80), (35, 65)]
            for oversold, overbought in rsi_configs:
                signal = self.signal_rsi(df, oversold, overbought)
                buy = sum(signal == 1)
                buy_pct = buy / len(df) * 100
                if buy_pct > rsi_best['buy_pct']:
                    rsi_best = {
                        'buy_pct': buy_pct,
                        'oversold': oversold,
                        'overbought': overbought
                    }
            print(f"最佳: RSI{rsi_best['oversold']}/{rsi_best['overbought']} -> 买入%: {rsi_best['buy_pct']:.1f}%")

            # =============3. 测试动量信号 ==============
            print(f' \n 动量信号: ')
            mom_best = {'buy_pct':0, 'window':None, 'threshold':None}
            windows = [10, 20, 60]
            mom_thresholds = [0, 0.2, 0.05, -0.02]

            for window in windows:
                for threshold in mom_thresholds:
                    signal = self.signal_momentum(df, window, threshold)
                    buy = sum(signal == 1)
                    buy_pct = buy / len(df) * 100
                    if buy_pct > mom_best['buy_pct']:
                        mom_best = {
                            'buy_pct': buy_pct,
                            'window': window,
                            'threshold': threshold
                        }
            print(f" 最佳: {mom_best['window']}天, 阈值{mom_best['threshold']} -> 买入%: {mom_best['buy_pct']:.1f}%")

            # ================4 . 测试突破信号========================
            print(f' \n 突破信号:')
            break_best = {'buy_pct':0, 'window':None}
            windows = [20, 60]

            for window in windows:
                signal = self.signal_breakout(df, window)
                buy = sum(signal == 1)
                buy_pct = buy / len(df) * 100
                if buy_pct > break_best['buy_pct']:
                    break_best = {
                        'buy_pct': buy_pct,
                        'window': window
                    }
            print(f"最佳: {break_best['window']}天 -> 买入%: {break_best['buy_pct']:.1f}%")

            # ==============5. 测试波动率信号 ====================
            print(f' \n 波动率信号: ')
            vol_best = {'buy_pct':0, 'window':None, 'low':None, 'high':None}
            vol_window = [20,60]
            vol_configs = [(0.01, 0.03), (0.015, 0.025), (0.02, 0.04)]

            for window in vol_window:
                for low_th, high_th in vol_configs:
                    signal = self.signal_volatility(df, window, high_th, low_th)
                    buy = sum(signal == 1)
                    buy_pct = buy / len(df) * 100
                    if buy_pct > vol_best['buy_pct']:
                        vol_best = {
                            'buy_pct': buy_pct,
                            'window': window,
                            'low': low_th,
                            'high': high_th
                        }
            print(f"最佳: {vol_best['window']}天, 低{vol_best['low']}/高{vol_best['high']} -> 买入%; {vol_best['buy_pct']:.1f}%")

            # 存储结果
            all_results.append({
                '股票': symbol,
                '数据天数': len(df),
                '均线最佳': f"MA{ma_best['short']}xMA{ma_best['long']}(阈值{ma_best['threshold']})",
                '均线买入%': ma_best['buy_pct'],
                'RSI最佳': f"{rsi_best['oversold']}/{rsi_best['overbought']}",
                'RSI买入%': rsi_best['buy_pct'],
                '动量最佳': f"{mom_best['window']}天 (阈值{mom_best['threshold']})",
                '动量买入%': mom_best['buy_pct'],
                '突破最佳': f"{break_best['window']}天",
                '突破买入%': break_best['buy_pct'],
                '波动率最佳': f"{vol_best['window']}天 (低{vol_best['low']}/高{vol_best['high']})",
                '波动率买入%': vol_best['buy_pct']
            })

        # ================打印汇总表格 ==================
        print(f'\n'+'='* 80)
        print(f"所有股票最佳信号汇总")
        print(f'=' * 80)

        df_results = pd.DataFrame(all_results)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 200)

        print(df_results.to_string(index=False))

        # ============找出整体最佳 ===============
        if all_results:
            print(f'\n' +'=' * 80)
            print(f' 整体最佳信号股票: ')
            print(f' =' * 80)

            best_ma = max(all_results, key=lambda x: x['均线买入%'])
            print(f"均线信号最佳: {best_ma['股票']}({best_ma['均线最佳']}) -> 买入%: {best_ma['均线买入%']:.1f}%")

            best_mom = max(all_results, key=lambda x: x['动量买入%'])
            print(f"动量信号最佳: {best_mom['股票']}({best_mom['动量最佳']}) -> 买入%: {best_mom['动量买入%']:.1f}%")

            best_break = max(all_results, key=lambda x: x['突破买入%'])
            print(f"突破信号最佳: {best_break['股票']}({best_break['突破最佳']}) -> 买入%: {best_break['突破买入%']:.1f}%")

            best_vol = max(all_results, key=lambda x: x['波动率买入%'])
            print(f"波动率信号最佳: {best_vol['股票']}({best_vol['波动率最佳']}) -> 买入%: {best_vol['波动率买入%']:.1f}%")

    def save_signals(self):
        """保存所有股票的信号到Excel"""
        print(f'\n' + '=' * 80)
        print(f" 保存信号到文件")
        print(f"=" * 80)

        if not self.data:
            print(f' 没有数据')
            return None

        saved_files = []
        for symbol, df in self.data.items():
            print(f' \n 保存; {symbol}' )
            try:
                # 创建信号到DataFrame
                df_signals = df.copy()

                # 添加所有信号列
                # 1. 均线信号 (多种组合)
                short_list = [5, 10, 20]
                long_list = [20, 60, 100, 150, 200]

                for short in short_list:
                    for long in long_list:
                        if short >= long:
                            continue
                        # 用阈值50生成信号
                        signal = self.signal_ma(df, short, long, 50)
                        df_signals[f'MA_{short}_{long}'] = signal

                # 2. RSI 信号
                rsi_configs = [(30, 70), (25, 75), (20, 80), (35, 65)]
                for oversold, overbought in rsi_configs:
                    signal = self.signal_rsi(df, oversold, overbought)
                    df_signals[f'RSI_{oversold}_{overbought}'] = signal

                # 3. 动量信号
                windows = [10, 20, 60]
                mom_thresholds = [0, 0.02, 0.05, -0.02]
                for window in windows:
                    for threshold in mom_thresholds:
                        signal = self.signal_momentum(df, window, threshold)
                        df_signals[f'Momentum_{window}_{threshold}'] = signal

                # 4. 突破信号
                break_windows = [20, 60]
                for window in break_windows:
                    signal = self.signal_breakout(df, window)
                    df_signals[f'Break_{window}'] = signal

                # 5. 波动率信号
                vol_configs = [(0.01, 0.03), (0.015, 0.025), (0.02, 0.04)]
                for window in [20, 60]:
                    for low_th, high_th, in vol_configs:
                        signal = self.signal_volatility(df, window, high_th, low_th)
                        df_signals[f'Volatility_{window}_{low_th}_{high_th}'] = signal

                # 保存到Excel
                file_path = self.signals_dir / f"{symbol}_信号.xlsx"
                df_signals.to_excel(file_path, index=False)
                print(f' 保存成功: {file_path.name} ({df_signals.shape[0]}行 x {df_signals.shape[1]}列)')
                saved_files.append(str(file_path))
            except Exception as e:
                print(f" 保存失败: {e}")

        print(f' \n' + '=' * 80)
        print(f' 共保存: {len(saved_files)} 个文件')
        print(f' 保存目录: {self.signals_dir}')

        return saved_files


if __name__ == "__main__":
    generator = SignalGenerator()

    # 1. 加载数据
    generator.load_data()

    # 2. 运行所有信号测试 (信号所有股票)
    generator.run_all_signal()

    # 3. 保存信号到文件
    generator.save_signals()


"""
## 第3课：交易信号生成

**任务目标**：
- 设计多种交易信号规则（均线、RSI、动量、突破、波动率）
- 为每只股票生成买卖信号（1=买入，0=持有，-1=卖出）
- 测试不同参数组合，寻找最佳信号参数
- 保存所有信号数据到Excel文件

**实现方案**：
1. **信号规则设计**：
   - **均线信号**：短期均线 > 长期均线时买入，反之卖出（支持滚动买入比例优化）
   - **RSI信号**：超卖（<30）买入，超买（>70）卖出
   - **动量信号**：N日涨幅 > 阈值时买入，反之卖出
   - **突破信号**：创新高买入，创新低卖出
   - **波动率信号**：低波动买入，高波动卖出

2. **信号生成函数**：
   - **`signal_ma()`**：均线交叉信号，支持多组短期/长期均线组合和阈值参数
   - **`signal_rsi()`**：RSI超买超卖信号
   - **`signal_momentum()`**：动量信号
   - **`signal_breakout()`**：价格突破信号
   - **`signal_volatility()`**：波动率信号

3. **参数优化**：
   - **均线信号**：测试短均线[5,10,20]、长均线[20,60,100,150,200]、阈值[50,55,60,65,70]
   - **RSI信号**：测试[30/70, 25/75, 20/80, 35/65]组合
   - **动量信号**：测试窗口[10,20,60]、阈值[0,0.02,0.05,-0.02]
   - **突破信号**：测试窗口[20,60]
   - **波动率信号**：测试窗口[20,60]、阈值组合

4. **结果汇总**：
   - 为每只股票打印最佳信号参数和买入比例
   - 生成汇总表格，展示所有股票的最佳信号
   - 识别整体表现最好的信号股票

5. **信号保存**：
   - 为每只股票生成包含所有信号列的DataFrame
   - 保存为Excel文件到signals/目录
   - 文件名格式：`{股票代码}_信号.xlsx`

**核心代码结构**：
```python
class SignalGenerator:
    ├── __init__()               # 初始化目录和文件查找
    ├── load_data()              # 加载清洗后的数据
    ├── signal_ma()              # 均线信号（金叉/死叉）
    ├── signal_rsi()             # RSI超买超卖信号
    ├── signal_momentum()        # 动量信号
    ├── signal_breakout()        # 突破信号（创新高/新低）
    ├── signal_volatility()      # 波动率信号
    ├── run_all_signal()         # 测试所有信号并打印最佳组合
    └── save_signals()           # 保存所有信号到Excel
```
"""




