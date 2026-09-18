---
type: table
title: 资方规则前端配置页面
page_key: funding_rule_front_cfg
belong: tables
status: draft
anchors: [funding_rule_front_cfg]
sources: ['database_schema:lowcode_pplatform.funding_rule_front_cfg']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [funding_rule_info, funding_rule_front_cfg__rule_layer, funding_rule_front_cfg__product_code,
  funding_rule_front_cfg__key_type, funding_rule_front_cfg__rule_key, funding_rule_front_cfg__enable,
  funding_rule_front_cfg__check_scene]
---

# 资方规则前端配置页面

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### rule

`rule_layer`, `key_name`, `key_type`, `rule_key`

### front

`front_key_name`, `front_key`, `front_field_style`

### biz_scope

`product_code`, `organization_id`, `check_scene`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: funding_rule_front_cfg
database: lowcode_pplatform
description: 资方规则前端配置页面
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [product_code, front_key_name, key_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: rule
  title: 规则层与规则标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: front
  title: 前端渲染配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: biz_scope
  title: 业务归属与校验场景
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
- key: act_procinst
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_rule_front_cfg
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: rule_layer
  data_type: string
  description: 规则层 UNDERLYING/FINANCING
  cluster: rule
  dictionary: funding_rule_front_cfg__rule_layer
- name: product_code
  data_type: string
  description: 产品code
  cluster: biz_scope
  dictionary: funding_rule_front_cfg__product_code
- name: front_key_name
  data_type: string
  description: 前端展示字段名称
  cluster: front
- name: front_key
  data_type: string
  description: 前端字段key
  cluster: front
- name: front_field_style
  data_type: string
  description: 前端字段渲染json
  cluster: front
- name: key_name
  data_type: string
  description: 字段名称描述
  cluster: rule
- name: key_type
  data_type: string
  description: 字段业务规则类型
  cluster: rule
  dictionary: funding_rule_front_cfg__key_type
- name: rule_key
  data_type: string
  description: 规则字段key
  cluster: rule
  dictionary: funding_rule_front_cfg__rule_key
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: funding_rule_front_cfg__enable
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
  cluster: act_procinst
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: common
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: act_procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: act_procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: act_procinst
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: biz_scope
- name: check_scene
  data_type: string
  description: 校验场景
  cluster: biz_scope
  dictionary: funding_rule_front_cfg__check_scene
```

## 页面链接

### 关联表

- [[tables/funding_rule_info]]

### 字典

- [[dicts/funding_rule_front_cfg__rule_layer]]（`funding_rule_front_cfg.rule_layer`）
- [[dicts/funding_rule_front_cfg__product_code]]（`funding_rule_front_cfg.product_code`）
- [[dicts/funding_rule_front_cfg__key_type]]（`funding_rule_front_cfg.key_type`）
- [[dicts/funding_rule_front_cfg__rule_key]]（`funding_rule_front_cfg.rule_key`）
- [[dicts/funding_rule_front_cfg__enable]]（`funding_rule_front_cfg.enable`）
- [[dicts/funding_rule_front_cfg__check_scene]]（`funding_rule_front_cfg.check_scene`）
