import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os

# 读取阿根廷出口数据
df = pd.read_csv('../dataset/agen.csv')

# 去除列名中的空格
df.columns = df.columns.str.strip()

# 转换日期列
df['FECHA_'] = pd.to_datetime(df['FECHA_'])

# 设置关税实施时间点（2025年4月9日）
tariff_date = pd.to_datetime('2025-04-09')

# 筛选2025年的数据用于关税影响分析
df_2025 = df[df['FECHA_'].dt.year == 2025].copy()

# 划分关税前后阶段（按月划分）
pre_tariff_months = [1, 2, 3]  # 关税前月份
post_tariff_months = [4, 5, 6, 7, 8, 9, 10]  # 关税后月份

# 筛选关税前和关税后的数据
pre_tariff_data = df_2025[df_2025['FECHA_'].dt.month.isin(pre_tariff_months)].copy()
post_tariff_data = df_2025[df_2025['FECHA_'].dt.month.isin(post_tariff_months)].copy()

# 定义分析函数
def export_impact_analysis(pre_data, post_data):
    """分析关税对阿根廷大豆出口的影响"""
    # 检查数据是否为空
    if pre_data.empty or post_data.empty:
        return None
    
    # 计算关键指标
    # 1. 出口量（千克）
    pre_volume_mean = pre_data['PESO_NETO_KILOS'].mean()
    post_volume_mean = post_data['PESO_NETO_KILOS'].mean()
    volume_change = post_volume_mean - pre_volume_mean
    volume_change_percent = (volume_change / pre_volume_mean) * 100 if pre_volume_mean != 0 else 0
    
    # 2. 出口额（美元）
    pre_value_mean = pre_data['MONTO_FOB_DOLAR'].mean()
    post_value_mean = post_data['MONTO_FOB_DOLAR'].mean()
    value_change = post_value_mean - pre_value_mean
    value_change_percent = (value_change / pre_value_mean) * 100 if pre_value_mean != 0 else 0
    
    # 3. 平均价格（美元/千克）
    pre_price_mean = pre_data['PRECIO_PROMEDIO'].mean()
    post_price_mean = post_data['PRECIO_PROMEDIO'].mean()
    price_change = post_price_mean - pre_price_mean
    price_change_percent = (price_change / pre_price_mean) * 100 if pre_price_mean != 0 else 0
    
    # 4. 统计检验
    # 月度数据用于统计检验
    pre_monthly_volume = pre_data.groupby(pre_data['FECHA_'].dt.month)['PESO_NETO_KILOS'].sum().values
    post_monthly_volume = post_data.groupby(post_data['FECHA_'].dt.month)['PESO_NETO_KILOS'].sum().values
    
    pre_monthly_value = pre_data.groupby(pre_data['FECHA_'].dt.month)['MONTO_FOB_DOLAR'].sum().values
    post_monthly_value = post_data.groupby(post_data['FECHA_'].dt.month)['MONTO_FOB_DOLAR'].sum().values
    
    pre_monthly_price = pre_data.groupby(pre_data['FECHA_'].dt.month)['PRECIO_PROMEDIO'].mean().values
    post_monthly_price = post_data.groupby(post_data['FECHA_'].dt.month)['PRECIO_PROMEDIO'].mean().values
    
    # 执行t检验
    try:
        _, p_value_volume = stats.ttest_ind(pre_monthly_volume, post_monthly_volume, equal_var=False)
        significance_volume = "显著" if p_value_volume < 0.05 else "不显著"
    except:
        p_value_volume = None
        significance_volume = "无法计算"
    
    try:
        _, p_value_value = stats.ttest_ind(pre_monthly_value, post_monthly_value, equal_var=False)
        significance_value = "显著" if p_value_value < 0.05 else "不显著"
    except:
        p_value_value = None
        significance_value = "无法计算"
    
    try:
        _, p_value_price = stats.ttest_ind(pre_monthly_price, post_monthly_price, equal_var=False)
        significance_price = "显著" if p_value_price < 0.05 else "不显著"
    except:
        p_value_price = None
        significance_price = "无法计算"
    
    # 构建结果字典
    results = {
        'volume': {
            'pre_mean': pre_volume_mean,
            'post_mean': post_volume_mean,
            'change': volume_change,
            'change_percent': volume_change_percent,
            'p_value': p_value_volume,
            'significance': significance_volume
        },
        'value': {
            'pre_mean': pre_value_mean,
            'post_mean': post_value_mean,
            'change': value_change,
            'change_percent': value_change_percent,
            'p_value': p_value_value,
            'significance': significance_value
        },
        'price': {
            'pre_mean': pre_price_mean,
            'post_mean': post_price_mean,
            'change': price_change,
            'change_percent': price_change_percent,
            'p_value': p_value_price,
            'significance': significance_price
        }
    }
    
    return results

