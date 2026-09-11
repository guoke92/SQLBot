---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（企业主数据表）
page_key: table.cust_company_info
domain: 平台内部服务对接
status: draft
aliases:
  - cust_company_info
  - 企业主数据表
  - 客户企业表
  - CustCompanyInfoDO
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info]
  - semantic:state_machines[企业建档/认证状态, 客户生命周期状态]
contract_version: "0.1"
---

企业主数据表，平台内部服务对接中「客户」这一实体的唯一权威载体。对外 Provider 暴露的 companyId / custId 即本表主键，各关系表（[[tables/cust_person_info]]、[[tables/cust_role_info]]、[[tables/cust_project_rel]]、[[tables/cust_group_rel]]）通过业务编码 code 挂接本表。

## 需求背景

企业信息需要在「客户中心—运营中台—业务系统」之间来回同步：建档与认证状态由 [[processes/cust_build_status_machine]] 驱动，生命周期状态由 [[processes/cust_status_machine]] 驱动，两者字段分离、互不覆盖。有效数据一律以 enable='Y' 为前提（见 [[rules/company_query_enable_y]]），状态类更新必须限定主数据（见 [[rules/status_update_main_data_type]]）。

## 版本演进

v0：按语义分析给出的字段语义与状态机证据首次成页；仅收录有证据的字段含义，未收录的列不做推断。

```ground:table
table: cust_company_info
columns:
  - field: id
    meaning: "企业主键，对外 Provider 的 companyId/custId 即此值（DO: CustCompanyInfoDO）"
    evidence: code
  - field: code
    meaning: "企业业务编码，新建时由 DataModelUtils.uuid() 生成，作为各关系表 ref_cust_company_info 的关联键"
    evidence: code
  - field: name
    meaning: "企业名称"
    evidence: code
  - field: certification_no
    meaning: "统一社会信用代码，跨系统一致性对齐字段"
    evidence: code
  - field: enable
    meaning: "有效标志，查询一律 .eq(enable, 'Y')"
    evidence: code
  - field: db_tenant_code
    meaning: "数据租户编码，数据隔离键；Provider 层常用 MetaDataThreadLocalConfig.setDbTenantCode(\"all\") 跨租户查询"
    evidence: code
  - field: cust_build_status
    meaning: "建档/认证状态（见状态机）"
    evidence: code
  - field: cust_status
    meaning: "客户生命周期状态（见状态机），与建档状态分离"
    evidence: code
  - field: cust_company_type
    meaning: "企业角色，JSON 数组字符串，如 \"[\\\"CORE\\\"]\"，创建时由 JSONArray/字符串拼接写入"
    evidence: code
  - field: identify_style
    meaning: "认证方式（自主/邀请-客户录入/邀请-平台录入/简易）"
    evidence: code
  - field: cust_build_type
    meaning: "建档渠道类型（PC_BUILD / AGW_BUILD）"
    evidence: code
  - field: cust_from
    meaning: "客户来源，邀请类认证为空时写 \"平台邀请\""
    evidence: code
  - field: data_type
    meaning: "数据类型，主数据为 CustDataTypeConstant.DATA_TYPE_MAIN；状态更新均带此条件"
    evidence: code
  - field: check_status
    meaning: "审核状态，提交建档时被置 null"
    evidence: code
  - field: audit_back_flag
    meaning: "审核退回标记 'Y'/'N'，非自主录入提交时置 'N'"
    evidence: code
  - field: need_register_ca
    meaning: "是否需要开通电子签章 'Y'/'N'；简易建档政策上强制为不开通"
    evidence: code
  - field: ca_register_status
    meaning: "电子签章开通状态 'Y'/'N'（对外返回还需叠加 caRegisterStatusY 校验）"
    evidence: code
  - field: need_register_bs
    meaning: "是否需要开通上上签 'Y'/'N'"
    evidence: code
  - field: bs_register_status
    meaning: "上上签开通状态 'Y'/'N'"
    evidence: code
  - field: legal_name / legal_phone / legal_email / legal_certification_type / legal_certification_no
    meaning: "法人姓名/电话/邮箱/证件类型/证件号，用于开通 CA 请求体"
    evidence: code
  - field: cust_email
    meaning: "企业邮箱"
    evidence: code
  - field: contact_address
    meaning: "联系地址"
    evidence: code
  - field: head_company
    meaning: "总部/集团企业标识，为空时（简易认证）置为 'Y'"
    evidence: code
  - field: ext
    meaning: "扩展 JSON，含 isChange/alterMode/alterTypes 等变更指令"
    evidence: code
  - field: cust_source
    meaning: "客户来源渠道标识（如 PLATFORM_PUSH）"
    evidence: code
```
---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info（企业联系人表）
page_key: table.cust_person_info
domain: 平台内部服务对接
status: draft
aliases:
  - cust_person_info
  - 企业联系人表
  - 经办人表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info]
contract_version: "0.1"
---

企业联系人（含客户管理员、经办人、游客）明细表。联系人既挂在企业 code 上，也通过 user_id 串联用户中心（[[tables/sys_user_sso_user]]），是内部服务对接中「人—企业—产品」链路的中间节点。

## 需求背景

联系人的有效性与企业侧口径不同：企业看 enable，联系人查询有效数据时取 status ∈ {ADD, EFFECT}（见 [[calibers/person_effective_status]]）。经办人无产品权限时会被置 enable='N'，解冻后恢复（见 [[rules/operator_permission_disable]]）。手机号加密存储，查询需传密文（见 [[rules/person_phone_encrypted_query]]）。

## 版本演进

v0：首次成页，收录语义分析中给出含义的联系人字段。

```ground:table
table: cust_person_info
columns:
  - field: ref_cust_company_info
    meaning: "所属企业 code，联系人查询主关联键"
    evidence: code
  - field: cust_company_id
    meaning: "所属企业 id"
    evidence: code
  - field: phone
    meaning: "手机号，加密存储（metaDataEncryptionService.encryptAndBase64Str），查询需传密文"
    evidence: code
  - field: user_id
    meaning: "对应 sys_user 主键，用于按用户维度串联企业联系人"
    evidence: code
  - field: user_type
    meaning: "用户类型：admin（客户管理员）/ operator（经办人）/ guest（游客）"
    evidence: code
  - field: company_type
    meaning: "企业角色（单值，对应 cust_company_type 数组中的一项）"
    evidence: code
  - field: status
    meaning: "联系人状态，查询有效联系人时取 ADD 或 EFFECT（CustPersonStatusConstant）"
    evidence: code
  - field: enable
    meaning: "有效标志 'Y'/'N'；经办人无产品权限时被置 'N'，解冻时恢复 'Y'"
    evidence: code
  - field: name / user_name / email
    meaning: "姓名/登录名/业务邮箱；仅本身为空时才由经办人新增流程补全"
    evidence: code
  - field: operator_id / operator_realname / operator
    meaning: "运营人员 id/姓名/登录名，由资产审核运营人员同步写入"
    evidence: code
  - field: operator_push_system
    meaning: "需要推送的运营中台渠道集合，逗号分隔，用于 systemLinkFacade.syncOperation"
    evidence: code
  - field: cust_build_status
    meaning: "联系人侧冗余的建档状态"
    evidence: code
```
---END FILE---

---FILE: tables/cust_role_info.md ---
---
type: table
title: cust_role_info（企业角色授权表）
page_key: table.cust_role_info
domain: 平台内部服务对接
status: draft
aliases:
  - cust_role_info
  - 企业角色表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_role_info]
contract_version: "0.1"
---

企业角色维度表，一个「企业 code + 角色」一行，用于承接运营中台企业 id（platform_cust_id）并参与换取 token / 授权。

## 需求背景

企业角色在 [[tables/cust_company_info]] 中以 JSON 数组存放，在关系表中拆成单值记录（见 [[concepts/company_role_bridge]]）。角色状态不独立演进，而是随企业状态联动更新（见 [[rules/role_status_follow_company]]）。

## 版本演进

v0：首次成页。

```ground:table
table: cust_role_info
columns:
  - field: ref_cust_company_info
    meaning: "所属企业 code"
    evidence: code
  - field: role_type
    meaning: "企业角色类型（CustCompanyTypeEnum.name()/dictKey），一个企业 code + 角色一条记录"
    evidence: code
  - field: status
    meaning: "角色状态，随企业状态更新（updateStatusByCustCompany）"
    evidence: code
  - field: platform_cust_id
    meaning: "运营中台企业 id（custEnterpriseId），用于换取 token/授权"
    evidence: code
  - field: enable / db_tenant_code
    meaning: "有效标志与租户编码"
    evidence: code
```
---END FILE---

