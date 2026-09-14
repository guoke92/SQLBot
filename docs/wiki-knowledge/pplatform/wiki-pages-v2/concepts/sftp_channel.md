---
type: concept
title: SFTP 渠道
page_key: sftp_channel
domain: SFTP 渠道
status: draft
aliases:
  - channel
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
contract_version: "0.1"
maps_to: cust_sftp.channel
field_targets:
  - cust_sftp.channel
also_confused_with:
  - cust_sftp.db_tenant_code
adjudication: boundary
belong: concepts
field_targets: [cust_sftp.channel]
---

# SFTP 渠道

“渠道”指文件交换的对接方编码，落库为 `cust_sftp.channel`（如 ZTSJ、tianma、meituan、sny_test），是 SFTP 配置的唯一业务键。

## 需求背景

不同渠道方的文件交互需要各自独立的 SFTP 主机与账号，凭渠道编码定位配置，配置表见 [[cust_sftp]]。

## 版本演进

- 实测 16 条 `channel` 互不相同，`host` 仍以 QA 环境地址为主。

## 边界（adjudication: boundary）

`channel` 是业务渠道编码（ZTSJ/tianma/meituan），`db_tenant_code` 是数据租户标识；两者取值域不同且非一一对应（`ISOLATE_TAG_zjsj`、`sny` 各有 2 条），按渠道统计与按租户统计结论会不同。