# 执行分析
analysis_results = export_impact_analysis(pre_tariff_data, post_tariff_data)

# 打印分析结果
print(f"\n\n==================== Argentina Soybean Export Tariff Impact Analysis ====================")

# 1. Export Volume Analysis
print(f"\n1. Export Volume (kg) Analysis:")
print(f"   Pre-tariff Monthly Avg: {analysis_results['volume']['pre_mean']:,.0f} kg")
print(f"   Post-tariff Monthly Avg: {analysis_results['volume']['post_mean']:,.0f} kg")
print(f"   Change: {analysis_results['volume']['change']:,.0f} kg")
print(f"   Change Percentage: {analysis_results['volume']['change_percent']:.2f}%")
print(f"   Test Method: Independent Samples t-test")
print(f"   p-value: {analysis_results['volume']['p_value']:.4f}")
print(f"   Significance: {analysis_results['volume']['significance']}")

# 2. Export Value Analysis
print(f"\n2. Export Value (USD) Analysis:")
print(f"   Pre-tariff Monthly Avg: ${analysis_results['value']['pre_mean']:,.2f}")
print(f"   Post-tariff Monthly Avg: ${analysis_results['value']['post_mean']:,.2f}")
print(f"   Change: ${analysis_results['value']['change']:,.2f}")
print(f"   Change Percentage: {analysis_results['value']['change_percent']:.2f}%")
print(f"   Test Method: Independent Samples t-test")
print(f"   p-value: {analysis_results['value']['p_value']:.4f}")
print(f"   Significance: {analysis_results['value']['significance']}")

# 3. Average Price Analysis
print(f"\n3. Average Price (USD/kg) Analysis:")
print(f"   Pre-tariff Avg Price: ${analysis_results['price']['pre_mean']:.4f}/kg")
print(f"   Post-tariff Avg Price: ${analysis_results['price']['post_mean']:.4f}/kg")
print(f"   Change: ${analysis_results['price']['change']:.4f}/kg")
print(f"   Change Percentage: {analysis_results['price']['change_percent']:.2f}%")
print(f"   Test Method: Independent Samples t-test")
print(f"   p-value: {analysis_results['price']['p_value']:.4f}")
print(f"   Significance: {analysis_results['price']['significance']}")

# 4. Comprehensive Assessment
print(f"\n\n==================== Comprehensive Tariff Impact Assessment ====================")
print("\nArgentina Soybean Export Impact:")

# Export Volume Assessment
volume_trend = "increased" if analysis_results['volume']['change'] > 0 else "decreased"
print(f"   Export Volume: {volume_trend} by {abs(analysis_results['volume']['change_percent']):.2f}% after tariff, impact {analysis_results['volume']['significance']}")

# Export Value Assessment
value_trend = "increased" if analysis_results['value']['change'] > 0 else "decreased"
print(f"   Export Value: {value_trend} by {abs(analysis_results['value']['change_percent']):.2f}% after tariff, impact {analysis_results['value']['significance']}")

# Price Assessment
price_trend = "increased" if analysis_results['price']['change'] > 0 else "decreased"
print(f"   Price: {price_trend} by {abs(analysis_results['price']['change_percent']):.2f}% after tariff, impact {analysis_results['price']['significance']}")

# 5. 月度趋势分析（包括2023-2025年）
print(f"\n\n==================== Monthly Trend Analysis (2023-2025) ====================")
# 按年和月分组进行聚合
monthly_trends_all_years = df.groupby([df['FECHA_'].dt.year, df['FECHA_'].dt.month]).agg({
    'PESO_NETO_KILOS': 'sum',
    'MONTO_FOB_DOLAR': 'sum',
    'PRECIO_PROMEDIO': 'mean'
}).round(2)

# 格式化日期为'YYYY-MM'格式用于显示
monthly_trends_all_years.index = [f"{year}-{month:02d}" for year, month in monthly_trends_all_years.index]
print(monthly_trends_all_years)

# 2025年月度数据用于保存
monthly_trends = df_2025.groupby(df_2025['FECHA_'].dt.month).agg({
    'PESO_NETO_KILOS': 'sum',
    'MONTO_FOB_DOLAR': 'sum',
    'PRECIO_PROMEDIO': 'mean'
}).round(2)

