---
type: rule
title: 变更态下运营中台企业 id 取自变更记录
page_key: rule.change_status_token_source
domain: 平台内部服务对接
status: draft
aliases:
  - 变更态token来源
oid: 1
scope:
  databases: []
sources:
  - semantic:state_machines[客户生命周期状态]
  - semantic:field_semantics[cust_change_record.cust_id / status / oper_cust_info / oper_channel / create_time]
contract_version: "0.1"
---

当企业进入变更态（cust_status=CHANGE）时，换取 token 使用的运营中台企业 id 取自客户变更记录，而非角色表常态字段。

## 需求背景

进入 CHANGE 的触发条件见 [[processes/cust_status_machine]]（queryCustAutoCheck 中 process!=CHECK 分支）；有效变更记录的取用规则见 [[rules/cust_change_record_latest_effective]]，术语映射见 [[concepts/platform_cust_id_bridge]]。

## 版本演进

v0：首次成页。

```ground:rule
name: 变更态下运营中台企业 id 取自变更记录
field: cust_company_info.cust_status
condition: "cust_status = CHANGE"
effect: "token 取变更记录上的运营中台 id"
evidence: code
```