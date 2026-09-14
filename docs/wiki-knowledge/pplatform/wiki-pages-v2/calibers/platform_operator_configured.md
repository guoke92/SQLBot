---
type: caliber
title: 配置了平台运营方
page_key: platform_operator_configured
domain: 租户配置
status: draft
aliases:
  - 配置了平台运营方
  - platform_operator 含 platform
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.platform_operator
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/component/PlatformComponentFacade.java:needPlatformOperatorCompany
contract_version: "0.1"
belong: calibers
---

`platform_operator` 是 JSON 数组，元素取值 `platform` / `tenant` 可组合。仅当数组包含 `platform` 时，租户生效校验才要求平台运营方企业存在；因此「配了运营方」与「需要运营方企业」不是等价条件，见 [[concepts/platform_operator]]。

## 需求背景

平台运营方与租户方运营方在业务上职责不同；只有涉及平台运营的租户才需要在生效时校验运营方企业主体，避免对纯租户方运营的租户施加无谓的前置条件。

## 版本演进

v0.1：依据 `needPlatformOperatorCompany` 判定建立口径。

```yaml
caliber: 配置了平台运营方
predicate: "tenant_setting_config.platform_operator 包含 'platform'"
scope: 租户生效必填校验是否需要校验平台运营方企业
evidence: "code:PlatformComponentFacade.java:needPlatformOperatorCompany"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/platform_operator]]、[[processes/tenant_status_effective]]。