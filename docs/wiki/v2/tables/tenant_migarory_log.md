---
type: table
title: 租户项目迁移记录表
page_key: tenant_migarory_log
belong: tables
status: draft
anchors: [tenant_migarory_log]
sources: ['database_schema:lowcode_pplatform.tenant_migarory_log']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, tenant_migarory_log__direction, tenant_migarory_log__type,
  tenant_migarory_log__status, tenant_migarory_log__enable]
---

# 租户项目迁移记录表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### migration_task

`platform_product_code`, `direction`, `type`, `batch_no`, `status`, `success_number`, `falied_number`, `total_number`

### request_payload

`req_sn`, `req_no`, `trace_id`, `request`, `response`, `message`, `data`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: tenant_migarory_log
database: lowcode_pplatform
description: 租户项目迁移记录表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: migration_task
  title: 迁移任务
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log
- key: request_payload
  title: 请求与报文
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log
- key: tenant_org
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log
- key: approval_flow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: platform_product_code
  data_type: string
  description: 产品编码
  cluster: migration_task
- name: direction
  data_type: string
  description: 数据方向
  cluster: migration_task
  dictionary: tenant_migarory_log__direction
- name: type
  data_type: string
  description: 类型
  cluster: migration_task
  dictionary: tenant_migarory_log__type
- name: batch_no
  data_type: string
  description: 批次号
  cluster: migration_task
- name: status
  data_type: string
  description: 迁移状态
  cluster: migration_task
  dictionary: tenant_migarory_log__status
- name: req_sn
  data_type: string
  description: 请求流水编码
  cluster: request_payload
- name: req_no
  data_type: string
  description: 请求编号
  cluster: request_payload
- name: trace_id
  data_type: string
  description: trace_id
  nullable: false
  cluster: request_payload
- name: request
  data_type: string
  description: 请求数据
  cluster: request_payload
- name: response
  data_type: string
  description: 返回数据
  cluster: request_payload
- name: message
  data_type: string
  description: 错误信息
  cluster: request_payload
- name: data
  data_type: string
  description: 迁移数据
  cluster: request_payload
- name: success_number
  data_type: number
  description: 成功数量
  cluster: migration_task
- name: falied_number
  data_type: number
  description: 失败数量
  cluster: migration_task
- name: total_number
  data_type: number
  description: 总数量
  cluster: migration_task
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: tenant_migarory_log__enable
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
  cluster: approval_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant_org
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_org
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: tenant_org
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_migarory_log.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_migarory_log.platform_product_code;database_profile:lowcode_pplatform.tenant_migarory_log.platform_product_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 产品编码
overlap:
  probed: true
  ratio: 0.0
  sample_size: 10
  miss: 10
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 列名/注释（产品编码）与 platform_product.code 语义关联，但探测 overlap=0.0（10/10 未命中，sample_size=10），值域不契合，判
  unlikely；仅名称证据不足以判 likely
```

## 页面链接

### 关联表

- [[tables/platform_product]]

### 字典

- [[dicts/tenant_migarory_log__direction]]（`tenant_migarory_log.direction`）
- [[dicts/tenant_migarory_log__type]]（`tenant_migarory_log.type`）
- [[dicts/tenant_migarory_log__status]]（`tenant_migarory_log.status`）
- [[dicts/tenant_migarory_log__enable]]（`tenant_migarory_log.enable`）
