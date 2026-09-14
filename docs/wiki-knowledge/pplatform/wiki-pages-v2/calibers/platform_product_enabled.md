---
type: caliber
title: 平台产品启用
page_key: platform_product_enabled
domain: 平台产品配置
status: draft
aliases: [产品启用, enable=Y]
oid: 1
scope:
  databases: [platform]
sources:
  - db
contract_version: "0.1"
belong: calibers
---

「平台产品启用」是 [[platform_product]] 的逻辑启用口径，`enable = 'Y'`，作用于产品列表可见性与唯一性检查，与生效状态 `product_status` 相互独立。

## 需求背景

保存与唯一性检查（[[product_code_name_unique]]）只考虑启用中的记录；列表白名单过滤见 [[list_whitelist_filter]]。

## 版本演进

- 初版口径，无历史变更。

```ground:caliber
name: 平台产品启用
predicate: "platform_product.enable = 'Y'"
scope: 产品列表/唯一性检查
evidence: db
```

关联：[[platform_product]]、[[platform_product_effective]]、[[product_code_name_unique]]