---
type: caliber
title: 限时短链到期校验
page_key: temporary_short_link_expire_check
domain: notification
status: draft
aliases: [限时有效短链口径, is_forever=N 校验]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
contract_version: "0.1"
belong: calibers
---

is_forever='N' 的短链在访问时必须校验 expire_time，过期即拦截。该口径的拦截动作与异常语义见 [[short_link_expire_check]]，术语定义见 [[temporary_short_link]]。

## 需求背景
限时短链承载活动、临时入口等场景，需求侧要求到期自动失效，不能依赖人工下架。

## 版本演进
- 该分支当前无 DB 数据样本，仅由代码常量分支支撑；上线后一旦出现 N 态数据即会生效。

```ground:caliber
name: 限时短链到期校验
predicate: short_link.is_forever = 'N'
scope: 短链访问跳转
evidence: ShortLinkController.java:48
```