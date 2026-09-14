---
type: caliber
title: 企微名片口径（customer_card_type='WX_WORK'）
page_key: customer_card_type_wx_work
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [企微名片, WX_WORK, 客服名片类型]
oid: 1
scope:
  databases: [unknown]
sources:
  - "db:tenant_setting_config.customer_card_type WX_WORK=128 / WX=6"
  - "db comment『与 operCardType 枚举一致』"
contract_version: "0.1"
belong: calibers
---

「企微名片」指客服名片下发渠道为 WX_WORK，即发送企业微信名片；对应地 WX 表示发送微信名片。该字段的值与 operCardType 枚举一致。

表结构见 [[tenant_setting_config]]。

## 需求背景
不同租户的客服触达渠道不同，名片类型决定下发哪一种名片。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 企微名片
predicate: "tenant_setting_config.customer_card_type = 'WX_WORK'"
scope: "客服名片下发渠道"
evidence: "db:WX_WORK=128 / WX=6；db comment『与 operCardType 枚举一致』"
```