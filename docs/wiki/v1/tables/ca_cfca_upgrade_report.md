---
type: table
title: CFCA证书升级业务上报与触达记录
page_key: ca_cfca_upgrade_report
belong: tables
status: draft
anchors: [ca_cfca_upgrade_report]
sources: ['database_schema:lowcode_pplatform.ca_cfca_upgrade_report']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_cfca_upgrade_report__source_system, ca_cfca_upgrade_report__company_type,
  ca_cfca_upgrade_report__biz_module, ca_cfca_upgrade_report__trigger_scene, ca_cfca_upgrade_report__todo_triggered,
  ca_cfca_upgrade_report__enable, ca_cfca_upgrade_report__db_tenant_code]
---

# CFCA证书升级业务上报与触达记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### business_event

`task_id`, `source_system`, `title`, `content`, `biz_module`, `occur_time`, `related_biz_no`, `trigger_scene`, `pass_info`, `todo_triggered`, `notify_time`

### company

`company_id`, `company_type`, `certification_no`, `customer_name`, `organization_id`

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
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [customer_name, title, authorized_user_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: business_event
  title: 上报事件
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: company
  title: 企业/客户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: authorized
  title: 被授权人
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_cfca_upgrade_report
- key: tenant
  title: 租户
  trust: proposed
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
  cluster: business_event
- name: source_system
  data_type: string
  description: 来源系统
  cluster: business_event
  dictionary: ca_cfca_upgrade_report__source_system
- name: company_id
  data_type: string
  description: 企业 ID
  cluster: company
- name: company_type
  data_type: string
  description: 企业角色
  cluster: company
  dictionary: ca_cfca_upgrade_report__company_type
- name: certification_no
  data_type: string
  description: 统码
  cluster: company
- name: customer_name
  data_type: string
  description: 企业/客户名称
  cluster: company
- name: title
  data_type: string
  description: 异常标题
  cluster: business_event
- name: content
  data_type: string
  description: 异常内容（单层 JSON）
  cluster: business_event
- name: biz_module
  data_type: string
  description: 所属模块
  cluster: business_event
  dictionary: ca_cfca_upgrade_report__biz_module
- name: occur_time
  data_type: temporal
  description: 异常发生时间
  cluster: business_event
- name: related_biz_no
  data_type: string
  description: 关联业务编号
  cluster: business_event
- name: trigger_scene
  data_type: string
  description: 触发场景
  cluster: business_event
  dictionary: ca_cfca_upgrade_report__trigger_scene
- name: pass_info
  data_type: string
  description: 透传 JSON
  cluster: business_event
- name: todo_triggered
  data_type: string
  description: 是否曾触发待办/消息 Y/N
  cluster: business_event
  dictionary: ca_cfca_upgrade_report__todo_triggered
- name: notify_time
  data_type: temporal
  description: 触发时间
  cluster: business_event
- name: authorized_user_id
  data_type: number
  description: 被授权人用户 ID
  cluster: authorized
- name: authorized_user_name
  data_type: string
  description: 被授权人姓名
  cluster: authorized
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: ca_cfca_upgrade_report__enable
- name: remark
  data_type: string
  description: remark
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: ca_cfca_upgrade_report__db_tenant_code
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: company
```

## 页面链接

### 字典

- [[dicts/ca_cfca_upgrade_report__source_system]]（`ca_cfca_upgrade_report.source_system`）
- [[dicts/ca_cfca_upgrade_report__company_type]]（`ca_cfca_upgrade_report.company_type`）
- [[dicts/ca_cfca_upgrade_report__biz_module]]（`ca_cfca_upgrade_report.biz_module`）
- [[dicts/ca_cfca_upgrade_report__trigger_scene]]（`ca_cfca_upgrade_report.trigger_scene`）
- [[dicts/ca_cfca_upgrade_report__todo_triggered]]（`ca_cfca_upgrade_report.todo_triggered`）
- [[dicts/ca_cfca_upgrade_report__enable]]（`ca_cfca_upgrade_report.enable`）
- [[dicts/ca_cfca_upgrade_report__db_tenant_code]]（`ca_cfca_upgrade_report.db_tenant_code`）
