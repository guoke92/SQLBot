---
type: table
title: 客户产品角色关联表
page_key: cust_role_info
belong: tables
status: draft
anchors: [cust_role_info]
sources: ['database_schema:lowcode_pplatform.cust_role_info', 'code_path:CustCompanyQueryMapper.xml:82']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_auth_application, cust_company_info, cust_role_info__enable, cust_role_info__status,
  cust_role_info__role_type]
---

# 客户产品角色关联表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

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
  label: [未激活, 已激活, 注销, 冻结]
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
    DEALER, CORE_MANAGER, FACTOR_COMPANY, '"SUPPLIER"', '"CORE"', CORE_ADMIN, CORE_SUB,
    CORE_FUNCTIONAL_DEPARTMENT, CORE_BRANCH, PLATFORM_COMPANY]
  label: {SUPPLIER: 供应商, CORE: 核心企业, FINANCE: 金融机构, PROJECT_COMPANY: 项目公司, CORPORATION_COMPANY: 集团公司,
    PLATFORM_OPERATOR_COMPANY: 平台运营方, DEALER: 经销商, CORE_MANAGER: 核心企业管理机构, FACTOR_COMPANY: 保理买卖方,
    CORE_SUB: 核心企业子公司, CORE_FUNCTIONAL_DEPARTMENT: 核心企业职能部门, CORE_BRANCH: 核心企业分公司,
    PLATFORM_COMPANY: 平台方}
- name: main_data_id
  type: number
  desc: 主数据id
default_filter:
  predicate: cust_role_info.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustCompanyQueryMapper.xml:82
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_role_info.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyQueryMapper.xml:80
source: l1_code
join_role: identity
priority: primary
authenticity_note: listEffectCompanyByCustType 以 code 连接角色表。
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_role_info.ref_cust_company_info
cardinality: one_to_many
trust: disputed
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
authenticity_note: name_evidence 仅为表名精确匹配（ref_cust_company_info ≈ cust_company_info），但本地注释为「客户类型」，与指向企业主档表的语义不符；overlap
  已探测 200 条全 miss（ratio=0.0），值域不契合，判 unlikely。
sides:
- {source: l1_code, left: cust_company_info.code, right: cust_role_info.ref_cust_company_info,
  trust: confirmed}
- {source: name, left: cust_company_info.id, right: cust_role_info.ref_cust_company_info,
  trust: proposed}
```

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
authenticity_note: 表名精确匹配且本地注释「应用客户角色」与目标表（客户产品开通表）语义相关，但 overlap 仅探测 1 条样本且 ratio=0.0，样本量不足不能作为否定或肯定依据，维持
  unknown。
```

## 页面链接

### 关联表

- [[tables/cust_auth_application]]
- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_role_info__enable]]（`cust_role_info.enable`）
- [[dicts/cust_role_info__status]]（`cust_role_info.status`）
- [[dicts/cust_role_info__role_type]]（`cust_role_info.role_type`）
