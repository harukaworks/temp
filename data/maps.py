from datetime import date

import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('../dataset/merge.csv')
df['date'] = pd.to_datetime(df['date'])

location_names = {
    402: 'Argentina',
    410: 'Brazil',
    502: 'USA'
}

product_names = {
    12019019: 'GM Yellow Soybean',
    12019011: 'Non-GM Yellow Soybean',
    12019020: 'Black Soybean'
}


import_products = [12019019]
export_products = [12019011, 12019020]

import_data = df[df['item'].isin(import_products)]
export_data = df[df['item'].isin(export_products)]

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('China Soybean Import Analysis', fontsize=16, fontweight='bold')

ax1 = axes[0, 0]
for loc in import_data['loc'].unique():
    loc_data = import_data[import_data['loc'] == loc]
    if not loc_data.empty:
        ax1.plot(loc_data['date'], loc_data['price'],
                marker='o', linewidth=2, label=location_names[loc])

ax1.set_title('Import Price Trend')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price (CNY/kg)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

ax2 = axes[0, 1]
for loc in import_data['loc'].unique():
    loc_data = import_data[import_data['loc'] == loc]
    if not loc_data.empty:
        ax2.plot(loc_data['date'], loc_data['amount']/1e6,
                marker='s', linewidth=2, label=location_names[loc])

ax2.set_title('Import Quantity Trend')
ax2.set_xlabel('Date')
ax2.set_ylabel('Quantity (million kg)')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=45)


ax3 = axes[1, 0]
for loc in import_data['loc'].unique():
    loc_data = import_data[import_data['loc'] == loc]
    if not loc_data.empty:
        ax3.plot(loc_data['date'], loc_data['CNY']/1e9,
                marker='^', linewidth=2, label=location_names[loc])

ax3.set_title('Import Value Trend')
ax3.set_xlabel('Date')
ax3.set_ylabel('Value (billion CNY)')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='x', rotation=45)

ax4 = axes[1, 1]
import_share = import_data.groupby('loc')['CNY'].sum()
locations = [location_names[loc] for loc in import_share.index]
colors = ['#ff9999', '#66b3ff', '#99ff99']
ax4.pie(import_share.values, labels=locations, autopct='%1.1f%%',
        colors=colors, startangle=90)
ax4.set_title('Import Market Share by Value')

plt.tight_layout()
plt.savefig('../charts/soybean_import_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('China Soybean Export Analysis to USA', fontsize=16, fontweight='bold')

usa_export = export_data[export_data['loc'] == 502]

ax1 = axes[0, 0]
for item in usa_export['item'].unique():
    item_data = usa_export[usa_export['item'] == item]
    if not item_data.empty:
        ax1.plot(item_data['date'], item_data['price'],
                marker='o', linewidth=2, label=product_names[item])

ax1.set_title('Export Price Trend by Product Type')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price (CNY/kg)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

ax2 = axes[0, 1]
for item in usa_export['item'].unique():
    item_data = usa_export[usa_export['item'] == item]
    if not item_data.empty:
        ax2.plot(item_data['date'], item_data['amount'],
                marker='s', linewidth=2, label=product_names[item])

ax2.set_title('Export Quantity Trend')
ax2.set_xlabel('Date')
ax2.set_ylabel('Quantity (kg)')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

ax3 = axes[1, 0]
for item in usa_export['item'].unique():
    item_data = usa_export[usa_export['item'] == item]
    if not item_data.empty:
        ax3.plot(item_data['date'], item_data['CNY'],
                marker='^', linewidth=2, label=product_names[item])

ax3.set_title('Export Value Trend by Product Type')
ax3.set_xlabel('Date')
ax3.set_ylabel('Value (CNY)')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='x', rotation=45)

ax4 = axes[1, 1]
export_share = usa_export.groupby('item')['CNY'].sum()
products = [product_names[item] for item in export_share.index]
colors = ['#ffcc99', '#c2c2f0']
ax4.pie(export_share.values, labels=products, autopct='%1.1f%%',
        colors=colors, startangle=90)
ax4.set_title('Export Product Share by Value')

plt.tight_layout()
plt.savefig('../charts/soybean_export_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(14, 8))

plt.subplot(2, 1, 1)
for loc in import_data['loc'].unique():
    loc_data = import_data[import_data['loc'] == loc]
    if not loc_data.empty:
        plt.plot(loc_data['date'], loc_data['price'],
                marker='o', linewidth=2, label=f'Import from {location_names[loc]}')

plt.title('Soybean Import Price Comparison by Origin')
plt.xlabel('Date')
plt.ylabel('Price (CNY/kg)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

plt.subplot(2, 1, 2)
for item in usa_export['item'].unique():
    item_data = usa_export[usa_export['item'] == item]
    if not item_data.empty:
        plt.plot(item_data['date'], item_data['price'],
                marker='s', linewidth=2, label=f'Export {product_names[item]}')

plt.title('Soybean Export Price Comparison ')
plt.xlabel('Date')
plt.ylabel('Price (CNY/kg)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('../charts/soybean_price_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
