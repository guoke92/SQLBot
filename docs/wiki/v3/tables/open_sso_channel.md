---
type: table
title: 开放登录SSO渠道
page_key: open_sso_channel
belong: tables
status: draft
anchors: [open_sso_channel]
sources: ['database_schema:lowcode_pplatform.open_sso_channel']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [open_sso_channel__channel_code, open_sso_channel__channel_kind, open_sso_channel__open_mode_default,
  open_sso_channel__sso_sync_status, open_sso_channel__enable]
---

# 开放登录SSO渠道

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: open_sso_channel
database: lowcode_pplatform
desc: 开放登录SSO渠道
inactive: false
primary_key: [id]
grain: SSO 渠道（catalog 有表；pplatform-web 无 @TableName DO）
name_anchors: [channel_code, channel_name, org_code, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: channel_code
  type: string
  desc: 业务/OpenAPI渠道码
  dict: [longteng, jingke]
- name: channel_name
  type: string
  desc: 渠道名称
- name: channel_kind
  type: string
  desc: 渠道类型
  dict: [LOCAL_SYS]
- name: app_id
  type: string
  desc: 开放平台 appId
- name: sso_client_id
  type: string
  desc: SSO clientId（每渠道独立）
- name: sso_client_secret
  type: string
  desc: SSO密钥
- name: sys_type
  type: string
  desc: SSO sysType
- name: sys_channel
  type: string
  desc: SSO sysChannel
- name: org_code
  type: string
  desc: 同步 SSO 机构编码
- name: open_mode_default
  type: string
  desc: 默认打开形态 EMBED/TOP
  dict: [EMBED]
- name: default_session_expire_minute
  type: number
  desc: 默认会话过期时间
- name: max_session_expire_minute
  type: number
  desc: 最长会话过期时间
- name: sso_sync_status
  type: string
  desc: ssoSyncStatus
  dict: [SYNCED]
- name: sso_sync_msg
  type: string
  desc: SSO同步描述
- name: sso_synced_at
  type: temporal
  desc: 同步时间
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict: [Y, N]
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
```

## 页面链接

### 字典

- [[dicts/open_sso_channel__channel_code]]（`open_sso_channel.channel_code`）
- [[dicts/open_sso_channel__channel_kind]]（`open_sso_channel.channel_kind`）
- [[dicts/open_sso_channel__open_mode_default]]（`open_sso_channel.open_mode_default`）
- [[dicts/open_sso_channel__sso_sync_status]]（`open_sso_channel.sso_sync_status`）
- [[dicts/open_sso_channel__enable]]（`open_sso_channel.enable`）
