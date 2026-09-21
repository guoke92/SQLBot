---
type: table
title: 客户银行账号信息主表
page_key: cust_account_info
belong: tables
status: draft
anchors: [cust_account_info]
sources: ['database_schema:lowcode_pplatform.cust_account_info']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_account_info__name, cust_account_info__enable, cust_account_info__default_account_flag,
  cust_account_info__account_type, cust_account_info__status, cust_account_info__error_try_count,
  cust_account_info__auth_state, cust_account_info__payment_remaining_count, cust_account_info__bank_id]
---

# 客户银行账号信息主表

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: cust_account_info
database: lowcode_pplatform
desc: 客户银行账号信息主表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, account_name, bank_province_name, bank_province_code, bank_city_name,
  bank_city_code, bank_code, bank_code_name, bank_branch_name]
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
  desc: 名称-废弃
  dict: [测试账户, '111', '324234']
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
- name: account_no
  type: string
  desc: 账户账号
- name: default_account_flag
  type: string
  desc: 是否为默认账户
  dict: ['0', '1']
- name: account_type
  type: string
  desc: 账户类型
  dict: [BANK, OPERATION_FEE_ACCOUNT, '1', received]
- name: receive_payment_type
  type: string
  desc: 收付类型
- name: account_name
  type: string
  desc: 账户名称
- name: bank_no
  type: string
  desc: 联行号
- name: bank_province_name
  type: string
  desc: 银行所属省份名称
- name: bank_province_code
  type: string
  desc: 银行所属省份代码
- name: bank_city_name
  type: string
  desc: 银行城市名称
- name: bank_city_code
  type: string
  desc: 银行城市代码
- name: bank_code
  type: string
  desc: 银行(总行)代码
- name: bank_code_name
  type: string
  desc: 银行(总行)名称
- name: bank_branch_name
  type: string
  desc: 账户开户行
- name: address
  type: string
  desc: 地址
- name: telephone
  type: string
  desc: 电话
- name: status
  type: string
  desc: 账户状态
  dict: [INIT]
- name: email
  type: string
  desc: 电子邮箱
- name: trans_id
  type: string
  desc: 交易ID
- name: error_try_count
  type: number
  desc: 打款金额错误次数
  dict: ['0']
- name: error_try_time
  type: temporal
  desc: 最后一次错误时间
- name: auth_state
  type: string
  desc: 认证状态
  dict: [APPLY_00, APPLY_40, APPLY_20]
- name: trace_no
  type: string
  desc: 系统跟踪号
- name: payment_remaining_count
  type: number
  desc: 剩余打款次数
  dict: ['3', '5', '2', '0', '1']
- name: ref_cust_company_info
  type: string
  desc: 客户账号信息
- name: main_data_id
  type: number
  desc: 主数据id
- name: bank_id
  type: string
  desc: 银行ID
  dict: ['103', '302', '102', '105']
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
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_account_info__name]]（`cust_account_info.name`）
- [[dicts/cust_account_info__enable]]（`cust_account_info.enable`）
- [[dicts/cust_account_info__default_account_flag]]（`cust_account_info.default_account_flag`）
- [[dicts/cust_account_info__account_type]]（`cust_account_info.account_type`）
- [[dicts/cust_account_info__status]]（`cust_account_info.status`）
- [[dicts/cust_account_info__error_try_count]]（`cust_account_info.error_try_count`）
- [[dicts/cust_account_info__auth_state]]（`cust_account_info.auth_state`）
- [[dicts/cust_account_info__payment_remaining_count]]（`cust_account_info.payment_remaining_count`）
- [[dicts/cust_account_info__bank_id]]（`cust_account_info.bank_id`）
