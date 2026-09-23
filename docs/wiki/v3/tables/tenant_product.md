---
type: table
title: 租户产品配置
page_key: tenant_product
belong: tables
status: draft
anchors:
- tenant_product
sources:
- database_schema:lowcode_pplatform.tenant_product
- code_path:TenantProductDaoImpl.java:43
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- authorization_agreement
- cust_auth_application
- cust_project_rel
- platform_product
- platform_product_cust_role
- tenant_project
- tenant_setting_config
- tenant_product__open_status
- tenant_product__max_financing_amount_flag
- tenant_product__is_migratory
- tenant_product__enable
- tenant_product__multiple
- tenant_product__product_cate
---
# 租户产品配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_product
database: lowcode_pplatform
desc: 租户产品配置
inactive: false
primary_key:
- id
grain: 一租户一平台产品一行
name_anchors:
- code
- name
- ref_tenant_product_project_code
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
  - STRONG
  - WEAKLY
  - CREDIT
  label:
  - 强确权
  - 弱确权
  - 信用类
- name: product_summary
  type: string
  desc: 产品概述
- name: product_description
  type: string
  desc: 产品详细描述
- name: customer_group
  type: string
  desc: 客户群体
- name: max_financing_period
  type: string
  desc: 融资期限上限
- name: max_financing_amount
  type: string
  desc: 融资金额上限
- name: credit_measures
  type: string
  desc: 增信措施
- name: transaction_structure
  type: string
  desc: 交易结构
- name: product_agreement
  type: string
  desc: 产品协议
- name: tenant_id
  type: number
  desc: 租户id
- name: open_status
  type: string
  desc: 产品开通状态
  dict:
  - Y
  - N
  - P
  label:
  - 已开通
  - 未开通
  - 开通中
- name: max_financing_amount_flag
  type: string
  desc: 是否限额融资资金上线
  dict:
  - N
  - Y
  - '0'
  - '1'
  label:
  - 否
  - 是
  - 否
  - 是
- name: platform_product_code
  type: string
  desc: 平台产品编号
- name: product_web_url
  type: string
  desc: 站点url
- name: is_migratory
  type: string
  desc: 是否迁移标识,N代表未迁移,Y代表迁移
  dict:
  - N
  - Y
  label:
    N: 未迁移
    Y: 迁移
- name: logo_icon_url
  type: string
  desc: 产品logo
- name: view_order
  type: number
  desc: 展示顺序
- name: ref_tenant_product_tenant_setting_config
  type: string
  desc: 租户-产品
- name: ref_tenant_product_project_code
  type: string
  desc: 租户产品-平台产品
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
- name: multiple
  type: string
  desc: 是否多个
  dict:
  - '0'
  - '1'
  label:
  - 否
  - 是
default_filter:
  predicate: tenant_product.enable = 'Y'
  trust: confirmed
  evidence: code_path:TenantProductDaoImpl.java:43
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: tenant_product.platform_product_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantProductDaoImpl.java:42
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
  sample_size: 8
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 租户产品对平台产品主键。
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: tenant_product.tenant_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantProductDomainService.java:147
source: l1_code
join_role: identity
priority: primary
authenticity_note: 开通产品写 tenant_id=TenantDTO.id（即 tenant_setting_config.id）。
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.code
right: tenant_product.ref_tenant_product_tenant_setting_config
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantProductDomainService.java:161
source: l1_code
join_role: identity
priority: primary
authenticity_note: 码引用租户配置 code，与 tenant_id 并存。
```
```ground:relation
type: EQUI_JOIN
left: authorization_agreement.platform_product_code
right: tenant_product.platform_product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;collide_refine:授权书与租户产品业务码；fk_like
source: collide_refine
join_role: business_code
priority: primary
authenticity_note: 授权书与租户产品业务码；fk_like
```
```ground:relation
type: EQUI_JOIN
left: cust_auth_application.platform_product_code
right: tenant_product.platform_product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;collide_refine:开通申请与租户产品业务码；fk_like
source: collide_refine
join_role: business_code
priority: primary
authenticity_note: 开通申请与租户产品业务码；fk_like
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.id
right: tenant_project.product_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantProjectDaoImpl.java:34
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: product
  comment: 产品编码
overlap:
  probed: true
  ratio: 1.0
  sample_size: 79
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 项目按租户产品主键关联。
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.code
right: tenant_project.ref_tenant_project_product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:TenantProjectDaoImpl.java:136
source: l1_code
join_role: identity
priority: primary
authenticity_note: 码引用租户产品 code。
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.platform_product_code
right: tenant_project.platform_product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;collide_refine:同语义产品业务码；父子场景重合高
source: collide_refine
join_role: business_code
priority: primary
authenticity_note: 同语义产品业务码；父子场景重合高
```
```ground:relation
type: EQUI_JOIN
left: platform_product.product_code
right: tenant_product.platform_product_code
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
right: tenant_product.ref_tenant_product_project_code
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
left: tenant_product.code
right: cust_auth_application.ref_cust_auth_application_tenant_product
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
left: tenant_product.id
right: cust_project_rel.product_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like
source: full_sweep
join_role: identity
priority: primary
authenticity_note: code+live
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.platform_product_code
right: platform_product_cust_role.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live_shared_domain L→R=1;user code filter
source: orphan_repair
join_role: business_code
priority: primary
authenticity_note: 内存 contains 同值域可 EQUI
```

## 页面链接

### 关联表

- [[tables/authorization_agreement]]
- [[tables/cust_auth_application]]
- [[tables/cust_project_rel]]
- [[tables/platform_product]]
- [[tables/platform_product_cust_role]]
- [[tables/tenant_project]]
- [[tables/tenant_setting_config]]

### 概念

- [[concepts/open_tenant_product_term]]
- [[concepts/platform_product_code_term]]
- [[concepts/product_cate_term]]

### 字典

- [[dicts/tenant_product__product_cate]]（`tenant_product.product_cate`）
- [[dicts/tenant_product__open_status]]（`tenant_product.open_status`）
- [[dicts/tenant_product__max_financing_amount_flag]]（`tenant_product.max_financing_amount_flag`）
- [[dicts/tenant_product__is_migratory]]（`tenant_product.is_migratory`）
- [[dicts/tenant_product__enable]]（`tenant_product.enable`）
- [[dicts/tenant_product__multiple]]（`tenant_product.multiple`）
