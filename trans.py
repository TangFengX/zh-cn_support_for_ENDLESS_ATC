import csv
import sys
import argparse
import os
import io

FILE_NAME = 'translations.csv'

def load_csv():
    if not os.path.exists(FILE_NAME):
        print(f"错误: 找不到文件 {FILE_NAME}")
        sys.exit(1)
    
    # 使用 errors='replace' 防止编码报错，重写后会自动修复
    try:
        with open(FILE_NAME, 'r', encoding='utf-8-sig', errors='replace', newline='') as f:
            content = f.read()
            f_sim = io.StringIO(content)
            reader = csv.DictReader(f_sim)
            fieldnames = reader.fieldnames
            rows = list(reader)
            
            if 'zh' not in fieldnames:
                fieldnames.append('zh')
            return fieldnames, rows
    except Exception as e:
        print(f"读取失败: {e}")
        sys.exit(1)

def save_csv(fieldnames, rows):
    with open(FILE_NAME, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def print_rows(rows_to_print, title="查询结果"):
    if not rows_to_print:
        print(f"\n=== {title} (无结果) ===")
        return

    # 1. 预处理数据：将所有内容转换为字符串，处理 None
    data = []
    for line_num, row in rows_to_print:
        data.append({
            "line": str(line_num),
            "key": str(row.get('key', '')),
            "en": str(row.get('en', '')).replace('\r', '').replace('\n', ' '), # 移除换行符防止破坏表格结构
            "nl": str(row.get('nl', '')).replace('\r', '').replace('\n', ' '),
            "zh": str(row.get('zh', '') or '')
        })

    # 2. 动态计算每一列的最大宽度 (在最小宽度和最大限制之间平衡)
    # 设置各列的最小显示宽度
    col_widths = {
        "line": 5,
        "key": 15,
        "en": 20,
        "nl": 15,
        "zh": 10
    }
    
    for item in data:
        col_widths["line"] = max(col_widths["line"], len(item["line"]))
        col_widths["key"] = max(col_widths["key"], len(item["key"]))
        col_widths["en"] = max(col_widths["en"], len(item["en"]))
        col_widths["nl"] = max(col_widths["nl"], len(item["nl"]))
        col_widths["zh"] = max(col_widths["zh"], len(item["zh"]))

    # 限制 key 和 en 不至于过宽占用整个屏幕（可选，比如最大 50）
    col_widths["en"] = min(col_widths["en"], 60)
    col_widths["key"] = min(col_widths["key"], 40)

    # 3. 打印表头
    header = (
        f"{'行号':<{col_widths['line']}} | "
        f"{'Key':<{col_widths['key']}} | "
        f"{'EN (原文)':<{col_widths['en']}} | "
        f"{'NL (参考)':<{col_widths['nl']}} | "
        f"{'ZH (当前)'}"
    )
    print(f"\n=== {title} ===")
    print(header)
    print("-" * (sum(col_widths.values()) + 12))

    # 4. 打印行内容 (对过长的 EN 文本不再强行截断，或者使用更宽松的限制)
    for item in data:
        # 如果 en 超过了限制宽度，这里依然会显示完整，只是会撑开表格
        # 如果你想严格对齐且不截断，可以使用 textwrap 模块，但最简单的方法是直接输出
        print(
            f"{item['line']:<{col_widths['line']}} | "
            f"{item['key']:<{col_widths['key']}} | "
            f"{item['en']:<{col_widths['en']}} | "
            f"{item['nl']:<{col_widths['nl']}} | "
            f"{item['zh']}"
        )
    print("-" * (sum(col_widths.values()) + 12))

# ... 前面部分 load_csv, save_csv, print_rows 保持不变 ...

def main():
    parser = argparse.ArgumentParser(description="Endless ATC 翻译工具 V2.1")
    parser.add_argument('-r', nargs=2, metavar=('START', 'END'), type=int, help='读取指定范围的行')
    parser.add_argument('-u', action='store_true', help='查找并以 n1-n2 格式输出所有未翻译的行范围')
    parser.add_argument('-w', nargs='+', metavar='KEY:VALUE', help='写入翻译')
    
    args = parser.parse_args()
    fieldnames, rows = load_csv()

    # --- 处理 -u 和 -r 的代码保持不变 ---
    if args.u:
        untranslated = []
        ranges = []
        for i, row in enumerate(rows):
            if not row.get('zh') or row.get('zh').strip() == "":
                untranslated.append((i + 1, row))
        
        if not untranslated:
            print("所有内容已完成翻译！")
        else:
            nums = [item[0] for item in untranslated]
            if nums:
                start = nums[0]
                for i in range(1, len(nums)):
                    if nums[i] != nums[i-1] + 1:
                        ranges.append(f"{start}-{nums[i-1]}")
                        start = nums[i]
                ranges.append(f"{start}-{nums[-1]}")
            print(f"未翻译行范围: {', '.join(ranges)}")
            #print_rows(untranslated[:50], "未翻译条目预览 (仅显示前50条)")

    elif args.r:
        start, end = args.r
        to_show = []
        for i in range(max(0, start-1), min(len(rows), end)):
            to_show.append((i + 1, rows[i]))
        print_rows(to_show, f"第 {start} 到 {end} 行内容")

    # --- 重点修改：处理 -w 并在写入后按行号顺序打印变更 ---
    if args.w:
        updated_rows_map = {} # 使用字典记录 {行号: 行数据} 以便排序
        all_keys_with_index = {r['key']: (i + 1, r) for i, r in enumerate(rows)}
        
        for item in args.w:
            if ':' in item:
                k, v = item.split(':', 1)
                if k in all_keys_with_index:
                    line_num, row_ref = all_keys_with_index[k]
                    row_ref['zh'] = v
                    updated_rows_map[line_num] = row_ref
                    # 注意：如果多次写入同一个 key，更新后的内容会保存在这里
                else:
                    print(f"警告: Key '{k}' 不存在")
            else:
                print(f"警告: 格式错误 '{item}'，应为 KEY:VALUE")

        if updated_rows_map:
            # 执行写入保存
            save_csv(fieldnames, rows)
            
            # 按行号排序并打印
            sorted_line_nums = sorted(updated_rows_map.keys())
            rows_to_print = [(ln, updated_rows_map[ln]) for ln in sorted_line_nums]
            
            print_rows(rows_to_print, f"写入成功！以下是本次更新的 {len(updated_rows_map)} 个条目：")
        else:
            print("没有有效的条目被更新。")

if __name__ == "__main__":
    main()

