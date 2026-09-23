---
type: table
title: 平台产品基础配置
page_key: platform_product
belong: tables
status: draft
anchors:
- platform_product
sources:
- database_schema:lowcode_pplatform.platform_product
- code_path:PlatformProductDaoImpl.java:76
created: '2026-09-20'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_project_rel
- funding_rule_info
- platform_product_client
- platform_product_cust_role
- tenant_interworking_product
- tenant_product
- tenant_project
- platform_product__product_type
- platform_product__platform_flag
- platform_product__multiple_project_flag
- platform_product__multiple_cust_role_flag
- platform_product__product_status
- platform_product__product_construction_status
- platform_product__max_financing_amount_flag
- platform_product__multiple_client_type
- platform_product__menu_type
- platform_product__wkfl_flag
- platform_product__enable
- platform_product__act_procinst_status
- platform_product__general_flag
- platform_product__product_cate
---
# 平台产品基础配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: platform_product
database: lowcode_pplatform
desc: 平台产品基础配置
inactive: false
primary_key:
- id
grain: 一平台产品一行
name_anchors:
- code
- name
- platform_code
- product_code
- project_code
- app_code
- default_menu_code
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
- name: product_type
  type: string
  desc: 通用产品标识
  dict:
  - INTERWORKING
  - GENERAL
  label:
  - 互通产品
  - 通用产品
- name: platform_flag
  type: string
  desc: 是否平台标识
  dict:
  - N
  - Y
  label:
  - 否
  - 是
- name: platform_code
  type: string
  desc: 平台编码
  dict:
  - XYC
  - VOUCHER
  - HTCP14
  - HTCP18
  - HTCP15
  - PPLATFORM
  - HTCP1
  - HTCP5
  - HTCP19
  - AMS
  - HTCP2
  - HTCP6
  - DRAFTQA
  - STORAGE
  - HTCP13
  - HTCP7
  - DRAFT
- name: multiple_project_flag
  type: string
  desc: 是否有多项目
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: multiple_cust_role_flag
  type: string
  desc: 是否有多企业角色
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: product_code
  type: string
  desc: 产品编码
  dict:
  - HTCP6
  - HTCP13
  - ACFLOW
  - ORDER
  - HTCP15
  - BEECREDIT
  - STORAGE
  - HTCP19
  - DRAFT
  - HTCP5
  - HTCP1
  - HTCP7
  - HTCP14
  - AMS
  - RVSFACTOR_PC
  - HTCP18
  - DEALER
  - VOUCHER
  - HTCP2
  - DRAFTQA
- name: product_cate
  type: string
  desc: 产品类型
  dict: [WEAKLY, STRONG, CREDIT]
  label: [弱确权, 强确权, 信用类]
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
- name: product_ref_num
  type: number
  desc: 引用产品的平台数
- name: product_status
  type: string
  desc: 产品状态
  dict:
  - '1'
  label:
  - 已生效
- name: product_construction_status
  type: string
  desc: 产品建设情况
  dict:
  - Y
- name: max_financing_amount_flag
  type: string
  desc: 是否限额融资资金上线
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: multiple_client_type
  type: string
  desc: 多端口类型
  dict:
  - default
  - CompanyType
- name: project_code
  type: string
  desc: 蜂搭平台项目编号
- name: app_code
  type: string
  desc: 蜂搭平台app编号
- name: basic_product
  type: string
  desc: 是否是产融底座
- name: menu_type
  type: string
  desc: 菜单展示类型(topLeft/left)
  dict:
  - left
- name: default_menu_code
  type: string
  desc: 默认菜单编号
- name: default_menu_index
  type: number
  desc: 默认菜单编号
- name: wkfl_flag
  type: string
  desc: 产品工作流启用开关
  dict:
  - Y
  - N
  label:
  - 是
  - 否
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
  dict:
  - r
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
- name: logo_icon_url
  type: string
  desc: 产品logo
- name: cust_role_combine
  type: string
  desc: 支持企业角色组合
- name: general_flag
  type: string
  desc: 通用产品标识
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: project_config
  type: string
  desc: 项目配置
default_filter:
  predicate: platform_product.enable = 'Y'
  trust: confirmed
  evidence: code_path:PlatformProductDaoImpl.java:76
```

## 关联关系

_（本页暂无保留的 EQUI_JOIN 边；已移除边见 `_raw/join_validation/removed_relations.md`。）_

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: platform_product_client.platform_product_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:PlatformProductClientDO.java:50
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
authenticity_note: 平台产品客户端配置挂 platform_product_id。
```

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
left: platform_product.code
right: tenant_project.ref_tenant_project_platform_product
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:项目 ref 存平台产品 UUID code
source: reextract_joins
join_role: business_code
priority: primary
authenticity_note: 项目 ref 存平台产品 UUID code
```

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: cust_project_rel.ref_cust_project_rel_platform_product
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
left: platform_product.product_code
right: funding_rule_info.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_hub_fk L→R=1.0
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: same_semantic+live
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
left: platform_product.product_code
right: tenant_project.platform_product_code
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
left: platform_product.product_code
right: platform_product_cust_role.product_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live_shared_domain;code contains-filter
source: orphan_repair
join_role: business_code
priority: primary
authenticity_note: 产品角色配置↔平台产品业务码
```

## 页面链接

### 关联表

- [[tables/cust_project_rel]]
- [[tables/funding_rule_info]]
- [[tables/platform_product_client]]
- [[tables/platform_product_cust_role]]
- [[tables/tenant_interworking_product]]
- [[tables/tenant_product]]
- [[tables/tenant_project]]

### 概念

- [[concepts/platform_product_code_term]]
- [[concepts/platform_product_master]]
- [[concepts/product_cate_term]]

### 字典

- [[dicts/platform_product__product_type]]（`platform_product.product_type`）
- [[dicts/platform_product__platform_flag]]（`platform_product.platform_flag`）
- [[dicts/platform_product__platform_code]]（`platform_product.platform_code`）
- [[dicts/platform_product__multiple_project_flag]]（`platform_product.multiple_project_flag`）
- [[dicts/platform_product__multiple_cust_role_flag]]（`platform_product.multiple_cust_role_flag`）
- [[dicts/platform_product__product_code]]（`platform_product.product_code`）
- [[dicts/platform_product__product_cate]]（`platform_product.product_cate`）
- [[dicts/platform_product__product_status]]（`platform_product.product_status`）
- [[dicts/platform_product__product_construction_status]]（`platform_product.product_construction_status`）
- [[dicts/platform_product__max_financing_amount_flag]]（`platform_product.max_financing_amount_flag`）
- [[dicts/platform_product__multiple_client_type]]（`platform_product.multiple_client_type`）
- [[dicts/platform_product__menu_type]]（`platform_product.menu_type`）
- [[dicts/platform_product__wkfl_flag]]（`platform_product.wkfl_flag`）
- [[dicts/platform_product__enable]]（`platform_product.enable`）
- [[dicts/platform_product__act_procinst_status]]（`platform_product.act_procinst_status`）
- [[dicts/platform_product__general_flag]]（`platform_product.general_flag`）
