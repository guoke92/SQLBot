---
type: table
title: 项目立项字段更新历史
page_key: wechat_project_approval_field_history
belong: tables
status: draft
aliases: []
anchors:
- wechat_project_approval_field_history
sources:
- database_schema:lowcode_pplatform.wechat_project_approval_field_history
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 项目立项字段更新历史

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### field_change

`field_name`, `field_label`, `old_value`, `new_value`, `change_source`

### operator

`operator_id`, `operator_name`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### apply_ref

`apply_id`, `sp_no`

### ownership

`app_tenant_code`, `db_tenant_code`, `organization_id`

### generic

`name`, `remark`

## 字段

```ground:table
table: wechat_project_approval_field_history
database: lowcode_pplatform
description: 项目立项字段更新历史
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- field_name
- operator_name
- code
- name
clusters:
- key: common
  title: 通用与审计
  include: always
- key: field_change
  title: 字段变更明细
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
- key: operator
  title: 操作人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
- key: act_procinst
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
- key: apply_ref
  title: 立项单引用
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
- key: ownership
  title: 租户与机构标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
- key: generic
  title: 通用名称与备注
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: apply_id
  data_type: number
  description: 关联 wechat_project_approval_apply.id
  nullable: true
  cluster: apply_ref
- name: sp_no
  data_type: string
  description: 审批编号
  nullable: true
  cluster: apply_ref
- name: field_name
  data_type: string
  description: 列名
  nullable: true
  cluster: field_change
- name: field_label
  data_type: string
  description: 中文标签
  nullable: true
  cluster: field_change
- name: old_value
  data_type: string
  description: 变更前值
  nullable: true
  cluster: field_change
- name: new_value
  data_type: string
  description: 变更后值
  nullable: true
  cluster: field_change
- name: change_source
  data_type: string
  description: 变更来源
  nullable: true
  cluster: field_change
  dictionary: wechat_project_approval_field_history_change_source
- name: operator_id
  data_type: string
  description: 操作人ID
  nullable: true
  cluster: operator
- name: operator_name
  data_type: string
  description: 操作人姓名
  nullable: true
  cluster: operator
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: generic
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: wechat_project_approval_field_history_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: generic
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
  cluster: act_procinst
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: ownership
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: ownership
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: act_procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: act_procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: act_procinst
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: ownership
```
