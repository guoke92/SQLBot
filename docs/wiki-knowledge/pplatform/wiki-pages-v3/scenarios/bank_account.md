---
type: scenario
title: 企业银行账户
page_key: bank_account
domain: 企业银行账户/集团/SFTP
status: draft
aliases: [银行账号, 打款认证]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:企业银行账户/集团/SFTP"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_account_info]
field_targets:
  - cust_account_info.auth_state
  - cust_account_info.default_account_flag
---

# 企业银行账户

问「默认账户 / 未打款认证 / 银行类账户」时进入本场景。

**主档** [[cust_account_info]]。打款次数上限来自共享配置 [[cust_setting_config]].payment_maximum_number，不是账户自己的状态机。`auth_state` 是打款认证过程；`status` 库内多为 `INIT`，不要当成认证结论。

```ground:scenario
scenario: bank_account
hubs:
- table: cust_account_info
  role: master
  grain: 一企下一银行账户
  window:
  - id
  - enable
  - create_time
  - update_time
  - ref_cust_company_info
  - account_no
  - account_name
  - account_type
  - default_account_flag
  - auth_state
  - payment_remaining_count
  - status
shared:
- table: cust_company_info
  role: identity
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - name
- table: cust_setting_config
  role: auth_config
  window:
  - id
  - enable
  - create_time
  - update_time
  - payment_maximum_number
  - payment_verification
lifecycle:
- enum: account_auth_state
  process: account_auth_state_flow
```
