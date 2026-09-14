---FILE: tables/sys_cust_org_user_permission.md ---
---
type: table
title: sys_cust_org_user_permission（用户数据权限表）
page_key: sys_cust_org_user_permission
domain: cust_org_permission
status: draft
aliases: [用户数据权限表, 数据权限表, sys_cust_org_user_permission]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

sys_cust_org_user_permission 是「数据权限」的落库表：它把某个用户在某企业某角色下可见的组织范围固化成一行记录。读侧由数据权限查询决定返回值，写侧由保存动作校验准入，两侧共用同一张表，因此它同时承载准入口径与默认兜底口径。

本表与 [[cust_person_info]]（判定是否为 [[admin]]）、[[cust_company_info]]（企业与企业角色）、[[permission_type]]、[[org_id_list]] 紧密相关；行为受 [[data_permission_save_admin_only]]、[[specified_requires_org_list]]、[[enterprise_admin_fixed_all]]、[[default_same_as_user_org_backfill]] 约束，值域见流程 [[data_permission_permission_type]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:table
table: sys_cust_org_user_permission
evidence: [code]
fields:
  - name: permission_type
    type: unknown
    desc: 数据权限类型，取值 ALL / SPECIFIED / SAME_AS_USER_ORG（String 字面量常量，非枚举）
    dict: permission_type
  - name: user_id
    type: unknown
    desc: 数据权限归属的用户 ID（sys_user.id）
    dict: ""
  - name: company_id
    type: unknown
    desc: 数据权限所属企业 ID（cust_company_info.id），保存时必须等于当前登录企业
    dict: ""
  - name: company_type
    type: unknown
    desc: 企业角色类型（companyType），与当前登录角色必须一致才可保存
    dict: company_type
  - name: org_id_list
    type: unknown
    desc: 数据范围组织 ID 列表；SPECIFIED 时来自请求，SAME_AS_USER_ORG 且为空时由用户组织绑定回填
    dict: ""
```
---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info（企业联系人）
page_key: cust_person_info
domain: cust_org_permission
status: draft
aliases: [企业联系人, 人员联系人表, cust_person_info]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
  - code:CustSysOrgApplication.java
contract_version: "0.1"
---

cust_person_info 描述「一个用户在某个企业内以什么身份存在」。它是数据权限与组织绑定两条链路的共同入口：能否配置数据权限、能否被挂到组织下，都要回到本表的 user_type、enable、company_type 与 ref_cust_company_info 上判定。

企业归属通过 ref_cust_company_info（指向 cust_company_info.code）而非主键表达，与 [[cust_id_company_id]] 讨论的 id/code 双轨一致。管理员身份见 concept [[admin]]，角色维度见 [[company_type]]，相关约束见 [[data_permission_save_admin_only]] 与 [[bind_org_user_requires_enabled_contact]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication、CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:table
table: cust_person_info
evidence: [code]
fields:
  - name: user_type
    type: unknown
    desc: 用户在企业内的类型：admin（管理员）/operator（经办人）/guest（游客）；数据权限判定只看 admin
    dict: user_type
  - name: company_type
    type: unknown
    desc: 该联系人所归属的企业角色类型（companyType），组织绑定与数据权限均按此维度隔离
    dict: company_type
  - name: ref_cust_company_info
    type: unknown
    desc: 所属企业业务编码，指向 cust_company_info.code（非主键 id）
    dict: ""
  - name: enable
    type: unknown
    desc: 联系人启用标识 Y/N；查管理员/绑定用户均要求 Y
    dict: ""
  - name: phone
    type: unknown
    desc: 手机号（加密存储）；管理员判定用 encryptAndBase64Str(sysUser.userName) 等值比较
    dict: ""
```
---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（客户企业主数据）
page_key: cust_company_info
domain: cust_org_permission
status: draft
aliases: [客户企业, 企业主数据, cust_company_info]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
  - code:CustSysOrgApplication.java
  - code:CustGroupRelApplication.java
contract_version: "0.1"
---

cust_company_info 是企业侧主数据：它给出企业角色（cust_company_type，JSON 数组，支持多角色）、建档认证状态（cust_build_status）、租户标识（db_tenant_code）以及启用/测试数据标记。组织初始化、集团导入与运营方解析都以本表为过滤起点。

建档状态见流程 [[cust_build_status]] 与口径 [[build_success_cust_scope]]、[[enabled_cust_scope]]；租户维度见 [[tenant_isolation_scope]]；企业角色语义见 [[company_type]]；主键与编码的区别见 [[cust_id_company_id]]。组织导入还要求一级组织名称等于本表 name（见 [[org_import_root_name_equals_company_name]]）。

## 需求背景
本页仅依据代码证据（DataPermissionApplication、CustSysOrgApplication、CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:table
table: cust_company_info
evidence: [code]
fields:
  - name: cust_build_status
    type: unknown
    desc: 企业建档/认证状态，组织初始化与组织操作的前置门槛（BUILD_SUCCESS）
    dict: cust_build_status
  - name: cust_company_type
    type: unknown
    desc: 企业角色类型，JSON 数组字符串（如 ["SUPPLIER"]），支持多角色
    dict: company_type
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识，查 sys 用户、集团关系与运营方范围的隔离键
    dict: ""
  - name: enable
    type: unknown
    desc: 企业启用标识 Y/N
    dict: ""
  - name: test_data
    type: unknown
    desc: 测试数据标识 Y；同租户存在多个运营方时过滤该标记保留真实运营方
    dict: ""
  - name: name
    type: unknown
    desc: 企业名称，组织导入的一级组织名称必须与之相等
    dict: ""
```
---END FILE---

---FILE: tables/cust_group_rel.md ---
---
type: table
title: cust_group_rel（集团关系）
page_key: cust_group_rel
domain: cust_org_permission
status: draft
aliases: [集团关系表, 集团成员关系, cust_group_rel]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
contract_version: "0.1"
---

cust_group_rel 描述企业之间的集团关系：一条记录把一个企业挂到某个集团节点上，并用 status 表达是否生效、用 level 与 root_flag 表达树形层级。导入建关系时默认 INEFFECTIVE，需要显式生效动作才进入可见范围。

状态值域见流程 [[cust_group_rel_status]]；生效范围与根节点范围见 [[effective_group_rel_scope]]、[[root_group_rel_scope]]；树的 id 与企业的 id 不可混用，见 [[group_id]]；父子角色一致性见 [[group_import_parent_child_role_consistency]]。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:table
table: cust_group_rel
evidence: [code]
fields:
  - name: status
    type: unknown
    desc: 集团关系状态：INEFFECTIVE（未生效）/EFFECTIVE（已生效），导入建关系默认 INEFFECTIVE
    dict: cust_group_rel_status
  - name: cust_type
    type: unknown
    desc: 该集团关系记录对应的企业角色类型，JSON 数组字符串
    dict: company_type
  - name: root_flag
    type: unknown
    desc: 根标识，根集团关系写死 "Y"
    dict: ""
  - name: level
    type: unknown
    desc: 集团层级，根节点 = 1
    dict: ""
```
---END FILE---

---FILE: tables/operation_user.md ---
---
type: table
title: operation_user（运营中台人员）
page_key: operation_user
domain: cust_org_permission
status: draft
aliases: [运营中台人员, 运营人员表, operation_user]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:operation_user
contract_version: "0.1"
---

operation_user 是运营中台侧的人员表。与客户侧联系人不同，它用 deleted 与 enable 两套独立开关控制有效性，主键 operation_id 被 cust_person_info.operator_id 引用，是运营中台身份与客户企业联系人之间的挂接点。

两套开关的语义不能互相替代：deleted 表达记录是否被删除，enable 表达记录是否启用，取值分布来自库内实测证据。客户侧企业维度见 [[cust_company_info]]，角色维度见 [[company_type]]。

## 需求背景
本页仅依据库内实测数据（db）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:table
table: operation_user
evidence: [db]
fields:
  - name: deleted
    type: unknown
    desc: 删除标识（实测 N=119 / Y=22），与 enable 为两套独立开关
    dict: ""
  - name: enable
    type: unknown
    desc: 启用标识（实测 Y=132 / N=9）
    dict: ""
  - name: operation_id
    type: unknown
    desc: 运营中台人员 ID，被 cust_person_info.operator_id 引用
    dict: ""
```
---END FILE---

---FILE: tables/org_manage.md ---
---
type: table
title: org_manage（租户级机构）
page_key: org_manage
domain: cust_org_permission
status: draft
aliases: [机构表, 租户机构, org_manage]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:OrgTypeEnum
  - db:org_manage
contract_version: "0.1"
---

org_manage 是租户级机构表，与客户组织架构（sys_cust_org、sys_cust_org_rel）是两条不同链路，同名「组织/机构」不可互推，判别见 concept [[org]]。其 org_type 写值来自 OrgTypeEnum（ORG 根 / SUB 子），status 为 varchar(10)，本链路未见写值点。

## 需求背景
本页仅依据代码证据（OrgTypeEnum）与库证据（org_manage）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:table
table: org_manage
evidence: [code, db]
fields:
  - name: org_type
    type: unknown
    desc: 机构类型，写值来自 OrgTypeEnum（ORG 根/SUB 子）
    dict: org_type
  - name: status
    type: varchar(10)
    desc: 机构状态（varchar(10)），本链路未见写值点
    dict: ""
```
---END FILE---

---FILE: processes/data_permission_permission_type.md ---
---
type: process
title: 数据权限类型（permission_type）
page_key: data_permission_permission_type
domain: cust_org_permission
status: draft
aliases: [数据权限类型, permission_type, ALL, SPECIFIED, SAME_AS_USER_ORG]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

数据权限类型是枚举式字符串常量的取值域，落在 [[sys_cust_org_user_permission]].permission_type 上。它描述「能看到多少组织」，与用户身份（user_type）不是一回事，边界见 [[permission_type]]。

保存路径不产生状态跃迁：传入什么类型就写什么类型，SPECIFIED 另加组织列表非空校验（[[specified_requires_org_list]]）。查询路径则存在两处隐式赋值：管理员固定 ALL（[[enterprise_admin_fixed_all]]），非管理员无记录或类型为空时兜底 SAME_AS_USER_ORG 并回填组织（[[default_same_as_user_org_backfill]]）。相关口径见 [[admin_permission_scope]]、[[specified_permission_scope]]、[[default_permission_scope]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:process
name: 数据权限类型
field: sys_cust_org_user_permission.permission_type
states:
  - value: ALL
    label: 全部数据（管理员固定）
    source: code_const
  - value: SPECIFIED
    label: 指定组织范围
    source: code_const
  - value: SAME_AS_USER_ORG
    label: 与用户组织绑定一致（默认兜底）
    source: code_const
transitions:
  - from: ALL
    event: 保存/批量保存并传入 permissionType
    to: ALL
    evidence: code_path:DataPermissionApplication.java:saveDataPermission
  - from: SPECIFIED
    event: 保存且 orgIdList 非空
    to: SPECIFIED
    evidence: code_path:DataPermissionApplication.java:saveDataPermission
  - from: SPECIFIED
    event: 保存但 orgIdList 为空
    to: SPECIFIED
    evidence: code_path:DataPermissionApplication.java:saveDataPermission（抛 CommonException 中断）
  - from: ""
    event: 查询：无记录或 permissionType 为空（非管理员）
    to: SAME_AS_USER_ORG
    evidence: code_path:DataPermissionApplication.java:getByUserCompanyType
  - from: ALL
    event: 查询：判断为企业管理员（userType=admin 且 enable=Y）
    to: ALL
    evidence: code_path:DataPermissionApplication.java:isEnterpriseAdmin
```
---END FILE---

---FILE: processes/cust_group_rel_status.md ---
---
type: process
title: 集团关系状态（cust_group_rel.status）
page_key: cust_group_rel_status
domain: cust_org_permission
status: draft
aliases: [集团关系状态, INEFFECTIVE, EFFECTIVE, cust_group_rel.status]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
  - code:CustCompanyInfoApplication.java
contract_version: "0.1"
---

集团关系记录在 [[cust_group_rel]] 上以 status 表达是否生效。导入/建关系默认落在 INEFFECTIVE，只有显式生效动作（或建档成功后的集团简易认证确认）才进入 EFFECTIVE；子公司平铺查询只认 EFFECTIVE（[[effective_group_rel_scope]]）。

相关：[[group_id]]（group id 与 cust id 不可混用）、[[root_group_rel_scope]]、[[group_import_parent_child_role_consistency]]、[[cust_build_status]]（建档成功是集团确认链路的前置）。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication、CustCompanyInfoApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:process
name: 集团关系状态
field: cust_group_rel.status
states:
  - value: INEFFECTIVE
    label: 未生效
    source: code_const
  - value: EFFECTIVE
    label: 已生效
    source: code_const
transitions:
  - from: INEFFECTIVE
    event: effectGroupRel(custId, custType)
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.java:effectGroupRel
  - from: INEFFECTIVE
    event: 建档成功集团简易认证确认
    to: EFFECTIVE
    evidence: code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
```
---END FILE---

---FILE: processes/cust_build_status.md ---
---
type: process
title: 企业建档/认证状态（cust_build_status）
page_key: cust_build_status
domain: cust_org_permission
status: draft
aliases: [建档状态, 企业认证状态, cust_build_status, BUILD_SUCCESS]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustCompanyInfoApplication.java
contract_version: "0.1"
---

[[cust_company_info]].cust_build_status 描述企业从初始到建档成功/驳回的流转。本状态是组织侧动作的前置门槛：只有 BUILD_SUCCESS 的企业才能初始化根组织、增改组织（[[build_success_cust_scope]]、[[org_operate_requires_build_success]]），并配合 enable='Y' 构成「有效企业」（[[enabled_cust_scope]]）。

状态值由 [[cust_company_info]] 的当前值配合提交/审核动作推进；与集团关系链路衔接处见 [[cust_group_rel_status]]。

## 需求背景
本页仅依据代码证据（CustCompanyInfoApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:process
name: 企业建档/认证状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始
    source: code_const
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_const
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证提交态）
    source: code_const
  - value: CUST_BUILDING
    label: 审核中
    source: code_const
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_const
  - value: BUILD_FAIL
    label: 建档驳回
    source: code_const
transitions:
  - from: ""
    event: 提交（按 identifyStyle 判定）
    to: CUST_CONFIRM_AWAIT / CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java:getCustBuildStatus
  - from: INIT
    event: 提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交送审
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
```
---END FILE---

---FILE: calibers/enterprise_admin_scope.md ---
---
type: caliber
title: 企业管理员判定范围
page_key: enterprise_admin_scope
domain: cust_org_permission
status: draft
aliases: [企业管理员判定, user_type=admin, 管理员口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

本口径回答「谁是管理员」：只看 [[cust_person_info]].user_type='admin'，并叠加以启用与手机号等值匹配为条件的实际判定实现（见 [[admin]]、[[data_permission_save_admin_only]]、[[enabled_contact_scope]]）。它是数据权限编辑准入与管理员固定 ALL（[[enterprise_admin_fixed_all]]）共同依赖的过滤条件。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 企业管理员判定范围
predicate: "cust_person_info.user_type = 'admin'"
scope: 数据权限编辑准入、管理员固定 ALL 判定
evidence: code_path:DataPermissionApplication.java:assertCurrentUserIsAdminOfTargetCompany,isEnterpriseAdmin
```
---END FILE---

---FILE: calibers/enabled_contact_scope.md ---
---
type: caliber
title: 启用联系人范围
page_key: enabled_contact_scope
domain: cust_org_permission
status: draft
aliases: [启用联系人, enable=Y, 联系人有效口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
  - code:CustSysOrgApplication.java
contract_version: "0.1"
---

本口径把 [[cust_person_info]].enable='Y' 作为联系人「有效」的门槛，供管理员/经办人查询与组织绑定校验复用。禁用联系人既不能被判为管理员，也不能被挂到组织下（见 [[bind_org_user_requires_enabled_contact]]）。

## 需求背景
本页仅依据代码证据（DataPermissionApplication、CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 启用联系人范围
predicate: "cust_person_info.enable = 'Y'"
scope: 管理员/经办人查询、组织绑定校验
evidence: code_path:DataPermissionApplication.java:isEnterpriseAdmin
```
---END FILE---

---FILE: calibers/build_success_cust_scope.md ---
---
type: caliber
title: 建档成功企业范围
page_key: build_success_cust_scope
domain: cust_org_permission
status: draft
aliases: [建档成功企业, BUILD_SUCCESS 范围, 建档准入口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
---

本口径以 [[cust_company_info]].cust_build_status='BUILD_SUCCESS' 圈定可做组织动作的企业集合，是 [[org_operate_requires_build_success]] 的判定基础。状态流转见 [[cust_build_status]]。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 建档成功企业范围
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS'"
scope: 初始化根组织、加/改组织的准入条件
evidence: code_path:CustSysOrgApplication.java:checkCustBuildStatus,listBuildSuccessCusts
```
---END FILE---

---FILE: calibers/enabled_cust_scope.md ---
---
type: caliber
title: 有效企业范围
page_key: enabled_cust_scope
domain: cust_org_permission
status: draft
aliases: [有效企业, enable=Y 企业, 企业启用口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
---

本口径以 [[cust_company_info]].enable='Y' 标识企业是否有效。它与建档成功条件是并列的两把尺子：组织初始化批处理通常要求二者同时成立（[[build_success_cust_scope]]），用户绑定查企业也走本口径。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 有效企业范围
predicate: "cust_company_info.enable = 'Y'"
scope: 组织初始化批处理、用户绑定查企业
evidence: code_path:CustSysOrgApplication.java:listBuildSuccessCusts
```
---END FILE---

---FILE: calibers/effective_group_rel_scope.md ---
---
type: caliber
title: 集团关系生效范围
page_key: effective_group_rel_scope
domain: cust_org_permission
status: draft
aliases: [集团关系生效范围, EFFECTIVE 过滤, 生效集团口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
contract_version: "0.1"
---

本口径限定集团树只展示已生效关系：[[cust_group_rel]].status='EFFECTIVE'。状态流转见 [[cust_group_rel_status]]，根节点识别另见 [[root_group_rel_scope]]。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 集团关系生效范围
predicate: "cust_group_rel.status = 'EFFECTIVE'"
scope: listSubCust 子公司平铺结果过滤
evidence: code_path:CustGroupRelApplication.java:listSubCust
```
---END FILE---

---FILE: calibers/root_group_rel_scope.md ---
---
type: caliber
title: 根集团关系范围
page_key: root_group_rel_scope
domain: cust_org_permission
status: draft
aliases: [根集团关系, level=1, 根节点口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
contract_version: "0.1"
---

本口径以 [[cust_group_rel]].level=1 识别根节点，与 root_flag（根标识写死 "Y"）互为印证。注意此处用的是集团关系记录自身，而非企业主键，见 [[group_id]]。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 根集团关系范围
predicate: "cust_group_rel.level = 1"
scope: 根节点识别
evidence: code_path:CustGroupRelApplication.java:processGroupByParent
```
---END FILE---

---FILE: calibers/specified_permission_scope.md ---
---
type: caliber
title: 指定组织权限范围
page_key: specified_permission_scope
domain: cust_org_permission
status: draft
aliases: [指定组织权限, SPECIFIED 口径, 指定范围]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

本口径把 [[sys_cust_org_user_permission]].permission_type='SPECIFIED' 与「组织列表必须非空」绑定，构成保存时的硬校验，见 [[specified_requires_org_list]] 与 [[org_id_list]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 指定组织权限范围
predicate: "sys_cust_org_user_permission.permission_type = 'SPECIFIED'"
scope: 保存时强制校验 orgIdList 非空
evidence: code_path:DataPermissionApplication.java:saveDataPermission
```
---END FILE---

---FILE: calibers/default_permission_scope.md ---
---
type: caliber
title: 默认数据权限范围
page_key: default_permission_scope
domain: cust_org_permission
status: draft
aliases: [默认数据权限, SAME_AS_USER_ORG 兜底, 兜底口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

非管理员在查不到记录或类型为空时落到本口径：按 [[sys_cust_org_user_permission]].permission_type='SAME_AS_USER_ORG' 兜底，并用用户组织绑定回填 [[org_id_list]]。语义边界见 [[same_as_user_org]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 默认数据权限范围
predicate: "sys_cust_org_user_permission.permission_type = 'SAME_AS_USER_ORG'"
scope: 非管理员无记录/类型为空时的兜底
evidence: code_path:DataPermissionApplication.java:getByUserCompanyType,listByCompany
```
---END FILE---

---FILE: calibers/admin_permission_scope.md ---
---
type: caliber
title: 管理员数据权限范围
page_key: admin_permission_scope
domain: cust_org_permission
status: draft
aliases: [管理员数据权限, ALL 口径, 管理员全量范围]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

本口径指管理员查询时固定返回的 permission_type='ALL'，不读权限库，见 [[enterprise_admin_fixed_all]] 与 [[admin]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 管理员数据权限范围
predicate: "sys_cust_org_user_permission.permission_type = 'ALL'"
scope: 企业管理员查询固定返回值（不读库）
evidence: code_path:DataPermissionApplication.java:getByUserCompanyType
```
---END FILE---

---FILE: calibers/tenant_isolation_scope.md ---
---
type: caliber
title: 租户隔离范围
page_key: tenant_isolation_scope
domain: cust_org_permission
status: draft
aliases: [租户隔离, db_tenant_code 口径, 租户过滤]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
  - code:CustGroupRelApplication.java
contract_version: "0.1"
---

本口径以 [[cust_company_info]].db_tenant_code = 入参租户为隔离键，作用于组织初始化、集团导入与运营方查询。运营方场景还叠加 test_data 过滤（见 [[cust_company_info]]）。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication、CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 租户隔离范围
predicate: "cust_company_info.db_tenant_code = 入参租户"
scope: 组织初始化、集团导入、运营方查询
evidence: code_path:CustSysOrgApplication.java:listBuildSuccessCusts；CustGroupRelApplication.java:queryTenantOperatorCompany
```
---END FILE---

---FILE: concepts/org.md ---
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
---

「组织/机构」在代码里指向两条完全不同的链路，必须按边界判别，不能互推。一条是租户级机构 org_manage（OrgTypeEnum ORG/SUB、tenant_code/apaaS tenant 维度，入口 CustOrgController /cust-web/org）；另一条是客户组织架构 sys_cust_org + sys_cust_org_rel（custId + companyType 维度，入口 CustSysOrgController /cust-web/sysOrg）。数据权限里的 org_id_list 属于后者，见 [[org_id_list]]；前者见 [[org_manage]]。

## 需求背景
本页仅依据代码证据（OrgFacade、CustSysOrgApplication、CustSysOrgController）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。
---END FILE---

---FILE: concepts/company_type.md ---
---
type: concept
title: companyType（企业角色类型）
page_key: company_type
domain: cust_org_permission
status: draft
aliases: [company_type, custType, roleType, 企业角色类型, custCompanyType]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication
  - code:CustSysOrgApplication
contract_version: "0.1"
maps_to: [cust_person_info.company_type, cust_company_info.cust_company_type, cust_role_info.role_type]
field_targets: [cust_person_info.company_type, cust_company_info.cust_company_type, cust_role_info.role_type, cust_group_rel.cust_type]
adjudication: synonym
also_confused_with: []
---

companyType、custType、roleType、custCompanyType 是同一取值域的别名（SUPPLIER/CORE/DEALER/FINANCE/CORPORATION_COMPANY/PLATFORM_OPERATOR_COMPANY 等），差别只在存储形态：[[cust_company_info]].cust_company_type 与 [[cust_group_rel]].cust_type 是 JSON 数组字符串（多角色），[[cust_person_info]].company_type 与 cust_role_info.role_type 是单值。initRootOrgBatchOneCompany 直接把 roleType 当 companyType 使用，是二者同义的直接证据。

## 需求背景
本页仅依据代码证据（DataPermissionApplication、CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。
---END FILE---

---FILE: concepts/permission_type.md ---
---
type: concept
title: permissionType（数据权限类型）
page_key: permission_type
domain: cust_org_permission
status: draft
aliases: [permission_type, ALL, SPECIFIED, SAME_AS_USER_ORG, PERMISSION_ALL, PERMISSION_SPECIFIED, PERMISSION_SAME_AS_USER_ORG]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication
contract_version: "0.1"
maps_to: sys_cust_org_user_permission.permission_type
field_targets: [sys_cust_org_user_permission.permission_type, sys_cust_org_user_permission.org_id_list]
adjudication: boundary
also_confused_with:
  - UserTypeEnum（admin/operator/guest）
  - 菜单权限 code
  - UserInfoFacade.ROLE_CODE_*
---

permission_type 描述「数据可见范围」，userType 描述「用户在企业中的身份」，菜单/角色权限（code、ROLE_CODE_*）又是另一套，三者不可互换。DataPermissionApplication 注释明确只支持 ALL、SPECIFIED、SAME_AS_USER_ORG，不做 SAME_AS_ORG 映射。取值域与流转见 [[data_permission_permission_type]]，落库见 [[sys_cust_org_user_permission]]，身份维度见 [[admin]]，兜底语义见 [[same_as_user_org]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。
---END FILE---

---FILE: concepts/admin.md ---
---
type: concept
title: 管理员
page_key: admin
domain: cust_org_permission
status: draft
aliases: [admin, 企业管理员, 平台管理员]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
maps_to: cust_person_info.user_type
field_targets: [cust_person_info.user_type, cust_person_info.enable, cust_person_info.phone]
adjudication: boundary
also_confused_with:
  - 需求文档中的平台管理员（跨企业）
---

代码中可判定的只有企业内管理员：[[cust_person_info]].user_type='admin' 且 enable='Y'，且 phone 与登录用户名密文一致。数据权限保存额外要求 companyId 必须等于当前登录企业，即无法跨企业代理配置（[[data_permission_save_admin_only]]）。需求文档中的「平台管理员」是跨企业概念，与代码可判定范围不同，不可据其推断权限行为。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。
---END FILE---

---FILE: concepts/cust_id_company_id.md ---
---
type: concept
title: custId / companyId
page_key: cust_id_company_id
domain: cust_org_permission
status: draft
aliases: [企业id, cust_company_info.id]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
  - code:CustSysOrgApplication.java
contract_version: "0.1"
maps_to: cust_company_info.id
field_targets: [cust_company_info.id, cust_person_info.ref_cust_company_info, sys_cust_org_user_permission.company_id]
adjudication: boundary
also_confused_with:
  - cust_company_info.code（ref_cust_company_info / custCode）
---

custId/companyId 指 [[cust_company_info]].id 自增主键；refCustCompanyInfo 与 ref_cust_project_rel_cust_company_info 则是 code 业务编码。[[cust_person_info]] 同时保存 cust_company_id（主键）与 ref_cust_company_info（code），查询条件混用会出现看似「查不到数据」的问题，改条件时必须先确认用的是哪一轨。

## 需求背景
本页仅依据代码证据（DataPermissionApplication、CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。
---END FILE---

---FILE: concepts/group_id.md ---
---
type: concept
title: groupId
page_key: group_id
domain: cust_org_permission
status: draft
aliases: [rootGroupId, parentGroupId, id]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
contract_version: "0.1"
maps_to: cust_group_rel.id
field_targets: [cust_group_rel.id, cust_group_rel.cust_id, cust_group_rel.root_cust_id]
adjudication: boundary
also_confused_with:
  - cust_group_rel.cust_id / root_cust_id
---

rootGroupId/parentGroupId 指向 [[cust_group_rel]] 自身记录 id，rootCustId/parentCustId 指向 [[cust_company_info]].id。树构建一律用 group id，业务归属一律用 cust id；在集团查询与导入场景里混用会直接改变结果集。相关流程见 [[cust_group_rel_status]]，范围见 [[root_group_rel_scope]]。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。
---END FILE---

---FILE: concepts/org_id_list.md ---
---
type: concept
title: orgIdList
page_key: org_id_list
domain: cust_org_permission
status: draft
aliases: [orgIds, org_id_list]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
maps_to: sys_cust_org_user_permission.org_id_list
field_targets: [sys_cust_org_user_permission.org_id_list, sys_cust_org_user_permission.permission_type]
adjudication: synonym
also_confused_with:
  - PlatCustOrgDTO.orgId
---

orgIdList / orgIds / org_id_list 都是 sys_cust_org 的 id 集合，属客户组织架构一路（见 [[org]]）。SAME_AS_USER_ORG 回填时经 listCustUserOrgs 得到并按 orgId 去重，来源是用户组织绑定而不是角色默认组织，见 [[same_as_user_org]]；SPECIFIED 下该字段非空是保存硬条件（[[specified_requires_org_list]]）。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。
---END FILE---

---FILE: concepts/same_as_user_org.md ---
---
type: concept
title: SAME_AS_USER_ORG
page_key: same_as_user_org
domain: cust_org_permission
status: draft
aliases: [SAME_AS_USER_ORG]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
maps_to: permission_type.SAME_AS_USER_ORG
field_targets: [sys_cust_org_user_permission.permission_type, sys_cust_org_user_permission.org_id_list]
adjudication: boundary
also_confused_with:
  - SAME_AS_ORG
---

saveDataPermission 注释明确「不做 SAME_AS_ORG 映射」；查询/列表遇到空类型才回填本值，且回填的 [[org_id_list]] 是用户组织绑定而非角色默认组织。它是兜底而非用户可选配置的等价物，见 [[default_permission_scope]] 与 [[data_permission_permission_type]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。
---END FILE---

---FILE: rules/data_permission_save_admin_only.md ---
---
type: rule
title: 数据权限仅本企业管理员可保存
page_key: data_permission_save_admin_only
domain: cust_org_permission
status: draft
aliases: [数据权限保存准入, 本企业管理员校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

保存/批量保存数据权限前先做三重校验：企业一致、角色一致、人合法。它决定了业务侧无法替其它企业配置权限，也决定 [[enterprise_admin_scope]] 与 [[enabled_contact_scope]] 是保存链路的必经过滤。落库对象见 [[sys_cust_org_user_permission]]，身份语义见 [[admin]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 数据权限仅本企业管理员可保存
content: 保存/批量保存前校验：companyId 必须等于当前登录企业、companyType 与当前登录角色一致、当前用户为 cust_person_info.user_type='admin' 且 enable='Y' 且 phone 匹配登录用户名密文。
impact: 越权配置数据权限被拒绝；业务侧无法替其它企业配置。
field_targets:
  - cust_person_info.user_type
  - cust_person_info.enable
  - cust_person_info.phone
  - sys_cust_org_user_permission.company_id
evidence: code_path:DataPermissionApplication.java:assertCurrentUserIsAdminOfTargetCompany
```
---END FILE---

---FILE: rules/specified_requires_org_list.md ---
---
type: rule
title: SPECIFIED 必须携带组织列表
page_key: specified_requires_org_list
domain: cust_org_permission
status: draft
aliases: [指定组织校验, SPECIFIED 非空校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

该规则阻止「指定组织但范围为空」的悬空权限落库，是 [[specified_permission_scope]] 的强制实现。涉及 [[sys_cust_org_user_permission]] 的 permission_type 与 [[org_id_list]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: SPECIFIED 必须携带组织列表
content: permissionType=SPECIFIED 且 orgIdList 为空时抛 CommonException('指定组织时，请选择组织列表')。
impact: 阻止『指定组织但无范围』的悬空权限。
field_targets:
  - sys_cust_org_user_permission.permission_type
  - sys_cust_org_user_permission.org_id_list
evidence: code_path:DataPermissionApplication.java:saveDataPermission,saveDataPermissionBatch
```
---END FILE---

---FILE: rules/enterprise_admin_fixed_all.md ---
---
type: rule
title: 企业管理员数据权限固定 ALL
page_key: enterprise_admin_fixed_all
domain: cust_org_permission
status: draft
aliases: [管理员固定 ALL, 管理员不读权限库]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

管理员不受组织范围限制，且无需预先配置权限记录——这是查询链路的短路分支，先判 [[enterprise_admin_scope]] 再决定是否读 [[sys_cust_org_user_permission]]。对应口径 [[admin_permission_scope]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 企业管理员数据权限固定 ALL
content: getByUserCompanyType 先判 isEnterpriseAdmin，命中则直接构造 permissionType=ALL、orgIdList=null 返回，不读权限库。
impact: 管理员不受组织范围限制，且无需预先配置权限记录。
field_targets:
  - sys_cust_org_user_permission.permission_type
evidence: code_path:DataPermissionApplication.java:getByUserCompanyType,isEnterpriseAdmin
```
---END FILE---

---FILE: rules/default_same_as_user_org_backfill.md ---
---
type: rule
title: 无记录/空类型默认 SAME_AS_USER_ORG 并回填组织
page_key: default_same_as_user_org_backfill
domain: cust_org_permission
status: draft
aliases: [兜底回填组织, 默认 SAME_AS_USER_ORG 规则]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
---

该规则把「查不到」变成「本人所属组织」而不是「全量可见」，是数据权限的安全兜底。回填来源是用户组织绑定，经 listCustUserOrgs 去重后写入 [[org_id_list]]；异常只告警不抛出，因此回填失败不会中断查询。语义边界见 [[same_as_user_org]]，口径见 [[default_permission_scope]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 无记录/空类型默认 SAME_AS_USER_ORG 并回填组织
content: 非管理员且未查出记录或 permissionType 为空时置 SAME_AS_USER_ORG，再由该用户在该企业+角色下的组织绑定填充 orgIdList（异常仅告警不抛出）。
impact: 数据范围兜底为『本人所属组织』，避免默认全量可见。
field_targets:
  - sys_cust_org_user_permission.permission_type
  - sys_cust_org_user_permission.org_id_list
evidence: code_path:DataPermissionApplication.java:fillOrgIdsIfSameAsUserOrg
```
---END FILE---

---FILE: rules/org_operate_requires_build_success.md ---
---
type: rule
title: 组织操作前置：企业建档成功
page_key: org_operate_requires_build_success
domain: cust_org_permission
status: draft
aliases: [组织操作前置, 建档成功门槛]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
---

未认证企业无法创建或初始化组织。该规则同时出现在单企业动作（addSubOrg、initRootOrg）与批量扫描两个入口，口径见 [[build_success_cust_scope]] 与 [[enabled_cust_scope]]，状态见 [[cust_build_status]]。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 组织操作前置：企业建档成功
content: addSubOrg 调用 checkCustBuildStatus 校验 cust_build_status=BUILD_SUCCESS；initRootOrg 同样要求建档成功；批量初始化按 enable='Y' + BUILD_SUCCESS 翻页扫描。
impact: 未认证企业无法创建/初始化组织。
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.enable
evidence: code_path:CustSysOrgApplication.java:checkCustBuildStatus,listBuildSuccessCusts
```
---END FILE---

---FILE: rules/org_import_root_name_equals_company_name.md ---
---
type: rule
title: 组织导入一级组织名称必须等于企业名称
page_key: org_import_root_name_equals_company_name
domain: cust_org_permission
status: draft
aliases: [根组织名称校验, 一级组织名称一致]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
---

导入解析（checkExcelData）阶段即拦截，防止导入产生与主数据不一致的根组织。涉及 [[cust_company_info]].name 与该企业组织树的根行。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 组织导入一级组织名称必须等于企业名称
content: checkExcelData 中 parentOrgName='/' 的根行只能一条且 orgName 必须等于 cust_company_info.name，否则报错。
impact: 防止导入产生与主数据不一致的根组织。
field_targets:
  - cust_company_info.name
evidence: code_path:CustSysOrgApplication.java:checkExcelData
```
---END FILE---

---FILE: rules/secondary_org_bind_group_exclusive.md ---
---
type: rule
title: 二级组织绑定不得跨（企业, 角色）分组
page_key: secondary_org_bind_group_exclusive
domain: cust_org_permission
status: draft
aliases: [二级组织唯一归属, 用户绑定分组校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
---

该规则保证组织归属唯一、且不落空分组。分组维度是 (custId, companyType)，与 [[company_type]]、[[cust_id_company_id]] 的语义一致；绑定的用户有效性另由 [[bind_org_user_requires_enabled_contact]] 把关。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 二级组织绑定不得跨（企业, 角色）分组
content: Sheet1 中同一 orgId 只能属于一个 (custId, companyType) 分组，且每组在 Sheet2 中必须至少有一行用户绑定。
impact: 保证组织归属唯一、避免空分组落库。
field_targets: []
evidence: code_path:CustSysOrgApplication.java:importSecondaryOrgUserBind
```
---END FILE---

---FILE: rules/bind_org_user_requires_enabled_contact.md ---
---
type: rule
title: 绑定组织用户要求联系人在该企业角色下启用
page_key: bind_org_user_requires_enabled_contact
domain: cust_org_permission
status: draft
aliases: [绑定用户启用校验, 用户未加入该企业]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
---

禁用或未加入企业的用户不能被挂到组织下。计数条件同时覆盖用户、企业编码、角色与启用标记，说明 [[cust_person_info]] 的这三列构成绑定校验的最小键；相关口径见 [[enabled_contact_scope]]。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 绑定组织用户要求联系人在该企业角色下启用
content: 按 userId + refCustCompanyInfo + companyType + enable='Y' 计数，为 0 则报『用户未加入该企业或未启用』。
impact: 禁用/未加入企业的用户不能被挂到组织下。
field_targets:
  - cust_person_info.enable
  - cust_person_info.company_type
  - cust_person_info.ref_cust_company_info
evidence: code_path:CustSysOrgApplication.java:importSecondaryOrgUserBind
```
---END FILE---

---FILE: rules/group_import_parent_child_role_consistency.md ---
---
type: rule
title: 集团成员导入父子角色一致性
page_key: group_import_parent_child_role_consistency
domain: cust_org_permission
status: draft
aliases: [父子角色一致, 集团导入角色校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustGroupRelApplication.java
contract_version: "0.1"
---

该规则阻断同链角色混挂的集团树，判定基于 [[cust_company_info]].cust_company_type（JSON 数组，多角色），语义见 [[company_type]]；关系落库见 [[cust_group_rel]]、[[cust_group_rel_status]]。

## 需求背景
本页仅依据代码证据（CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 集团成员导入父子角色一致性
content: 若父级企业已存在，其 cust_company_type 必须包含子级申报的企业角色；父级尚未存在时，同一父级下所有子级角色必须一致。
impact: 阻断同链角色混挂的集团树。
field_targets:
  - cust_company_info.cust_company_type
evidence: code_path:CustGroupRelApplication.java:checkRoleExcelData
```
---END FILE---

---REVIEW: tables | 物理库名与字段类型缺失---
本批页面 frontmatter 的 scope.databases 一律写 [unknown]：语义分析未给出任何物理库名，且表名跨 sys_* 与 cust_* 两族，无法在无证据情况下断言其所属物理库。同理，ground:table 中除 org_manage.status（varchar(10)，库证据）外的字段类型均写 unknown，原因是本次分析未提供 DDL/类型信息；字段的业务含义（desc）与取值域（dict）保留未改。涉及页面：tables/sys_cust_org_user_permission、tables/cust_person_info、tables/cust_company_info、tables/cust_group_rel、tables/operation_user、tables/org_manage。待补 DB 名称与字段类型证据后回填。
---END REVIEW---

---REVIEW: rules | 运营方查询过滤测试数据---
语义分析中该规则条目被截断：content 未结束（field_targets 仅到 "cust_company_info.test_data, cus"），且 evidence 字段缺失，无法按「逐字来自证据」要求写出 ground:rule 的 evidence 与完整 content，故本次未产出 rules/ 页面。已可确认部分：同一 db_tenant_code 下 cust_company_type 含 PLATFORM_OPERATOR_COMPANY 的企业数 >1 时，过滤 test_data='Y' 仅保留真实运营方。涉及 [[cust_company_info]] 的 test_data、db_tenant_code，以及 [[company_type]]、[[tenant_isolation_scope]]。待 evidence 补全后按 rule 页建页。
---END REVIEW---