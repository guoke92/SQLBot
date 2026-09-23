---
type: table
title: 开放登录SSO渠道
page_key: open_sso_channel
belong: tables
status: draft
anchors:
- open_sso_channel
sources:
- database_schema:lowcode_pplatform.open_sso_channel
- code_path:OpenSsoChannelDao.java:24
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_app_channel_config
- cust_company_info
- open_sso_channel__sso_sync_status
- open_sso_channel__enable
- open_sso_channel__open_mode_default
---
# 开放登录SSO渠道

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: open_sso_channel
database: lowcode_pplatform
desc: 开放登录SSO渠道
inactive: false
primary_key:
- id
grain: 一渠道一行；channel_code 唯一；live 另有 tenant_code 列（与 db_tenant_code 并存）
name_anchors:
- channel_code
- channel_name
- org_code
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: channel_code
  type: string
  desc: 业务/OpenAPI渠道码
- name: channel_name
  type: string
  desc: 渠道名称
- name: channel_kind
  type: string
  desc: 渠道类型
  dict:
  - LOCAL_SYS
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
  label: [iframe 嵌入]
- name: default_session_expire_minute
  type: number
  desc: 默认会话过期时间
- name: max_session_expire_minute
  type: number
  desc: 最长会话过期时间
- name: sso_sync_status
  type: string
  desc: ssoSyncStatus
  dict:
  - SYNCED
  written_with:
  - sso_sync_msg
  - sso_synced_at
- name: sso_sync_msg
  type: string
  desc: SSO同步描述
  written_with:
  - sso_sync_status
  - sso_synced_at
- name: sso_synced_at
  type: temporal
  desc: 同步时间
  written_with:
  - sso_sync_status
  - sso_sync_msg
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label:
  - 启用
  - 停用
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
- name: tenant_code
  type: string
  nullable: false
default_filter:
  predicate: open_sso_channel.enable = 'Y'
  trust: confirmed
  evidence: code_path:OpenSsoChannelDao.java:24
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: open_sso_channel.app_id
right: cust_app_channel_config.app_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:shared_domain;reextract:开放 SSO 与客户渠道 app
source: reextract_joins
join_role: business_code
priority: primary
authenticity_note: 开放 SSO 与客户渠道 app
```

```ground:relation
type: EQUI_JOIN
left: open_sso_channel.channel_code
right: cust_company_info.channel_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: full_sweep:same_semantic UAT company.channel_code empty
source: full_sweep
join_role: business_code
priority: secondary
authenticity_note: same_semantic:sso
```

## 页面链接

### 关联表

- [[tables/cust_app_channel_config]]
- [[tables/cust_company_info]]

### 概念

- [[concepts/channel_archive_longteng]]
- [[concepts/channel_code_homonym_bundle]]
- [[concepts/open_sso_channel_term]]
- [[concepts/tenant_code_vs_db_tenant]]

### 字典

- [[dicts/open_sso_channel__channel_kind]]（`open_sso_channel.channel_kind`）
- [[dicts/open_sso_channel__open_mode_default]]（`open_sso_channel.open_mode_default`）
- [[dicts/open_sso_channel__sso_sync_status]]（`open_sso_channel.sso_sync_status`）
- [[dicts/open_sso_channel__enable]]（`open_sso_channel.enable`）
