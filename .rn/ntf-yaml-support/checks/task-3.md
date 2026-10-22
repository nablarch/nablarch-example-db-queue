# task-3 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| 変換対象の全てのExcelファイルに対応するYAMLファイルが生成されている | OK | 変換対象 Excel は `ProjectCreationServiceActionTest.xlsx` の1件（3シート）。`mvn -B -o com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT:convert`（pom.xml の `<configuration>` を使用）→ `Converted 1 file(s).` / BUILD SUCCESS。警告なし（warnInterleavedBlocks も出ていない）。`ProjectCreationServiceActionTest/` 配下に `setUpDb.yaml`（空シートのため0バイト）・`正常にプロジェクト情報が取り込まれるケース.yaml`・`プロジェクトの取り込みに失敗するケース.yaml` の3ファイルを生成（`evidence/task-3-convert.txt`） | OK | Excel は1件・3シート（workbook.xml と rels で確認）で、同名 YAML 3ファイルが存在。setUpDb は `<sheetData/>` の空シートで0バイト YAML は妥当（`YamlLoader.load` は null を読むと空 Map を返す） |
| サンプリング比較（各ファイル最低3件、元データが3件未満の場合は元データ件数分）でExcelとYAMLの内容が一致している | OK | `scripts/compare_xlsx_yaml.py` で全シート・全ブロック・全セルを比較し `RESULT: ALL MATCH`（`evidence/task-3-compare.txt`）。代表サンプルは下記 Sampling Comparison。比較スクリプトが差異を検出できることを、YAML コピーへの改変（値の変更・ブロック削除）で確認済み（2 NG を検出。`evidence/task-3-compare-negative.txt`） | OK | xlsx の生 XML を独立にダンプ（`<rPh>` 除去）し、正常ケース全19ブロックと失敗ケース全行を YAML と目視照合して全セル一致。Sampling Comparison 表の各行も実ファイルと一致。R92 は `group_id: "4"` として出力。スクリプト再実行でも ALL MATCH |
| 変換後のYAMLファイルがコミットされている | OK | YAML 3ファイルを Task #3 のコミットに含める（Excel は未削除） | OK | 668f93d で YAML 3ファイルを追加。HEAD に YAML と xlsx の両方が存在し、`src` 配下に未コミット差分なし |

Script: `scripts/compare_xlsx_yaml.py`（xlsx の LIST_MAP / SETUP_TABLE / EXPECTED_TABLE ブロックを抽出し、同名 YAML と全セル比較する。ふりがな `<rPh>` を除外、Excel の `null` ⇔ YAML null、YAML は nablarch-testing-yaml（snakeyaml-engine）と同じ YAML 1.2 の真偽値解釈で読む）

Notes:
- 初回比較では testShots の `no` カラムが NG になった。PyYAML（YAML 1.1）が引用符なしのキー `no` を真偽値 False と解釈したためで、スクリプト側の問題。nablarch-testing-yaml の依存は snakeyaml-engine 3.0.1（YAML 1.2）で、`no` は文字列キーとして読まれるため、変換結果には問題がない。スクリプトを YAML 1.2 の真偽値解釈に修正して再比較した。
- compare_xlsx_yaml.py の制約（本データでは影響なしを QA が確認）: (a) YAML 値は `str()` して比較するため引用符の有無は区別しない（nablarch-testing-yaml も toString で値を取るため実質影響なし）、(b) 比較対象は LIST_MAP / SETUP_TABLE / EXPECTED_TABLE のみ（本データの Excel 指示子・YAML トップレベルキーはこの3種のみ）、(c) ヘッダは A 列から隙間なく並ぶ前提、(d) 同名ブロックの重複は警告しない（先頭のみ比較）。
- dump_xlsx.py はふりがな（`<rPh>`）も連結表示するため、目視確認に使う場合は注意（比較には compare_xlsx_yaml.py を使用）。
- Task #1 で修正したテストデータ（R92 `EXPECTED_TABLE[4]=PROJECT`）は、YAML の `expected_tables` に `group_id: "4"` / `table: "PROJECT"`（プロジェクト２の1行）として出力されている（Task #1 QA の提案事項を確認）。

## Sampling Comparison

| YAML ファイル | 比較件数 | レコードキー/行 | Excel 値 | YAML 値 | 一致 |
| --- | --- | --- | --- | --- | --- |
| `setUpDb.yaml` | 0（元データ0件。シート・YAML ともに空） | — | — | — | OK |
| `正常にプロジェクト情報が取り込まれるケース.yaml` | 3（全ブロック・全セルはスクリプトで比較済み） | testShots R7 no=4 / expectedTable | `4` | `"4"` | OK |
| 同上 | | SETUP_TABLE[4]=INS_PROJECT_RECEIVE_MESSAGE R76 RECEIVED_MESSAGE_SEQUENCE=0000000003 / PROCESS_ID | `012345678901234567890123456789012345` | `"012345678901234567890123456789012345"` | OK |
| 同上 | | EXPECTED_TABLE[4]=PROJECT R94 PROJECT_NAME / SALES | `プロジェクト２` / `2` | `"プロジェクト２"` / `"2"` | OK |
| 同上（null 表現） | | EXPECTED_TABLE[2]=PROJECT R48 PROJECT_END_DATE | `null` | `null` | OK |
| 同上（空セル） | | SETUP_TABLE[2]=INS_PROJECT_RECEIVE_MESSAGE R34 PROJECT_END_DATE | （空セル） | `""` | OK |
| `プロジェクトの取り込みに失敗するケース.yaml` | 3（元データ3件：testShots 1行・SETUP 1行・EXPECTED 1行。PROJECT は空） | testShots R4 no=1 / expectedStatusCode | `20` | `"20"` | OK |
| 同上 | | SETUP_TABLE[1]=INS_PROJECT_RECEIVE_MESSAGE R10 PROJECT_START_DATE / PROJECT_END_DATE | `20160102` / `20160101` | `"20160102"` / `"20160101"` | OK |
| 同上 | | EXPECTED_TABLE[1]=INS_PROJECT_RECEIVE_MESSAGE R21 STATUS | `2` | `"2"` | OK |

## .xls/.xlsx 併存チェック

- 併存の有無: なし（リポジトリ内の Excel は `ProjectCreationServiceActionTest.xlsx` の1件のみ）
- 差分確認結果の保存先: 該当なし
- 未使用側（通常 `.xlsx`）の削除: 該当なし

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | OK | 全シート・全ブロック・全セル比較で最低3件の要件を大きく上回る。QA 独自の改変（空文字→null、カラム順入替、null→"null"、末尾スペース）でもスクリプトが NG を検出。Improvement: 改変テストの手順と出力を evidence に残す（反映済み: `evidence/task-3-compare-negative.txt`） |
| Edge case coverage | OK | null、空シート、`rows: []`、`no` キー、Task #1 で修正した R92 をカバー。Improvement: 空セル→`""` の行を Sampling Comparison に追加、スクリプトの制約を Notes に明記（いずれも反映済み） |

## Expert Reviews (code changes only)

N/A — no code changes in this task.

## Overall Verdict

- Self-check: OK
- QA: OK
- Language expert: N/A
- Software-engineering expert: N/A
- Ready for user review: Yes
