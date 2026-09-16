---
type: scenario
title: 渠道接入
page_key: channel_access
domain: 准入接入与接入密钥
status: draft
aliases: [接入密钥, OpenAPI渠道, SFTP]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:准入接入与接入密钥", "code:page-plan.yaml:企业银行账户/集团/SFTP"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_access_secret]
field_targets:
  - cust_access_secret.channel
  - cust_access_secret.enable
---

# 渠道接入

问「某渠道密钥是否有效 / SFTP 通道」时进入本场景。按 `channel` 查，不按企业主档状态。

**主档** [[cust_access_secret]]：渠道加解密凭证。  
**从属** [[cust_sftp]]：同 channel 的文件通道。两表都没有指向企业的等值 JOIN。

```ground:scenario
scenario: channel_access
hubs:
- table: cust_access_secret
  role: master
  grain: 一渠道一行
  window:
  - id
  - enable
  - create_time
  - update_time
  - channel
  - encry_type
  - name
- table: cust_sftp
  role: sftp
  grain: 一渠道一行
  window:
  - id
  - enable
  - create_time
  - update_time
  - channel
  - host
  - port
  - user_name
  - name
lifecycle: []
shared: []
```
