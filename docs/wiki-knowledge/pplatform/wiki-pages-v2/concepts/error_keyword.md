---
type: concept
title: 报错关键字（errorKeyword）
page_key: error_keyword
domain: 资金规则与异常处理
status: draft
aliases:
  - errorKeyword
  - errorMessage
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyExceptionResolutionProviderImpl.java
  - db:funding_exception_resolution
maps_to: funding_exception_resolution.error_keyword
field_targets:
  - funding_exception_resolution.error_keyword
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
belong: concepts
field_targets: [funding_exception_resolution.error_keyword]
---

报错关键字是 [[funding_exception_resolution]] 的命中词：Provider 用它与上游传入的 errorMessage 做 contains 匹配。代码中局部变量命名为 errorMessage，实际取的是 DTO.errorKeyword，**命名混淆但语义同一字段**。

## 需求背景

- 命中为大小写敏感的 contains，且可命中多条全部返回（[[exception_provider_contains_match]]）。
- 关键字同时是业务唯一键成员，参与导入查重与保存前校验（[[exception_import_all_or_nothing]]、[[exception_check_before_save_unique]]）。

## 版本演进

v0 首次建立，判定类型 synonym，边界即「局部变量名 errorMessage 与字段 errorKeyword 的命名混淆」。