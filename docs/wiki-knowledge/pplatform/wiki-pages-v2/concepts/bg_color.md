---
type: concept
title: 灰度颜色 / 背景颜色
page_key: bg_color
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [bgColor, bg_color, 灰色, 彩色]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.updateTenantColorGray / setColorlight / updateTenantColorNull"
  - "db comment『背景颜色(L:彩色 G：灰色)』"
contract_version: "0.1"
maps_to: tenant_setting_config.bg_color
field_targets:
  - tenant_setting_config.bg_color
adjudication: boundary
also_confused_with:
  - tenant_setting_config.ai_resource_color
  - tenant_setting_config.main_theme_color
  - tenant_setting_config.adapt_colour
belong: concepts
field_targets: [tenant_setting_config.bg_color]
---

「灰度颜色 / 背景颜色」指 [[tenant_setting_config]].bg_color，取 L（彩色）/ G（灰色），其实际生效受 Redis 灰度开关缓存（BGCOLOR_SWITCH_TTL）控制。状态流转见 [[tenant_bg_color_gray]]，判定口径见 [[bg_color_gray]] 与 [[bg_color_light]]。

边界：bg_color 是灰度开关结果；`ai_resource_color` 是智能客服按钮色（HEX，DB 存在脏值）；`main_theme_color` 是主题色，并会在 ai_resource_color 为空时兜底；`adapt_colour` 是适配背景色。后三者都不参与灰度缓存判断。

## 需求背景
灰度需要全局可控又允许租户个别选择，因此颜色选择与灰度开关结果必须落在同一列并由缓存控制生效时机，同时与其他「颜色」字段明确区分。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；暂无历史版本记录。