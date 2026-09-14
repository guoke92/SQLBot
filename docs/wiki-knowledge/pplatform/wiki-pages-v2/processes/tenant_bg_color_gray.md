---
type: process
title: 租户背景颜色灰度状态机
page_key: tenant_bg_color_gray
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [背景颜色灰度, bg_color 状态机, 彩色/灰色]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.updateTenantColorGray / setColorlight / updateTenantColorNull；TenantSettingConfigController.getBgColor"
  - "db comment『背景颜色(L:彩色 G：灰色)』；Redis 灰度缓存 BGCOLOR_SWITCH_TTL"
contract_version: "0.1"
belong: processes
---

该状态机描述 `tenant_setting_config.bg_color` 在全局灰度窗口下的取值变化：窗口生效且租户未自定义颜色时批量置 G（灰），灰度期内租户主动选择彩色则落 L，缓存过期或走 `bgcolor/reset/light` 时置 NULL。前端展示态与落库态并不完全一致——灰度窗口内颜色为 L 时对前端返回 state=OFF 仅作展示，不回写数据库。

颜色语义与相邻颜色字段的边界见 [[bg_color]]；判定口径见 [[bg_color_gray]] 与 [[bg_color_light]]。

## 需求背景
灰度期间需要统一收敛租户主题为灰色以减少视觉变更，同时允许租户在灰度期内选择保留彩色；灰度结束后通过重置恢复默认，不做历史值回写。

## 版本演进
v0.1（本页）：首版契约，两态与四条迁移来自语义分析证据；暂无历史版本记录。

```ground:process
name: 租户背景颜色/灰度
field: tenant_setting_config.bg_color
states:
  - value: "L"
    label: 彩色
    source: code_const
  - value: "G"
    label: 灰色
    source: code_const
transitions:
  - from: ""
    event: "全局灰度窗口生效且租户未自定义颜色 → updateTenantColorGray() 批量置 G"
    to: "G"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorGray"
  - from: "G"
    event: "灰度期内租户选择彩色 setColorlight(id) 落 L"
    to: "L"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:setColorlight"
  - from: "L"
    event: "灰度窗口内租户颜色为 L 时对前端返回 state=OFF（仅展示态，不落库）"
    to: "L"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:getBgColor"
  - from: "任意"
    event: "缓存过期 / bgcolor/reset/light → updateTenantColorNull() 置 NULL"
    to: ""
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:updateTenantColorNull"
```