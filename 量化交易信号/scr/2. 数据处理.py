"""
目标：让数据可以计算

内容：

计算收益率（pct_change）
shift（避免未来函数）
rolling（移动窗口）
清洗缺失值

输出：

干净价格数据
收益率数据

"""
import pandas as pd
import numpy as np
from pathlib import Path

class DataCleaner:
    """数据清洗与计算"""
    def __init__(self):
        """第1步: 初始化"""
        print('\n' + '=' * 80)
        print(f' 数据清洗与计算 - 初始化')
        print('=' * 80)

        # 1. 获取当前文件目录
        current_dir = Path(__file__).parent
        self.project_root = current_dir.parent
        print(f" 项目根目录: {self.project_root}")

        # 2. 设置数据目录
        self.raw_dir = self.project_root / "DATA" / "raw"
        self.processed_dir = self.project_root / 'DATA' / '清洗后的数据'
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        print(f' 原始数据目录: {self.raw_dir}')
        print(f" 清洗后数据目录: {self.processed_dir}")

        # 3. 检查原始数据是否存在
        self.raw_files = list(self.raw_dir.glob("*.xlsx"))
        print(f" 找到 {len(self.raw_files)} 个原始数据文件")

        # 4. 存储数据
        self.raw_data = {}
        self.cleaned_data = {}

        print(f' \n' + '=' * 50)
        print(f' 初始化完成')
        print('=' * 50)

    def load_data(self):
        """第2步: 加载所有原始数据"""
        print('\n' + '=' * 80)
        print(f' 加载原始数据')
        print(f' =' * 70)

        if not self.raw_files:
            print(f" 没有找到原始数据文件")
            return None

        for file_path in self.raw_files:
            symbol = file_path.stem   # 文件名就是股票代码
            print(f" \n 加载: {symbol}")

            try:
                df = pd.read_excel(file_path)
                print(f' 成功: {df.shape[0]}行 x {df.shape[1]}列')

                #显示列名
                print(f" 列名: {list(df.columns)}")

                # 显示前3行
                print(f' \n 前3行数据: ')
                print(f" {df.head(3)}")

                self.raw_data[symbol] = df
            except Exception as e:
                print(f" 失败: {e}")

        print(f" \n 共加载: {len(self.raw_data)} 只股票")
        print('=' * 50)

        return self.raw_data

    def calculate_returns(self):
        """计算所有股票的收益率"""
        print(f'\n' + '=' * 70)
        print(f' 计算收益率')
        print('=' * 70)

        if not self.raw_data:
            print(f" 没有数据")
            return None

        for symbol, df in self.raw_data.items():
            print(f" {symbol}")

            # 按日期排序
            df = df.sort_values('Date')

            # 日收益率: (今日 - 昨日) / 昨日
            df['daily_return'] = df['Close'].pct_change()

            # 累计收益率 (从1开始)
            df['cumulative_return'] = (1 + df['daily_return']).cumprod()

            # 使用 loc 设置第一行 (避免警告)
            df.loc[df.index[0], 'cumulative_return'] = 1.0

            # 对数收益率
            df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))

            print(f" 日收益率: {df['daily_return'].count()} 个有效数据")
            print(f" 累计收益率: {df['cumulative_return'].iloc[-1]:.4f}")
            print(f" 对数收益率: {df['log_return'].iloc[-1]:.4f}")

            self.raw_data[symbol] = df

        print(f" \n" + '=' * 80)
        print(f" 收益率计算完成")
        return self.raw_data

    def calculate_indicators(self):
        """ 计算计算指标(MA, EMA, 动量, macd, 价格, rsi)"""
        print(f'\n' + '=' * 80)
        print(f' 计算所有技术指标')
        print(f'=' * 80)

        if not self.raw_data:
            print(f" 没用数据")
            return None

        for symbol, df in self.raw_data.items():
            print(f" \n {symbol}")

            df = df.sort_values("Date")

            # 1. 移动平均线
            for p in [5, 10, 20, 60, 100, 150, 200]:
                df[f"MA{p}"] = df['Close'].rolling(p).mean()

            # 2. MACD (多组参数)
            macd_params = [
                (12, 26, 9),
                (5, 35, 5),
                (8, 21, 5),
                (10, 30, 7),
                (20, 50, 9)
            ]

            for fast, slow, signal in macd_params:
                ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
                ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
                macd = ema_fast - ema_slow
                macd_signal = macd.ewm(span=signal, adjust=False).mean()
                macd_hist = macd - macd_signal

                df[f"MACD_{fast}_{slow}_{signal}"] = macd
                df[f"MACD_signal_{fast}_{slow}_{signal}"] = macd_signal
                df[f"MACD_hist_{fast}_{slow}_{signal}"] = macd_hist


            # 3. 波动率
            df['volatility_20'] = df['daily_return'].rolling(20).std()
            df['volatility_60'] = df['daily_return'].rolling(60).std()

            # 4. 动量
            df['momentum_10'] = df['Close'].pct_change(10)
            df['momentum_20'] = df['Close'].pct_change(20)
            df['momentum_60'] = df['Close'].pct_change(60)

            # 5. 价格位置
            df['high_20'] = df['Close'].rolling(20).max()
            df['low_20'] = df['Close'].rolling(20).min()
            df['high_60'] = df['Close'].rolling(60).max()
            df['low_60'] = df['Close'].rolling(60).min()

            # 6. RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['RSI_14'] = 100 - (100 / (1 + rs))
            print(f' 计算完成: {df.shape[1]} 列')

            self.raw_data[symbol] = df

        # 显示列名 ( 移到循环外面, 只显示一次)
        first_symbol = list(self.raw_data.keys())[0]
        columns = self.raw_data[first_symbol].columns.tolist()
        print(f' 总列数: {len(columns)}')
        print(f" {columns}")


        print(f' \n' + '=' * 80)
        print(f" 所有指标计算完成")
        return self.raw_data

    def clean_data(self):
        """清洗缺失值"""
        print(f'\n' + '=' * 50)
        print(f' 清洗缺失值')
        print(f'=' * 50)

        if not self.raw_data:
            print(f' 没用数据')
            return None

        for symbol, df in self.raw_data.items():
            print(f' \n {symbol}')

            before = len(df)
            # 用前一行数据填充
            df = df.ffill() # ffill -> forward fill

            # 如果第一行还是NAN, 用后一行填充
            df = df.bfill()     #bfill -> backward fill

            after = len(df)

            print(f" 清洗前: {before} 行")
            print(f" 清洗后: {after} 行")
            print(f" 删除: {before - after} 行")

            self.raw_data[symbol] = df

        print(f"\n" + '=' * 50)
        print(f" 数据清洗完成")
        return self.raw_data

    def save_data(self):
        """保存清洗后的数据"""
        print(f'\n' + '=' * 50)
        print(f' 保存清洗后的数据')
        print('=' * 50)

        if not self.raw_data:
            print(" 没用数据")
            return None

        saved_files = []

        for symbol, df, in self.raw_data.items():
            file_path = self.processed_dir / f"{symbol}_清洗后的数据.xlsx"
            df.to_excel(file_path, index=False)
            print(f" {symbol}: 保存成功: ({df.shape[0]} 行)")
            saved_files.append(str(file_path))

        print(f" \n 共保存: {len(saved_files)} 个文件")
        print(f" 保存目录: {self.processed_dir}")

        return saved_files

    def run(self):
        """运行完整流程"""
        print(f'\n' + '=' * 80)
        print(f' 运行完整清洗流程')
        print(f'=' * 80)

        # 1. 加载数据
        data = self.load_data()
        if not data:
            return

        # 2. 计算收益率
        self.calculate_returns()

        # 3. 计算指标
        self.calculate_indicators()

        # 4. 清洗缺失值
        self.clean_data()

        # 5. 保存数据
        self.save_data()


