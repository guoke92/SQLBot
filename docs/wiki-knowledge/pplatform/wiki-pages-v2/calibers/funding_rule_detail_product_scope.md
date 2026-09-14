---
type: caliber
title: 资方规则明细产品范围（DB 实际落库值）
page_key: funding_rule_detail_product_scope
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则明细 product_code 分布
  - funding_rule_detail ACFLOW 占比
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_rule_detail
contract_version: "0.1"
belong: calibers
---

[[funding_rule_detail]] 的 product_code 同样双产品并存，ACFLOW 约占七成。

## 需求背景

实测产品分布与导入时资方校验硬编码 ACFLOW 的实现之间存在语义张力：为 RVSFACTOR_PC 导入的明细能够落库，但其资方合法性判断仍以 ACFLOW 名单为准，见 [[rule_import_funding_party_hardcoded]]。

## 版本演进

v0 首次建立，占比取自 calibers 条目 DB 证据，未做时间切片。

```ground:caliber
name: 资方规则明细产品范围（DB 实际落库值）
predicate: funding_rule_detail.product_code = 'ACFLOW'
scope: DB 实测 1062/1530；另一取值 RVSFACTOR_PC 468/1530
evidence: db
```