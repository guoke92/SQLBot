---
type: rule
title: 管理员变更冻旧建新
page_key: freeze_old_create_new_admin
belong: rules
domain: cust
status: draft
field_targets: [cust_person_info.enable, cust_person_info.status]
sources: ['code_path:CustPersonApplication.java:841']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_person_info]
---

# 管理员变更冻旧建新

管理员变更把旧行 enable=N、status=FREEZE 共写，再插入新行 status=EFFECT。
不要把企业冻结理解成同一套：企业 freeze 只改 cust_status 和角色 status，外加 SSO 冻管理员。


```ground:rule
rule: 管理员变更冻旧建新
field_targets: [cust_person_info.enable, cust_person_info.status]
impact: write_constraint
content: '管理员变更把旧行 enable=N、status=FREEZE 共写，再插入新行 status=EFFECT。

  不要把企业冻结理解成同一套：企业 freeze 只改 cust_status 和角色 status，外加 SSO 冻管理员。

  '
evidence: code_path:CustPersonApplication.java:841
```

## 页面链接

- [[tables/cust_person_info]]
- [[dicts/cust_person_info__enable]]
- [[dicts/cust_person_info__status]]
- [[processes/cust_person_info__status]]
