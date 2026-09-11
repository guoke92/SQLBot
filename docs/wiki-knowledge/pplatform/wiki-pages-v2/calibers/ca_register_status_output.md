---
type: caliber
title: 电子签章开通状态对外口径（ca_register_status + caRegisterStatusY）
page_key: caliber.ca_register_status_output
domain: 平台内部服务对接
status: draft
aliases:
  - 签章开通口径
  - caRegisterStatusY
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.ca_register_status]
  - semantic:field_semantics[cust_company_info.need_register_ca]
contract_version: "0.1"
---

对外返回企业是否已开通电子签章时，不能只看 ca_register_status，还需叠加 caRegisterStatusY 校验。

## 需求背景

是否「需要」开通与是否「已」开通是两个字段：need_register_ca 表达诉求，ca_register_status 表达结果，对外输出需两者与校验标记共同决定。简易认证路径下 need_register_ca 被政策强制为不开通（见 [[rules/simple_auth_ca_forbidden]]）。

## 版本演进

v0：首次成页。

```ground:caliber
name: 电子签章开通状态对外口径
field: cust_company_info.ca_register_status
values:
  - "'Y'"
  - "'N'"
criterion: "对外返回还需叠加 caRegisterStatusY 校验"
related_fields:
  - cust_company_info.need_register_ca
evidence: code
```