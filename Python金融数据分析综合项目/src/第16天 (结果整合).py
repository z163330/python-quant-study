'''
第16天
					结果整合
-整理所有分析结果
-汇总核心结论
-明确策略结论

练习：
-用文字总结每个策略的表现
'''

import pandas as pd
import numpy as np
from pathlib import Path

class ResultIntegrator:
    """结果整合器 - 汇总所有策略分析结果"""
    def __init__(self):
        """初始化结果整合器"""
        print(f'\n' +'=' * 80)
        print(f'方法1: 初始化结果整合器')
        print(f"=" * 80)

        # 1. 获取当前文件目录
        print(f' \n1. 获取当前文件目录')
        current_dir = Path(__file__).parent
        print(f" 当前文件目录: {current_dir}")

        # 2. 找到项目根目录
        print(f" \n2. 找到项目根目录")
        self.project_root = current_dir.parent
        print(f' 项目根目录: {self.project_root}')

        # 3. 设置数据目录: (读取之前所有文件的结果)
        print(f' \n3. 设置数据目录: ')
        self.ma_result_dir = self.project_root / "data" / "策略结果"
        self.momentum_result_dir = self.project_root / "data" / "动量策略结果"
        self.comparison_dir = self.project_root / "data" / "策略对比"
        self.performance_dir = self.project_root / "data" / "绩效指标"
        self.risk_dir = self.project_root / "data" / "风险分析"

        print(f" 均线策略结果目录: {self.ma_result_dir}")
        print(f" 动量策略结果目录: {self.momentum_result_dir}")
        print(f" 策略对比目录: {self.comparison_dir}")
        print(f" 绩效指标目录: {self.performance_dir}")
        print(f" 风险分析目录: {self.risk_dir}")

        # 4. 设置输出目录 (保存最终结果)
        print(f" \n4. 设置输出目录")
        self.output_dir = self.project_root / "data" / "最终报告"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f" 输出目录: {self.output_dir}")

        # 5. 初始化结果存储
        print(f" \n5. 初始化结果存储")
        self.ma_results = None
        self.momentum_results = None
        self.comparison_results = None
        self.performance_results = None
        self.risk_results = None

        print(f"\n" + "=" * 80)
        print(f" 方法1完成: 初始化成功")
        print(f'-' * 80)
        print(f' 输出目录: {self.output_dir}')
        print('=' * 80)

    def load_all_results(self):
        """加载所有策略的分析结果"""
        print(f'\n' + '=' * 80)
        print(f" 方法2: 加载所有结果")
        print('=' * 80)

        # 1. 加载均线策略结果
        print(f" \n1. 加载均线策略结果")
        ma_folders = list(self.ma_result_dir.glob("回测结果_*"))

        if ma_folders:
            latest_ma_folder = max(ma_folders, key=lambda x: x.stat().st_mtime)
            ma_file = latest_ma_folder / "批量回测结果.xlsx"

            if ma_file.exists():
                self.ma_results = pd.read_excel(ma_file)
                self.ma_results.columns = self.ma_results.columns.str.strip()
                print(f" 均线策略: {len(self.ma_results)} 只股票")
            else:
                print(f" 没有找到均线策略批量回测结果")
        else:
            print(f" 没有找到均线策略结果文件夹")

        # 2. 加载动量策略结果
        print(f" \n2. 加载动量策略结果")
        momentum_folders = list(self.momentum_result_dir.glob("动量回测结果_*"))

        if momentum_folders:
            latest_momentum_folder = max(momentum_folders, key=lambda x: x.stat().st_mtime)
            momentum_file = latest_momentum_folder / "批量回测结果.xlsx"

            if momentum_file.exists():
                self.momentum_results = pd.read_excel(momentum_file)
                self.momentum_results.columns = self.momentum_results.columns.str.strip()
                print(f' 动量策略: {len(self.momentum_results)} 只股票')
            else:
                print(f" 没有找到动量策略批量回测结果")
        else:
            print(f' 没有找到动量策略结果文件夹')

        # 3. 加载策略对比结果
        print(f" \n3. 加载策略对比结果")
        comparison_folders = list(self.comparison_dir.glob("策略对比结果_*"))

        if comparison_folders:
            latest_comparison = max(comparison_folders, key=lambda x: x.stat().st_mtime)
            comparison_file = latest_comparison / "策略对比汇总.xlsx"

            if comparison_file.exists():
                self.comparison_results = pd.read_excel(comparison_file)
                print(f" 策略对比结果已加载")
            else:
                print(f" 没有找到策略对比汇总文件")
        else:
            print(f' 没有找到策略对比结果文件夹')

        # 4. 加载绩效指标结果
        print(f' \n4. 加载绩效指标结果')

        # 先检查目录是否存在
        if self.performance_dir.exists():
            # 查找所有子文件夹
            performance_folders = list(self.performance_dir.glob("*"))

            # 过滤出包含 "绩效指标结果" 的文件夹
            performance_folders = [f for f in performance_folders if "绩效指标结果" in f.name]

            if performance_folders:
                # 取最新的
                latest_performance = max(performance_folders, key=lambda x: x.stat().st_mtime)
                print(f" 找到文件夹: {latest_performance.name}")

                # 查找策略绩效对比汇总文件
                performance_file = latest_performance / "策略绩效对比汇总.xlsx"

                if performance_file.exists():
                    self.performance_results = pd.read_excel(performance_file)
                    print(f" 绩效指标结果已加载: {performance_file.name}")
                else:
                    print(f" 没有找到策略绩效对比汇总文件")
                    print(f" 文件夹内容: {list(latest_performance.glob('*'))}")
            else:
                print(f' 没有找到绩效指标结果文件夹')
        else:
            print(f" 绩效指标目录不现在")

        # 5. 加载风险分析结果
        print(f" \n5. 加载风险分析结果")
        risk_folders = list(self.risk_dir.glob("风险分析结果_*"))

        if risk_folders:
            latest_risk = max(risk_folders, key=lambda x: x.stat().st_mtime)
            risk_file = latest_risk / "风险对比结果.xlsx"

            if risk_file.exists():
                self.risk_results = pd.read_excel(risk_file)
                risk_file = latest_risk / "风险对比结果.xlsx"
                print(f" 风险分析结果已加载")
            else:
                print(f" 没有找到风险对比结果文件")
        else:
            print(f" 没有找到风险分析结果文件夹")

        # 6. 显示加载汇总
        print(f" \n" + '-' * 80)
        print(f" 加载汇总")
        print(f" 均线策略: {'✅' if self.ma_results is not None else '❌'}")
        print(f" 动量策略: {'✅' if self.momentum_results is not None else '❌' }")
        print(f" 策略对比: {'✅' if self.comparison_results is not None else '❌'}")
        print(f" 绩效指标: {'✅' if self.performance_results is not None else '❌'}")
        print(f" 风险分析: {'✅' if self.risk_results is not None else '❌'}")

        print(f'\n' + '=' * 80 )
        print(f" 方法2完成: 所有结果加载成功")

        return {
            'ma': self.ma_results,
            'momentum': self.momentum_results,
            'comparison': self.comparison_results,
            'performance': self.performance_results,
            'risk': self.risk_results
        }

    def calculate_summary_stats(self):
        """计算所有策略的汇总统计"""
        print(f'\n' + '=' * 80)
        print(f' 方法3: 计算汇总统计')
        print(f'=' * 80)

        # 1. 检查是否有数据
        print(f' \n1. 检查数据')
        if self.ma_results is None or self.momentum_results is None:
            print(f" 缺少数据: ")
            return None
        print(f' 数据检查通过')

        # 2. 计算均线策略汇总
        print(f' \n2. 计算均线策略汇总')
        ma_summary = {
            '策略名称': "均线策略",
            '股票数量': len(self.ma_results),
            '平均收益': self.ma_results['策略总收益'].mean(),
            '中位数收益': self.ma_results['策略总收益'].median(),
            '最高收益': self.ma_results['策略总收益'].max(),
            '最低收益': self.ma_results['策略总收益'].min(),
            '平均最大回撤': self.ma_results['最大回撤'].mean(),
            '平均夏普比率': self.ma_results['夏普比率'].mean(),
            '平均胜率': self.ma_results['胜率'].mean()
        }
        print(f' 股票数量: {ma_summary["股票数量"]}')
        print(f' 平均收益: {ma_summary["平均收益"]:.2%}')
        print(f' 平均最大回撤: {ma_summary["平均最大回撤"]:.2%}')
        print(f' 平均夏普比率: {ma_summary["平均夏普比率"]:.4f}')

        # 3. 计算动量策略汇总
        print(f' \n3. 计算动量策略汇总')
        momentum_summary = {
            '策略名称': "动量策略",
            '股票数量': len(self.momentum_results),
            '平均收益': self.momentum_results['策略总收益'].mean(),
            '中位数收益': self.momentum_results['策略总收益'].median(),
            '最高收益': self.momentum_results['策略总收益'].max(),
            '最低收益': self.momentum_results['策略总收益'].min(),
            '平均最大回撤': self.momentum_results['最大回撤'].mean(),
            '平均夏普比率': self.momentum_results['夏普比率'].mean(),
            '平均胜率': self.momentum_results['胜率'].mean()
        }
        print(f' 股票数量: {momentum_summary["股票数量"]}')
        print(f' 平均收益: {momentum_summary["平均收益"]:.2%}')
        print(f' 平均最大回撤: {momentum_summary["平均最大回撤"]:.2%}')
        print(f' 平均夏普比率: {momentum_summary["平均夏普比率"]:.4f}')

        # 4. 创建汇总表格
        print(f" \n4. 创建汇总表格")
        summary_df = pd.DataFrame([ma_summary, momentum_summary])

        # 格式化显示
        display_df = summary_df.copy()
        for col in ['平均收益', '中位数收益', '最高收益', '最低收益', '平均最大回撤', '平均胜率']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")

        if "平均夏普比率" in display_df.columns:
            display_df['平均夏普比率'] = display_df['平均夏普比率'].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")

        print(f' \n 策略汇总对比表')
        print('=' * 80)
        print(display_df.to_string(index=False))
        print(f" =" * 80)

        # 5. 保存到对象
        self.ma_summary = ma_summary
        self.momentum_summary = momentum_summary
        self.summary_df = summary_df

        print(f'\n' + '=' * 80)
        print(f" 方法3完成: 汇总统计计算成功")
        return summary_df

    def generate_strategy_summary(self):
        """生成出来文字总结"""
        print('\n' + "=" * 80)
        print(f" 方法4: 生成出来文字总结")
        print(f'\n' + '=' * 80)

        # 1. 检查是否有汇总数据
        if not hasattr(self, 'ma_summary') or not hasattr(self, 'momentum_summary'):
            print(f" 缺少汇总数据")
            return None
        ma = self.ma_summary
        momentum = self.momentum_summary

        print(f'\n' + '=' * 80)
        print(f" 策略总结")
        print('=' * 80)

        # 2. 均线策略总结
        print(f" \n1. 均线策略总结")
        print(f"-" * 50)
        print(f" 策略逻辑: 短期均线上穿长期均线买入, 下穿卖出........")
        print(f" 股票数量: {ma['股票数量']} 只")
        print(f" 平均收益: {ma['平均收益']:.2%}")
        print(f" 平均最大回撤: {ma['平均最大回撤']:.2%}")
        print(f" 平均夏普比率: {ma['平均夏普比率']:.4f}")
        print(f" 平均胜率: {ma['平均胜率']:.2%}")

        # 判断表现
        if ma['平均收益'] >0.30:
            print(f" 收益表现: 优秀 (平均收益 > 30%)")
        elif ma['平均收益'] > 0.15:
            print(f" 收益表现: 良好 (平均收益 > 15%)")
        else:
            print(f" 收益表现: 一般")

        if abs(ma['平均最大回撤']) < 0.15:
            print(f" 风险控制: 优秀 (回撤 < 15%)")
        elif abs(ma['平均最大回撤']) < 0.25:
            print(f" 风险控制: 良好 (回撤 < 25%)")
        else:
            print(f" 风险控制: 一般 (回撤 > 25%)")

        # 3. 动量策略汇总
        print(f" \n2. 动量策略总结")
        print(f"-" * 50)
        print(f" 策略逻辑: 过去N天上涨买入, 下跌卖出........")
        print(f" 股票数量: {momentum['股票数量']} 只")
        print(f" 平均收益: {momentum['平均收益']:.2%}")
        print(f" 平均最大回撤: {momentum['平均最大回撤']:.2%}")
        print(f" 平均夏普比率: {momentum['平均夏普比率']:.4f}")
        print(f" 平均胜率: {momentum['平均胜率']:.2%}")

        # 判断表现
        if momentum['平均收益'] > 0.30:
            print(f" 收益表现: 优秀 (平均收益 > 30%)")
        elif momentum['平均收益'] > 0.15:
            print(f" 收益表现: 良好 (平均收益 > 15%)")
        else:
            print(f" 收益表现: 一般")

        if abs(momentum['平均最大回撤']) < 0.15:
            print(f" 风险控制: 优秀 (回撤 < 15%)")
        elif abs(momentum['平均最大回撤']) < 0.25:
            print(f" 风险控制: 良好 (回撤 < 25%)")
        else:
            print(f" 风险控制: 一般 (回撤 > 25%)")

        # 4. 策略对比结论
        print(f' \n3. 策略对比结论')
        print('-' * 50)

        if ma['平均收益'] > momentum['平均收益']:
            print(f' 收益: 均线策略优于动量策略')
        else:
            print(f" 收益: 动量策略优于均线策略")

        if abs(ma['平均最大回撤']) < abs(momentum['平均最大回撤']):
            print(f' 风险: 均线策略更稳健 (回撤更小)')
        else:
            print(f" 风险: 动量策略更稳健 (回撤更小)")

        print(f" \n" + '=' * 80)
        print(f" 方法4完成: 策略文字总结生成成功")

    def generate_final_report(self):
        """生成最终分析报告"""
        print('\n' + '=' * 80)
        print(f' 方法5: 生成最终报告')
        print(f'=' * 80)

        # 1. 检查是否有数据
        if not hasattr(self, 'ma_summary') or not hasattr(self, 'momentum_summary'):
            print(f" 缺少汇总数据")
            return None
        ma = self.ma_summary
        momentum = self.momentum_summary

        # 2. 生成报告内容
        print(f' \n2. 生成报告内容')
        from datetime import datetime
        now = datetime.now().strftime("%Y%m%d")

        report = []
        report.append('=' * 80)
        report.append("策略分析最终报告")
        report.append('=' * 80)
        report.append('')
        report.append(f"报告生成时间: {now}")
        report.append('')

        # 1. 策略概述
        report.append(" 1. 策略概述")
        report.append("-" * 50)
        report.append("")
        report.append("1. 均线策略: ")
        report.append("  - 买入信号: 短期均线上穿长期均线 (金叉)")
        report.append("  - 卖出信号: 短期均线下穿长期均线 (死叉)")
        report.append("  - 参数: MA5 x MA20")
        report.append("")
        report.append("2. 动量策略")
        report.append("  - 买入信号: 过去N天累计收益率为正 (动量 > 0)")
        report.append("  - 卖出信号: 过去N天累计收益率为负 (动量 < 0)")
        report.append("  - 参数: 20天动量")
        report.append("")

        # 2. 策略表现
        report.append(" 2. 策略表现总结")
        report.append("-" * 50)
        report.append("")
        report.append(" 1. 均线策略: ")
        report.append(f"  - 股票数量: {ma['股票数量']} 只")
        report.append(f"  - 平均收益: {ma['平均收益']:.2%}")
        report.append(f"  - 平均最大回撤: {ma['平均最大回撤']:.2%}")
        report.append(f"  - 平均夏普比率: {ma['平均夏普比率']:.4f}")
        report.append(f"  - 平均胜率: {ma['平均胜率']:.2%}")
        report.append(f"")
        report.append(f" 2. 动量策略")
        report.append(f"  - 股票数量: {momentum['股票数量']} 只")
        report.append(f"  - 平均收益: {momentum['平均收益']:.2%}")
        report.append(f"  - 平均最大回撤: {momentum['平均最大回撤']:.2%}")
        report.append(f"  - 平均夏普比率: {momentum['平均夏普比率']:.4f}")
        report.append(f"  - 平均胜率: {momentum['平均胜率']:.2%}")
        report.append(f"")

        # 3. 策略对比
        report.append("3. 策略对比结论")
        report.append('-' * 50)
        report.append("")

        if ma['平均收益'] > momentum['平均收益']:
            report.append(" 收益: 均线策略优于动量策略")
        else:
            report.append(" 收益: 动量策略优于均线策略")

        if abs(ma['平均最大回撤']) < abs(momentum['平均最大回撤']):
            report.append(" 风险: 均线策略更稳健 (回撤更小) ")
        else:
            report.append(" 风险: 动量策略更稳健 (回撤更小) ")

        if ma['平均夏普比率'] > momentum['平均夏普比率']:
            report.append(" 风险调整收益: 均线策略更优")
        else:
            report.append(" 风险调整收益: 动量策略更优")

        report.append("")

        # 4. 最终结论
        report.append(" 4. 最终结论")
        report.append('-' * 50)
        report.append("")

        # 5. 综合评分
        ma_score = 0
        momentum_score = 0

        if ma['平均收益'] > momentum['平均收益']:
            ma_score += 1
        else:
            momentum_score += 1

        if abs(ma['平均最大回撤']) < abs(momentum['平均最大回撤']):
            ma_score += 1
        else:
            momentum_score += 1

        if ma['平均夏普比率'] > momentum['平均夏普比率']:
            ma_score += 1
        else:
            momentum_score += 1

        if ma_score > momentum_score:
            report.append(" 推荐策略: 均线策略")
            report.append("")
            report.append(" 理由: ")
            report.append("  - 收益表现更好")
            report.append("  - 风险控制更稳健")
            report.append("  - 风险调整后收益更高")
        elif momentum_score > ma_score:
            report.append(" 推荐策略: 动量策略")
            report.append("")
            report.append(" 理由: ")
            report.append("  - 收益表现更好")
            report.append("  - 风险控制更稳健")
            report.append("  - 风险调整后收益更高")
        else:
            report.append(" 两个策略表现相当")
            report.append("")
            report.append(" 建议: ")
            report.append("  - 可以组合使用, 分散风险")

        report.append("")
        report.append("=" * 80)
        report.append("报告结果")
        report.append("=" * 80)
        report.append("")

        # 6. 打印报告
        print(f' \n6. 打印报告')
        print("\n" + "\n".join(report))

        # 7. 保存报告到文件
        print(f' \n7. 保存报告到文件')
        report_path = self.output_dir / f"最终报告_{now}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))

        print(f' 报告已保存: {report_path}')

        # 8 保存到对象
        self.final_report = report

        print(f'\n' + '=' * 70)
        print(f' 方法5完成: 最终报告生成成功')
        return report




