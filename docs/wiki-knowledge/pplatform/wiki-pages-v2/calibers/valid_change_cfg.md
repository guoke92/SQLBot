---
type: caliber
title: 有效变更项配置
page_key: valid_change_cfg
domain: 企业变更与运营变更
status: draft
aliases: [变更项配置口径, enable=Y 配置]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: calibers
---

口径定义：变更项配置列表只取 `cust_change_cfg.enable = 'Y'` 的行。它是 [[change_cfg_match]] 规则的第一道过滤，与端类型、认证方式、客户类型、是否总公司等条件叠加后得到企业可见的变更项清单（[[cust_change_cfg]]）。

## 需求背景

变更项配置需要支持下线而不物理删除，因此所有读取路径统一加 `enable` 条件，避免历史配置重新出现在企业可见清单中。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 有效变更项配置
predicate: "cust_change_cfg.enable = 'Y'"
scope: 客户变更配置列表查询
evidence: "code_path:CustChangeApplication.java#list(EnableEnum.Y.name())"
```

相关页面：[[cust_change_cfg]]、[[change_cfg_match]]、[[valid_change_record]]、[[valid_oper_change_record]]。