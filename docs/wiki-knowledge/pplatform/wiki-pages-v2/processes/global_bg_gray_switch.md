---
type: process
title: 全局背景灰度开关（Redis 缓存 BgColorCacheDto）
page_key: global_bg_gray_switch
domain: 租户配置
status: draft
aliases:
  - 全局灰度开关
  - BGCOLOR_SWITCH
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:setBgColor
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:getBgColor
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:bgColorClear
contract_version: "0.1"
belong: processes
---

全局灰度窗口不落库，而是以 `RedisKeyConstants.BGCOLOR_SWITCH_TTL` 对应的 `BgColorCacheDto` 缓存承载，缓存内记录 `startDate~endDate`。写入窗口即进入 ON；读取时若 `now` 超过 `endTime` 即判定过期，等效 OFF；调用清理接口直接删除缓存回到 OFF。该开关驱动 [[processes/bg_color_gray]] 中租户颜色的变更。

## 需求背景

灰度窗口需要秒级生效、按时自动失效，且不应为每个租户写库，因此以带 TTL 的缓存作为开关源，读取侧再做一次时间判定，兼顾「未到时间不生效」和「过期即失效」。

## 版本演进

v0.1：登记当前代码中三个入口（写入、读取判定、清理）构成的开关状态。

```yaml
state_machine: 全局背景灰度开关（Redis 缓存）
field: RedisKeyConstants.BGCOLOR_SWITCH_TTL(BgColorCacheDto)
states:
  - value: "ON"
    label: 灰度窗口生效中
    source: code_enum
  - value: "OFF"
    label: 灰度窗口未生效/已过期
    source: code_enum
transitions:
  - from: "OFF"
    event: bgcolor/set 写入 startDate~endDate
    to: "ON"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:setBgColor"
  - from: "ON"
    event: now 超出 endTime（读取时判定过期）
    to: "OFF"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:getBgColor"
  - from: "ON"
    event: bgcolor/reset/light 删除缓存
    to: "OFF"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/controller/TenantSettingConfigController.java:bgColorClear"
```

相关页面：[[processes/bg_color_gray]]、[[concepts/bg_color]]、[[calibers/gray_bg_tenant]]。