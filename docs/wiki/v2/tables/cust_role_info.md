---
type: table
title: 客户产品角色关联表
page_key: cust_role_info
belong: tables
status: draft
anchors: [cust_role_info]
sources: ['database_schema:lowcode_pplatform.cust_role_info']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_auth_application, cust_role_info__enable, cust_role_info__status,
  cust_role_info__role_type]
---

# 客户产品角色关联表

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: cust_role_info
database: lowcode_pplatform
desc: 客户产品角色关联表
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
- name: status
  type: string
  desc: 状态
  dict: [ADD, EFFECT, WRITEOFF, FREEZE]
- name: platform_cust_id
  type: number
  desc: 关联平台企业ID
- name: ref_cust_company_info
  type: string
  desc: 客户类型
- name: ref_cust_auth_application
  type: string
  desc: 应用客户角色
- name: role_type
  type: string
  desc: 角色类型
  dict: [SUPPLIER, CORE, FINANCE, PROJECT_COMPANY, CORPORATION_COMPANY, PLATFORM_OPERATOR_COMPANY,
    DEALER, CORE_MANAGER, FACTOR_COMPANY, '"SUPPLIER"', '"CORE"', CORE_ADMIN, CORE_SUB]
- name: main_data_id
  type: number
  desc: 主数据id
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: cust_auth_application.id
right: cust_role_info.ref_cust_auth_application
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.cust_role_info.ref_cust_auth_application;database_profile:lowcode_pplatform.cust_role_info.ref_cust_auth_application
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_auth_application
  comment: 应用客户角色
overlap:
  probed: true
  ratio: 0.0
  sample_size: 1
  miss: 1
  deepened: false
  query_ok: true
  authenticity: unknown
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_role_info.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_role_info.ref_cust_company_info;database_profile:lowcode_pplatform.cust_role_info.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
  comment: 客户类型
overlap:
  probed: true
  ratio: 0.0
  sample_size: 200
  miss: 200
  deepened: false
  query_ok: true
  authenticity: unlikely
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_auth_application]]

### 字典

- [[dicts/cust_role_info__enable]]（`cust_role_info.enable`）
- [[dicts/cust_role_info__status]]（`cust_role_info.status`）
- [[dicts/cust_role_info__role_type]]（`cust_role_info.role_type`）
