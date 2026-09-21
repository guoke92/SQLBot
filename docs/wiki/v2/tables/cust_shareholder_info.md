---
type: table
title: 客户关联方信息主表
page_key: cust_shareholder_info
belong: tables
status: draft
anchors: [cust_shareholder_info]
sources: ['database_schema:lowcode_pplatform.cust_shareholder_info']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_shareholder_info__code, cust_shareholder_info__name,
  cust_shareholder_info__enable, cust_shareholder_info__remark, cust_shareholder_info__ref_cust_company_info,
  cust_shareholder_info__certification_type, cust_shareholder_info__certification_no,
  cust_shareholder_info__fund_amount_act, cust_shareholder_info__fund_scale, cust_shareholder_info__relation_type]
---

# 客户关联方信息主表

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: cust_shareholder_info
database: lowcode_pplatform
desc: 客户关联方信息主表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
  dict: [6f4831e29b584aa5893c71b3f201a62a, f10bfdc45bc44710be7b10712ede351f, 23ec1de85da643cbb8a2a3045673da8a,
    e6da13e575914d2db0e2d2e4590a9e3a, b0ca86d46721415abc21b5f44f844f3d, 28a82b234425439d999d153ad48887bc]
- name: name
  type: string
  desc: 关联方名称
  dict: ['34', asdf, '11', asdfdf]
- name: enable
  type: string
  desc: enable
  dict: [Y]
- name: remark
  type: string
  desc: remark
  dict: [wert, '11']
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
  dict: [78bd395c9ca34fe4b87fa1a816c6714a, 313e49f751f146c9bec2d19682d756dc, 40a501bb9f1945069631e728ac752d59,
    a1c94e1e892b4ec28c3332dac47754d3, 6c682c4d0f804d1e9705ae80daedbe19]
- name: certification_type
  type: string
  desc: 证件类型
  dict: [CRET_ID]
- name: certification_no
  type: string
  desc: 证件号码
  dict: [wertwetew, '11']
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
  dict: [wretwewt, '111']
- name: fund_scale
  type: string
  desc: 出资比例（%）
  dict: [wt, '11']
- name: investment_date
  type: temporal
  desc: 投资日期
- name: relation_type
  type: string
  desc: 关联方类型
  dict: [LEGAL_PERSON, SENIOR_MANAGER]
- name: main_data_id
  type: number
  desc: 主数据id
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
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_shareholder_info__code]]（`cust_shareholder_info.code`）
- [[dicts/cust_shareholder_info__name]]（`cust_shareholder_info.name`）
- [[dicts/cust_shareholder_info__enable]]（`cust_shareholder_info.enable`）
- [[dicts/cust_shareholder_info__remark]]（`cust_shareholder_info.remark`）
- [[dicts/cust_shareholder_info__ref_cust_company_info]]（`cust_shareholder_info.ref_cust_company_info`）
- [[dicts/cust_shareholder_info__certification_type]]（`cust_shareholder_info.certification_type`）
- [[dicts/cust_shareholder_info__certification_no]]（`cust_shareholder_info.certification_no`）
- [[dicts/cust_shareholder_info__fund_amount_act]]（`cust_shareholder_info.fund_amount_act`）
- [[dicts/cust_shareholder_info__fund_scale]]（`cust_shareholder_info.fund_scale`）
- [[dicts/cust_shareholder_info__relation_type]]（`cust_shareholder_info.relation_type`）
