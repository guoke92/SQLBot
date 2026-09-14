---
type: caliber
title: 交e保账户存在性口径
page_key: bocom_account_existence
domain: 外部渠道与银行对接
status: draft
aliases:
  - 交e保账户存在性口径
  - BocomFacade.existBocomAccount
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:BocomFacade#existBocomAccount
contract_version: "0.1"
belong: calibers
---

# 交e保账户存在性口径

## 业务定位

该口径规定判断企业是否已开立交e保账户时的完整条件：以 `cust_company_info.certification_no` 作为 `certificationNos` 查询键，同时限定 `dbTenantCode = cust_company_info.db_tenant_code`、`platformCode='pplatform'`、`productCode='ACFLOW'`、`readLocalFlag=true`。五个条件同时满足才算"已存在交e保账户"。

## 需求背景

银行账户存在性判断必须锚定到具体的租户与产品，否则跨租户同名企业或同企业的其他产品账户会造成误判；`readLocalFlag=true` 表示只读本地数据、不外呼银行接口。该口径把 [[tables/cust_company_info]] 的 `certification_no` 与 `db_tenant_code` 作为跨系统对齐键，见 [[concepts/product_code]]。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 交e保账户存在性口径
predicate: "certificationNos = [cust_company_info.certification_no] AND dbTenantCode = cust_company_info.db_tenant_code AND platformCode='pplatform' AND productCode='ACFLOW' AND readLocalFlag=true"
scope: BocomFacade.existBocomAccount
evidence: "code:BocomFacade#existBocomAccount"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/bocom_clearing_product]]、[[calibers/channel_tenant_mapping]]
- 术语：[[concepts/product_code]]