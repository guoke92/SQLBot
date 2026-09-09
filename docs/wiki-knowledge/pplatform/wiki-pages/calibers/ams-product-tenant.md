---
type: caliber
title: AMS产品租户
page_key: ams-product-tenant
belong: calibers
domain: AMS联系人第三方对接
status: published
aliases: [AMS产品租户判定]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

AMS 产品租户口径：当租户互通产品表中产品 openStatus='Y' 且 platformProductId 属于 AMS 系统链接产品（amsSysLinkSup、amsSysLinkProj、amsSysLinkFinance）时，判定为开通 AMS 产品的租户。

## 需求背景
获取开通 AMS 产品的租户 ID 用于后续 AMS 同步操作，代码路径 CustCompanyUtilApplication.getTenantIdsWithAmsProduct。

## 版本演进
初始版本基于 CustCompanyUtilApplication.getTenantIdsWithAmsProduct 提取。

```ground:caliber
name: AMS产品租户
predicate: "TenantInterworkingProductDO.openStatus='Y' AND platformProductId IN (amsSysLinkSup, amsSysLinkProj, amsSysLinkFinance)"
scope: "获取开通AMS产品的租户ID"
evidence: "code_path:CustCompanyUtilApplication.getTenantIdsWithAmsProduct"
```

[[tenant_interworking_product_do]]