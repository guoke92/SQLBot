---
type: caliber
title: 收费企业角色口径
page_key: chargeable_company_role
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_company_type, cust_company_info.data_type, cust_company_info.enable]
scope:
  databases: [lowcode_pplatform]
---

# 收费企业角色口径

业务定位：判断企业是否具备可收费角色的标准，用于企业端缴费校验和待办生成。

## 需求背景

并非所有企业都需要缴纳 CA 服务费，只有特定角色（SUPPLIER、CORE）且处于启用状态的主数据才纳入收费范围。该口径确保缴费校验的准确性。

## 版本演进

当前口径固定为两种角色，未来可能支持更多角色或动态配置。

```ground:caliber
name: 收费企业角色口径
predicate: "cust_company_info.cust_company_type IN ('SUPPLIER','CORE') AND cust_company_info.enable='Y' AND cust_company_info.data_type='MAIN'"
scope: 企业端缴费校验与待办生成
evidence: "code:CaFeeBizNodeCheckApplication.hasChargeableRoleUnderCertNo + CaFeePaymentCheckApplication.checkFeePaymentForPortal"
```

[[ca_fee_company]] · [[certification_no]]

相关：[[cust_company_info]]
