---
type: caliber
title: 灰色背景口径（bg_color='G'）
page_key: bg_color_gray
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [灰色背景, bg_color='G', GRAY]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:ColorConstants.GRAY 写值点 updateTenantColorGray / getBgColor"
  - "db comment『背景颜色(L:彩色 G：灰色)』"
contract_version: "0.1"
belong: calibers
---

「灰色背景」是全局灰度生效期内租户的默认背景色，写值点为 `ColorConstants.GRAY`，落库值 G。批量置灰发生在灰度窗口生效且租户未自定义颜色时。

状态流转见 [[tenant_bg_color_gray]]，对照口径见 [[bg_color_light]]，语义边界见 [[bg_color]]。

## 需求背景
灰度期间需要统一视觉基线，未主动选择颜色的租户默认收敛为灰色。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 灰色背景
predicate: "tenant_setting_config.bg_color = 'G'"
scope: "全局灰度生效期内的租户默认色"
evidence: "code:ColorConstants.GRAY 写值点 updateTenantColorGray / getBgColor；db comment『背景颜色(L:彩色 G：灰色)』"
```