---
type: scenario
title: 运营人员变更
page_key: oper_change
domain: 企业变更与运营变更
status: draft
aliases: [运营变更, 方案经理变更]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:企业变更与运营变更", "code:page-plan.yaml:数据权限与组织"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_oper_change_record]
field_targets:
  - cust_oper_change_record.change_type
---

# 运营人员变更

问「联系人运营人员变更历史 / 有效运营人员」时进入本场景。这不是企业信息变更 [[company_change]]。

**主档** [[cust_oper_change_record]]，查询固定 `enable='Y'`、按创建时间倒序。  
**共享** [[operation_user]]：运营中台同步人员；`org_manage` 库空，组织树不在本窗。

```ground:scenario
scenario: oper_change
hubs:
- table: cust_oper_change_record
  role: master
  grain: 一次运营人员改派
  window:
  - id
  - enable
  - create_time
  - update_time
  - person_id
  - change_type
  - before_operator_id
  - after_operator_id
shared:
- table: cust_person_info
  role: person
  window:
  - id
  - enable
  - create_time
  - update_time
  - name
  - ref_cust_company_info
- table: operation_user
  role: operator
  window:
  - id
  - enable
  - create_time
  - update_time
  - operation_id
  - operation_name
  - operation_group
  - deleted
lifecycle: []
```
