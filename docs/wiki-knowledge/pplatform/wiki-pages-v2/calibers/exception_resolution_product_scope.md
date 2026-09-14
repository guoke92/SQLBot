---
type: caliber
title: 异常解析产品范围（DB 实际落库值）
page_key: exception_resolution_product_scope
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析 product_code 分布
  - 异常解析 ACFLOW 占比
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_exception_resolution
contract_version: "0.1"
belong: calibers
---

[[funding_exception_resolution]] 的 product_code 在实际库中呈双产品并存：ACFLOW 为主、RVSFACTOR_PC 为次。

## 需求背景

该分布是「产品 code 不写死」的实测依据，与资方规则导入中硬编码 ACFLOW 的做法（[[rule_import_funding_party_hardcoded]]）形成对照。产品名 → code 的翻译链见 [[exception_import_name_code_translation]]。本口径是 DB 实测值，不构成校验规则，不能反向用于限制导入取值。

## 版本演进

v0 首次建立，占比取自 calibers 条目 DB 证据，未做时间切片，未区分 enable 状态。

```ground:caliber
name: 异常解析产品范围（DB 实际落库值）
predicate: funding_exception_resolution.product_code = 'ACFLOW'
scope: DB 实测 58/90；另一取值 RVSFACTOR_PC 32/90
evidence: db
```