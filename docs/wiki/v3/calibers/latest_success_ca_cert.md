---
type: caliber
title: 企业最新一证四步成功行
page_key: latest_success_ca_cert
belong: calibers
domain: ca_fee
status: draft
field_targets: [ca_certification_info.submit_status, ca_certification_info.enable,
  ca_certification_info.cust_id]
sources: ['code_path:CaCertificationInfoAppServiceImpl.java:661']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_certification_info, cust_company_info]
---

# 企业最新一证四步成功行

按企业主键取最新 SUCCESS。不要用 ca_fee_company.ca_status 代替一证四步提交结果。

```ground:caliber
caliber: 企业最新一证四步成功行
field_targets: [ca_certification_info.submit_status, ca_certification_info.enable,
  ca_certification_info.cust_id]
predicate: ca_certification_info.submit_status = 'SUCCESS' AND ca_certification_info.enable
  = 'Y' AND ca_certification_info.cust_id = :company_id
scope: global
boundary: 按企业主键取最新 SUCCESS。不要用 ca_fee_company.ca_status 代替一证四步提交结果。
using_relations:
- left: cust_company_info.id
  right: ca_certification_info.cust_id
evidence: code_path:CaCertificationInfoAppServiceImpl.java:661
```

## 页面链接

- [[tables/ca_certification_info]]
- [[tables/cust_company_info]]
- [[dicts/ca_certification_info__enable]]
- [[dicts/ca_certification_info__submit_status]]
- [[processes/ca_certification_info__submit_status]]
