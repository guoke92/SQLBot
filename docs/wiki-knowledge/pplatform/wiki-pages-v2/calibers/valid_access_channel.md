---
type: caliber
title: 有效接入渠道
page_key: valid_access_channel
domain: 准入接入与接入密钥
status: draft
aliases:
  - enable=Y 渠道
  - 可用渠道
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.validateChangeChannelAndTenant
  - code:CustAccessApplication.validateSetValueOfTianma
  - db:cust_access_secret
contract_version: "0.1"
belong: calibers
---

# 有效接入渠道

## 业务定位

该口径定义「渠道可用」的判定条件：在 [[tables/cust_access_secret|cust_access_secret]] 中，`enable = 'Y'` 的渠道才被视为有效渠道，可用于开放 API 建档、变更渠道与天马渠道的校验。它是 [[rules/access_channel_must_exist_and_enabled|接入渠道必须存在且启用]] 规则的判定基础，也是 [[concepts/enable|启用]] 术语在接入链路上的具体落地。

## 需求背景

接入请求必须先过渠道校验才能进入租户定位环节；按 `channel + enable='Y'` 查询查不到即拒绝，避免禁用渠道继续接入。对应的反向口径见 [[calibers/disabled_access_channel|禁用接入渠道]]。

## 版本演进

口径条件在给定证据中未发生变化；DB 实测 Y=19、N=2。

```ground:caliber
name: 有效接入渠道
predicate: "cust_access_secret.enable = 'Y'"
scope: 开放API渠道校验、变更渠道校验、天马渠道校验
evidence: "code:CustAccessApplication.validateSetValue/validateChangeChannelAndTenant/validateSetValueOfTianma; db:enable Y=19,N=2"
```