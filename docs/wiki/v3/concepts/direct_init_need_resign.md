---
type: concept
title: 直推变更需重签授权书
page_key: direct_init_need_resign
belong: concepts
domain: cust
status: draft
aliases: [need_resign_auth, 电子授权重签, 重签授权书]
maps_to: cust_change_record.need_resign_auth
field_targets: [cust_change_record.need_resign_auth, cust_change_record.electronic_auth_sign_status,
  cust_change_record.need_cust_confirm]
sources: ['code_path:ChannelChangeDirectItemDetector.java:39', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_change_record]
also_confused_with: [cross_tenant_resign, auth_supplement_flag, electronic_auth_flag,
  auth_channel_flag, electronic_auth_sign_status_term, direct_init_change_record]
adjudication: boundary
---

# 直推变更需重签授权书

need_resign_auth：变更项含 UN0009/UN0012/UN0013/UN0016 时需重签（ChannelChangeDirectItemDetector.needResignAuth）。
Y 时自动补 UN0008 企业授权书；electronic_auth_sign_status=PENDING；企业 cust_status=变更中、建档状态待客户确认。
不是租户 sign_flag（跨贴牌补签），也不是企业 auth_aggrement_supplement_flag / migarory_auth_aggrement_flag，也不是 generate_electronic_auth_flag。

## 页面链接

- [[tables/cust_change_record]]
- [[dicts/cust_change_record__electronic_auth_sign_status]]
- [[dicts/cust_change_record__need_cust_confirm]]
- [[dicts/cust_change_record__need_resign_auth]]
- [[processes/cust_change_record__electronic_auth_sign_status]]
- [[concepts/auth_channel_flag]]
- [[concepts/auth_supplement_flag]]
- [[concepts/cross_tenant_resign]]
- [[concepts/direct_init_change_record]]
- [[concepts/electronic_auth_flag]]
- [[concepts/electronic_auth_sign_status_term]]
