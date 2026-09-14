---
type: caliber
title: 平台产品已生效
page_key: platform_product_effective
domain: 平台产品配置
status: draft
aliases: [已生效产品, product_status=1]
oid: 1
scope:
  databases: [platform]
sources:
  - db
contract_version: "0.1"
belong: calibers
---

「平台产品已生效」是平台产品列表与生效动作后的判活口径，等价于 [[platform_product]] 的 `product_status = '1'`。它与租户上架、客户开通分属三层语义，见 [[product_open_status]]。

## 需求背景

产品列表只展示已生效产品；生效动作的跃迁路径见 [[platform_product_status]]。启用标记是另一维度，见 [[platform_product_enabled]]。

## 版本演进

- DB 分布中 `'1'` 已出现（20 行），`'0'` 为生效前初始态未落样本。

```ground:caliber
name: 平台产品已生效
predicate: "platform_product.product_status = '1'"
scope: 平台产品列表/生效
evidence: db
```

关联：[[platform_product]]、[[platform_product_status]]、[[product_open_status]]