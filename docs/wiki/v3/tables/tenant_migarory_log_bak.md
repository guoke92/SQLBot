---
type: table
title: 租户项目迁移记录表
page_key: tenant_migarory_log_bak
belong: tables
status: draft
anchors: [tenant_migarory_log_bak]
sources: ['database_schema:lowcode_pplatform.tenant_migarory_log_bak']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, tenant_migarory_log_bak__name, tenant_migarory_log_bak__direction,
  tenant_migarory_log_bak__type, tenant_migarory_log_bak__status, tenant_migarory_log_bak__success_number,
  tenant_migarory_log_bak__falied_number, tenant_migarory_log_bak__total_number, tenant_migarory_log_bak__enable]
---

# 租户项目迁移记录表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_migarory_log_bak
database: lowcode_pplatform
desc: 租户项目迁移记录表
inactive: false
primary_key: [id]
grain: 迁移日志备份（无业务 DO）
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
  dict: [migratoryProject, syncProject, syncProduct, EFFECTED, migratoryCust, 迁移客户,
    CREATED, 同步项目, ACTIVE_CFCA_SIGN, PROJECT_SYNC, CHANGED, PROJECT_SYNC_VALIDATE,
    migratoryTenant, INPUT_project_20240905163839, 迁移租户, 同步产品, DELETED, INPUT_tenant_20240905172700,
    INPUT_project_20240905164552]
- name: direction
  type: string
  desc: 数据方向
  dict: [IN, OUT]
- name: type
  type: string
  desc: 类型
  dict: [migratoryProject, PROJECT_SYNC, CUST_PRODUCT_SYNC, syncProject, TENANT_SYNC,
    syncProduct, PRODUCT_SYNC, migratoryCust, migratoryTenant, CREATED, DELETED, PROJECT_SYNC_VALIDATE,
    TENANT_SYNC_VALIDATE, EFFECTED]
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
- name: platform_product_code
  type: string
  desc: 产品编码
- name: req_no
  type: string
  desc: 请求编号
- name: request
  type: string
  desc: 请求数据
- name: response
  type: string
  desc: 返回数据
- name: error
  type: string
  desc: 错误信息
- name: data
  type: string
  desc: 迁移数据
- name: success_number
  type: number
  desc: 成功数量
  dict: ['1']
- name: falied_number
  type: number
  desc: 失败数量
  dict: ['1', '0']
- name: total_number
  type: number
  desc: 总数量
  dict: ['1']
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
- name: trace_id
  type: string
  desc: trace_id
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
