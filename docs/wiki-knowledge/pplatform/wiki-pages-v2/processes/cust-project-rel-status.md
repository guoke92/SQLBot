---
type: process
title: 企业项目关联生效状态
page_key: cust-project-rel-status
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_rel.status
  - 关联生效状态
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustProjectController.java
  - db:cust_project_rel
contract_version: "0.1"
belong: processes
---

# 企业项目关联生效状态

该状态落在 [[tables/cust_project_rel]] 的 `status`，表示某企业在某项目下的关联关系是否已生效。它影响关联企业清单是否进入生效口径，与逻辑删除标识 `enable` 是两套独立过滤条件。

## 需求背景

企业关联项目在满足业务前置条件（产品为 ACFLOW/ORDER，且该角色下不存在已生效项目）时，由 updateRelPrjStatus 接口把 status 从 0 置为 1，写库值取 `EnableEnum.Y.getDictKey()`。查询侧普遍叠加 `enable = 'Y'` 过滤（如 [[calibers/chanyong-related-company]]），因此「已删除」与「未生效」需分别判断。

## 版本演进

DB 中出现带首尾空格的 ` 1 ` 值，属历史脏数据，读取与比较需容错；未见从 1 回退到 0 的迁移路径证据。

```ground:state_machine
name: "企业项目关联生效状态"
field: cust_project_rel.status
states:
  - value: "0"
    label: "未生效"
    source: db_dist
  - value: "1"
    label: "已生效"
    source: db_dist
  - value: "' 1 '"
    label: "已生效（历史脏数据，带首尾空格）"
    source: db_dist
transitions:
  - from: "0"
    event: "调用 updateRelPrjStatus，且产品为 ACFLOW/ORDER 且该角色下无生效项目时"
    to: "1"
    evidence: "code_path:CustProjectController.java:updateRelPrjStatus（set status = EnableEnum.Y.getDictKey()）"
```