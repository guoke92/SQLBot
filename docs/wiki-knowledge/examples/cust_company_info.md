---
type: table
title: 企业主档表
page_key: cust_company_info
domain: 企业建档
status: published
aliases: [企业档案, 公司主档, 企业表]
anchors: [cust_company_info]
sources: ["catalog.yaml", "CustCompanyInfo.java"]
created: 2026-08-28
updated: 2026-08-29
tags: [主数据]
related: [cust-build-type, identify-style, 有效企业]
contract_version: "0.1"
---

# 企业主档表

企业主档（cust_company_info）记录企业的建档、认证与状态信息，一行代表一个企业档案，
是[[企业建档流程]]与[[有效企业]]口径的核心表。企业清单类查询的主表。

## 字段

```ground:table
table: cust_company_info
description: 企业主档表
inactive: false
fields:
  - name: cust_build_type
    data_type: string
    description: 建档录入方式
    dictionary: cust_build_type
    nullable: true
  - name: identify_style
    data_type: string
    description: 认证方式
    dictionary: identify_style
    nullable: true
  - name: cust_build_status
    data_type: string
    description: 建档状态
    nullable: false
  - name: cust_status
    data_type: string
    description: 客户状态
    nullable: false
  - name: data_type
    data_type: string
    description: 数据类型（1=正式主数据）
    nullable: false
  - name: enable
    data_type: string
    description: 启用标记（Y/N）
    nullable: false
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_detail.company_id
right: cust_company_info.id
cardinality: many_to_one
cast: null
status: proposed
evidence: code_path:CompanyService.java:88
```

## 业务规则

用户问"企业清单/企业数"而未说明包含无效企业时，默认采用[[有效企业]]口径；
"平台录入"语境见[[平台录入]]与[[cust_build_type]]，勿与[[identify_style|认证方式]]混淆。
