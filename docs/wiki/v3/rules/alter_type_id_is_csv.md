---
type: rule
title: 变更单变更项是逗号分隔配置主键
page_key: alter_type_id_is_csv
belong: rules
domain: cust
status: draft
field_targets: [cust_change_record.alter_type_id]
sources: ['code_path:CustSyncEventProcessor.java:1898']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_change_record]
---

# 变更单变更项是逗号分隔配置主键

alter_type_id 存多个 cust_change_cfg.id，用 split 后 IN 查询。不要把它当成 item_code，也不要编单列 EQUI_JOIN。


```ground:rule
rule: 变更单变更项是逗号分隔配置主键
field_targets: [cust_change_record.alter_type_id]
impact: query_constraint
content: 'alter_type_id 存多个 cust_change_cfg.id，用 split 后 IN 查询。不要把它当成 item_code，也不要编单列
  EQUI_JOIN。

  '
evidence: code_path:CustSyncEventProcessor.java:1898
```

## 页面链接

- [[tables/cust_change_record]]
