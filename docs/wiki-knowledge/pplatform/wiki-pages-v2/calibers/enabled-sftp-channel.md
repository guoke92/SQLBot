---
type: caliber
title: 启用的 SFTP 渠道口径
page_key: enabled-sftp-channel
domain: SFTP渠道对接
status: draft
aliases: [启用渠道, cust_sftp.enable=Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
belong: calibers
---

启用的 SFTP 渠道指当前可参与文件交互的渠道配置，判定条件为 `cust_sftp.enable = 'Y'`，作用域为 SFTP 渠道配置表（[[tables/cust_sftp]]）。

## 需求背景

渠道 SFTP 账号会随对接上下线增删，需要启停标记区分在用的配置；同时同名渠道可能存在 -test 后缀的测试配置，统计时需一并排除，字段边界见 [[concepts/sftp-channel]]。

## 版本演进

v0 契约按现状固化：该字段实测全部为 'Y'，目前无代码写值证据，启停是否由运营端维护待后续核实。

## 口径锚点

```ground:caliber
name: 启用的 SFTP 渠道
predicate: cust_sftp.enable = 'Y'
scope: SFTP 渠道配置表（实测全部为 Y，无代码写值证据）
evidence: db
```