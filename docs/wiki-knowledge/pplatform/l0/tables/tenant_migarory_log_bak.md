---
type: table
title: 租户项目迁移记录表
page_key: tenant_migarory_log_bak
belong: tables
status: draft
aliases: []
anchors:
- tenant_migarory_log_bak
sources:
- database_schema:lowcode_pplatform.tenant_migarory_log_bak
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目迁移记录表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### migration_core

`name`, `direction`, `type`, `batch_no`, `status`, `platform_product_code`

### request_payload

`req_sn`, `req_no`, `request`, `response`, `error`, `data`

### counts

`success_number`, `falied_number`, `total_number`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### misc

`remark`, `organization_id`, `trace_id`

## 字段

```ground:table
table: tenant_migarory_log_bak
database: lowcode_pplatform
description: 租户项目迁移记录表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- platform_product_code
clusters:
- key: common
  title: 通用
  include: always
- key: migration_core
  title: 迁移核心信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
- key: request_payload
  title: 请求与返回数据
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
- key: counts
  title: 数量统计
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
- key: misc
  title: 其他信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: migration_core
- name: direction
  data_type: string
  description: 数据方向
  nullable: true
  cluster: migration_core
  dictionary: tenant_migarory_log_bak_direction
- name: type
  data_type: string
  description: 类型
  nullable: true
  cluster: migration_core
  dictionary: tenant_migarory_log_bak_type
- name: batch_no
  data_type: string
  description: 批次号
  nullable: true
  cluster: migration_core
- name: status
  data_type: string
  description: 迁移状态
  nullable: true
  cluster: migration_core
  dictionary: tenant_migarory_log_bak_status
- name: req_sn
  data_type: string
  description: 请求流水编码
  nullable: true
  cluster: request_payload
- name: platform_product_code
  data_type: string
  description: 产品编码
  nullable: true
  cluster: migration_core
- name: req_no
  data_type: string
  description: 请求编号
  nullable: true
  cluster: request_payload
- name: request
  data_type: string
  description: 请求数据
  nullable: true
  cluster: request_payload
- name: response
  data_type: string
  description: 返回数据
  nullable: true
  cluster: request_payload
- name: error
  data_type: string
  description: 错误信息
  nullable: true
  cluster: request_payload
- name: data
  data_type: string
  description: 迁移数据
  nullable: true
  cluster: request_payload
- name: success_number
  data_type: number
  description: 成功数量
  nullable: true
  cluster: counts
- name: falied_number
  data_type: number
  description: 失败数量
  nullable: true
  cluster: counts
- name: total_number
  data_type: number
  description: 总数量
  nullable: true
  cluster: counts
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_migarory_log_bak_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: misc
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
  cluster: approval
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
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: misc
- name: trace_id
  data_type: string
  description: trace_id
  nullable: false
  cluster: misc
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_migarory_log_bak.platform_product_code
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak.platform_product_code
```
