---
type: rule
title: 客户端查询平台产品编码必填
page_key: client_query_platform_product_code_required
belong: rules
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则要求在客户端查询场景中，操作者及所属企业 ID 必需，平台产品编码不能为空白，否则抛出业务异常。

## 需求背景

客户端查询同样需要精确定位租户与产品，缺失任何一个将导致查询失败。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 客户端查询平台产品编码必填
content: 在 queryForClient 中，若 operator 或 operator.getCompanyId 为 null，或 platformProductCode 为 blank，抛出 BaseException
impact: 阻断客户端查询，返回业务异常
field_targets: ["companyId", "platformProductCode"]
evidence: code_path:ProjectAlipayClearingConfigApplication.queryForClient
```

[[tables/ProjectAlipayClearingConfigQryDTO]] [[company_id]] [[productCode]]