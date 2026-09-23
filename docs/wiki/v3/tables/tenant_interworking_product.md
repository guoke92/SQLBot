---
type: table
title: 租户互通产品
page_key: tenant_interworking_product
belong: tables
status: draft
anchors:
- tenant_interworking_product
sources:
- database_schema:lowcode_pplatform.tenant_interworking_product
- code_path:TenantInterworkingProductDaoImpl.java:37
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_interworking_product
- platform_product
- tenant_interworking_project
- tenant_setting_config
- tenant_interworking_product__open_status
- tenant_interworking_product__max_financing_amount_flag
- tenant_interworking_product__enable
- tenant_interworking_product__product_cate
- tenant_interworking_product__scope
---
# 租户互通产品

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_interworking_product
database: lowcode_pplatform
desc: 租户互通产品
inactive: false
primary_key:
- id
grain: 一租户一互通产品一行
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
- name: platform_product_id
  type: number
  desc: 平台产品id
- name: product_cate
  type: string
  desc: 产品类型
  dict:
  - WEAKLY
  - STRONG
  - CREDIT
  label:
  - 弱确权
  - 强确权
  - 信用类
- name: tenant_id
  type: number
  desc: 租户id
- name: open_status
  type: string
  desc: 产品开通状态
  dict:
  - N
  - Y
  label:
  - 未开通
  - 已开通
- name: max_financing_amount_flag
  type: string
  desc: 是否限额融资资金上限
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: logo_icon_url
  type: string
  desc: 产品logo
- name: credit_measures
  type: string
  desc: 增信措施
- name: max_financing_period
  type: string
  desc: 融资期限上限
- name: max_financing_amount
  type: string
  desc: 融资金额上限
- name: transaction_structure
  type: string
  desc: 交易结构
- name: platform_product_code
  type: string
  desc: 平台产品编号
- name: product_summary
  type: string
  desc: 产品概述
- name: product_description
  type: string
  desc: 产品详细描述
- name: customer_group
  type: string
  desc: 客户群体
- name: target_sys_channel
  type: string
  desc: 目标系统ssochannel
- name: scope
  type: string
  desc: 适应范围标识
  dict: [ALL, SOME]
  label: [全部, 特定范围]
- name: scope_project
  type: string
  desc: 适用范围项目
- name: ref_tenant_interworking_product_platform_product
  type: string
  desc: 关联产品大类
- name: ref_tenant_interworking_product_tenant_setting_config
  type: string
  desc: 关联租户
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label:
  - 启用
  - 停用
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
- name: scope_role
  type: string
  desc: 适用角色
default_filter:
  predicate: tenant_interworking_product.enable = 'Y'
  trust: confirmed
  evidence: code_path:TenantInterworkingProductDaoImpl.java:37
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: tenant_interworking_product.platform_product_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantInterworkingProductDaoImpl.java:36
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 11
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: tenant_interworking_product.tenant_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantInterworkingProductDaoImpl.java:35
source: l1_code
join_role: identity
priority: primary
authenticity_note: 互通产品按租户配置主键。
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
left: tenant_interworking_product.platform_product_code
right: tenant_interworking_project.platform_product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;collide_refine:互通产品/项目同语义业务码；重合高
source: collide_refine
join_role: business_code
priority: primary
authenticity_note: 互通产品/项目同语义业务码；重合高
```
```ground:relation
type: EQUI_JOIN
left: platform_product.product_code
right: tenant_interworking_product.platform_product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: code+live
```
```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_interworking_product.ref_tenant_interworking_product_platform_product
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: code+live
```
```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.code
right: tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: code+live
```

## 页面链接

### 关联表

- [[tables/cust_interworking_product]]
- [[tables/platform_product]]
- [[tables/tenant_interworking_project]]
- [[tables/tenant_setting_config]]

### 概念

- [[concepts/interworking_open_term]]
- [[concepts/platform_product_code_term]]
- [[concepts/product_cate_term]]

### 字典

- [[dicts/tenant_interworking_product__product_cate]]（`tenant_interworking_product.product_cate`）
- [[dicts/tenant_interworking_product__open_status]]（`tenant_interworking_product.open_status`）
- [[dicts/tenant_interworking_product__max_financing_amount_flag]]（`tenant_interworking_product.max_financing_amount_flag`）
- [[dicts/tenant_interworking_product__scope]]（`tenant_interworking_product.scope`）
- [[dicts/tenant_interworking_product__enable]]（`tenant_interworking_product.enable`）
