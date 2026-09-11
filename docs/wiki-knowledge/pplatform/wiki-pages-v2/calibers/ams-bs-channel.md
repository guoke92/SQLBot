---
type: caliber
title: AMS 走 BS/上上签通道
page_key: caliber.ams_bs_channel
domain: 授权协议与电子授权
status: draft
aliases:
  - AMS 走上上签
  - BS_Auth 与 CFCA_Auth 分流
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatFormMigratoryApplication.java
  - db:argeement_migratory_record
  - db:cust_company_info
contract_version: "0.1"
---

协议类型与签署机构按产品分流：`platform_product_code='AMS'` 时 `agreement_type='BS_Auth'`、签署机构取 `BEST_SIGN`；其他产品取 `CFCA_Auth`，签署机构为 `PAPER_LESS`。这与开通状态字段相呼应——AMS 用 `need_register_bs`/`bs_register_status`，其余产品用 `need_register_ca`/`ca_register_status`，两者在 `openCa` 中互斥判断，术语边界见 [[concepts/ca-cfca]]。

## 需求背景
AMS 产品线使用上上签（BestSign）作为签署渠道，其余产品线使用 CFCA，因此协议迁移初始化与签署机构选择必须按产品分派。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: AMS 走 BS/上上签通道
predicate: "argeement_migratory_record.platform_product_code = 'AMS' → agreement_type = 'BS_Auth'；其他产品 → agreement_type = 'CFCA_Auth'"
scope: "协议迁移初始化与签署机构选择（BEST_SIGN vs PAPER_LESS）"
evidence: "code_path:PlatFormMigratoryApplication.java#getCaAgreement"
```