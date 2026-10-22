#!/usr/bin/env python3
"""NTF Excel テストデータ(.xlsx)の指定シートをグリッド表示する検証用スクリプト。

Task #3 のサンプリング比較で、変換前 Excel の生のブロックレイアウト
（SETUP_TABLE / EXPECTED_TABLE などの配置順）を確認し、
nablarch-testing-converter が出力した YAML と突き合わせるために使う。
標準ライブラリのみ（zipfile + xml.etree）で動作し、openpyxl 不要。

使い方: python3 -I dump_xlsx.py <xlsx> [シート名の部分一致]
"""
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def col_to_idx(ref):
    s = "".join(c for c in ref if c.isalpha())
    n = 0
    for ch in s:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def main():
    path = sys.argv[1]
    want = sys.argv[2] if len(sys.argv) > 2 else None
    z = zipfile.ZipFile(path)

    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall(f"{NS}si"):
            shared.append("".join(t.text or "" for t in si.iter(f"{NS}t")))

    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.get("Id"): r.get("Target") for r in rels}
    RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

    for sh in wb.find(f"{NS}sheets"):
        name = sh.get("name")
        if want and want not in name:
            continue
        rid = sh.get(f"{RNS}id")
        target = relmap[rid]
        if not target.startswith("xl/"):
            target = "xl/" + target
        print(f"===== SHEET: {name} =====")
        sdata = ET.fromstring(z.read(target))
        for row in sdata.iter(f"{NS}row"):
            cells = {}
            maxc = -1
            for c in row.findall(f"{NS}c"):
                ref = c.get("r")
                ci = col_to_idx(ref)
                t = c.get("t")
                v = c.find(f"{NS}v")
                val = ""
                if v is not None:
                    if t == "s":
                        val = shared[int(v.text)]
                    else:
                        val = v.text
                else:
                    isv = c.find(f"{NS}is")
                    if isv is not None:
                        val = "".join(x.text or "" for x in isv.iter(f"{NS}t"))
                cells[ci] = val
                maxc = max(maxc, ci)
            rowvals = [cells.get(i, "") for i in range(maxc + 1)]
            if any(x.strip() for x in rowvals):
                rn = row.get("r")
                print(f"R{rn}: " + " | ".join(rowvals))


if __name__ == "__main__":
    main()
