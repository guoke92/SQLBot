---
type: caliber
title: 彩色背景口径（bg_color='L'）
page_key: bg_color_light
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [彩色背景, bg_color='L', LIGHT]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.setColorlight"
  - "db comment『背景颜色(L:彩色 G：灰色)』"
contract_version: "0.1"
belong: calibers
---

「彩色背景」表示租户在灰度期内主动选择保留彩色，落库值 L。注意前端在窗口内可能返回 state=OFF（展示态），与落库值不一致，判断时应以库值为准。

状态流转见 [[tenant_bg_color_gray]]，对照口径见 [[bg_color_gray]]。

## 需求背景
灰度不能强制全部租户变色，需保留租户主动选择彩色的能力。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 彩色背景
predicate: "tenant_setting_config.bg_color = 'L'"
scope: "租户主动选择彩色或灰度重置"
evidence: "code:TenantAppliactionService.setColorlight；db comment"
```