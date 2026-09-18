---
type: rule
title: 发起变更必须检查在途
page_key: change_requires_onway_check
belong: rules
domain: cust
status: draft
field_targets: [cust_company_info.cust_status, cust_company_info.cust_build_status]
sources: ['code_path:CustCompanyInfoApplication.java:7345']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# 发起变更必须检查在途

企业自行变更在写成 CHANGE/CUST_CHANGE 之前调用 checkBusiOnWayService。
不要把冻结/注销配置里的 needCheckInWay 当成同样实现：那两处还是空 TODO。


```ground:rule
rule: 发起变更必须检查在途
field_targets: [cust_company_info.cust_status, cust_company_info.cust_build_status]
impact: write_constraint
content: '企业自行变更在写成 CHANGE/CUST_CHANGE 之前调用 checkBusiOnWayService。

  不要把冻结/注销配置里的 needCheckInWay 当成同样实现：那两处还是空 TODO。

  '
evidence: code_path:CustCompanyInfoApplication.java:7345
```

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__cust_status]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_status]]
