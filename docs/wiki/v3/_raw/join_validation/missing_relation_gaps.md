# Missing / orphan relation inventory

- generated_at: `2026-09-23T03:48:52.352470+00:00`
- wiki tables: 78
- confirmed/proposed EQUI_JOIN unique edges: **92**
- connected components: 25 (largest=48)
- orphan tables (no direct/indirect join): **20**

> 本清单在 scrub / comment_fk / 二值补全后重算图统计。孤立表列表如下；
> 配置/埋点/任务类可保持孤立。历史「候选缺口」见 git 旧版。

## 当前孤立表

- `async_io_task`
- `ca_fee_special_config`
- `client_api_sync_error`
- `cust_access_secret`
- `cust_auth_application_config`
- `cust_change_cfg`
- `cust_config_mapping`
- `cust_message_send_policy`
- `cust_setting_config`
- `cust_sftp`
- `gpt_learn_poster_log`
- `lc_sql_init_log`
- `migratory_user_record`
- `operation_user`
- `org_manage`
- `platform_product_cust_role`
- `project_file_info`
- `short_link`
- `wec_project_cust_operation_rel`
- `wec_project_operation_rel`
