---
type: table
title: 租户项目迁移记录表
page_key: tenant_migarory_log
belong: tables
status: draft
anchors: [tenant_migarory_log]
sources: ['database_schema:lowcode_pplatform.tenant_migarory_log']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, tenant_migarory_log__direction, tenant_migarory_log__type,
  tenant_migarory_log__status, tenant_migarory_log__enable]
---

# 租户项目迁移记录表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_migarory_log
database: lowcode_pplatform
desc: 租户项目迁移记录表
inactive: false
primary_key: [id]
grain: 租户/项目迁移请求日志
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: platform_product_code
  type: string
  desc: 产品编码
- name: direction
  type: string
  desc: 数据方向
  dict: [IN, OUT]
- name: type
  type: string
  desc: 类型
  dict: [migratoryProject, syncProject, migratoryCust, PROJECT_SYNC_VALIDATE, PROJECT_SYNC,
    CUST_PRODUCT_SYNC, TENANT_SYNC, TENANT_SYNC_VALIDATE, syncProduct, PROJECT_QUERY,
    migratoryTenant, migratoryOnTheWayCust, PRODUCT_SYNC, PRODUCT_SYNC_VALIDATE]
- name: batch_no
  type: string
  desc: 批次号
- name: status
  type: string
  desc: 迁移状态
  dict: [Y, N]
- name: req_sn
  type: string
  desc: 请求流水编码
- name: req_no
  type: string
  desc: 请求编号
- name: trace_id
  type: string
  desc: trace_id
  nullable: false
- name: request
  type: string
  desc: 请求数据
- name: response
  type: string
  desc: 返回数据
- name: message
  type: string
  desc: 错误信息
- name: data
  type: string
  desc: 迁移数据
- name: success_number
  type: number
  desc: 成功数量
- name: falied_number
  type: number
  desc: 失败数量
- name: total_number
  type: number
  desc: 总数量
- name: enable
  type: string
  desc: enable
  dict: [Y]
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
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
