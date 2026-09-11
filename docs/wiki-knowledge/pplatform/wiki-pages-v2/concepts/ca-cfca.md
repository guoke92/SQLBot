---
type: concept
title: CA / CFCA
page_key: concept.ca_cfca
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子签章
  - 数字证书
  - PAPER_LESS
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustCompanyInfoApplication.java
  - db:cust_company_info
  - db:argeement_migratory_record
contract_version: "0.1"
maps_to: "cust_company_info.need_register_ca / ca_register_status；非 AMS 产品走 CFCA（SignAgencyTransferEnum.PAPER_LESS），协议类型 DATA_SOURCE_CFCA_AUTH"
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
adjudication: boundary
also_confused_with:
  - 上上签 / BS（BEST_SIGN）
boundary: "AMS 产品走 BS：need_register_bs / bs_register_status、协议类型 BS_Auth、签署机构 BEST_SIGN；两者开通过程在 openCa 中互斥判断"
sources: ["enrich:wiki-admin"]
---

「CA / CFCA」指产融侧为线下授权书签署准备的电子签章能力：是否需开通由 `need_register_ca` 表达，是否已开通由 `ca_register_status` 表达，二者同时为 `'Y'` 才满足 [[calibers/offline-electronic-auth-trigger]] 的证书前置条件。若企业正在重开 CA，则等开通成功后链式触发签署。

与「上上签 / BS」的边界见 [[calibers/ams-bs-channel]]：AMS 产品走 `BS_Auth`/`BEST_SIGN`，其余产品走 `CFCA_Auth`/`PAPER_LESS`，开通过程在 `openCa` 中互斥判断，因此两个术语不能混用。

## 需求背景
不同产品线的签署渠道不同，电子签章能力的开通状态必须逐渠道记录，才能保证签署编排在「渠道开通中」时安全等待而非误判为不具备条件。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。

相关：[[cust_company_info]]
