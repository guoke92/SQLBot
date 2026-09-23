---
type: concept
title: 讯易链项目运营（对等产融）
page_key: wec_project_ops_peer
belong: concepts
status: draft
anchors: [wec_project_operation_rel.wec_project_id, wec_project_cust_operation_rel.project_id]
field_targets:
  - wec_project_operation_rel.wec_project_id
  - wec_project_cust_operation_rel.project_id
sources: ['orphan_repair:source分流 产融/讯易链']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [wec_project_operation_rel, wec_project_cust_operation_rel, tenant_project, cust_project_rel]
---

# 讯易链项目运营（对等产融）

产融用 `tenant_project` / `cust_project_rel`；讯易链用 `wec_project_operation_rel` / `wec_project_cust_operation_rel`。  
同一运营接口按 `source`（产融 / 讯易链）分流，**ID 空间隔离**，禁止跨域 EQUI_JOIN。

讯易链内部：`wec_project_operation_rel.wec_project_id` → `wec_project_cust_operation_rel.project_id` 可 JOIN。
