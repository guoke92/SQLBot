# Reextract confirmed written (20)

- generated_at: `2026-09-22T09:31:09.234957+00:00`
- policy: Curated from reextract-joins accepted (fk_like/shared_domain), patterns.md rules, orphan-gap priority; skipped redundant sibling hub-FK same-name

- [NEW] `tenant_product_menu.menu_id` → `tenant_product_menu_res.menu_id` host=`tenant_product_menu_res` verdict=`fk_like` — 菜单与按钮同 menu_id
- [NEW] `tenant_product_menu.product_code` → `tenant_product_menu_res.product_code` host=`tenant_product_menu_res` verdict=`fk_like` — 菜单与按钮同 product_code
- [NEW] `platform_product.product_code` → `platform_product_cust_role.product_code` host=`platform_product_cust_role` verdict=`shared_domain` — 平台产品业务码（非 UUID code）
- [NEW] `tenant_setting_config.dbass_app_id` → `tenant_setting_config_share.dbass_app_id` host=`tenant_setting_config_share` verdict=`fk_like` — 共享租户与租户配置
- [NEW] `cust_company_info.id` → `ca_cfca_upgrade_report.company_id` host=`ca_cfca_upgrade_report` verdict=`fk_like` — CFCA 升级上报企业
- [NEW] `tenant_project.id` → `ca_fee_special_config.project_id` host=`ca_fee_special_config` verdict=`fk_like` — CA 特殊配置项目
- [NEW] `ca_fee_company.certification_no` → `ca_fee_special_config.certification_no` host=`ca_fee_special_config` verdict=`fk_like` — CA 特殊配置证书号
- [NEW] `funding_rule_info.product_code` → `funding_rule_front_cfg.product_code` host=`funding_rule_front_cfg` verdict=`fk_like` — 资方规则前端配置
- [NEW] `funding_rule_info.product_code` → `funding_exception_resolution.product_code` host=`funding_exception_resolution` verdict=`fk_like` — 资金方异常解析
- [NEW] `funding_rule_info.product_code` → `funding_rule_detail.product_code` host=`funding_rule_detail` verdict=`fk_like` — 规则明细产品码
- [NEW] `tenant_project_approval_flow.node_code` → `tenant_project_approval_flow_node.node_code` host=`tenant_project_approval_flow_node` verdict=`fk_like` — 流程实例节点码
- [NEW] `tenant_project_approval_flow.node_code` → `tenant_project_approval_flow_config.node_code` host=`tenant_project_approval_flow_config` verdict=`shared_domain` — 流程预设节点码
- [NEW] `wechat_project_approval_apply.sp_no` → `wechat_project_approval_field_history.sp_no` host=`wechat_project_approval_field_history` verdict=`fk_like` — 企微审批单号
- [NEW] `tenant_interworking_product.code` → `cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product` host=`cust_interworking_product` verdict=`fk_like` — 互通产品 code→ref
- [NEW] `platform_product.code` → `tenant_project.ref_tenant_project_platform_product` host=`tenant_project` verdict=`fk_like` — 项目 ref 存平台产品 UUID code
- [NEW] `tenant_product.platform_product_code` → `tenant_project.platform_product_code` host=`tenant_project` verdict=`fk_like` — 租户产品/项目业务产品码
- [NEW] `tenant_interworking_product.platform_product_code` → `tenant_interworking_project.platform_product_code` host=`tenant_interworking_project` verdict=`fk_like` — 互通产品/项目业务产品码
- [NEW] `cust_interworking_product.platform_product_code` → `tenant_interworking_product.platform_product_code` host=`tenant_interworking_product` verdict=`shared_domain` — 企业互通产品业务码
- [NEW] `open_sso_channel.app_id` → `cust_app_channel_config.app_id` host=`cust_app_channel_config` verdict=`shared_domain` — 开放 SSO 与客户渠道 app
- [NEW] `tenant_setting_config.id` → `cust_interworking_product.tenant_id` host=`cust_interworking_product` verdict=`fk_like` — 企业互通产品租户
