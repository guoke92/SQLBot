---
type: table
title: 租户项目审批流程配置表
page_key: tenant_project_approval_flow_config
belong: tables
status: draft
aliases: []
anchors:
- tenant_project_approval_flow_config
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_flow_config
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目审批流程配置表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### flow_node

`flow_code`, `node_code`, `node_name`, `node_order`, `is_optional`, `is_operate`

### approval_instance

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

## 字段

```ground:table
table: tenant_project_approval_flow_config
database: lowcode_pplatform
description: 租户项目审批流程配置表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- flow_code
- node_code
- node_name
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: flow_node
  title: 审批流程与节点配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_config
- key: approval_instance
  title: 审批实例信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_config
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_flow_config
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: flow_code
  data_type: string
  description: 流程编码：NO_ONLINE，STANDARD，REGULAR
  nullable: true
  cluster: flow_node
  dictionary: tenant_project_approval_flow_config_flow_code
- name: node_code
  data_type: string
  description: 节点编码字典
  nullable: true
  cluster: flow_node
  dictionary: tenant_project_approval_flow_config_node_code
- name: node_name
  data_type: string
  description: 节点名称（中文）
  nullable: true
  cluster: flow_node
- name: node_order
  data_type: number
  description: 节点顺序
  nullable: true
  cluster: flow_node
- name: is_optional
  data_type: string
  description: 是否可选节点：Y/N
  nullable: true
  cluster: flow_node
  dictionary: tenant_project_approval_flow_config_is_optional
- name: is_operate
  data_type: string
  description: 是否可操作
  nullable: true
  cluster: flow_node
  dictionary: tenant_project_approval_flow_config_is_operate
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
  dictionary: tenant_project_approval_flow_config_enable
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
  cluster: approval_instance
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
  cluster: approval_instance
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_instance
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_instance
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
```
