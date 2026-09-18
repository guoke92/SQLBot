---
type: table
title: 智能审核引流卡片埋点记录
page_key: gpt_learn_poster_log
belong: tables
status: draft
anchors: [gpt_learn_poster_log]
sources: ['database_schema:lowcode_pplatform.gpt_learn_poster_log']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [gpt_learn_poster_log__enable, gpt_learn_poster_log__app_tenant_code, gpt_learn_poster_log__db_tenant_code]
---

# 智能审核引流卡片埋点记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### user

`user_id`, `user_name`

### company

`company_id`, `company_name`, `organization_id`

### card_event

`popup_time`, `click_time`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### audit

（空）

## 字段

```ground:table
table: gpt_learn_poster_log
database: lowcode_pplatform
description: 智能审核引流卡片埋点记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [user_name, company_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: user
  title: 用户信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.gpt_learn_poster_log
- key: company
  title: 企业与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.gpt_learn_poster_log
- key: card_event
  title: 卡片交互时间
  trust: proposed
  evidence: database_schema:lowcode_pplatform.gpt_learn_poster_log
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.gpt_learn_poster_log
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.gpt_learn_poster_log
- key: audit
  title: 审计字段
  trust: proposed
  evidence: database_schema:lowcode_pplatform.gpt_learn_poster_log
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: user_id
  data_type: number
  description: 用户ID
  cluster: user
- name: user_name
  data_type: string
  description: 用户名
  cluster: user
- name: company_id
  data_type: number
  description: 企业ID
  cluster: company
- name: company_name
  data_type: string
  description: 企业名称
  cluster: company
- name: popup_time
  data_type: temporal
  description: 卡片弹出时间
  cluster: card_event
- name: click_time
  data_type: temporal
  description: 卡片点击时间
  cluster: card_event
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
  dictionary: gpt_learn_poster_log__enable
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
  cluster: tenant
  dictionary: gpt_learn_poster_log__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: gpt_learn_poster_log__db_tenant_code
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
  cluster: company
```

## 页面链接

### 字典

- [[dicts/gpt_learn_poster_log__enable]]（`gpt_learn_poster_log.enable`）
- [[dicts/gpt_learn_poster_log__app_tenant_code]]（`gpt_learn_poster_log.app_tenant_code`）
- [[dicts/gpt_learn_poster_log__db_tenant_code]]（`gpt_learn_poster_log.db_tenant_code`）
