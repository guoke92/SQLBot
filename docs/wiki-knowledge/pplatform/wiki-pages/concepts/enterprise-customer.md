---
type: concept
title: 企业客户
page_key: enterprise-customer
domain: 企业建档与准入
status: published
aliases: [企业, 客户公司, 公司]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: cust_company_info
also_confused_with: ["cust_person_info（企业联系人）"]
adjudication: boundary
boundary: cust_company_info 存储企业主体信息，cust_person_info 存储企业下的个人用户信息
field_targets: []
scope:
  databases: [lowcode_pplatform]
---

# 企业客户

企业客户指企业主体信息，存储在 `cust_company_info` 表中，包括企业名称、统一社会信用代码、法人信息、企业角色、认证状态等。它区别于企业下的个人用户信息 `cust_person_info`。

## 需求背景

业务中“企业”“客户公司”“公司”等术语常混用，但数据侧统一指向 `cust_company_info`。企业客户是建档与准入的核心对象，所有认证、生命周期、角色规则均围绕该实体展开。

## 版本演进

本概念由语义分析中的术语桥提炼，映射关系为 `maps_to: cust_company_info`，与个人用户信息边界清晰。详见 [[cust_company_info]] 与 [[联系人_客户人员]]。

相关概念：[[admin]]、[[auth-status]]、[[freeze]]、[[enterprise-role]]