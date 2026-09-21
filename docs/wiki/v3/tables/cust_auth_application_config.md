---
type: table
title: 客户产品开通配置
page_key: cust_auth_application_config
belong: tables
status: draft
anchors: [cust_auth_application_config]
sources: ['database_schema:lowcode_pplatform.cust_auth_application_config']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_auth_application]
---

# 客户产品开通配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_auth_application_config
database: lowcode_pplatform
desc: 客户产品开通配置
inactive: false
primary_key: [id]
grain: 客户产品开通配置（现网 0 行；pplatform-web 无 DO / 业务引用）
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
- name: cust_id
  type: number
  desc: 企业id
- name: product_sign_mode
  type: string
  desc: 产品协议签署方式
- name: product_protocol_agreement
  type: string
  desc: 产品协议
- name: needs_company_type_configuration
  type: string
  desc: 是否区分企业
- name: needs_product_agreement_configuration
  type: string
  desc: 是否需要产品协议
- name: ref_cust_auth_application_config_cust_auth_application
  type: string
  desc: 客户产品开通
- name: enable
  type: string
  desc: enable
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
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_auth_application_config.cust_id
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.cust_auth_application_config.cust_id;database_profile:lowcode_pplatform.cust_auth_application_config.cust_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业id
overlap:
  probed: true
  sample_size: 0
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
```

```ground:relation
type: EQUI_JOIN
left: cust_auth_application.id
right: cust_auth_application_config.ref_cust_auth_application_config_cust_auth_application
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.cust_auth_application_config.ref_cust_auth_application_config_cust_auth_application;database_profile:lowcode_pplatform.cust_auth_application_config.ref_cust_auth_application_config_cust_auth_application
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: cust_auth_application
  comment: 客户产品开通
overlap:
  probed: true
  sample_size: 0
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_auth_application]]
