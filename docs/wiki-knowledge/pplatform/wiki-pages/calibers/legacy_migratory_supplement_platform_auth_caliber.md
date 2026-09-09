---
type: caliber
title: "存量迁移企业需补签平台授权书口径"
page_key: legacy_migratory_supplement_platform_auth_caliber
belong: calibers
domain: "授权协议与电子授权"
status: published
aliases: ["补签平台授权书口径", "迁移企业补签口径"]
oid: 1

sources: ["code:CustAuthAgreementDomainService.enableCompanyManagerAuthAggrement", "enrich:wiki-admin"]
contract_version: "0.1"
coverage_note: "企业+用户"
scope:
  databases: [lowcode_pplatform]
---

该口径判断某个存量迁移企业的管理员是否需要补签平台授权书：非平台推送且（非迁移或补签标识为 Y）且当前不存在有效的 PLATFORM 授权记录。

## 需求背景

[[存量迁移企业授权书补签规则]] 控制授权书补签按钮和产品开通条件，本口径是规则判断的核心谓词。

## 版本演进

暂无。

```ground:caliber
name: 存量迁移企业需补签平台授权书口径
predicate: "cust_company_info.custSource <> 'PLATFORM_PUSH' AND (cust_company_info.custSource <> 'MIGRATORY' OR cust_company_info.authAggrementSupplementFlag = 'Y') AND NOT EXISTS (authorization_agreement WHERE platform_product_code='PLATFORM' AND authed_status='Y' AND cust_id=企业ID AND cust_manager_id=用户ID)"
scope: "企业+用户"
evidence: "code:CustAuthAgreementDomainService.enableCompanyManagerAuthAggrement"
```