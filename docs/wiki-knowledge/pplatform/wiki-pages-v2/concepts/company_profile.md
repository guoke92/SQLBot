---
type: concept
title: 企业画像
page_key: concepts/company_profile
domain: 企业画像
status: draft
aliases:
  - 客户信息
  - 企业信息主表
  - CustCompanyInfo
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyInfoApplication.java
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
maps_to: cust_company_info / CustCompanyInfoDO
field_targets:
  - cust_company_info.custBuildStatus
  - cust_company_info.custStatus
  - cust_company_info.custCompanyType
  - cust_company_info.certificationNo
  - cust_company_info.dataType
adjudication: synonym
also_confused_with:
  - 企业认证状态
  - 企业客户状态
---

# 企业画像

「企业画像」在本 wiki 中是同义词集合：企业画像 = 客户信息 = 企业信息主表 = `CustCompanyInfo`，代码层落点为 [[tables/cust_company_info]] / `CustCompanyInfoDO`。同义判定的依据是这些叫法在代码与表中指向同一实体，而非不同的视图或聚合。

需要与之划清界限的是两个**字段级状态**概念：企业认证状态（[[processes/cust_company_info_cust_build_status]]，字段 `custBuildStatus`）与企业客户状态（[[processes/cust_company_info_cust_status]]，字段 `custStatus`）。它们是企业画像上的两个属性，不是企业画像本身。说「企业画像变了」时，应进一步确认变的是哪个属性。

企业画像的常用派生口径有三条：生效企业（[[calibers/company_effect]]）、平台运营方唯一（[[calibers/platform_operator_unique]]）、主数据信用代码唯一（[[calibers/main_data_certification_unique]]）。其中 `custCompanyType` 字段还被 GP 学习域引用，用于判定金融机构用户（[[calibers/gptlearn_finance_user]]）。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：企业画像是否对外提供只读视图、是否存在缓存副本。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/cust_company_info]]、[[processes/cust_company_info_cust_build_status]]、[[processes/cust_company_info_cust_status]]、[[calibers/company_effect]]、[[calibers/platform_operator_unique]]、[[calibers/main_data_certification_unique]]、[[calibers/gptlearn_finance_user]]。