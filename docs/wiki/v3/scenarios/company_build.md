---
type: scenario
title: 企业建档
page_key: company_build
belong: scenarios
domain: cust
status: draft
aliases: [简易建档, 客户建档, 企业认证]
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info, cust_project_rel, cust_role_info, cust_person_info, cust_project_code_record,
  cust_project_pushcust]
---

# 企业建档

客户主档建档/认证。关联项目时并入 cust_project_rel.relation。

```ground:scenario
scenario: company_build
hubs:
- table: cust_company_info
  role: master
shared:
- table: cust_project_rel
  role: project_link
- table: cust_role_info
  role: company_role
- table: cust_person_info
  role: admin_person
- table: cust_project_code_record
  role: project_code
- table: cust_project_pushcust
  role: default_project
lifecycle:
- dict: cust_company_info__cust_build_status
  process: cust_company_info__cust_build_status
- dict: cust_company_info__cust_status
  process: cust_company_info__cust_status
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_person_info]]
- [[tables/cust_project_code_record]]
- [[tables/cust_project_pushcust]]
- [[tables/cust_project_rel]]
- [[tables/cust_role_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__cust_status]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_status]]
