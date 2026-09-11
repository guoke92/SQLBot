---
type: table
title: 前端规则配置表（funding_rule_front_cfg）
page_key: tables/funding_rule_front_cfg
domain: funding
status: draft
aliases:
  - funding_rule_front_cfg
  - 前端字段配置
  - 规则前端配置表
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_rule_front_cfg"
  - "code:FundRuleInfoApplication#validateRuleLayerAndFrontCfg"
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
---


# 前端规则配置表（funding_rule_front_cfg）

## 业务定位

本表是**规则字段的元数据字典**，定义「页面上有哪些可配置字段、字段显示成什么名字、属于哪类业务规则、归在哪个规则层」。它决定了 [[tables/funding_rule_detail]] 中 `rule_key` 的合法取值域（`front_key`），也决定导入模板中「规则名称」列如何匹配（按 `key_name`，配合 `product + rule_layer + key_name` 三元组）。

`key_type` 描述字段受哪一类业务规则约束，DB 实测枚举为 `FIELD_REQUIRED` / `FIELD_LENGTH_LIMIT` / `FILE_TYPE_LIMIT` / `FILE_SIZE_SINGLE_LIMIT` / `FILE_SIZE_TOTAL_LIMIT` / `FILE_SIZE_PACKAGE_LIMIT` / `FILE_COUNT_LIMIT` / `FILE_NAME_SYMBOL` / `INVOICE_COUNT_LIMIT` / `YEARS_CHECK` / `DATE_CHECK_NATURAL` / `DATE_CHECK_WORKDAY`，覆盖必填、长度、附件类型/大小/数量、发票份数、年限与日期（自然日/工作日）校验。

## 需求背景

无语义分析挂载的需求文档锚点。当前理解来自 `FundRuleInfoApplication#validateRuleLayerAndFrontCfg`（校验规则层与前端配置一致性）与 `FundingPartyRuleProviderImpl#doQuery`（对外查询需带 `enable='Y'` 的前端配置）。

## 版本演进

无 `action=uncovered` 的主张。字段级事实：`check_scene` 实测仅 `SUBMIT_VALIDATE`，表明本表配置目前只驱动提交环节校验；`front_key_name` 与 `key_name` 并存，说明展示名存在「名称描述」与「前端展示名」两套，导入匹配使用 `key_name`。

```ground:table
table: funding_rule_front_cfg
database: lowcode_pplatform
desc: 资方规则前端配置页面
fields:
  - name: id
    type: number
    desc: 表主键
  - name: rule_layer
    type: string
    desc: 规则层 UNDERLYING/FINANCING
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
  - name: front_field_style
    type: string
    desc: 前端字段渲染json
  - name: front_key
    type: string
    desc: 前端字段key
  - name: front_key_name
    type: string
    desc: 前端展示字段名称
  - name: key_name
    type: string
    desc: 字段名称描述
  - name: key_type
    type: string
    desc: 字段业务规则类型
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
  - name: rule_key
    type: string
    desc: 规则字段key
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```

## 关联

- 口径：[[calibers/funding_rule_front_cfg_valid_enable_y]]
- 概念：[[concepts/rule_key]]、[[concepts/rule_layer]]
- 表：[[tables/funding_rule_detail]]