---FILE: tables/cust_project_rel.md ---
---
type: table
title: cust_project_rel（企业—项目/产品关联表）
page_key: table.cust_project_rel
domain: 平台内部服务对接
status: draft
aliases:
  - cust_project_rel
  - 企业项目关联表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_project_rel]
contract_version: "0.1"
---

企业与租户项目/产品的关联关系表，承载「哪个企业以什么角色开通了哪个产品」这一对接事实。

## 需求背景

项目与产品 id 以字符串形式存储，并与 [[tables/tenant_project]] 的 project_id、[[tables/platform_product]] 的 product_code 对齐（见 [[concepts/product_code_bridge]]）。tenant_code 与 db_tenant_code 同值写入，是租户隔离在关系表上的落点。

## 版本演进

v0：首次成页。

```ground:table
table: cust_project_rel
columns:
  - field: ref_cust_project_rel_cust_company_info
    meaning: "关联企业 code"
    evidence: code
  - field: project_id / product_id
    meaning: "关联租户项目 id / 产品 id（字符串存储）"
    evidence: code
  - field: tenant_code / db_tenant_code
    meaning: "租户编码（两者同值写入）"
    evidence: code
  - field: company_type
    meaning: "关联关系对应的企业角色"
    evidence: code
  - field: show_flag
    meaning: "是否展示 'Y'/'N'"
    evidence: code
  - field: enable
    meaning: "有效标志 'Y'/'N'"
    evidence: code
  - field: ref_cust_project_rel_platform_product / op_contact_a / op_contact_a_group
    meaning: "平台产品编码 / 运营对接人 / 运营对接人组"
    evidence: code
```
---END FILE---

---FILE: tables/cust_group_rel.md ---
---
type: table
title: cust_group_rel（集团/企业树关系表）
page_key: table.cust_group_rel
domain: 平台内部服务对接
status: draft
aliases:
  - cust_group_rel
  - 集团关系表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_group_rel]
contract_version: "0.1"
---

描述企业之间的集团树形结构：当前企业、直接父企业、根企业的 id 与集团节点 id 双轨记录，并给出层级与根标识。

## 需求背景

总部/集团标识在 [[tables/cust_company_info]] 中以 head_company 表达，树形结构则落在本表；成员角色 cust_type 与企业的角色数组同源（见 [[concepts/company_role_bridge]]）。根节点 level 为 1，root_flag='Y'。

## 版本演进

v0：首次成页。

```ground:table
table: cust_group_rel
columns:
  - field: cust_id / parent_cust_id / root_cust_id
    meaning: "当前企业 / 直接父企业 / 集团根企业 id"
    evidence: code
  - field: parent_group_id / root_group_id
    meaning: "直接父集团节点 / 根集团节点 id（树形结构键）"
    evidence: code
  - field: cust_type
    meaning: "成员角色，JSON 数组字符串"
    evidence: code
  - field: status
    meaning: "生效状态 INEFFECTIVE/EFFECTIVE"
    evidence: code
  - field: root_flag
    meaning: "是否根节点 'Y'"
    evidence: code
  - field: level
    meaning: "层级，根节点为 1"
    evidence: code
```
---END FILE---

---FILE: tables/sys_cust_user_rel.md ---
---
type: table
title: sys_cust_user_rel（企业—用户—角色—产品授权表）
page_key: table.sys_cust_user_rel
domain: 平台内部服务对接
status: draft
aliases:
  - sys_cust_user_rel
  - 授权关系表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[sys_cust_user_rel]
  - semantic:state_machines[经办人产品关联冻结状态]
contract_version: "0.1"
---

sys 服务侧的授权关系表，记录企业、用户、角色、产品四元关系及其冻结状态，是平台内部服务鉴权对接的落地表。

## 需求背景

冻结状态由 [[processes/operator_freeze_machine]] 描述：冻结经办人置 'Y'，解冻置 'N'。冻结同时会影响 [[tables/cust_person_info]] 的 enable 取值（见 [[rules/operator_permission_disable]]）。

## 版本演进

v0：首次成页。

```ground:table
table: sys_cust_user_rel
columns:
  - field: cust_id / cust_type / user_id / role_id / product_id
    meaning: "企业-用户-角色-产品的授权关系（sys 服务表）"
    evidence: code
  - field: is_freeze
    meaning: "关联是否冻结 'Y'/'N'（UserFreezeEnum.FREEZE/UN_FROZEN）"
    evidence: code
```
---END FILE---

---FILE: tables/tenant_setting_config.md ---
---
type: table
title: tenant_setting_config（租户配置表）
page_key: table.tenant_setting_config
domain: 平台内部服务对接
status: draft
aliases:
  - tenant_setting_config
  - 租户配置表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config]
contract_version: "0.1"
---

租户级配置表，是平台内部服务对接的「参数中枢」：运营中台鉴权秘钥、SSO 渠道、门户与小程序配置、子账号授权书模板等均由此表驱动。

## 需求背景

对接运营中台时，sysChannel 取 sso_tenant_chanel，鉴权秘钥取 platform_secret_key，二者共同参与签名计算（见 [[rules/token_sign_md5]]）。生效租户的判定口径见 [[calibers/tenant_active_list]]，平台运营方取值口径见 [[calibers/platform_operator_value]]。运营中台企业 id 的对接字段见 [[concepts/platform_cust_id_bridge]]。

## 版本演进

v0：首次成页；仅收录语义分析中明确给出含义的配置项。

```ground:table
table: tenant_setting_config
columns:
  - field: db_tenant_code
    meaning: "租户数据编码，全局隔离键"
    evidence: code
  - field: enable / status
    meaning: "有效标志 / 生效标志（查询生效租户 activeList、'Y' 判定）"
    evidence: code
  - field: sso_tenant_chanel
    meaning: "SSO 渠道标识，作为 sysChannel 用于请求运营中台 token 与拉取互通系统列表"
    evidence: code
  - field: platform_secret_key
    meaning: "运营中台鉴权秘钥，参与 md5(secret+sysChannel+loginName)"
    evidence: code
  - field: platform_operator
    meaning: "平台运营方配置，JSON 数组，取值 PLATFORM（联易融）/TENANT（租户自身）"
    evidence: code
  - field: band_name
    meaning: "品牌名，用于同步给运营中台的 bizLabel"
    evidence: code
  - field: oper_auth_agreement
    meaning: "子账号授权书模板 id，未配置时回落 Nacos 值 operAuthAgreement"
    evidence: code
  - field: source / portal_flag / need_hfive / need_mp_wx
    meaning: "租户来源（PPLATFORM_SYSTEM）/ 门户开关 / 是否需要 H5 / 是否需要小程序微信配置，用于配置完备性校验"
    evidence: code
  - field: prd_mp_app_id / uat_mp_app_id / hfive_dev_domain / hfive_test_domain / hfive_uat_domain / hfive_prd_domain
    meaning: "小程序 appid 与环境域名，按 spring.profiles.active 取值"
    evidence: code
  - field: is_stack
    meaning: "是否堆栈/迁移标识 'Y'/'N'，决定 PlatMiniProgramTenantInfoDto 的 migratory/stock"
    evidence: code
```
---END FILE---

---FILE: tables/tenant_product.md ---
---
type: table
title: tenant_product（租户产品开通表）
page_key: table.tenant_product
domain: 平台内部服务对接
status: draft
aliases:
  - tenant_product
  - 租户产品表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_product]
contract_version: "0.1"
---

记录某租户开通了哪些平台产品，以及这些产品是否已完成迁移。

## 需求背景

产品编码与 [[tables/platform_product]] 的 product_code 对齐（见 [[concepts/product_code_bridge]]），项目层实体见 [[tables/tenant_project]]；迁移标识与租户级 is_stack 的语义相关（见 [[calibers/tenant_stack_migratory]]）。

## 版本演进

v0：首次成页。

```ground:table
table: tenant_product
columns:
  - field: platform_product_code / db_tenant_code
    meaning: "租户开通的平台产品编码 / 租户编码"
    evidence: code
  - field: is_migratory
    meaning: "租户产品是否已迁移 'Y'/'N'"
    evidence: code
```
---END FILE---

