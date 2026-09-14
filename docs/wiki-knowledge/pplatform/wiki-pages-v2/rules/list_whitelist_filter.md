---
type: rule
title: 产品列表白名单过滤
page_key: list_whitelist_filter
domain: 平台产品配置
status: draft
aliases: [BR-002, filterLimitProduct, platform.limit.product.support]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductController.java#listTenantProduct
  - code:PlatformProductController.java#filterLimitProduct
  - code:PlatformProductProviderImpl.java#listOpenProductByCompanyId
  - reqdoc:BR-002
contract_version: "0.1"
belong: rules
---

Nacos 配置 `platform.limit.product.support` 非空时，仅返回 `productCode` 命中白名单的产品，用于收敛客户端可见的平台产品集合。列表取数链路为：AGW 请求直接返回；非 AGW 取当前 `dbTenantCode`，按 [[tenant_product]] 已开通列表过滤，再经白名单过滤。

## 需求背景

需求文档 BR-002 与实现一致（confirmed）：`listTenantProduct` 完成租户维度过滤后调用 `filterLimitProduct` 做白名单裁剪。白名单以 [[platform_product_code]] 为匹配键。

## 版本演进

- 初版规则，配置项取值由 Nacos 管理，运行期可变。

```ground:rule
name: 列表白名单过滤
content: "Nacos 配置 platform.limit.product.support 非空时，仅返回包含 productCode 的产品"
impact: 控制客户端可见平台产品集合
field_targets:
  - platform_product.product_code
evidence: "code_path:PlatformProductController.java#listTenantProduct;PlatformProductController.java#filterLimitProduct;PlatformProductProviderImpl.java#listOpenProductByCompanyId + reqdoc:BR-002"
```

关联：[[platform_product]]、[[tenant_product]]、[[platform_product_code]]、[[tenant_product_on_shelf]]