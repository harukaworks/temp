import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 读取数据
df = pd.read_csv('../dataset/braz.csv')

# 创建日期列
df['date'] = pd.to_datetime(df[['Year', 'Month']].assign(day=1))

# 关税实施时间点（根据之前的分析，关税时间是2025年4月9日）
tariff_date = pd.to_datetime('2025-04-09')

# 筛选2023-2025年的数据
df_2023_2025 = df[(df['Year'] >= 2023) & (df['Year'] <= 2025)].copy()

# 筛选2025年的数据
df_2025 = df[df['Year'] == 2025].copy()

# 划分关税前后阶段（按月划分）
pre_tariff_months = [1, 2, 3]  # 关税前月份
post_tariff_months = [4, 5, 6, 7, 8, 9, 10]  # 关税后月份

# 筛选关税前和关税后的数据
pre_tariff_data = df_2025[df_2025['Month'].isin(pre_tariff_months)].copy()
post_tariff_data = df_2025[df_2025['Month'].isin(post_tariff_months)].copy()

# 定义分析函数
def export_impact_analysis(pre_data, post_data, country_name=None):
    """Analyze the impact of tariffs on Brazil soybean exports"""
    # If country is specified, filter data for that country
    if country_name:
        pre_data = pre_data[pre_data['Country'] == country_name].copy()
        post_data = post_data[post_data['Country'] == country_name].copy()
    
    # Check if data is empty
    if pre_data.empty or post_data.empty:
        return None
    
    # Calculate monthly averages
    pre_mean = pre_data['US$ FOB'].mean()
    post_mean = post_data['US$ FOB'].mean()
    
    # Calculate total export values
    pre_total = pre_data['US$ FOB'].sum()
    post_total = post_data['US$ FOB'].sum()
    
    # Calculate change and percentage change
    change = post_mean - pre_mean
    change_percent = (change / pre_mean) * 100 if pre_mean != 0 else 0
    
    # Monthly data for statistical test
    pre_monthly_data = pre_data.groupby('Month')['US$ FOB'].sum().values
    post_monthly_data = post_data.groupby('Month')['US$ FOB'].sum().values
    
    # Hypothesis test
    try:
        _, p_value = stats.ttest_ind(pre_monthly_data, post_monthly_data, equal_var=False)
        significance = "Significant" if p_value < 0.05 else "Not Significant"
    except:
        p_value = None
        significance = "Cannot Calculate"
    
    return {
        "Country": country_name if country_name else "Global",
        "Pre-Tariff Monthly Avg (USD)": pre_mean,
        "Post-Tariff Monthly Avg (USD)": post_mean,
        "Pre-Tariff Total (USD)": pre_total,
        "Post-Tariff Total (USD)": post_total,
        "Monthly Avg Change (USD)": change,
        "Change Percentage (%)": change_percent,
        "p-value": p_value,
        "Significance": significance
    }

# 获取主要出口目的地（基于2025年数据）
top_countries = df_2025.groupby('Country')['US$ FOB'].sum().sort_values(ascending=False).head(10).index.tolist()

# 1. Global overall analysis
print("==================== Brazil Soybean Export Tariff Impact Analysis ====================")
global_result = export_impact_analysis(pre_tariff_data, post_tariff_data)
print(f"\n1. Global Overall Impact：")
print(f"   Pre-Tariff Monthly Avg: ${global_result['Pre-Tariff Monthly Avg (USD)']:,.2f}")
print(f"   Post-Tariff Monthly Avg: ${global_result['Post-Tariff Monthly Avg (USD)']:,.2f}")
print(f"   Change: ${global_result['Monthly Avg Change (USD)']:,.2f}")
print(f"   Change Percentage: {global_result['Change Percentage (%)']:.2f}%")
print(f"   Significance: {global_result['Significance']}")

# 2. Major countries analysis
print(f"\n2. Major Export Countries/Regions Impact：")
country_results = []
for country in top_countries:
    result = export_impact_analysis(pre_tariff_data, post_tariff_data, country)
    if result:
        country_results.append(result)
        trend = "increased" if result["Monthly Avg Change (USD)"] > 0 else "decreased"
        print(f"   {country}: Post-tariff monthly avg exports {trend} by {abs(result['Change Percentage (%)']):.2f}%, impact is {result['Significance']}")

# 3. Special focus on China market
china_result = export_impact_analysis(pre_tariff_data, post_tariff_data, 'China')
print(f"\n3. China Market Special Analysis：")
print(f"   Pre-Tariff Monthly Avg: ${china_result['Pre-Tariff Monthly Avg (USD)']:,.2f}")
print(f"   Post-Tariff Monthly Avg: ${china_result['Post-Tariff Monthly Avg (USD)']:,.2f}")
print(f"   Change: ${china_result['Monthly Avg Change (USD)']:,.2f}")
print(f"   Change Percentage: {china_result['Change Percentage (%)']:.2f}%")
print(f"   Significance: {china_result['Significance']}")

