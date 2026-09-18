---
type: concept
title: 企业管理员变更
page_key: admin_change_topic
belong: concepts
domain: cust
status: draft
aliases: [管理员变更, 管理员手机号变更, 冻旧建新, UN0012, UN0013, UN0014]
maps_to: cust_person_info__status.FREEZE
field_targets: [cust_person_info__status.FREEZE, cust_person_info.status, cust_person_info.enable,
  cust_person_info.user_type]
sources: ['code_path:CustPersonApplication.java:841', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_person_info]
also_confused_with: [freeze_audit]
adjudication: boundary
---

# 企业管理员变更

需求「企业管理员变更专题」是换人：旧行 enable=N 且 status=FREEZE，新行 status=EFFECT、user_type=accountAdmin。
变更项码 UN0012 管理员变更、UN0013 手机号、UN0014 证件有效期，见 CustUpdateItemCodeConstants 注释。
不是企业冻结留痕表。V1.17 起确认人是新管理员。
document_claim:企业管理员变更专题.md#11

## 页面链接

- [[tables/cust_person_info]]
- [[dicts/cust_person_info__enable]]
- [[dicts/cust_person_info__status]]
- [[dicts/cust_person_info__user_type]]
- [[processes/cust_person_info__status]]
- [[concepts/freeze_audit]]
