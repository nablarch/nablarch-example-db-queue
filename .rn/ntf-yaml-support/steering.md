# nablarch-example-db-queue NTF YAML 対応 steering

## Overview
- 目的・背景: NTF（Nablarch Testing Framework）の AI 対応として、AI が読み書きできないバイナリ形式の Excel テストデータを YAML 形式に移行する（背景資料: https://github.com/Fintan-contents/nablarch-system-development-guide/pull/211）。
- Acceptance criteria 要約:
  - 既存 `ntf-yaml-support` ブランチ上で、過去の移行コミットを維持したまま再実施する（ベースラインコミット → task-1〜5 を積み上げる）
  - ベースライン（develop と同一ツリー）で既存の全テストがパスする
  - `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT`（test 依存）と `nablarch-testing-converter:1.0.0-SNAPSHOT`（`<build><plugins>` のビルドプラグイン）を追加する
  - `YamlTestDataParser`（`testDataParser`）を、`testDataParser` が参照される全フェーズで有効になる設定ファイルに追加する（`interpreters` は `dateTimeInterpreter` → `compositeInterpreter` の2つのみ）
  - 全対象 Excel を YAML へ変換し（サンプリング一致確認）、Excel を削除したうえで全テストがパスする
- 対象プロジェクト名: nablarch-example-db-queue
- 変換対象 Excel（1件）: `src/test/java/com/nablarch/example/app/batch/ProjectCreationServiceActionTest.xlsx`
- 指示書: `.rn/ntf-yaml-support/ntf-yaml-support-instructions_db-queue_V1.6.md`（原本: `/home/k10949/instructions/ntf-yaml-support-instructions_db-queue_V1.6.md`）

## Build / Test
- README 確認結果: 動作環境は Java 17 / Maven 3.9.9 以降。H2 を組み込み済み（DB サーバ不要）。
- プロファイル指定は不要。DB セットアップとエンティティクラス生成は `mvn generate-resources`（`mvn package` にも含まれる）で実行される。
- gsp プラグインを Java 17 で動かす JVM オプションは `.mvn/jvm.config`（`--add-opens java.base/java.lang=ALL-UNNAMED`）で指定済み。
- テストは日本語ロケールで実行する（`LANG=ja_JP.UTF-8`。`C.UTF-8` ではメッセージ解決に失敗しテストが落ちる。前回作業の知見）。
- 実行手順:
  1. `LANG=ja_JP.UTF-8 mvn -B clean generate-resources`
  2. `LANG=ja_JP.UTF-8 mvn -B test`

## Scripts
- `scripts/dump_xlsx.py`: NTF Excel テストデータ（.xlsx）の各シートをグリッド表示する検証用スクリプト（標準ライブラリのみ。openpyxl 不要）。Task #1 ではユーザーが修正したテストデータの新旧比較（差分は `evidence/task-1-testdata-fix.diff`）に使い、Task #3 では Excel の生レイアウト確認に使う（ふりがなも連結表示するため、セル値の比較には compare_xlsx_yaml.py を使う）。使い方: `python3 -I dump_xlsx.py <xlsx> [シート名の部分一致]`
- `scripts/compare_xlsx_yaml.py`: Task #3 のサンプリング比較用。xlsx の LIST_MAP / SETUP_TABLE / EXPECTED_TABLE ブロックを NTF と同じ規則で抽出し、同名 YAML と全セル比較する（ふりがな除外、Excel の `null` ⇔ YAML null、YAML は nablarch-testing-yaml（snakeyaml-engine）と同じ YAML 1.2 の真偽値解釈）。使い方: `python3 -I compare_xlsx_yaml.py <xlsx> <YAML ディレクトリ>`。全一致で終了コード 0

## Tasks

### #1: ベースライン化（developと同一状態）し、全PASSを確認する
**Purpose**: 既存の `ntf-yaml-support` ブランチ（コミット履歴を維持）の先端の上に、ワーキングツリー全体を `develop` と同一内容へ揃えるコミットを1つ新規に積み、その状態で全テストがパスすることを確認する。過去の移行コミットがあっても必ず再実施する。
**Prerequisites**: none
**Steps**:
- [x] 既存の `ntf-yaml-support` ブランチへ切り替える（新規作成なし。履歴維持）
- [x] 過去の移行コミット（`4865a20`〜`a0859ef`）を巻き戻さず、先端の上に処理を積む
- [x] `git read-tree -u --reset develop` → `git commit` でベースラインコミット `2e0ea2d` を作成（`HEAD^{tree}` = `develop^{tree}` = `ecdb691e`）
- [x] （ユーザー指示）ベースライン化後、ビルド・テスト前に一旦停止し、ユーザーがテストデータを修正。修正を別コミット `5331421` として積む（シート「正常にプロジェクト情報が取り込まれるケース」R92 `EXPECTED_TABLE[3]=PROJECT` → `EXPECTED_TABLE[4]=PROJECT`。前回 Task #3 で報告した分断ブロックの解消）
- [x] README を確認し、ビルド・テスト手順を把握する
- [x] steering.md と scripts の初版を作成する
- [x] 本指示書を `.rn/ntf-yaml-support/` 配下へコピーし、`cmp` で原本と同一であることを確認する
- [x] `mvn clean generate-resources` でエンティティクラスを生成する（BUILD SUCCESS）
- [x] `mvn test` で全テストがパスすることを確認する（Tests run: 2, Failures: 0, Errors: 0 / BUILD SUCCESS）
- [x] 結果を `checks/task-1.md` に記録する
- [x] 変更ファイルをコミットする
- [x] self-check
- [x] QA expert review (Agent: general-purpose / Opus) — 全項目 OK
- [ ] user review（全 task 完了後にまとめて実施）
**Completion criteria**:
- 既存の `ntf-yaml-support` ブランチ上で作業しており、コミット履歴が維持されている（過去の移行コミットが残っている）
- ブランチの既存先端の上に、ワーキングツリー全体が `develop` と同一内容になる新規コミットが1つ積まれている
- `mvn test` が全テストパスで終了している（BUILD SUCCESS）
- 本指示書のコピーが `.rn/ntf-yaml-support/` 配下に原本と同一内容で配置され、コミットされている

