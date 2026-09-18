---
type: table
title: 客户银行账号信息主表
page_key: cust_account_info
belong: tables
status: draft
anchors: [cust_account_info]
sources: ['database_schema:lowcode_pplatform.cust_account_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_account_info__enable, cust_account_info__default_account_flag,
  cust_account_info__account_type, cust_account_info__status, cust_account_info__auth_state,
  cust_account_info__bank_id]
---

# 客户银行账号信息主表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### account

`account_no`, `default_account_flag`, `account_type`, `receive_payment_type`, `account_name`, `status`, `auth_state`

### bank

`bank_no`, `bank_province_name`, `bank_province_code`, `bank_city_name`, `bank_city_code`, `bank_code`, `bank_code_name`, `bank_branch_name`, `bank_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### contact

`address`, `telephone`, `email`

### payment_monitor

`trans_id`, `error_try_count`, `error_try_time`, `trace_no`, `payment_remaining_count`

### org

`organization_id`, `ref_cust_company_info`, `main_data_id`

## 字段

```ground:table
table: cust_account_info
database: lowcode_pplatform
description: 客户银行账号信息主表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, account_name, bank_province_name, bank_province_code, bank_city_name,
  bank_city_code, bank_code, bank_code_name, bank_branch_name]
clusters:
- key: common
  title: 通用
  include: always
- key: account
  title: 账户信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: bank
  title: 银行信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: contact
  title: 联系信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: payment_monitor
  title: 打款与交易监控
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_account_info
- key: org
  title: 机构与主数据
  trust: proposed
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
  cluster: common
- name: name
  data_type: string
  description: 名称-废弃
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_account_info__enable
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
  cluster: workflow
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
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: org
- name: account_no
  data_type: string
  description: 账户账号
  cluster: account
- name: default_account_flag
  data_type: string
  description: 是否为默认账户
  cluster: account
  dictionary: cust_account_info__default_account_flag
- name: account_type
  data_type: string
  description: 账户类型
  cluster: account
  dictionary: cust_account_info__account_type
- name: receive_payment_type
  data_type: string
  description: 收付类型
  cluster: account
- name: account_name
  data_type: string
  description: 账户名称
  cluster: account
- name: bank_no
  data_type: string
  description: 联行号
  cluster: bank
- name: bank_province_name
  data_type: string
  description: 银行所属省份名称
  cluster: bank
- name: bank_province_code
  data_type: string
  description: 银行所属省份代码
  cluster: bank
- name: bank_city_name
  data_type: string
  description: 银行城市名称
  cluster: bank
- name: bank_city_code
  data_type: string
  description: 银行城市代码
  cluster: bank
- name: bank_code
  data_type: string
  description: 银行(总行)代码
  cluster: bank
- name: bank_code_name
  data_type: string
  description: 银行(总行)名称
  cluster: bank
- name: bank_branch_name
  data_type: string
  description: 账户开户行
  cluster: bank
- name: address
  data_type: string
  description: 地址
  cluster: contact
- name: telephone
  data_type: string
  description: 电话
  cluster: contact
- name: status
  data_type: string
  description: 账户状态
  cluster: account
  dictionary: cust_account_info__status
- name: email
  data_type: string
  description: 电子邮箱
  cluster: contact
- name: trans_id
  data_type: string
  description: 交易ID
  cluster: payment_monitor
- name: error_try_count
  data_type: number
  description: 打款金额错误次数
  cluster: payment_monitor
- name: error_try_time
  data_type: temporal
  description: 最后一次错误时间
  cluster: payment_monitor
- name: auth_state
  data_type: string
  description: 认证状态
  cluster: account
  dictionary: cust_account_info__auth_state
- name: trace_no
  data_type: string
  description: 系统跟踪号
  cluster: payment_monitor
- name: payment_remaining_count
  data_type: number
  description: 剩余打款次数
  cluster: payment_monitor
- name: ref_cust_company_info
  data_type: string
  description: 客户账号信息
  cluster: org
- name: main_data_id
  data_type: number
  description: 主数据id
  cluster: org
- name: bank_id
  data_type: string
  description: 银行ID
  cluster: bank
  dictionary: cust_account_info__bank_id
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_account_info.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_account_info.ref_cust_company_info;database_profile:lowcode_pplatform.cust_account_info.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
  comment: 客户账号信息
overlap:
  probed: true
  ratio: 0.0
  sample_size: 200
  miss: 200
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 列名 stem 与左表精确同名，但重叠率 0.0（probed，sample 200，miss 200），本列注释「客户账号信息」亦为自指语义，不足以支撑外键，判
  unlikely。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_account_info__enable]]（`cust_account_info.enable`）
- [[dicts/cust_account_info__default_account_flag]]（`cust_account_info.default_account_flag`）
- [[dicts/cust_account_info__account_type]]（`cust_account_info.account_type`）
- [[dicts/cust_account_info__status]]（`cust_account_info.status`）
- [[dicts/cust_account_info__auth_state]]（`cust_account_info.auth_state`）
- [[dicts/cust_account_info__bank_id]]（`cust_account_info.bank_id`）
