---
type: caliber
title: 流程/申请数据
page_key: process_apply_data
domain: 企业建档与认证
status: draft
aliases:
  - 记录数据
  - 申请数据
oid: 1
scope:
  databases: []
sources:
  - code:CustDataTypeConstant.DATA_TYPE_RECORD/DATA_TYPE_APPLY
contract_version: "0.1"
---

“流程/申请数据”口径覆盖 `cust_company_info` 中 `data_type IN ('0','2')` 的记录：`0` 为记录数据（暂存/变更过程数据），`2` 为申请数据（认证流程数据）。两者合起来代表企业的过程态数据，与主数据（[[main_data]]）相对。

该口径是“在途变更”判断的基础：当存在 `data_type = '2'` 且认证状态不在成功/失败态的流程数据时，视为存在在途变更流程，见 [[change_precondition_check]]。

```ground:caliber
name: 流程/申请数据
predicate: cust_company_info.data_type IN ('0','2')
scope: 认证流程、变更流程数据
evidence: "code_path:CustDataTypeConstant.DATA_TYPE_RECORD/DATA_TYPE_APPLY"
```

## 需求背景

暂无需求文档主张。过程数据通过 `main_data_id` 关联主数据，主数据通过 `apply_data_id` 关联最近一次流程数据，二者构成双向引用。

## 版本演进

- v0.1：依据代码证据建立口径页。