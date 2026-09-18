---
type: table
title: 资金方异常解析及建议主表
page_key: funding_exception_resolution
belong: tables
status: draft
anchors: [funding_exception_resolution]
sources: ['database_schema:lowcode_pplatform.funding_exception_resolution', 'code_path:FundingPartyExceptionResolutionProviderImpl.java:107']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [funding_rule_info, funding_exception_resolution__funding_party_code, funding_exception_resolution__product_code,
  funding_exception_resolution__enable]
---

# 资金方异常解析及建议主表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: funding_exception_resolution
database: lowcode_pplatform
desc: 资金方异常解析及建议主表
inactive: false
primary_key: [id]
grain: 资金方+产品+报错关键字一行建议
name_anchors: [funding_party_code, funding_party_name, product_code, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: exception_no
  type: string
  desc: 异常编号
- name: funding_party_code
  type: string
  desc: 对接方标识
  dict: [abc, hsbc, cgb, szbank, bod, cdrcb, scb, default, lzbank, czbank, icbcProjectLoan,
    bob, cmbchina, hfbank, boscBeehive, icbc, alipay]
- name: funding_party_name
  type: string
  desc: 资金方名称
- name: error_keyword
  type: string
  desc: 报错关键字
- name: error_reason
  type: string
  desc: 报错原因
- name: suggestion
  type: string
  desc: 建议处理方案
- name: file_path
  type: string
  desc: 附件
- name: product_code
  type: string
  desc: 产品code
  dict: [ACFLOW, RVSFACTOR_PC]
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
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
default_filter:
  predicate: funding_exception_resolution.enable = 'Y'
  trust: confirmed
  evidence: code_path:FundingPartyExceptionResolutionProviderImpl.java:107
```

## 页面链接

### 关联表

- [[tables/funding_rule_info]]

### 字典

- [[dicts/funding_exception_resolution__funding_party_code]]（`funding_exception_resolution.funding_party_code`）
- [[dicts/funding_exception_resolution__product_code]]（`funding_exception_resolution.product_code`）
- [[dicts/funding_exception_resolution__enable]]（`funding_exception_resolution.enable`）
