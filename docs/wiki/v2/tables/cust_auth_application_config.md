---
type: table
title: 客户产品开通配置
page_key: cust_auth_application_config
belong: tables
status: draft
anchors: [cust_auth_application_config]
sources: ['database_schema:lowcode_pplatform.cust_auth_application_config']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_auth_application]
---

# 客户产品开通配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_config

`product_sign_mode`, `product_protocol_agreement`, `needs_company_type_configuration`, `needs_product_agreement_configuration`

### relation

`cust_id`, `ref_cust_auth_application_config_cust_auth_application`, `organization_id`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### audit

（空）

## 字段

```ground:table
table: cust_auth_application_config
database: lowcode_pplatform
description: 客户产品开通配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: product_config
  title: 产品开通配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
- key: relation
  title: 关联主体
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
- key: audit
  title: 审计
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: cust_id
  data_type: number
  description: 企业id
  cluster: relation
- name: product_sign_mode
  data_type: string
  description: 产品协议签署方式
  cluster: product_config
- name: product_protocol_agreement
  data_type: string
  description: 产品协议
  cluster: product_config
- name: needs_company_type_configuration
  data_type: string
  description: 是否区分企业
  cluster: product_config
- name: needs_product_agreement_configuration
  data_type: string
  description: 是否需要产品协议
  cluster: product_config
- name: ref_cust_auth_application_config_cust_auth_application
  data_type: string
  description: 客户产品开通
  cluster: relation
- name: enable
  data_type: string
  description: enable
  cluster: common
- name: remark
  data_type: string
  description: remark
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  cluster: act_procinst
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: act_procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: act_procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: act_procinst
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: relation
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
authenticity_note: name_evidence=family_hub(stem=cust, comment=企业id)，列名/注释与 cust_company_info
  主档语义相符；overlap 已探测但 ratio/ratio_reverse 均为 null、sample_size=0，值域契合无证据，故不给 likely
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
authenticity_note: name_evidence=long_ref(stem=cust_auth_application)，列名由父表名拼接而来且注释「客户产品开通」一致；overlap
  已探测但 ratio/ratio_reverse 均为 null、sample_size=0，无值域证据，故不给 likely
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_auth_application]]
