---
type: table
title: 企业互通产品
page_key: cust_interworking_product
belong: tables
status: draft
anchors: [cust_interworking_product]
sources: ['database_schema:lowcode_pplatform.cust_interworking_product', 'code_path:CustInterworkingProductDaoImpl.java:48']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, platform_product, cust_customized_product, tenant_interworking_product,
  cust_interworking_product__open_status, cust_interworking_product__platform_product_code,
  cust_interworking_product__agree_authorization_flag, cust_interworking_product__ref_cust_interworking_product_tenant_interworking_product,
  cust_interworking_product__enable]
---

# 企业互通产品

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_interworking_product
database: lowcode_pplatform
desc: 企业互通产品
inactive: false
primary_key: [id]
grain: 一行一记录（id）
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
- name: open_status
  type: string
  desc: 开通状态
  dict: [OPENED]
- name: cust_id
  type: number
  desc: 企业id
- name: open_time
  type: temporal
  desc: 开通时间
- name: open_user
  type: number
  desc: 开通人
- name: platform_product_code
  type: string
  desc: 平台产品编码
  dict: [HTCP1, HTCP2, HTCP13, HTCP14, AMS, HTCP5]
- name: agree_authorization_flag
  type: string
  desc: 是否同意授权
  dict: [N]
- name: agree_authorization_time
  type: temporal
  desc: 同意授权时间
- name: product_id
  type: number
  desc: 互通产品id
- name: tenant_id
  type: number
  desc: 租户id
- name: ref_cust_interworking_product_cust_company_info
  type: string
  desc: 关联企业
- name: ref_cust_interworking_product_tenant_interworking_product
  type: string
  desc: 关联互通产品
  dict: [29b4c489bccc4c0f90293b7d22f3ea74, 7d2e4e19006c45d99eba5700ce8d2404, b3770dfd357549058a0ec1344f5144e4,
    d75957823c444de690d1c2036bb9e844, 5afb2d5a0ac241f395f9dfc9436b7a93, 9d205a2ef8624dd8bdda73e449180cb4,
    72ee7278ef6641d2a034d977fd9c7c3a, f97f8fc6672e4465a461170b682a85aa, 4264a4d3ef144caf851983a844b15a9d,
    e43f564036794cfb92a92b0a31098fe1, 14ef19ef031a4b0f9e97223ec1235d0c, a5095d15ebed4eee9a8900bb3d98258f,
    af0c15eee0bc41a8b3fa39079ea44a97, f5a6ba16bde247da8005652037051571, 4932eca2392d45f8821aba513f379c7f,
    10947e5d6b9c4ea09ef94c5a80624336, ccf30c163d794060bba0450b455b796c, 2dbc124f73dd4e9eb96cc74685b17645,
    11050e432dab4b24b9adbff8644ea5a2, 87a6136555544df2adf6295bdd75956f, d6a784c151cf4f8d9ffe8302bd03cbd2,
    0f93f67a813b4fd79134f46e65017cc2]
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
default_filter:
  predicate: cust_interworking_product.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustInterworkingProductDaoImpl.java:48
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

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
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_interworking_product.ref_cust_interworking_product_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustInterworkingProductDaoImpl.java:47
source: l1_code
join_role: identity
priority: primary
authenticity_note: 互通产品按企业 code 关联。listCustAllProduct 先 getById 再取 code；不要把 cust_id
  当成这条查询的 JOIN。
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_interworking_product.ref_cust_interworking_product_cust_company_info
cardinality: one_to_many
trust: disputed
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
sides:
- {source: l1_code, left: cust_company_info.code, right: cust_interworking_product.ref_cust_interworking_product_cust_company_info,
  trust: confirmed}
- {source: name, left: cust_company_info.id, right: cust_interworking_product.ref_cust_interworking_product_cust_company_info,
  trust: proposed}
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
