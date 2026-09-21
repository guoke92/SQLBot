---
type: concept
title: 电子授权书签署状态
page_key: electronic_auth_sign_status_term
belong: concepts
domain: cust
status: draft
aliases: [electronic_auth_sign_status, 线下电子授权签署状态]
maps_to: cust_change_record.electronic_auth_sign_status
field_targets: [cust_change_record.electronic_auth_sign_status, cust_build_record.electronic_auth_sign_status]
sources: ['code_path:ElectronicAuthSignStatus.java:12', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_change_record, cust_build_record]
also_confused_with: [electronic_auth_flag, direct_init_need_resign, authorization_book]
adjudication: boundary
---

# 电子授权书签署状态

建档单与变更单共用 ElectronicAuthSignStatus：PENDING/SIGNED/UPLOAD_FAILED/FAILED/VOIDED。
补偿任务 OfflineElectronicAuthCompensationJobHandler 扫描两表 PENDING/UPLOAD_FAILED。
VOIDED=直推在途变更被新流水覆盖，补偿不再拾取（仅变更单路径常见）。
不是租户 generate_electronic_auth_flag，也不是 need_resign_auth（Y/N 是否需要重签）。
PENDING 在本列=待签署；与审批 wf_status.PENDING（待发起）、SSO 同步 PENDING、节点待审批等同码不同义。

## 页面链接

- [[tables/cust_build_record]]
- [[tables/cust_change_record]]
- [[dicts/cust_build_record__electronic_auth_sign_status]]
- [[dicts/cust_change_record__electronic_auth_sign_status]]
- [[processes/cust_change_record__electronic_auth_sign_status]]
- [[concepts/authorization_book]]
- [[concepts/direct_init_need_resign]]
- [[concepts/electronic_auth_flag]]
