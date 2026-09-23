# Removed EQUI_JOIN relations (53)

- generated_at: `2026-09-22T08:06:43.933903+00:00`
- files_touched: 37

## code_disproven (3)

- `cust_company_info.id` → `cust_setting_config.cust_id` (host=`cust_setting_config`, trust=`proposed`)
  - CustSettingConfig used as singleton (list/getById); cust_id not used as per-company FK in code; live empty
- `tenant_project_approval_flow.code` → `tenant_project_approval.flow_code` (host=`tenant_project_approval`, trust=`proposed`)
  - ApiModelProperty: flow_code → tenant_project_approval_flow_config#flow_code, not flow.code; ProjectApprovalApplication.listFlowConfig queries FlowConfig by flowCode
- `tenant_project_approval_flow_config.id` → `tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config` (host=`tenant_project_approval`, trust=`proposed`)
  - runtime joins by flow_code string to flow_config, not by flow_config.id; live empty_endpoint

## empty_no_code (2)

- `cust_company_info.id` → `cust_auth_application_config.cust_id` (host=`cust_auth_application_config`, trust=`proposed`)
  - no CustAuthApplicationConfig usage in pplatform-web; live empty_endpoint
- `cust_auth_application.id` → `cust_auth_application_config.ref_cust_auth_application_config_cust_auth_application` (host=`cust_auth_application_config`, trust=`proposed`)
  - no CustAuthApplicationConfig usage in pplatform-web; live empty_endpoint

## false_friend (6)

- `cust_company_info.id` → `cust_account_info.ref_cust_company_info` (host=`cust_account_info`, trust=`disputed`)
  - negligible overlap on large domains (left->right=0.0, right->left=0.0, join_hits=2, distinct L/R=94906/46240); not a usable equi-join
- `cust_company_info.id` → `cust_auth_application.ref_cust_company_info` (host=`cust_auth_application`, trust=`disputed`)
  - negligible overlap on large domains (left->right=0.0038, right->left=0.0166, join_hits=358, distinct L/R=94906/29687); not a usable equi-join
- `cust_company_info.id` → `cust_certification_info.ref_cust_company_info` (host=`cust_certification_info`, trust=`disputed`)
  - negligible overlap on large domains (left->right=0.0, right->left=0.0021, join_hits=4, distinct L/R=94906/2069); not a usable equi-join
- `cust_company_info.id` → `cust_interworking_product.ref_cust_interworking_product_cust_company_info` (host=`cust_interworking_product`, trust=`disputed`)
  - negligible overlap on large domains (left->right=0.0, right->left=0.0066, join_hits=2, distinct L/R=94906/261); not a usable equi-join
- `cust_company_info.id` → `cust_person_info.ref_cust_company_info` (host=`cust_person_info`, trust=`disputed`)
  - negligible overlap on large domains (left->right=0.0038, right->left=0.0176, join_hits=358, distinct L/R=94906/54029); not a usable equi-join
- `cust_company_info.id` → `cust_role_info.ref_cust_company_info` (host=`cust_role_info`, trust=`disputed`)
  - negligible overlap on large domains (left->right=0.0038, right->left=0.007, join_hits=359, distinct L/R=94906/54135); not a usable equi-join

## impossible (39)

