---
type: caliber
title: 已生效的冻结解冻留痕
page_key: freeze_audit_record
belong: calibers
domain: cust
status: draft
field_targets: [cust_company_lifecycle_info.enable, cust_company_lifecycle_info.company_id,
  cust_company_lifecycle_info.type, cust_company_lifecycle_info.reason]
sources: ['code_path:CustCompanyInfoApplication.java:7090']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_lifecycle_info, cust_company_info]
---

# 已生效的冻结解冻留痕

回答「冻结/解冻记录」。预生成草稿是 enable=N，确认后才是 Y。
type=FRZ 冻结，type=UNFRZ 解冻。枚举没有中文 displayName，不要把 FRZ 当成别的码。


```ground:caliber
caliber: 已生效的冻结解冻留痕
field_targets: [cust_company_lifecycle_info.enable, cust_company_lifecycle_info.company_id,
  cust_company_lifecycle_info.type, cust_company_lifecycle_info.reason]
predicate: cust_company_lifecycle_info.enable = 'Y' AND cust_company_lifecycle_info.company_id
  = :company_id
scope: global
boundary: '回答「冻结/解冻记录」。预生成草稿是 enable=N，确认后才是 Y。

  type=FRZ 冻结，type=UNFRZ 解冻。枚举没有中文 displayName，不要把 FRZ 当成别的码。

  '
using_relations:
- left: cust_company_info.id
  right: cust_company_lifecycle_info.company_id
evidence: code_path:CustCompanyInfoApplication.java:7090
```

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_company_lifecycle_info]]
- [[dicts/cust_company_lifecycle_info__enable]]
- [[dicts/cust_company_lifecycle_info__type]]
