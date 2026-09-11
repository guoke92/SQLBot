---
type: rule
title: 认证状态条件更新
page_key: auth_status_conditional_update
domain: 企业建档与认证
status: draft
aliases:
  - 认证状态并发保护
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
contract_version: "0.1"
---

更新认证状态时，系统要求匹配**原状态**、`enable = 'Y'`、`data_type = '1'`（主数据，见 [[main_data]]）三个条件同时成立，才执行更新。这是一条乐观并发控制规则，用于保证认证状态机（[[enterprise_auth_status_machine]]）状态迁移的原子性，避免并发请求造成状态跳变或覆盖。

需要写认证状态时，务必带上原状态与数据类型条件，不能只按主键直接更新。

```ground:rule
name: 认证状态条件更新
content: 更新认证状态时需匹配原状态且 enable='Y' 且 data_type='1'（主数据），防止并发错误。
impact: 保证状态迁移的原子性。
field_targets:
  - cust_build_status
evidence: "code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。