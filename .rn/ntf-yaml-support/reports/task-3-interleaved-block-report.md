# Task #3 事象報告書：EXPECTED_TABLE 分断ブロックの YAML 未出力について

## 文書情報

| 項目 | 内容 |
|---|---|
| 対象プロジェクト | nablarch-example-db-queue |
| 対象ブランチ | `ntf-yaml-support` |
| 対象テスト | `ProjectCreationServiceActionTest`（バッチ：DBキュー監視アクション） |
| 対象ファイル（変換元） | `src/test/java/com/nablarch/example/app/batch/ProjectCreationServiceActionTest.xlsx`（削除済み） |
| 対象ファイル（変換後） | `.../ProjectCreationServiceActionTest/正常にプロジェクト情報が取り込まれるケース.yaml` |
| 発生タスク | Task #3（Excel→YAML 変換・サンプリング比較） |
| 発生日 | 2026-10-07 |
| 作成日 | 2026-10-08 |
| 変換ツール | `nablarch-testing-converter:1.0.0-SNAPSHOT`（Maven プラグイン、`convert` ゴール） |
| ステータス | ユーザー承認済み（「挙動等価として続行」）。本書は事後の整理資料 |

---

## 1. 事象の概要

`nablarch-testing-converter` で Excel テストデータを YAML へ変換した際、シート「正常にプロジェクト情報が取り込まれるケース」の **`EXPECTED_TABLE[3]=PROJECT`（Excel 92行目）1 ブロックが YAML に出力されなかった**。変換ツールは以下の警告を出力している。

```
nablarch.test.tool.converter.xls.XlsFormatReader warnInterleavedBlocks
警告: [ProjectCreationServiceActionTest] シート "正常にプロジェクト情報が取り込まれるケース" では、
データタイプ "EXPECTED_TABLE"・グループID "3" のデータブロックの間に別のデータブロックが
挟まっています。テスティングフレームワークは Excel 形式では後ろのデータブロックを読まないため、
次のデータブロックを出力しません: [PROJECT]
```

これは変換ツールが **NTF（Nablarch Testing Framework）の Excel 読み取り挙動を忠実に再現した結果**であり、変換バグではない。すなわち、この省略されたブロックは **Excel 実行時にも NTF に読まれていなかった**。したがって Excel 版・YAML 版の双方でテストの検証内容は同一であり、両版とも全テストがパスする（挙動等価）。

ただし「Excel ファイル上に物理的に存在するデータブロックが、YAML には存在しない」という **ファイル内容としての差異**は事実であるため、移行ルール「サンプリング比較で差異→修正せず報告・停止」に従い一旦停止・報告し、ユーザー承認を得て続行した。

---

## 2. 事象の詳細

### 2.1 当該シートのブロック構成（抜粋）

シート「正常にプロジェクト情報が取り込まれるケース」は 4 ショット（testShots no.1〜4）を持ち、各ショットは `setUpTable` / `expectedTable` のグループ番号で準備データ・期待値を参照する。EXPECTED_TABLE 周辺のレイアウトは以下のとおり（行番号は Excel の行）。

```
R21  EXPECTED_TABLE[1]=INS_PROJECT_RECEIVE_MESSAGE
R25  EXPECTED_TABLE[1]=PROJECT
R42  EXPECTED_TABLE[2]=INS_PROJECT_RECEIVE_MESSAGE
R46  EXPECTED_TABLE[2]=PROJECT
R62  EXPECTED_TABLE[3]=INS_PROJECT_RECEIVE_MESSAGE
R66  EXPECTED_TABLE[3]=PROJECT          ← グループ3の PROJECT 期待値（1回目）
R85  EXPECTED_TABLE[4]=INS_PROJECT_RECEIVE_MESSAGE   ← グループ4のブロック（4行）
R92  EXPECTED_TABLE[3]=PROJECT          ← ★問題のブロック（グループ4の後ろに再登場）
```

- グループ 1・2 は `INS...` と `PROJECT` が隣接し正常。
- グループ 3 の `PROJECT` 期待値は **R66** に正しく存在する。
- その後 **グループ 4 のブロック（R85〜R90）** が入り、さらにその後ろの **R92** に再び `EXPECTED_TABLE[3]=PROJECT` が現れる。

### 2.2 問題ブロック（R92）の中身

| 項目 | 値 |
|---|---|
| ラベル | `EXPECTED_TABLE[3]=PROJECT` |
| データ | PROJECT_NAME=プロジェクト２, PROJECT_TYPE=**development**, 開始=2016-01-02, 終了=2016-01-03, CLIENT_ID=2, …, USER_ID=102, NOTE=かきくけこ |

