---
type: process
title: 租户生效状态机
page_key: tenant_status_effective
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [租户生效状态, status 状态机, effective]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.effective / predicateEffective；TenantAppliactionService.syncTenant"
  - "db:tenant_setting_config.status 分布 Y=124 / N=240"
contract_version: "0.1"
belong: processes
---

租户生效状态机描述 `tenant_setting_config.status` 在「待生效 → 已生效」之间的迁移。生效是一次全量校验：合同模板、通知、待办、短信、平台运营方、门户页、产品、基础信息八项配置全部通过后，才把 `status` 回写为 Y；任一未完成则返回告警并保持原状态。迁移租户落库时不显式设置状态，保持空/待生效。

该状态机与三个口径直接相关：[[enable_tenant_config]]（读取前置）、[[tenant_effective]]（已生效筛选）、[[tenant_pending_effective]]（待生效筛选）。状态字段本身见 [[tenant_setting_config]]。

## 需求背景
租户创建后配置项分散在多个模块，需要一次性校验后才允许对外生效，避免半配置租户被业务使用；迁移租户为避免触发新增事件，先以占位状态落库。

## 版本演进
v0.1（本页）：首版契约，三态与四条迁移均来自语义分析证据；暂无历史版本记录。

```ground:process
name: 租户生效状态
field: tenant_setting_config.status
states:
  - value: "N"
    label: 待生效
    source: db_dist
  - value: "Y"
    label: 已生效
    source: db_dist
  - value: ""
    label: 空/未生效（迁移租户初始态，导出展示为『待生效』）
    source: code_const
transitions:
  - from: "N"
    event: "effective() 八项配置（合同模板/通知/待办/短信/平台运营方/门户页/产品/基础信息）全部校验通过"
    to: "Y"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:effective#L108"
  - from: "N"
    event: "任一配置项未完成 → 返回 WindowAlertDTO.alertEnabled=true，状态不变"
    to: "N"
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:predicateEffective"
  - from: "任意"
    event: "syncTenant 迁移租户落库（不显式设置 status，保持待生效）"
    to: ""
    evidence: "code_path:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/application/TenantAppliactionService.java:syncTenant"
```