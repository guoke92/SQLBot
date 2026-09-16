---
type: table
title: 开放登录SSO渠道
page_key: open_sso_channel
belong: tables
status: draft
aliases: []
anchors:
- open_sso_channel
sources:
- database_schema:lowcode_pplatform.open_sso_channel
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 开放登录SSO渠道

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### channel_profile

`channel_code`, `channel_name`, `channel_kind`, `name`

### credentials

`app_id`, `sso_client_id`, `sso_client_secret`

### sso_mapping

`sys_type`, `sys_channel`, `org_code`, `organization_id`

### open_session

`open_mode_default`, `default_session_expire_minute`, `max_session_expire_minute`

### sso_sync

`sso_sync_status`, `sso_sync_msg`, `sso_synced_at`

### tenant

`app_tenant_code`, `db_tenant_code`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: open_sso_channel
database: lowcode_pplatform
description: 开放登录SSO渠道
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- channel_code
- channel_name
- org_code
- code
- name
clusters:
- key: common
  title: 通用
  include: always
- key: channel_profile
  title: 渠道档案
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: credentials
  title: 接入凭证
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: sso_mapping
  title: SSO系统映射
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: open_session
  title: 打开与会话配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: sso_sync
  title: SSO同步
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: approval
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: channel_code
  data_type: string
  description: 业务/OpenAPI渠道码
  nullable: true
  cluster: channel_profile
- name: channel_name
  data_type: string
  description: 渠道名称
  nullable: true
  cluster: channel_profile
- name: channel_kind
  data_type: string
  description: 渠道类型
  nullable: true
  cluster: channel_profile
  dictionary: open_sso_channel_channel_kind
- name: app_id
  data_type: string
  description: 开放平台 appId
  nullable: true
  cluster: credentials
- name: sso_client_id
  data_type: string
  description: SSO clientId（每渠道独立）
  nullable: true
  cluster: credentials
- name: sso_client_secret
  data_type: string
  description: SSO密钥
  nullable: true
  cluster: credentials
- name: sys_type
  data_type: string
  description: SSO sysType
  nullable: true
  cluster: sso_mapping
- name: sys_channel
  data_type: string
  description: SSO sysChannel
  nullable: true
  cluster: sso_mapping
- name: org_code
  data_type: string
  description: 同步 SSO 机构编码
  nullable: true
  cluster: sso_mapping
- name: open_mode_default
  data_type: string
  description: 默认打开形态 EMBED/TOP
  nullable: true
  cluster: open_session
  dictionary: open_sso_channel_open_mode_default
- name: default_session_expire_minute
  data_type: number
  description: 默认会话过期时间
  nullable: true
  cluster: open_session
- name: max_session_expire_minute
  data_type: number
  description: 最长会话过期时间
  nullable: true
  cluster: open_session
- name: sso_sync_status
  data_type: string
  description: ssoSyncStatus
  nullable: true
  cluster: sso_sync
  dictionary: open_sso_channel_sso_sync_status
- name: sso_sync_msg
  data_type: string
  description: SSO同步描述
  nullable: true
  cluster: sso_sync
- name: sso_synced_at
  data_type: temporal
  description: 同步时间
  nullable: true
  cluster: sso_sync
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: channel_profile
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: open_sso_channel_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: sso_mapping
```
