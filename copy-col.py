import pandas as pd

# 配置信息
file_b = '/home/xiri/Project/zh-cn_support_for_ENDLESS_ATC/translations_v5.8.4-Copy.csv'
file_a = '/home/xiri/Project/zh-cn_support_for_ENDLESS_ATC/translations_v5.8.4.csv'
col_a = 'zh'      # A.csv 中你想要提取的列名
col_b = 'zh'      # B.csv 中你想要覆盖的列名
output = 'B_new.csv'

# 读取 CSV
# 如果你的文件是刚才提到的 GBK 编码，请将 encoding 改为 'gbk'
df_a = pd.read_csv(file_a, encoding='utf-8')
df_b = pd.read_csv(file_b, encoding='utf-8')

# 执行覆盖
# 注意：这要求 A 和 B 的行数及顺序是一一对应的
df_b[col_b] = df_a[col_a]

# 保存结果
df_b.to_csv(output, index=False, encoding='utf-8')
print(f"完成！结果已保存至 {output}")