---FILE: tables/tenant_project.md ---
---
type: table
title: tenant_project（租户项目表）
page_key: table.tenant_project
domain: 平台内部服务对接
status: draft
aliases:
  - tenant_project
  - 租户项目表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_project]
contract_version: "0.1"
---

租户下的项目实体，承接产品编码与项目状态，是企业—项目关联（[[tables/cust_project_rel]]）的另一端。

## 需求背景

项目列表展示时需要回带产品名称，名称来源为 [[tables/platform_product]]。项目状态生效值为 EFFECTIVE。

## 版本演进

v0：首次成页。

```ground:table
table: tenant_project
columns:
  - field: tenant_id / platform_product_code / product_id / name
    meaning: "所属租户 id / 平台产品编码 / 产品 id / 项目名"
    evidence: code
  - field: project_status / enable / db_tenant_code
    meaning: "项目状态（EFFECTIVE 生效）/ 有效标志 / 租户编码"
    evidence: code
```
---END FILE---

---FILE: tables/platform_product.md ---
---
type: table
title: platform_product（平台产品表）
page_key: table.platform_product
domain: 平台内部服务对接
status: draft
aliases:
  - platform_product
  - 平台产品表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[platform_product]
contract_version: "0.1"
---

平台侧产品字典表，提供产品编码与名称，是项目列表展示与租户产品开通的对照基准。

## 需求背景

产品编码在多个关系表中以不同列名出现（platform_product_code、ref_cust_project_rel_platform_product），统一口径见 [[concepts/product_code_bridge]]。

## 版本演进

v0：首次成页。

```ground:table
table: platform_product
columns:
  - field: product_code / name
    meaning: "平台产品编码与名称（用于项目列表展示 product 名）"
    evidence: code
```
---END FILE---

---FILE: tables/sys_user_sso_user.md ---
---
type: table
title: sys_user / sso_user（用户中心与 SSO 用户表）
page_key: table.sys_user_sso_user
domain: 平台内部服务对接
status: draft
aliases:
  - sys_user
  - sso_user
  - 用户中心表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[sys_user / sso_user]
contract_version: "0.1"
---

用户中心（sys_user）与 SSO（sso_user）两张表在语义分析中作为同一组用户身份字段来源给出，是经办人信息的事实基准。

## 需求背景

[[tables/cust_person_info]] 的姓名/登录名/业务邮箱仅在自身为空时才由经办人新增流程补全，其权威来源是本组表（见 [[rules/person_info_source_of_truth]]）。user_id 与 [[tables/cust_person_info]] 的 user_id 指向 sys_user 主键。

## 版本演进

v0：首次成页；按语义分析给出的合并条目收录字段，未拆分为两页。

```ground:table
table: sys_user / sso_user
columns:
  - field: id / login_name / user_name / name / email / mobile / certificate_type / certificate_no / certification_start_time / certification_end_time
    meaning: "用户中心与 SSO 用户字段，经办人信息以 sys_user+sso_user 为准，业务邮箱变更时按条件回写登录邮箱"
    evidence: code
```
---END FILE---

---FILE: tables/cust_change_record.md ---
---
type: table
title: cust_change_record（客户变更记录表）
page_key: table.cust_change_record
domain: 平台内部服务对接
status: draft
aliases:
  - cust_change_record
  - 客户变更记录表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_change_record]
contract_version: "0.1"
---

客户信息变更流程的记录表，保存变更前后内容、操作渠道与状态，并在变更态下提供运营中台企业 id。

## 需求背景

当企业处于变更中（cust_status=CHANGE）时，换取 token 所需的运营中台企业 id 取自本表记录中的 custEnterpriseId 而非 [[tables/cust_role_info]]（见 [[rules/change_status_token_source]]）。有效记录的取用口径见 [[rules/cust_change_record_latest_effective]]。

## 版本演进

v0：首次成页。

```ground:table
table: cust_change_record
columns:
  - field: cust_id / status / oper_cust_info / oper_channel / create_time
    meaning: "客户变更记录；status 取 CUST_CHECK_PASS 时作为取值最新有效记录；oper_cust_info JSON 中的 custEnterpriseId 用于运营中台 id"
    evidence: code
```
---END FILE---

---FILE: tables/lc_sql_init_log.md ---
---
type: table
title: lc_sql_init_log（插件 SQL 执行日志表）
page_key: table.lc_sql_init_log
domain: 平台内部服务对接
status: draft
aliases:
  - lc_sql_init_log
  - 插件SQL日志表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[lc_sql_init_log]
contract_version: "0.1"
---

记录插件（低代码扩展）执行 SQL 文本的日志表，用于排查内部服务对接过程中由插件代执行的 DDL/DML。

## 需求背景

本表 name 列虽命名为「插件名称」，但实测取值为 '2'/'3'/'a'/'b' 等测试脏数据，不能作为业务枚举口径使用；description 列才是真正承载 SQL 文本的字段（varchar(1024)）。任何按 name 做插件分类统计的尝试都缺乏证据支撑。

## 版本演进

v0：首次成页；name 的「插件名称」语义仅来自 DDL 注释，实测数据不支持该口径，故不产出对应枚举页。

```ground:table
table: lc_sql_init_log
columns:
  - field: id
    meaning: "自增主键"
    evidence: db
  - field: name
    meaning: "插件名称（DDL 注释如此，但实测值为 '2'/'3'/'a'/'b'，属测试脏数据，不可作为业务枚举口径）"
    evidence: db
  - field: description
    meaning: "插件执行的 sql 文本（varchar(1024)）"
    evidence: db
```
---END FILE---

---FILE: processes/cust_build_status_machine.md ---
---
type: process
title: 企业建档/认证状态机（cust_company_info.cust_build_status）
page_key: process.cust_build_status
domain: 平台内部服务对接
status: draft
aliases:
  - 建档状态
  - 认证状态机
  - cust_build_status
oid: 1
scope:
  databases: []
sources:
  - semantic:state_machines[企业建档/认证状态]
  - semantic:field_semantics[cust_company_info.cust_build_status]
contract_version: "0.1"
---

企业从临时创建到建档成功的完整流转，由 RVS 创建、客户提交、运营中台审核三类事件驱动，并区分自主/邀请录入与简易认证两条支路。

## 需求背景

建档状态与生命周期状态分离：审核通过时除置 BUILD_SUCCESS 外还会把 cust_status 置为 EFFECT（见 [[processes/cust_status_machine]]）。不同认证方式决定提交后的落点状态与是否需要退回标记（见 [[rules/submit_cust_field_reset]]）；简易认证路径额外受 CA 开通政策约束（见 [[rules/simple_auth_ca_forbidden]]）。

## 版本演进

v0：按语义分析给出的状态与转换证据首次成页，未收录无证据的转换。

```ground:process
name: 企业建档/认证状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化（新建临时企业）
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证路径）
    source: code_enum
  - value: CUST_BUILDING
    label: 客户已提交/运营中台审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败/被拒
    source: code_enum
transitions:
  - from: INIT
    event: "RVS 调 getAndCreateTempCompany 创建临时企业"
    to: INIT
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormRvsApplication.java#getAndCreateTempCompany"
  - from: INIT
    event: "邀请认证-客户录入/注册认证提交"
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#submitCust + #getCustBuildStatus(IdentifyTypeConstant.INVITE/SELF)"
  - from: INIT
    event: "邀请认证-平台录入提交"
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java#submitCust + #getCustBuildStatus(IdentifyTypeConstant.INVITE_AGW)"
  - from: BUILD_FAIL
    event: "被拒后重新提交"
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(条件 before==INIT||before==BUILD_FAIL && after==CUST_CONFIRM_AWAIT)"
  - from: CUST_CONFIRM_AWAIT
    event: "客户提交进入运营中台审核"
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(#updateCustBuildStatus 分支 before==CUST_CONFIRM_AWAIT && after==CUST_BUILDING)"
  - from: CUST_BUILDING
    event: "运营中台审核退回"
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(分支 before==CUST_BUILDING && after==CUST_CONFIRM_AWAIT)"
  - from: CUST_BUILDING
    event: "审核通过（同时置 cust_status=EFFECT）"
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(after==BUILD_SUCCESS → custCompanyInfoService.updateById(custStatus=EFFECT))"
  - from: CUST_CONFIRM_AWAIT
    event: "平台录入客户点击确认提交"
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(IdentifyTypeConstant.INVITE_AGW 且 after==BUILD_SUCCESS)"
  - from: CUST_BUILDING
    event: "运营中台审核拒绝"
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(after==BUILD_FAIL 发送拒绝通知/短信)"
  - from: CUST_CONFIRM_AWAIT
    event: "审核拒绝"
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(after==BUILD_FAIL)"
  - from: INIT
    event: "简易认证提交"
    to: AWAIT_CUST_CONFIRM
    evidence: "code_path:CustCompanyInfoApplication.java#submitForSimpleAuth(companyInfoDO.setCustBuildStatus(AWAIT_CUST_CONFIRM))"
  - from: AWAIT_CUST_CONFIRM
    event: "客户确认（简易认证）"
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java#confirmCustInfoForSimpleAuth(custCompanyInfoDao.updateStatus(custId, BUILD_SUCCESS, CustStatusEnum.EFFECT))"
```
---END FILE---

