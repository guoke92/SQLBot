---
type: rule
title: 对接人组别随 operation_id 反查刷新
page_key: rule/op-contact-group-refresh
domain: 微企链立项与项目审批
status: draft
aliases:
  - op_contact_group 联动
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

运营/档案/风控三组对接人列各配一个组别列，组别不是独立录入的，而是随对应对接人的 `operation_id` 反查刷新得到。因此组别列是派生数据：只要 contact 改了而 group 没跟着刷新，两者就会不一致。

排查「组别和对接人对不上」时，首先要确认是否存在绕过刷新逻辑的写入路径。标识体系说明见 [[concepts/operation-id-contact-reference]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 对接人组别随 operation_id 反查刷新
subject: wechat_project_approval_apply.op_contact_group
evidence: code
source_meaning: 运营组别，随 op_contact 的 operation_id 反查刷新
```