---
type: rule
title: 异常解析产品名→code 与资金方名→code 二次翻译
page_key: exception_import_name_code_translation
domain: 资金规则与异常处理
status: draft
aliases:
  - 导入翻译规则
  - 产品名转 code
  - 资金方名转标识
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

导入允许用户填「产品名称」与「资金方名称-标识」，系统负责翻译成 product_code 与 funding_party_code 后回写，再校验回填值是否落在合法集合内。

## 需求背景

该规则是「全量校验通过才入库」（[[exception_import_all_or_nothing]]）阶段 2 / 阶段 3 的组成部分，翻译失败会以「不在允许范围内 / 不存在」的形式进入错误列表，导致整批拒绝。产品合法集合来自 listPlatformProduct(GENERAL)，与平台产品的维护链路相关。

## 版本演进

v0 首次建立，证据取自异常解析导入链路。

```ground:rule
name: 异常解析产品名→code 与资金方名→code 二次翻译
content: 阶段2 用 listPlatformProduct(GENERAL) 构 productName→productCode 映射回填；阶段3 用 RPC 结果构 "fundingPartyName-fundingKey"→fundingKey 映射回填，再校验回填值是否在合法集合内。
impact: 导入模板允许填产品名称/资金方名称-标识，系统会翻译；翻译失败则报“不在允许范围内/不存在”
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
evidence: code_path:ExceptionResolutionApplication.java:collectProductCodeErrors/collectFundingPartyCodeErrors
```