ラベルは `[3]` だが、データ内容（`development` / 2016-01-02〜2016-01-03 / USER_ID=102 / かきくけこ）は、グループ **4** の SETUP/EXPECTED の 2 行目（`0000000002` プロジェクト２ development）に対応する。すなわち **本来はグループ 4 の PROJECT 期待値であるべきものが、グループ番号を `[3]` と誤記されている**と判断できる。

### 2.3 NTF の読み取り挙動

NTF の Excel リーダ（`PoiXlsReader`）は、同一「データタイプ＋グループID」のブロックが、別のブロックを挟んで**分断**されて配置されている場合、後方のブロックを読み込まない。本件では `EXPECTED_TABLE` グループ 3 の `PROJECT` が R66 と R92 に分断され、間にグループ 4 のブロック（R85〜R90）が挟まっている。このため NTF は **R92 を読まず**、グループ 3 の PROJECT 期待値としては R66 のみを採用する。変換ツールはこの挙動を再現し、R92 を YAML に出力しなかった。

---

## 3. 原因

### 3.1 直接原因

Excel シート上で、`EXPECTED_TABLE` グループ 3 の `PROJECT` ブロックが 2 箇所（R66・R92）に分断配置され、間にグループ 4 のブロックが挟まっていた。NTF（および挙動を再現する変換ツール）は分断された後方ブロック（R92）を読み取らないため、当該ブロックが YAML に出力されなかった。

### 3.2 根本原因

元 Excel 作成時の **データブロックのグループ番号の付け間違い（記述ミス）**。本来グループ 4 の PROJECT 期待値（`EXPECTED_TABLE[4]=PROJECT`）とすべきブロックが、

1. グループ番号を `[3]` と誤記され、かつ
2. グループ 4 のブロック群より後ろ（シート末尾）に配置された

ことで、「グループ 3 の分断後方ブロック」という NTF が読み取らない状態になっていた。結果として、

- このブロックは Excel 運用時から一度も検証に使われていなかった（＝元々デッドデータ）。
- 併せて、**グループ 4（ショット no.4「未処理のプロジェクトのみ登録されること」）の PROJECT テーブルに対する期待値検証が、元 Excel の時点から実質的に欠落していた**。

本事象は YAML 変換が作り出した欠陥ではなく、**元 Excel に潜在していた記述ミスが変換を機に可視化されたもの**である。

---

## 4. Excel 版と YAML 版の挙動比較

| 観点 | Excel 版（移行前） | YAML 版（移行後） | 等価性 |
|---|---|---|---|
| R92 ブロックの物理的存在 | 存在する（シート末尾） | 存在しない（未出力） | ファイル内容としては差異あり |
| NTF が R92 を読み取るか | 読み取らない（分断後方ブロック） | 読み取り対象が存在しない | **挙動等価** |
| ショット no.3 の PROJECT 期待値 | R66（プロジェクト２/maintenance/null/2016-01-02）を使用 | expected_tables group 3 PROJECT に同内容を保持 | **一致** |
| ショット no.4 の PROJECT 期待値検証 | 期待値ブロックが読まれず **PROJECT を検証しない** | 期待値ブロックが無く **PROJECT を検証しない** | **挙動等価（ともに未検証）** |
| ショット no.1/no.2 の各期待値 | 正常に検証 | 同内容を保持し検証 | **一致** |
| テスト結果 | `Tests run: 2, Failures: 0, Errors: 0`（Task #1 ベースライン） | `Tests run: 2, Failures: 0, Errors: 0`（Task #5） | **一致（ともに BUILD SUCCESS）** |

**結論**：R92 ブロックは Excel 版でも NTF に読まれていなかったため、Excel 版・YAML 版でテストの検証内容・結果は完全に等価。移行による検証力の低下・デグレは発生していない。

> 補足：ショット no.4「未処理のプロジェクトのみ登録されること」は、本来 PROJECT テーブルの登録結果（STATUS=0 の未処理レコードのみが登録されること）を検証すべきテストだが、上記の元 Excel 記述ミスにより PROJECT の期待値検証が欠落している。これは Excel 時代からの既存事象であり、本移行のスコープ外。

---

## 5. 影響評価

| 項目 | 評価 |
|---|---|
| 移行作業への影響 | なし（挙動等価。全テストパス） |
| 既存テストのデグレ | なし（Excel 版でも R92 は未使用） |
| テスト検証力 | 移行による変化なし。ただしショット no.4 の PROJECT 検証欠落は**元 Excel 時点から存在する既存の弱点** |
| 可読性・将来保守性 | むしろ向上（YAML 化で、どのブロックが存在し何を検証しているかがテキスト差分で明確になった） |

