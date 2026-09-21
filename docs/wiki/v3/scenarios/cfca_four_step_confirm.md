---
type: scenario
title: 一证四步聚合提交
page_key: cfca_four_step_confirm
belong: scenarios
domain: ca_fee
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_certification_info]
---

# 一证四步聚合提交

一证四步聚合提交

```ground:scenario
scenario: cfca_four_step_confirm
hubs:
- table: ca_certification_info
  role: master
lifecycle:
- dict: ca_certification_info__submit_status
  process: ca_certification_info__submit_status
```

## 页面链接

- [[tables/ca_certification_info]]
- [[dicts/ca_certification_info__submit_status]]
- [[processes/ca_certification_info__submit_status]]
