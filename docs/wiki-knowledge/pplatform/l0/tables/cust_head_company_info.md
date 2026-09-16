---
type: table
title: 客户总公司信息
page_key: cust_head_company_info
belong: tables
status: draft
aliases: []
anchors:
- cust_head_company_info
sources:
- database_schema:lowcode_pplatform.cust_head_company_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户总公司信息

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### company_base

`name`, `cust_short_name`, `cust_english_name`, `cust_english_short_name`

### registration

`certification_no`, `time_permanent`, `establishment_time`, `regist_province_city`, `regist_province_city_english`, `registered_address`, `regist_province_city_english_end`

### legal

`legal_name`, `legal_phone`, `legal_certification_no`, `legal_certification_type`, `legal_time_permanent`, `legal_english_first_name`, `legal_english_sec_name`, `legal_birth_date`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### head

`head_approval_date`, `head_business_scope`

### relation

`ref_cust_head_company_info_cust_company_info`, `organization_id`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`remark`

## 字段

```ground:table
table: cust_head_company_info
database: lowcode_pplatform
description: 客户总公司信息
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- cust_short_name
- cust_english_name
- cust_english_short_name
- legal_name
- legal_english_first_name
- legal_english_sec_name
clusters:
- key: common
  title: 通用审计
  include: always
- key: company_base
  title: 企业名称
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: registration
  title: 工商注册
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: legal
  title: 法人信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: head
  title: 总公司核准
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: relation
  title: 关联与组织
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_head_company_info
- key: tenant
  title: 租户标识
  confidence: proposed
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
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 企业名称
  nullable: true
  cluster: company_base
- name: cust_short_name
  data_type: string
  description: 企业简称
  nullable: true
  cluster: company_base
- name: cust_english_name
  data_type: string
  description: 企业名称(英文)
  nullable: true
  cluster: company_base
- name: cust_english_short_name
  data_type: string
  description: 企业简称(英文)
  nullable: true
  cluster: company_base
- name: certification_no
  data_type: string
  description: 统一社会信用代码
  nullable: true
  cluster: registration
- name: time_permanent
  data_type: string
  description: 营业执照有效期
  nullable: true
  cluster: registration
- name: establishment_time
  data_type: temporal
  description: 注册日期
  nullable: true
  cluster: registration
- name: regist_province_city
  data_type: string
  description: 注册省份
  nullable: true
  cluster: registration
- name: regist_province_city_english
  data_type: string
  description: 注册省市(英文)
  nullable: true
  cluster: registration
- name: registered_address
  data_type: string
  description: 注册地址
  nullable: true
  cluster: registration
- name: legal_name
  data_type: string
  description: 法人姓名
  nullable: true
  cluster: legal
- name: legal_phone
  data_type: string
  description: 法人手机号
  nullable: true
  cluster: legal
- name: legal_certification_no
  data_type: string
  description: 法人证件号
  nullable: true
  cluster: legal
- name: legal_certification_type
  data_type: string
  description: 法人证件类型
  nullable: true
  cluster: legal
- name: legal_time_permanent
  data_type: string
  description: 法人证件有效期
  nullable: true
  cluster: legal
- name: ref_cust_head_company_info_cust_company_info
  data_type: string
  description: 客户信息和总公司信息
  nullable: true
  cluster: relation
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_head_company_info_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval
- name: organization_id
  data_type: string
  description: ''
  nullable: true
  cluster: relation
- name: legal_english_first_name
  data_type: string
  description: 法人英文姓
  nullable: true
  cluster: legal
- name: legal_english_sec_name
  data_type: string
  description: 法人英文名
  nullable: true
  cluster: legal
- name: legal_birth_date
  data_type: temporal
  description: 法人生日
  nullable: true
  cluster: legal
- name: regist_province_city_english_end
  data_type: string
  description: 注册市(英文)
  nullable: true
  cluster: registration
- name: head_approval_date
  data_type: temporal
  description: 总公司核准日期
  nullable: true
  cluster: head
- name: head_business_scope
  data_type: string
  description: 总公司经营范围
  nullable: true
  cluster: head
```