---FILE: processes/cust_status_machine.md ---
---
type: process
title: 客户生命周期状态机（cust_company_info.cust_status）
page_key: process.cust_status
domain: 平台内部服务对接
status: draft
aliases:
  - 客户生命周期状态
  - cust_status
  - 企业状态机
oid: 1
scope:
  databases: []
sources:
  - semantic:state_machines[客户生命周期状态]
  - semantic:field_semantics[cust_company_info.cust_status]
contract_version: "0.1"
---

企业作为「客户」的生命周期状态：新增、变更中、生效、冻结、注销。它独立于建档状态，但在建档成功时被同步推进为 EFFECT。

## 需求背景

冻结/解冻/注销均由客户中心发起并同步（custStatusSync）。进入 CHANGE 后，换取运营中台 token 的企业 id 来源发生变化（见 [[rules/change_status_token_source]]）。状态类更新一律限定主数据（见 [[rules/status_update_main_data_type]]）。

## 版本演进

v0：按语义分析给出的状态与转换证据首次成页。

```ground:process
name: 客户生命周期状态
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/待处理（新建企业与自主注册初始态）
    source: code_enum
  - value: CHANGE
    label: 变更中（走变更流程，token 取变更记录上的运营中台 id）
    source: code_enum
  - value: EFFECT
    label: 已生效
    source: code_enum
  - value: FREEZE
    label: 已冻结
    source: code_enum
  - value: WRITEOFF
    label: 已注销
    source: code_enum
transitions:
  - from: ADD
    event: "建档成功"
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(custStatus=EFFECT) / #confirmCustInfoForSimpleAuth"
  - from: EFFECT
    event: "冻结企业"
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java#freeze → #custStatusOperator + #custStatusSync(CustStatusEnum.FREEZE)"
  - from: FREEZE
    event: "解冻企业"
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java#unfreeze → #custStatusSync(CustStatusEnum.EFFECT)"
  - from: EFFECT
    event: "注销/停用企业"
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java#diable → #custStatusOperator(WRITEOFF) + #custStatusSync(CustStatusEnum.WRITEOFF)"
  - from: ADD
    event: "发起变更流程"
    to: CHANGE
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/facade/cust/OperCustFacade.java#queryCustAutoCheck(process!=CHECK → CustStatusEnum.CHANGE)"
```
---END FILE---

---FILE: processes/operator_freeze_machine.md ---
---
type: process
title: 经办人产品关联冻结状态机（sys_cust_user_rel.is_freeze）
page_key: process.operator_freeze
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人冻结
  - is_freeze
  - 授权冻结状态
oid: 1
scope:
  databases: []
sources:
  - semantic:state_machines[经办人产品关联冻结状态]
  - semantic:field_semantics[sys_cust_user_rel.is_freeze]
contract_version: "0.1"
---

经办人与产品之间授权关系的冻结状态，只有「未冻结 / 已冻结」两态，由运营侧的冻结与解冻操作驱动。

## 需求背景

冻结影响下游联系人可用性：经办人无产品权限时 [[tables/cust_person_info]].enable 被置 'N'，解冻时恢复 'Y'（见 [[rules/operator_permission_disable]]）。冻结状态取值语义与 UserFreezeEnum 对齐。

## 版本演进

v0：按语义分析给出的状态与转换证据首次成页；语义分析中该状态机的转换列表末尾存在截断，仅收录完整可读的转换（见文末 REVIEW）。

```ground:process
name: 经办人产品关联冻结状态
field: sys_cust_user_rel.is_freeze
states:
  - value: N
    label: 未冻结
    source: code_enum
  - value: Y
    label: 已冻结
    source: code_enum
transitions:
  - from: N
    event: "冻结经办人（operationType=FREEZE）"
    to: Y
    evidence: "code_path:CustCompanyInfoApplication 同仓 PlatFormUserApplication.java#freezeOrThawOperatorUser(sysCustUserRelDO.setIsFreeze(\"Y\"))"
  - from: Y
    event: "解冻经办人（operationType=THAW）"
    to: N
    evidence: "code_path:PlatFormUserApplication.java#freezeOrThawOperatorUser(THAW 分支 setIsFreeze(\"N\"))"
```
---END FILE---

---FILE: calibers/enable_valid_flag.md ---
---
type: caliber
title: 有效标志口径（enable='Y'）
page_key: caliber.enable_valid_flag
domain: 平台内部服务对接
status: draft
aliases:
  - 有效标志
  - enable 口径
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.enable]
  - semantic:field_semantics[cust_person_info.enable]
  - semantic:field_semantics[cust_project_rel.enable]
  - semantic:field_semantics[tenant_setting_config.enable / status]
contract_version: "0.1"
---

「有效」在多数业务表中的表达方式为字符标志位，取值 'Y'/'N'。

## 需求背景

企业查询一律附加 .eq(enable, 'Y')（见 [[rules/company_query_enable_y]]）；联系人侧的 enable 会因经办人权限被逻辑改写，因此不能等同于企业侧口径，二者同时参与有效数据判定时需分别处理（见 [[rules/operator_permission_disable]]）。租户侧的生效判定还要叠加 status（见 [[calibers/tenant_active_list]]）。

## 版本演进

v0：首次成页。

```ground:caliber
name: 有效标志口径
field: enable
values:
  - "'Y'"
  - "'N'"
criterion: "查询有效数据一律 .eq(enable, 'Y')"
applies_to:
  - cust_company_info.enable
  - cust_person_info.enable
  - cust_project_rel.enable
evidence: code
```
---END FILE---

---FILE: calibers/person_effective_status.md ---
---
type: caliber
title: 有效联系人状态口径（status ∈ {ADD, EFFECT}）
page_key: caliber.person_effective_status
domain: 平台内部服务对接
status: draft
aliases:
  - 有效联系人
  - CustPersonStatusConstant
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.status]
contract_version: "0.1"
---

联系人没有沿用 enable 作为有效性判据，而是以状态枚举判定：查询有效联系人时取 ADD 或 EFFECT。

## 需求背景

该口径与企业的建档/生命周期状态机（[[processes/cust_build_status_machine]]、[[processes/cust_status_machine]]）不是同一套枚举，跨表统计时不可混用。联系人侧另有 cust_build_status 冗余字段，两者需区分。

## 版本演进

v0：首次成页。

```ground:caliber
name: 有效联系人状态口径
field: cust_person_info.status
values:
  - ADD
  - EFFECT
criterion: "查询有效联系人时取 ADD 或 EFFECT（CustPersonStatusConstant）"
evidence: code
```
---END FILE---

---FILE: calibers/ca_register_status_output.md ---
---
type: caliber
title: 电子签章开通状态对外口径（ca_register_status + caRegisterStatusY）
page_key: caliber.ca_register_status_output
domain: 平台内部服务对接
status: draft
aliases:
  - 签章开通口径
  - caRegisterStatusY
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.ca_register_status]
  - semantic:field_semantics[cust_company_info.need_register_ca]
contract_version: "0.1"
---

对外返回企业是否已开通电子签章时，不能只看 ca_register_status，还需叠加 caRegisterStatusY 校验。

## 需求背景

是否「需要」开通与是否「已」开通是两个字段：need_register_ca 表达诉求，ca_register_status 表达结果，对外输出需两者与校验标记共同决定。简易认证路径下 need_register_ca 被政策强制为不开通（见 [[rules/simple_auth_ca_forbidden]]）。

