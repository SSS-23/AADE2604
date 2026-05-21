import os
import re


def extract_footer(html_content):
    """提取 <footer>...</footer> 内容（含标签本身）"""
    match = re.search(r'<footer[\s\S]*?</footer>', html_content, re.IGNORECASE)
    if match:
        return match.group(0)
    return None


def add_prefix_to_links(footer_html, prefix='../'):
    """
    给 footer 中所有相对链接加上 prefix（../）。
    处理 href="..." 和 src="..." 属性中的相对路径。
    跳过：绝对路径（http/https/mailto/tel）、锚点（#）、已有 ../ 前缀的路径。
    """
    def replace_attr(match):
        attr  = match.group(1)   # href 或 src
        quote = match.group(2)   # " 或 '
        value = match.group(3)   # 路径值

        # 跳过绝对路径、锚点、空值、data URI、已有 ../
        if (not value
                or value.startswith(('#', 'http://', 'https://',
                                     'mailto:', 'tel:', 'data:', '../'))):
            return match.group(0)

        return f'{attr}={quote}{prefix}{value}{quote}'

    # 匹配 href="..." / href='...' / src="..." / src='...'
    pattern = r'(href|src)=(["\'])([^"\']*)\2'
    return re.sub(pattern, replace_attr, footer_html, flags=re.IGNORECASE)


def replace_footer_in_file(filepath, new_footer):
    """用 new_footer 替换指定文件中的 <footer>...</footer>"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if not re.search(r'<footer[\s\S]*?</footer>', content, re.IGNORECASE):
        print(f'  [跳过] 未找到 <footer>：{filepath}')
        return

    updated = re.sub(r'<footer[\s\S]*?</footer>', new_footer,
                     content, flags=re.IGNORECASE)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated)

    print(f'  [完成] 已替换：{filepath}')


def main():
    # ── 配置 ──────────────────────────────────────────────
    root_dir      = '.'          # 项目根目录（脚本与 index.html 同级）
    index_file    = os.path.join(root_dir, 'index.html')
    sub_dirs      = ['1-research', 'news-events']   # 需要处理的子文件夹
    # ──────────────────────────────────────────────────────

    # 1. 读取 index.html 的 footer
    if not os.path.exists(index_file):
        print(f'错误：找不到 {index_file}，请确认脚本与 index.html 在同一目录。')
        return

    with open(index_file, 'r', encoding='utf-8') as f:
        index_content = f.read()

    root_footer = extract_footer(index_content)
    if not root_footer:
        print('错误：index.html 中未找到 <footer>...</footer>。')
        return

    print('已从 index.html 提取 footer。\n')

    # 2. 生成子文件夹专用 footer（链接加 ../）
    sub_footer = add_prefix_to_links(root_footer, prefix='../')

    # 3. 处理根目录下的 HTML 文件（排除 index.html 自身）
    print('=== 根目录 HTML 文件 ===')
    for filename in os.listdir(root_dir):
        if filename.lower().endswith('.html') and filename != 'index.html':
            filepath = os.path.join(root_dir, filename)
            if os.path.isfile(filepath):
                replace_footer_in_file(filepath, root_footer)

    # 4. 处理子文件夹中的 HTML 文件
    for sub in sub_dirs:
        sub_path = os.path.join(root_dir, sub)
        if not os.path.isdir(sub_path):
            print(f'\n[警告] 子文件夹不存在，已跳过：{sub_path}')
            continue

        print(f'\n=== 子文件夹：{sub} ===')
        for filename in os.listdir(sub_path):
            if filename.lower().endswith('.html'):
                filepath = os.path.join(sub_path, filename)
                if os.path.isfile(filepath):
                    replace_footer_in_file(filepath, sub_footer)

    print('\n全部完成！')


if __name__ == '__main__':
    main()