# 4. Monthly trend analysis
print(f"\n4. 2025 Monthly Export Trends：")
monthly_trends = df_2025.groupby(['Month', 'Country'])['US$ FOB'].sum().unstack().fillna(0)
monthly_trends['Total'] = monthly_trends.sum(axis=1)
print(monthly_trends[['China', 'Total']])

# 5. China's share of Brazil's total exports
print(f"\n5. China's Share of Brazil's Total Soybean Exports：")
china_percentage_pre = pre_tariff_data[pre_tariff_data['Country'] == 'China']['US$ FOB'].sum() / pre_tariff_data['US$ FOB'].sum() * 100
china_percentage_post = post_tariff_data[post_tariff_data['Country'] == 'China']['US$ FOB'].sum() / post_tariff_data['US$ FOB'].sum() * 100
print(f"   Pre-Tariff: {china_percentage_pre:.2f}%")
print(f"   Post-Tariff: {china_percentage_post:.2f}%")
print(f"   Change: {(china_percentage_post - china_percentage_pre):.2f} percentage points")

# 保存结果到CSV
global_df = pd.DataFrame([global_result])
country_df = pd.DataFrame(country_results)

# Create result directory if it doesn't exist
import os
output_dir = '../dataset/'
os.makedirs(output_dir, exist_ok=True)

# Save results
global_df.to_csv(os.path.join(output_dir, 'brazil_global_export_impact.csv'), index=False, encoding='utf-8-sig')
country_df.to_csv(os.path.join(output_dir, 'brazil_country_export_impact.csv'), index=False, encoding='utf-8-sig')

# Generate visualization charts

# 1. Monthly export trend chart (2023-2025)
plt.figure(figsize=(14, 7))
# Prepare data for 2023-2025 monthly trends
df_2023_2025['year_month'] = df_2023_2025['date'].dt.strftime('%Y-%m')
monthly_data_all = df_2023_2025.groupby('year_month')['US$ FOB'].sum().reset_index()
monthly_data_all['date'] = pd.to_datetime(monthly_data_all['year_month'])
monthly_data_all = monthly_data_all.sort_values('date')

# China data for 2023-2025
china_data_all = df_2023_2025[df_2023_2025['Country'] == 'China'].groupby('year_month')['US$ FOB'].sum().reset_index()
china_data_all['date'] = pd.to_datetime(china_data_all['year_month'])
china_data_all = china_data_all.sort_values('date')

# Plot the data
plt.plot(monthly_data_all['date'], monthly_data_all['US$ FOB'], marker='o', linewidth=2, label='Global Export Value')
plt.plot(china_data_all['date'], china_data_all['US$ FOB'], marker='s', linewidth=2, label='Export to China')

# Add tariff implementation line
plt.axvline(x=pd.to_datetime('2025-04-01'), color='r', linestyle='--', label='Tariff Implementation')

# Set x-ticks for better readability
plt.xticks(pd.date_range(start='2023-01-01', end='2025-10-01', freq='3M'), rotation=45)

plt.title('Brazil Soybean Monthly Export Trend (2023-2025)')
plt.xlabel('Date')
plt.ylabel('Export Value (USD)')
plt.legend()
plt.grid(True)
plt.ticklabel_format(style='plain', axis='y')
plt.tight_layout()
plt.savefig('../charts/brazil_export_trend.png', dpi=300)

# 2. China market share trend chart (2023-2025)
plt.figure(figsize=(14, 7))
# Calculate China's share for each month from 2023-2025
monthly_shares = []
monthly_dates = []

for year in range(2023, 2026):
    for month in range(1, 13):
        # Skip future months in 2025 if needed
        if year == 2025 and month > 10:
            break
        
        month_data = df[(df['Year'] == year) & (df['Month'] == month)]
        total_value = month_data['US$ FOB'].sum()
        china_value = month_data[month_data['Country'] == 'China']['US$ FOB'].sum()
        
        if total_value > 0:
            share = (china_value / total_value) * 100
        else:
            share = 0
        
        monthly_shares.append(share)
        monthly_dates.append(f"{year}-{month:02d}")

# Convert to datetime for plotting
monthly_dates_dt = pd.to_datetime(monthly_dates)

# Plot the data
plt.plot(monthly_dates_dt, monthly_shares, marker='o', linewidth=2, color='green')

# Add tariff implementation line
plt.axvline(x=pd.to_datetime('2025-04-01'), color='r', linestyle='--', label='Tariff Implementation')

# Set x-ticks for better readability
plt.xticks(pd.date_range(start='2023-01-01', end='2025-10-01', freq='3M'), rotation=45)

plt.title('China\'s Monthly Share of Brazil\'s Soybean Exports (2023-2025)')
plt.xlabel('Date')
plt.ylabel('Share (%)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('../charts/brazil_china_percentage.png', dpi=300)

print(f"\n\nAnalysis results have been saved：")
print(f"- brazil_global_export_impact.csv (Brazil Global Export Tariff Impact)")
print(f"- brazil_country_export_impact.csv (Major Countries Export Tariff Impact)")
print(f"\nCharts have been saved：")
print(f"- brazil_export_trend.png (Monthly Export Trend 2023-2025)")
print(f"- brazil_china_percentage.png (China Market Share Trend 2023-2025)")