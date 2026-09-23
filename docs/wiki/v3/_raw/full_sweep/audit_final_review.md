# Wiki v3 full sweep — agent final review

- generated_at: `2026-09-23T04:14:20.291254+00:00`
- reviewer: agent (not scripts alone)
- LLM: `deepseek/deepseek-flash` @ atk.llschain.com (env only; not committed)
- live DB: UAT `lowcode_pplatform`

## Verdict

Sweep + continuation complete. EQUI_JOIN：**119**（confirmed 113 / proposed 6）。Dict triage：**keep 309 / hold 0**（28 hold 已全部 promote）。

## Continuation (this pass)

### Hold dict promote
- LLM：26 个纯 Y/N → keep + 中文 label，并回写表字段 `label:`。
- 源码收口 2 个：
  - `group_company`：展示逻辑 Y→是 / 非 Y→否；`'1'` 标为脏数据等同否。
  - `need_register_bs`：对齐 `OpenStatus`（Y/P/N = 需要开通/开通中/未开通）。

### Code-diff residual
- 新确认 3 边：`cust_person_info.user_id`→`authorized_user_id` / `migratory_user_record.user_id`；`ca_fee_company.source_project_id`↔`ca_fee_order.project_id`。
- False-friend 探针全部失败（weak/impossible），与预期一致。
- 剩余 52 条 code_wiki_diff 已分类入库 `code_diff_rejected.yaml`（type noise / wrong target / copy-not-join / self-edge），**不写入 wiki**。

### Semantics
- `field_semantics.yaml` 已标注 funding B↔C + platform hub、project invite channel 的 live 确认。

### Sync
- related / 页面链接 / fence 镜像已刷新。

## Residual risks
1. UAT 空子表上的 confirmed FK 仍保留（生产可能有数据）。
2. `flow_code` 仍 proposed（UAT 列空）。
3. SSO `channel_code`→`cust_company_info.channel_code` 仍 proposed（企业侧空）。
4. Code extract 噪声已归档，勿再 bulk-write。

## Artifacts
- `docs/wiki/v3/_raw/full_sweep/hold_promote_result.yaml`
- `docs/wiki/v3/_raw/full_sweep/hold_promote_llm.yaml`
- `docs/wiki/v3/_raw/full_sweep/code_diff_rejected.yaml`
- `docs/wiki/v3/_raw/full_sweep/continue_candidate_validate.yaml`
- `docs/wiki/v3/_raw/full_sweep/remaining_relations.md`
- this file + `docs/wiki/v3/_raw/audit_final_review.md`

---

## Orphan repair follow-up (2026-09-23)

- EQUI_JOIN：**131**（confirmed 122 / proposed 9）
- `ref*`：**39/39 已挂 JOIN**（含 UAT 空的 proposed）
- 孤立表：**14**（真孤立 / 配置灌入非 JOIN，未强行互连）
  - 仍孤立：`async_io_task`, `client_api_sync_error`, `cust_access_secret`, `cust_config_mapping`, `cust_message_send_policy`, `cust_setting_config`（配额灌入非 JOIN）, `cust_sftp`, `gpt_learn_poster_log`, `lc_sql_init_log`, `operation_user`, `org_manage`, `short_link`, `tenant_migarory_log`, `tenant_migarory_log_bak`
- 已接入：`project_file_info`, `platform_product_cust_role`, `ca_fee_special_config`, `wec_project_*`, `cust_auth_application_config`
- wec ↔ 产融：**对等场景、ID 空间隔离**，已写说明、禁止跨域 EQUI_JOIN
- 明细：`docs/wiki/v3/_raw/full_sweep/orphan_and_unref.md` / `orphan_repair_written.yaml`
