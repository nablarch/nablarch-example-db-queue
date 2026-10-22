# task-2 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` が test スコープで追加されている | OK | `<dependencies>` 末尾（`nablarch-testing-junit5` の後）に groupId `com.nablarch.framework` / version `1.0.0-SNAPSHOT` / scope `test` で追加。`dependency:resolve` で `nablarch-testing-yaml:jar:1.0.0-SNAPSHOT:test` を確認 | | |
| `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` がビルドプラグインとして追加されている | OK | `<build><plugins>` 先頭に追加。plugin 直下の `<configuration>` に from=xls / to=yaml / input・output=`${project.basedir}/src/test/java` / overwrite=true（nablarch-example-batch と同じ形）。`<dependencies>` には入れていない。`<executions>` なしのため通常ビルドでは実行されない。pom.xml の CRLF を維持し、差分は追加 19 行のみ | | |
| `YamlTestDataParser` が `testDataParser` が参照される全フェーズで有効な設定ファイルに、testdata.html の設定例どおり追加されている | OK | 応答電文（`response_*` / sendSync）なしの DB キュー監視バッチのため `unit-test.xml` のみに配置（本番用 `src/main/resources` には入れていない）。`test-data.xml` の import・`dbInfo` 定義より後に、`dbInfo` 参照と `interpreters` 内 `<list>` の `dateTimeInterpreter` → `compositeInterpreter` の2つのみを記載。`testDataReader` は指定なし | | |
| `mvn dependency:resolve` が成功し、converter の `convert` ゴールが `mvn help:describe` で解決できる | OK | `mvn -B -o validate` / `dependency:resolve` / `help:describe -Dplugin=com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT` がいずれも BUILD SUCCESS。describe 出力に `nablarch-testing-converter:convert` ゴールあり（`evidence/task-2-validate.txt`、`task-2-dependency-resolve.txt`、`task-2-help-describe.txt`） | | |

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
