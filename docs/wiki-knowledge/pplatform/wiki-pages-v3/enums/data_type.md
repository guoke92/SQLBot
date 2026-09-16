---
type: enum
title: data_type
page_key: data_type
domain: 基线
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustDataTypeConstant.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# data_type

[[cust_company_info]] 的 `data_type`：同一企业在本表可同时有主数据行和流程行。

代码 `CustDataTypeConstant`：`1` 主数据、`0` 流程数据、`2` 编辑过程。列注释写成「1,主数据，0记录数据」，漏了 `2`，且把 `0` 叫记录数据——问数以代码为准。主数据行才参与生效/冻结/注销。问有效企业见 [[effective_company]]。

```ground:enum
enum: data_type
fields: [cust_company_info.data_type]
values:
  "0":
    label: "流程数据"
  "1":
    label: "主数据"
  "2":
    label: "编辑过程"
```
