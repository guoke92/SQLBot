---
type: rule
title: 增量幂等建行
page_key: incremental_idempotent_row
domain: CA证书认证
status: draft
aliases: [createOrGetByKey, 幂等建行规则]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
belong: rules
---

createOrGetByKey 以 (cust_id, data_date, head_company_data, submit_status='PENDING') 命中即复用已有行，未命中才新建并生成 batch_no；batchNo 不再进入幂等键。

**影响**：重复触发不产生重复行；跨天重发会产生新行。前者保证门户/中台重复通知下数据不膨胀，后者意味着按 data_date 做日切统计时不能把同一业务跨日合并。

## 需求背景

规则依赖 [[incremental_idempotent_key|增量落库幂等键]] 口径；由于 PENDING 同时是幂等条件，一旦行被置为 SUCCESS/FAIL，再次触发就会新建一行，因此"同样材料出现多行"未必是缺陷。

## 版本演进

- v0：首次固化幂等键构成，并记录 batch_no 被移出幂等键的变更。

```ground:rule
name: 增量幂等建行
content: createOrGetByKey 以 (cust_id, data_date, head_company_data, submit_status='PENDING') 命中即复用已有行，未命中才新建并生成 batch_no；batchNo 不再进入幂等键
impact: 重复触发不产生重复行；跨天重发会产生新行
field_targets:
  - ca_certification_info.cust_id
  - ca_certification_info.data_date
  - ca_certification_info.head_company_data
  - ca_certification_info.submit_status
  - ca_certification_info.batch_no
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#createOrGetByKey"
```

关联页面：[[ca_certification_info]]、[[incremental_idempotent_key]]、[[batch_no]]、[[submit_idempotent_short_circuit]]。