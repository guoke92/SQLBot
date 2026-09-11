---FILE: tables/operation_user.md ---
---
type: table
title: 运营人员表 operation_user
page_key: table.operation_user
domain: 数据权限与组织
status: draft
aliases: [operation_user, 运营中台人员表, 运营人员]
oid: 1
scope:
  databases: [base]
sources: [db]
contract_version: "0.1"
---

运营中台侧的运营人员主数据表，保存运营人员的业务编码、姓名、运营组别、所属机构编号以及审批流实例信息。本表是「运营人员归属」的源端：产融侧 [[tables/cust_person_info]] 的 operator_id / operator_realname / operator 三个字段分别冗余自本表的 operation_id / operation_name 与登录名，构成 [[concepts/operator_identity_bridge]]。本表 organization_id 与 [[tables/org_manage]] 同域，构成 [[concepts/org_identity_bridge]]。

本表的审计字段（create_by / create_user / update_by / update_user）实测全部为空串，说明审计值实际未落值，排障时不可将其作为「谁创建了运营人员」的依据。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；现有结论均来自物理库字段语义（db 证据）。

## 版本演进

v0：依据 db 证据建档。其中 enable / deleted / db_tenant_code 附有实测分布，是查询口径的直接依据，删除过滤规则见 [[rules/operation_user_deleted_filter]]。

```ground:table
table: operation_user
fields:
  - name: id
    meaning: 运营中台人员主键
    evidence: db
  - name: code
    meaning: 编码（运营人员业务编码）
    evidence: db
  - name: name
    meaning: 名称
    evidence: db
  - name: operation_id
    meaning: 运营中台人员ID（对接运营中台的用户标识，产融侧 cust_person_info.operator_id 存放的值）
    evidence: db
  - name: operation_name
    meaning: 运营人员姓名（产融侧 cust_person_info.operator_realname 的来源）
    evidence: db
  - name: operation_group
    meaning: 运营组别
    evidence: db
  - name: organization_id
    meaning: 机构编号（指向机构域 org_manage.organization_id）
    evidence: db
  - name: status
    meaning: 用户状态标识
    evidence: db
  - name: enable
    meaning: 启用标识；实测 Y=132 / N=9
    evidence: db
  - name: deleted
    meaning: 逻辑删除标识；实测 N=119 / Y=22（存在已删除数据，查询必须带 deleted 过滤）
    evidence: db
  - name: db_tenant_code
    meaning: 数据租户标识；实测仅出现 'base'（7 条），说明该表当前仅承载 base 租户运营人员
    evidence: db
  - name: app_tenant_code
    meaning: 逻辑租户标识（与 db_tenant_code 分属逻辑/数据两层）
    evidence: db
  - name: act_procinst_id
    meaning: 流程实例ID（运营人员的审批流实例）
    evidence: db
  - name: act_procinst_no
    meaning: 流程申请编号
    evidence: db
  - name: act_procinst_status
    meaning: 当前审批状态
    evidence: db
  - name: act_procinst_date
    meaning: 审批结束时间
    evidence: db
  - name: create_by
    meaning: 创建人id；实测全部为 ''（空串），该表审计字段实际未落值
    evidence: db
  - name: create_user
    meaning: 创建人名称；实测全部为 ''
    evidence: db
  - name: update_by
    meaning: 更新人id；实测全部为 ''
    evidence: db
  - name: update_user
    meaning: 更新人名称；实测全部为 ''
    evidence: db
```

---END FILE---

---FILE: tables/org_manage.md ---
---
type: table
title: 机构管理表 org_manage
page_key: table.org_manage
domain: 数据权限与组织
status: draft
aliases: [org_manage, 机构表, 机构管理]
oid: 1
scope:
  databases: [base]
sources: [db, code]
contract_version: "0.1"
---

机构域主数据表，通过 parent_code 自引用构成机构树。organization_id 与 [[tables/operation_user]].organization_id 属同一机构域主键，二者构成 [[concepts/org_identity_bridge]]；org_type 与代码侧 OrgTypeEnum（ORG 根机构 / SUB 子机构）对应；client_type 用于区分来源端，代码 OrgFacade 中以 clientType=='AGW' 判断是否跳过租户过滤，见 [[rules/org_agw_skip_tenant_filter]]。

org_name 与 name 的区别在于前者面向展示，建档与查询口径应以 org_name 为准。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自 db 字段语义与代码侧（OrgTypeEnum、SysOrgDO.parentId/selectByCode、OrgFacade）证据。

## 版本演进

v0：依据 db + code 证据建档。

```ground:table
table: org_manage
fields:
  - name: id
    meaning: 机构管理主键
    evidence: db
  - name: org_name
    meaning: 机构名称（面向展示的名称字段，区别于 name）
    evidence: db
  - name: org_no
    meaning: 机构号
    evidence: db
  - name: org_level
    meaning: 机构层级（int，机构树的深度）
    evidence: db
  - name: org_type
    meaning: 机构类型（varchar32，与代码侧 OrgTypeEnum：ORG 根机构 / SUB 子机构 对应）
    evidence: code
  - name: parent_code
    meaning: 父机构编号（自引用，构成机构树；对应代码 SysOrgDO.parentId/selectByCode 链路）
    evidence: db
  - name: organization_id
    meaning: 机构编号（与 operation_user.organization_id 同域的机构主键）
    evidence: db
  - name: status
    meaning: 状态
    evidence: db
  - name: client_type
    meaning: 端类型（区分 AGW/客户端等来源；代码 OrgFacade 中以 clientType=='AGW' 判断是否跳过租户过滤）
    evidence: code
  - name: enable
    meaning: enable（默认 Y）
    evidence: db
  - name: db_tenant_code
    meaning: 数据租户标识
    evidence: db
  - name: app_tenant_code
    meaning: 逻辑租户标识
    evidence: db
```

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: 企业信息表 cust_company_info
page_key: table.cust_company_info
domain: 数据权限与组织
status: draft
aliases: [cust_company_info, 企业信息, 企业主数据]
oid: 1
scope:
  databases: [base]
sources: [code, db]
contract_version: "0.1"
---

产融侧的企业主数据表，承载企业认证/建档、经营状态、企业角色类型、认证方式与统一社会信用代码等关键字段。本表是 [[concepts/company_business_code]] 的源端：对外引用键是 code 而非 id，子表（cust_person_info / cust_role_info）统一以 ref_cust_company_info 指向它。

