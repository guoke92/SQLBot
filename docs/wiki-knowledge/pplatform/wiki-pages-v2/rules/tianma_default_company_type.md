---
type: rule
title: 天马建档默认企业角色为供应商
page_key: tianma_default_company_type
domain: 外部渠道与银行对接
status: draft
aliases:
  - CompanyType.SPY
  - 天马默认 SUPPLIER
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaService#companyArchive
  - code:CustAccessApplication#getCompanyType
contract_version: "0.1"
belong: rules
---

# 天马建档默认企业角色为供应商

## 业务定位

天马入站建档时，若 `req.getCompanyType()` 为空则写入 `CompanyType.SPY.name()`，否则取入参枚举名；随后 `CustAccessApplication#getCompanyType` 将 `SPY` 映射为 `CustCompanyTypeEnum.SUPPLIER` 落入 `cust_company_type`。

## 需求背景

天马场景下的入站企业默认为供应商角色。`cust_company_type` 是 JSON 数组字符串（如 `["SUPPLIER"]`），查询侧用 `like` 模糊匹配（`query` / `batchQuery` / `changeCompanyInfo`），因此写入值必须是对外约定的枚举名，不能写中文或自由文本。

## 影响与约束

天马入站企业若未显式传角色，会在库里被识别为供应商；下游按角色过滤的查询会据此命中。角色是查询键之一，出现"查不到"问题时应先核对本映射是否生效。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析，尚无需求文档或变更单佐证。

```ground:rule
name: 天马建档默认企业角色为供应商
content: "req.getCompanyType() 为空时写入 CompanyType.SPY.name()，否则取入参枚举名；随后 getCompanyType 将 SPY 映射为 CustCompanyTypeEnum.SUPPLIER"
impact: 天马入站默认识别为供应商角色
field_targets:
  - cust_company_info.cust_company_type
evidence: "code:TianmaService#companyArchive, CustAccessApplication#getCompanyType"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 概念：[[concepts/tianma_inbound_outbound]]
- 规则：[[rules/tianma_inbound_validation]]、[[rules/tianma_channel_key]]