---
type: rule
title: 同一企业同一角色只能有一个有效管理员
page_key: unique_admin_per_company_role
belong: rules
domain: cust
status: draft
field_targets: [cust_person_info.user_type, cust_person_info.enable, cust_person_info.company_type,
  cust_person_info.ref_cust_company_info]
sources: ['code_path:CustPersonApplication.java:334']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
---

# 同一企业同一角色只能有一个有效管理员

保存/改管理员前统计 company_type + ref_cust_company_info + enable=Y + user_type=accountAdmin（排除自身）必须为 0。
冻结旧管理员（enable=N）后可以再建新管理员。企业冻结不写 person.enable，所以冻结企业仍可能挡住新增管理员。


```ground:rule
rule: 同一企业同一角色只能有一个有效管理员
field_targets: [cust_person_info.user_type, cust_person_info.enable, cust_person_info.company_type,
  cust_person_info.ref_cust_company_info]
impact: write_constraint
content: '保存/改管理员前统计 company_type + ref_cust_company_info + enable=Y + user_type=accountAdmin（排除自身）必须为
  0。

  冻结旧管理员（enable=N）后可以再建新管理员。企业冻结不写 person.enable，所以冻结企业仍可能挡住新增管理员。

  '
evidence: code_path:CustPersonApplication.java:334
```

## 页面链接

- [[tables/cust_person_info]]
- [[dicts/cust_person_info__company_type]]
- [[dicts/cust_person_info__enable]]
- [[dicts/cust_person_info__user_type]]
