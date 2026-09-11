---
type: table
title: cust_sftp SFTP 渠道配置表
page_key: tables/cust_sftp
domain: SFTP渠道对接
status: draft
aliases: [SFTP 配置, 渠道 SFTP 配置]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
---

`cust_sftp` 保存各对接渠道的 SFTP 服务器配置与登录账号，是渠道文件交换的接入元数据表：一行对应一个渠道（或渠道的某套测试配置）的 SFTP 账号。启用口径见 [[calibers/enabled-sftp-channel]]，字段混淆边界见 [[concepts/sftp-channel]]。

## 需求背景

不同渠道（如 bgy / tianma / meituan / sny）的文件交互独立开设 SFTP 账号，账号命名形如 `app_<渠道>_<日期/编号>`，服务器以 qa.sftp.lls.com:22 为主、个别为 uat.sftp.lls.com。渠道编码与数据租户标识是两个不同来源的概念，统计与排障时不可互相替代。

## 版本演进

v0 契约按现状固化。本页字段语义均来自 DB 实测，暂无代码侧写值证据；`enable` 实测全部为 'Y'，是否存在失效配置需后续数据核对后再补充演进说明。

## 字段语义锚点

```ground:fields
table: cust_sftp
fields:
  - field: channel
    meaning: SFTP 对接渠道编码（如 bgy/tianma/meituan/sny）
    evidence: db
  - field: user_name
    meaning: SFTP 登录账号，命名形如 app_<渠道>_<日期/编号>
    evidence: db
  - field: host / port
    meaning: SFTP 服务器地址与端口，实测 qa.sftp.lls.com:22 为主、个别 uat.sftp.lls.com
    evidence: db
  - field: db_tenant_code
    meaning: 所属数据租户标识
    evidence: db
```