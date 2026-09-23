# Wiki relation / related consistency review

- generated_at: `2026-09-23T06:56:13.956984+00:00`
- verdict: **PASS**

## Counts

| metric | value |
|---|---|
| tables | 78 |
| EQUI_JOIN edges | 131 |
| by trust | `{'confirmed': 122, 'proposed': 9}` |
| connected tables | 64 |
| orphan tables | 14 |
| fence mirrors missing | 0 |
| mirrored meta diffs | 0 |
| duplicate fences | 0 |
| related missing join neighbor | 0 |
| unexpected soft related | 0 |
| dangling related | 0 |
| page-link mismatches | 0 |
| join endpoint missing from ground:table | 0 |

## Soft peers (non-EQUI, intentionally in related)

| table | soft peers | status |
|---|---|---|
| `cust_account_info` | `cust_setting_config` | OK |
| `cust_project_rel` | `wec_project_cust_operation_rel` | OK |
| `cust_setting_config` | `cust_account_info` | OK |
| `tenant_project` | `wec_project_operation_rel` | OK |
| `wec_project_cust_operation_rel` | `cust_project_rel` | OK |
| `wec_project_operation_rel` | `tenant_project` | OK |

## Checks

| check | result |
|---|---|
| EQUI_JOIN mirrored both ends | yes |
| mirrored fence meta consistent | yes |
| related ⊇ join neighbors | yes |
| soft peers preserved | yes |
| 页面链接 covers join+soft | yes |
| no dangling related | yes |
| join columns exist on table pages | yes |
| sync preserves soft peers | yes (test_sync_wiki_related) |

## Remaining orphans

- `async_io_task`
- `client_api_sync_error`
- `cust_access_secret`
- `cust_config_mapping`
- `cust_message_send_policy`
- `cust_setting_config`
- `cust_sftp`
- `gpt_learn_poster_log`
- `lc_sql_init_log`
- `operation_user`
- `org_manage`
- `short_link`
- `tenant_migarory_log`
- `tenant_migarory_log_bak`

## Fixes applied this review

1. `sync_wiki_related` used to **drop** soft table `related` (对等/非 JOIN)；已改为保留，并写入「关联表」链接。
2. 恢复 soft peers：wec↔产融、`cust_setting_config`↔`cust_account_info`。
3. 补 concept：`concepts/wec_project_ops_peer.md`。
4. 回归测试：`tools/wiki_extract/tests/test_sync_wiki_related.py`。
