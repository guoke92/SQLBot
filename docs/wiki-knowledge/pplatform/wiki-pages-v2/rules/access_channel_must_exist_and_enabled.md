---
type: rule
title: 接入渠道必须存在且启用
page_key: access_channel_must_exist_and_enabled
domain: 准入接入与接入密钥
status: draft
aliases:
  - 渠道校验规则
  - 渠道不存在
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.validateChangeChannelAndTenant
contract_version: "0.1"
belong: rules
---

# 接入渠道必须存在且启用

## 业务定位

该规则是开放接入的第一道门禁：建档、变更渠道、天马建档三条链路均以 `channel + enable='Y'` 查询 [[tables/cust_access_secret|cust_access_secret]]，查不到即拒绝，不再进行租户定位。

## 需求背景

渠道是租户定位与数据隔离的前提，若渠道不存在或已禁用仍允许接入，会出现落库归属不明或已停用渠道继续写入的问题。因此校验在链路入口统一执行，判定条件见 [[calibers/valid_access_channel|有效接入渠道]] 与 [[calibers/disabled_access_channel|禁用接入渠道]]。

## 版本演进

规则在三条链路上被重复实现（建档校验、变更渠道校验、天马渠道校验），暂未见统一抽取的证据。

```ground:rule
name: 接入渠道必须存在且启用
content: 开放API建档、变更、天马建档均按channel + enable=Y查询cust_access_secret，查不到即抛“渠道不存在”。
impact: 接入请求拒绝，后续租户定位无法进行。
field_targets:
  - cust_access_secret.channel
  - cust_access_secret.enable
evidence: "code:CustAccessApplication.validateSetValue/validateChangeChannelAndTenant/validate"
```

---REVIEW: rule | 接入渠道必须存在且启用
- 语义分析中 rules 数组的证据串被截断（止于 `.../validate`），完整代码文件与行号缺失，需补齐 validateSetValueOfTianma 等路径后回填 evidence。
- rules 数组可能还存在其他规则条目但未在本次语义分析中给出，需确认是否遗漏。
---END REVIEW---