- `platform_product.code` → `argeement_migratory_record.platform_product_code` (host=`argeement_migratory_record`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `authorization_agreement.platform_product_code` (host=`authorization_agreement`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `ca_fee_company.id` → `ca_fee_order.company_id` (host=`ca_fee_order`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `cust_auth_application.platform_product_code` (host=`cust_auth_application`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_product.id` → `cust_auth_application.ref_cust_auth_application_tenant_product` (host=`cust_auth_application`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `cust_company_lifecycle_info.code` → `cust_company_info.apply_data_id` (host=`cust_company_info`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `cust_account_info.code` → `cust_company_info.apply_data_id` (host=`cust_company_info`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `cust_company_info.id` → `cust_head_company_info.ref_cust_head_company_info_cust_company_info` (host=`cust_head_company_info`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `cust_interworking_product.platform_product_code` (host=`cust_interworking_product`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `cust_customized_product.id` → `cust_interworking_product.product_id` (host=`cust_interworking_product`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_interworking_product.id` → `cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product` (host=`cust_interworking_product`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `cust_customized_product.id` → `cust_project_rel.product_id` (host=`cust_project_rel`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.id` → `cust_project_rel.ref_cust_project_rel_platform_product` (host=`cust_project_rel`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `cust_auth_application.id` → `cust_role_info.ref_cust_auth_application` (host=`cust_role_info`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `cust_company_info.id` → `cust_shareholder_info.ref_cust_company_info` (host=`cust_shareholder_info`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product_cust_role.product_code` → `platform_product.product_ref_num` (host=`platform_product`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `platform_product_cust_role.product_code` (host=`platform_product_cust_role`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.id` → `tenant_interworking_product.ref_tenant_interworking_product_platform_product` (host=`tenant_interworking_product`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_setting_config.id` → `tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config` (host=`tenant_interworking_product`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `tenant_interworking_product.platform_product_code` (host=`tenant_interworking_product`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_setting_config.id` → `tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config` (host=`tenant_interworking_project`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_interworking_product.id` → `tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product` (host=`tenant_interworking_project`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `tenant_interworking_project.platform_product_code` (host=`tenant_interworking_project`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `tenant_migarory_log.platform_product_code` (host=`tenant_migarory_log`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `tenant_migarory_log_bak.platform_product_code` (host=`tenant_migarory_log_bak`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_setting_config.id` → `tenant_product.ref_tenant_product_tenant_setting_config` (host=`tenant_product`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `tenant_product.platform_product_code` (host=`tenant_product`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_product.code` → `tenant_product_menu.product_code` (host=`tenant_product_menu`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_product.code` → `tenant_product_menu_res.product_code` (host=`tenant_product_menu_res`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_product_menu.id` → `tenant_product_menu_res.menu_id` (host=`tenant_product_menu_res`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.code` → `tenant_project.platform_product_code` (host=`tenant_project`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_interworking_project.code` → `tenant_project.project_code` (host=`tenant_project`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `platform_product.id` → `tenant_project.ref_tenant_project_platform_product` (host=`tenant_project`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_project.id` → `tenant_project_approval.ref_tenant_project_approval_tenant_project` (host=`tenant_project_approval`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_product.code` → `tenant_project_approval_business_info.product_code` (host=`tenant_project_approval_business_info`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_project_approval.id` → `tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval` (host=`tenant_project_approval_flow`, trust=`disputed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_project_approval_flow_node.code` → `tenant_project_approval_flow.node_code` (host=`tenant_project_approval_flow`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_project_approval_flow.code` → `tenant_project_approval_flow_config.flow_code` (host=`tenant_project_approval_flow_config`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)
- `tenant_project_approval_flow_node.code` → `tenant_project_approval_flow_config.node_code` (host=`tenant_project_approval_flow_config`, trust=`proposed`)
  - no shared values: join_hits=0 and both inclusion counts are 0 (cannot be an equi-join / same business key in this DB)

## superseded_by_code_join (1)

- `cust_company_info.id` → `cust_project_rel.ref_cust_project_rel_cust_company_info` (host=`cust_project_rel`, trust=`disputed`)
  - same right already has confirmed cust_company_info.code → cust_project_rel.ref_cust_project_rel_cust_company_info; prior live=weak_overlap

## superseded_same_left_endpoint (2)

- `cust_company_info.id` → `cust_company_lifecycle_info.ref_cust_company_info` (host=`cust_company_lifecycle_info`, trust=`disputed`)
  - same left `cust_company_info.id` already has confirmed join to `cust_company_lifecycle_info.company_id` between cust_company_info↔cust_company_lifecycle_info; uncertain `cust_company_lifecycle_info.ref_cust_company_info` removed
- `cust_company_info.id` → `cust_customized_product.ref_cust_customized_product_cust_company_info` (host=`cust_customized_product`, trust=`disputed`)
  - same left `cust_company_info.id` already has confirmed join to `cust_customized_product.cust_id` between cust_company_info↔cust_customized_product; uncertain `cust_customized_product.ref_cust_customized_product_cust_company_info` removed
