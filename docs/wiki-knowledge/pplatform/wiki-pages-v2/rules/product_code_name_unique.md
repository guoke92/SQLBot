---
type: rule
title: 平台产品编码与名称唯一
page_key: product_code_name_unique
domain: 平台产品配置
status: draft
aliases: [BR-001, checkBeforeSave]
oid: 1
scope:
  databases: [platform]
sources:
  - db:platform_product.product_code(UNI)/uq_name
  - code:PlatformProductController.java#checkBeforeSave
  - code:PlatformProductApplication.java#checkBeforeSave
  - code:PlatformProductDomainService.java#checkBeforeSave
  - reqdoc:BR-001
contract_version: "0.1"
belong: rules
---

保存或更新 PlatformProductDO 之前必须通过 `checkBeforeSave`：校验产品基本信息、`product_code` 唯一性与产品类型枚举（[[general_product]] / [[interworking_product]]），任一失败抛 BaseException，落库被阻断。DB 侧 `product_code` 唯一索引与名称唯一索引构成第二道防线。

## 需求背景

需求文档 BR-001 与实现一致：Controller → Application → DomainService 三层同名 `checkBeforeSave` 承接校验。类型枚举只接受 GENERAL / INTERWORKING，查询哨兵值 ALL='2' 不可作为存储值提交。

## 版本演进

- BR-001 首次契约化即标记为已确认（confirmed），锚点证据为代码与需求文档双源。

```ground:rule
name: 平台产品编码/名称唯一
content: "platform_product.product_code 与 name 建唯一索引，保存前 checkBeforeSave 校验产品基本信息、code 唯一与类型枚举"
impact: 重复编码/名称阻断保存
field_targets:
  - platform_product.product_code
  - platform_product.name
evidence: "code_path:PlatformProductController.java#checkBeforeSave;PlatformProductApplication.java#checkBeforeSave;PlatformProductDomainService.java#checkBeforeSave + reqdoc:BR-001"
```

关联：[[platform_product]]、[[general_product]]、[[interworking_product]]、[[platform_product_enabled]]