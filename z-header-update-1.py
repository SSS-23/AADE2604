"""
从 index.html 提取 <header>...</header>，批量替换当前目录及所有子目录中其他 HTML 文件的 header。
"""

import os
import re
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")


def extract_header(html: str) -> str:
    m = re.search(r"(<header\b[^>]*>.*?</header>)", html, re.DOTALL | re.IGNORECASE)
    if not m:
        raise ValueError("index.html 中未找到 <header>...</header>")
    return m.group(1)


def replace_header(html: str, new_header: str) -> tuple[str, bool]:
    result, count = re.subn(
        r"<header\b[^>]*>.*?</header>",
        new_header,
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return result, count > 0


def main():
    with open(SOURCE, encoding="utf-8") as f:
        source_html = f.read()

    new_header = extract_header(source_html)
    print(f"[source] 已提取 header（{len(new_header)} 字符）\n")

    root = os.path.dirname(os.path.abspath(__file__))
    updated, skipped, no_header = [], [], []

    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if not name.lower().endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            if os.path.abspath(path) == os.path.abspath(SOURCE):
                continue

            with open(path, encoding="utf-8", errors="replace") as f:
                original = f.read()

            replaced, changed = replace_header(original, new_header)

            if not changed:
                no_header.append(os.path.relpath(path, root))
                continue

            if replaced == original:
                skipped.append(os.path.relpath(path, root))
                continue

            with open(path, "w", encoding="utf-8") as f:
                f.write(replaced)
            updated.append(os.path.relpath(path, root))

    print(f"已更新 ({len(updated)}):")
    for p in updated:
        print(f"  ✓  {p}")

    if skipped:
        print(f"\n已是最新，跳过 ({len(skipped)}):")
        for p in skipped:
            print(f"  –  {p}")

    if no_header:
        print(f"\n无 <header> 标签，跳过 ({len(no_header)}):")
        for p in no_header:
            print(f"  ○  {p}")

    print(f"\n完成：更新 {len(updated)} 个，跳过 {len(skipped) + len(no_header)} 个。")


if __name__ == "__main__":
    main()
