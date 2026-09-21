---
type: concept
title: 集团成员单位
page_key: group_member_rel
belong: concepts
domain: cust
status: draft
aliases: [集团成员管理, 集团关系]
maps_to: cust_group_rel.status
field_targets: [cust_group_rel.status, cust_group_rel.cust_id, cust_group_rel.root_cust_id]
sources: ['code_path:CustGroupRelApplication.java:710', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_group_rel]
also_confused_with: [core_company]
adjudication: boundary
---

# 集团成员单位

document_claim:集团成员管理.md#13。行在 cust_group_rel，cust_id 是企业主键。
EFFECTIVE 已生效、INEFFECTIVE 未生效、REJECTED 已拒绝。不是企业角色 CORE。
客户端「组织架构树」走 sys 库 Dubbo（SysOrgFacade），本仓 catalog 无对应表，不要用 cust_group_rel 或空表 org_manage 回答。

## 页面链接

- [[tables/cust_group_rel]]
- [[dicts/cust_group_rel__status]]
- [[concepts/core_company]]
