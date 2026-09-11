---
type: rule
title: 天马入站参数强校验
page_key: rules/tianma_inbound_validation
domain: 外部渠道与银行对接
status: draft
aliases:
  - TianmaService#companyArchive 必填校验
  - PARAM_NULL
  - PARAM_ERROR
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaService#companyArchive
contract_version: "0.1"
---

# 天马入站参数强校验

## 业务定位

天马入站建档在 `TianmaService#companyArchive` 中以 `Assert` 串做必填校验，必填项为：`specifityCptSocialUnifiedCode`（资金方统一社会信用证）、`coreSocialUnifiedCode`（核心企业）、`companyName`、`socialUnifiedCode`（且长度必须为 18）、`authorizerPersonName`、`authorizerPersonCellphone`、`interestRate`（综合利率）。缺失分别抛 `CloudPcExceptionEnum.PARAM_NULL` / `PARAM_ERROR`。

## 需求背景

天马入站数据直接驱动建档落库：`socialUnifiedCode` 对应 `certification_no` 这一唯一识别键，`companyName` 对应重复校验的匹配键 `name`，`interestRate` 对应 `company_ext_data` 中的综合利率拓展字段。这些字段一旦缺失，后续重复校验、银行账户查询与清分配置都会失效，因此在入站即拒绝，不进建档流程。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析，尚无需求文档或变更单佐证。

```ground:rule
name: 天马入站参数强校验
content: "必填：specifityCptSocialUnifiedCode（资金方统一社会信用证）、coreSocialUnifiedCode（核心企业）、companyName、socialUnifiedCode（且长度必须为18）、authorizerPersonName、authorizerPersonCellphone、interestRate（综合利率）；缺失分别抛 CloudPcExceptionEnum.PARAM_NULL / PARAM_ERROR"
impact: 天马侧字段缺失或不合法会在入站即被拒绝，不进建档流程
field_targets:
  - cust_company_info.name
  - cust_company_info.certification_no
  - cust_company_info.company_ext_data
evidence: "code:TianmaService#companyArchive（Assert 串）"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 概念：[[concepts/tianma_inbound_outbound]]、[[concepts/reg_archive]]
- 规则：[[rules/tianma_default_company_type]]、[[rules/tianma_channel_key]]
- 口径：[[calibers/channel_tenant_mapping]]