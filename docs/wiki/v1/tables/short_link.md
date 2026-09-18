---
type: table
title: 短链接
page_key: short_link
belong: tables
status: draft
anchors: [short_link]
sources: ['database_schema:lowcode_pplatform.short_link']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [short_link__type, short_link__is_forever, short_link__enable, short_link__app_tenant_code,
  short_link__db_tenant_code]
---

# 短链接

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### short_link

`name`, `source_url`, `expire_time`, `number`, `type`, `is_forever`

### tenant

`app_tenant_code`, `db_tenant_code`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`organization_id`

## 字段

```ground:table
table: short_link
database: lowcode_pplatform
description: 短链接
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: short_link
  title: 短链业务
  trust: proposed
  evidence: database_schema:lowcode_pplatform.short_link
- key: tenant
  title: 租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.short_link
- key: act_procinst
  title: 流程实例
  trust: proposed
  evidence: database_schema:lowcode_pplatform.short_link
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
- name: name
  data_type: string
  description: 名称
  cluster: short_link
- name: source_url
  data_type: string
  description: 源链接
  cluster: short_link
- name: expire_time
  data_type: temporal
  description: 到期时间
  cluster: short_link
- name: number
  data_type: string
  description: 编码
  cluster: short_link
- name: type
  data_type: string
  description: 类型
  cluster: short_link
  dictionary: short_link__type
- name: is_forever
  data_type: string
  description: 到期类型
  cluster: short_link
  dictionary: short_link__is_forever
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: short_link__enable
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
  dictionary: short_link__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: short_link__db_tenant_code
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
```

## 页面链接

### 字典

- [[dicts/short_link__type]]（`short_link.type`）
- [[dicts/short_link__is_forever]]（`short_link.is_forever`）
- [[dicts/short_link__enable]]（`short_link.enable`）
- [[dicts/short_link__app_tenant_code]]（`short_link.app_tenant_code`）
- [[dicts/short_link__db_tenant_code]]（`short_link.db_tenant_code`）
