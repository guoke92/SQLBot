---
type: concept
title: SFTP 渠道（channel）
page_key: sftp-channel
domain: SFTP渠道对接
status: draft
aliases: [channel, name, user_name]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
maps_to: cust_sftp.channel = 渠道编码（英文），cust_sftp.name = 渠道中文名，cust_sftp.user_name = 登录账号
field_targets:
  - cust_sftp.channel
  - cust_sftp.name
  - cust_sftp.user_name
  - cust_sftp.db_tenant_code
adjudication: boundary
also_confused_with:
  - db_tenant_code（租户标识）
boundary: channel 与 db_tenant_code 不同源（如 ZTSJ 既是 channel 也是 tenant，但多数渠道的 tenant 是域名形式）；同名渠道存在 -test 后缀的测试配置，统计需排除。
sources: ["enrich:wiki-admin"]
belong: concepts
---

SFTP 渠道指文件交互的对接方，表 [[tables/cust_sftp]] 中用 `channel` 存渠道编码、`name` 存渠道中文名、`user_name` 存登录账号。

## 需求背景

渠道维度的排障与统计需要在「渠道编码」「账号」「租户」之间建立正确映射：账号命名形如 app_<渠道>_<日期/编号>，而租户标识多数为域名形式，与渠道编码并非同源。启用口径见 [[calibers/enabled-sftp-channel]]。

## 版本演进

v0 契约按现状固化；同名渠道的 -test 后缀测试配置属历史遗留，建议后续版本统一清理或以字段标注。

## 判定边界

channel 与 db_tenant_code 不同源（如 ZTSJ 既是 channel 也是 tenant，但多数渠道的 tenant 是域名形式）；同名渠道存在 -test 后缀的测试配置，统计需排除。

相关：[[cust_sftp]]