### #2: 設定変更 — pom.xml と unit-test.xml にYAML対応を追加
**Purpose**: `pom.xml` に `nablarch-testing-yaml`（test 依存）と `nablarch-testing-converter`（ビルドプラグイン）を追加し、`YamlTestDataParser` を testdata.html の設定例どおりに配置する。
**Prerequisites**: #1
**Steps**:
- [x] `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT`（test scope）を追加する
- [x] `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` を追加する（plugin 直下の `<configuration>` に from=xls / to=yaml / input / output=`${project.basedir}/src/test/java` / overwrite=true。nablarch-example-batch 準拠）。pom.xml の改行コード（CRLF）は維持する
- [x] 応答電文（`response_*` / sendSync）の有無で判定する → 非該当（`@BatchRequestTest` の DB キュー監視バッチ。`src/test` 配下に `response_` / sendSync なし。テスト用 diConfig `project-creation-service.xml` は `db-queue.xml` のみ import し、実行中にテストデータを読むモックなし）
- [x] `unit-test.xml` に `YamlTestDataParser` を配置する（`test-data.xml` の import・`dbInfo` 定義より後。`interpreters` 内の `<list>` に `dateTimeInterpreter` → `compositeInterpreter` の2つのみ）
- [x] `mvn -o validate` / `mvn -o dependency:resolve` / `mvn -o help:describe -Dplugin=com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT` がいずれも BUILD SUCCESS（`evidence/task-2-*.txt`）
- [x] 変更したファイルをコミットする
- [x] self-check
- [x] QA / language / software-engineering expert review (Agent: general-purpose / Opus) — 全項目 OK（GWT は N/A）。本コミット単独では `mvn test` が通らない点（YAML 未生成）を checks/task-2.md の Notes に記録
- [ ] user review（全 task 完了後にまとめて実施）
**Completion criteria**:
- `pom.xml` に `nablarch-testing-yaml:1.0.0-SNAPSHOT` が test スコープで追加されている
- `pom.xml` の `<build><plugins>` に `nablarch-testing-converter:1.0.0-SNAPSHOT` がビルドプラグインとして追加されている
- `YamlTestDataParser` が `testDataParser` が参照される全フェーズで有効な設定ファイルに、testdata.html の設定例どおり追加されている
- `mvn dependency:resolve` が成功し、converter の `convert` ゴールが `mvn help:describe` で解決できる

### #3: ExcelテストデータをYAMLに変換
**Purpose**: `nablarch-testing-converter` で Excel テストデータを YAML に変換し、サンプリングで内容一致を確認する。
**Prerequisites**: #2
**Steps**:
- [x] 対象 Excel の所在を確認する（`ProjectCreationServiceActionTest.xlsx` の1件）
- [x] 同名 `.xls` / `.xlsx` の併存を確認する（併存なし）
- [x] converter README の手順で全対象 Excel を YAML 変換する（`LANG=ja_JP.UTF-8 mvn -B -o com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT:convert`。pom.xml の `<configuration>` を使用。`Converted 1 file(s).` / BUILD SUCCESS）
- [x] 変換時に warnInterleavedBlocks 警告が出ないこと、ケース4（正常系 testShots No.4）の YAML に `EXPECTED_TABLE` グループ4の PROJECT 期待値ブロックが含まれることを確認する（Task #1 QA の提案。警告なし・出力あり）
- [x] 各 YAML ファイルを Excel と比較する（`scripts/compare_xlsx_yaml.py` で全ブロック・全セル比較 → ALL MATCH。差異検出能力も改変コピーで確認）
- [x] 比較結果を `checks/task-3.md` の Sampling Comparison に記録する
- [x] YAML ファイルをコミットする（Excel はまだ削除しない）
- [x] self-check
- [ ] QA expert review (Agent: general-purpose / Opus)
- [ ] user review（全 task 完了後にまとめて実施）
**Completion criteria**:
- 全対象 Excel に対応する YAML が生成されている
- サンプリング比較で Excel と YAML の内容が一致している
- YAML がコミットされている

### #4: Excelを削除する
**Purpose**: 変換対象だった Excel を削除してコミットする。
**Prerequisites**: #3
**Steps**:
- [ ] 変換対象の Excel を削除する
- [ ] 残存 Excel が0件であることを `checks/task-4.md` に記録する
- [ ] 削除をコミットする
- [ ] self-check / QA expert review
- [ ] user review
**Completion criteria**:
- 変換対象だった全 Excel ファイルが削除されている
- 削除がコミットされている

### #5: YAMLテストデータで全テストをパスさせる
**Purpose**: Excel なしで全テストがパスすることを確認する。
**Prerequisites**: #4
**Steps**:
- [ ] `mvn test` が BUILD SUCCESS になることを確認する
- [ ] テストログで YamlTestDataParser が使われていることを確認する
- [ ] self-check / QA / language / software-engineering expert review
- [ ] user review
**Completion criteria**:
- `mvn test` が BUILD SUCCESS で終了する（全テストパス、Excel ファイルなし）
- テストログで YamlTestDataParser が実際に使われていることが確認できる
