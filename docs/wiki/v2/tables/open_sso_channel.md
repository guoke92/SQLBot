---
type: table
title: 开放登录SSO渠道
page_key: open_sso_channel
belong: tables
status: draft
anchors: [open_sso_channel]
sources: ['database_schema:lowcode_pplatform.open_sso_channel']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [open_sso_channel__channel_code, open_sso_channel__channel_kind, open_sso_channel__open_mode_default,
  open_sso_channel__sso_sync_status, open_sso_channel__enable]
---

# 开放登录SSO渠道

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### channel

`channel_code`, `channel_name`, `channel_kind`, `app_id`, `open_mode_default`

### session

`default_session_expire_minute`, `max_session_expire_minute`

### sso_client

`sso_client_id`, `sso_client_secret`, `sys_type`, `sys_channel`

### sso_sync

`sso_sync_status`, `sso_sync_msg`, `sso_synced_at`

### org

`org_code`, `organization_id`

### tenant

`app_tenant_code`, `db_tenant_code`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: open_sso_channel
database: lowcode_pplatform
description: 开放登录SSO渠道
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [channel_code, channel_name, org_code, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: channel
  title: 渠道配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: session
  title: 会话策略
  trust: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: sso_client
  title: SSO 客户端
  trust: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: sso_sync
  title: SSO 同步
  trust: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: org
  title: 机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.open_sso_channel
- key: act_procinst
  title: 审批流程
  trust: proposed
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
  cluster: channel
  dictionary: open_sso_channel__channel_code
- name: channel_name
  data_type: string
  description: 渠道名称
  cluster: channel
- name: channel_kind
  data_type: string
  description: 渠道类型
  cluster: channel
  dictionary: open_sso_channel__channel_kind
- name: app_id
  data_type: string
  description: 开放平台 appId
  cluster: channel
- name: sso_client_id
  data_type: string
  description: SSO clientId（每渠道独立）
  cluster: sso_client
- name: sso_client_secret
  data_type: string
  description: SSO密钥
  cluster: sso_client
- name: sys_type
  data_type: string
  description: SSO sysType
  cluster: sso_client
- name: sys_channel
  data_type: string
  description: SSO sysChannel
  cluster: sso_client
- name: org_code
  data_type: string
  description: 同步 SSO 机构编码
  cluster: org
- name: open_mode_default
  data_type: string
  description: 默认打开形态 EMBED/TOP
  cluster: channel
  dictionary: open_sso_channel__open_mode_default
- name: default_session_expire_minute
  data_type: number
  description: 默认会话过期时间
  cluster: session
- name: max_session_expire_minute
  data_type: number
  description: 最长会话过期时间
  cluster: session
- name: sso_sync_status
  data_type: string
  description: ssoSyncStatus
  cluster: sso_sync
  dictionary: open_sso_channel__sso_sync_status
- name: sso_sync_msg
  data_type: string
  description: SSO同步描述
  cluster: sso_sync
- name: sso_synced_at
  data_type: temporal
  description: 同步时间
  cluster: sso_sync
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
  dictionary: open_sso_channel__enable
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
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
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
  cluster: org
```

## 页面链接

### 字典

- [[dicts/open_sso_channel__channel_code]]（`open_sso_channel.channel_code`）
- [[dicts/open_sso_channel__channel_kind]]（`open_sso_channel.channel_kind`）
- [[dicts/open_sso_channel__open_mode_default]]（`open_sso_channel.open_mode_default`）
- [[dicts/open_sso_channel__sso_sync_status]]（`open_sso_channel.sso_sync_status`）
- [[dicts/open_sso_channel__enable]]（`open_sso_channel.enable`）
