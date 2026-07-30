"""
目标: 获取股票价格数据

内容:
获取OHLCV (open, high, low, close, volume)
多股票数据
保存Excel

"""

import pandas as pd
import numpy as np
from pathlib import Path
import yfinance as yf
from datetime import datetime

class StockDataFetcher:
    """股票数据获取"""
    def __init__(self):
        """初始化获取数据"""
        print(f'\n' + '=' * 80 )
        print(f' 获取数据')
        print('=' * 50)

        # 1. 获取当前文件目录
        current_dir = Path(__file__).parent
        print(f" 当前文件目录: {current_dir}")

        # 2. 找到项目根目录 (scr的上一级)
        self.project_root = current_dir.parent
        print(f" 项目根目录: {self.project_root}")

        # 3. 设置数据目录(项目根目录/DATA /RAW)
        self.data_dir = self.project_root / "DATA" / "raw"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        print(f' 数据目录: {self.data_dir}')

        # 4. 用户输入股票代码
        stock_input = input(f" 请输入股票代码 (多个用逗号分隔, 如 AAPL, MSFT, GOOGL): ")
        self.stocks = [s.strip().upper() for s in stock_input.split(',')]
        print(f" 股票列表: {self.stocks}")

        # 5. 用户输入开始日期
        self.start_date = input(f" 请输入开始日期 (如: YYYY-MM-DD): ")

        # 6. 结束日期自动用当天
        self.end_date = datetime.now().strftime("%Y-%m-%d")

        print(f" 开始日期: {self.start_date}")
        print(f" 结束日期: {self.end_date} (今天)")

        print(f'\n' + '=' * 80)
        print(f' 初始化完成')
        print(f"-" * 70)

    def get_stock_data(self):
        """获取多只股票"""
        print(f"\n 开始获取数据")

        all_data = {}
        success = 0
        failed = 0

        for symbol in self.stocks:
            print(f' \n {symbol}')
            try:
                df = yf.download(symbol, start=self.start_date, end=self.end_date, progress=False)
                if df.empty:
                    print(f" 无数据")
                    failed += 1
                    continue

                # 重置索引, 把日期变成一列
                df = df.reset_index()

                # 处理 MultiIndex 列名
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)


                all_data[symbol] = df
                print(f" {df.shape[0]} 行")

                # 显示打印前10行数据
                print(f' \n {symbol}前10行数据')
                print(df.head(10).to_string())

                success += 1
            except Exception as e:
                print(f" 获取失败{e}")
                failed += 1

        print(f" \n 完成: 成功{success}, 失败{failed}")
        self.all_data = all_data
        return all_data

    def save_to_excel(self):
        """保存所有数据到Excel"""
        print(f'\n' + '=' * 80)
        print(f" 保存所有数据到Excel")
        print(f'=' * 80)

        if not self.all_data:
            print(f' 没有数据可保存............')
            return None

        saved_files = []

        for symbol, df in self.all_data.items():
            filename = f"{symbol}.xlsx"
            filepath = self.data_dir / filename
            df.to_excel(filepath, index=False)
            print(f" {symbol}: 保存成功: ({df.shape[0]} 行)")
            saved_files.append(str(filepath))

        print(f' 共保存: {len(saved_files)} 个文件')
        print(f" 保存目录: {self.data_dir}")

        return saved_files

# 测试
if __name__ == "__main__":
    fetcher = StockDataFetcher()
    data = fetcher.get_stock_data()

    # 保存到Excel 里.
    if data:
        fetcher.save_to_excel()


"""
## 第1课：股票价格数据获取

**任务目标**：
- 使用 yfinance 获取多只股票的 OHLCV 数据（Open、High、Low、Close、Volume）
- 支持用户自定义股票代码和日期范围
- 保存数据为 Excel 文件到指定目录

**实现方案**：
1. **数据源选择**：使用 yfinance 库（免费、无需 API 密钥）
2. **主要功能**：
   - 用户交互式输入股票代码（支持多只股票，逗号分隔）
   - 用户自定义开始日期（结束日期自动设为当天）
   - 自动创建数据目录（DATA/raw/）
   - 重置索引，将日期列作为普通列
   - 处理 MultiIndex 列名问题
   - 保存为 Excel 文件，便于直接查看

3. **技术特点**：
   - 完全免费，无需 API 密钥
   - 支持美股、港股等多市场
   - 自动处理列名格式
   - 显示数据前10行预览

**核心代码结构**：
```python
class StockDataFetcher:
    ├── __init__()               # 初始化目录和用户输入
    ├── get_stock_data()         # 获取多只股票OHLCV数据
    └── save_to_excel()          # 保存数据到Excel文件
```
"""








