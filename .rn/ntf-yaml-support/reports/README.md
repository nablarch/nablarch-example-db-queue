# reports/ — Task #3 事象（EXPECTED_TABLE 分断ブロック）関連資料

Task #3（Excel→YAML 変換）で検出した「`EXPECTED_TABLE[3]=PROJECT`（Excel 92行目）が YAML に未出力」事象に関する報告書と証跡を格納する。

## 格納物

```
reports/
├── README.md                              … 本索引
├── task-3-interleaved-block-report.md     … 事象報告書（概要/詳細/直接原因・根本原因/挙動比較/対応案）
├── data/
│   ├── ProjectCreationServiceActionTest.xlsx          … 変換元 Excel（git c367605 から復元）
│   ├── 正常にプロジェクト情報が取り込まれるケース.yaml   … 変換後 YAML（R92 未出力の該当シート）
│   ├── プロジェクトの取り込みに失敗するケース.yaml       … 変換後 YAML（失敗ケース）
│   └── setUpDb.yaml                                    … 変換後 YAML（空シート, 0 バイト）
└── logs/
    ├── conversion-warning.log  … 変換ログ（warnInterleavedBlocks 警告を含む）
    ├── excel-test.log          … Excel 版テスト（mvn clean test, BUILD SUCCESS）
    └── yaml-test.log           … YAML 版テスト（mvn clean test, BUILD SUCCESS）
```

まず `task-3-interleaved-block-report.md` を参照のこと。結論は「変換は挙動保存であり Excel 版・YAML 版でテスト結果は等価」。

## ログ再取得の手順（参考）

- 変換ログ: Excel を `src/test/java/com/nablarch/example/app/batch/` に一時配置し
  `mvn com.nablarch.framework:nablarch-testing-converter:1.0.0-SNAPSHOT:convert` を実行（出力 YAML は既存コミットとバイト一致）。
- Excel 版テスト: 上記 Excel 配置に加え `src/test/resources/unit-test.xml` を develop 版（YAML 上書き前）に戻して `LANG=ja_JP.UTF-8 mvn clean test`。実行後は `git checkout` と Excel 削除で復元する。
- YAML 版テスト: 本番構成のまま `LANG=ja_JP.UTF-8 mvn clean test`。
