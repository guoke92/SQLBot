---
type: caliber
title: 主数据判定口径（data_type = DATA_TYPE_MAIN）
page_key: caliber.main_data_type
domain: 平台内部服务对接
status: draft
aliases:
  - 主数据
  - DATA_TYPE_MAIN
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.data_type]
contract_version: "0.1"
---

企业表同一物理表内混放多类数据，主数据以 CustDataTypeConstant.DATA_TYPE_MAIN 标识。

## 需求背景

所有状态更新均带此条件限定（见 [[rules/status_update_main_data_type]]），否则会误改非主数据行。这是企业侧最基础的一致性口径，跨服务写企业状态时必须遵守。

## 版本演进

v0：首次成页。

```ground:caliber
name: 主数据判定口径
field: cust_company_info.data_type
values:
  - CustDataTypeConstant.DATA_TYPE_MAIN
criterion: "状态更新均带此条件"
evidence: code
```