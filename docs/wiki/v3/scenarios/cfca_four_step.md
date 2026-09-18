---
type: scenario
title: CFCA 一证四步
page_key: cfca_four_step
belong: scenarios
domain: ca_fee
status: draft
aliases: [开通CA, 证书升级采集]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_certification_info, cust_company_info]
---

# CFCA 一证四步

门户 /cust-web/ca 采集 JSON 列，PENDING 提交后 SUCCESS/FAIL。与 CA 服务费订单不是同一张表。

```ground:scenario
scenario: cfca_four_step
hubs:
- table: ca_certification_info
  role: master
shared:
- table: cust_company_info
  role: company
lifecycle:
- dict: ca_certification_info__submit_status
  process: ca_certification_info__submit_status
```

## 页面链接

- [[tables/ca_certification_info]]
- [[tables/cust_company_info]]
- [[dicts/ca_certification_info__submit_status]]
- [[processes/ca_certification_info__submit_status]]
