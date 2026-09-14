---
type: caliber
title: 异常解析有效数据口径
page_key: exception_resolution_enable_y
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析 enable 口径
  - funding_exception_resolution enable
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyExceptionResolutionProviderImpl.java
contract_version: "0.1"
belong: calibers
---

[[funding_exception_resolution]] 的可见性完全由 enable 决定，列表、导出、Provider 查询三处口径一致，避免口径漂移。

## 需求背景

导入与保存固定写 'Y'，查询固定过滤 'Y'，因此本表在业务上不存在「停用但仍保留」的中间态；批量删除走物理删除（[[batch_delete_physical]]），enable 不承担软删职责。

## 版本演进

v0 首次建立，口径语句逐字取自 calibers 条目。

```ground:caliber
name: 异常解析有效数据
predicate: funding_exception_resolution.enable = 'Y'
scope: 列表/导出/Provider 查询统一过滤；导入固定写 Y
evidence: code
```