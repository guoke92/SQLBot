---
type: table
title: 企业互通产品
page_key: cust_interworking_product
belong: tables
status: draft
anchors: [cust_interworking_product]
sources: ['database_schema:lowcode_pplatform.cust_interworking_product']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, platform_product, cust_customized_product, tenant_interworking_product,
  cust_interworking_product__open_status, cust_interworking_product__platform_product_code,
  cust_interworking_product__agree_authorization_flag, cust_interworking_product__ref_cust_interworking_product_tenant_interworking_product,
  cust_interworking_product__enable, cust_interworking_product__app_tenant_code, cust_interworking_product__db_tenant_code]
---

# 企业互通产品

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`name`, `platform_product_code`, `product_id`

### open

`open_status`, `open_time`, `open_user`

### agree

`agree_authorization_flag`, `agree_authorization_time`

### relations

`cust_id`, `tenant_id`, `ref_cust_interworking_product_cust_company_info`, `ref_cust_interworking_product_tenant_interworking_product`, `app_tenant_code`, `db_tenant_code`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`organization_id`

## 字段

```ground:table
table: cust_interworking_product
database: lowcode_pplatform
description: 企业互通产品
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 产品标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
- key: open
  title: 开通信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
- key: agree
  title: 授权信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
- key: relations
  title: 企业/租户关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_interworking_product
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
  cluster: identity
- name: open_status
  data_type: string
  description: 开通状态
  cluster: open
  dictionary: cust_interworking_product__open_status
- name: cust_id
  data_type: number
  description: 企业id
  cluster: relations
- name: open_time
  data_type: temporal
  description: 开通时间
  cluster: open
- name: open_user
  data_type: number
  description: 开通人
  cluster: open
- name: platform_product_code
  data_type: string
  description: 平台产品编码
  cluster: identity
  dictionary: cust_interworking_product__platform_product_code
- name: agree_authorization_flag
  data_type: string
  description: 是否同意授权
  cluster: agree
  dictionary: cust_interworking_product__agree_authorization_flag
- name: agree_authorization_time
  data_type: temporal
  description: 同意授权时间
  cluster: agree
- name: product_id
  data_type: number
  description: 互通产品id
  cluster: identity
- name: tenant_id
  data_type: number
  description: 租户id
  cluster: relations
- name: ref_cust_interworking_product_cust_company_info
  data_type: string
  description: 关联企业
  cluster: relations
- name: ref_cust_interworking_product_tenant_interworking_product
  data_type: string
  description: 关联互通产品
  cluster: relations
  dictionary: cust_interworking_product__ref_cust_interworking_product_tenant_interworking_product
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_interworking_product__enable
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
  cluster: relations
  dictionary: cust_interworking_product__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: relations
  dictionary: cust_interworking_product__db_tenant_code
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
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_interworking_product.cust_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_interworking_product.cust_id;database_profile:lowcode_pplatform.cust_interworking_product.cust_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业id
overlap:
  probed: true
  ratio: 0.9948
  sample_size: 194
  miss: 1
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: left=cust_company_info.id；名称族匹配且重叠 0.9948，企业ID关联可信。
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: cust_interworking_product.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_interworking_product.platform_product_code;database_profile:lowcode_pplatform.cust_interworking_product.platform_product_code
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
  sample_size: 4
  miss: 4
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: left=platform_product.code；名称精确匹配但探测零重叠（4/4 miss），暂判不成立，待补样本。
```

```ground:relation
type: EQUI_JOIN
left: cust_customized_product.id
right: cust_interworking_product.product_id
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_interworking_product.product_id;database_profile:lowcode_pplatform.cust_interworking_product.product_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: product
  comment: 互通产品id
overlap:
  probed: true
  ratio: 0.0
  sample_size: 14
  miss: 14
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: left=cust_customized_product.id；名称弱匹配且零重叠（14/14 miss），可能非同一产品实体。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_interworking_product.ref_cust_interworking_product_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_interworking_product.ref_cust_interworking_product_cust_company_info;database_profile:lowcode_pplatform.cust_interworking_product.ref_cust_interworking_product_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: cust_company_info
  comment: 关联企业
overlap:
  probed: true
  ratio: 0.005
  sample_size: 200
  miss: 199
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: left=cust_company_info.id；长引用名指向企业，但重叠仅 0.005（200 样本），引用格式/类型可能不一致。
```

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_product.id
right: cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product;database_profile:lowcode_pplatform.cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_interworking_product
  comment: 关联互通产品
overlap:
  probed: true
  ratio: 0.0
  sample_size: 14
  miss: 14
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: left=tenant_interworking_product.id；长引用名指向互通产品，但零重叠（14/14 miss），可能引用非该父表主键或格式不匹配。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/platform_product]]
- [[tables/cust_customized_product]]
- [[tables/tenant_interworking_product]]

### 字典

- [[dicts/cust_interworking_product__open_status]]（`cust_interworking_product.open_status`）
- [[dicts/cust_interworking_product__platform_product_code]]（`cust_interworking_product.platform_product_code`）
- [[dicts/cust_interworking_product__agree_authorization_flag]]（`cust_interworking_product.agree_authorization_flag`）
- [[dicts/cust_interworking_product__ref_cust_interworking_product_tenant_interworking_product]]（`cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product`）
- [[dicts/cust_interworking_product__enable]]（`cust_interworking_product.enable`）
- [[dicts/cust_interworking_product__app_tenant_code]]（`cust_interworking_product.app_tenant_code`）
- [[dicts/cust_interworking_product__db_tenant_code]]（`cust_interworking_product.db_tenant_code`）
