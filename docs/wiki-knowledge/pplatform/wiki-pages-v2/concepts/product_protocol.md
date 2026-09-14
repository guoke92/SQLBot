---
type: concept
title: 产品协议
page_key: product_protocol
domain: 授权协议与电子授权
status: draft
aliases:
  - ProductProtocol
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
maps_to:
  - argeement_migratory_record.agreement_type
field_targets:
  - argeement_migratory_record.agreement_type
adjudication: synonym
also_confused_with:
  - authorization_agreement.platform_product_code
belong: concepts
sources: ["enrich:wiki-admin"]
---

「产品协议」是 [[agreement_type]] 的一个取值族（`ProductProtocol*`）：按产品码返回不同的协议类型（AMS/BEECREDIT/RVSFACTOR_PC/ACFLOW/ORDER/DEALER/STORAGE/VOUCHER）。它与“平台级协议”并列，但**不同于** `PLATFORM_PRODUCT_TYPE`（平台级管理员授权书）——后者属于 [[authorization_agreement]] 的产品码维度，见 [[platform_level_auth_agreement]]。

## 需求背景
每个业务线在开通时都需要客户签署对应的产品协议，迁移时按产品码逐条拉取，因此在迁移记录中表现为“同协议类型、不同产品码各一条”。

## 版本演进
产品协议的类型数量随业务线增加而扩张（AMS/BEECREDIT/RVSFACTOR_PC/ACFLOW/ORDER/DEALER/STORAGE/VOUCHER），是协议迁移需求长期演进的主要驱动之一。

相关：[[argeement_migratory_record]]
