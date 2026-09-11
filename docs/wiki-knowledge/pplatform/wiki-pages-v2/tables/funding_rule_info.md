---
type: table
title: 资方规则信息表（funding_rule_info）
page_key: tables/funding_rule_info
domain: funding
status: draft
aliases:
  - funding_rule_info
  - 资方规则主表
  - 资金方规则信息
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_rule_info"
  - "code:FundRuleInfoApplication#saveRuleInfo"
  - "code:FundRuleInfoApplication#activeRule"
  - "code:FundRuleInfoApplication#inActiveRule"
  - "code:FundRuleInfoApplication#exportRecords"
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


# 资方规则信息表（funding_rule_info）

## 业务定位

本表是**资方规则的版本化主表**：一个「产品 + 资方」组合对应一条主记录（由 `code` 唯一标识，`DataModelUtils.getUniqueKey()` 生成），其下挂载若干明细（见 [[tables/funding_rule_detail]]）。主表承载三类信息：身份（`product_code` + `funding_party_mark` + `funding_party_name`）、生命周期（`rule_status` + `version`）、有效标识（`enable`）。

规则的**生命周期**是本表的语义核心：新增即落 `PENDING`，需显式生效才变 `ACTIVE`，外部（Dubbo）只能消费 `ACTIVE` 规则；每次更新 `version` 累加 1，明细随之携带同版本。详见 [[processes/funding_rule_status_machine]]。

## 需求背景

语义分析未挂载任何 `reqdoc_claims`，本页背景描述均来自代码证据：`saveRuleInfo` 的新增查重（`productCode + fundingPartyMark`）、`activeRule` / `inActiveRule` 的状态迁移、`FundingPartyRuleProviderImpl#doQuery` 的 `rule_status=ACTIVE` 过滤，共同构成了「先建后生效、外部只见生效版」的设计意图。

## 版本演进

无 `action=uncovered` 的主张，故无 (document_claim，未证实) 条目。字段级演进事实：`version` 从新增时的 1 开始逐次累加，明细表 `funding_rule_detail.version` 会跟随主表版本，DB 实测分布为 1/2/3/4/6/8/9/13/17/23/25，说明同一主记录已被反复更新（非连续值属正常，因为并非每次更新都落明细）。

```ground:table
table: funding_rule_info
database: lowcode_pplatform
desc: 资方规则信息
fields:
  - name: id
    type: number
    desc: 表主键
  - name: rule_status
    type: string
    desc: 规则状态 ACTIVE/INACTIVE/PENDING
    dict: rule_status
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: funding_party_mark
    type: string
    desc: 资金方标识
  - name: funding_party_name
    type: string
    desc: 资方名称
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: product_code
    type: string
    desc: 产品code
  - name: remark
    type: string
    desc: remark
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
  - name: version
    type: number
    desc: 版本号
```

## 关联表

- [[funding_rule_detail]]：funding_rule_info.id → funding_rule_detail.rule_info_id（java-eq:FundRuleInfoApplication.java，suggested）
## 关联

- 口径：[[calibers/funding_rule_info_valid_enable_y]]、[[calibers/funding_rule_info_active_rule]]
- 流程：[[processes/funding_rule_status_machine]]
- 规则：[[rules/rule_info_create_duplicate_check]]、[[rules/rule_info_update_version_increment]]、[[rules/rule_info_create_initial_pending]]、[[rules/rule_info_provider_active_only]]、[[rules/rule_import_product_code_direct_match]]
- 概念：[[concepts/rule_layer]]、[[concepts/product_code]]、[[concepts/funding_key]]