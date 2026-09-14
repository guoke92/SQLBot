---
type: rule
title: 资方规则导入的资方校验产品被硬编码为 ACFLOW
page_key: rule_import_funding_party_hardcoded
domain: 资金规则与异常处理
status: draft
aliases:
  - 资方校验硬编码 ACFLOW
  - collectFundingPartyMarkErrors
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_info
contract_version: "0.1"
belong: rules
---

规则导入校验资方标识时，代码固定使用 ProductCodeEnum.ACFLOW 调 ClientQueryFunderMarkService，合法资方集合与 mark→name 映射均以 ACFLOW 为准，而错误文案中拼的却是行自身的 productCode。

## 需求背景

实现与实测数据存在语义张力：DB 中 [[funding_rule_detail]] 与 [[funding_rule_info]] 均存在 RVSFACTOR_PC 产品数据（见 [[funding_rule_detail_product_scope]]、[[exception_resolution_product_scope]]），但为 RVSFACTOR_PC 导入规则时，资方合法性仍按 ACFLOW 名单判断，落库的 fundingPartyName 也可能来自 ACFLOW 映射。这对「名称仅用于展示」的假设（[[funding_party_name]]）构成风险，需业务确认。

## 版本演进

v0 首次建立，按代码现状登记，不做行为修正。

```ground:rule
name: 资方规则导入的资方校验产品被硬编码为 ACFLOW
content: collectFundingPartyMarkErrors 里 dto.setProductCode(ProductCodeEnum.ACFLOW) 后调 ClientQueryFunderMarkService，合法资方集合与 mark→name 映射均以 ACFLOW 为准，但错误文案中拼的是行自身的 productCode。
impact: 为 RVSFACTOR_PC 导入规则时，资方合法性仍按 ACFLOW 名单判断，且落库的 fundingPartyName 可能来自 ACFLOW 映射；与 DB 实测两产品并存存在语义张力
field_targets:
  - funding_rule_info.product_code
  - funding_rule_info.funding_party_mark
  - funding_rule_info.funding_party_name
evidence: code_path:FundRuleInfoApplication.java:collectFundingPartyMarkErrors
```