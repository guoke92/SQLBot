---
type: rule
title: 统一社会信用代码跨系统一致性对齐
page_key: certification_no_cross_system_align
domain: 平台内部服务对接
status: draft
aliases:
  - 统一社会信用代码对齐
  - certification_no 对齐
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.certification_no]
contract_version: "0.1"
belong: rules
---

certification_no（统一社会信用代码）被定义为跨系统一致性对齐字段：企业主数据与运营中台等外部系统之间以此字段对齐同一法人主体。

## 需求背景

在企业建档与认证流转（[[processes/cust_build_status_machine]]）中，该字段是识别同一主体的业务键，与内部主键 id、业务编码 code 的用途不同（见 [[concepts/company_id_bridge]]、[[concepts/company_code_bridge]]）。

## 版本演进

v0：首次成页。

```ground:rule
name: 统一社会信用代码跨系统一致性对齐
field: cust_company_info.certification_no
condition: "跨系统企业主体比对"
effect: "作为一致性对齐字段"
evidence: code
```