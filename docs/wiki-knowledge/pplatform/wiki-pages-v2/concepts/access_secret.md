---
type: concept
title: 接入密钥
page_key: access_secret
domain: 准入接入与接入密钥
status: draft
aliases:
  - 客户接入秘钥信息
  - 渠道密钥
  - cust_access_secret
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
  - code:CustAccessApplication
contract_version: "0.1"
maps_to: cust_access_secret.id
also_confused_with:
  - cust_sftp.channel
  - tenant_setting_config.db_tenant_code
adjudication: boundary
boundary: 接入密钥表存渠道、租户、证书路径；SFTP配置存文件传输账号；租户配置存租户业务配置，三者通过channel/db_tenant_code间接关联。
belong: concepts
field_targets: [cust_access_secret.id]
sources: ["enrich:wiki-admin"]
---

# 接入密钥

## 业务定位

「接入密钥」是业务口语中对渠道接入配置的统称，其权威落点是 [[tables/cust_access_secret|cust_access_secret]] 的一条记录。记录以渠道为粒度，打包了渠道身份、落库租户、证书/密钥文件路径与各类开关；所谓「密钥」在库中存的是文件路径与密码，而不是密钥内容本身。

## 边界与混淆

- 与 `cust_sftp.channel` 的区别：SFTP 配置的 channel 描述文件传输通道，接入密钥的 channel 描述开放 API 接入渠道，二者通过渠道值间接关联但用途不同。
- 与 `tenant_setting_config.db_tenant_code` 的区别：租户配置存租户业务参数，接入密钥存渠道到租户的映射关系，是「用哪个租户」而非「租户怎么配」。

详细口径见 [[calibers/valid_access_channel|有效接入渠道]]、[[calibers/encry_type_rsa|接入密钥加密类型RSA]]、[[calibers/key_num_2|密钥对数2]]。

## 需求背景

接入方需要一套可运维的渠道配置：既能按渠道切换租户、轮换证书，也能在不删数据的前提下停用渠道。相关约束见 [[rules/access_channel_must_exist_and_enabled|接入渠道必须存在且启用]]。

## 版本演进

`status_query_license_enabled`、`rel_lls_secret_id`、`code` 三个字段在给定接入链路中均未见使用，其中前者在代码 DO 中缺失，属配置模型与代码实现不同步的迹象。

---REVIEW: concept | 接入密钥
- 术语桥 maps_to 指向 `cust_access_secret.id`，但 `id` 未在 field_semantics 中单列，需确认主键列名与语义。
---END REVIEW---

相关：[[cust_access_secret]]
