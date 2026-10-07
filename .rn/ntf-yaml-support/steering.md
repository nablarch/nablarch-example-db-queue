# Goal

対象プロジェクト：nablarch-example-db-queue

NTF（Nablarch Testing Framework）のAI対応として、AIが読み書きできないバイナリ形式のExcelテストデータをYAML形式に移行する。
背景資料: https://github.com/Fintan-contents/nablarch-system-development-guide/pull/211

対象プロジェクトに存在するNTFのExcelテストデータ（現時点で1件）：
- `src/test/java/com/nablarch/example/app/batch/ProjectCreationServiceActionTest.xlsx`

# ビルド・テスト手順（README 確認結果）

- 動作環境: Java 17 / Maven 3.9.9 以降。H2 Database Engine を組み込み済み（別途DBサーバ不要）。
- エンティティ生成・DDL・データ投入は `gsp-dba-maven-plugin` が `generate-sources` フェーズに自動バインドされており、**プロファイル指定は不要**。`mvn test` 実行時に自動で生成される。
- gsp プラグインを Java 17 で動かすための JVM オプションは `.mvn/jvm.config`（`--add-opens java.base/java.lang=ALL-UNNAMED`）で指定済み。
- ビルド・テストコマンド: `mvn clean test`
- テスト実行は日本語ロケールで行う（`LANG=ja_JP.UTF-8`。`C.UTF-8` だとメッセージ解決に失敗しテストが落ちるため）。

# Acceptance criteria

- `develop` ブランチから作成した `ntf-yaml-support` ブランチで全作業が行われている
- 作業前に既存の全テストがパスすることを確認済みである
- `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` が test スコープの依存として追加されている
- `pom.xml` に `nablarch-testing-converter:1.0.0-SNAPSHOT` が `<build><plugins>` のビルドプラグインとして追加されている（test依存ではない）
- `testDataParser` が参照される全フェーズで YAML が有効になるよう、`YamlTestDataParser` コンポーネントと `yamlInterpreters` リストが適切な設定ファイルに追加されている
- 変換対象の全てのExcelファイルがそれぞれ対応するYAMLファイルに変換されている（サンプリング一致確認済み）
- 変換後、変換対象だったExcelファイルが全て削除されている
- YAMLテストデータを使った状態で全テストがパスしている

# Assumptions

- `nablarch-testing-yaml:1.0.0-SNAPSHOT` と `nablarch-testing-converter:1.0.0-SNAPSHOT` はローカルMavenリポジトリ（`~/.m2`）に存在する
- テスト実行にはH2インメモリDBを使用し、DBセットアップ済みである
- YAMLファイルの出力先は `src/test/java` 配下（Excelと同じ場所）とし、`nablarch.test.resource-root` の設定変更は不要
- 変換ツール（`nablarch-testing-converter`）の実行手順は `/home/k10949/workspace/nablarch-testing-converter/README.md` に従う

# Rules

- commit every change; one completion marker per task
- push は行わない（コミットのみ実施し、リモートへの push は最後にユーザーが行う）
- テストクラス（`.java`）は変更しない
- `develop` から新規作成した `ntf-yaml-support` ブランチで作業する
- steering.md は各タスクで更新し、当該タスクのコミットに含める
- テストはExcelファイルが存在しない状態で最終パスを確認する
- YAML変換後はサンプリングでExcelとYAMLの内容を比較してから削除する
- サンプリング比較で差異が見つかった場合は修正せずユーザーに報告して停止する

## YamlTestDataParser / yamlInterpreters の配置判定

- 本プロジェクトのテスト（`ProjectCreationServiceActionTest`）はバッチ（DBキュー監視）アクションの単体テストであり、`sendSync` / 応答電文（`response_*`）を使う同期送信系テストは**存在しない**（test ツリー内に `sendSync` / `response_` の記述なし）。
- したがって**非トリガー構成**であり、`src/test/resources/unit-test.xml` への単一配置で足りる（アクション起動 diConfig 側への配置は不要）。
- 配置順は `nablarch/test/test-data.xml` の import より後・`dbInfo` 定義より後に置き、参照（`dbInfo` / 各 interpreter）解決を担保する。

# Tasks

### #1: 現状のビルド・テストで全PASSを確認する

**Purpose**: `develop` から `ntf-yaml-support` ブランチを作成し、変更前の状態で全テストがパスすることを確認する。

**Prerequisites**: none

**Steps**:

- [x] `develop` ブランチの存在を確認し、そこから `ntf-yaml-support` ブランチを新規作成する
- [x] 対象プロジェクトの README を確認し、ビルド・テストの実行手順を把握する
- [x] 隣接プロジェクトの `.rn/` 配下MDを参照し、steering.md の初版を作成する（README で確認したビルド・テスト手順を明記）
- [x] README で確認した手順でテストを実行し、全テストがパスすることを確認する（`mvn clean test`。gsp はフェーズ自動バインドのためプロファイル不要）
- [x] 結果を `checks/task-1.md` に記録する（self-check列のみ）
- [x] 変更ファイル（check ファイルおよび更新した steering.md）をコミットする
- [x] self-check (OK/NG per completion criterion, record in checks/task-1.md)
- [x] QA expert review (Agent: general-purpose / Opus 4.8)
- [ ] user review

