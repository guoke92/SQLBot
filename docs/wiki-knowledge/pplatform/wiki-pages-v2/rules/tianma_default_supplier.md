---
type: rule
title: 天马默认企业类型为供应商
page_key: tianma_default_supplier
domain: 外部渠道与银行对接
status: draft
aliases:
  - 天马默认 SPY
oid: 1
scope:
  databases:
    - cust
sources:
  - code:TianmaService.companyArchive
  - code:CustAccessApplication.getCompanyType
contract_version: "0.1"
belong: rules
---

天马建档请求未传 companyType 时，按供应商角色落库。

## 需求背景
天马渠道的业务场景以供应商建档为主，缺省即视为供应商可避免渠道侧必填改造；内部映射见 [[company_type]]，落库字段见 [[cust_company_info]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 天马默认企业类型为供应商
content: 天马建档请求 companyType 为空时按 CompanyType.SPY 落库（内部映射 CustCompanyTypeEnum.SUPPLIER）
impact: cust_company_info.cust_company_type 取值
field_targets:
  - cust_company_info.cust_company_type
evidence: "code:TianmaService.companyArchive; CustAccessApplication.getCompanyType"
```