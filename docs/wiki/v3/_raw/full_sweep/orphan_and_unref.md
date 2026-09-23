# Orphan repair result

- edges now: **131** (`{'confirmed': 122, 'proposed': 9}`)
- connected tables: **64** / 78; orphans: **14**
- ref*: linked **39** / 39; unlinked: **0**

## Written this pass

- ✓ `cust_auth_application.code` → `cust_auth_application_config.ref_cust_auth_application_config_cust_auth_application` (proposed)
- ✓ `cust_company_info.id` → `cust_auth_application_config.cust_id` (proposed)
- ✓ `cust_company_info.code` → `cust_company_lifecycle_info.ref_cust_company_info` (proposed)
- ✓ `tenant_project_approval.code` → `tenant_project_approval.ref_tenant_project_approval_tenant_project_approval` (confirmed)
- ✓ `tenant_project.id` → `project_file_info.project_id` (confirmed)
- ✓ `platform_product.product_code` → `platform_product_cust_role.product_code` (confirmed)
- ✓ `tenant_product.platform_product_code` → `platform_product_cust_role.product_code` (confirmed)
- ✓ `tenant_project.id` → `ca_fee_special_config.project_id` (confirmed)
- ✓ `ca_fee_order.project_id` → `ca_fee_special_config.project_id` (confirmed)
- ✓ `ca_fee_company.certification_no` → `ca_fee_special_config.certification_no` (confirmed)
- ✓ `cust_company_info.certification_no` → `ca_fee_special_config.certification_no` (confirmed)
- ✓ `wec_project_operation_rel.wec_project_id` → `wec_project_cust_operation_rel.project_id` (confirmed)

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

## Remaining unlinked ref*

(none)
