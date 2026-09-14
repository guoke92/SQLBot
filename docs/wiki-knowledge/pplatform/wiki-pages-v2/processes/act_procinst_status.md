---
type: process
title: 企微审批状态状态机
page_key: act_procinst_status
domain: 项目报表/统计/上报
status: draft
aliases:
  - 企微审批状态
  - act_procinst_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:ACT_PROCINST_APPROVED
contract_version: "0.1"
belong: processes
---

act_procinst_status 表示企微审批流实例的当前状态，落在 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]] 上。在本主题中它主要作为筛选条件使用：只有审批通过（'2'）的立项才进入提醒范围与阶段自动流转的判定。

## 需求背景

需求文档未单独描述该状态机；分析中仅有「审批通过」一个值点与其常量名。

## 版本演进

v0 契约首版，只登记已确认的 '2'（审批通过）。其余状态值（如审批中、驳回）在本次分析中无证据，契约不发明；待补证后再扩展本页。值点明细见 [[enums/wechat_project_approval_apply_act_procinst_status|act_procinst_status 值点]]（如与基线写值点不一致以写值点与 DB 为准）。

```ground:process
name: 企微审批状态
field: wechat_project_approval_apply.act_procinst_status
states:
  - value: "2"
    label: 审批通过
    source: code_const
transitions: []
evidence: code_path:ProjectStatisticsApplication.java:ACT_PROCINST_APPROVED
```