---
type: caliber
title: 永久短链不校验到期时间
page_key: permanent_short_link_skip_expire
domain: notification
status: draft
aliases: [永久有效短链口径, is_forever=Y 不校验]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
  - db:short_link.is_forever
contract_version: "0.1"
belong: calibers
---

凡是 is_forever='Y' 的短链，在访问跳转时完全不校验 expire_time，即使该列有值也不影响跳转。该口径与 [[temporary_short_link_expire_check]] 构成互斥边界，术语定义见 [[permanent_short_link]]。

## 需求背景
永久短链用于长期投放（例如印刷物、长期协议链接），需求侧要求其不受投放期限影响，避免误过期导致业务中断。

## 版本演进
- DB 中所有样本均为 Y，即当前线上全量短链都命中该口径。

```ground:caliber
name: 永久短链不校验到期时间
predicate: short_link.is_forever = 'Y'
scope: 短链访问跳转
evidence: ShortLinkController.java:48 + db
```