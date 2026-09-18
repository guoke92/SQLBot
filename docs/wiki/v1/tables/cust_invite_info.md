---
type: table
title: 客户邀请信息
page_key: cust_invite_info
belong: tables
status: draft
anchors: [cust_invite_info]
sources: ['database_schema:lowcode_pplatform.cust_invite_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_invite_info__progress, cust_invite_info__enable, cust_invite_info__app_tenant_code,
  cust_invite_info__db_tenant_code]
---

# 客户邀请信息

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### invite

`progress`, `invite_time`, `channel_code`, `invite_from`, `invite_cust_id`

### contact

`contact_name`, `email`, `contact_phone`

### audit

（空）

### procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: cust_invite_info
database: lowcode_pplatform
description: 客户邀请信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, contact_name, channel_code]
clusters:
- key: common
  title: 通用
  include: always
- key: invite
  title: 邀请信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_invite_info
- key: contact
  title: 联系人信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_invite_info
- key: audit
  title: 审计信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_invite_info
- key: procinst
  title: 流程实例
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_invite_info
- key: tenant_org
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_invite_info
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
  cluster: common
- name: progress
  data_type: string
  description: 进度
  cluster: invite
  dictionary: cust_invite_info__progress
- name: invite_time
  data_type: temporal
  description: 邀请时间
  cluster: invite
- name: contact_name
  data_type: string
  description: 联系人
  cluster: contact
- name: email
  data_type: string
  description: 邮箱
  cluster: contact
- name: contact_phone
  data_type: string
  description: 联系人手机号码
  cluster: contact
- name: channel_code
  data_type: string
  description: 渠道码
  cluster: invite
- name: invite_from
  data_type: string
  description: 邀请主体
  cluster: invite
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_invite_info__enable
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
  cluster: procinst
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant_org
  dictionary: cust_invite_info__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_org
  dictionary: cust_invite_info__db_tenant_code
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: procinst
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: tenant_org
- name: invite_cust_id
  data_type: number
  description: 邀请客户id
  cluster: invite
```

## 页面链接

### 字典

- [[dicts/cust_invite_info__progress]]（`cust_invite_info.progress`）
- [[dicts/cust_invite_info__enable]]（`cust_invite_info.enable`）
- [[dicts/cust_invite_info__app_tenant_code]]（`cust_invite_info.app_tenant_code`）
- [[dicts/cust_invite_info__db_tenant_code]]（`cust_invite_info.db_tenant_code`）