## 版本演进

v0：首次成页。

```ground:caliber
name: 电子签章开通状态对外口径
field: cust_company_info.ca_register_status
values:
  - "'Y'"
  - "'N'"
criterion: "对外返回还需叠加 caRegisterStatusY 校验"
related_fields:
  - cust_company_info.need_register_ca
evidence: code
```
---END FILE---

---FILE: calibers/cust_from_platform_invite.md ---
---
type: caliber
title: 客户来源空值口径（邀请类认证写「平台邀请」）
page_key: caliber.cust_from_platform_invite
domain: 平台内部服务对接
status: draft
aliases:
  - 平台邀请
  - cust_from 口径
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.cust_from]
  - semantic:field_semantics[cust_company_info.cust_source]
contract_version: "0.1"
---

客户来源在邀请类认证（客户录入/平台录入）且原值为空时，统一补写为「平台邀请」。

## 需求背景

cust_from 与 cust_source 语义不同：前者是业务来源描述（可为「平台邀请」），后者是渠道标识（如 PLATFORM_PUSH）。统计来源分布时应先明确取哪一列。

## 版本演进

v0：首次成页。

```ground:caliber
name: 客户来源空值口径
field: cust_company_info.cust_from
values:
  - "平台邀请"
criterion: "邀请类认证为空时写 \"平台邀请\""
related_fields:
  - cust_company_info.cust_source
evidence: code
```
---END FILE---

---FILE: calibers/main_data_type.md ---
---
type: caliber
title: 主数据判定口径（data_type = DATA_TYPE_MAIN）
page_key: caliber.main_data_type
domain: 平台内部服务对接
status: draft
aliases:
  - 主数据
  - DATA_TYPE_MAIN
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.data_type]
contract_version: "0.1"
---

企业表同一物理表内混放多类数据，主数据以 CustDataTypeConstant.DATA_TYPE_MAIN 标识。

## 需求背景

所有状态更新均带此条件限定（见 [[rules/status_update_main_data_type]]），否则会误改非主数据行。这是企业侧最基础的一致性口径，跨服务写企业状态时必须遵守。

## 版本演进

v0：首次成页。

```ground:caliber
name: 主数据判定口径
field: cust_company_info.data_type
values:
  - CustDataTypeConstant.DATA_TYPE_MAIN
criterion: "状态更新均带此条件"
evidence: code
```
---END FILE---

---FILE: calibers/tenant_active_list.md ---
---
type: caliber
title: 生效租户口径（activeList / enable 与 status 双判定）
page_key: caliber.tenant_active_list
domain: 平台内部服务对接
status: draft
aliases:
  - 生效租户
  - activeList
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.enable / status]
contract_version: "0.1"
---

租户配置的生效判定需同时满足有效标志与生效标志，查询生效租户时以 activeList 形式取用。

## 需求背景

租户配置项（[[tables/tenant_setting_config]]）是平台内部服务对接的前置条件，未生效租户不应参与 token 换取与互通系统拉取。

## 版本演进

v0：首次成页。

```ground:caliber
name: 生效租户口径
field: tenant_setting_config.enable / status
values:
  - "'Y'"
criterion: "查询生效租户 activeList、'Y' 判定"
evidence: code
```
---END FILE---

---FILE: calibers/platform_operator_value.md ---
---
type: caliber
title: 平台运营方取值口径（PLATFORM / TENANT）
page_key: caliber.platform_operator_value
domain: 平台内部服务对接
status: draft
aliases:
  - 平台运营方
  - platform_operator
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.platform_operator]
contract_version: "0.1"
---

tenant_setting_config.platform_operator 以 JSON 数组存放平台运营方，取值 PLATFORM（联易融）或 TENANT（租户自身）。

## 需求背景

该字段决定运营主体归属，影响对接链路上由谁提供运营能力。它是数组结构而非单值，判定时需按集合语义处理。

## 版本演进

v0：首次成页。

```ground:caliber
name: 平台运营方取值口径
field: tenant_setting_config.platform_operator
values:
  - PLATFORM
  - TENANT
criterion: "JSON 数组，取值 PLATFORM（联易融）/TENANT（租户自身）"
evidence: code
```
---END FILE---

---FILE: calibers/tenant_stack_migratory.md ---
---
type: caliber
title: 堆栈/迁移标识口径（is_stack → migratory/stock）
page_key: caliber.tenant_stack_migratory
domain: 平台内部服务对接
status: draft
aliases:
  - is_stack
  - 迁移标识
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.is_stack]
  - semantic:field_semantics[tenant_product.is_migratory]
contract_version: "0.1"
---

租户级 is_stack 决定小程序租户信息 DTO 中 migratory/stock 的取值，产品级另有 is_migratory 表示产品迁移状态。

## 需求背景

两者分属租户层与产品层：租户级标识影响小程序信息输出（PlatMiniProgramTenantInfoDto），产品级标识表达 [[tables/tenant_product]] 的开通产品是否已迁移，不可互相替代。

## 版本演进

v0：首次成页。

```ground:caliber
name: 堆栈/迁移标识口径
field: tenant_setting_config.is_stack
values:
  - "'Y'"
  - "'N'"
criterion: "决定 PlatMiniProgramTenantInfoDto 的 migratory/stock"
related_fields:
  - tenant_product.is_migratory
evidence: code
```
---END FILE---

---FILE: concepts/company_id_bridge.md ---
---
type: concept
title: companyId / custId → 企业主键（cust_company_info.id）
page_key: concept.company_id_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - companyId
  - custId
  - cust_id
  - custCompanyId
  - 企业主键
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.id]
  - semantic:field_semantics[cust_person_info.cust_company_id]
  - semantic:field_semantics[cust_group_rel.cust_id / parent_cust_id / root_cust_id]
contract_version: "0.1"
maps_to:
  - term: companyId
    target: cust_company_info.id
    evidence: code
  - term: custId
    target: cust_company_info.id
    evidence: code
  - term: cust_company_id
    target: cust_company_info.id
    evidence: code
  - term: cust_id
    target: cust_company_info.id
    evidence: code
field_targets:
  - cust_company_info.id
  - cust_person_info.cust_company_id
  - cust_group_rel.cust_id
  - cust_group_rel.parent_cust_id
  - cust_group_rel.root_cust_id
also_confused_with:
  - cust_company_info.code
---

对外 Provider 暴露的 companyId / custId 与库内的 cust_company_id、cust_id 指向同一实体主键，即 [[tables/cust_company_info]].id。

## 需求背景

跨服务传参时同一个企业会以 companyId、custId、cust_company_id 三种写法出现；与之极易混淆的是业务编码 code，后者才是各关系表 ref_cust_company_info 系列列的关联键（见 [[concepts/company_code_bridge]]）。集团树中的 cust_id / parent_cust_id / root_cust_id 同样指向企业主键。

## 版本演进

v0：首次成页；仅登记有证据的术语映射，未对未出现的别名做外推。
---END FILE---

---FILE: concepts/company_code_bridge.md ---
---
type: concept
title: ref_cust_company_info → 企业业务编码（cust_company_info.code）
page_key: concept.company_code_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - ref_cust_company_info
  - 企业业务编码
  - cust_company_code
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.code]
  - semantic:field_semantics[cust_person_info.ref_cust_company_info]
  - semantic:field_semantics[cust_role_info.ref_cust_company_info]
  - semantic:field_semantics[cust_project_rel.ref_cust_project_rel_cust_company_info]
contract_version: "0.1"
maps_to:
  - term: ref_cust_company_info
    target: cust_company_info.code
    evidence: code
  - term: ref_cust_project_rel_cust_company_info
    target: cust_company_info.code
    evidence: code
field_targets:
  - cust_company_info.code
  - cust_person_info.ref_cust_company_info
  - cust_role_info.ref_cust_company_info
  - cust_project_rel.ref_cust_project_rel_cust_company_info
also_confused_with:
  - cust_company_info.id
---

各关系表中以 ref_cust_company_info（或带前缀的变体）命名的列，关联的不是企业主键而是业务编码，即 [[tables/cust_company_info]].code。

## 需求背景

该编码在新建企业时由 DataModelUtils.uuid() 生成，是关系表拼接的稳定锚点；联系人查询的主关联键即 ref_cust_company_info。做 join 时若误用 id 关联会漏数据。

