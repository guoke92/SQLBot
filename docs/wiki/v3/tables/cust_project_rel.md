---
type: table
title: 客户项目关联表
page_key: cust_project_rel
belong: tables
status: draft
anchors:
- cust_project_rel
sources:
- database_schema:lowcode_pplatform.cust_project_rel
- code_path:CustCompanyQueryMapper.xml:97
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_company_info
- platform_product
- tenant_product
- tenant_project
- wec_project_cust_operation_rel
- cust_project_rel__company_type
- cust_project_rel__enable
- cust_project_rel__show_flag
- cust_project_rel__status
- cust_project_rel__project_open_status
---
# 客户项目关联表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_project_rel
database: lowcode_pplatform
desc: 客户项目关联表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- channel_code
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
  dict:
  - SUPPLIER
  - CORE
  - FINANCE
  - PROJECT_COMPANY
  - CORPORATION_COMPANY
  - PLATFORM_OPERATOR_COMPANY
  - DEALER
  - CORE_MANAGER
  - PLATFORM_OPREATOR_COMPANY
- name: ref_cust_project_rel_cust_company_info
  type: string
  desc: 客户和项目关系
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
  dict:
  - RVSFACTOR_PC
  - ACFLOW
  - ORDER
  - BEECREDIT
  - DRAFTQA
  - STORAGE
  - DRAFT
  - AMS
  - VOUCHER
  - DEALER
  - RVSFACTOR
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
  dict:
  - Y
  - N
  label: [是, 否]
- name: config_model
  type: string
  desc: 项目配置模式
- name: status
  type: string
  desc: 关联状态
  dict:
  - '1'
  - '0'
  label: [是, 否]
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
- name: op_update_user
  type: string
  desc: 运营信息更新人
- name: op_update_time
  type: temporal
  desc: 运营信息更新时间
- name: project_open_status
  type: string
  desc: 项目开通状态
  dict:
  - NOT_OPEN
  - OPENED
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
left: tenant_project.channel_code
right: cust_project_rel.channel_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: code:copy
```


## 关联说明（非 EQUI / 对等场景）

- 与 `wec_project_cust_operation_rel` 为产融 / 讯易链**对等「项目-企业运营关系」**；字段可对照，ID 空间不同。

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/platform_product]]
- [[tables/tenant_product]]
- [[tables/tenant_project]]
- [[tables/wec_project_cust_operation_rel]]

### 概念

- [[concepts/channel_code_homonym_bundle]]
- [[concepts/channel_code_term]]
- [[concepts/project_rel_status]]

### 字典

- [[dicts/cust_project_rel__company_type]]（`cust_project_rel.company_type`）
- [[dicts/cust_project_rel__enable]]（`cust_project_rel.enable`）
- [[dicts/cust_project_rel__remark]]（`cust_project_rel.remark`）
- [[dicts/cust_project_rel__show_flag]]（`cust_project_rel.show_flag`）
- [[dicts/cust_project_rel__status]]（`cust_project_rel.status`）
- [[dicts/cust_project_rel__project_open_status]]（`cust_project_rel.project_open_status`）
