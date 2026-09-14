---
type: concept
title: org（机构/组织）
page_key: org
domain: cust_org_permission
status: draft
aliases: [机构, 组织, org_manage, sys_org, SysOrgDO, sys_cust_org, SysCustOrgDO]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:OrgFacade
  - code:CustSysOrgApplication
  - code:CustSysOrgController
contract_version: "0.1"
maps_to: [org_manage.id, sys_cust_org.id]
field_targets: [org_manage.id, org_manage.org_type, sys_cust_org.id]
adjudication: boundary
also_confused_with:
  - OrgFacade/OrgController 的租户级机构
  - CustSysOrgApplication/CustSysOrgController 的客户组织架构
belong: concepts
---

「组织/机构」在代码里指向两条完全不同的链路，必须按边界判别，不能互推。一条是租户级机构 org_manage（OrgTypeEnum ORG/SUB、tenant_code/apaaS tenant 维度，入口 CustOrgController /cust-web/org）；另一条是客户组织架构 sys_cust_org + sys_cust_org_rel（custId + companyType 维度，入口 CustSysOrgController /cust-web/sysOrg）。数据权限里的 org_id_list 属于后者，见 [[org_id_list]]；前者见 [[org_manage]]。

## 需求背景
本页仅依据代码证据（OrgFacade、CustSysOrgApplication、CustSysOrgController）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。