两个状态字段分别驱动两条状态机：cust_build_status 见 [[processes/cust_build_status_fsm]]，cust_status 见 [[processes/cust_status_fsm]]。企业查询默认要求 enable='Y'，建档成功口径见 [[calibers/build_success_cust]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自代码侧枚举与查询链路证据（CustBuildStatusEnum、CustStatusEnum、IdentifyTypeConstant、queryTenantOperatorCompany 等）。

## 版本演进

v0：依据 code 证据建档；db_tenant_code 作为跨企业/跨租户查询与写库路由依据，见 [[concepts/tenant_code_layers]]。

```ground:table
table: cust_company_info
fields:
  - name: code
    meaning: 企业业务编码（对外引用键，子表以 ref_cust_company_info 指向它，而非 id）
    evidence: code
  - name: cust_build_status
    meaning: 企业认证/建档状态（CustBuildStatusEnum）
    evidence: code
  - name: cust_status
    meaning: 企业经营状态（CustStatusEnum：ADD/EFFECT/FREEZE/WRITEOFF/CHANGE）
    evidence: code
  - name: cust_company_type
    meaning: 企业角色类型，JSON 数组字符串（如 ["SUPPLIER"]），可多角色
    evidence: code
  - name: db_tenant_code
    meaning: 数据租户标识（跨企业/跨租户查询与写库路由依据）
    evidence: code
  - name: identify_style
    meaning: 认证方式（IdentifyTypeConstant：INVITE 邀请-客户录入 / INVITE_AGW 邀请-平台录入 / SELF 自主认证 / SIMPLE 简易认证）
    evidence: code
  - name: certification_no
    meaning: 统一社会信用代码（同租户内企业唯一键之一）
    evidence: code
  - name: enable
    meaning: 启用标识 Y/N，所有企业查询默认过滤 enable='Y'
    evidence: code
  - name: test_data
    meaning: 测试数据标识（Y 为测试运营方；queryTenantOperatorCompany 在多运营方时过滤 test_data='Y'）
    evidence: code
  - name: need_register_ca
    meaning: 是否需要开通电子签章 CA（Y/N，简易认证时被强制校正为不开通）
    evidence: code
  - name: head_company
    meaning: 是否总部企业（为空时提交登记为 Y）
    evidence: code
```

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: 企业联系人表 cust_person_info
page_key: table.cust_person_info
domain: 数据权限与组织
status: draft
aliases: [cust_person_info, 联系人, 企业联系人]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

产融侧的企业联系人/用户表，通过 ref_cust_company_info 关联到 [[tables/cust_company_info]].code（见 [[concepts/company_business_code]]）。user_type 决定该联系人是否可参与数据权限与管理动作，其状态机见 [[processes/cust_person_user_type_fsm]]；企业管理员口径见 [[calibers/company_admin]]，非游客口径见 [[calibers/non_guest_user]]。

本表同时承载运营人员归属信息：operator_id / operator_realname / operator 冗余自 [[tables/operation_user]]，构成 [[concepts/operator_identity_bridge]]；company_type 与 cust_company_info.cust_company_type、cust_role_info.role_type 同域，见 [[concepts/company_role_type]]。phone 为加密 Base64 存储，见 [[rules/phone_encrypted_base64]]。本表 user_id 参与数据权限三维，见 [[concepts/data_permission_triple]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自代码侧枚举与加密工具链路（UserTypeEnum、CustPersonStatusConstant、CustCertificationResultTypeEnum、RealNameResultEnum、encryptAndBase64Str/decryptStr）。

## 版本演进

v0：依据 code 证据建档。

```ground:table
table: cust_person_info
fields:
  - name: user_type
    meaning: 用户类型（UserTypeEnum：admin 企业管理员 / operator 经办人 / guest 游客），决定是否可参与数据权限与管理动作
    evidence: code
  - name: company_type
    meaning: 该联系人归属的企业角色类型（与 cust_company_info.cust_company_type 对应）
    evidence: code
  - name: ref_cust_company_info
    meaning: 关联企业业务编码（指向 cust_company_info.code）
    evidence: code
  - name: phone
    meaning: 手机号，加密后以 Base64 存储（写入用 encryptAndBase64Str，展示用 decryptStr）
    evidence: code
  - name: enable
    meaning: 启用标识 Y/N（冻结用户置 N）
    evidence: code
  - name: status
    meaning: 用户状态（CustPersonStatusConstant：ADD/EFFECT/FREEZE）
    evidence: code
  - name: operator_id
    meaning: 归属运营人员ID（指向 operation_user.operation_id）
    evidence: code
  - name: operator_realname
    meaning: 归属运营人员姓名（冗余自 operation_user.operation_name）
    evidence: code
  - name: operator
    meaning: 归属运营人员登录名
    evidence: code
  - name: phone_realname_status
    meaning: 手机号实名状态（CustCertificationResultTypeEnum：待认证/自动通过/人工通过）
    evidence: code
  - name: face_status
    meaning: 人脸认证状态
    evidence: code
  - name: real_name_result
    meaning: 实名结果（RealNameResultEnum.VERIFIED_SUCCESS）
    evidence: code
```

---END FILE---

---FILE: tables/cust_role_info.md ---
---
type: table
title: 企业角色表 cust_role_info
page_key: table.cust_role_info
domain: 数据权限与组织
status: draft
aliases: [cust_role_info, 企业角色]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

企业角色表，按角色类型拆分记录企业的角色身份。role_type 与 cust_company_info.cust_company_type、cust_person_info.company_type 同域，见 [[concepts/company_role_type]]；根组织初始化按 role_type 逐角色执行（initRootOrg）。platform_cust_id 表示运营中台企业ID，未同步时置空并作为待补推标记。ref_cust_company_info 关联 [[tables/cust_company_info]].code。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自代码侧 initRootOrg 链路证据。

## 版本演进

v0：依据 code 证据建档。

```ground:table
table: cust_role_info
fields:
  - name: role_type
    meaning: 企业角色类型（与 cust_company_info.cust_company_type 同域；initRootOrg 按此字段逐角色初始化根组织）
    evidence: code
  - name: platform_cust_id
    meaning: 运营中台企业ID（未同步时置空，作为待补推标记）
    evidence: code
  - name: ref_cust_company_info
    meaning: 关联企业业务编码
    evidence: code
  - name: status
    meaning: 角色状态（随企业状态联动更新）
    evidence: code
```

---END FILE---

---FILE: tables/cust_user_rel.md ---
---
type: table
title: 用户产品关系表 cust_user_rel
page_key: table.cust_user_rel
domain: 数据权限与组织
status: draft
aliases: [cust_user_rel, 用户产品关系]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

用户与产品（业务系统）的关联表，决定经办人需要推送到哪些业务系统。is_freeze 是冻结标识，'N' 表示未冻结；删除 sys 用户前要求全部产品关系均已冻结，见 [[rules/sys_user_delete_all_products_frozen]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自代码侧冻结/删除校验链路。

## 版本演进

v0：依据 code 证据建档。

```ground:table
table: cust_user_rel
fields:
  - name: is_freeze
    meaning: 用户-产品关系冻结标识（'N' 表示未冻结；全部冻结才允许删除 sys 用户）
    evidence: code
  - name: product_id
    meaning: 产品（系统）ID，决定经办人推送哪些业务系统
    evidence: code
```

---END FILE---

---FILE: tables/sys_user.md ---
---
type: table
title: 登录用户表 sys_user
page_key: table.sys_user
domain: 数据权限与组织
status: draft
aliases: [sys_user, 登录用户]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

系统登录用户表。组织树在渲染 createUser/updateUser 时，若名称缺失会按 createBy/updateBy 反查本表 name 填充；邮箱在业务邮箱变更时按条件同步更新 email。删除本表用户前需校验 [[tables/cust_user_rel]] 是否全部冻结，见 [[rules/sys_user_delete_all_products_frozen]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自代码侧组织树与邮箱同步链路。

## 版本演进

v0：依据 code 证据建档。

```ground:table
table: sys_user
fields:
  - name: name
    meaning: 登录用户姓名（组织树 createUser/updateUser 缺失时按 createBy/updateBy 反查填充）
    evidence: code
  - name: email
    meaning: 登录邮箱（业务邮箱变更时按条件同步更新）
    evidence: code
```

---END FILE---

---FILE: tables/sys_cust_org_user_permission.md ---
---
type: table
title: 客户组织数据权限表 sys_cust_org_user_permission
page_key: table.sys_cust_org_user_permission
domain: 数据权限与组织
status: draft
aliases: [sys_cust_org_user_permission, 数据权限表]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

数据权限表，主体维度由 user_id + company_id + company_type 构成唯一三维，见 [[concepts/data_permission_triple]]。permission_type 的取值与流转见 [[processes/data_permission_type_fsm]]；缺省处理见 [[rules/data_permission_default_same_as_user_org]]；SPECIFIED 必填 org_id_list 见 [[rules/specified_requires_org_id_list]]。企业管理员在该企业该角色下的判定口径见 [[calibers/company_admin]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自代码侧 DataPermissionApplication 证据。

## 版本演进

v0：依据 code 证据建档。

```ground:table
table: sys_cust_org_user_permission
fields:
  - name: user_id
    meaning: 数据权限主体用户ID（与 company_id、company_type 构成唯一三维）
    evidence: code
  - name: company_id
    meaning: 数据权限归属企业ID
    evidence: code
  - name: company_type
    meaning: 数据权限归属企业角色类型
    evidence: code
  - name: permission_type
    meaning: 数据权限类型：ALL / SPECIFIED / SAME_AS_USER_ORG；无记录或为空时按 SAME_AS_USER_ORG 处理
    evidence: code
  - name: org_id_list
    meaning: 数据范围组织ID列表（仅 SPECIFIED 必填；SAME_AS_USER_ORG 时由用户组织绑定回填）
    evidence: code
```

---END FILE---

---FILE: tables/cust_group_rel.md ---
---
type: table
title: 集团关系表 cust_group_rel
page_key: table.cust_group_rel
domain: 数据权限与组织
status: draft
aliases: [cust_group_rel, 集团关系]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

集团与成员企业之间的关系表，status 驱动集团关系生效状态机（见 [[processes/cust_group_rel_status_fsm]]）。子公司平铺列表以 status='EFFECTIVE' 过滤，见 [[calibers/effective_group_member]]。同一租户存在多个运营方时，运营方企业的判定依赖 [[calibers/real_operator]] 与 [[calibers/platform_operator_company]]。

本页字段覆盖不完整：语义分析的 field_semantics 未收录本表，仅能从状态机与口径证据中确认 status 一个字段，其余字段待补。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：仅依据状态机与口径中的 code 证据建档。

```ground:table
table: cust_group_rel
fields:
  - name: status
    meaning: 集团关系生效状态（取值 INEFFECTIVE 未生效 / EFFECTIVE 已生效；listSubCust 以 EFFECTIVE 过滤）
    evidence: code_path:CustGroupRelApplication.java#listSubCust
```

---END FILE---

---REVIEW: table | cust_group_rel 字段覆盖不完整---
语义分析的 field_semantics 未收录 cust_group_rel，本页仅能确认 status 字段（证据来自 CustGroupRelApplication#addExistRootGroupRel / #effectGroupRel / #listSubCust）。集团关系的新增、生效、删除链路上还引用了哪些字段（如集团企业编码、成员企业编码、额度相关字段）无法从现有证据判定，需补采字段语义后再扩表。
---END REVIEW---

---FILE: processes/cust_build_status_fsm.md ---
---
type: process
title: 企业认证/建档状态机（cust_build_status）
page_key: process.cust_build_status_fsm
domain: 数据权限与组织
status: draft
aliases: [企业建档状态机, cust_build_status, CustBuildStatusEnum]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: cust_company_info.cust_build_status
---

企业认证/建档状态机，承载于 [[tables/cust_company_info]].cust_build_status。状态取值来自代码枚举 CustBuildStatusEnum。流转的入口取决于认证方式 identify_style：邀请-客户录入（INVITE）与自主认证（SELF）提交后进入 CUST_CONFIRM_AWAIT，邀请-平台录入（INVITE_AGW）提交后直接进入 CUST_BUILDING。简易认证（SIMPLE）走独立的 AWAIT_CUST_CONFIRM 支线。

建档成功是组织根节点初始化、机构管理员绑定定时任务与企业查询前置校验的前置口径，见 [[calibers/build_success_cust]]。建档成功同时触发企业经营状态从 ADD 到 EFFECT，见 [[processes/cust_status_fsm]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 CustCompanyInfoApplication 相关方法。

## 版本演进

v0：依据 code 证据建模，覆盖入库、驳回重提、审核退回、审核通过、简易认证确认五类事件。

```ground:process
name: 企业认证/建档状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始/待提交
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 审核中（运营中台）
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 审核驳回/建档失败
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 简易认证提交后的待确认
    source: code_enum
transitions:
  - from: INIT
    event: 邀请认证（客户录入）/自主认证提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java#getCustBuildStatus
  - from: INIT
    event: 邀请认证-平台录入（INVITE_AGW）提交
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java#getCustBuildStatus
  - from: BUILD_FAIL
    event: 驳回后重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交，推送运营中台审核
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_BUILDING
    event: 运营中台审核退回（客户录入场景）
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_BUILDING
    event: 运营中台审核通过，流转到客户确认（平台录入场景）
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_BUILDING
    event: 认证审核通过
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_CONFIRM_AWAIT
    event: 平台录入客户点击确认提交
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_CONFIRM_AWAIT
    event: 认证审核拒绝
    to: BUILD_FAIL
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: INIT
    event: 简易认证提交（非建档成功、非变更）
    to: AWAIT_CUST_CONFIRM
    evidence: code_path:CustCompanyInfoApplication.java#submitForSimpleAuth
  - from: AWAIT_CUST_CONFIRM
    event: 简易认证确认（含资金方直接生效）
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java#confirmCustInfoForSimpleAuth
```

---END FILE---

---FILE: processes/cust_status_fsm.md ---
---
type: process
title: 企业经营状态机（cust_status）
page_key: process.cust_status_fsm
domain: 数据权限与组织
status: draft
aliases: [企业经营状态机, cust_status, CustStatusEnum]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: cust_company_info.cust_status
---

企业经营状态机，承载于 [[tables/cust_company_info]].cust_status，取值来自代码枚举 CustStatusEnum：ADD / EFFECT / FREEZE / WRITEOFF / CHANGE。建档成功会把企业从 ADD 推进到 EFFECT（见 [[processes/cust_build_status_fsm]]）；冻结与解冻分别联动冻结/解冻企业管理员（见 [[calibers/company_admin]]）；注销前必须先冻结企业下全部用户，见 [[rules/writeoff_freeze_all_users]]。

企业信息变更会进入 CHANGE（变更在途），由 CustPersonApplication#adminChangeSaveOrUpdate 触发。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 CustCompanyInfoApplication 与 CustPersonApplication。

## 版本演进

v0：依据 code 证据建模。

```ground:process
name: 企业经营状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/待生效
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
  - value: CHANGE
    label: 变更在途
    source: code_enum
transitions:
  - from: ADD
    event: 建档成功生效
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: EFFECT
    event: 冻结企业（同时冻结企业管理员）
    to: FREEZE
    evidence: code_path:CustCompanyInfoApplication.java#freeze
  - from: FREEZE
    event: 解冻企业（同时解冻企业管理员）
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java#unfreeze
  - from: EFFECT
    event: 注销企业
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator
  - from: WRITEOFF
    event: 注销前先冻结企业下全部用户
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator(freezeCustAllUsers)
  - from: EFFECT
    event: 发起企业信息变更
    to: CHANGE
    evidence: code_path:CustPersonApplication.java#adminChangeSaveOrUpdate
```

---END FILE---

---FILE: processes/data_permission_type_fsm.md ---
---
type: process
title: 数据权限类型机（permission_type）
page_key: process.data_permission_type_fsm
domain: 数据权限与组织
status: draft
aliases: [数据权限类型机, permission_type, ALL, SPECIFIED, SAME_AS_USER_ORG]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: sys_cust_org_user_permission.permission_type
---

数据权限类型机，承载于 [[tables/sys_cust_org_user_permission]].permission_type，取值为 ALL（全部数据）/ SPECIFIED（指定组织）/ SAME_AS_USER_ORG（同用户所属组织）。这是一张「按主体三维惰性推进」的状态机：无记录或值为空时按 SAME_AS_USER_ORG 处理（见 [[rules/data_permission_default_same_as_user_org]]）；一旦判定主体是该企业该角色启用中的管理员，则直接落到 ALL（判定口径见 [[calibers/company_admin]]）。

SPECIFIED 的保存要求 org_id_list 必填，见 [[rules/specified_requires_org_id_list]]；SAME_AS_USER_ORG 的组织范围由用户组织绑定回填。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 DataPermissionApplication。

## 版本演进

v0：依据 code 证据建模，含「空值即缺省」这一非显式落库的隐式流转。

```ground:process
name: 数据权限类型机
field: sys_cust_org_user_permission.permission_type
states:
  - value: ALL
    label: 全部数据
    source: code_enum
  - value: SPECIFIED
    label: 指定组织
    source: code_enum
  - value: SAME_AS_USER_ORG
    label: 同用户所属组织
    source: code_enum
transitions:
  - from: 空（无记录）
    event: 查询且非企业管理员
    to: SAME_AS_USER_ORG
    evidence: code_path:DataPermissionApplication.java#getByUserCompanyType
  - from: 空（permissionType 为空）
    event: 列表查询补默认值
    to: SAME_AS_USER_ORG
    evidence: code_path:DataPermissionApplication.java#listByCompany
  - from: 任意
    event: 用户为该企业该角色启用中的管理员
    to: ALL
    evidence: code_path:DataPermissionApplication.java#isEnterpriseAdmin
  - from: SAME_AS_USER_ORG
    event: 保存指定组织（orgIdList 必填）
    to: SPECIFIED
    evidence: code_path:DataPermissionApplication.java#saveDataPermission
  - from: SPECIFIED
    event: 保存为全部
    to: ALL
    evidence: code_path:DataPermissionApplication.java#saveDataPermissionBatch
```

---END FILE---

---FILE: processes/cust_person_user_type_fsm.md ---
---
type: process
title: 企业联系人类型机（user_type）
page_key: process.cust_person_user_type_fsm
domain: 数据权限与组织
status: draft
aliases: [联系人类型机, user_type, UserTypeEnum]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: cust_person_info.user_type
---

企业联系人类型机，承载于 [[tables/cust_person_info]].user_type，取值 UserTypeEnum：admin（企业管理员）/ operator（经办人）/ guest（游客）。guest → operator 发生在新增/编辑经办人时（AMS 以外来源默认认证通过）；guest → admin 发生在建档成功赋予管理员权限时（endueCompanyAdminUser）。

管理员的变更是「冻结旧记录 + 新建记录」而非原地改字段：旧管理员置 enable=N、status=FREEZE，新管理员另起一条记录。这一模式决定了查询时必须叠加 [[calibers/company_admin]] 的启用过滤，否则会把历史管理员算进来。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 CustPersonApplication 与 CustCompanyInfoApplication。

## 版本演进

v0：依据 code 证据建模。

```ground:process
name: 企业联系人类型机
field: cust_person_info.user_type
states:
  - value: admin
    label: 企业管理员
    source: code_enum
  - value: operator
    label: 经办人
    source: code_enum
  - value: guest
    label: 游客
    source: code_enum
transitions:
  - from: guest
    event: 新增/编辑经办人（AMS 以外来源默认认证通过）
    to: operator
    evidence: code_path:CustPersonApplication.java#insertOrUpdatePerson
  - from: guest
    event: 建档成功赋予管理员权限
    to: admin
    evidence: code_path:CustCompanyInfoApplication.java#endueCompanyAdminUser
  - from: admin
    event: 管理员变更：旧管理员置 enable=N/status=FREEZE，新建管理员记录
    to: admin
    evidence: code_path:CustPersonApplication.java#ifNessaryFrzAdm
  - from: admin
    event: 简易认证管理员换手机号：旧记录冻结、新记录生效
    to: admin
    evidence: code_path:CustPersonApplication.java#simpleChangePerson
```

---END FILE---

---FILE: processes/cust_group_rel_status_fsm.md ---
---
type: process
title: 集团关系生效状态机（cust_group_rel.status）
page_key: process.cust_group_rel_status_fsm
domain: 数据权限与组织
status: draft
aliases: [集团关系状态机, 集团关系生效, INEFFECTIVE, EFFECTIVE]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: cust_group_rel.status
---

集团关系生效状态机，承载于 [[tables/cust_group_rel]].status，取值 INEFFECTIVE（未生效）/ EFFECTIVE（已生效）。新增根集团关系时，若企业已建档成功则直接生效，否则先落未生效，待集团或成员企业建档成功时由 effectGroupRel 触发生效；删除集团成员前要校验在途业务与额度，随后才删除记录。

生效口径是子公司平铺列表的过滤条件，见 [[calibers/effective_group_member]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 CustGroupRelApplication。

## 版本演进

v0：依据 code 证据建模；本表字段在 field_semantics 中未收录，仅确认 status，详见 [[tables/cust_group_rel]] 的 REVIEW。

```ground:process
name: 集团关系生效状态机
field: cust_group_rel.status
states:
  - value: INEFFECTIVE
    label: 未生效
    source: code_enum
  - value: EFFECTIVE
    label: 已生效
    source: code_enum
transitions:
  - from: （新增）
    event: 新增根集团关系：企业建档成功则直接生效，否则未生效
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.java#addExistRootGroupRel
  - from: INEFFECTIVE
    event: 集团/成员企业建档成功触发生效
    to: EFFECTIVE
    evidence: code_path:CustGroupRelApplication.java#effectGroupRel
  - from: EFFECTIVE
    event: 删除集团成员前校验在途业务与额度，随后删除
    to: （删除）
    evidence: code_path:CustGroupRelApplication.java#removeRootGroup
```

---END FILE---

---FILE: calibers/build_success_cust.md ---
---
type: caliber
title: 建档成功企业
page_key: caliber.build_success_cust
domain: 数据权限与组织
status: draft
aliases: [建档成功, BUILD_SUCCESS 企业]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「建档成功企业」是组织域最重要的过滤口径：组织根节点初始化、机构管理员绑定定时任务、企业查询前置校验三处都要求企业同时满足建档成功与启用。它依赖 [[processes/cust_build_status_fsm]] 到达 BUILD_SUCCESS，并叠加 [[tables/cust_company_info]].enable 维度，因此不能只判状态字段。此处引用的档案成功状态也决定 [[processes/cust_group_rel_status_fsm]] 中集团关系能否直接生效。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustSysOrgApplication）成文。

```ground:caliber
name: 建档成功企业
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.enable = 'Y'"
scope: 组织根节点初始化、机构管理员绑定定时任务、企业查询前置校验
evidence: code_path:CustSysOrgApplication.java#listBuildSuccessCusts / #checkCustBuildStatus
```

---END FILE---

---FILE: calibers/company_admin.md ---
---
type: caliber
title: 企业管理员
page_key: caliber.company_admin
domain: 数据权限与组织
status: draft
aliases: [企业管理员, admin 口径]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「企业管理员」口径由 user_type='admin' 与 enable='Y' 两个条件共同构成。因为管理员的更换是「冻结旧记录 + 新建记录」（见 [[processes/cust_person_user_type_fsm]]），缺少 enable 过滤会把历史管理员当成现任管理员。该口径是数据权限保存鉴权、数据权限查询默认 ALL、组织绑定三处的前置判定，直接决定 [[processes/data_permission_type_fsm]] 是否能落到 ALL。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（DataPermissionApplication）成文。

```ground:caliber
name: 企业管理员
predicate: "cust_person_info.user_type = 'admin' AND cust_person_info.enable = 'Y'"
scope: 数据权限保存鉴权、数据权限查询默认 ALL、组织绑定
evidence: code_path:DataPermissionApplication.java#assertCurrentUserIsAdminOfTargetCompany / #isEnterpriseAdmin
```

---END FILE---

---FILE: calibers/non_guest_user.md ---
---
type: caliber
title: 非游客用户
page_key: caliber.non_guest_user
domain: 数据权限与组织
status: draft
aliases: [非游客, user_type != guest]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「非游客用户」仅以 [[tables/cust_person_info]].user_type 不等于 guest 为条件，用于联系人分页与运营人员展示。它是比 [[calibers/company_admin]] 更宽的集合，不叠加 enable 过滤，因此其结果集会包含已冻结联系人，展示层需自行注意语义差异。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustPersonApplication）成文。

```ground:caliber
name: 非游客用户
predicate: "cust_person_info.user_type != 'guest'"
scope: 联系人分页、运营人员展示
evidence: code_path:CustPersonApplication.java#pagePerson / #getOperatorByCompanyCode
```

---END FILE---

---FILE: calibers/platform_operator_company.md ---
---
type: caliber
title: 运营方企业
page_key: caliber.platform_operator_company
domain: 数据权限与组织
status: draft
aliases: [运营方企业, PLATFORM_OPERATOR_COMPANY]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「运营方企业」口径要求 [[tables/cust_company_info]].cust_company_type 这个 JSON 数组字符串中包含 PLATFORM_OPERATOR_COMPANY，且企业处于启用状态。由于 cust_company_type 是数组字符串（可多角色，见 [[concepts/company_role_type]]），判定时是「包含」而非「等于」。

同一租户可能存在多个运营方，实际取用时通常还需叠加 [[calibers/real_operator]] 过滤测试数据。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustGroupRelApplication）成文。

```ground:caliber
name: 运营方企业
predicate: "cust_company_info.cust_company_type 包含 'PLATFORM_OPERATOR_COMPANY' AND cust_company_info.enable = 'Y'"
scope: 租户运营方查询
evidence: code_path:CustGroupRelApplication.java#queryTenantOperatorCompany
```

---END FILE---

---FILE: calibers/real_operator.md ---
---
type: caliber
title: 真实运营方
page_key: caliber.real_operator
domain: 数据权限与组织
status: draft
aliases: [真实运营方, test_data 过滤]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「真实运营方」是 [[calibers/platform_operator_company]] 之上的排除口径：当同一租户存在多个运营方时，排除 test_data='Y' 的测试运营方。判定需要兼容 test_data 为空的情况，即空值不算测试数据。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustGroupRelApplication#queryTenantOperatorCompany）成文。

```ground:caliber
name: 真实运营方
predicate: "test_data ！= 'Y'"
scope: 同一租户存在多个运营方时的过滤（兼容 test_data 为空）
evidence: code_path:CustGroupRelApplication.java#queryTenantOperatorCompany
```

---END FILE---

---FILE: calibers/effective_group_member.md ---
---
type: caliber
title: 集团有效成员
page_key: caliber.effective_group_member
domain: 数据权限与组织
status: draft
aliases: [集团有效成员, EFFECTIVE 成员]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「集团有效成员」以 [[tables/cust_group_rel]].status = 'EFFECTIVE' 为唯一条件，用于子公司平铺列表过滤。状态到达 EFFECTIVE 的路径见 [[processes/cust_group_rel_status_fsm]]；未生效记录（INEFFECTIVE）不应出现在平铺结果中。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustGroupRelApplication#listSubCust）成文。

```ground:caliber
name: 集团有效成员
predicate: "cust_group_rel.status = 'EFFECTIVE'"
scope: 子公司平铺列表 listSubCust 过滤
evidence: code_path:CustGroupRelApplication.java#listSubCust
```

---END FILE---

---FILE: calibers/org_bound_legal_user.md ---
---
type: caliber
title: 二级组织绑定合法用户
page_key: caliber.org_bound_legal_user
domain: 数据权限与组织
status: draft
aliases: [二级组织绑定合法用户]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

本口径在语义分析原文中被截断，predicate 只到 "cust_person_info.user_id = ? AND cust_person_" 为止，scope 与 evidence 也未能取到。从谓词前缀可判定它是「某一用户 + 某联系人侧条件」的联合条件，用于二级组织绑定时校验用户合法性，与 [[tables/cust_person_info]]、[[tables/sys_cust_org_user_permission]] 相关；但完整的第二个条件与适用链路无法从现有证据确定，本页暂不作为可执行口径使用。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本口径的语义分析条目本身不完整，需求背景待补。

## 版本演进

v0：仅登记截断原文，等待语义分析补全后重写。

```ground:caliber
name: 二级组织绑定合法用户
predicate: "cust_person_info.user_id = ? AND cust_person_"
scope: （语义分析原文在此截断，未给出）
evidence: （语义分析原文在此截断，未给出）
```

---END FILE---

---REVIEW: caliber | 二级组织绑定合法用户---
语义分析中该口径条目被截断：predicate 止于 "cust_person_info.user_id = ? AND cust_person_"，scope 与 evidence 缺失。需要确认：(1) 第二个条件的完整字段与取值（疑似 cust_person_info 上的某个状态/启用条件）；(2) 该口径的证据代码路径（疑似组织绑定相关 Application 方法）；(3) 是否与 [[calibers/company_admin]]、[[calibers/non_guest_user]] 存在重叠或互斥关系。补全前本页不得被下游消费。
---END REVIEW---

---FILE: concepts/tenant_code_layers.md ---
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

---END FILE---

---FILE: concepts/operator_identity_bridge.md ---
---
type: concept
title: 运营人员标识桥（operation_user ↔ cust_person_info）
page_key: concept.operator_identity_bridge
domain: 数据权限与组织
status: draft
aliases: [运营人员标识桥, operator_id, operator_realname, operator]
oid: 1
scope:
  databases: [base]
sources: [db, code]
contract_version: "0.1"
maps_to:
  - operation_user.operation_id
  - cust_person_info.operator_id
  - cust_person_info.operator_realname
field_targets:
  - table: operation_user
    field: operation_id
    meaning: 运营中台人员ID（对接运营中台的用户标识，产融侧 cust_person_info.operator_id 存放的值）
    evidence: db
  - table: operation_user
    field: operation_name
    meaning: 运营人员姓名（产融侧 cust_person_info.operator_realname 的来源）
    evidence: db
  - table: cust_person_info
    field: operator_id
    meaning: 归属运营人员ID（指向 operation_user.operation_id）
    evidence: code
  - table: cust_person_info
    field: operator_realname
    meaning: 归属运营人员姓名（冗余自 operation_user.operation_name）
    evidence: code
  - table: cust_person_info
    field: operator
    meaning: 归属运营人员登录名
    evidence: code
adjudication: 产融侧只存 operation_id（非 operation_user.id），operator_realname 是姓名冗余；引用运营人员必须走 operation_id 而非主键 id。
also_confused_with: [operation_user.id, organization_id]
---

术语桥：运营人员归属跨两个域——运营中台侧的 [[tables/operation_user]] 与产融侧的 [[tables/cust_person_info]]。产融侧 cust_person_info.operator_id 存放的是 operation_user.operation_id，而不是该表主键 id；operator_realname 则是 operation_name 的冗余快照。这意味着在 operation_user 上做关联时必须避开 id 主键，否则会连到错误的运营人员。

姓名是冗余字段，源端改名后产融侧不会自动跟随，需要以 operation_id 为准反查 [[tables/operation_user]] 的 operation_name。运营人员展示口径见 [[calibers/non_guest_user]]。

---END FILE---

---FILE: concepts/org_identity_bridge.md ---
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
sources: [db, code]
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

---END FILE---

---FILE: concepts/company_business_code.md ---
---
type: concept
title: 企业业务编码桥（code ↔ ref_cust_company_info）
page_key: concept.company_business_code
domain: 数据权限与组织
status: draft
aliases: [企业业务编码, ref_cust_company_info, cust_company_info.code]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
maps_to:
  - cust_company_info.code
  - cust_person_info.ref_cust_company_info
  - cust_role_info.ref_cust_company_info
field_targets:
  - table: cust_company_info
    field: code
    meaning: 企业业务编码（对外引用键，子表以 ref_cust_company_info 指向它，而非 id）
    evidence: code
  - table: cust_role_info
    field: ref_cust_company_info
    meaning: 关联企业业务编码
    evidence: code
  - table: cust_company_info
    field: certification_no
    meaning: 统一社会信用代码（同租户内企业唯一键之一）
    evidence: code
adjudication: 企业侧对外引用一律走 cust_company_info.code（业务编码）；certification_no 是同租户内唯一键之一但不是关系外键，ref_cust_company_info 指向的是 code 而非 id。
also_confused_with: [cust_company_info.id, certification_no]
---

术语桥：企业业务编码 code 是 [[tables/cust_company_info]] 对外暴露的引用键，引用方式在子表中名为 ref_cust_company_info（[[tables/cust_person_info]]、[[tables/cust_role_info]] 都有该字段）。最容易踩的坑是误用主键 id 关联，语义分析已明确「子表以 ref_cust_company_info 指向它，而非 id」。

另一个易混字段是 certification_no（统一社会信用代码）：它是同租户内的企业唯一键之一，但承担的是去重/识别职责，不是关系外键。

---END FILE---

---FILE: concepts/company_role_type.md ---
---
type: concept
title: 企业角色类型同域（cust_company_type / company_type / role_type）
page_key: concept.company_role_type
domain: 数据权限与组织
status: draft
aliases: [企业角色类型, cust_company_type, company_type, role_type]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
maps_to:
  - cust_company_info.cust_company_type
  - cust_person_info.company_type
  - cust_role_info.role_type
  - sys_cust_org_user_permission.company_type
field_targets:
  - table: cust_company_info
    field: cust_company_type
    meaning: 企业角色类型，JSON 数组字符串（如 ["SUPPLIER"]），可多角色
    evidence: code
  - table: cust_person_info
    field: company_type
    meaning: 该联系人归属的企业角色类型（与 cust_company_info.cust_company_type 对应）
    evidence: code
  - table: cust_role_info
    field: role_type
    meaning: 企业角色类型（与 cust_company_info.cust_company_type 同域；initRootOrg 按此字段逐角色初始化根组织）
    evidence: code
  - table: sys_cust_org_user_permission
    field: company_type
    meaning: 数据权限归属企业角色类型
    evidence: code
adjudication: 同一语义（企业角色）在四张表上字段名不同：企业侧是 JSON 数组字符串（多角色，判定用"包含"），角色表是按角色拆行，联系人与数据权限表是单值；跨表比较时必须先做展开/对齐。
also_confused_with: [user_type, identify_style]
---

术语桥：「企业角色类型」在四张表上以四个不同字段名出现——cust_company_info.cust_company_type、cust_person_info.company_type、cust_role_info.role_type、sys_cust_org_user_permission.company_type。语义分析明确后三者与 cust_company_type 同域。

关键差异是形态而非语义：企业主数据上是 JSON 数组字符串（如 ["SUPPLIER"]，可多角色，判定用「包含」，见 [[calibers/platform_operator_company]]），cust_role_info 则按角色逐行拆分（initRootOrg 按此逐角色初始化根组织），联系人与数据权限表是单值。跨表比较前必须先展开成集合再对齐，否则多角色企业会漏判。适用场景见 [[concepts/data_permission_triple]]。

---END FILE---

---FILE: concepts/data_permission_triple.md ---
---
type: concept
title: 数据权限三维（user_id + company_id + company_type）
page_key: concept.data_permission_triple
domain: 数据权限与组织
status: draft
aliases: [数据权限三维, user_id, company_id, company_type]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
maps_to:
  - sys_cust_org_user_permission.user_id
  - sys_cust_org_user_permission.company_id
  - sys_cust_org_user_permission.company_type
field_targets:
  - table: sys_cust_org_user_permission
    field: user_id
    meaning: 数据权限主体用户ID（与 company_id、company_type 构成唯一三维）
    evidence: code
  - table: sys_cust_org_user_permission
    field: company_id
    meaning: 数据权限归属企业ID
    evidence: code
  - table: sys_cust_org_user_permission
    field: company_type
    meaning: 数据权限归属企业角色类型
    evidence: code
  - table: sys_cust_org_user_permission
    field: permission_type
    meaning: 数据权限类型：ALL / SPECIFIED / SAME_AS_USER_ORG；无记录或为空时按 SAME_AS_USER_ORG 处理
    evidence: code
adjudication: 数据权限的唯一主体是「用户 + 企业 + 企业角色类型」三元组；同一用户在不同企业或不同角色下是独立的权限行，缺任一维度都会串权。
also_confused_with: [cust_person_info.company_type, cust_company_info.cust_company_type, org_id_list]
---

术语桥：数据权限不是二维的「用户–企业」，而是三元组：user_id + company_id + company_type，三者共同构成唯一键。这意味着同一用户在同一企业但不同角色下可以拥有互相独立的数据权限行；读取权限时必须三个维度齐全。

company_type 与 [[concepts/company_role_type]] 同域（同名同义），不要和 [[tables/cust_person_info]].user_type（admin/operator/guest）混淆——后者是用户身份，前者是企业角色。三元组缺行或缺 permission_type 时的缺省行为见 [[rules/data_permission_default_same_as_user_org]]。

---END FILE---

---FILE: rules/data_permission_triple_unique.md ---
---
type: rule
title: 数据权限按用户+企业+角色三维唯一
page_key: rule.data_permission_triple_unique
domain: 数据权限与组织
status: draft
aliases: [数据权限唯一三维]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

落到 [[tables/sys_cust_org_user_permission]] 的每一条权限记录，主体是 user_id + company_id + company_type 三元组。同一用户在不同企业、或同一企业不同角色下的权限互不影响，删除/更新权限必须三键齐备，只按 user_id 操作会跨企业串权。语义模型见 [[concepts/data_permission_triple]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由字段语义（「与 company_id、company_type 构成唯一三维」）直接得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 数据权限三维唯一
statement: 数据权限的主体键是 user_id + company_id + company_type 三元组
condition: 读写 sys_cust_org_user_permission
action: 任何查询与更新都必须同时限定三个维度
evidence: code_path:DataPermissionApplication.java#getByUserCompanyType / #listByCompany
```

---END FILE---

---FILE: rules/data_permission_default_same_as_user_org.md ---
---
type: rule
title: 数据权限缺省按 SAME_AS_USER_ORG 处理
page_key: rule.data_permission_default_same_as_user_org
domain: 数据权限与组织
status: draft
aliases: [数据权限缺省规则, 无记录默认同用户组织]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

当 [[tables/sys_cust_org_user_permission]] 中没有对应三元组的记录，或查出的 permission_type 为空时，系统不报错也不放行全量，而是按 SAME_AS_USER_ORG（同用户所属组织）处理。这是一条「空值即缺省」的隐式流转，见 [[processes/data_permission_type_fsm]]。

需要与企业管理员的处理区分：如果主体是该企业该角色启用中的管理员，则直接按 ALL（见 [[calibers/company_admin]]），而不是缺省值。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由字段语义「无记录或为空时按 SAME_AS_USER_ORG 处理」及 DataPermissionApplication 证据得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 数据权限缺省
statement: 无权限记录或 permission_type 为空时按 SAME_AS_USER_ORG 处理，非管理员不放行为全部数据
condition: 查询权限且主体不是该企业该角色启用中的管理员
action: 以用户所属组织作为数据范围
evidence: code_path:DataPermissionApplication.java#getByUserCompanyType / #listByCompany
```

---END FILE---

---FILE: rules/specified_requires_org_id_list.md ---
---
type: rule
title: SPECIFIED 权限必须填写 org_id_list
page_key: rule.specified_requires_org_id_list
domain: 数据权限与组织
status: draft
aliases: [SPECIFIED 必填组织]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

把 [[tables/sys_cust_org_user_permission]].permission_type 保存为 SPECIFIED 时，org_id_list 必填；而 SAME_AS_USER_ORG 不需要填，其组织范围由用户组织绑定回填。组织ID的取值域见 [[concepts/org_identity_bridge]]，状态流转见 [[processes/data_permission_type_fsm]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由字段语义（「仅 SPECIFIED 必填；SAME_AS_USER_ORG 时由用户组织绑定回填」）得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: SPECIFIED 必填 org_id_list
statement: permission_type=SPECIFIED 时 org_id_list 必填；SAME_AS_USER_ORG 时由用户组织绑定回填
condition: 保存数据权限
action: 校验 org_id_list 非空，否则拒绝落库
evidence: code_path:DataPermissionApplication.java#saveDataPermission / #saveDataPermissionBatch
```

---END FILE---

---FILE: rules/operation_user_deleted_filter.md ---
---
type: rule
title: 运营人员查询必须带 deleted 过滤
page_key: rule.operation_user_deleted_filter
domain: 数据权限与组织
status: draft
aliases: [operation_user 删除过滤]
oid: 1
scope:
  databases: [base]
sources: [db]
contract_version: "0.1"
---

[[tables/operation_user]] 存在已删除数据（db 实测 deleted 分布为 N=119 / Y=22），因此对该表的任何查询都必须显式带 deleted 过滤条件，否则约 15% 的已删除运营人员会进入结果集。这是本表最容易被忽略的查询前置条件。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由 db 字段语义直接得出。注意：语义分析只给出「查询必须带 deleted 过滤」这一要求，未给出保留值的具体约定（Y/N 哪一侧为有效），落地时需与调用方确认。

## 版本演进

v0：依据 db 证据成文。

```ground:rule
name: operation_user 逻辑删除过滤
statement: 查询 operation_user 必须带 deleted 过滤
condition: 任意对 operation_user 的读取
action: 过滤掉已删除记录（实测 N=119 / Y=22，存在已删除数据）
evidence: db
```

---END FILE---

---FILE: rules/sys_user_delete_all_products_frozen.md ---
---
type: rule
title: 删除 sys 用户前须全部产品关系已冻结
page_key: rule.sys_user_delete_all_products_frozen
domain: 数据权限与组织
status: draft
aliases: [删除 sys 用户前置校验, is_freeze]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

删除 [[tables/sys_user]] 用户之前，必须校验该用户在所有产品上的关系记录是否均已冻结：[[tables/cust_user_rel]].is_freeze 为 'N' 表示未冻结，只有全部产品关系都冻结（无未冻结记录）才允许删除。该规则把「产品维度的冻结状态」作为「用户删除」的闸门，product_id 决定需要检查哪些业务系统。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由 cust_user_rel 字段语义（「全部冻结才允许删除 sys 用户」）得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: sys 用户删除前置校验
statement: 只有用户全部产品关系均冻结时才允许删除 sys 用户
condition: 存在 is_freeze='N' 的产品关系
action: 拒绝删除 sys 用户
evidence: code_path:cust_user_rel.is_freeze（'N' 表示未冻结）
```

---END FILE---

---FILE: rules/writeoff_freeze_all_users.md ---
---
type: rule
title: 注销企业前先冻结企业下全部用户
page_key: rule.writeoff_freeze_all_users
domain: 数据权限与组织
status: draft
aliases: [注销前冻结全部用户, freezeCustAllUsers]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

企业注销时，先执行 freezeCustAllUsers 把该企业下全部用户冻结，再置企业状态为 WRITEOFF；即注销动作的实际生效依赖「用户先冻结」这一前置步骤。流转见 [[processes/cust_status_fsm]]，用户冻结体现为 [[tables/cust_person_info]].enable/N 与 status/FREEZE。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由状态机中 custStatusOperator(freezeCustAllUsers) 的证据得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 注销前冻结全部用户
statement: 企业注销前必须先冻结该企业下全部用户
condition: 企业状态由 EFFECT 走向 WRITEOFF
action: 调用 freezeCustAllUsers 冻结全部用户后再注销
evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator(freezeCustAllUsers)
```

---END FILE---

---FILE: rules/simple_auth_no_ca.md ---
---
type: rule
title: 简易认证强制不开通电子签章 CA
page_key: rule.simple_auth_no_ca
domain: 数据权限与组织
status: draft
aliases: [简易认证 CA 校正, need_register_ca]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

当企业走简易认证（identify_style=SIMPLE，见 [[tables/cust_company_info]]）时，need_register_ca 会被强制校正为「不开通」，即便上游传入了开通意图也会被覆盖。该校正与简易认证支线的建档状态流转（AWAIT_CUST_CONFIRM → BUILD_SUCCESS，见 [[processes/cust_build_status_fsm]]）配套。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由字段语义「简易认证时被强制校正为不开通」得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 简易认证 CA 校正
statement: 简易认证场景 need_register_ca 强制为不开通
condition: identify_style = SIMPLE
action: 覆盖 need_register_ca 为 N
evidence: code_path:cust_company_info.need_register_ca（简易认证时被强制校正为不开通）
```

---END FILE---

---FILE: rules/org_agw_skip_tenant_filter.md ---
---
type: rule
title: client_type=AGW 跳过机构租户过滤
page_key: rule.org_agw_skip_tenant_filter
domain: 数据权限与组织
status: draft
aliases: [AGW 跳过租户过滤, org_manage.client_type]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

[[tables/org_manage]] 的 client_type 用于区分端来源；OrgFacade 中以 clientType=='AGW' 判断是否跳过租户过滤。即来自 AGW 端调用时，机构数据不走租户维度裁剪，这是跨租户可见性的一个显式例外，与 [[concepts/tenant_code_layers]] 的租户层次直接相关。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由 org_manage.client_type 字段语义得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: AGW 端跳过租户过滤
statement: clientType=='AGW' 时跳过机构数据的租户过滤
condition: OrgFacade 收到 client_type=AGW 的调用
action: 不追加租户过滤条件
evidence: code_path:OrgFacade（clientType=='AGW' 判断）
```

---END FILE---

---FILE: rules/phone_encrypted_base64.md ---
---
type: rule
title: 联系人手机号加密后 Base64 存储
page_key: rule.phone_encrypted_base64
domain: 数据权限与组织
status: draft
aliases: [手机号加密, encryptAndBase64Str, decryptStr]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

[[tables/cust_person_info]].phone 不以明文存储：写入时用 encryptAndBase64Str 加密并转 Base64，展示时用 decryptStr 解密。因此库内直接比对手机号字符串不会命中，任何按手机号的查询/去重都必须先走加密链路。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由 phone 字段语义（「加密后以 Base64 存储」）得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 手机号加密存储
statement: cust_person_info.phone 加密后以 Base64 存储
condition: 写入或展示手机号
action: 写入用 encryptAndBase64Str，展示用 decryptStr；禁止明文比对
evidence: code_path:cust_person_info.phone（写入用 encryptAndBase64Str，展示用 decryptStr）
```

---END FILE---

---REVIEW: table | 物理库名归属待确认---
所有页面的 frontmatter scope.databases 暂填 [base]。该值取自 db 证据中 operation_user.db_tenant_code「实测仅出现 'base'（7 条）」的观察结果，属数据租户标识，并非已确认的物理库名。需要确认：(1) 本主题涉及表（operation_user、org_manage、cust_company_info、cust_person_info、cust_role_info、cust_user_rel、sys_user、sys_cust_org_user_permission、cust_group_rel）实际落在哪些物理库/数据源；(2) db_tenant_code 与物理库名之间的映射关系。确认后统一回填各页 frontmatter。
---END REVIEW---

---REVIEW: caliber | 语义分析 calibers 条目被截断---
语义分析的 calibers 数组末尾被截断于「二级组织绑定合法用户」一条，且 field_semantics、state_machines 亦无截断标记。存在以下可能：其后还有未纳入本次分析的口径（例如组级/机构级数据范围、运营人员机构绑定相关口径）。本批次已按现有证据产出 7 个 caliber 页；待语义分析补全后需重新比对是否遗漏口径，并检查 [[calibers/org_bound_legal_user]] 的完整定义。
---END REVIEW---