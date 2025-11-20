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

# 筛选2025年的数据（因为我们关注的是2025年4月前后）
df_2025 = df[df['Year'] == 2025].copy()

# 划分关税前后阶段（按月划分）
pre_tariff_months = [1, 2, 3]  # 关税前月份
post_tariff_months = [4, 5, 6, 7, 8, 9, 10]  # 关税后月份

# 筛选关税前和关税后的数据
pre_tariff_data = df_2025[df_2025['Month'].isin(pre_tariff_months)].copy()
post_tariff_data = df_2025[df_2025['Month'].isin(post_tariff_months)].copy()

# 定义分析函数
def export_impact_analysis(pre_data, post_data, country_name=None):
    """分析关税对巴西大豆出口的影响"""
    # 如果指定了国家，筛选特定国家的数据
    if country_name:
        pre_data = pre_data[pre_data['Country'] == country_name].copy()
        post_data = post_data[post_data['Country'] == country_name].copy()
    
    # 检查数据是否为空
    if pre_data.empty or post_data.empty:
        return None
    
    # 计算月度平均值
    pre_mean = pre_data['US$ FOB'].mean()
    post_mean = post_data['US$ FOB'].mean()
    
    # 计算总出口额
    pre_total = pre_data['US$ FOB'].sum()
    post_total = post_data['US$ FOB'].sum()
    
    # 计算变化量和变化百分比
    change = post_mean - pre_mean
    change_percent = (change / pre_mean) * 100 if pre_mean != 0 else 0
    
    # 月度数据用于统计检验
    pre_monthly_data = pre_data.groupby('Month')['US$ FOB'].sum().values
    post_monthly_data = post_data.groupby('Month')['US$ FOB'].sum().values
    
    # 假设检验
    try:
        _, p_value = stats.ttest_ind(pre_monthly_data, post_monthly_data, equal_var=False)
        significance = "显著" if p_value < 0.05 else "不显著"
    except:
        p_value = None
        significance = "无法计算"
    
    return {
        "国家": country_name if country_name else "全球",
        "关税前月均出口额(美元)": pre_mean,
        "关税后月均出口额(美元)": post_mean,
        "关税前总出口额(美元)": pre_total,
        "关税后总出口额(美元)": post_total,
        "月均值变化量(美元)": change,
        "变化百分比(%)": change_percent,
        "p值": p_value,
        "显著性": significance
    }

# 获取主要出口目的地（基于2025年数据）
top_countries = df_2025.groupby('Country')['US$ FOB'].sum().sort_values(ascending=False).head(10).index.tolist()

# 1. 全球总体分析
print("==================== 巴西大豆出口关税影响分析 ====================")
global_result = export_impact_analysis(pre_tariff_data, post_tariff_data)
print(f"\n1. 全球总体影响：")
print(f"   关税前月均出口额：${global_result['关税前月均出口额(美元)']:,.2f}")
print(f"   关税后月均出口额：${global_result['关税后月均出口额(美元)']:,.2f}")
print(f"   变化量：${global_result['月均值变化量(美元)']:,.2f}")
print(f"   变化百分比：{global_result['变化百分比(%)']:.2f}%")
print(f"   显著性：{global_result['显著性']}")

# 2. 主要国家分析
print(f"\n2. 主要出口国家/地区影响：")
country_results = []
for country in top_countries:
    result = export_impact_analysis(pre_tariff_data, post_tariff_data, country)
    if result:
        country_results.append(result)
        trend = "增长" if result["月均值变化量(美元)"] > 0 else "下降"
        print(f"   {country}：关税后月均出口额{trend}{abs(result['变化百分比(%)']):.2f}%，影响{result['显著性']}")

# 3. 特别关注中国市场
china_result = export_impact_analysis(pre_tariff_data, post_tariff_data, 'China')
print(f"\n3. 中国市场特别分析：")
print(f"   关税前月均出口额：${china_result['关税前月均出口额(美元)']:,.2f}")
print(f"   关税后月均出口额：${china_result['关税后月均出口额(美元)']:,.2f}")
print(f"   变化量：${china_result['月均值变化量(美元)']:,.2f}")
print(f"   变化百分比：{china_result['变化百分比(%)']:.2f}%")
print(f"   显著性：{china_result['显著性']}")

