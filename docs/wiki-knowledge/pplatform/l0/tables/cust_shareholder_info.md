---
type: table
title: 客户关联方信息主表
page_key: cust_shareholder_info
belong: tables
status: draft
aliases: []
anchors:
- cust_shareholder_info
sources:
- database_schema:lowcode_pplatform.cust_shareholder_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户关联方信息主表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### shareholder_identity

`name`, `certification_type`, `certification_no`, `relation_type`

### contact

`telephone`, `email`

### fund

`fund_type`, `currency`, `fund_amount_ought`, `fund_amount_act`, `fund_scale`, `investment_date`

### reference

`organization_id`, `ref_cust_company_info`, `main_data_id`

### 未归簇

`remark`

## 字段

```ground:table
table: cust_shareholder_info
database: lowcode_pplatform
description: 客户关联方信息主表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用字段
  include: always
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: shareholder_identity
  title: 关联方身份
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: contact
  title: 联系方式
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: fund
  title: 出资信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: reference
  title: 机构与关联引用
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
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
  description: 关联方名称
  nullable: true
  cluster: shareholder_identity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_shareholder_info_enable
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
  description: 机构编号
  nullable: true
  cluster: reference
- name: ref_cust_company_info
  data_type: string
  description: 客户股东信息
  nullable: true
  cluster: reference
- name: certification_type
  data_type: string
  description: 证件类型
  nullable: true
  cluster: shareholder_identity
  dictionary: cust_shareholder_info_certification_type
- name: certification_no
  data_type: string
  description: 证件号码
  nullable: true
  cluster: shareholder_identity
- name: telephone
  data_type: string
  description: 联系电话
  nullable: true
  cluster: contact
- name: email
  data_type: string
  description: 电子邮件
  nullable: true
  cluster: contact
- name: fund_type
  data_type: string
  description: 出资方式
  nullable: true
  cluster: fund
- name: currency
  data_type: string
  description: 出资币种
  nullable: true
  cluster: fund
- name: fund_amount_ought
  data_type: string
  description: 应出资金额
  nullable: true
  cluster: fund
- name: fund_amount_act
  data_type: string
  description: 实际出资金额
  nullable: true
  cluster: fund
- name: fund_scale
  data_type: string
  description: 出资比例（%）
  nullable: true
  cluster: fund
- name: investment_date
  data_type: temporal
  description: 投资日期
  nullable: true
  cluster: fund
- name: relation_type
  data_type: string
  description: 关联方类型
  nullable: true
  cluster: shareholder_identity
  dictionary: cust_shareholder_info_relation_type
- name: main_data_id
  data_type: number
  description: 主数据id
  nullable: true
  cluster: reference
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_shareholder_info.ref_cust_company_info
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_shareholder_info.ref_cust_company_info
```