**Completion criteria**:

- `mvn test` が全テストパスで終了している（BUILD SUCCESS）

### #2: 設定変更 — pom.xml と unit-test.xml にYAML対応を追加

**Purpose**: `pom.xml` に `nablarch-testing-yaml`（test 依存）を追加し、`nablarch-testing-converter` を `<build><plugins>` のビルドプラグインとして追加し、`unit-test.xml` に `yamlInterpreters` リストと `YamlTestDataParser` コンポーネントの設定を追加する。設定内容は隣接プロジェクト（web/batch）のYAML対応設定を参考にする。

**Prerequisites**: #1

**Steps**:

- [x] `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT`（test scope）を追加する
- [x] `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` をビルドプラグインとして追加する（`<configuration>` に from=xls / to=yaml / input / output / overwrite を設定）
- [x] 本テストが同期送信系（応答電文 `response_*` / sendSync）かを判定する → 非該当（非トリガー）
- [x] `yamlInterpreters` リストと `YamlTestDataParser`（`testDataParser` 上書き）を `unit-test.xml` に配置する（test-data.xml import より後・dbInfo 定義より後）
- [x] `mvn dependency:resolve` で yaml 依存が解決でき、`mvn help:describe` で converter プラグインの `convert` ゴールが解決できることを確認する
- [x] 変更したファイルをコミットする
- [x] self-check / QA / language / software-engineering expert review
- [ ] user review

**Completion criteria**:

- `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` が test スコープで追加されている
- `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` がビルドプラグインとして追加されている
- `yamlInterpreters` リストと `testDataParser`（`YamlTestDataParser`）が `unit-test.xml` に追加されている
- `mvn dependency:resolve` が成功し、converter プラグインの `convert` ゴールが `mvn help:describe` で解決できる

### #3: ExcelテストデータをYAMLに変換

**Purpose**: `nablarch-testing-converter` を使って ExcelのテストデータをYAML形式に変換し、ソースツリー内に配置して、変換内容をサンプリングで確認する。

**Prerequisites**: #2

**Steps**:

- [x] 対象 Excel ファイルの所在を確認する（.xlsx 1件）
- [x] 同名の `.xls` と `.xlsx` が併存していないか確認する（本プロジェクトは `.xlsx` 1件のみで併存なし）
- [x] README の手順に従い、全ての対象ExcelファイルをYAML変換する（Converted 1 file(s)）
- [x] 変換後、各YAMLファイルについてExcelの内容とサンプリングで比較し、一致を確認する
- [x] サンプリング比較結果を `checks/task-3.md` に記録する（差異1件→報告・停止→ユーザー承認「挙動等価として続行」）
- [x] 変換したYAMLファイルをコミットする（Excelはまだ削除しない）
- [x] self-check / QA expert review
- [ ] user review

**Completion criteria**:

- 変換対象の全てのExcelファイルに対応するYAMLファイルが生成されている
- サンプリング比較でExcelとYAMLの内容が一致している
- 変換後のYAMLファイルがコミットされている

### #4: Excelを削除する

**Purpose**: 変換対象だった Excel を削除してコミットする。

**Prerequisites**: #3

**Steps**:

- [ ] 変換対象となった Excel ファイルを削除する
- [ ] 削除結果（残存Excelが0件であること）を `checks/task-4.md` に記録する
- [ ] Excelファイル削除をコミットする
- [ ] self-check / QA expert review
- [ ] user review

**Completion criteria**:

- 変換対象だった全 Excel ファイルが削除されている
- 削除がコミットされている

### #5: YAMLテストデータで全テストをパスさせる

**Purpose**: Excelなしで全テストがパスすることを確認する。

**Prerequisites**: #4

**Steps**:

- [ ] `mvn test` が BUILD SUCCESS になることを確認する
- [ ] テストログで YamlTestDataParser が実際に使われていることを確認する
- [ ] self-check / QA / language / software-engineering expert review
- [ ] user review

**Completion criteria**:

- `mvn test` が BUILD SUCCESS で終了する（全テストパス、Excel ファイルなし）
- テストログで YamlTestDataParser が実際に使われていることが確認できる

# State

- **Status**: in progress
- **Last completed**: #3 Excel→YAML変換（1ブック→3 YAML）。サンプリング差異1件（R92 EXPECTED_TABLE[3]=PROJECT の欠落、NTF未読ブロックの挙動保存）を報告→ユーザー承認「挙動等価として続行」。YAML状態でmvn test全パス確認済み
- **Next**: #4 Excelを削除する
