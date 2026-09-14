---
type: caliber
title: 企业+信用代码+租户三元匹配
page_key: company_certification_tenant_match
domain: 外部渠道与银行对接
status: draft
aliases:
  - 三元匹配口径
  - 信用代码定位企业
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.query
  - code:CustAccessApplication.changeCompanyInfo
contract_version: "0.1"
belong: calibers
---

渠道查询与变更定位企业时，以统一社会信用代码为主键、叠加数据租户与企业角色条件，构成三元匹配。

## 需求背景
由于入站请求的租户上下文为 `all`（[[inbound_all_tenant_context]]），必须显式叠加 db_tenant_code 才能落到正确租户；企业角色列为 JSON 数组、只能用 like 模糊匹配，因此不参与等价性判定（见 [[company_type]]）。信用代码字段名映射见 [[social_unified_code]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 企业+信用代码+租户三元匹配
predicate: "cust_company_info.certification_no = '<socialUnifiedCode>'"
scope: 渠道查询/变更定位企业的核心条件（叠加 db_tenant_code 与 cust_company_type like）
evidence: "code:CustAccessApplication.query / changeCompanyInfo"
```