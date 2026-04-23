"""
步骤 1：从 1-research/ 中取第一个 HTML 的 <header>，对其中本站 href 补加 ../
步骤 2：把修改后的 header 替换给 1-research/ 和 news-events/ 里所有 HTML 文件
"""

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET_DIRS = ["1-research", "news-events"]


# ── 工具函数 ────────────────────────────────────────────────

def extract_header(html: str) -> str:
    m = re.search(r"(<header\b[^>]*>.*?</header>)", html, re.DOTALL | re.IGNORECASE)
    if not m:
        raise ValueError("未找到 <header>...</header>")
    return m.group(1)


def should_skip(href: str) -> bool:
    """返回 True 表示不需要补 ../（外链、邮箱、锚点、已有前缀）"""
    h = href.strip()
    return (
        h.startswith(("http://", "https://", "mailto:", "#", "javascript:", "../"))
        or h == ""
    )


def add_prefix_to_href(match: re.Match) -> str:
    """re.sub 回调：给单个 href 属性值补加 ../ 前缀"""
    quote = match.group(1)       # " 或 '
    href = match.group(2)
    if should_skip(href):
        return match.group(0)    # 原样保留
    return f'href={quote}../{href}{quote}'


def fix_hrefs(header: str) -> tuple[str, int]:
    """对 header 内所有需要处理的 href 补加 ../，返回 (新 header, 修改数量)"""
    counter = [0]

    def callback(m: re.Match) -> str:
        result = add_prefix_to_href(m)
        if result != m.group(0):
            counter[0] += 1
        return result

    new_header = re.sub(r'href=(["\'])(.*?)\1', callback, header)
    return new_header, counter[0]


def replace_header_in_file(path: str, new_header: str) -> str:
    """把文件中的 <header>...</header> 替换为 new_header，返回状态字符串"""
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    result, n = re.subn(
        r"<header\b[^>]*>.*?</header>",
        new_header,
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if n == 0:
        return "no-header"
    if result == content:
        return "same"

    with open(path, "w", encoding="utf-8") as f:
        f.write(result)
    return "updated"


# ── 主流程 ──────────────────────────────────────────────────

def main():
    # ── 步骤 1：从 1-research/ 取第一个 HTML 提取并修正 header ──
    research_dir = os.path.join(ROOT, "1-research")
    source_file = next(
        (os.path.join(research_dir, f)
         for f in sorted(os.listdir(research_dir))
         if f.lower().endswith(".html")),
        None,
    )
    if source_file is None:
        raise FileNotFoundError("1-research/ 中没有找到 HTML 文件")

    print(f"[source] {os.path.relpath(source_file, ROOT)}")

    with open(source_file, encoding="utf-8", errors="replace") as f:
        raw_header = extract_header(f.read())

    new_header, fix_count = fix_hrefs(raw_header)

    print(f"[fix]    补加 ../ 的 href 数量：{fix_count}")
    if fix_count:
        # 打印被修改的 href，方便核查
        for m in re.finditer(r'href=(["\'])\.\./.*?\1', new_header):
            print(f"         {m.group(0)}")
    print()

    # ── 步骤 2：批量替换 1-research/ 和 news-events/ ──
    stats = {"updated": [], "same": [], "no-header": []}

    for folder in TARGET_DIRS:
        folder_path = os.path.join(ROOT, folder)
        if not os.path.isdir(folder_path):
            print(f"[warn]   目录不存在，跳过：{folder}")
            continue

        for name in sorted(os.listdir(folder_path)):
            if not name.lower().endswith(".html"):
                continue
            path = os.path.join(folder_path, name)
            status = replace_header_in_file(path, new_header)
            stats[status].append(os.path.relpath(path, ROOT))

    print(f"已更新 ({len(stats['updated'])}):")
    for p in stats["updated"]:
        print(f"  ✓  {p}")

    if stats["same"]:
        print(f"\n已是最新，跳过 ({len(stats['same'])}):")
        for p in stats["same"]:
            print(f"  –  {p}")

    if stats["no-header"]:
        print(f"\n无 <header> 标签，跳过 ({len(stats['no-header'])}):")
        for p in stats["no-header"]:
            print(f"  ○  {p}")

    total = sum(len(v) for v in stats.values())
    print(f"\n完成：共扫描 {total} 个文件，更新 {len(stats['updated'])} 个。")


if __name__ == "__main__":
    main()