## 版本演进

v0：首次成页。
---END FILE---

---FILE: concepts/db_tenant_code_bridge.md ---
---
type: concept
title: 租户编码术语桥（db_tenant_code / tenant_code / sysChannel）
page_key: concept.db_tenant_code_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - db_tenant_code
  - tenant_code
  - 租户编码
  - sysChannel
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.db_tenant_code]
  - semantic:field_semantics[cust_project_rel.tenant_code / db_tenant_code]
  - semantic:field_semantics[tenant_setting_config.db_tenant_code]
  - semantic:field_semantics[tenant_setting_config.sso_tenant_chanel]
contract_version: "0.1"
maps_to:
  - term: db_tenant_code
    target: tenant_setting_config.db_tenant_code
    evidence: code
  - term: tenant_code
    target: tenant_setting_config.db_tenant_code
    evidence: code
  - term: sysChannel
    target: tenant_setting_config.sso_tenant_chanel
    evidence: code
field_targets:
  - cust_company_info.db_tenant_code
  - cust_project_rel.tenant_code
  - cust_project_rel.db_tenant_code
  - tenant_setting_config.db_tenant_code
  - tenant_setting_config.sso_tenant_chanel
---

数据隔离键的统一术语：db_tenant_code 是全局隔离键，cust_project_rel 中 tenant_code 与 db_tenant_code 同值写入；对接运营中台时，sysChannel 取 tenant_setting_config.sso_tenant_chanel。

## 需求背景

Provider 层默认按当前租户隔离，跨租户查询需显式设置（见 [[rules/cross_tenant_query_all]]）。sysChannel 参与鉴权签名（见 [[rules/token_sign_md5]]），与 db_tenant_code 不是同一字段，但都源自租户配置（[[tables/tenant_setting_config]]）。

## 版本演进

v0：首次成页。
---END FILE---

---FILE: concepts/company_role_bridge.md ---
---
type: concept
title: 企业角色术语桥（cust_company_type / company_type / role_type / cust_type）
page_key: concept.company_role_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - 企业角色
  - cust_company_type
  - company_type
  - role_type
  - cust_type
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.cust_company_type]
  - semantic:field_semantics[cust_person_info.company_type]
  - semantic:field_semantics[cust_role_info.role_type]
  - semantic:field_semantics[cust_group_rel.cust_type]
  - semantic:field_semantics[cust_project_rel.company_type]
contract_version: "0.1"
maps_to:
  - term: cust_company_type
    target: cust_company_info.cust_company_type
    evidence: code
  - term: company_type
    target: cust_person_info.company_type
    evidence: code
  - term: role_type
    target: cust_role_info.role_type
    evidence: code
  - term: cust_type
    target: cust_group_rel.cust_type
    evidence: code
field_targets:
  - cust_company_info.cust_company_type
  - cust_person_info.company_type
  - cust_role_info.role_type
  - cust_group_rel.cust_type
  - cust_project_rel.company_type
---

「企业角色」在企业主表以 JSON 数组字符串存放，在关系表中拆成单值：联系人的 company_type 是数组中的一项，cust_role_info.role_type 一企业一角色一行，集团成员用 cust_type 表达，项目关联用 company_type 表达。

## 需求背景

同一角色概念在不同表以数组、单值、枚举名三种形态出现，跨表比对前需先做形态归一（数组展开 → 单值）。role_type 取值来自 CustCompanyTypeEnum.name()/dictKey，是这套术语的枚举基准。相关状态联动见 [[rules/role_status_follow_company]]。

## 版本演进

v0：首次成页；数组元素的具体取值范围在语义分析中仅以示例形式出现，未做穷举。
---END FILE---

---FILE: concepts/platform_cust_id_bridge.md ---
---
type: concept
title: 运营中台企业 id 术语桥（custEnterpriseId / platform_cust_id）
page_key: concept.platform_cust_id_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - custEnterpriseId
  - platform_cust_id
  - 运营中台企业id
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_role_info.platform_cust_id]
  - semantic:field_semantics[cust_change_record.cust_id / status / oper_cust_info / oper_channel / create_time]
contract_version: "0.1"
maps_to:
  - term: custEnterpriseId
    target: cust_role_info.platform_cust_id
    evidence: code
  - term: oper_cust_info.custEnterpriseId
    target: cust_role_info.platform_cust_id
    evidence: code
field_targets:
  - cust_role_info.platform_cust_id
  - cust_change_record.oper_cust_info
---

运营中台侧的企业 id（custEnterpriseId）在平台库内落在 cust_role_info.platform_cust_id，用于换取 token / 授权；客户变更记录把同一 id 存进 oper_cust_info JSON。

## 需求背景

两个来源并非随时可互换：企业处于变更流程时，token 所需的运营中台 id 取自变更记录（见 [[rules/change_status_token_source]]）；常态下取角色表字段。

## 版本演进

v0：首次成页。
---END FILE---

---FILE: concepts/product_code_bridge.md ---
---
type: concept
title: 产品/项目编码术语桥（product_code / platform_product_code / product_id / project_id）
page_key: concept.product_code_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - product_code
  - platform_product_code
  - product_id
  - project_id
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[platform_product.product_code / name]
  - semantic:field_semantics[tenant_product.platform_product_code / db_tenant_code]
  - semantic:field_semantics[tenant_project.tenant_id / platform_product_code / product_id / name]
  - semantic:field_semantics[cust_project_rel.project_id / product_id]
contract_version: "0.1"
maps_to:
  - term: product_code
    target: platform_product.product_code
    evidence: code
  - term: platform_product_code
    target: platform_product.product_code
    evidence: code
  - term: product_id
    target: tenant_project.product_id
    evidence: code
  - term: project_id
    target: tenant_project.project_id
    evidence: code
field_targets:
  - platform_product.product_code
  - tenant_product.platform_product_code
  - tenant_project.platform_product_code
  - tenant_project.product_id
  - cust_project_rel.project_id
  - cust_project_rel.product_id
  - cust_project_rel.ref_cust_project_rel_platform_product
also_confused_with:
  - tenant_project.name
---

产品编码（字典表 [[tables/platform_product]].product_code）在租户产品、租户项目、企业项目关联三处分别以 platform_product_code、ref_cust_project_rel_platform_product 等形式出现；项目与产品 id 在关系表中以字符串存储。

## 需求背景

编码与 id 并存：product_code 是业务编码，product_id / project_id 是实体 id，列表展示需要的产品名称来自平台产品表，三者不可互替。

## 版本演进

v0：首次成页。
---END FILE---

---FILE: concepts/identify_style_bridge.md ---
---
type: concept
title: 认证方式术语桥（identify_style 与 IdentifyTypeConstant）
page_key: concept.identify_style_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - identify_style
  - 认证方式
  - IdentifyTypeConstant
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.identify_style]
  - semantic:state_machines[企业建档/认证状态]
contract_version: "0.1"
maps_to:
  - term: identify_style
    target: cust_company_info.identify_style
    evidence: code
  - term: IdentifyTypeConstant.INVITE
    target: cust_company_info.identify_style
    evidence: code
  - term: IdentifyTypeConstant.SELF
    target: cust_company_info.identify_style
    evidence: code
  - term: IdentifyTypeConstant.INVITE_AGW
    target: cust_company_info.identify_style
    evidence: code
field_targets:
  - cust_company_info.identify_style
---

认证方式在库内为 identify_style（自主 / 邀请-客户录入 / 邀请-平台录入 / 简易），在提交逻辑中体现为 IdentifyTypeConstant 的 INVITE、SELF、INVITE_AGW 分支。

## 需求背景

认证方式决定提交后落到的建档状态（见 [[processes/cust_build_status_machine]]），也决定退回标记与来源补写的处理分支（[[rules/submit_cust_field_reset]]、[[calibers/cust_from_platform_invite]]）。

## 版本演进

v0：首次成页；「简易」对应的常量名在语义分析中未给出，不做推测。
---END FILE---

---FILE: concepts/user_type_bridge.md ---
---
type: concept
title: 联系人用户类型术语桥（admin / operator / guest）
page_key: concept.user_type_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - user_type
  - admin
  - operator
  - guest
  - 客户管理员
  - 经办人
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.user_type]
  - semantic:field_semantics[cust_person_info.operator_id / operator_realname / operator]
