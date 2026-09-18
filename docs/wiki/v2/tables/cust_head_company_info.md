---
type: table
title: 客户总公司信息
page_key: cust_head_company_info
belong: tables
status: draft
anchors: [cust_head_company_info]
sources: ['database_schema:lowcode_pplatform.cust_head_company_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_head_company_info__legal_certification_type, cust_head_company_info__enable]
---

# 客户总公司信息

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### cust_profile

`name`, `cust_short_name`, `cust_english_name`, `cust_english_short_name`

### cert

`certification_no`, `time_permanent`, `establishment_time`

### regist

`regist_province_city`, `regist_province_city_english`, `registered_address`, `regist_province_city_english_end`

### legal

`legal_name`, `legal_phone`, `legal_certification_no`, `legal_certification_type`, `legal_time_permanent`, `legal_english_first_name`, `legal_english_sec_name`, `legal_birth_date`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### head

`head_approval_date`, `head_business_scope`

### tenant

`app_tenant_code`, `db_tenant_code`

### ref_link

`ref_cust_head_company_info_cust_company_info`, `organization_id`

## 字段

```ground:table
table: cust_head_company_info
database: lowcode_pplatform
description: 客户总公司信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, cust_short_name, cust_english_name, cust_english_short_name,
  legal_name, legal_english_first_name, legal_english_sec_name]
clusters:
- key: common
  title: 通用
  include: always
- key: cust_profile
  title: 企业名称
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: cert
  title: 证照登记
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: regist
  title: 注册信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: legal
  title: 法人信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: head
  title: 总公司核准
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: ref_link
  title: 关联标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
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
  description: 企业名称
  cluster: cust_profile
- name: cust_short_name
  data_type: string
  description: 企业简称
  cluster: cust_profile
- name: cust_english_name
  data_type: string
  description: 企业名称(英文)
  cluster: cust_profile
- name: cust_english_short_name
  data_type: string
  description: 企业简称(英文)
  cluster: cust_profile
- name: certification_no
  data_type: string
  description: 统一社会信用代码
  cluster: cert
- name: time_permanent
  data_type: string
  description: 营业执照有效期
  cluster: cert
- name: establishment_time
  data_type: temporal
  description: 注册日期
  cluster: cert
- name: regist_province_city
  data_type: string
  description: 注册省份
  cluster: regist
- name: regist_province_city_english
  data_type: string
  description: 注册省市(英文)
  cluster: regist
- name: registered_address
  data_type: string
  description: 注册地址
  cluster: regist
- name: legal_name
  data_type: string
  description: 法人姓名
  cluster: legal
- name: legal_phone
  data_type: string
  description: 法人手机号
  cluster: legal
- name: legal_certification_no
  data_type: string
  description: 法人证件号
  cluster: legal
- name: legal_certification_type
  data_type: string
  description: 法人证件类型
  cluster: legal
  dictionary: cust_head_company_info__legal_certification_type
- name: legal_time_permanent
  data_type: string
  description: 法人证件有效期
  cluster: legal
- name: ref_cust_head_company_info_cust_company_info
  data_type: string
  description: 客户信息和总公司信息
  cluster: ref_link
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_head_company_info__enable
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
  cluster: ref_link
- name: legal_english_first_name
  data_type: string
  description: 法人英文姓
  cluster: legal
- name: legal_english_sec_name
  data_type: string
  description: 法人英文名
  cluster: legal
- name: legal_birth_date
  data_type: temporal
  description: 法人生日
  cluster: legal
- name: regist_province_city_english_end
  data_type: string
  description: 注册市(英文)
  cluster: regist
- name: head_approval_date
  data_type: temporal
  description: 总公司核准日期
  cluster: head
- name: head_business_scope
  data_type: string
  description: 总公司经营范围
  cluster: head
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_head_company_info.ref_cust_head_company_info_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_head_company_info.ref_cust_head_company_info_cust_company_info;database_profile:lowcode_pplatform.cust_head_company_info.ref_cust_head_company_info_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: cust_company_info
  comment: 客户信息和总公司信息
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

### 字典

- [[dicts/cust_head_company_info__legal_certification_type]]（`cust_head_company_info.legal_certification_type`）
- [[dicts/cust_head_company_info__enable]]（`cust_head_company_info.enable`）
