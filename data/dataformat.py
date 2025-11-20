import pandas as pd

df1 = pd.read_csv('../dataset/2024in.csv', encoding='gbk')
df2 = pd.read_csv('../dataset/2025in.csv', encoding='gbk')
df3 = pd.read_csv('../dataset/2024out.csv', encoding='gbk')
df4 = pd.read_csv('../dataset/2025out.csv', encoding='gbk')

df = pd.concat([df1, df2, df3, df4])
del df1, df2, df3, df4

df = df.replace(12011000, pd.NA)
df.drop(df.columns[-1], axis=1, inplace=True)
df.dropna(inplace=True)

df['date'] = pd.to_datetime(df['数据年月'], format='%Y%m')
df = pd.get_dummies(df, columns=['贸易伙伴编码', '商品编码'], drop_first=True, dtype=int, prefix='', prefix_sep='')
df['amount'] = df['第一数量']
df['CNY'] = df['人民币'].str.replace(',', '').astype(int)
df['price'] = (df['CNY'] / df['amount']).round(2)

df.drop(
    columns=['商品名称', '贸易伙伴名称', '第一计量单位', '第二数量', '第二计量单位', '第一数量', '人民币', '数据年月'],
    inplace=True)
df.to_csv('../dataset/merge.csv', index=False, encoding='utf-8')

print(df)