contract_version: "0.1"
maps_to:
  - term: admin
    target: cust_person_info.user_type
    evidence: code
  - term: operator
    target: cust_person_info.user_type
    evidence: code
  - term: guest
    target: cust_person_info.user_type
    evidence: code
field_targets:
  - cust_person_info.user_type
  - cust_person_info.operator_id
  - cust_person_info.operator_realname
  - cust_person_info.operator
also_confused_with:
  - cust_person_info.operator
---

联系人 user_type 三值：admin（客户管理员）、operator（经办人）、guest（游客）。注意它与运营人员字段 operator（运营登录名）同名不同义。

## 需求背景

「经办人」既可作为 user_type 的取值，也可指联系人在产品权限语境下的角色，其可用性由 enable 与冻结状态共同决定（[[processes/operator_freeze_machine]]）。运营人员信息（operator_id / operator_realname / operator）来自资产审核侧同步，不参与用户身份判定。

## 版本演进

v0：首次成页。
---END FILE---

---FILE: rules/company_query_enable_y.md ---
---
type: rule
title: 企业查询一律附加 enable='Y'
page_key: rule.company_query_enable_y
domain: 平台内部服务对接
status: draft
aliases:
  - 企业查询有效标志规则
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.enable]
contract_version: "0.1"
---

查询企业数据时必须附加 enable='Y' 条件，否则会取到逻辑删除或失效的企业行。

## 需求背景

该约束是企业表（[[tables/cust_company_info]]）的基础过滤条件，各服务读取企业信息时均应遵守；与之配套的主数据过滤见 [[rules/status_update_main_data_type]]。

## 版本演进

v0：首次成页。

```ground:rule
name: 企业查询一律附加 enable='Y'
field: cust_company_info.enable
condition: "查询一律 .eq(enable, 'Y')"
effect: "过滤掉非有效企业行"
evidence: code
```
---END FILE---

---FILE: rules/status_update_main_data_type.md ---
---
type: rule
title: 企业状态更新必须限定主数据（data_type）
page_key: rule.status_update_main_data_type
domain: 平台内部服务对接
status: draft
aliases:
  - 状态更新主数据条件
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.data_type]
  - semantic:state_machines[客户生命周期状态]
contract_version: "0.1"
---

对企业表做状态更新时，必须带 data_type = CustDataTypeConstant.DATA_TYPE_MAIN 条件。

## 需求背景

企业表在同一张物理表内混合了多种数据类型，缺少该条件会误更新非主数据行。冻结、解冻、注销、建档状态推进等路径（见 [[processes/cust_status_machine]]）都依赖此约束。

## 版本演进

v0：首次成页。

```ground:rule
name: 企业状态更新必须限定主数据
field: cust_company_info.data_type
condition: "data_type = CustDataTypeConstant.DATA_TYPE_MAIN"
effect: "所有状态更新均带此条件，避免误改非主数据行"
evidence: code
```
---END FILE---

---FILE: rules/cross_tenant_query_all.md ---
---
type: rule
title: 跨租户查询需显式设置 dbTenantCode="all"
page_key: rule.cross_tenant_query_all
domain: 平台内部服务对接
status: draft
aliases:
  - 跨租户查询
  - dbTenantCode all
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.db_tenant_code]
contract_version: "0.1"
---

Provider 层默认按当前租户隔离数据，需要跨租户读取时必须通过 MetaDataThreadLocalConfig.setDbTenantCode("all") 显式放宽。

## 需求背景

该开关作用于 [[tables/cust_company_info]] 等带 db_tenant_code 的表（见 [[concepts/db_tenant_code_bridge]]）。跨租户查询属于越权边界，仅在平台侧内部对接场景使用。

## 版本演进

v0：首次成页。

```ground:rule
name: 跨租户查询需显式设置 dbTenantCode="all"
field: cust_company_info.db_tenant_code
condition: "MetaDataThreadLocalConfig.setDbTenantCode(\"all\")"
effect: "Provider 层跨租户查询"
evidence: code
```
---END FILE---

---FILE: rules/operator_permission_disable.md ---
---
type: rule
title: 经办人无产品权限时 enable 置 'N'，解冻恢复 'Y'
page_key: rule.operator_permission_disable
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人权限置无效
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.enable]
  - semantic:state_machines[经办人产品关联冻结状态]
contract_version: "0.1"
---

当经办人失去产品权限时，联系人记录的 enable 被置为 'N'；解冻后恢复为 'Y'。

## 需求背景

这是联系人侧 enable 与产品授权冻结状态（[[processes/operator_freeze_machine]]、[[tables/sys_cust_user_rel]]）的联动点。因此在联系人有效性判定中，enable 与 status 需一并考虑（[[calibers/person_effective_status]]）。

## 版本演进

v0：首次成页。

```ground:rule
name: 经办人无产品权限时 enable 置 'N'，解冻恢复 'Y'
field: cust_person_info.enable
condition: "经办人无产品权限"
effect: "置 'N'；解冻时恢复 'Y'"
evidence: code
```
---END FILE---

---FILE: rules/submit_cust_field_reset.md ---
---
type: rule
title: 提交建档时的字段重置（check_status 置 null、audit_back_flag 置 'N'）
page_key: rule.submit_cust_field_reset
domain: 平台内部服务对接
status: draft
aliases:
  - 提交建档字段重置
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.check_status]
  - semantic:field_semantics[cust_company_info.audit_back_flag]
contract_version: "0.1"
---

提交建档时把 check_status 置为 null；非自主录入的提交路径把 audit_back_flag 置为 'N'。

## 需求背景

这两步是进入审核前的状态清理，配合建档状态机（[[processes/cust_build_status_machine]]）的提交分支生效。判定分支取决于认证方式（[[concepts/identify_style_bridge]]）。

## 版本演进

v0：首次成页。

```ground:rule
name: 提交建档时的字段重置
field: cust_company_info.check_status / cust_company_info.audit_back_flag
condition: "提交建档；非自主录入提交"
effect: "check_status 置 null；audit_back_flag 置 'N'"
evidence: code
```
---END FILE---

---FILE: rules/simple_auth_ca_forbidden.md ---
---
type: rule
title: 简易建档强制不开通电子签章，head_company 为空置 'Y'
page_key: rule.simple_auth_ca_forbidden
domain: 平台内部服务对接
status: draft
aliases:
  - 简易认证签章政策
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.need_register_ca]
  - semantic:field_semantics[cust_company_info.head_company]
contract_version: "0.1"
---

简易建档路径下，need_register_ca 政策上强制为不开通；head_company 为空时（简易认证）置为 'Y'。

## 需求背景

这条政策决定简易认证企业不会走 CA 开通流程，因而对外签章状态口径（[[calibers/ca_register_status_output]]）在这类企业上恒为未开通。简易认证的状态流转见 [[processes/cust_build_status_machine]]。

## 版本演进

v0：首次成页。

```ground:rule
name: 简易建档强制不开通电子签章，head_company 为空置 'Y'
field: cust_company_info.need_register_ca / cust_company_info.head_company
condition: "简易建档；head_company 为空（简易认证）"
effect: "need_register_ca 强制不开通；head_company 置 'Y'"
evidence: code
```
---END FILE---

---FILE: rules/cust_change_record_latest_effective.md ---
---
type: rule
title: 变更记录取 status=CUST_CHECK_PASS 的最新有效记录
page_key: rule.cust_change_record_latest_effective
domain: 平台内部服务对接
status: draft
aliases:
  - 变更记录取值规则
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_change_record.cust_id / status / oper_cust_info / oper_channel / create_time]
contract_version: "0.1"
---

读取客户变更记录时，以 status 为 CUST_CHECK_PASS 作为有效判据，并取最新的那条记录。

## 需求背景

该记录承载变更态下的运营中台企业 id（见 [[rules/change_status_token_source]]、[[concepts/platform_cust_id_bridge]]），取值错误会直接导致换 token 失败。

## 版本演进

v0：首次成页。

```ground:rule
name: 变更记录取 status=CUST_CHECK_PASS 的最新有效记录
field: cust_change_record.status
condition: "status = CUST_CHECK_PASS"
effect: "作为取值最新有效记录"
evidence: code
```
---END FILE---

---FILE: rules/change_status_token_source.md ---
---
type: rule
title: 变更态下运营中台企业 id 取自变更记录
page_key: rule.change_status_token_source
domain: 平台内部服务对接
status: draft
aliases:
  - 变更态token来源
