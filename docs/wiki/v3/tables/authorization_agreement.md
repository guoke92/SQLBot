---
type: table
title: 授权确认书表
page_key: authorization_agreement
belong: tables
status: draft
anchors: [authorization_agreement]
sources: ['database_schema:lowcode_pplatform.authorization_agreement', 'code_path:AuthorizationAgreementDaoImpl.java:44']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, cust_company_info, authorization_agreement__platform_product_code,
  authorization_agreement__authed_status, authorization_agreement__company_type, authorization_agreement__enable,
  authorization_agreement__creation_type]
---

# 授权确认书表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: authorization_agreement
database: lowcode_pplatform
desc: 授权确认书表
inactive: false
primary_key: [id]
grain: 企业授权确认书
name_anchors: [code, name, cust_manager_name, cust_name]
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
- name: cust_manager_id
  type: number
  desc: 企业管理员id
- name: platform_product_code
  type: string
  desc: 平台产品id
  dict: [PLATFORM, ACFLOW, RVSFACTOR_PC, ORDER, AMS, STORAGE, BEECREDIT, VOUCHER,
    pplatform, RVSFACTOR]
- name: authed_status
  type: string
  desc: 授权书认证状态
  dict: [N, Y]
- name: cust_id
  type: number
  desc: 企业id
- name: original_cust_id
  type: string
  desc: 源系统custid
- name: company_type
  type: string
  desc: 企业角色
  dict: [SUPPLIER, CORE, FINANCE, PROJECT_COMPANY, PLATFORM_OPERATOR_COMPANY, PLATFORM_OPREATOR_COMPANY,
    CORPORATION_COMPANY, DEALER, CORE_MANAGER, '["CORE"]', '["FINANCE"]', '["PROJECT_COMPANY"]',
    FACTOR_COMPANY]
- name: cust_manager_name
  type: string
  desc: 客户管理员名称
- name: cust_name
  type: string
  desc: 企业名称
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
- name: creation_type
  type: string
  desc: 创建类型
  dict: [CUST_BUILD_INIT, AUTO, COMPANY_MANAGER_CHANGE_CODE]
default_filter:
  predicate: authorization_agreement.enable = 'Y'
  trust: confirmed
  evidence: code_path:AuthorizationAgreementDaoImpl.java:44
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: authorization_agreement.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:AuthorizationAgreementDaoImpl.java:43
source: l1_code
join_role: identity
priority: primary
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: platform_product.code
right: authorization_agreement.platform_product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.authorization_agreement.platform_product_code;database_profile:lowcode_pplatform.authorization_agreement.platform_product_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品id
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

- [[tables/platform_product]]
- [[tables/cust_company_info]]

### 字典

- [[dicts/authorization_agreement__platform_product_code]]（`authorization_agreement.platform_product_code`）
- [[dicts/authorization_agreement__authed_status]]（`authorization_agreement.authed_status`）
- [[dicts/authorization_agreement__company_type]]（`authorization_agreement.company_type`）
- [[dicts/authorization_agreement__enable]]（`authorization_agreement.enable`）
- [[dicts/authorization_agreement__creation_type]]（`authorization_agreement.creation_type`）
