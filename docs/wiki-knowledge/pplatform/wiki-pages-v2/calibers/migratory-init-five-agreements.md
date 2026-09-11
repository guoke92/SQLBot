---
type: caliber
title: 迁移初始化五类协议
page_key: caliber.migratory_init_five_agreements
domain: 授权协议与电子授权
status: draft
aliases:
  - 迁移初始化协议类型清单
  - setAgreementMigratory
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatFormMigratoryApplication.java
  - db:argeement_migratory_record
contract_version: "0.1"
---

迁移初始化会为每个客户 × 每个产品生成五类待拉取协议记录：认证类协议（`CFCA_Auth` 或 `BS_Auth`，按 [[calibers/ams-bs-channel]] 分流）、产品协议、`CustPersonLicense`、`UserProtocol`、`PrivacyPolicy`。去重以「该 custId + productCode + type 的记录计数为 0」为条件，避免重复插入；写入后进入 [[calibers/pending-pull-agreement-records]] 描述的拉取流程。

## 需求背景
协议在客户端侧按类型分散存放，迁移必须按类型逐项拉取才能完整还原客户已签署的协议集合，去重条件保证初始化可重入。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 迁移初始化五类协议
predicate: "argeement_migratory_record.agreement_type IN ('CFCA_Auth'|'BS_Auth', 产品协议, 'CustPersonLicense', 'UserProtocol', 'PrivacyPolicy')"
scope: "每个客户×每个产品各生成一条待拉取记录（按 custId+productCode+type 计数为 0 才插入）"
evidence: "code_path:PlatFormMigratoryApplication.java#setAgreementMigratory"
```