---
type: rule
title: 注册分布式锁
page_key: register_distributed_lock
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 注册防重锁
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:register
contract_version: "0.1"
belong: rules
---

注册按“租户 + 手机号”加分布式锁，防止并发重复提交。

## 需求背景

同一租户下同一手机号的并发注册必须串行化，锁维度取 [[cust_company_info.db_tenant_code]]
（见 [[db_tenant_code]]）；密码用 RSA 私钥解密后再落库。

## 版本演进

- v0（草稿）：规则来自代码锁实现。

```ground:rule
name: 注册分布式锁
content: "register 使用 Redis 锁 saas:register:{dbTenantCode}:{cellphone}，未取到锁抛“注册处理中，请勿重复提交”；密码用 RSA 私钥解密。"
impact: "防止同租户同手机并发注册。"
field_targets:
  - cust_company_info.db_tenant_code
evidence: "code_path:SaaSAuthController.java:register"
```

相关：[[cust_company_info]]、[[db_tenant_code]]。