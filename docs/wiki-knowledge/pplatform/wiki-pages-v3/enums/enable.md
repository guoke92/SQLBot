---
type: enum
title: enable
page_key: enable
domain: 基线
status: draft
aliases: [是否启用]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeConstants.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# enable

`Y` / `N` 开关。常量 `ENABLE_Y` / `FLAG_Y` / `FLAG_N` 没有中文 displayName；各列自己的「已锁定 / 已生成 / 已签」写在表字段上，不要套到本字典。

`agreement_version`、`pay_channel` 不是本字典。`renew_remind_sent` 虽也是 Y/N，表示本期续费待办是否已生成，复位见 [[ca_fee_renew_remind]]。

```ground:enum
enum: enable
fields:
  - ca_fee_company.enable
  - ca_fee_company.fee_locked
  - ca_fee_company.special_config_flag
  - ca_fee_order.enable
  - ca_fee_order.agreement_signed
  - ca_fee_project_config.charge_enabled
  - ca_fee_project_config.enable
  - cust_company_info.enable
  - cust_company_info.need_register_ca
  - cust_company_info.head_company
  - ca_certification_info.enable
  - ca_certification_info.head_company_data
  - cust_change_record.enable
  - cust_change_record.need_cust_confirm
  - cust_change_cfg.enable
  - cust_change_cfg.head_company
  - cust_change_cfg.open_process
  - cust_person_info.enable
  - cust_invite_info.enable
  - cust_auth_application.enable
  - cust_role_info.enable
  - platform_product_cust_role.enable
  - cust_access_secret.enable
  - cust_sftp.enable
  - cust_account_info.enable
  - cust_group_rel.enable
  - authorization_agreement.enable
  - platform_product.enable
  - cust_customized_product.enable
  - cust_project_rel.enable
  - project_file_info.enable
  - tenant_setting_config.enable
  - short_link.enable
  - funding_rule_info.enable
  - funding_rule_detail.enable
  - funding_exception_resolution.enable
  - cust_company_survey_whitelist.enable
  - gpt_learn_poster_log.enable
  - cust_oper_change_record.enable
  - operation_user.enable
values:
  "Y": {}
  "N": {}
```
