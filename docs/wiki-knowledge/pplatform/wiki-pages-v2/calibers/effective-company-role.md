---
type: caliber
title: 有效企业角色口径
page_key: effective-company-role
domain: 客户角色与端口
status: draft
aliases:
  - 有效角色口径
  - enable=Y 角色
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#getCompanyTypeByCompanyCode
  - code_path:CustRoleApplication.java#getCompanyTypeByCompanyCodeAndType
  - db_dist: cust_role_info.enable
contract_version: "0.1"
belong: calibers
---

# 有效企业角色口径

查询「某企业具备哪些业务角色」时，必须以 enable='Y' 过滤 [[tables/cust_role_info]]。getCompanyTypeByCompanyCode 与 getCompanyTypeByCompanyCodeAndType 都附加了该条件，因此对外的角色判断结果天然不含停用记录。

注意与 [[calibers/non-writeoff-role]] 的区别：enable 是**配置态是否启用**，status 是**生命周期状态**。两个条件作用点不同、不可互相替代——前者用于「读角色」，后者用于「批量改状态时跳过终态」。

## 需求背景

需求文档描述角色鉴权时只讲角色枚举，未提启用标志；实现侧以 enable='Y' 作为有效角色的统一前置条件。

## 版本演进

- enable 列作为逻辑启用标志引入后，删除角色改为「置 enable='N' + 状态流转」的组合，读侧口径固定为 enable='Y'。

```ground:caliber
name: 有效企业角色口径
predicate: cust_role_info.enable = 'Y'
scope: CustRoleApplication#getCompanyTypeByCompanyCode / getCompanyTypeByCompanyCodeAndType 查询该企业角色时附加的过滤条件
evidence: code_path:CustRoleApplication.java#getCompanyTypeByCompanyCode
```

## 关联

- [[tables/cust_role_info]]
- [[calibers/non-writeoff-role]]
- [[concepts/company-role]]