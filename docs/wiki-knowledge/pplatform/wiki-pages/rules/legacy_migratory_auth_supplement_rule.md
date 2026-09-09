---
type: rule
title: "存量迁移企业授权书补签规则"
page_key: legacy_migratory_auth_supplement_rule
belong: rules
domain: "授权协议与电子授权"
status: published
aliases: ["迁移企业补签规则", "授权书补签规则"]
oid: 1

sources: ["code:CustAuthAgreementDomainService.enableCompanyManagerAuthAggrement", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [authorization_agreement.authed_status, authorization_agreement.platform_product_code, cust_company_info.auth_aggrement_supplement_flag, cust_company_info.cust_source]
coverage_note: "存量迁移企业"
scope:
  databases: [lowcode_pplatform]
---

该规则决定存量迁移企业是否需要补签 [[授权书]]：平台推送来源不补签；迁移来源且无补签标识不补签；其余情况需检查是否存在有效的 PLATFORM 授权记录。

## 需求背景

存量迁移过来的企业，如果之前在业务系统没签署过新授权协议则每个管理员要签署新的授权协议，新授权协议只需签署一份。该规则控制授权书补签按钮和产品开通条件，是 [[存量迁移企业需补签平台授权书口径]] 的具体落地。

## 版本演进

暂无。

```ground:rule
name: 存量迁移企业授权书补签规则
content: "企业来源为 PLATFORM_PUSH 不补签；来源为 MIGRATORY 且 auth_aggrement_supplement_flag='N' 不补签；否则需检查 authorization_agreement 中是否存在 platform_product_code='PLATFORM' 且 authed_status='Y' 的记录"
impact: "控制授权书补签按钮和产品开通条件"
field_targets:
  - "cust_company_info.cust_source"
  - "cust_company_info.auth_aggrement_supplement_flag"
  - "authorization_agreement.authed_status"
  - "authorization_agreement.platform_product_code"
evidence: "code_path:CustAuthAgreementDomainService.enableCompanyManagerAuthAggrement + reqdoc:存量迁移过来的企业，如果之前在业务系统没签署过新授权协议则每个管理员要签署新的授权协议，新授权协议只需签署一份"
```

相关：[[authorization_agreement]] [[cust_company_info]]
