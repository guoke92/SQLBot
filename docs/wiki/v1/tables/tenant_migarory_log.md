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
  tenant_migarory_log__status, tenant_migarory_log__enable, tenant_migarory_log__app_tenant_code,
  tenant_migarory_log__db_tenant_code]
---

# 租户项目迁移记录表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### migration_exec

`direction`, `type`, `batch_no`, `status`, `req_sn`, `req_no`, `trace_id`

### payload

`request`, `response`, `message`, `data`

### metrics

`success_number`, `falied_number`, `total_number`

### refs

`platform_product_code`, `app_tenant_code`, `db_tenant_code`, `organization_id`

### approval

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
- key: migration_exec
  title: 迁移执行要素
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log
- key: payload
  title: 请求与返回载荷
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log
- key: metrics
  title: 迁移数量统计
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log
- key: refs
  title: 关联对象与租户归属
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_migarory_log
- key: approval
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
  cluster: refs
- name: direction
  data_type: string
  description: 数据方向
  cluster: migration_exec
  dictionary: tenant_migarory_log__direction
- name: type
  data_type: string
  description: 类型
  cluster: migration_exec
  dictionary: tenant_migarory_log__type
- name: batch_no
  data_type: string
  description: 批次号
  cluster: migration_exec
- name: status
  data_type: string
  description: 迁移状态
  cluster: migration_exec
  dictionary: tenant_migarory_log__status
- name: req_sn
  data_type: string
  description: 请求流水编码
  cluster: migration_exec
- name: req_no
  data_type: string
  description: 请求编号
  cluster: migration_exec
- name: trace_id
  data_type: string
  description: trace_id
  nullable: false
  cluster: migration_exec
- name: request
  data_type: string
  description: 请求数据
  cluster: payload
- name: response
  data_type: string
  description: 返回数据
  cluster: payload
- name: message
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
- name: falied_number
  data_type: number
  description: 失败数量
  cluster: metrics
- name: total_number
  data_type: number
  description: 总数量
  cluster: metrics
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
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: refs
  dictionary: tenant_migarory_log__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: refs
  dictionary: tenant_migarory_log__db_tenant_code
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
  cluster: refs
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
authenticity_note: 名称证据支持（platform_product 词干 + 注释「产品编码」），但已探测 overlap：样本 10 行全部 miss，ratio=0.0，提示两侧编码体系或取值口径不一致（本地列可能为枚举/未落库编码），暂判
  unlikely，建议扩大样本或核对编码规范后复核。
```

## 页面链接

### 关联表

- [[tables/platform_product]]

### 字典

- [[dicts/tenant_migarory_log__direction]]（`tenant_migarory_log.direction`）
- [[dicts/tenant_migarory_log__type]]（`tenant_migarory_log.type`）
- [[dicts/tenant_migarory_log__status]]（`tenant_migarory_log.status`）
- [[dicts/tenant_migarory_log__enable]]（`tenant_migarory_log.enable`）
- [[dicts/tenant_migarory_log__app_tenant_code]]（`tenant_migarory_log.app_tenant_code`）
- [[dicts/tenant_migarory_log__db_tenant_code]]（`tenant_migarory_log.db_tenant_code`）
