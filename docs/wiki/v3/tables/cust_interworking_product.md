---
type: table
title: 企业互通产品
page_key: cust_interworking_product
belong: tables
status: draft
anchors:
- cust_interworking_product
sources:
- database_schema:lowcode_pplatform.cust_interworking_product
- code_path:CustInterworkingProductDaoImpl.java:48
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_company_info
- tenant_interworking_product
- tenant_setting_config
- cust_interworking_product__open_status
- cust_interworking_product__agree_authorization_flag
- cust_interworking_product__enable
---
# 企业互通产品

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_interworking_product
database: lowcode_pplatform
desc: 企业互通产品
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
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
  dict:
  - OPENED
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
- name: agree_authorization_flag
  type: string
  desc: 是否同意授权
  dict:
  - N
  - Y
  label: [否, 是]
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
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label: [启用, 停用]
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
trust: confirmed
authenticity: likely
evidence: code_path:CustInterworkingProductDaoImpl.java:74
source: l1_code
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
authenticity_note: 企业互通产品按 cust_id=企业主键查询（与 ref_* 存 code 的双轨并存）。
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

```ground:relation
type: EQUI_JOIN
left: tenant_interworking_product.code
right: cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:互通产品 code→ref
source: reextract_joins
join_role: business_code
priority: primary
authenticity_note: 互通产品 code→ref
```
```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: cust_interworking_product.tenant_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:企业互通产品租户
source: reextract_joins
join_role: identity
priority: primary
authenticity_note: 企业互通产品租户
```

```ground:relation
type: EQUI_JOIN
left: cust_interworking_product.platform_product_code
right: tenant_interworking_product.platform_product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:shared_domain;collide_refine:企业互通与租户互通产品业务码；重合高可连
source: collide_refine
join_role: business_code
priority: primary
authenticity_note: 企业互通与租户互通产品业务码；重合高可连
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/tenant_interworking_product]]
- [[tables/tenant_setting_config]]

### 概念

- [[concepts/platform_product_code_term]]

### 字典

- [[dicts/cust_interworking_product__open_status]]（`cust_interworking_product.open_status`）
- [[dicts/cust_interworking_product__agree_authorization_flag]]（`cust_interworking_product.agree_authorization_flag`）
- [[dicts/cust_interworking_product__enable]]（`cust_interworking_product.enable`）
