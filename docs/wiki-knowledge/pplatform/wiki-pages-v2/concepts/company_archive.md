---
type: concept
title: 建档
page_key: company_archive
domain: 外部渠道与银行对接
status: draft
aliases:
  - companyArchive
  - reg
  - channelArchive
  - 非自主建档
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.setCustCompany
  - code:CustAccessApplication.validateSetValue
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
also_confused_with:
  - cust_company_info.check_status
adjudication: boundary
belong: concepts
field_targets: [cust_company_info.cust_build_status]
sources: ["enrich:wiki-admin"]
---

「建档」指企业在本地的初始化过程及其状态机（cust_build_status），与运营侧的「审核」（check_status）是两条独立主线。

## 需求背景
建档分为自主（isIndependent=true）与非自主两类，校验强度不同（[[independent_archive_validation]]）；失败件与作废件均可重新建档（[[build_fail_reusable]]、[[writeoff_excluded]]）。对外查询的 status 以 check_status 优先映射，仅在 check_status 为空时才回落到建档状态兜底，因此两条状态线不可互相替代（参见 [[check_status]]）。

## 版本演进
暂无版本演进记录。

相关：[[cust_company_info]]
