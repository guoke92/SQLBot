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
title: 认证方式
page_key: identify_style
domain: 客户与建档
aliases:
- 邀请认证
- 简易认证
- 自主注册
- 注册认证
- 平台邀请认证
- 网关邀请认证
anchors:
- identify_style
---
# 认证方式

企业采用的认证产品模式：谁邀请/何种模式完成认证。INVITE=邀请认证-客户录入、 INVITE_AGW=邀请认证-内管录入、SIMPLE=简易认证、SELF=注册认证（自主）。

```ground:enum
enum: identify_style
fields:
- cust_company_info.identify_style
values:
  INVITE:
    label: 邀请认证-客户录入
  INVITE_AGW:
    label: 邀请认证-内管录入
  SIMPLE:
    label: 简易认证
  SELF:
    label: 注册认证（自主）
```

## 关联
- [[cust_company_info|cust_company_info]]
