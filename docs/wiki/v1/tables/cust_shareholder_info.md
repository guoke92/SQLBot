---
type: table
title: 客户关联方信息主表
page_key: cust_shareholder_info
belong: tables
status: draft
anchors: [cust_shareholder_info]
sources: ['database_schema:lowcode_pplatform.cust_shareholder_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_shareholder_info__code, cust_shareholder_info__name,
  cust_shareholder_info__enable, cust_shareholder_info__remark, cust_shareholder_info__app_tenant_code,
  cust_shareholder_info__db_tenant_code, cust_shareholder_info__ref_cust_company_info,
  cust_shareholder_info__certification_type, cust_shareholder_info__certification_no,
  cust_shareholder_info__email, cust_shareholder_info__fund_amount_act, cust_shareholder_info__fund_scale,
  cust_shareholder_info__relation_type]
---

# 客户关联方信息主表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### tenant

`app_tenant_code`, `db_tenant_code`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### shareholder

`name`, `certification_type`, `certification_no`, `telephone`, `email`, `relation_type`

### fund

`fund_type`, `currency`, `fund_amount_ought`, `fund_amount_act`, `fund_scale`, `investment_date`

### reference

`organization_id`, `ref_cust_company_info`, `main_data_id`

## 字段

```ground:table
table: cust_shareholder_info
database: lowcode_pplatform
description: 客户关联方信息主表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: shareholder
  title: 关联方身份
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: fund
  title: 出资信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_shareholder_info
- key: reference
  title: 归属与引用
  trust: proposed
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
  cluster: common
  dictionary: cust_shareholder_info__code
- name: name
  data_type: string
  description: 关联方名称
  cluster: shareholder
  dictionary: cust_shareholder_info__name
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_shareholder_info__enable
- name: remark
  data_type: string
  description: remark
  cluster: common
  dictionary: cust_shareholder_info__remark
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
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
  dictionary: cust_shareholder_info__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: cust_shareholder_info__db_tenant_code
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: reference
- name: ref_cust_company_info
  data_type: string
  description: 客户股东信息
  cluster: reference
  dictionary: cust_shareholder_info__ref_cust_company_info
- name: certification_type
  data_type: string
  description: 证件类型
  cluster: shareholder
  dictionary: cust_shareholder_info__certification_type
- name: certification_no
  data_type: string
  description: 证件号码
  cluster: shareholder
  dictionary: cust_shareholder_info__certification_no
- name: telephone
  data_type: string
  description: 联系电话
  cluster: shareholder
- name: email
  data_type: string
  description: 电子邮件
  cluster: shareholder
  dictionary: cust_shareholder_info__email
- name: fund_type
  data_type: string
  description: 出资方式
  cluster: fund
- name: currency
  data_type: string
  description: 出资币种
  cluster: fund
- name: fund_amount_ought
  data_type: string
  description: 应出资金额
  cluster: fund
- name: fund_amount_act
  data_type: string
  description: 实际出资金额
  cluster: fund
  dictionary: cust_shareholder_info__fund_amount_act
- name: fund_scale
  data_type: string
  description: 出资比例（%）
  cluster: fund
  dictionary: cust_shareholder_info__fund_scale
- name: investment_date
  data_type: temporal
  description: 投资日期
  cluster: fund
- name: relation_type
  data_type: string
  description: 关联方类型
  cluster: shareholder
  dictionary: cust_shareholder_info__relation_type
- name: main_data_id
  data_type: number
  description: 主数据id
  cluster: reference
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_shareholder_info.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_shareholder_info.ref_cust_company_info;database_profile:lowcode_pplatform.cust_shareholder_info.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
  comment: 客户股东信息
overlap:
  probed: true
  ratio: 0.0
  sample_size: 5
  miss: 5
  deepened: false
  query_ok: true
  authenticity: unlikely
authenticity_note: 名称证据 exact_table 命中父表 cust_company_info，与注释「客户股东信息」语义相符；但探测重叠率
  0.0（5/5 miss，sample_size=5，未深化），样本过小不足以最终否定，暂判 unlikely，建议人工复核数据是否对齐。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_shareholder_info__code]]（`cust_shareholder_info.code`）
- [[dicts/cust_shareholder_info__name]]（`cust_shareholder_info.name`）
- [[dicts/cust_shareholder_info__enable]]（`cust_shareholder_info.enable`）
- [[dicts/cust_shareholder_info__remark]]（`cust_shareholder_info.remark`）
- [[dicts/cust_shareholder_info__app_tenant_code]]（`cust_shareholder_info.app_tenant_code`）
- [[dicts/cust_shareholder_info__db_tenant_code]]（`cust_shareholder_info.db_tenant_code`）
- [[dicts/cust_shareholder_info__ref_cust_company_info]]（`cust_shareholder_info.ref_cust_company_info`）
- [[dicts/cust_shareholder_info__certification_type]]（`cust_shareholder_info.certification_type`）
- [[dicts/cust_shareholder_info__certification_no]]（`cust_shareholder_info.certification_no`）
- [[dicts/cust_shareholder_info__email]]（`cust_shareholder_info.email`）
- [[dicts/cust_shareholder_info__fund_amount_act]]（`cust_shareholder_info.fund_amount_act`）
- [[dicts/cust_shareholder_info__fund_scale]]（`cust_shareholder_info.fund_scale`）
- [[dicts/cust_shareholder_info__relation_type]]（`cust_shareholder_info.relation_type`）