# 保存分析结果到CSV
results_df = pd.DataFrame({
    '指标': ['出口量(千克)', '出口额(美元)', '平均价格(美元/千克)'],
    '关税前平均值': [
        analysis_results['volume']['pre_mean'],
        analysis_results['value']['pre_mean'],
        analysis_results['price']['pre_mean']
    ],
    '关税后平均值': [
        analysis_results['volume']['post_mean'],
        analysis_results['value']['post_mean'],
        analysis_results['price']['post_mean']
    ],
    '变化量': [
        analysis_results['volume']['change'],
        analysis_results['value']['change'],
        analysis_results['price']['change']
    ],
    '变化百分比(%)': [
        analysis_results['volume']['change_percent'],
        analysis_results['value']['change_percent'],
        analysis_results['price']['change_percent']
    ],
    'p值': [
        analysis_results['volume']['p_value'],
        analysis_results['value']['p_value'],
        analysis_results['price']['p_value']
    ],
    '显著性': [
        analysis_results['volume']['significance'],
        analysis_results['value']['significance'],
        analysis_results['price']['significance']
    ]
})

# 保存月度数据
trend_df = pd.DataFrame(monthly_trends).reset_index()
trend_df.columns = ['月份', '出口量(千克)', '出口额(美元)', '平均价格(美元/千克)']

# 创建结果目录（如果不存在）
output_dir = '../dataset/'
os.makedirs(output_dir, exist_ok=True)

# 保存结果
results_df.to_csv(os.path.join(output_dir, 'argentina_export_tariff_impact.csv'), index=False, encoding='utf-8-sig')
trend_df.to_csv(os.path.join(output_dir, 'argentina_monthly_trends.csv'), index=False, encoding='utf-8-sig')

# 生成可视化图表（英文）
# 1. 月度出口量趋势图（2023-2025）
plt.figure(figsize=(14, 7))
x_labels = monthly_trends_all_years.index
plt.plot(x_labels, monthly_trends_all_years['PESO_NETO_KILOS'] / 1000000, marker='o', linewidth=2, color='blue', label='Export Volume (Million kg)')

# 标记关税实施时间点
# 查找2025-04对应的索引位置
tax_year_month = '2025-04'
if tax_year_month in x_labels:
    tariff_index = list(x_labels).index(tax_year_month)
    plt.axvline(x=tariff_index, color='r', linestyle='--', label='Tariff Implementation (Apr 2025)')

plt.title('Argentina Soybean Monthly Export Volume Trend (2023-2025)')
plt.xlabel('Date (Year-Month)')
plt.ylabel('Export Volume (Million kg)')

# 优化x轴标签显示
plt.xticks(rotation=45, ha='right')
# 只显示部分标签以避免拥挤
step = max(1, len(x_labels) // 12)
plt.xticks(x_labels[::step])

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('../charts/argentina_volume_trend.png', dpi=300)

# 2. 月度出口额趋势图（2023-2025）
plt.figure(figsize=(14, 7))
plt.plot(x_labels, monthly_trends_all_years['MONTO_FOB_DOLAR'] / 1000000, marker='s', linewidth=2, color='green', label='Export Value (Million USD)')

# 标记关税实施时间点
if tax_year_month in x_labels:
    plt.axvline(x=tariff_index, color='r', linestyle='--', label='Tariff Implementation (Apr 2025)')

plt.title('Argentina Soybean Monthly Export Value Trend (2023-2025)')
plt.xlabel('Date (Year-Month)')
plt.ylabel('Export Value (Million USD)')

# 优化x轴标签显示
plt.xticks(rotation=45, ha='right')
plt.xticks(x_labels[::step])

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('../charts/argentina_value_trend.png', dpi=300)

# 3. 月度价格趋势图（2023-2025）
plt.figure(figsize=(14, 7))
plt.plot(x_labels, monthly_trends_all_years['PRECIO_PROMEDIO'], marker='^', linewidth=2, color='red', label='Average Price (USD/kg)')

# 标记关税实施时间点
if tax_year_month in x_labels:
    plt.axvline(x=tariff_index, color='r', linestyle='--', label='Tariff Implementation (Apr 2025)')

plt.title('Argentina Soybean Monthly Average Price Trend (2023-2025)')
plt.xlabel('Date (Year-Month)')
plt.ylabel('Average Price (USD/kg)')

# 优化x轴标签显示
plt.xticks(rotation=45, ha='right')
plt.xticks(x_labels[::step])

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('../charts/argentina_price_trend.png', dpi=300)

print(f"\n\nAnalysis results have been saved to the dataset folder:")
print(f"- argentina_export_tariff_impact.csv (Argentina Export Tariff Impact)")
print(f"- argentina_monthly_trends.csv (Monthly Trend Data)")
print(f"\nCharts have been saved to the charts folder:")
print(f"- argentina_volume_trend.png (Monthly Export Volume Trend 2023-2025)")
print(f"- argentina_value_trend.png (Monthly Export Value Trend 2023-2025)")
print(f"- argentina_price_trend.png (Monthly Average Price Trend 2023-2025)")