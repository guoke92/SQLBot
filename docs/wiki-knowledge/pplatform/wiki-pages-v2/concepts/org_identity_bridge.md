---
type: concept
title: 机构标识桥（org_manage ↔ operation_user）
page_key: concept.org_identity_bridge
domain: 数据权限与组织
status: draft
aliases: [机构标识桥, organization_id, 机构编号]
oid: 1
scope:
  databases: [base]
sources: [db, code, "enrich:wiki-admin"]
contract_version: "0.1"
maps_to:
  - org_manage.organization_id
  - operation_user.organization_id
  - sys_cust_org_user_permission.org_id_list
field_targets:
  - table: operation_user
    field: organization_id
    meaning: 机构编号（指向机构域 org_manage.organization_id）
    evidence: db
  - table: org_manage
    field: organization_id
    meaning: 机构编号（与 operation_user.organization_id 同域的机构主键）
    evidence: db
  - table: org_manage
    field: parent_code
    meaning: 父机构编号（自引用，构成机构树；对应代码 SysOrgDO.parentId/selectByCode 链路）
    evidence: db
  - table: sys_cust_org_user_permission
    field: org_id_list
    meaning: 数据范围组织ID列表（仅 SPECIFIED 必填；SAME_AS_USER_ORG 时由用户组织绑定回填）
    evidence: code
adjudication: 机构域统一以 organization_id 作为跨表引用键；org_manage 内部的树形关系走 parent_code 自引用，不要与 organization_id 混用。
also_confused_with: [org_manage.id, org_no, org_manage.parent_code]
---

术语桥：机构编号 organization_id 是 org_manage 与 operation_user 共同使用的跨域引用键，两者同域。注意 org_manage 自身还有三个易混字段：主键 id、机构号 org_no、以及构成机构树的自引用 parent_code——只有 organization_id 是对外引用的那一个。

下游影响：数据权限的 org_id_list 存放的正是这一域的组织ID，SAME_AS_USER_ORG 时由用户组织绑定回填，见 [[processes/data_permission_type_fsm]] 与 [[rules/specified_requires_org_id_list]]。机构类型取值见 org_manage.org_type（ORG 根机构 / SUB 子机构）。

相关：[[org_manage]]
