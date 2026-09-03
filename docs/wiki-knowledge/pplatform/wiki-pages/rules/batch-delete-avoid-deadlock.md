---
type: rule
title: 批量删除其他账户避免死锁
page_key: batch-delete-avoid-deadlock
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_account_info.ref_cust_company_info]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“批量删除其他账户避免死锁”要求删除非当前账户时，先按 `ref_cust_company_info` 查询 ID 列表，再用主键 ID 批量删除，避免非主键条件删除导致数据库死锁。

## 需求背景

直接使用非主键字段删除账户可能引起数据库锁竞争。该规则通过两阶段删除降低死锁风险，提升系统稳定性。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 批量删除其他账户避免死锁
content: 删除非当前账户时先按 ref_cust_company_info 查询ID列表，再用主键ID批量删除，避免非主键条件删除导致死锁
impact: 降低数据库死锁风险
field_targets:
  - cust_account_info.id
  - cust_account_info.ref_cust_company_info
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:deleteOtherCustAccount"
```

[[cust_account_info]] 表字段 `id` 与 `ref_cust_company_info` 参与该规则。