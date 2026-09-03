---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:wechat-project-initiation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 企微项目立项审批主表（sp_no 唯一键；45 业务字段；企微 API 同步+洞察回写+人工编辑三源）。
page_key: wechat_project_approval_apply
domain: 项目审批
aliases:
- wechat_project_approval_apply
anchors:
- wechat_project_approval_apply
---
# wechat_project_approval_apply

企微项目立项审批主表（sp_no 唯一键；45 业务字段；企微 API 同步+洞察回写+人工编辑三源）。

```ground:table
table: wechat_project_approval_apply
description: 企微项目立项审批主表（sp_no 唯一键；45 业务字段；企微 API 同步+洞察回写+人工编辑三源）。
inactive: false
fields:
- name: act_procinst_status
  dictionary: sp-status
- name: bussiness_manager
- name: data_source
  dictionary: data-source
- name: first_settlement_time
- name: op_contact
- name: prd
- name: project_approval_name
- name: project_online_name
- name: project_phase
  dictionary: project-phase
- name: solution_manager
- name: sp_no
- name: sp_pass_time
- name: sp_type
```
