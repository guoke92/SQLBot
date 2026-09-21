---
type: table
title: 资方规则前端配置页面
page_key: funding_rule_front_cfg
belong: tables
status: draft
anchors: [funding_rule_front_cfg]
sources: ['database_schema:lowcode_pplatform.funding_rule_front_cfg', 'code_path:FundingPartyRuleProviderImpl.java:105']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [funding_rule_front_cfg__rule_layer, funding_rule_front_cfg__product_code,
  funding_rule_front_cfg__key_type, funding_rule_front_cfg__rule_key, funding_rule_front_cfg__enable,
  funding_rule_front_cfg__check_scene]
---

# 资方规则前端配置页面

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: funding_rule_front_cfg
database: lowcode_pplatform
desc: 资方规则前端配置页面
inactive: false
primary_key: [id]
grain: 按产品配置前端字段
name_anchors: [product_code, front_key_name, key_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: rule_layer
  type: string
  desc: 规则层 UNDERLYING/FINANCING
  dict: [FINANCING, UNDERLYING, OTHER]
  label: [融资规则, 底层规则, 其他规则]
- name: product_code
  type: string
  desc: 产品code
  dict: [ACFLOW, RVSFACTOR_PC]
- name: front_key_name
  type: string
  desc: 前端展示字段名称
- name: front_key
  type: string
  desc: 前端字段key
- name: front_field_style
  type: string
  desc: 前端字段渲染json
- name: key_name
  type: string
  desc: 字段名称描述
- name: key_type
  type: string
  desc: 字段业务规则类型
  dict: [FIELD_REQUIRED, FIELD_LENGTH_LIMIT, YEARS_CHECK, FILE_TYPE_LIMIT, FILE_NAME_SYMBOL,
    FILE_COUNT_LIMIT, FILE_SIZE_SINGLE_LIMIT, INVOICE_COUNT_LIMIT, FILE_SIZE_PACKAGE_LIMIT,
    DATE_CHECK_NATURAL, DATE_CHECK_WORKDAY, FILE_SIZE_TOTAL_LIMIT]
- name: rule_key
  type: string
  desc: 规则字段key
  dict: [B0003, list.contractNo, list.contractName, transferDate, foundedDate, list.contractDate,
    baseContNo, list.contractAmount, baseContName, contractDate, contractAmount]
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
- name: check_scene
  type: string
  desc: 校验场景
  dict: [SUBMIT_VALIDATE]
default_filter:
  predicate: funding_rule_front_cfg.enable = 'Y'
  trust: confirmed
  evidence: code_path:FundingPartyRuleProviderImpl.java:105
```

## 页面链接

### 字典

- [[dicts/funding_rule_front_cfg__rule_layer]]（`funding_rule_front_cfg.rule_layer`）
- [[dicts/funding_rule_front_cfg__product_code]]（`funding_rule_front_cfg.product_code`）
- [[dicts/funding_rule_front_cfg__key_type]]（`funding_rule_front_cfg.key_type`）
- [[dicts/funding_rule_front_cfg__rule_key]]（`funding_rule_front_cfg.rule_key`）
- [[dicts/funding_rule_front_cfg__enable]]（`funding_rule_front_cfg.enable`）
- [[dicts/funding_rule_front_cfg__check_scene]]（`funding_rule_front_cfg.check_scene`）