# 4. 月度趋势分析
print(f"\n4. 2025年月度出口趋势：")
monthly_trends = df_2025.groupby(['Month', 'Country'])['US$ FOB'].sum().unstack().fillna(0)
monthly_trends['Total'] = monthly_trends.sum(axis=1)
print(monthly_trends[['China', 'Total']])

# 5. 中国占巴西出口总额的比例变化
print(f"\n5. 中国占巴西大豆出口总额的比例：")
china_percentage_pre = pre_tariff_data[pre_tariff_data['Country'] == 'China']['US$ FOB'].sum() / pre_tariff_data['US$ FOB'].sum() * 100
china_percentage_post = post_tariff_data[post_tariff_data['Country'] == 'China']['US$ FOB'].sum() / post_tariff_data['US$ FOB'].sum() * 100
print(f"   关税前：{china_percentage_pre:.2f}%")
print(f"   关税后：{china_percentage_post:.2f}%")
print(f"   变化：{(china_percentage_post - china_percentage_pre):.2f}个百分点")

# 保存结果到CSV
global_df = pd.DataFrame([global_result])
country_df = pd.DataFrame(country_results)

# 创建结果目录（如果不存在）
import os
output_dir = '../dataset/'
os.makedirs(output_dir, exist_ok=True)

# 保存结果
global_df.to_csv(os.path.join(output_dir, 'brazil_global_export_impact.csv'), index=False, encoding='utf-8-sig')
country_df.to_csv(os.path.join(output_dir, 'brazil_country_export_impact.csv'), index=False, encoding='utf-8-sig')

# 生成可视化图表
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 1. 月度出口趋势图
plt.figure(figsize=(12, 6))
monthly_data = df_2025.groupby('Month')['US$ FOB'].sum()
plt.plot(monthly_data.index, monthly_data.values, marker='o', linewidth=2, label='全球出口总额')
china_monthly = df_2025[df_2025['Country'] == 'China'].groupby('Month')['US$ FOB'].sum()
plt.plot(china_monthly.index, china_monthly.values, marker='s', linewidth=2, label='对中国出口额')
plt.axvline(x=3.5, color='r', linestyle='--', label='关税实施时间')
plt.title('2025年巴西大豆月度出口趋势')
plt.xlabel('月份')
plt.ylabel('出口额（美元）')
plt.legend()
plt.grid(True)
plt.ticklabel_format(style='plain', axis='y')
plt.tight_layout()
plt.savefig('../charts/brazil_export_trend.png', dpi=300)

# 2. 中国市场占比变化图
plt.figure(figsize=(10, 6))
months = list(range(1, 11))
china_percentages = []
for month in months:
    month_data = df_2025[df_2025['Month'] == month]
    if month_data['US$ FOB'].sum() > 0:
        china_share = month_data[month_data['Country'] == 'China']['US$ FOB'].sum() / month_data['US$ FOB'].sum() * 100
        china_percentages.append(china_share)
    else:
        china_percentages.append(0)
plt.plot(months, china_percentages, marker='o', linewidth=2, color='green')
plt.axvline(x=3.5, color='r', linestyle='--', label='关税实施时间')
plt.title('2025年中国占巴西大豆出口的月度比例')
plt.xlabel('月份')
plt.ylabel('占比（%）')
plt.grid(True)
plt.tight_layout()
plt.savefig('../charts/brazil_china_percentage.png', dpi=300)

print(f"\n\n分析结果已保存：")
print(f"- brazil_global_export_impact.csv (巴西全球出口关税影响)")
print(f"- brazil_country_export_impact.csv (主要国家出口关税影响)")
print(f"\n图表已保存：")
print(f"- brazil_export_trend.png (月度出口趋势图)")
print(f"- brazil_china_percentage.png (中国市场占比变化图)")