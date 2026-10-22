# task-5 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| `mvn test` が BUILD SUCCESS で終了する（全テストパス、Excel ファイルなし） | OK | Excel 0件（Task #4）の状態で `LANG=ja_JP.UTF-8` により `mvn -B clean generate-resources` → BUILD SUCCESS、`mvn -B test` → Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 / BUILD SUCCESS（`evidence/task-5-generate-resources.txt`、`evidence/task-5-test.txt`） | | |
| テストログで YamlTestDataParser が実際に使われていることが確認できる | OK | テストログに `XmlComponentDefinitionLoader … component name = testDataParser, defined … BasicTestDataParser, override … YamlTestDataParser` と `nablarch.test.core.reader.YamlTestDataParser … YamlTestDataParser does not use TestDataReader; the injected value is ignored.` を確認。さらに、YAML のグループ4 PROJECT 期待値（SALES `"2"`）を一時的に `"999"` に改変して `mvn -o test` を実行すると `no=[4] … table=PROJECT line=1 column=SALES expected:<[999]> but was:<[2]>` で FAILURE となり、YAML のデータが検証に使われていることを確認（`evidence/task-5-test-negative.txt`）。`git restore` で復元後、再実行して BUILD SUCCESS（`evidence/task-5-test-after-restore.txt`） | | |

Notes:
- 改変テストは Task #1 QA の提案（期待値を壊して失敗することの動的確認）への対応。Task #1 で修正した R92（グループ4 の PROJECT 期待値）が、YAML 化後に実際に検証されていることも同時に確認できた。改変は作業ツリー上の一時変更のみで、コミットしていない。
- `YamlTestDataParser does not use TestDataReader; the injected value is ignored.` は INFO ログ。unit-test.xml では `testDataReader` を指定していない（Rules どおり）。

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | | |
| Edge case coverage | | |

## Expert Reviews (code changes only)

### Language Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Best practices | | |
| Codebase style consistency | | |
| GWT test format | | |

### Software-engineering Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Separation of concerns | | |
| System integrity | | |
| Maintainability | | |

## Overall Verdict

- Self-check: OK
- QA:
- Language expert:
- Software-engineering expert:
- Ready for user review:
