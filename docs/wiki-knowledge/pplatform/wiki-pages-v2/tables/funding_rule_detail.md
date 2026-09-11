---
type: table
title: 资方规则明细表（funding_rule_detail）
page_key: tables/funding_rule_detail
domain: funding
status: draft
aliases:
  - funding_rule_detail
  - 资方规则明细
  - 规则明细表
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_rule_detail"
  - "code:FundRuleInfoApplication#saveRuleInfo"
  - "code:FundRuleInfoApplication#getRuleInfoById"
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


# 资方规则明细表（funding_rule_detail）

## 业务定位

本表以「键值对 + 规则层」的形式承载资方规则的具体内容：一行即一条 **规则项**，`rule_key` 是机器键（对应前端配置 [[tables/funding_rule_front_cfg]] 的 `front_key`），`rule_value` 是规则值，`rule_layer`（`UNDERLYING` / `FINANCING` / `OTHER`）决定这条规则归属底层/融资/其他哪一层。业务上通过 `rule_info_id` / `fund_rule_code_ref` 双通道回指主表 [[tables/funding_rule_info]]，并冗余 `funding_party_mark` 与 `version` 以便独立查询。

所有明细查询都带 `enable='Y'`（见 [[calibers/funding_rule_detail_valid_enable_y]]）；保存采用「按 `ruleInfoId + ruleKey + enable='Y'` 命中即更新、否则新增」的幂等写法。

## 需求背景

无语义分析挂载的需求文档锚点。当前理解来自 `FundRuleInfoApplication#saveRuleInfo` 与 `FundingPartyRuleProviderImpl#doQuery`：明细以 `ruleKey` 为幂等粒度落库，未在 `ruleMap` 中出现的 `frontKey` 直接跳过而不中断保存。

## 版本演进

无 `action=uncovered` 的主张。DB 实测 `version` 值为 1/2/3/4/6/8/9/13/17/23/25，说明明细跟随主表版本写入但并非逐版留痕；`check_scene` 实测仅 `SUBMIT_VALIDATE`，表明当前明细规则只服务「提交校验」这一场景。

```ground:table
table: funding_rule_detail
database: lowcode_pplatform
desc: 资方规则信息详情
fields:
  - name: id
    type: number
    desc: 表主键
  - name: rule_layer
    type: string
    desc: 规则层
    dict: rule_layer
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
  - name: check_scene
    type: string
    desc: 校验场景
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
  - name: fund_rule_code_ref
    type: string
    desc: 关联规则信息code
  - name: funding_party_mark
    type: string
    desc: 资方标识
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
  - name: rule_info_id
    type: number
    desc: 关系规则信息ID
  - name: rule_key
    type: string
    desc: 字段key 对应front_key
  - name: rule_value
    type: string
    desc: 规则值
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
    desc: 版本
```

## 关联表

- [[funding_rule_info]]：funding_rule_detail.rule_info_id → funding_rule_info.id（java-eq:FundRuleInfoApplication.java，suggested）
## 关联

- 口径：[[calibers/funding_rule_detail_valid_enable_y]]
- 规则：[[rules/rule_detail_save_idempotent]]
- 概念：[[concepts/rule_key]]、[[concepts/rule_layer]]
- 表：[[tables/funding_rule_info]]、[[tables/funding_rule_front_cfg]]