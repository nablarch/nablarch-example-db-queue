#!/usr/bin/env python3
"""NTF Excel テストデータ(.xlsx)と変換後 YAML の内容を突き合わせる検証用スクリプト。

Task #3 のサンプリング比較のため、Excel の各シートから LIST_MAP / SETUP_TABLE /
EXPECTED_TABLE ブロックを NTF と同じ規則（コメント行 `//` と空行で区切り、
先頭から読んだ最初の同一ブロックのみ有効）で抽出し、同名 YAML
（<テストクラス>/<シート名>.yaml）の値と全セル比較する。
セル値はふりがな（<rPh>）を除いた本文で比較し、Excel の文字列 `null` は
YAML の null と、空セルは YAML の空文字と対応するものとして扱う。
YAML は nablarch-testing-yaml（snakeyaml-engine）と同じ YAML 1.2 の真偽値解釈で読む。
標準ライブラリ + PyYAML で動作し、openpyxl 不要。

使い方: python3 -I compare_xlsx_yaml.py <xlsx> <YAML ディレクトリ>
出力: ブロック毎の比較結果（行数・不一致セル）と、各ファイル先頭3行のサンプル。
終了コード: 全一致なら 0、不一致があれば 1。
"""
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import yaml

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
BLOCK = re.compile(r"^(LIST_MAP|SETUP_TABLE|EXPECTED_TABLE)(?:\[(\w+)\])?=(.+)$")


class Yaml12Loader(yaml.SafeLoader):
    """YAML 1.2 と同様に true/false のみを真偽値とするローダー。

    nablarch-testing-yaml は snakeyaml-engine（YAML 1.2）を使うため、
    PyYAML（YAML 1.1）の既定のまま読むと testShots の `no` キーが False になる。
    """


Yaml12Loader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in v if tag != "tag:yaml.org,2002:bool"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
Yaml12Loader.add_implicit_resolver(
    "tag:yaml.org,2002:bool", re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"), list("tTfF"))


def col_to_idx(ref):
    n = 0
    for ch in "".join(c for c in ref if c.isalpha()):
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def text_of(node):
    """ふりがな（rPh）を除いた本文テキストを返す。"""
    if node.find(f"{NS}r") is not None or node.find(f"{NS}t") is not None:
        parts = [t.text or "" for t in node.findall(f"{NS}t")]
        parts += [t.text or "" for r in node.findall(f"{NS}r") for t in r.findall(f"{NS}t")]
        return "".join(parts)
    return ""


def read_sheets(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared = [text_of(si) for si in root.findall(f"{NS}si")]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.get("Id"): r.get("Target") for r in rels}
    sheets = {}
    for sh in wb.find(f"{NS}sheets"):
        target = relmap[sh.get(f"{RNS}id")]
        target = target.lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        rows = []
        for row in ET.fromstring(z.read(target)).iter(f"{NS}row"):
            cells = {}
            for c in row.findall(f"{NS}c"):
                v = c.find(f"{NS}v")
                if v is not None:
                    val = shared[int(v.text)] if c.get("t") == "s" else v.text
                else:
                    isv = c.find(f"{NS}is")
                    val = text_of(isv) if isv is not None else ""
                cells[col_to_idx(c.get("r"))] = val or ""
            rows.append((int(row.get("r")), cells))
        sheets[sh.get("name")] = rows
    return sheets


def extract_blocks(rows):
    """シートの行からブロックを抽出する。キーは (種別, グループID, 名前)。"""
    blocks = {}
    i = 0
    while i < len(rows):
        rn, cells = rows[i]
        m = BLOCK.match(cells.get(0, "").strip())
        i += 1
        if not m:
            continue
        kind, gid, name = m.group(1), m.group(2) or "", m.group(3).strip()
        # ヘッダ行
        while i < len(rows) and not any(v.strip() for v in rows[i][1].values()):
            i += 1
        hrn, hcells = rows[i]
        header = [hcells[k] for k in sorted(hcells) if hcells[k].strip()]
        prev = hrn
        i += 1
        data = []
        while i < len(rows):
            drn, dcells = rows[i]
            first = dcells.get(0, "")
            if drn != prev + 1 or not any(v.strip() for v in dcells.values()):
                break
            if first.startswith("//"):
                prev = drn
                i += 1
                continue
            data.append((drn, [dcells.get(k, "") for k in range(len(header))]))
            prev = drn
            i += 1
        key = (kind, gid, name)
        if key not in blocks:  # NTF は先頭の同一ブロックのみ読む
            blocks[key] = (rn, header, data)
    return blocks


def yaml_blocks(doc):
    out = {}
    for lm in doc.get("list_maps", []) or []:
        out[("LIST_MAP", "", lm["id"])] = lm.get("rows") or []
    for sect, kind in (("setup_tables", "SETUP_TABLE"), ("expected_tables", "EXPECTED_TABLE")):
        for t in doc.get(sect, []) or []:
            out[(kind, str(t.get("group_id", "")), t["table"])] = t.get("rows") or []
    return out


def norm_excel(v):
    return None if v == "null" else v


def main():
    xlsx, ydir = sys.argv[1], sys.argv[2]
    ng = 0
    for sheet, rows in read_sheets(xlsx).items():
        ypath = os.path.join(ydir, sheet + ".yaml")
        print(f"===== {sheet} -> {ypath}")
        if not os.path.exists(ypath):
            print("  NG: YAML なし"); ng += 1; continue
        doc = yaml.load(open(ypath, encoding="utf-8"), Loader=Yaml12Loader) or {}
        xb, yb = extract_blocks(rows), yaml_blocks(doc)
        if set(xb) != set(yb):
            print(f"  NG: ブロック集合不一致 excel-only={sorted(set(xb)-set(yb))} yaml-only={sorted(set(yb)-set(xb))}")
            ng += 1
        samples = []
        for key in sorted(set(xb) & set(yb)):
            rn, header, data = xb[key]
            yrows = yb[key]
            bad = []
            if len(data) != len(yrows):
                bad.append(f"行数 excel={len(data)} yaml={len(yrows)}")
            for (drn, vals), yr in zip(data, yrows):
                if list(yr.keys()) != header:
                    bad.append(f"R{drn} カラム不一致 {header} vs {list(yr.keys())}")
                    continue
                for col, xv in zip(header, vals):
                    yv = yr[col]
                    yv = yv if yv is None else str(yv)
                    if norm_excel(xv) != yv:
                        bad.append(f"R{drn} {col}: excel={xv!r} yaml={yv!r}")
                samples.append((key, drn, header[0], vals[0], yr[header[0]], vals[-1], yr[header[-1]], header[-1]))
            status = "OK" if not bad else "NG"
            ng += bool(bad)
            print(f"  {status} {key[0]}[{key[1]}]={key[2]} (R{rn}) rows={len(data)}")
            for b in bad:
                print(f"     {b}")
        print("  -- samples --")
        for key, drn, c0, x0, y0, xl, yl, cl in samples:
            print(f"  {key[0]}[{key[1]}]={key[2]} R{drn}: {c0} excel={x0!r} yaml={y0!r} / {cl} excel={xl!r} yaml={yl!r}")
    print("RESULT:", "ALL MATCH" if ng == 0 else f"{ng} NG")
    sys.exit(1 if ng else 0)


if __name__ == "__main__":
    main()
