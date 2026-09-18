---
type: table
title: 租户互通产品项目
page_key: tenant_interworking_project
belong: tables
status: draft
anchors: [tenant_interworking_project]
sources: ['database_schema:lowcode_pplatform.tenant_interworking_project']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_interworking_product, platform_product, tenant_project, tenant_setting_config,
  tenant_product, tenant_interworking_project__code, tenant_interworking_project__tenant_id,
  tenant_interworking_project__platform_product_code, tenant_interworking_project__ref_tenant_interworking_project_tenant_setting_config,
  tenant_interworking_project__ref_tenant_interworking_project_tenant_interworking_product,
  tenant_interworking_project__enable, tenant_interworking_project__app_tenant_code,
  tenant_interworking_project__db_tenant_code]
---

# 租户互通产品项目

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`name`

### product

`product_id`, `platform_product_code`

### tenant_org

`tenant_id`, `app_tenant_code`, `db_tenant_code`, `organization_id`

### project_ref

`project_id`, `ref_tenant_interworking_project_tenant_setting_config`, `ref_tenant_interworking_project_tenant_interworking_product`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: tenant_interworking_project
database: lowcode_pplatform
description: 租户互通产品项目
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 身份标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_project
- key: product
  title: 产品
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_project
- key: tenant_org
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_project
- key: project_ref
  title: 项目关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_project
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_interworking_project
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
  dictionary: tenant_interworking_project__code
- name: name
  data_type: string
  description: 名称
  cluster: identity
- name: product_id
  data_type: number
  description: 产品id
  cluster: product
- name: tenant_id
  data_type: number
  description: 租户id
  cluster: tenant_org
  dictionary: tenant_interworking_project__tenant_id
- name: platform_product_code
  data_type: string
  description: 平台产品编码
  cluster: product
  dictionary: tenant_interworking_project__platform_product_code
- name: project_id
  data_type: number
  description: 项目id
  cluster: project_ref
- name: ref_tenant_interworking_project_tenant_setting_config
  data_type: string
  description: 租户项目
  cluster: project_ref
  dictionary: tenant_interworking_project__ref_tenant_interworking_project_tenant_setting_config
- name: ref_tenant_interworking_project_tenant_interworking_product
  data_type: string
  description: 租户产品项目
  cluster: project_ref
  dictionary: tenant_interworking_project__ref_tenant_interworking_project_tenant_interworking_product
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: tenant_interworking_project__enable
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
  cluster: tenant_org
  dictionary: tenant_interworking_project__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_org
  dictionary: tenant_interworking_project__db_tenant_code
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
  cluster: tenant_org
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_product.id
right: tenant_interworking_project.product_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.tenant_interworking_project.product_id;database_profile:lowcode_pplatform.tenant_interworking_project.product_id
source: name
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
authenticity_note: tenant_interworking_product.id 对 product_id，名称族后缀匹配，正向覆盖率 0.8333，判
  likely。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project.id
right: tenant_interworking_project.project_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.tenant_interworking_project.project_id;database_profile:lowcode_pplatform.tenant_interworking_project.project_id
source: name
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
authenticity_note: tenant_project.id 对 project_id，名称族后缀匹配，覆盖率 1.0，判 likely。
```

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config
cardinality: one_to_many
trust: proposed
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
authenticity_note: tenant_setting_config.id 对长引用，名称指向租户配置，但样本重叠 0，判 unknown。
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
authenticity_note: platform_product.code 对 platform_product_code，名称匹配但实测重叠 0，判 unlikely。
```

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_product.id
right: tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product
cardinality: one_to_many
trust: proposed
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
authenticity_note: tenant_interworking_product.id 对长引用，名称指向租户产品，但重叠 0，判 unlikely。
```

## 页面链接

### 关联表

- [[tables/tenant_interworking_product]]
- [[tables/platform_product]]
- [[tables/tenant_project]]
- [[tables/tenant_setting_config]]
- [[tables/tenant_product]]

### 字典

- [[dicts/tenant_interworking_project__code]]（`tenant_interworking_project.code`）
- [[dicts/tenant_interworking_project__tenant_id]]（`tenant_interworking_project.tenant_id`）
- [[dicts/tenant_interworking_project__platform_product_code]]（`tenant_interworking_project.platform_product_code`）
- [[dicts/tenant_interworking_project__ref_tenant_interworking_project_tenant_setting_config]]（`tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config`）
- [[dicts/tenant_interworking_project__ref_tenant_interworking_project_tenant_interworking_product]]（`tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product`）
- [[dicts/tenant_interworking_project__enable]]（`tenant_interworking_project.enable`）
- [[dicts/tenant_interworking_project__app_tenant_code]]（`tenant_interworking_project.app_tenant_code`）
- [[dicts/tenant_interworking_project__db_tenant_code]]（`tenant_interworking_project.db_tenant_code`）
