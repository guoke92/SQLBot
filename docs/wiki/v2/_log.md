# L0 ingest log (2026-09-20)

source: tools.wiki_extract compile (database_schema)

touched tables (78): `argeement_migratory_record`, `async_io_task`, `authorization_agreement`, `ca_certification_info`, `ca_cfca_upgrade_report`, `ca_fee_company`, `ca_fee_order`, `ca_fee_project_config`, `ca_fee_special_config`, `client_api_sync_error`, `cust_access_secret`, `cust_account_info`, `cust_app_channel_config`, `cust_auth_application`, `cust_auth_application_config`, `cust_build_record`, `cust_certification_info`, `cust_change_cfg`, `cust_change_record`, `cust_company_info`, `cust_company_lifecycle_info`, `cust_company_survey_state`, `cust_company_survey_whitelist`, `cust_config_mapping`, `cust_customized_product`, `cust_group_rel`, `cust_head_company_info`, `cust_interworking_product`, `cust_invite_info`, `cust_message_send_policy`, `cust_oper_change_record`, `cust_person_info`, `cust_project_code_record`, `cust_project_pushcust`, `cust_project_rel`, `cust_role_info`, `cust_setting_config`, `cust_sftp`, `cust_shareholder_info`, `cust_survey_answer`, `cust_user_rel`, `funding_exception_resolution`, `funding_rule_detail`, `funding_rule_front_cfg`, `funding_rule_info`, `gpt_learn_poster_log`, `lc_sql_init_log`, `migratory_user_record`, `open_sso_channel`, `operation_user`, `org_manage`, `platform_product`, `platform_product_client`, `platform_product_cust_role`, `project_file_info`, `short_link`, `tenant_interworking_product`, `tenant_interworking_project`, `tenant_migarory_log`, `tenant_migarory_log_bak`, `tenant_product`, `tenant_product_menu`, `tenant_product_menu_res`, `tenant_project`, `tenant_project_approval`, `tenant_project_approval_business_info`, `tenant_project_approval_flow`, `tenant_project_approval_flow_comment`, `tenant_project_approval_flow_config`, `tenant_project_approval_flow_credit`, `tenant_project_approval_flow_file`, `tenant_project_approval_flow_node`, `tenant_setting_config`, `tenant_setting_config_share`, `wec_project_cust_operation_rel`, `wec_project_operation_rel`, `wechat_project_approval_apply`, `wechat_project_approval_field_history`

join authenticity: likely=29 unlikely=37 unknown=21 (all edges kept, no primary)

overlap: probed=87 likely=31 unlikely=37 unknown=19 llm_added=0 overlap_added=12 name_only_unprobed=0 deepened=8

grain: L0 placeholder 一行一记录（pk）; confirm from source. inactive left false until source/docs prove dormancy.

status: all pages draft; no published writes.
