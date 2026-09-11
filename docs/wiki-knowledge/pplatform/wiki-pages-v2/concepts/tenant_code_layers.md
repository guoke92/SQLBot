---
type: concept
title: 数据租户与逻辑租户（db_tenant_code / app_tenant_code）
page_key: concept.tenant_code_layers
domain: 数据权限与组织
status: draft
aliases: [数据租户, 逻辑租户, db_tenant_code, app_tenant_code]
oid: 1
scope:
  databases: [base]
sources: [db, code]
contract_version: "0.1"
maps_to:
  - db_tenant_code
  - app_tenant_code
field_targets:
  - table: operation_user
    field: db_tenant_code
    meaning: 数据租户标识；实测仅出现 'base'（7 条），说明该表当前仅承载 base 租户运营人员
    evidence: db
  - table: operation_user
    field: app_tenant_code
    meaning: 逻辑租户标识（与 db_tenant_code 分属逻辑/数据两层）
    evidence: db
  - table: org_manage
    field: db_tenant_code
    meaning: 数据租户标识
    evidence: db
  - table: org_manage
    field: app_tenant_code
    meaning: 逻辑租户标识
    evidence: db
  - table: cust_company_info
    field: db_tenant_code
    meaning: 数据租户标识（跨企业/跨租户查询与写库路由依据）
    evidence: code
adjudication: db_tenant_code 是数据层标识，承担跨企业/跨租户查询与写库路由；app_tenant_code 是逻辑层标识。两者分属逻辑/数据两层，不可互相替代。
also_confused_with: [organization_id, ref_cust_company_info]
---

术语桥：两张表（operation_user、org_manage）同时存在 db_tenant_code 与 app_tenant_code，二者名称相近但层次不同——前者是数据层、后者是逻辑层。产融侧 cust_company_info.db_tenant_code 被明确标注为「跨企业/跨租户查询与写库路由依据」，是判定该桥走向的关键证据。

实际影响：任何按租户的查询必须明确走哪一层。operation_user 实测仅出现 'base'（7 条），说明该表当前只承载 base 租户运营人员，跨租户场景不能在本表上做租户维度推断。相关规则见 [[rules/org_agw_skip_tenant_filter]]（AGW 来源跳过租户过滤）。