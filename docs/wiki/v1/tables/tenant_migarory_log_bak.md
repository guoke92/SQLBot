---
type: table
title: 租户项目迁移记录表
page_key: tenant_migarory_log_bak
belong: tables
status: draft
anchors: [tenant_migarory_log_bak]
sources: ['database_schema:lowcode_pplatform.tenant_migarory_log_bak']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, tenant_migarory_log_bak__name, tenant_migarory_log_bak__direction,
  tenant_migarory_log_bak__type, tenant_migarory_log_bak__status, tenant_migarory_log_bak__success_number,
  tenant_migarory_log_bak__falied_number, tenant_migarory_log_bak__total_number, tenant_migarory_log_bak__enable,
  tenant_migarory_log_bak__app_tenant_code, tenant_migarory_log_bak__db_tenant_code]
---

# 租户项目迁移记录表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### migration

`direction`, `type`, `batch_no`, `status`, `req_sn`, `req_no`

### payload

`request`, `response`, `error`, `data`

### metrics

`success_number`, `falied_number`, `total_number`

### tenant

`app_tenant_code`, `db_tenant_code`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`platform_product_code`, `organization_id`, `trace_id`

## 字段

```ground:table
table: tenant_migarory_log_bak
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
- key: migration
  title: 迁移任务
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
- key: payload
  title: 请求与返回数据
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
- key: metrics
  title: 数量统计
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
- key: tenant
  title: 租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak
- key: approval
  title: 审批流程
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
  dictionary: tenant_migarory_log_bak__name
- name: direction
  data_type: string
  description: 数据方向
  cluster: migration
  dictionary: tenant_migarory_log_bak__direction
- name: type
  data_type: string
  description: 类型
  cluster: migration
  dictionary: tenant_migarory_log_bak__type
- name: batch_no
  data_type: string
  description: 批次号
  cluster: migration
- name: status
  data_type: string
  description: 迁移状态
  cluster: migration
  dictionary: tenant_migarory_log_bak__status
- name: req_sn
  data_type: string
  description: 请求流水编码
  cluster: migration
- name: platform_product_code
  data_type: string
  description: 产品编码
- name: req_no
  data_type: string
  description: 请求编号
  cluster: migration
- name: request
  data_type: string
  description: 请求数据
  cluster: payload
- name: response
  data_type: string
  description: 返回数据
  cluster: payload
- name: error
  data_type: string
  description: 错误信息
  cluster: payload
- name: data
  data_type: string
  description: 迁移数据
  cluster: payload
- name: success_number
  data_type: number
  description: 成功数量
  cluster: metrics
  dictionary: tenant_migarory_log_bak__success_number
- name: falied_number
  data_type: number
  description: 失败数量
  cluster: metrics
  dictionary: tenant_migarory_log_bak__falied_number
- name: total_number
  data_type: number
  description: 总数量
  cluster: metrics
  dictionary: tenant_migarory_log_bak__total_number
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: tenant_migarory_log_bak__enable
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
  cluster: tenant
  dictionary: tenant_migarory_log_bak__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: tenant_migarory_log_bak__db_tenant_code
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
- name: trace_id
  data_type: string
  description: trace_id
  nullable: false
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_migarory_log_bak.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_migarory_log_bak.platform_product_code;database_profile:lowcode_pplatform.tenant_migarory_log_bak.platform_product_code
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
  sample_size: 14
  miss: 14
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 名称与注释均指向产品编码，但探测 14 条全 miss、overlap 0.0，且本列取值含 JSON 数组，与 platform_product.code
  值域不匹配，故判定不成立
```

## 页面链接

### 关联表

- [[tables/platform_product]]

### 字典

- [[dicts/tenant_migarory_log_bak__name]]（`tenant_migarory_log_bak.name`）
- [[dicts/tenant_migarory_log_bak__direction]]（`tenant_migarory_log_bak.direction`）
- [[dicts/tenant_migarory_log_bak__type]]（`tenant_migarory_log_bak.type`）
- [[dicts/tenant_migarory_log_bak__status]]（`tenant_migarory_log_bak.status`）
- [[dicts/tenant_migarory_log_bak__success_number]]（`tenant_migarory_log_bak.success_number`）
- [[dicts/tenant_migarory_log_bak__falied_number]]（`tenant_migarory_log_bak.falied_number`）
- [[dicts/tenant_migarory_log_bak__total_number]]（`tenant_migarory_log_bak.total_number`）
- [[dicts/tenant_migarory_log_bak__enable]]（`tenant_migarory_log_bak.enable`）
- [[dicts/tenant_migarory_log_bak__app_tenant_code]]（`tenant_migarory_log_bak.app_tenant_code`）
- [[dicts/tenant_migarory_log_bak__db_tenant_code]]（`tenant_migarory_log_bak.db_tenant_code`）
