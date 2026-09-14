---
type: rule
title: 异常解析保存前唯一性校验
page_key: exception_check_before_save_unique
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析唯一键校验
  - 报错关键字已经存在
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - db:funding_exception_resolution
contract_version: "0.1"
belong: rules
---

页面手工新增/编辑与导入链路共用同一唯一键三元组 (productCode, fundingPartyCode, errorKeyword)，命中即抛 BaseException('报错关键字已经存在')。

## 需求背景

保存前校验是 DB 唯一约束（funding_exception_resolution_un）在应用层的等价实现，并被导入查重复用（[[exception_import_all_or_nothing]]）。校验会排除自身 id，因此编辑同一条记录不会误判冲突。

## 版本演进

v0 首次建立。

```ground:rule
name: 异常解析保存前唯一性校验
content: checkBeforeSave 按 productCode + fundingPartyCode + errorKeyword（并排除自身 id）查询，命中即抛 BaseException('报错关键字已经存在')。
impact: 页面手工新增/编辑同样受唯一键约束
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.error_keyword
evidence: code_path:ExceptionResolutionApplication.java:checkBeforeSave
```