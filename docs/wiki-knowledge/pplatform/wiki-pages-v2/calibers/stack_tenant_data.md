---
type: caliber
title: 存量租户数据
page_key: caliber.stack_tenant_data
domain: 租户配置
status: draft
aliases:
  - 存量租户
  - isStack
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.is_stack
contract_version: "0.1"
---

以 `is_stack='Y'` 标记从历史系统迁移或早期即存在的租户数据，用于区分租户数据的来源批次。该口径常用于判断某租户是否受历史行为约束（例如背景色/灰度、生效流程的差异化处理）。当前证据仅给出该取值的存在，未展开具体分支逻辑。

## 需求背景

租户存在存量与新增两类来源，部分运营配置在存量租户上需要特殊处理，因此需要一个可查询的数据来源标记。

## 版本演进

v0.1：依据 DB 取值分布建立口径。

```yaml
caliber: 存量租户数据
predicate: "tenant_setting_config.is_stack = 'Y'"
scope: 租户数据来源区分
evidence: db
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/tenant_source]]。