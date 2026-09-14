---
type: process
title: 平台产品生效状态流转
page_key: platform_product_status
domain: 平台产品配置
status: draft
aliases: [平台产品生效状态, product_status 状态机]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductApplication.java#effective
  - code:PlatformProductDomainService.java#effective
  - code:PlatformProduct.java:100
  - code:ProductStatusEnum.java
contract_version: "0.1"
belong: processes
---

平台产品生效状态描述产品定义自身从「待生效」进入「已生效」的单向跃迁，落库字段为 [[platform_product]] 的 `product_status`。它与租户侧、客户侧的「开通状态」是三套不同语义，辨析见 [[product_open_status]]。

## 需求背景

产品只有生效后才进入客户端可选集合，判活口径为 [[platform_product_effective]]；上架到租户是另一道闸口，见 [[tenant_product_open_status]]。保存前的类型与唯一性校验见 [[product_code_name_unique]]。

## 版本演进

- `ProductStatusEnum` 提供 `TO_BE_EFFECTIVE='0'` 与 `EFFECTIVE='1'` 两个 dictKey；DB 分布仅见 `'1'`（20 行），`'0'` 为生效前初始态，未在样本数据中出现。

```ground:process
name: 平台产品生效状态
field: platform_product.product_status
states:
  - value: "0"
    label: 待生效
    source: code_enum
  - value: "1"
    label: 已生效
    source: db_dist
transitions:
  - from: "0"
    event: 人工提交生效 effective()
    to: "1"
    evidence: "code_path:PlatformProductApplication.java#effective -> PlatformProductDomainService.java#effective -> PlatformProduct.java:100"
```

关联：[[platform_product]]、[[platform_product_effective]]、[[product_open_status]]、[[product_code_name_unique]]