# 调用
if __name__ == "__main__":
    integrator = ResultIntegrator()

    # 加载所有结果
    all_data = integrator.load_all_results()

    if all_data['ma'] is not None:
        print(f' \n均线策略股票数: {len(all_data["ma"])}')
    if all_data['momentum'] is not None:
        print(f' \n动量策略股票数: {len(all_data["momentum"])}')

    # 计算汇总统计
    summary = integrator.calculate_summary_stats()
    if summary is not None:
        print(f" \n汇总完成, 共{len(summary)} 个策略")

    # 生成策略文字总结
    integrator.generate_strategy_summary()

    # 生成最终报告
    integrator.generate_final_report()


"""
## 第16天：结果整合

**任务目标**：
- 整理所有分析结果（均线策略、动量策略、策略对比、绩效指标、风险分析）
- 汇总核心结论（收益、风险、风险调整收益对比）
- 明确策略结论（推荐策略及理由）
- 用文字总结每个策略的表现

**实现方案**：
1. **数据加载**：
   - 加载第8天均线策略回测结果（data/策略结果/回测结果_*/批量回测结果.xlsx）
   - 加载第10天动量策略回测结果（data/动量策略结果/动量回测结果_*/批量回测结果.xlsx）
   - 加载第11天策略对比结果（data/策略对比/策略对比结果_*/策略对比汇总.xlsx）
   - 加载第13天绩效指标结果（data/绩效指标/绩效指标结果_*/策略绩效对比汇总.xlsx）
   - 加载第14天风险分析结果（data/风险分析/风险分析结果_*/风险对比结果.xlsx）

2. **汇总统计计算**：
   - **均线策略汇总**：股票数量、平均收益、中位数收益、最高/最低收益、平均最大回撤、平均夏普比率、平均胜率
   - **动量策略汇总**：同上
   - **汇总对比表**：格式化显示两种策略的各项指标对比
   - **表现评级**：根据收益和回撤自动评级（优秀/良好/一般）

3. **策略文字总结**：
   - **均线策略总结**：策略逻辑描述、关键指标、收益表现评级、风险控制评级
   - **动量策略总结**：策略逻辑描述、关键指标、收益表现评级、风险控制评级
   - **策略对比结论**：收益对比、风险对比、风险调整收益对比

4. **最终报告生成**：
   - **策略概述**：两种策略的逻辑和参数说明
   - **策略表现总结**：均线策略和动量策略的完整指标
   - **策略对比结论**：收益、风险、风险调整收益的明确对比
   - **综合评分**：基于收益、回撤、夏普比率三项指标评分
   - **推荐策略**：根据评分结果推荐更优策略及理由
   - **报告输出**：打印到控制台并保存为TXT文件

5. **结果保存系统**：
   - 保存最终报告TXT文件（data/最终报告/最终报告_YYYYMMDD.txt）

**核心代码结构**：
```python
class ResultIntegrator:
    ├── __init__()                       # 初始化目录
    ├── load_all_results()                # 加载所有策略分析结果
    ├── calculate_summary_stats()         # 计算汇总统计
    ├── generate_strategy_summary()       # 生成策略文字总结
    └── generate_final_report()           # 生成最终报告
```
"""