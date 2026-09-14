---
type: caliber
title: 禁用接入渠道
page_key: disabled_access_channel
domain: 准入接入与接入密钥
status: draft
aliases:
  - enable=N 渠道
  - 停用渠道
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
belong: calibers
---

# 禁用接入渠道

## 业务定位

该口径是 [[calibers/valid_access_channel|有效接入渠道]] 的补集：`enable = 'N'` 的渠道在 [[tables/cust_access_secret|cust_access_secret]] 中保留记录但不参与接入。DB 中存在 2 条禁用渠道，接入校验会拒绝。

## 需求背景

渠道停用需要保留历史配置（密钥路径、租户映射）而不物理删除，因此通过 [[concepts/enable|启用]] 开关做软禁用；被禁用渠道的接入请求在校验阶段即被拒绝。

## 版本演进

口径条件在给定证据中未发生变化；仅以 DB 分布作证。

```ground:caliber
name: 禁用接入渠道
predicate: "cust_access_secret.enable = 'N'"
scope: DB中存在2条禁用渠道，接入校验会拒绝
evidence: "db:enable N=2"
```