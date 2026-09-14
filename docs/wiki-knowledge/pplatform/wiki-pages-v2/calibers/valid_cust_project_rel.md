---
type: caliber
title: 有效项目关联
page_key: valid_cust_project_rel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 启用态企业项目关联
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getPclogPath
contract_version: "0.1"
belong: calibers
---

口径“有效项目关联”：登录取企业/项目 logo 时，只使用 enable='Y' 的 [[cust_project_rel]] 记录，
并与 db_tenant_code 联合过滤。

## 需求背景

企业-项目关联存在解绑/停用记录，登录返回的项目信息必须只取有效关联，
避免给前端返回已停用项目的 logo。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 有效项目关联
predicate: "cust_project_rel.enable = 'Y'"
scope: 登录取企业/项目 logo
evidence: "code_path:SaaSAuthController.java:getPclogPath"
```

相关：[[cust_project_rel]]、[[valid_tenant_project]]、[[tenant_project]]。