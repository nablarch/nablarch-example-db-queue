# task-3 Completion Check

## 変換結果

- `nablarch-testing-converter:convert`（from=xls / to=yaml / input=output=src/test/java / overwrite=true）を実行。
- `Converted 1 file(s).` / BUILD SUCCESS。
- 生成YAML（Excel 1ブックが各シート単位のYAMLに分割される）:
  - `ProjectCreationServiceActionTest/setUpDb.yaml`（空＝元の @BeforeClass 等の空シート相当）
  - `ProjectCreationServiceActionTest/正常にプロジェクト情報が取り込まれるケース.yaml`
  - `ProjectCreationServiceActionTest/プロジェクトの取り込みに失敗するケース.yaml`

## 変換時の警告（重要）

変換中に converter が以下の WARNING を出力した:

```
nablarch.test.tool.converter.xls.XlsFormatReader warnInterleavedBlocks
警告: [ProjectCreationServiceActionTest] シート "正常にプロジェクト情報が取り込まれるケース" では、
データタイプ "EXPECTED_TABLE"・グループID "3" のデータブロックの間に別のデータブロックが挟まっています。
テスティングフレームワークは Excel 形式では後ろのデータブロックを読まないため、
次のデータブロックを出力しません: [PROJECT]
```

## サンプリング比較（Excel vs YAML）

Excel の生レイアウトを `.rn/ntf-yaml-support/scripts/dump_xlsx.py` で抽出して突き合わせた。

### シート「プロジェクトの取り込みに失敗するケース」→ 一致

| ブロック | Excel | YAML | 判定 |
|---|---|---|---|
| testShots no.1 | expectedStatusCode=20, setUpTable=1, expectedTable=1 | 同左 | OK |
| SETUP_TABLE[1] INS_PROJECT_RECEIVE_MESSAGE | 0000000001/プロジェクト１/dev/開発/20160102/20160101/… STATUS=0 | 同左 | OK |
| EXPECTED_TABLE[1] INS_PROJECT_RECEIVE_MESSAGE | 0000000001/…/2016-01-02/2016-01-01/… STATUS=2 | 同左 | OK |

### シート「正常にプロジェクト情報が取り込まれるケース」→ 1ブロックが欠落（差異）

| ブロック | Excel | YAML | 判定 |
|---|---|---|---|
| SETUP_TABLE[1] INS…（R13） | 0000000001/プロジェクト１/dev/… | 同左 | OK |
| EXPECTED_TABLE[1] INS…（R23） | 0000000001/…/STATUS=1 | 同左 | OK |
| EXPECTED_TABLE[1] PROJECT（R27） | プロジェクト１/dev/… | 同左 | OK |
| EXPECTED_TABLE[3] PROJECT（R66） | プロジェクト２/maintenance/null/2016-01-02 | expected_tables group 3 PROJECT に存在 | OK |
| EXPECTED_TABLE[4] INS…（R87-90） | 4行（プロジェクト１〜４） | expected_tables group 4 INS に4行存在 | OK |
| **EXPECTED_TABLE[3] PROJECT（R92-94）** | **プロジェクト２/development/2016-01-02/2016-01-03/…** | **YAMLに存在しない（converter が省略）** | **差異** |

## 差異の原因（調査結果）

- Excel シート「正常にプロジェクト情報が取り込まれるケース」の最終ブロック（R92）は
  `EXPECTED_TABLE[3]=PROJECT` とラベル付けされているが、データ内容（プロジェクト２/development/
  2016-01-02/2016-01-03、EXPECTED_TABLE[4] INS の2行目と対応）は**グループ4の期待値**に見える。
  → 元 Excel の**グループID の付け間違い**（本来 `[4]` とすべき箇所が `[3]`）と推測される。
- このため group 3 の EXPECTED_TABLE=PROJECT ブロックが、group 4 のブロック（R85-90）を挟んで
  **2箇所（R66 と R92）に分断**されている。
- NTF（`PoiXlsReader`）は Excel をブロック単位で上から読み、同一グループのブロックが別ブロックを
  挟んで分断されている場合、**後方のブロック（R92）を読み込まない**。converter はこの NTF の挙動を
  忠実に再現し、R92 ブロックを YAML に出力しなかった（＝WARNING の内容）。
- 結果として **YAML は「NTF が Excel から実際に読み取る内容」と等価**（挙動保存）。R92 ブロックは
  Excel 実行時にも NTF に読まれていなかったため、テストの検証内容は Excel／YAML で変わらない見込み。
  ただし「Excel ファイル上に存在するデータブロックが YAML に存在しない」という**ファイル内容としての
  差異**であることは事実。

## 判定・対応

- Rules「サンプリング比較で差異が見つかった場合は修正せずユーザーに報告して停止する」に該当したため、一旦停止してユーザーに報告。
- **ユーザー判断: 「挙動等価として続行」**（元Excelは修正しない）。差異ブロック（R92）はNTFがExcel実行時にも読まないブロックであり、変換は挙動保存であるため続行する。
- 続行判断の裏付けとして、YAML状態（testDataParser=YamlTestDataParser に上書き済み、Excelは未削除だがYAMLが優先的に読まれる）で `mvn clean test` を実行:
  - `Tests run: 2, Failures: 0, Errors: 0, Skipped: 0` / `BUILD SUCCESS`
  - ログで `override component ... component name = testDataParser ... override = YamlTestDataParser`（上書き有効）および `YamlTestDataParser does not use TestDataReader`（実使用）を確認。
  - → 欠落ブロックはテスト結果に影響せず、Excel／YAMLで検証内容が等価であることを実機で確認。

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| 変換対象の全Excelに対応するYAMLが生成されている | OK | 1ブック→3 YAML（setUpDb / 正常ケース / 失敗ケース）を生成 | OK | 3ファイルの生成を独立確認 |
| サンプリング比較でExcelとYAMLの内容が一致（差異は報告・停止） | OK（差異1件は報告済み・ユーザー承認で続行） | 失敗ケース全ブロック一致、正常ケースはR92欠落のみ（挙動保存・NTF未読ブロック）。YAMLでテスト全パス実機確認 | OK | 全ブロック突合でR92以外の欠落・不一致なし。空シート・振り仮名・null表現・日付も整合。YAML状態で Tests run:2/0/0・BUILD SUCCESS を再現 |
| 変換後のYAMLがコミットされている | OK | c367605 | OK | コミット確認 |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | OK | 正常4ショット＋異常1ショット、INS/PROJECT両テーブルの期待値を網羅。YAML変換後も検証内容を保持 |
| Edge case coverage | OK | 開始日null/終了日null/開始>終了の異常/未処理のみ登録/PROCESS_ID有無/振り仮名処理など境界が維持。R92欠落はNTFのExcel分断ブロック非読込挙動の忠実な再現で挙動等価を実証 |

## Expert Reviews (code changes only)

N/A — no code changes in this task.

## Overall Verdict

- Self-check: OK（差異1件はユーザー承認済みで続行）
- QA: OK
- Ready for user review: Yes
