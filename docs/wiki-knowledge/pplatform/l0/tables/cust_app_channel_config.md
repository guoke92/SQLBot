---
type: table
title: 客户应用渠道关系
page_key: cust_app_channel_config
belong: tables
status: draft
aliases: []
anchors:
- cust_app_channel_config
sources:
- database_schema:lowcode_pplatform.cust_app_channel_config
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户应用渠道关系

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### biz_identity

`app_id`, `name`, `organization_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`remark`

## 字段

```ground:table
table: cust_app_channel_config
database: lowcode_pplatform
description: 客户应用渠道关系
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用与审计
  include: always
- key: biz_identity
  title: 业务主体
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_app_channel_config
- key: workflow
  title: 流程审批
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_app_channel_config
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_app_channel_config
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: app_id
  data_type: string
  description: 应用id
  nullable: true
  cluster: biz_identity
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: biz_identity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_app_channel_config_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
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
  cluster: biz_identity
```
