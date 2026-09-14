---
type: caliber
title: 有效项目
page_key: valid_tenant_project
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 启用态项目
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getPclogPath
contract_version: "0.1"
belong: calibers
---

口径“有效项目”：登录取项目 logo 时只使用 enable='Y' 的 [[tenant_project]] 记录。

## 需求背景

项目停用后不应再返回其 logo；项目 logo 取自 [[tenant_project.logo_path]] 并转换为下载 URL。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 有效项目
predicate: "tenant_project.enable = 'Y'"
scope: 登录取项目 logo
evidence: "code_path:SaaSAuthController.java:getPclogPath"
```

相关：[[tenant_project]]、[[valid_cust_project_rel]]。