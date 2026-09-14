---
type: concept
title: 协议类型（agreementType）
page_key: agreement_type
domain: 授权协议与电子授权
status: draft
aliases:
  - AgreementDocType
  - serviceKey
  - 协议 code
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
adjudication: boundary
also_confused_with:
  - authorization_agreement.platform_product_code
belong: concepts
---

协议类型区分“协议的种类”：PrivacyPolicy / UserProtocol / CustPersonLicense / CFCA_Auth / BS_Auth / ProductProtocol*，对应 [[argeement_migratory_record]] 的 `agreement_type`。而 `platform_product_code` 区分“业务线产品”（ACFLOW/AMS/BEECREDIT/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER）。同一协议类型在每个产品码下各有一条迁移记录——两个维度是交叉关系，不是同义。

## 需求背景
协议拉取需要按“产品 × 协议类型”的粒度记录进度与文件路径，才能支持不同业务线各自回溯，见 [[agreement_migratory_pending_pull]]、[[agreement_migratory_pulled]]，产品协议的具体取值见 [[product_protocol]]。

## 版本演进
`ProductProtocol*` 是一族按产品码派生的协议类型，说明早期只有平台级协议（隐私政策、用户协议、CA 协议等），后续随业务线接入扩展出按产品的协议类型。