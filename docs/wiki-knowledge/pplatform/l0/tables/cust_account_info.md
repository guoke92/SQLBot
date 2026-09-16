---
type: table
title: 客户银行账号信息主表
page_key: cust_account_info
belong: tables
status: draft
aliases: []
anchors:
- cust_account_info
sources:
- database_schema:lowcode_pplatform.cust_account_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户银行账号信息主表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### identity

`name`, `organization_id`, `ref_cust_company_info`, `main_data_id`

### account

`account_no`, `default_account_flag`, `account_type`, `receive_payment_type`, `account_name`, `status`, `auth_state`

### bank

`bank_no`, `bank_province_name`, `bank_province_code`, `bank_city_name`, `bank_city_code`, `bank_code`, `bank_code_name`, `bank_branch_name`, `bank_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### payment

`trans_id`, `error_try_count`, `error_try_time`, `trace_no`, `payment_remaining_count`

### contact

`address`, `telephone`, `email`

### 未归簇

`remark`

## 字段

```ground:table
table: cust_account_info
database: lowcode_pplatform
description: 客户银行账号信息主表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- account_name
- bank_province_name
- bank_province_code
- bank_city_name
- bank_city_code
- bank_code
- bank_code_name
- bank_branch_name
clusters:
- key: common
  title: 通用（主键/编码/启用/审计时间戳）
  include: always
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: identity
  title: 客户主体与主数据
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: account
  title: 账户信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: bank
  title: 银行信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: payment
  title: 打款与交易跟踪
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: contact
  title: 联系方式与地址
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
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
  description: 名称-废弃
  nullable: true
  cluster: identity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_account_info_enable
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
  cluster: workflow
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
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: identity
- name: account_no
  data_type: string
  description: 账户账号
  nullable: true
  cluster: account
- name: default_account_flag
  data_type: string
  description: 是否为默认账户
  nullable: true
  cluster: account
  dictionary: cust_account_info_default_account_flag
- name: account_type
  data_type: string
  description: 账户类型
  nullable: true
  cluster: account
  dictionary: cust_account_info_account_type
- name: receive_payment_type
  data_type: string
  description: 收付类型
  nullable: true
  cluster: account
- name: account_name
  data_type: string
  description: 账户名称
  nullable: true
  cluster: account
- name: bank_no
  data_type: string
  description: 联行号
  nullable: true
  cluster: bank
- name: bank_province_name
  data_type: string
  description: 银行所属省份名称
  nullable: true
  cluster: bank
- name: bank_province_code
  data_type: string
  description: 银行所属省份代码
  nullable: true
  cluster: bank
- name: bank_city_name
  data_type: string
  description: 银行城市名称
  nullable: true
  cluster: bank
- name: bank_city_code
  data_type: string
  description: 银行城市代码
  nullable: true
  cluster: bank
- name: bank_code
  data_type: string
  description: 银行(总行)代码
  nullable: true
  cluster: bank
- name: bank_code_name
  data_type: string
  description: 银行(总行)名称
  nullable: true
  cluster: bank
- name: bank_branch_name
  data_type: string
  description: 账户开户行
  nullable: true
  cluster: bank
- name: address
  data_type: string
  description: 地址
  nullable: true
  cluster: contact
- name: telephone
  data_type: string
  description: 电话
  nullable: true
  cluster: contact
- name: status
  data_type: string
  description: 账户状态
  nullable: true
  cluster: account
  dictionary: cust_account_info_status
- name: email
  data_type: string
  description: 电子邮箱
  nullable: true
  cluster: contact
- name: trans_id
  data_type: string
  description: 交易ID
  nullable: true
  cluster: payment
- name: error_try_count
  data_type: number
  description: 打款金额错误次数
  nullable: true
  cluster: payment
- name: error_try_time
  data_type: temporal
  description: 最后一次错误时间
  nullable: true
  cluster: payment
- name: auth_state
  data_type: string
  description: 认证状态
  nullable: true
  cluster: account
  dictionary: cust_account_info_auth_state
- name: trace_no
  data_type: string
  description: 系统跟踪号
  nullable: true
  cluster: payment
- name: payment_remaining_count
  data_type: number
  description: 剩余打款次数
  nullable: true
  cluster: payment
- name: ref_cust_company_info
  data_type: string
  description: 客户账号信息
  nullable: true
  cluster: identity
- name: main_data_id
  data_type: number
  description: 主数据id
  nullable: true
  cluster: identity
- name: bank_id
  data_type: string
  description: 银行ID
  nullable: true
  cluster: bank
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_account_info.ref_cust_company_info
cardinality: one_to_many
confidence: proposed
evidence: database_schema:lowcode_pplatform.cust_account_info.ref_cust_company_info
```
