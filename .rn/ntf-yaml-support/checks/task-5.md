# task-5 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| `mvn test` が BUILD SUCCESS で終了する（全テストパス、Excel ファイルなし） | OK | Excel 0件（Task #4）の状態で `LANG=ja_JP.UTF-8` により `mvn -B clean generate-resources` → BUILD SUCCESS、`mvn -B test` → Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 / BUILD SUCCESS（`evidence/task-5-generate-resources.txt`、`evidence/task-5-test.txt`） | OK | HEAD・作業ツリー・target/test-classes に .xls/.xlsx が無い状態で `mvn -B -o test` を再実行し、Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 / BUILD SUCCESS。surefire XML に2テストケースを記録 |
| テストログで YamlTestDataParser が実際に使われていることが確認できる | OK | テストログに `XmlComponentDefinitionLoader … component name = testDataParser, defined … BasicTestDataParser, override … YamlTestDataParser` と `nablarch.test.core.reader.YamlTestDataParser … YamlTestDataParser does not use TestDataReader; the injected value is ignored.` を確認。さらに、YAML のグループ4 PROJECT 期待値（SALES `"2"`）を一時的に `"999"` に改変して `mvn -o test` を実行すると `no=[4] … table=PROJECT line=1 column=SALES expected:<[999]> but was:<[2]>` で FAILURE となり、YAML のデータが検証に使われていることを確認（`evidence/task-5-test-negative.txt`）。`git restore` で復元後、再実行して BUILD SUCCESS（`evidence/task-5-test-after-restore.txt`） | OK | 再実行ログで testDataParser の上書き（BasicTestDataParser → YamlTestDataParser）と YamlTestDataParser の INFO を確認。リポジトリのコピー上で失敗ケース YAML の `list_maps` の expectedStatusCode を "20"→"0" に改変すると `expected status code is [0].but was [20]` で FAILURE となることを独立に確認。改変はコミットに残っていない（`git diff HEAD` 空） |

Notes:
- 改変テストは Task #1 QA の提案（期待値を壊して失敗することの動的確認）への対応。Task #1 で修正した R92（グループ4 の PROJECT 期待値）が、YAML 化後に実際に検証されていることも同時に確認できた。改変は作業ツリー上の一時変更のみで、コミットしていない。
- `YamlTestDataParser does not use TestDataReader; the injected value is ignored.` は INFO ログ。unit-test.xml では `testDataReader` を指定していない（Rules どおり）。

- 参考（範囲外。language expert の指摘）: 正常系 testShots の no.2（説明「プロジェクト開始日がnull」）は group 2 で `PROJECT_END_DATE` が空/null、no.3（説明「終了日がnull」）は `PROJECT_START_DATE` が null で、説明文とデータが逆になっている。元の Excel 由来で変換の問題ではない。Rules によりテストデータは変更しない（必要なら別課題）。

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | OK | BUILD SUCCESS とパーサ上書きログに加え、期待値を壊すと FAILURE・戻すと SUCCESS となることで YAML が判定に効いていることを実証。QA でも別セクション（list_maps のステータスコード）の改変で再現 |
| Edge case coverage | OK | 正常・異常の両テストがパスし、改変テストで expected_tables（正常系）と list_maps（異常系）の両方の検出を確認。Improvement（範囲外）: setup_tables の改変や YAML 欠落時の挙動は未確認 |

## Expert Reviews (code changes only)

### Language Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Best practices | OK | YAML は `list_maps` / `setup_tables` / `expected_tables` の NTF YAML 形式。値はすべて引用符付き文字列（先頭ゼロ・日付が化けない）、null は引用符なし、空セルは `""`、0件テーブルは `rows: []`。`no:` キーは YAML 1.2（snakeyaml-engine）で文字列。0バイトの setUpDb.yaml は空シートの忠実な出力で、空 Map として扱われる |
| Codebase style consistency | OK | pom / unit-test.xml / YAML の書式は nablarch-example-batch（NAB-682）と同一。YAML はテストクラス同名ディレクトリ・シート名.yaml で配置。YAML は UTF-8（BOM なし）・LF、pom.xml は CRLF、unit-test.xml は LF でベースラインの改行コードを維持 |
| GWT test format | N/A | `git diff 2e0ea2d HEAD` でテストクラス `.java`・src/main の差分は0行 |

### Software-engineering Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Separation of concerns | OK | src 配下の変更は pom.xml・unit-test.xml・YAML 追加・xlsx 削除のみ。作業記録と検証スクリプトは `.rn/ntf-yaml-support/` に集約。Improvement（任意）: develop への PR 時に `.rn/` を含めるかを決める |
| System integrity | OK | Excel 0件・YAML のみで全テストパス、改変テストで YAML の使用を実証。テストクラス・本番成果物に影響なし。過去履歴を維持し、ベースライン・ユーザー修正・各 Task を別コミットに分離。途中でテストが通らないのは 5a5ec02 のみで記録済み。Improvement: 5a5ec02 の件を steering.md にも記載（反映済み） |
| Maintainability | OK | YAML は人・AI が読み書きしやすい引用付き文字列で、`group_id` / `table` でブロックを特定可能。スクリプトは docstring に目的・使い方・前提を記載。Improvement: Excel 削除後のスクリプト再実行手順（履歴から xlsx を取り出す）と PyYAML 依存を steering.md に明記（反映済み）。evidence へのコマンド記載・絶対パスの扱いは任意 |

## Overall Verdict

- Self-check: OK
- QA: OK
- Language expert: OK
- Software-engineering expert: OK
- Ready for user review: Yes
