---
type: table
title: 租户产品配置
page_key: tenant_product
belong: tables
status: draft
anchors: [tenant_product]
sources: ['database_schema:lowcode_pplatform.tenant_product', 'code_path:TenantProductDaoImpl.java:43']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_auth_application, platform_product, tenant_setting_config, tenant_product_menu,
  tenant_product_menu_res, tenant_project, tenant_project_approval_business_info,
  tenant_product__product_cate, tenant_product__open_status, tenant_product__max_financing_amount_flag,
  tenant_product__platform_product_code, tenant_product__is_migratory, tenant_product__enable,
  tenant_product__multiple]
---

# 租户产品配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_product
database: lowcode_pplatform
desc: 租户产品配置
inactive: false
primary_key: [id]
grain: 一租户一平台产品一行
name_anchors: [code, name, ref_tenant_product_project_code]
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
  dict: [STRONG, WEAKLY, CREDIT]
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
  dict: [Y, N, P]
  label: [已开通, 未开通, 开通中]
- name: max_financing_amount_flag
  type: string
  desc: 是否限额融资资金上线
  dict: [N, Y, '0', '1']
- name: platform_product_code
  type: string
  desc: 平台产品编号
  dict: [ACFLOW, RVSFACTOR_PC, ORDER, BEECREDIT, VOUCHER, DRAFTQA, STORAGE, DRAFT]
- name: product_web_url
  type: string
  desc: 站点url
- name: is_migratory
  type: string
  desc: 是否迁移标识,N代表未迁移,Y代表迁移
  dict: [N, Y]
  label: [未迁移, 迁移]
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
- name: multiple
  type: string
  desc: 是否多个
  dict: ['0']
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

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: tenant_product.ref_tenant_product_tenant_setting_config
cardinality: one_to_many
trust: disputed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_product.ref_tenant_product_tenant_setting_config;database_profile:lowcode_pplatform.tenant_product.ref_tenant_product_tenant_setting_config
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: tenant_setting_config
  comment: 租户-产品
overlap:
  probed: true
  ratio: 0.0061
  sample_size: 165
  miss: 164
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 长引用名指向 tenant_setting_config.id，但 overlap=0.0061（165 样本仅 1 命中），值域不契合，判
  unlikely。
sides:
- {source: l1_code, left: tenant_setting_config.id, right: tenant_product.tenant_id,
  trust: confirmed}
- {source: name, left: tenant_setting_config.id, right: tenant_product.ref_tenant_product_tenant_setting_config,
  trust: proposed}
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: tenant_product.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_product.platform_product_code;database_profile:lowcode_pplatform.tenant_product.platform_product_code
source: name
join_role: business_code
priority: secondary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品编号
overlap:
  probed: true
  ratio: 0.0
  sample_size: 8
  miss: 8
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 列名与注释有关联语义，但探测 overlap=0.0（8 样本全部未命中），值域不契合，判 unlikely，保留待人工复核。
```

## 页面链接

### 关联表

- [[tables/cust_auth_application]]
- [[tables/platform_product]]
- [[tables/tenant_setting_config]]
- [[tables/tenant_product_menu]]
- [[tables/tenant_product_menu_res]]
- [[tables/tenant_project]]
- [[tables/tenant_project_approval_business_info]]

### 字典

- [[dicts/tenant_product__product_cate]]（`tenant_product.product_cate`）
- [[dicts/tenant_product__open_status]]（`tenant_product.open_status`）
- [[dicts/tenant_product__max_financing_amount_flag]]（`tenant_product.max_financing_amount_flag`）
- [[dicts/tenant_product__platform_product_code]]（`tenant_product.platform_product_code`）
- [[dicts/tenant_product__is_migratory]]（`tenant_product.is_migratory`）
- [[dicts/tenant_product__enable]]（`tenant_product.enable`）
- [[dicts/tenant_product__multiple]]（`tenant_product.multiple`）
