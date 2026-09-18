---
type: table
title: 授权确认书表
page_key: authorization_agreement
belong: tables
status: draft
anchors: [authorization_agreement]
sources: ['database_schema:lowcode_pplatform.authorization_agreement']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, authorization_agreement__platform_product_code, authorization_agreement__authed_status,
  authorization_agreement__company_type, authorization_agreement__enable, authorization_agreement__creation_type]
---

# 授权确认书表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `creation_type`

### cust

`cust_manager_id`, `cust_id`, `original_cust_id`, `company_type`, `cust_manager_name`, `cust_name`, `organization_id`

### auth

`platform_product_code`, `authed_status`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: authorization_agreement
database: lowcode_pplatform
description: 授权确认书表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, cust_manager_name, cust_name]
clusters:
- key: common
  title: 通用
  include: always
- key: cust
  title: 企业客户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.authorization_agreement
- key: auth
  title: 授权要素
  trust: proposed
  evidence: database_schema:lowcode_pplatform.authorization_agreement
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.authorization_agreement
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.authorization_agreement
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
- name: cust_manager_id
  data_type: number
  description: 企业管理员id
  cluster: cust
- name: platform_product_code
  data_type: string
  description: 平台产品id
  cluster: auth
  dictionary: authorization_agreement__platform_product_code
- name: authed_status
  data_type: string
  description: 授权书认证状态
  cluster: auth
  dictionary: authorization_agreement__authed_status
- name: cust_id
  data_type: number
  description: 企业id
  cluster: cust
- name: original_cust_id
  data_type: string
  description: 源系统custid
  cluster: cust
- name: company_type
  data_type: string
  description: 企业角色
  cluster: cust
  dictionary: authorization_agreement__company_type
- name: cust_manager_name
  data_type: string
  description: 客户管理员名称
  cluster: cust
- name: cust_name
  data_type: string
  description: 企业名称
  cluster: cust
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: authorization_agreement__enable
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
  cluster: cust
- name: creation_type
  data_type: string
  description: 创建类型
  cluster: common
  dictionary: authorization_agreement__creation_type
```

## 关联关系

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

### 字典

- [[dicts/authorization_agreement__platform_product_code]]（`authorization_agreement.platform_product_code`）
- [[dicts/authorization_agreement__authed_status]]（`authorization_agreement.authed_status`）
- [[dicts/authorization_agreement__company_type]]（`authorization_agreement.company_type`）
- [[dicts/authorization_agreement__enable]]（`authorization_agreement.enable`）
- [[dicts/authorization_agreement__creation_type]]（`authorization_agreement.creation_type`）