oid: 1
scope:
  databases: []
sources:
  - semantic:state_machines[客户生命周期状态]
  - semantic:field_semantics[cust_change_record.cust_id / status / oper_cust_info / oper_channel / create_time]
contract_version: "0.1"
---

当企业进入变更态（cust_status=CHANGE）时，换取 token 使用的运营中台企业 id 取自客户变更记录，而非角色表常态字段。

## 需求背景

进入 CHANGE 的触发条件见 [[processes/cust_status_machine]]（queryCustAutoCheck 中 process!=CHECK 分支）；有效变更记录的取用规则见 [[rules/cust_change_record_latest_effective]]，术语映射见 [[concepts/platform_cust_id_bridge]]。

## 版本演进

v0：首次成页。

```ground:rule
name: 变更态下运营中台企业 id 取自变更记录
field: cust_company_info.cust_status
condition: "cust_status = CHANGE"
effect: "token 取变更记录上的运营中台 id"
evidence: code
```
---END FILE---

---FILE: rules/token_sign_md5.md ---
---
type: rule
title: 运营中台鉴权签名 md5(secret + sysChannel + loginName)
page_key: rule.token_sign_md5
domain: 平台内部服务对接
status: draft
aliases:
  - 鉴权签名规则
  - token 签名
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.platform_secret_key]
  - semantic:field_semantics[tenant_setting_config.sso_tenant_chanel]
contract_version: "0.1"
---

请求运营中台 token 时，签名由 platform_secret_key、sysChannel、loginName 三者拼接后做 md5 得到。

## 需求背景

三个入参分属不同来源：secret 与 sysChannel 来自租户配置（[[tables/tenant_setting_config]]，见 [[concepts/db_tenant_code_bridge]]），loginName 来自用户身份（[[tables/sys_user_sso_user]]）。任一取值不正确都会导致鉴权失败。

## 版本演进

v0：首次成页。

```ground:rule
name: 运营中台鉴权签名 md5(secret + sysChannel + loginName)
field: tenant_setting_config.platform_secret_key
condition: "请求运营中台 token"
effect: "md5(secret+sysChannel+loginName)"
evidence: code
```
---END FILE---

---FILE: rules/person_phone_encrypted_query.md ---
---
type: rule
title: 联系人手机号加密存储，查询需传密文
page_key: rule.person_phone_encrypted_query
domain: 平台内部服务对接
status: draft
aliases:
  - 手机号密文查询
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.phone]
contract_version: "0.1"
---

cust_person_info.phone 以密文落库（metaDataEncryptionService.encryptAndBase64Str），按手机号检索时必须传入加密后的密文，明文匹配不会命中。

## 需求背景

这是联系人查询（含按手机号定位经办人）的前置条件，属于内部服务对接中的敏感字段处理约定。

## 版本演进

v0：首次成页。

```ground:rule
name: 联系人手机号加密存储，查询需传密文
field: cust_person_info.phone
condition: "按手机号查询联系人"
effect: "查询需传密文（encryptAndBase64Str）"
evidence: code
```
---END FILE---

---FILE: rules/person_info_source_of_truth.md ---
---
type: rule
title: 经办人信息以 sys_user + sso_user 为准
page_key: rule.person_info_source_of_truth
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人信息基准
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info.name / user_name / email]
  - semantic:field_semantics[sys_user / sso_user]
contract_version: "0.1"
---

联系人姓名、登录名、业务邮箱的权威来源是 sys_user + sso_user；仅当联系人侧自身为空时才由经办人新增流程补全，业务邮箱变更时按条件回写登录邮箱。

## 需求背景

这条规则决定了 [[tables/cust_person_info]] 与 [[tables/sys_user_sso_user]] 的主从关系，避免两边都有值时互相覆盖。

## 版本演进

v0：首次成页。

```ground:rule
name: 经办人信息以 sys_user + sso_user 为准
field: cust_person_info.name / user_name / email
condition: "a) 仅本身为空时 b) 业务邮箱变更时"
effect: "由经办人新增流程补全 / 按条件回写登录邮箱，基准为用户中心与 SSO"
evidence: code
```
---END FILE---

---FILE: rules/role_status_follow_company.md ---
---
type: rule
title: 企业角色状态随企业状态联动更新
page_key: rule.role_status_follow_company
domain: 平台内部服务对接
status: draft
aliases:
  - 角色状态联动
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_role_info.status]
  - semantic:state_machines[客户生命周期状态]
contract_version: "0.1"
---

cust_role_info.status 不独立演进，通过 updateStatusByCustCompany 随企业状态同步更新。

## 需求背景

企业在冻结、解冻、注销时（[[processes/cust_status_machine]]），其在 [[tables/cust_role_info]] 中的角色记录必须同步，否则授权与 token 换取会与企业实际状态不一致。

## 版本演进

v0：首次成页。

```ground:rule
name: 企业角色状态随企业状态联动更新
field: cust_role_info.status
condition: "企业状态变更"
effect: "updateStatusByCustCompany 同步角色状态"
evidence: code
```
---END FILE---

---FILE: rules/oper_auth_agreement_fallback.md ---
---
type: rule
title: 子账号授权书模板未配置时回落 Nacos 值
page_key: rule.oper_auth_agreement_fallback
domain: 平台内部服务对接
status: draft
aliases:
  - 授权书模板回落
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.oper_auth_agreement]
contract_version: "0.1"
---

租户未配置 oper_auth_agreement 时，使用 Nacos 中的 operAuthAgreement 值作为授权书模板 id。

## 需求背景

这是租户配置（[[tables/tenant_setting_config]]）与配置中心之间的兜底约定，属于内部服务对接中「配置缺失不应阻断流程」的处理方式。

## 版本演进

v0：首次成页。

```ground:rule
name: 子账号授权书模板未配置时回落 Nacos 值
field: tenant_setting_config.oper_auth_agreement
condition: "未配置时"
effect: "回落 Nacos 值 operAuthAgreement"
evidence: code
```
---END FILE---

---FILE: rules/certification_no_cross_system_align.md ---
---
type: rule
title: 统一社会信用代码跨系统一致性对齐
page_key: rule.certification_no_cross_system_align
domain: 平台内部服务对接
status: draft
aliases:
  - 统一社会信用代码对齐
  - certification_no 对齐
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.certification_no]
contract_version: "0.1"
---

certification_no（统一社会信用代码）被定义为跨系统一致性对齐字段：企业主数据与运营中台等外部系统之间以此字段对齐同一法人主体。

## 需求背景

在企业建档与认证流转（[[processes/cust_build_status_machine]]）中，该字段是识别同一主体的业务键，与内部主键 id、业务编码 code 的用途不同（见 [[concepts/company_id_bridge]]、[[concepts/company_code_bridge]]）。

## 版本演进

v0：首次成页。

```ground:rule
name: 统一社会信用代码跨系统一致性对齐
field: cust_company_info.certification_no
condition: "跨系统企业主体比对"
effect: "作为一致性对齐字段"
evidence: code
```
---END FILE---

---REVIEW: frontmatter | 全部页面 scope.databases 待补---
语义分析未给出任何物理库名（field_semantics 的 evidence 仅标注 db / code，state_machines 仅给出 code_path 与类名）。因此所有页面的 scope.databases 暂为空数组，待补充物理库名后再回填。不属于可推断项，未做猜测。
---END REVIEW---

---REVIEW: process | 经办人产品关联冻结状态（证据截断）---
语义分析的第三台状态机在 transitions 末尾被截断，最后一条可见片段为「from N / event 冻结企业」，其后 to 值与 evidence 缺失。本页仅收录两条完整转换（FREEZE / THAW）。若「冻结企业」应触发关联冻结，需要补充完整证据后再追加转换。
---END REVIEW---

---REVIEW: caliber | 有效标志口径的证据范围---
calibers/enable_valid_flag 将 enable 的 'Y' 判定收敛为统一口径，但语义分析中「查询一律 .eq(enable, 'Y')」的原句只出现在 cust_company_info.enable 条目下；其余表（cust_person_info、cust_project_rel、tenant_setting_config）的 enable 语义为「有效标志 'Y'/'N'」。若下游需要严格区分「强制过滤条件」与「字段取值域」，应把本页拆分为企业侧强制口径与通用标志域两页。
---END REVIEW---