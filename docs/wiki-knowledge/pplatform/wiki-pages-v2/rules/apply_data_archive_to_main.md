---
type: rule
title: 流程数据归档回主数据
page_key: apply_data_archive_to_main
domain: 企业建档与认证
status: draft
aliases:
  - 认证成功回写主数据
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:ApplyCompanyInfoApplication.java:setApplyDataToMain
contract_version: "0.1"
belong: rules
---

认证成功后，流程申请数据（`data_type='2'`）的内容被回写到主数据（`data_type='1'`）：企业、人员、账户、关联方、开通产品、影像均按此复制，并在主数据上回写 `apply_data_id` 以记录最近一次认证流程。

```ground:rule
name: 流程数据归档回主数据
content: 认证成功后 APPLY 数据回写 MAIN（copy 企业/人员/账户/关联方/开通产品/影像），并回写 apply_data_id
impact: 主数据与流程数据一致性
field_targets:
  - cust_company_info.data_type
  - cust_company_info.main_data_id
  - cust_company_info.apply_data_id
evidence: code_path:ApplyCompanyInfoApplication.java:setApplyDataToMain
```

## 需求背景

[[tables/cust_company_info]] 单表承载主数据与流程数据，认证过程中所有修改都落在流程数据上，只有认证通过才整体归档到主数据，从而保证未通过的修改不污染企业当前态。这也是 [[rules/applying_record_uniqueness]] 需要串行的原因。

## 版本演进

v0 初稿：规则以 `setApplyDataToMain` 的复制范围固化，覆盖的资源清单以代码为准。

关联：[[processes/cust_build_status_state_machine]]、[[calibers/main_data_judgment]]、[[concepts/build_success]]。