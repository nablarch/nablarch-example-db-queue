# task-1 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| 既存の `ntf-yaml-support` ブランチ上で作業しており、コミット履歴が維持されている（過去の移行コミットが残っている） | OK | ブランチ新規作成・rebase・amend・hard reset なし。過去の移行コミット `4865a20`〜`a0859ef` がベースラインコミット `2e0ea2d` の祖先として残存 | | |
| ブランチの既存先端の上に、ワーキングツリー全体が `develop` と同一内容になる新規コミットが1つ積まれている | OK | `git read-tree -u --reset develop` → コミット `2e0ea2d`（親 `a0859ef`）。`2e0ea2d^{tree}` = `develop^{tree}` = `ecdb691e`。その後ユーザー指示のテストデータ修正を別コミット `5331421` として積む（xlsx 1セルのみ: R92 `EXPECTED_TABLE[3]=PROJECT` → `EXPECTED_TABLE[4]=PROJECT`。`evidence/task-1-testdata-fix.diff`） | | |
| `mvn test` が全テストパスで終了している（BUILD SUCCESS） | OK | `LANG=ja_JP.UTF-8` で `mvn -B clean generate-resources` → BUILD SUCCESS、`mvn -B test` → Tests run: 2, Failures: 0, Errors: 0, Skipped: 0 / BUILD SUCCESS（修正後テストデータで実行。`evidence/task-1-generate-resources.txt`、`evidence/task-1-test.txt`） | | |
| 本指示書のコピーが `.rn/ntf-yaml-support/` 配下に原本と同一内容で配置され、コミットされている | OK | `.rn/ntf-yaml-support/ntf-yaml-support-instructions_db-queue_V1.6.md` を配置し、`cmp` で原本と同一を確認。Task #1 のコミットに含める | | |

Script: `scripts/dump_xlsx.py`（xlsx の全セルをグリッド表示。テストデータ修正の新旧比較に使用）

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
