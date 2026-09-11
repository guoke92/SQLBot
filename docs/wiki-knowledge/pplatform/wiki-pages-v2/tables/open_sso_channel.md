---
type: table
title: 开放登录SSO渠道
page_key: open_sso_channel
domain: 基线
status: draft
anchors: [open_sso_channel]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# 开放登录SSO渠道

（基线页：33 字段，行数估计 2。行语义/常用过滤待语义摄取增强。）

```ground:table
table: open_sso_channel
database: lowcode_pplatform
desc: 开放登录SSO渠道
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: app_id
    type: string
    phys: varchar(128)
    desc: 开放平台 appId
    topk: 73d62771729e4ffba7f263cb6012746d
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
  - name: channel_code
    type: string
    phys: varchar(128)
    desc: 业务/OpenAPI渠道码
    topk: longteng
  - name: channel_kind
    type: string
    phys: varchar(64)
    desc: 渠道类型
    topk: LOCAL_SYS
  - name: channel_name
    type: string
    phys: varchar(128)
    desc: 渠道名称
    topk: 龙腾
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: default_session_expire_minute
    type: number
    phys: int(10)
    desc: 默认会话过期时间
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
  - name: max_session_expire_minute
    type: number
    phys: int(10)
    desc: 最长会话过期时间
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: open_mode_default
    type: string
    phys: varchar(128)
    desc: 默认打开形态 EMBED/TOP
    topk: EMBED
  - name: org_code
    type: string
    phys: varchar(128)
    desc: 同步 SSO 机构编码
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: sso_client_id
    type: string
    phys: varchar(128)
    desc: SSO clientId（每渠道独立）
    topk: r6n8u7p3
  - name: sso_client_secret
    type: string
    phys: varchar(256)
    desc: SSO密钥
  - name: sso_sync_msg
    type: string
    phys: varchar(256)
    desc: SSO同步描述
  - name: sso_sync_status
    type: string
    phys: varchar(64)
    desc: ssoSyncStatus
    topk: SYNCED
  - name: sso_synced_at
    type: temporal
    phys: datetime
    desc: 同步时间
  - name: sys_channel
    type: string
    phys: varchar(128)
    desc: SSO sysChannel
    topk: scpr-pplatform-pc
  - name: sys_type
    type: string
    phys: varchar(64)
    desc: SSO sysType
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```
