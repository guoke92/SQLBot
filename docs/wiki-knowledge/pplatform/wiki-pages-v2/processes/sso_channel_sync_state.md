---
type: process
title: SSO 渠道同步状态
page_key: sso_channel_sync_state
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sso_sync_status 状态
oid: 1
scope:
  databases: [unknown]
sources:
  - db:open_sso_channel.sso_sync_status
  - db:open_sso_channel.sso_sync_msg
contract_version: "0.1"
belong: processes
---

[[open_sso_channel.sso_sync_status]] 目前只观测到 SYNCED（已同步）一个取值（DB 实测），
失败信息落在 [[open_sso_channel.sso_sync_msg]]，例如“找不到此系统渠道：scpr-pplatform-pc_org91130421356828213h”，
说明存在“渠道未在 SSO 平台登记/机构后缀不匹配”的失败场景。

## 需求背景

渠道配置需要从业务侧同步到 SSO 平台，同步结果直接决定该渠道能否完成单点登录；
同步失败原因必须可见以支持排查（文档主张的初始化服务链路见 REVIEW）。

## 版本演进

- v0（草稿）：只有 DB 实测状态值，未观测到状态迁移证据，故不登记 transitions。

```ground:process
name: SSO 渠道同步状态
field: open_sso_channel.sso_sync_status
states:
  - value: SYNCED
    label: 已同步
    source: db_dist
transitions: []
```

相关：[[open_sso_channel]]、[[sys_channel]]、[[login_captcha_policy]]。