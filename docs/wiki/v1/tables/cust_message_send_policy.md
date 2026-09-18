---
type: table
title: 客户消息发送策略
page_key: cust_message_send_policy
belong: tables
status: draft
anchors: [cust_message_send_policy]
sources: ['database_schema:lowcode_pplatform.cust_message_send_policy']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
---

# 客户消息发送策略

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`name`

### msg_policy

`scenes_type`, `msg_kind`, `send_enable`

### ownership

`app_tenant_code`, `db_tenant_code`, `organization_id`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: cust_message_send_policy
database: lowcode_pplatform
description: 客户消息发送策略
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 业务标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_message_send_policy
- key: msg_policy
  title: 消息场景与发送开关
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_message_send_policy
- key: ownership
  title: 数据归属
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_message_send_policy
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_message_send_policy
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: scenes_type
  data_type: string
  description: 场景码
  cluster: msg_policy
- name: msg_kind
  data_type: string
  description: 消息类型
  cluster: msg_policy
- name: send_enable
  data_type: string
  description: 发送标识
  cluster: msg_policy
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: identity
- name: enable
  data_type: string
  description: enable
  cluster: common
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
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: ownership
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: ownership
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: ownership
```
