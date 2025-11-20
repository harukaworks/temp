import pandas as pd
import matplotlib.pyplot as plt


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

df['trade_partner'] = df.apply(decode_trade_partner, axis=1)
df['product_type'] = df.apply(decode_product_type, axis=1)

import_data = df[df['product_type'] == 'GM Yellow Soybean']
export_data = df[df['product_type'].isin(['Non-GM Yellow Soybean', 'Black Soybean'])]

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('China Soybean Import Analysis (GM Yellow Soybean)', fontsize=16, fontweight='bold')

ax1 = axes[0, 0]
for partner in import_data['trade_partner'].unique():
    partner_data = import_data[import_data['trade_partner'] == partner]
    if not partner_data.empty:
        ax1.plot(partner_data['date'], partner_data['price'],
                 marker='o', linewidth=2, label=partner)

ax1.set_title('Import Price Trend by Trade Partner')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price (CNY/kg)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

ax2 = axes[0, 1]
for partner in import_data['trade_partner'].unique():
    partner_data = import_data[import_data['trade_partner'] == partner]
    if not partner_data.empty:
        ax2.plot(partner_data['date'], partner_data['amount'] / 1e6,
                 marker='s', linewidth=2, label=partner)

ax2.set_title('Import Quantity Trend')
ax2.set_xlabel('Date')
ax2.set_ylabel('Quantity (million kg)')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

ax3 = axes[1, 0]
for partner in import_data['trade_partner'].unique():
    partner_data = import_data[import_data['trade_partner'] == partner]
    if not partner_data.empty:
        ax3.plot(partner_data['date'], partner_data['CNY'] / 1e9,
                 marker='^', linewidth=2, label=partner)

ax3.set_title('Import Value Trend')
ax3.set_xlabel('Date')
ax3.set_ylabel('Value (billion CNY)')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='x', rotation=45)

ax4 = axes[1, 1]
import_share = import_data.groupby('trade_partner')['CNY'].sum()
colors = ['#ff9999', '#66b3ff', '#99ff99']
ax4.pie(import_share.values, labels=import_share.index, autopct='%1.1f%%',
        colors=colors, startangle=90)
ax4.set_title('Import Market Share by Value')

plt.tight_layout()
plt.savefig('../charts/soybean_import_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('China Soybean Export Analysis', fontsize=16, fontweight='bold')

ax1 = axes[0, 0]
for product in export_data['product_type'].unique():
    product_data = export_data[export_data['product_type'] == product]
    if not product_data.empty:
        ax1.plot(product_data['date'], product_data['price'],
                 marker='o', linewidth=2, label=product)

ax1.set_title('Export Price Trend')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price (CNY/kg)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

ax2 = axes[0, 1]
for product in export_data['product_type'].unique():
    product_data = export_data[export_data['product_type'] == product]
    if not product_data.empty:
        ax2.plot(product_data['date'], product_data['amount'],
                 marker='s', linewidth=2, label=product)

ax2.set_title('Export Quantity Trend')
ax2.set_xlabel('Date')
ax2.set_ylabel('Quantity (kg)')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

ax3 = axes[1, 0]
for product in export_data['product_type'].unique():
    product_data = export_data[export_data['product_type'] == product]
    if not product_data.empty:
        ax3.plot(product_data['date'], product_data['CNY'],
                 marker='^', linewidth=2, label=product)

ax3.set_title('Export Value Trend')
ax3.set_xlabel('Date')
ax3.set_ylabel('Value (CNY)')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='x', rotation=45)

ax4 = axes[1, 1]
export_share = export_data.groupby('product_type')['CNY'].sum()
colors = ['#ffcc99', '#c2c2f0']
ax4.pie(export_share.values, labels=export_share.index, autopct='%1.1f%%',
        colors=colors, startangle=90)
ax4.set_title('Export Product Share by Value')

plt.tight_layout()
plt.savefig('../charts/soybean_export_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(14, 8))

plt.subplot(2, 1, 1)
for partner in import_data['trade_partner'].unique():
    partner_data = import_data[import_data['trade_partner'] == partner]
    if not partner_data.empty:
        plt.plot(partner_data['date'], partner_data['price'],
                 marker='o', linewidth=2, label=f'Import from {partner}')

plt.title('Soybean Import Price')
plt.xlabel('Date')
plt.ylabel('Price (CNY/kg)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

plt.subplot(2, 1, 2)
for product in export_data['product_type'].unique():
    product_data = export_data[export_data['product_type'] == product]
    if not product_data.empty:
        plt.plot(product_data['date'], product_data['price'],
                 marker='s', linewidth=2, label=f'Export {product}')

plt.title('Soybean Export Price')
plt.xlabel('Date')
plt.ylabel('Price (CNY/kg)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('../charts/soybean_price_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
