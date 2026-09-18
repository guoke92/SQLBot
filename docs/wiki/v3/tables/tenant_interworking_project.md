---
type: table
title: 租户互通产品项目
page_key: tenant_interworking_project
belong: tables
status: draft
anchors: [tenant_interworking_project]
sources: ['database_schema:lowcode_pplatform.tenant_interworking_project', 'code_path:TenantInterworkingProjectDaoImpl.java:25']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project, tenant_interworking_product, tenant_setting_config, platform_product,
  tenant_interworking_project__platform_product_code]
---

# 租户互通产品项目

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_interworking_project
database: lowcode_pplatform
desc: 租户互通产品项目
inactive: false
primary_key: [id]
grain: 互通产品绑定的项目
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
- name: product_id
  type: number
  desc: 产品id
- name: tenant_id
  type: number
  desc: 租户id
- name: platform_product_code
  type: string
  desc: 平台产品编码
  dict: [HTCP1, HTCP14, AMS, HTCP13, HTCP5]
- name: project_id
  type: number
  desc: 项目id
- name: ref_tenant_interworking_project_tenant_setting_config
  type: string
  desc: 租户项目
- name: ref_tenant_interworking_project_tenant_interworking_product
  type: string
  desc: 租户产品项目
- name: enable
  type: string
  desc: enable
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
default_filter:
  predicate: tenant_interworking_project.enable = 'Y'
  trust: confirmed
  evidence: code_path:TenantInterworkingProjectDaoImpl.java:25
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project.id
right: tenant_interworking_project.project_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantInterworkingProjectApplicationService.java:64
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: project
  comment: 项目id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 9
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 互通项目绑定的是 tenant_project.id，不是项目 code。
```

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_product.id
right: tenant_interworking_project.product_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantInterworkingProjectDaoImpl.java:32
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: product
  comment: 产品id
overlap:
  probed: true
  ratio: 0.8333
  ratio_reverse: 0.125
  sample_size: 6
  miss: 1
  deepened: true
  query_ok: true
  authenticity: unknown
authenticity_note: 互通项目绑定的是互通产品主键，不是 tenant_product.id。
```

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_product.code
right: tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantInterworkingProjectApplicationService.java:67
source: l1_code
join_role: identity
priority: primary
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: tenant_interworking_project.tenant_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantInterworkingProjectDaoImpl.java:24
source: l1_code
join_role: identity
priority: primary
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config
cardinality: one_to_many
trust: disputed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config;database_profile:lowcode_pplatform.tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_setting_config
  comment: 租户项目
overlap:
  probed: true
  ratio: 0.0
  sample_size: 2
  miss: 2
  deepened: false
  query_ok: true
  authenticity: unknown
sides:
- {source: l1_code, left: tenant_setting_config.id, right: tenant_interworking_project.tenant_id,
  trust: confirmed}
- {source: name, left: tenant_setting_config.id, right: tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config,
  trust: proposed}
```

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_product.id
right: tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product
cardinality: one_to_many
trust: disputed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product;database_profile:lowcode_pplatform.tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_interworking_product
  comment: 租户产品项目
overlap:
  probed: true
  ratio: 0.0
  sample_size: 6
  miss: 6
  deepened: false
  query_ok: true
  authenticity: unlikely
sides:
- {source: l1_code, left: tenant_interworking_product.id, right: tenant_interworking_project.product_id,
  trust: confirmed}
- {source: name, left: tenant_interworking_product.id, right: tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product,
  trust: proposed}
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_interworking_project.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_interworking_project.platform_product_code;database_profile:lowcode_pplatform.tenant_interworking_project.platform_product_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品编码
overlap:
  probed: true
  ratio: 0.0
  sample_size: 5
  miss: 5
  deepened: false
  query_ok: true
  authenticity: unlikely
```

## 页面链接

### 关联表

- [[tables/tenant_project]]
- [[tables/tenant_interworking_product]]
- [[tables/tenant_setting_config]]
- [[tables/platform_product]]

### 字典

- [[dicts/tenant_interworking_project__platform_product_code]]（`tenant_interworking_project.platform_product_code`）
