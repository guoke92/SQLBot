---
type: table
title: 客户项目关联表
page_key: cust_project_rel
belong: tables
status: draft
anchors: [cust_project_rel]
sources: ['database_schema:lowcode_pplatform.cust_project_rel', 'code_path:CustCompanyQueryMapper.xml:97']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_customized_product, cust_company_info, platform_product, tenant_project,
  cust_project_rel__company_type, cust_project_rel__enable, cust_project_rel__show_flag,
  cust_project_rel__config_model, cust_project_rel__status, cust_project_rel__top_flag,
  cust_project_rel__project_open_status]
---

# 客户项目关联表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_project_rel
database: lowcode_pplatform
desc: 客户项目关联表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, channel_code]
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
- name: project_id
  type: string
  desc: 项目id
- name: tenant_code
  type: string
  desc: 租户
- name: product_id
  type: string
  desc: 产品
- name: channel_code
  type: string
  desc: 渠道码
- name: company_type
  type: string
  desc: 客户角色(只取一个)
  dict: [SUPPLIER, CORE, FINANCE, PROJECT_COMPANY, CORPORATION_COMPANY, PLATFORM_OPERATOR_COMPANY,
    DEALER, CORE_MANAGER, PLATFORM_OPREATOR_COMPANY]
- name: ref_cust_project_rel_cust_company_info
  type: string
  desc: 客户和项目关系
- name: enable
  type: string
  desc: enable
  dict: [Y, N]
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
- name: show_flag
  type: string
  desc: 展示标记
  dict: [Y, N]
- name: config_model
  type: string
  desc: 项目配置模式
  dict: [admin]
- name: status
  type: string
  desc: 关联状态
  dict: ['1', '0']
- name: ref_cust_project_rel_platform_product
  type: string
  desc: 平台产品
- name: tenant_flg_en
  type: string
  desc: 项目标识（英文）
- name: op_contact_a
  type: string
  desc: 运营对接人A
- name: op_contact_b
  type: string
  desc: 运营对接人B
- name: op_contact_a_group
  type: string
  desc: 运营组别
- name: verification_contact
  type: string
  desc: 查验对接人
- name: verification_contact_group
  type: string
  desc: 查验组别
- name: risk_control_contact_a
  type: string
  desc: 风控对接人A
- name: risk_control_contact_b
  type: string
  desc: 风控对接人B
- name: risk_control_contact_a_group
  type: string
  desc: 风控组别
- name: top_flag
  type: string
  desc: 置顶标识
  dict: ['0', '1']
- name: op_update_user
  type: string
  desc: 运营信息更新人
- name: op_update_time
  type: temporal
  desc: 运营信息更新时间
- name: project_open_status
  type: string
  desc: 项目开通状态
  dict: [NOT_OPEN, OPENED]
default_filter:
  predicate: cust_project_rel.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustCompanyQueryMapper.xml:97
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_project_rel.ref_cust_project_rel_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyQueryMapper.xml:97
source: l1_code
join_role: identity
priority: primary
authenticity_note: 代码按企业 code 关联项目，不是 cust_company_info.id。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project.id
right: cust_project_rel.project_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyQueryMapper.xml:137
source: l1_code
join_role: identity
priority: primary
authenticity_note: XML 等值 cpl.project_id = tp.id；库列 varchar(512) 对 bigint 主键，Java
  常把 Long 当字符串存。
cast: varchar←bigint
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_project_rel.ref_cust_project_rel_cust_company_info
cardinality: one_to_many
trust: disputed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_project_rel.ref_cust_project_rel_cust_company_info;database_profile:lowcode_pplatform.cust_project_rel.ref_cust_project_rel_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: cust_company_info
  comment: 客户和项目关系
overlap:
  probed: true
  ratio: 0.01
  sample_size: 200
  miss: 198
  deepened: false
  query_ok: true
  authenticity: unlikely
sides:
- {source: l1_code, left: cust_company_info.code, right: cust_project_rel.ref_cust_project_rel_cust_company_info,
  trust: confirmed}
- {source: name, left: cust_company_info.id, right: cust_project_rel.ref_cust_project_rel_cust_company_info,
  trust: proposed}
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_customized_product.id
right: cust_project_rel.product_id
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_project_rel.product_id;database_profile:lowcode_pplatform.cust_project_rel.product_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: product
  comment: 产品
overlap:
  probed: true
  ratio: 0.0
  sample_size: 15
  miss: 15
  deepened: false
  query_ok: true
  authenticity: unlikely
```

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: cust_project_rel.ref_cust_project_rel_platform_product
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_project_rel.ref_cust_project_rel_platform_product;database_profile:lowcode_pplatform.cust_project_rel.ref_cust_project_rel_platform_product
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: platform_product
  comment: 平台产品
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

- [[tables/cust_customized_product]]
- [[tables/cust_company_info]]
- [[tables/platform_product]]
- [[tables/tenant_project]]

### 字典

- [[dicts/cust_project_rel__company_type]]（`cust_project_rel.company_type`）
- [[dicts/cust_project_rel__enable]]（`cust_project_rel.enable`）
- [[dicts/cust_project_rel__show_flag]]（`cust_project_rel.show_flag`）
- [[dicts/cust_project_rel__config_model]]（`cust_project_rel.config_model`）
- [[dicts/cust_project_rel__status]]（`cust_project_rel.status`）
- [[dicts/cust_project_rel__top_flag]]（`cust_project_rel.top_flag`）
- [[dicts/cust_project_rel__project_open_status]]（`cust_project_rel.project_open_status`）
