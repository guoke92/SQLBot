---
type: concept
title: 协议
page_key: agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 用户协议
  - 隐私政策
  - 产品协议
  - CA 协议
  - BS 协议
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatFormMigratoryApplication.java
  - db:argeement_migratory_record
contract_version: "0.1"
maps_to: "argeement_migratory_record（协议迁移记录）+ 底层 BaseContractProvider/IContractInfoProvider 维护的合同表；agreement_type 取 AgreementDocType"
field_targets:
  - argeement_migratory_record.agreement_type
  - argeement_migratory_record.sign_mode
  - argeement_migratory_record.agreement_path
  - argeement_migratory_record.agreement_no
adjudication: boundary
also_confused_with:
  - 授权书
boundary: "协议是文本文件与签署事实（含 sign_mode、agreement_path、agreement_no）；授权书是管理员授权状态记录，不含文件落库"
belong: concepts
---

「协议」指客户与平台/机构之间签署的文本及其签署事实：类型由 `AgreementDocType` 给出（`BS_Auth`/`CFCA_Auth`/产品协议/`CustPersonLicense`/`UserProtocol`/`PrivacyPolicy`），迁移记录落在 [[tables/argeement_migratory_record]]，文件路径与编号由 `agreement_path`/`agreement_no` 承载，清单见 [[calibers/migratory_init_five_agreements]]，签署方式取值见 [[processes/agreement_sign_mode]]。

与 [[concepts/authorization-agreement]] 的边界是：协议有文件、有签署模式、有拉取与判重；授权书只有「谁授过权」的关系状态。日常称为「CA 协议」「BS 协议」时指的是签署机构维度上的协议类型，仍属本术语。

## 需求背景
协议集合按产品与类型分散存放于客户端，迁移与展示都需要一个统一的「协议」概念来承载类型、文件与签署事实，故与授权关系记录分离命名。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。