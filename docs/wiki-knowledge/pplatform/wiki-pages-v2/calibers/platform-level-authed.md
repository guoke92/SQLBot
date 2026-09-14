---
type: caliber
title: 平台级授权已完成
page_key: platform-level-authed
domain: 授权协议与电子授权
status: draft
aliases:
  - PLATFORM 授权已完成
  - 平台授权判定
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:authorization_agreement
contract_version: "0.1"
belong: calibers
---

判定企业/管理员是否已签署平台授权书时，只取 `platform_product_code='PLATFORM'` 且 `authed_status='Y'` 的行；由于授权按自然人（`cust_manager_id`）维度记录，同一人在多家企业任职时只需一份平台级授权即全部免签。具体产品行（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）的 `Y` 表示存量系统已授权，不参与该口径。

相关术语边界见 [[concepts/platform-product-code]]，状态迁移见 [[processes/authorization-agreement-authed-status]]。

## 需求背景
若按产品逐条校验授权，同一管理员在同一企业的多个产品上会被要求重复签署；因此把「平台级」授权作为唯一免签依据，产品级记录只作为存量已授权的事实保留。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 平台级授权已完成
predicate: "authorization_agreement.platform_product_code = 'PLATFORM' AND authorization_agreement.authed_status = 'Y'"
scope: "企业/管理员是否已签署平台授权书（按人维度，一个角色签过即全部免签）"
evidence: "code_path:CustAuthAgreementDomainService.java#hasCompanySignedAuthAggrement"
```