# 调用
if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.run()


"""
## 第2课：数据清洗与指标计算

**任务目标**：
- 计算日收益率、累计收益率和对数收益率
- 计算多种技术指标（移动平均线、MACD、波动率、动量、RSI）
- 清洗缺失值（前向填充、后向填充）
- 保存清洗后的数据到指定目录

**实现方案**：
1. **数据加载**：
   - 自动定位第1课生成的原始数据目录（DATA/raw/）
   - 加载所有Excel文件，按股票代码存储
   - 自动创建清洗后数据输出目录（DATA/清洗后的数据/）

2. **收益率计算**：
   - **日收益率**：`pct_change()` 计算（今日-昨日）/ 昨日
   - **累计收益率**：`(1 + 日收益率)` 的累积乘积，从1开始
   - **对数收益率**：`ln(Close / Close.shift(1))`

3. **技术指标计算**：
   - **移动平均线**：5、10、20、60、100、150、200日均线
   - **MACD**：多组参数组合（12/26/9、5/35/5、8/21/5、10/30/7、20/50/9），包含DIF、Signal、Histogram
   - **波动率**：20日和60日滚动标准差
   - **动量**：10日、20日、60日价格变化率
   - **价格位置**：20日和60日最高价/最低价
   - **RSI**：14日相对强弱指标

4. **数据清洗**：
   - **前向填充**：使用前一行数据填充缺失值
   - **后向填充**：如果第一行仍有缺失，使用后一行填充
   - 显示清洗前后的数据行数变化

5. **结果保存**：
   - 保存为Excel文件到DATA/清洗后的数据/目录
   - 文件名格式：`{股票代码}_清洗后的数据.xlsx`

**核心代码结构**：
```python
class DataCleaner:
    ├── __init__()               # 初始化目录和文件查找
    ├── load_data()              # 加载所有原始数据
    ├── calculate_returns()      # 计算日收益率、累计收益率、对数收益率
    ├── calculate_indicators()   # 计算MA、MACD、波动率、动量、RSI
    ├── clean_data()             # 前向填充和后向填充清洗缺失值
    ├── save_data()              # 保存清洗后的数据到Excel
    └── run()                    # 运行完整清洗流程
```
"""



