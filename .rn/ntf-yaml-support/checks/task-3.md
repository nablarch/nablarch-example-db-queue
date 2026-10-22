# task-3 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| 変換対象の全てのExcelファイルに対応するYAMLファイルが生成されている | OK | 変換対象 Excel は `ProjectCreationServiceActionTest.xlsx` の1件（3シート）。`mvn -B -o com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT:convert`（pom.xml の `<configuration>` を使用）→ `Converted 1 file(s).` / BUILD SUCCESS。警告なし（warnInterleavedBlocks も出ていない）。`ProjectCreationServiceActionTest/` 配下に `setUpDb.yaml`（空シートのため0バイト）・`正常にプロジェクト情報が取り込まれるケース.yaml`・`プロジェクトの取り込みに失敗するケース.yaml` の3ファイルを生成（`evidence/task-3-convert.txt`） | | |
| サンプリング比較（各ファイル最低3件、元データが3件未満の場合は元データ件数分）でExcelとYAMLの内容が一致している | OK | `scripts/compare_xlsx_yaml.py` で全シート・全ブロック・全セルを比較し `RESULT: ALL MATCH`（`evidence/task-3-compare.txt`）。代表サンプルは下記 Sampling Comparison。比較スクリプトが差異を検出できることを、YAML コピーへの改変（値の変更・ブロック削除）で確認済み（2 NG を検出） | | |
| 変換後のYAMLファイルがコミットされている | OK | YAML 3ファイルを Task #3 のコミットに含める（Excel は未削除） | | |

Script: `scripts/compare_xlsx_yaml.py`（xlsx の LIST_MAP / SETUP_TABLE / EXPECTED_TABLE ブロックを抽出し、同名 YAML と全セル比較する。ふりがな `<rPh>` を除外、Excel の `null` ⇔ YAML null、YAML は nablarch-testing-yaml（snakeyaml-engine）と同じ YAML 1.2 の真偽値解釈で読む）

Notes:
- 初回比較では testShots の `no` カラムが NG になった。PyYAML（YAML 1.1）が引用符なしのキー `no` を真偽値 False と解釈したためで、スクリプト側の問題。nablarch-testing-yaml の依存は snakeyaml-engine 3.0.1（YAML 1.2）で、`no` は文字列キーとして読まれるため、変換結果には問題がない。スクリプトを YAML 1.2 の真偽値解釈に修正して再比較した。
- Task #1 で修正したテストデータ（R92 `EXPECTED_TABLE[4]=PROJECT`）は、YAML の `expected_tables` に `group_id: "4"` / `table: "PROJECT"`（プロジェクト２の1行）として出力されている（Task #1 QA の提案事項を確認）。

## Sampling Comparison

| YAML ファイル | 比較件数 | レコードキー/行 | Excel 値 | YAML 値 | 一致 |
| --- | --- | --- | --- | --- | --- |
| `setUpDb.yaml` | 0（元データ0件。シート・YAML ともに空） | — | — | — | OK |
| `正常にプロジェクト情報が取り込まれるケース.yaml` | 3（全ブロック・全セルはスクリプトで比較済み） | testShots R7 no=4 / expectedTable | `4` | `"4"` | OK |
| 同上 | | SETUP_TABLE[4]=INS_PROJECT_RECEIVE_MESSAGE R76 RECEIVED_MESSAGE_SEQUENCE=0000000003 / PROCESS_ID | `012345678901234567890123456789012345` | `"012345678901234567890123456789012345"` | OK |
| 同上 | | EXPECTED_TABLE[4]=PROJECT R94 PROJECT_NAME / SALES | `プロジェクト２` / `2` | `"プロジェクト２"` / `"2"` | OK |
| 同上（null 表現） | | EXPECTED_TABLE[2]=PROJECT R48 PROJECT_END_DATE | `null` | `null` | OK |
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
| Meaningful tests/verification | | |
| Edge case coverage | | |

## Expert Reviews (code changes only)

N/A — no code changes in this task.

## Overall Verdict

- Self-check: OK
- QA:
- Language expert: N/A
- Software-engineering expert: N/A
- Ready for user review:
