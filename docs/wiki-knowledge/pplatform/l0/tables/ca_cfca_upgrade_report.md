---
type: table
title: CFCA证书升级业务上报与触达记录
page_key: ca_cfca_upgrade_report
belong: tables
status: draft
aliases: []
anchors:
- ca_cfca_upgrade_report
sources:
- database_schema:lowcode_pplatform.ca_cfca_upgrade_report
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# CFCA证书升级业务上报与触达记录

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### company

`company_id`, `company_type`, `certification_no`, `customer_name`, `organization_id`

### task_source

`task_id`, `source_system`

### report_event

`title`, `content`, `biz_module`, `occur_time`, `related_biz_no`, `trigger_scene`, `pass_info`

### notify

`todo_triggered`, `notify_time`

### authorized

`authorized_user_id`, `authorized_user_name`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: ca_cfca_upgrade_report
database: lowcode_pplatform
description: CFCA证书升级业务上报与触达记录
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- customer_name
- title
- authorized_user_name
- code
- name
clusters:
- key: common
  title: 通用与审计
  include: always
- key: company
  title: 企业与机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: task_source
  title: 任务与来源
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: report_event
  title: 异常上报
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: notify
  title: 待办触达
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: authorized
  title: 被授权人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: task_id
  data_type: string
  description: 业务系统任务ID
  nullable: true
  cluster: task_source
- name: source_system
  data_type: string
  description: 来源系统
  nullable: true
  cluster: task_source
- name: company_id
  data_type: string
  description: 企业 ID
  nullable: true
  cluster: company
- name: company_type
  data_type: string
  description: 企业角色
  nullable: true
  cluster: company
  dictionary: ca_cfca_upgrade_report_company_type
- name: certification_no
  data_type: string
  description: 统码
  nullable: true
  cluster: company
- name: customer_name
  data_type: string
  description: 企业/客户名称
  nullable: true
  cluster: company
- name: title
  data_type: string
  description: 异常标题
  nullable: true
  cluster: report_event
- name: content
  data_type: string
  description: 异常内容（单层 JSON）
  nullable: true
  cluster: report_event
- name: biz_module
  data_type: string
  description: 所属模块
  nullable: true
  cluster: report_event
- name: occur_time
  data_type: temporal
  description: 异常发生时间
  nullable: true
  cluster: report_event
- name: related_biz_no
  data_type: string
  description: 关联业务编号
  nullable: true
  cluster: report_event
- name: trigger_scene
  data_type: string
  description: 触发场景
  nullable: true
  cluster: report_event
- name: pass_info
  data_type: string
  description: 透传 JSON
  nullable: true
  cluster: report_event
- name: todo_triggered
  data_type: string
  description: 是否曾触发待办/消息 Y/N
  nullable: true
  cluster: notify
  dictionary: ca_cfca_upgrade_report_todo_triggered
- name: notify_time
  data_type: temporal
  description: 触发时间
  nullable: true
  cluster: notify
- name: authorized_user_id
  data_type: number
  description: 被授权人用户 ID
  nullable: true
  cluster: authorized
- name: authorized_user_name
  data_type: string
  description: 被授权人姓名
  nullable: true
  cluster: authorized
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: common
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: company
```
