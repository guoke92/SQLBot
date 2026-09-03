---
type: rule
title: AMS产品CA开通特殊逻辑
page_key: rule_ams_ca_open_special
domain: customer
status: published
aliases: []
oid: 1
sources: ["enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.bs_register_status, cust_company_info.ca_register_status]
scope:
  databases: [lowcode_pplatform]
---

该规则描述AMS产品开通CA时的特殊处理，走独立电子签章通道。

## 需求背景

`openCa` 中若 `productAppId=AMS`，`baseContractProvider.companySignRegister` 签署机构使用 `BEST_SIGN`，成功后将 `bs_register_status` 和 `ca_register_status` 都置 Y；法人信息缺失时可取经办人作为签署人。

## 版本演进

规则来自代码路径 `CustAccessAsyncApplication.openCa`，无文档声明冲突。

```ground:rule
name: AMS产品CA开通特殊逻辑
content: "openCa中若productAppId=AMS，baseContractProvider.companySignRegister签署机构使用BEST_SIGN，成功后将bs_register_status和ca_register_status都置Y；法人信息缺失时可取经办人作为签署人"
impact: AMS电子签章走独立通道
field_targets:
  - "cust_company_info.bs_register_status"
  - "cust_company_info.ca_register_status"
evidence: "code_path:CustAccessAsyncApplication.openCa"
```

相关：[[cust_company_info]]
