---
type: table
title: 客户关联方信息主表
page_key: cust_shareholder_info
belong: tables
status: draft
anchors:
- cust_shareholder_info
sources:
- database_schema:lowcode_pplatform.cust_shareholder_info
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_company_info
- cust_shareholder_info__enable
- cust_shareholder_info__certification_type
- cust_shareholder_info__relation_type
---

# 客户关联方信息主表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_shareholder_info
database: lowcode_pplatform
desc: 客户关联方信息主表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
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
  desc: 关联方名称
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label: [启用, 停用]
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
- name: ref_cust_company_info
  type: string
  desc: 客户股东信息
- name: certification_type
  type: string
  desc: 证件类型
  dict:
  - CRET_ID
- name: certification_no
  type: string
  desc: 证件号码
- name: telephone
  type: string
  desc: 联系电话
- name: email
  type: string
  desc: 电子邮件
- name: fund_type
  type: string
  desc: 出资方式
- name: currency
  type: string
  desc: 出资币种
- name: fund_amount_ought
  type: string
  desc: 应出资金额
- name: fund_amount_act
  type: string
  desc: 实际出资金额
- name: fund_scale
  type: string
  desc: 出资比例（%）
- name: investment_date
  type: temporal
  desc: 投资日期
- name: relation_type
  type: string
  desc: 关联方类型
  dict:
  - LEGAL_PERSON
  - SENIOR_MANAGER
- name: main_data_id
  type: number
  desc: 主数据id
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_shareholder_info.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ApplyCompanyInfoApplication.java:190
source: l1_code
join_role: identity
priority: primary
authenticity_note: 股东按企业 code 复制/查询，不是 id。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_shareholder_info__enable]]（`cust_shareholder_info.enable`）
- [[dicts/cust_shareholder_info__certification_type]]（`cust_shareholder_info.certification_type`）
- [[dicts/cust_shareholder_info__relation_type]]（`cust_shareholder_info.relation_type`）
