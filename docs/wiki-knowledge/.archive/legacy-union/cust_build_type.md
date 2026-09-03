---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-build-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 录入方式
page_key: cust_build_type
domain: 客户与建档
aliases:
- 平台录入
- 客户录入
- 内管录入
- PC端录入
- 网关录入
anchors:
- cust_build_type
---
# 录入方式

企业建档时从哪个操作端录入：PC_BUILD=客户录入（企业端自主填报）， AGW_BUILD=平台录入（内管/运营代录）。与认证方式（identify_style）语义相邻但不同： 录入方式只区分操作端，认证方式区分认证产品模式。用户说"平台录入"指 cust_build_type=AGW_BUILD。

```ground:enum
enum: cust_build_type
fields:
- cust_company_info.cust_build_type
values:
  PC_BUILD:
    label: 客户录入
  AGW_BUILD:
    label: 平台录入
```

## 关联
- [[cust_company_info|cust_company_info]]
