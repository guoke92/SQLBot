---
type: concept
title: 建档
page_key: build
domain: 客户中心
status: draft
aliases:
  - 认证
  - 企业认证
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:checkMessage
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
also_confused_with:
  - cust_person_info.cust_build_status
adjudication: boundary
belong: concepts
field_targets: [cust_company_info.cust_build_status]
---

「建档/认证」统一指企业级建档状态 [[cust_company_info]].cust_build_status，取值来自 CustBuildStatusEnum，流转见 [[company_build_status]]。注意 [[cust_person_info]] 上存在同名字段 cust_build_status，属联系人维度的冗余字段，企业级判定应以企业主档为准。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。