---

## 6. 対応案

| 案 | 内容 | 長所 | 短所 | 位置づけ |
|---|---|---|---|---|
| **A. 現状維持（推奨）** | YAML をそのまま採用し移行完了とする | 挙動等価で安全。移行スコープ（テキスト化）を逸脱しない。テストクラス非変更の原則も維持 | ショット no.4 の PROJECT 検証欠落は残る（ただし元からの事象） | 本移行の完了案として推奨 |
| B. 別課題として品質改善を登録 | ショット no.4 の PROJECT 期待値欠落を別チケット化し、移行とは切り離して追補 | 移行の純粋性を保ちつつ既存の弱点を追跡できる | 追補作業は別途必要 | A と併用推奨（記録のみでも可） |
| C. YAML を直接補正 | `正常に…ケース.yaml` の expected_tables に group 4 の PROJECT 期待値（未処理 STATUS=0 の登録結果）を追記 | 検証力が向上し no.4 が本来の検証を行う | 移行＝「挙動保存」の範囲を超える機能追加。期待値を新規に設計する必要があり、移行ルール「修正しない」に抵触。要レビュー | 品質改善として実施する場合のみ。移行とは分離 |
| D. 元 Excel を修正して再変換 | Excel の R92 を `[4]` に修正し正しい位置へ移動、PROJECT 期待値を正しく整備してから再変換 | 変換元が正される | Excel は本移行で廃止予定であり逆行。手戻り大。C と同じく期待値の新規設計が必要 | 非推奨 |

**推奨**：本移行は「Excel の内容を忠実に YAML 化する」ことがスコープであり、挙動は完全に等価であるため **案 A（現状維持）** で移行を完了する。ショット no.4 の PROJECT 検証欠落は Excel 時代からの既存事象のため、必要なら **案 B** として別途品質改善課題に登録する。案 C/D（期待値の新規追加）はテストの検証ロジックを変更する行為であり、移行とは独立したレビュー・意思決定のもとで実施すべきである。

---

## 7. 添付資料（本 `reports/` 配下）

| 種別 | パス | 内容 |
|---|---|---|
| 変換元 Excel | `data/ProjectCreationServiceActionTest.xlsx` | 変換元の Excel ブック（git 履歴 c367605 から復元。本体ツリーからは削除済み） |
| 変換後 YAML | `data/正常にプロジェクト情報が取り込まれるケース.yaml` | 本事象の該当シートの変換結果（R92 ブロックが未出力） |
| 変換後 YAML | `data/プロジェクトの取り込みに失敗するケース.yaml` | 失敗ケースシートの変換結果（全ブロック一致） |
| 変換後 YAML | `data/setUpDb.yaml` | 空シートの変換結果（0 バイト） |
| 変換ログ | `logs/conversion-warning.log` | `nablarch-testing-converter:convert` 実行ログ。`warnInterleavedBlocks` 警告と `Converted 1 file(s)` を含む |
| Excel 版テストログ | `logs/excel-test.log` | Excel を配置し `unit-test.xml` を YAML 上書き前（develop 版）に戻して実行した `mvn clean test`。`Tests run: 2, Failures: 0, Errors: 0` / BUILD SUCCESS |
| YAML 版テストログ | `logs/yaml-test.log` | 本番構成（YamlTestDataParser 上書き）での `mvn clean test`。`Tests run: 2, Failures: 0, Errors: 0` / BUILD SUCCESS。ログ中に YamlTestDataParser 使用の証跡あり |

> Excel 版・YAML 版の両ログとも `Tests run: 2 / Failures: 0 / Errors: 0 / BUILD SUCCESS` で、§4 の挙動等価を実機ログで裏付ける。両ログ中の `ApplicationException: プロジェクトの開始と終了の関係が不正です。` は失敗ケース（`expectedStatusCode=20`）が意図的に発生させる想定内の FATAL ログであり、テスト失敗ではない。

## 8. 参考情報

- 検証に用いた Excel ダンプスクリプト：`.rn/ntf-yaml-support/scripts/dump_xlsx.py`（openpyxl 不使用、標準ライブラリのみ）
- サンプリング比較の記録：`.rn/ntf-yaml-support/checks/task-3.md`
- 変換ツールの重複/分断ブロック挙動の仕様：`/home/k10949/workspace/nablarch-testing-converter/README.md`
- 関連コミット：`c367605`（Task #3 変換）、`1bcf9ed`（Task #4 Excel 削除）
