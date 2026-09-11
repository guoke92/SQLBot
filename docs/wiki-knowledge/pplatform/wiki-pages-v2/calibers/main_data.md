---
type: caliber
title: 主数据
page_key: main_data
domain: 企业建档与认证
status: draft
aliases:
  - 企业主数据
oid: 1
scope:
  databases: []
sources:
  - code:CustDataTypeConstant.DATA_TYPE_MAIN
contract_version: "0.1"
---

“主数据”口径用于把同一个企业实体在 `cust_company_info` 中的**正式记录**与过程记录区分开：`data_type = '1'` 的记录代表企业主数据，是企业查询与更新的默认范围（见 [[cust_company_info]]、[[effective_company]]）。

认证/变更过程中产生的记录数据与申请数据不属于主数据，口径见 [[process_apply_data]]；主数据通过 `apply_data_id` 指向最近一次流程数据，过程数据通过 `main_data_id` 回指主数据。

```ground:caliber
name: 主数据
predicate: cust_company_info.data_type = '1'
scope: 企业主数据查询与更新
evidence: "code_path:CustDataTypeConstant.DATA_TYPE_MAIN"
```

## 需求背景

暂无需求文档主张。该口径是状态更新等写操作的前置条件之一，见 [[auth_status_conditional_update]]。

## 版本演进

- v0.1：依据代码证据建立口径页。