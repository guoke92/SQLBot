---
type: rule
title: 企业状态更新必须限定主数据（data_type）
page_key: rule.status_update_main_data_type
domain: 平台内部服务对接
status: draft
aliases:
  - 状态更新主数据条件
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.data_type]
  - semantic:state_machines[客户生命周期状态]
contract_version: "0.1"
---

对企业表做状态更新时，必须带 data_type = CustDataTypeConstant.DATA_TYPE_MAIN 条件。

## 需求背景

企业表在同一张物理表内混合了多种数据类型，缺少该条件会误更新非主数据行。冻结、解冻、注销、建档状态推进等路径（见 [[processes/cust_status_machine]]）都依赖此约束。

## 版本演进

v0：首次成页。

```ground:rule
name: 企业状态更新必须限定主数据
field: cust_company_info.data_type
condition: "data_type = CustDataTypeConstant.DATA_TYPE_MAIN"
effect: "所有状态更新均带此条件，避免误改非主数据行"
evidence: code
```