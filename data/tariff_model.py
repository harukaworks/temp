import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm

# 读取合并后的数据
df = pd.read_csv('../dataset/merge.csv')
df['date'] = pd.to_datetime(df['date'])

def decode_trade_partner(row):
    """根据410和502列确定贸易伙伴"""
    if row['410'] == 0 and row['502'] == 0:
        return 'Argentina'
    elif row['410'] == 1:
        return 'Brazil'
    elif row['502'] == 1:
        return 'USA'
    else:
        return 'Unknown'

def decode_product_type(row):
    """根据12019019和12019020列确定商品类型"""
    if row['12019019'] == 1:
        return 'GM Yellow Soybean'
    elif row['12019020'] == 1:
        return 'Black Soybean'
    elif row['12019019'] == 0 and row['12019020'] == 0:
        return 'Non-GM Yellow Soybean'
    else:
        return 'Unknown'

# 数据预处理
df['trade_partner'] = df.apply(decode_trade_partner, axis=1)
df['product_type'] = df.apply(decode_product_type, axis=1)

# 确定进出口方向（从中国视角）
df['is_import'] = df['12019019'] == 1  # 中国进口GM黄大豆
df['is_export'] = df['12019020'] == 1  # 中国出口黑大豆

# 筛选出中国与美国的进出口数据
df_usa = df[df['trade_partner'] == 'USA'].copy()

# 关税实施时间点
tariff_date = pd.to_datetime('2025-04-09')

# 分离中国从美国进口数据
china_import_usa = df_usa[df_usa['is_import'] == True].sort_values('date')
# 分离中国对美国出口数据
china_export_usa = df_usa[df_usa['is_export'] == True].sort_values('date')

# 划分关税前后阶段
def split_tariff_period(data):
    """将数据分为关税前和关税后两个阶段"""
    pre_tariff = data[data['date'] < tariff_date]
    post_tariff = data[data['date'] >= tariff_date]
    return pre_tariff, post_tariff

# 中国从美国进口关税前后数据
pre_import, post_import = split_tariff_period(china_import_usa)
# 中国对美国出口关税前后数据
pre_export, post_export = split_tariff_period(china_export_usa)

# 定义统计模型分析函数
def tariff_impact_analysis(pre_data, post_data, metric_name, metric_unit):
    """分析关税对某一指标的影响"""
    # 检查数据是否为空
    if pre_data.empty or post_data.empty:
        return {
            "指标": metric_name,
            "单位": metric_unit,
            "关税前平均值": None,
            "关税前标准差": None,
            "关税后平均值": None,
            "关税后标准差": None,
            "变化量": None,
            "变化百分比(%)": None,
            "检验方法": None,
            "p值": None,
            "显著性": "无数据"
        }
    
    # 计算描述性统计
    pre_mean = pre_data[metric_name].mean()
    pre_std = pre_data[metric_name].std()
    post_mean = post_data[metric_name].mean()
    post_std = post_data[metric_name].std()

    # 计算变化量和变化百分比
    change = post_mean - pre_mean
    change_percent = (change / pre_mean) * 100 if pre_mean != 0 else 0

    # 假设检验：t-test（如果数据正态分布）或 Mann-Whitney U 检验（非正态分布）
    try:
        # 首先检查数据是否正态分布（Shapiro-Wilk 检验）
        _, p_norm_pre = stats.shapiro(pre_data[metric_name])
        _, p_norm_post = stats.shapiro(post_data[metric_name])
        
        if p_norm_pre > 0.05 and p_norm_post > 0.05:
            # 正态分布，使用独立样本 t-test
            _, p_value = stats.ttest_ind(pre_data[metric_name], post_data[metric_name])
            test_name = "独立样本 t-test"
        else:
            # 非正态分布，使用 Mann-Whitney U 检验
            _, p_value = stats.mannwhitneyu(pre_data[metric_name], post_data[metric_name])
            test_name = "Mann-Whitney U 检验"
    except:
        # 如果样本量太小（Shapiro-Wilk 检验要求样本量 3-5000），直接使用 Mann-Whitney U 检验
        _, p_value = stats.mannwhitneyu(pre_data[metric_name], post_data[metric_name])
        test_name = "Mann-Whitney U 检验"

    # 判断影响是否显著
    significance = "显著" if p_value < 0.05 else "不显著"

    # 构建结果字典
    result = {
        "指标": metric_name,
        "单位": metric_unit,
        "关税前平均值": pre_mean,
        "关税前标准差": pre_std,
        "关税后平均值": post_mean,
        "关税后标准差": post_std,
        "变化量": change,
        "变化百分比(%)": change_percent,
        "检验方法": test_name,
        "p值": p_value,
        "显著性": significance
    }

    return result

# 定义指标列表
sales_metrics = [
    {"name": "price", "unit": "元/千克"},
    {"name": "amount", "unit": "千克"},
    {"name": "CNY", "unit": "人民币"}
]

# 中国从美国进口的关税影响分析
print("==================== 中国从美国进口关税影响分析 ====================")
import_results = []
for metric in sales_metrics:
    result = tariff_impact_analysis(pre_import, post_import, metric["name"], metric["unit"])
    import_results.append(result)
    print(f"\n--- {metric['name']} ({metric['unit']}) ---")
    for key, value in result.items():
        if key not in ["指标", "单位"]:
            if value is None:
                print(f"{key}: N/A")
            elif isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")

# 中国对美国出口的关税影响分析
print("\n\n==================== 中国对美国出口关税影响分析 ====================")
export_results = []
for metric in sales_metrics:
    result = tariff_impact_analysis(pre_export, post_export, metric["name"], metric["unit"])
    export_results.append(result)
    print(f"\n--- {metric['name']} ({metric['unit']}) ---")
    for key, value in result.items():
        if key not in ["指标", "单位"]:
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")

# 综合评估
print("\n\n==================== 关税影响综合评估 ====================")

# 进口方面
print("\n1. 中国从美国进口影响：")
for result in import_results:
    trend = "上涨" if result["变化量"] > 0 else "下降"
    print(f"   {result['指标']}: 关税后{trend}{abs(result['变化百分比(%)']):.2f}%，影响{result['显著性']}")

# 出口方面
print("\n2. 中国对美国出口影响：")
for result in export_results:
    trend = "上涨" if result["变化量"] > 0 else "下降"
    print(f"   {result['指标']}: 关税后{trend}{abs(result['变化百分比(%)']):.2f}%，影响{result['显著性']}")

# 输出详细结果到文件
import_results_df = pd.DataFrame(import_results)
export_results_df = pd.DataFrame(export_results)

# 保存结果为CSV文件
import_results_df.to_csv('../dataset/china_import_usa_tariff_impact.csv', index=False, encoding='utf-8-sig')
export_results_df.to_csv('../dataset/china_export_usa_tariff_impact.csv', index=False, encoding='utf-8-sig')

print("\n\n分析结果已保存至dataset文件夹：")
print("- china_import_usa_tariff_impact.csv (中国从美国进口关税影响)")
print("- china_export_usa_tariff_impact.csv (中国对美国出口关税影响)")