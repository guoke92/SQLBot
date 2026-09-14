---
type: table
title: 开放登录SSO渠道
page_key: open_sso_channel
domain: DBAss/SSO登录与通道
status: draft
anchors: [open_sso_channel]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












开放平台 SSO 渠道配置表，登记业务渠道与 SSO 平台侧系统渠道（[[sys_channel]]）的绑定关系，
承载 appId、clientId/secret、机构编码（[[org_code]]）与同步状态，是登录、登出、图形验证码策略
与渠道初始化的配置来源。本表与 [[tenant_setting_config]] 语义相邻：租户配置的统码
（[[tenant_sso_chanel]]）在代码中被直接当作 sysChannel 使用（`byCode.getSsoTenantChanel()` → `userDTO.setSsoSysChannel`），
二者存储位置不同，不可互换。

## 需求背景

各业务渠道接入 SSO 单点登录前，需在 SSO 平台登记系统渠道并同步渠道码、密钥、所属机构。
本表保存该绑定关系与同步结果：登录链路据此判断图形验证码策略（[[login_captcha_policy]]），
渠道同步异常通过 sso_sync_msg 记录失败原因（[[sso_channel_sync_state]]）。

## 版本演进

- v0（草稿）：字段语义来自 DB 实测值 + 代码引用，字段类型与物理库名未在语义分析中给出，见 REVIEW。

```ground:table
table: open_sso_channel
database: lowcode_pplatform
desc: 开放登录SSO渠道
fields:
  - name: channel_kind
    type: string
    phys: varchar(64)
    desc: 渠道类型
    dict: channel_kind
    topk: "LOCAL_SYS"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: sso_sync_status
    type: string
    phys: varchar(64)
    desc: ssoSyncStatus
    dict: sso_sync_status
    topk: "SYNCED"
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
  - name: channel_code
    type: string
    phys: varchar(128)
    desc: 业务/OpenAPI渠道码
    topk: "longteng"
  - name: channel_name
    type: string
    phys: varchar(128)
    desc: 渠道名称
    topk: "龙腾"
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
    topk: "EMBED"
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
  - name: sso_client_secret
    type: string
    phys: varchar(256)
    desc: SSO密钥
  - name: sso_sync_msg
    type: string
    phys: varchar(256)
    desc: SSO同步描述
  - name: sso_synced_at
    type: temporal
    phys: datetime
    desc: 同步时间
  - name: sys_channel
    type: string
    phys: varchar(128)
    desc: SSO sysChannel
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
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

相关：[[sys_channel]]、[[tenant_sso_chanel]]、[[org_code]]、[[sso_channel_sync_state]]、[[login_captcha_policy]]。