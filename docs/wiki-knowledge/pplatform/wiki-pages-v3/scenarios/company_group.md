---
type: scenario
title: 企业集团关系
page_key: company_group
domain: 企业银行账户/集团/SFTP
status: draft
aliases: [集团成员, 集团树]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:企业银行账户/集团/SFTP"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_group_rel]
field_targets:
  - cust_group_rel.status
  - cust_group_rel.root_flag
---

# 企业集团关系

问「有效集团成员 / 集团根企业」时进入本场景。

**主档** [[cust_group_rel]]：`cust_id` / `parent_cust_id` / `root_cust_id` 都指向 [[cust_company_info]].id。成员列表代码按 `status='EFFECTIVE'` 过滤。

```ground:scenario
scenario: company_group
hubs:
- table: cust_group_rel
  role: master
  grain: 集团树一条边
  window:
  - id
  - enable
  - create_time
  - update_time
  - cust_id
  - parent_cust_id
  - root_cust_id
  - root_flag
  - level
  - cust_type
  - status
shared:
- table: cust_company_info
  role: member
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - name
  - cust_company_type
lifecycle:
- enum: group_rel_status
  process: group_rel_status_flow
```
