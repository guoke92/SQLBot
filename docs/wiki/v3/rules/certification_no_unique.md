---
type: rule
title: 统一社会信用代码不可重复建档
page_key: certification_no_unique
belong: rules
domain: cust
status: draft
field_targets: [cust_company_info.certification_no]
sources: ['code_path:CustCompanyInfoApplication.java:5220']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 统一社会信用代码不可重复建档

同一租户 db_tenant_code 下 certification_no 已存在且不是当前企业时拒绝新增。
例外：自主认证且 BUILD_FAIL 的旧记录允许再建，但必须先删除失败记录，不是静默覆盖。


```ground:rule
rule: 统一社会信用代码不可重复建档
field_targets: [cust_company_info.certification_no]
impact: write_constraint
content: '同一租户 db_tenant_code 下 certification_no 已存在且不是当前企业时拒绝新增。

  例外：自主认证且 BUILD_FAIL 的旧记录允许再建，但必须先删除失败记录，不是静默覆盖。

  '
evidence: code_path:CustCompanyInfoApplication.java:5220
```

## 页面链接

- [[tables/cust_company_info]]
