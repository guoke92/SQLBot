---
type: process
title: 集团关系生效状态机（cust_group_rel.status）
page_key: process.cust_group_rel_status_fsm
domain: 数据权限与组织
status: draft
aliases: [集团关系状态机, 集团关系生效, INEFFECTIVE, EFFECTIVE]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: cust_group_rel.status
---

集团关系生效状态机，承载于 [[tables/cust_group_rel]].status，取值 INEFFECTIVE（未生效）/ EFFECTIVE（已生效）。新增根集团关系时，若企业已建档成功则直接生效，否则先落未生效，待集团或成员企业建档成功时由 effectGroupRel 触发生效；删除集团成员前要校验在途业务与额度，随后才删除记录。

生效口径是子公司平铺列表的过滤条件，见 [[calibers/effective_group_member]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 CustGroupRelApplication。

## 版本演进

v0：依据 code 证据建模；本表字段在 field_semantics 中未收录，仅确认 status，详见 [[tables/cust_group_rel]] 的 REVIEW。

```ground:process
name: 集团关系生效状态机
field: cust_group_rel.status
states:
  - value: INEFFECTIVE
    label: 未生效
    source: code_enum
  - value: EFFECTIVE
    label: 已生效
    source: code_enum
transitions:
  - from: （新增）
    event: 新增根集团关系：企业建档成功则直接生效，否则未生效
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.java#addExistRootGroupRel
  - from: INEFFECTIVE
    event: 集团/成员企业建档成功触发生效
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.java#effectGroupRel
  - from: EFFECTIVE
    event: 删除集团成员前校验在途业务与额度，随后删除
    to: （删除）
    evidence: code_path:CustGroupRelApplication.java#removeRootGroup
```