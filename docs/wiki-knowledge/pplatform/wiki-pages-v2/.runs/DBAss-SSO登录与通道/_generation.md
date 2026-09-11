---FILE: tables/open_sso_channel.md ---
---
type: table
title: open_sso_channel（SSO 渠道配置表）
page_key: table:open_sso_channel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - open_sso_channel
  - SSO渠道表
  - 开放SSO渠道表
oid: 1
scope:
  databases: []
sources:
  - "db:open_sso_channel"
contract_version: "0.1"
---

# open_sso_channel（SSO 渠道配置表）

业务定位：SSO 登录渠道的配置主表，一条记录对应一个登录渠道。渠道上同时挂着 SSO 侧凭据（sso_client_id / sso_client_secret）、开放平台 appId、业务渠道码、默认打开形态，以及同步到 SSO 的机构编码与同步状态。渠道标识的判读口径见 [[concepts/sso-channel-identifier]]，同步状态流转见 [[processes/sso-channel-sync-status]]。

## 需求背景

DBAss/SSO 登录链路上需要同时满足两类渠道语义：SSO 系统渠道（sys_channel）用于登录、发邀请码、同步用户时选择 sysChannel；业务/OpenAPI 渠道码（channel_code）用于开放平台接入。两者不可互相替代——实测 channel_code 为 longteng，而 sys_channel 形如 scpr-pplatform-pc。渠道能否被选用由 [[calibers/valid-sso-channel]] 与 [[calibers/channel-sync-success]] 共同约束；org_code 会在查询用户 SSO 数据时作为 RpcContext orgCode 透传。

## 版本演进

v0 仅沉淀当前线上实测结构与字段语义，语义分析中未见该表的版本演进证据。

```ground:table
table: open_sso_channel
columns:
  - name: sys_channel
    meaning: "SSO 系统渠道标识，一条记录对应一个登录渠道（如 scpr-pplatform-pc、scpr-pplatform-pc_org...）"
    evidence: db
  - name: sys_type
    meaning: "SSO 系统类型标识，值与部分 sys_channel（含 org 后缀）一致，用作 SSO 侧系统分类"
    evidence: db
  - name: sso_client_id
    meaning: "每渠道独立的 SSO clientId"
    evidence: db
  - name: sso_client_secret
    meaning: "SSO 密钥（渠道维度）"
    evidence: db
  - name: channel_code
    meaning: "业务/OpenAPI 渠道码（实测值 longteng，非 SSO sysChannel）"
    evidence: db
  - name: channel_kind
    meaning: "渠道类型（实测 LOCAL_SYS）"
    evidence: db
  - name: app_id
    meaning: "开放平台 appId"
    evidence: db
  - name: open_mode_default
    meaning: "默认打开形态 EMBED/TOP（实测 EMBED）"
    evidence: db
  - name: org_code
    meaning: "同步到 SSO 的机构编码；查询用户 SSO 数据时作为 RpcContext orgCode 透传"
    evidence: code
  - name: sso_sync_status
    meaning: "SSO 同步状态（实测 SYNCED）"
    evidence: db
  - name: sso_sync_msg
    meaning: "SSO 同步描述/失败原因"
    evidence: db
  - name: enable
    meaning: "启用标记 Y/N"
    evidence: db
```
---END FILE---

---FILE: tables/operation_user.md ---
---
type: table
title: operation_user（运营中台人员表）
page_key: table:operation_user
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - operation_user
  - 运营中台人员表
  - 运营人员表
oid: 1
scope:
  databases: []
sources:
  - "db:operation_user"
contract_version: "0.1"
---

# operation_user（运营中台人员表）

业务定位：记录运营中台人员，operation_id 是外部系统主键，用于把 SSO/DBAss 侧的用户与运营中台账号对齐。人员在运营组内以 operation_group 归组，可在 SSO 与 DBAss 之间按需冻结/解冻（见 [[rules/freeze-unfreeze-user]]）。

## 需求背景

运营人员既出现在登录链路，也出现在冻结/解冻入口 `PlatFormUserApplication#freezeOrThawOperatorUser`。查询运营人员时必须叠加删除与启用两个条件，口径见 [[calibers/active-operation-user]]；status 承载运营中台侧的状态语义，与本地 [[tables/sys_user]] 的 user_status 不是同一维度。

## 版本演进

v0 仅记录当前实测字段语义，未见版本演进证据。

```ground:table
table: operation_user
columns:
  - name: operation_id
    meaning: "运营中台人员 id（外部系统主键）"
    evidence: db
  - name: operation_name
    meaning: "运营人员姓名"
    evidence: db
  - name: operation_group
    meaning: "运营组别"
    evidence: db
  - name: status
    meaning: "运营中台用户状态标识"
    evidence: db
  - name: deleted
    meaning: "逻辑删除标识 N/Y（N=未删除）"
    evidence: db
  - name: enable
    meaning: "启用标记 Y/N"
    evidence: db
```
---END FILE---

---FILE: tables/tenant_setting_config.md ---
---
type: table
title: tenant_setting_config（租户设置配置表）
page_key: table:tenant_setting_config
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - tenant_setting_config
  - 租户设置配置表
  - TenantSettingConfigDO
oid: 1
scope:
  databases: []
sources:
  - "code:SaaSAuthController.java#getTenantSetting"
  - "code:TenantSettingConfigDO"
contract_version: "0.1"
---

# tenant_setting_config（租户设置配置表）

业务定位：租户级配置的聚合表，登录与通道相关的关键字段都落在这里：租户绑定的 SSO 渠道、SSO 系统渠道，以及 DBAss 的应用标识与私钥。字段名拼写（ssoTenantChanel 少一个 n）是历史遗留，判读时须与 [[tables/open_sso_channel]] 的 sys_channel 区分，详见 [[concepts/sso-channel-identifier]]。

## 需求背景

登录、发邀请码、同步用户时使用 ssoTenantChanel 作为 sysChannel；注销、登录验证码开关、渠道判优时使用 ssoSysChannel。对外返回租户配置时，dbassAppId 与 dbassPrivateKey 会被置空，属于敏感字段脱敏要求。查询租户配置时会带启用条件（见 [[calibers/valid-tenant-setting]]），AGW 客户端还有兜底取值逻辑（见 [[calibers/agw-client]]）。

## 版本演进

v0 仅记录当前字段语义与代码引用点，未见版本演进证据。

```ground:table
table: tenant_setting_config
columns:
  - name: ssoTenantChanel
    meaning: "租户级 SSO 渠道（拼写为 chanel）；登录、发邀请码、同步用户时作为 sysChannel 使用"
    evidence: code
  - name: ssoSysChannel
    meaning: "租户绑定的 SSO 系统渠道；注销、登录验证码开关、渠道判优时使用"
    evidence: code
  - name: dbassAppId
    meaning: "DBAss 应用标识；对外返回租户配置时被置空（敏感）"
    evidence: code
  - name: dbassPrivateKey
    meaning: "DBAss 私钥；对外返回租户配置时被置空（敏感）"
    evidence: code
```
---END FILE---

---FILE: tables/sys_cust_user_rel.md ---
---
type: table
title: sys_cust_user_rel（企业-用户关系表）
page_key: table:sys_cust_user_rel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sys_cust_user_rel
  - 企业用户关系表
  - 用户企业关系表
oid: 1
scope:
  databases: []
sources:
  - "code:UserFacade.java#querySysCustUserList"
contract_version: "0.1"
---

# sys_cust_user_rel（企业-用户关系表）

业务定位：表达「某个用户在某家企业（某产品）下」的关联关系与冻结状态。它是登录可用性判定与用户级联删除判定的关键表：is_freeze 只作用于这条关系，而不是全局账号。冻结标记的状态流转见 [[processes/user-freeze-state]]，查询口径见 [[calibers/not-frozen-cust-user-rel]] 与 [[calibers/pre-delete-user-check]]。

## 需求背景

产品需要支持「只冻结某产品下的关联、不冻结登录」的运营诉求，因此冻结语义被下沉到关系维度，与 [[tables/sys_user]] 的 user_status 形成两个层级；对外展示状态由两者合成（见 [[concepts/user-freeze-flag]]）。关系上还会挂 role_id，新用户默认角色绑定规则见 [[rules/default-cust-user-role-binding]]。

## 版本演进

v0 仅记录 is_freeze 的取值与流转证据，未见版本演进证据。

```ground:table
table: sys_cust_user_rel
columns:
  - name: is_freeze
    meaning: "企业-用户关系维度的冻结标记，N=激活、Y=冻结（注释：冻结标记,N表示激活,Y表示冻结）"
    evidence: code
```
---END FILE---

---FILE: tables/sys_user.md ---
---
type: table
title: sys_user（全局用户表）
page_key: table:sys_user
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sys_user
  - 全局用户表
  - 用户主表
oid: 1
scope:
  databases: []
sources:
  - "code:UserFacade.java#getUserStatusEnum"
  - "code:SaaSAuthController.java#init"
contract_version: "0.1"
---

# sys_user（全局用户表）

业务定位：全局用户主表，承载账号级状态（user_status）、与 SSO 用户的关联（sso_user_id）以及数据租户归属（tenant_code）。它是登录初始化流程的收口对象：SSO 登录成功后会被置为 NORMAL（见 [[rules/login-init-flow]]、[[processes/sys-user-status]]）。

## 需求背景

账号级状态与关系级冻结必须分开看：[[tables/sys_cust_user_rel]] 的 is_freeze 只冻结某产品下的关系，user_status 才是全局状态，二者合成对外展示值（N+FREEZE→INIT，Y→FREEZE）。取 SSO 用户、企业联系人时需按 tenant_code 做数据租户过滤，租户语义见 [[concepts/tenant-identifier]]。

## 版本演进

v0 仅记录当前字段语义与状态枚举，未见版本演进证据。

```ground:table
table: sys_user
columns:
  - name: user_status
    meaning: "全局用户状态（NORMAL/INIT/FREEZE），由 UserStatusEnum 承载"
    evidence: code
  - name: sso_user_id
    meaning: "sys_user 关联的 SSO 用户 id，用于查登录历史、同步邮箱"
    evidence: code
  - name: tenant_code
    meaning: "sys_user 所属数据租户；跨租户取 sso_user/企业联系人时用 dbTenantCode 过滤"
    evidence: code
```
---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info（企业联系人表）
page_key: table:cust_person_info
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - cust_person_info
  - 企业联系人表
  - 经办人表
oid: 1
scope:
  databases: []
sources:
  - "code:UserFacade.java#handUserList"
  - "code:SaaSAuthController.java#makePersonEffect"
contract_version: "0.1"
---

# cust_person_info（企业联系人表）

业务定位：企业在平台侧的联系人（经办人/管理员/游客）档案，记录用户在具体企业下的类型、有效性与生效状态。登录与切换公司都会触发「联系人转生效」（见 [[processes/cust-person-status]]），冻结用户时也可能把 enable 置 N。

## 需求背景

经办人列表、管理员查询统一以 enable = Y 为条件（见 [[calibers/valid-cust-person]]）。user_type 决定展示优先级：admin > operator > guest，同一用户命中多条时取优先级最高的一条。operator_push_system 用于把该经办人同步到其他系统渠道，多值以逗号分隔。

## 版本演进

v0 记录当前实测语义；status 在代码中仅见 ADD→EFFECT 一档流转，未见其他取值证据。

```ground:table
table: cust_person_info
columns:
  - name: status
    meaning: "企业联系人（经办人）状态，实测代码中仅见 ADD→EFFECT"
    evidence: code
  - name: user_type
    meaning: "用户在企业的类型：admin/operator/guest，按 admin>operator>guest 取优先级最高一条展示"
    evidence: code
  - name: enable
    meaning: "是否有效 Y/N，查询经办人/管理员时以 Y 为条件"
    evidence: code
  - name: operator_push_system
    meaning: "该经办人需要推送的系统渠道（逗号分隔），用于向其他系统同步经办人"
    evidence: code
```
---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（客户企业信息表）
page_key: table:cust_company_info
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - cust_company_info
  - 客户企业信息表
  - 企业信息表
oid: 1
scope:
  databases: []
sources:
  - "code:CustCompanyInfoApplication.java#getCustBuildStatus"
  - "code:CustSysOrgApplication.java#listBuildSuccessCusts"
contract_version: "0.1"
---

# cust_company_info（客户企业信息表）

业务定位：企业（客户）主档，承载建档/认证状态、认证方式、是否开通电子签章以及企业角色等属性，是登录后「能否初始化组织、能否赋管理员」的判据来源。状态机见 [[processes/cust-build-status]]，相关口径见 [[calibers/main-data-company]] 与 [[calibers/build-success-company]]。

## 需求背景

认证方式 identify_style 决定状态流转路径与消息模板：INVITE / INVITE_AGW / SELF / SIMPLE；不同方式提交后落到不同的 cust_build_status。needRegisterCa 在简单认证下会被强制校正为不开通，避免走电子签章流程。企业角色字段是企业级多值语义，见 [[concepts/company-type]]。

## 版本演进

v0 记录当前字段语义与状态机证据，未见版本演进证据。

```ground:table
table: cust_company_info
columns:
  - name: cust_build_status
    meaning: "企业建档/认证状态（CustBuildStatusEnum），决定是否可初始化组织、赋管理员"
    evidence: code
  - name: identify_style
    meaning: "认证方式：INVITE/INVITE_AGW/SELF/SIMPLE，决定状态流转与消息模板"
    evidence: code
  - name: needRegisterCa
    meaning: "是否需要开通电子签章 Y/N；简单认证下强制校正为不开通"
    evidence: code
```
---END FILE---

---FILE: tables/sso_user.md ---
---
type: table
title: sso_user（SSO 用户表）
page_key: table:sso_user
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sso_user
  - SSO用户表
oid: 1
scope:
  databases: []
sources:
  - "code:SsoFacade"
contract_version: "0.1"
---

# sso_user（SSO 用户表）

业务定位：SSO 侧用户档案。login_name 实际存放手机号，唯一性由 loginName + sysChannel 共同约束，因此同一手机号在不同 SSO 渠道下是不同账号。它与 [[tables/sys_user]] 通过 sso_user_id 关联，跨数据租户读取时需按 dbTenantCode 过滤（见 [[concepts/tenant-identifier]]）。

## 需求背景

注册路径（SsoFacade.addUser / UserInfoFacade）会把用户落到 SSO 并同时建立本地关系，默认绑定游客角色（见 [[rules/default-cust-user-role-binding]]）。登录成功后由 [[rules/login-init-flow]] 回写本地用户状态。

## 版本演进

v0 仅记录 login_name 的语义与唯一性约束，未见版本演进证据。

```ground:table
table: sso_user
columns:
  - name: login_name
    meaning: "SSO 登录名，实际存放手机号；按 loginName+sysChannel 唯一"
    evidence: code
```
---END FILE---

---FILE: tables/sso_system.md ---
---
type: table
title: sso_system（SSO 系统表）
page_key: table:sso_system
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sso_system
  - SSO系统表
  - SsoSystemDO
oid: 1
scope:
  databases: []
sources:
  - "code:SsoSystemDO"
contract_version: "0.1"
---

# sso_system（SSO 系统表）

业务定位：SSO 侧系统（渠道）注册表。sysChannel 是这里的核心标识，被用于查询验证码开关与 orgCode，并作为登录链路 sysChannel 的正源。它与 [[tables/open_sso_channel]] 的 sys_channel、[[tables/tenant_setting_config]] 的 ssoSysChannel / ssoTenantChanel 同名异层，判读见 [[concepts/sso-channel-identifier]]。

## 需求背景

租户登录、注销、验证码开关、渠道判优都依赖 sysChannel 取值；对 AGW 客户端，租户配置中的渠道值会兜底为 scpr-pplatform-agw（见 [[calibers/agw-client]]）。

## 版本演进

v0 仅记录 sysChannel 的用途，未见版本演进证据。

```ground:table
table: sso_system
columns:
  - name: sysChannel
    meaning: "SSO 系统渠道，用于查 captcha 开关与 orgCode"
    evidence: code
```
---END FILE---

---FILE: processes/user-freeze-state.md ---
---
type: process
title: 用户冻结状态（sys_cust_user_rel.is_freeze）
page_key: process:user-freeze-state
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 用户冻结状态机
  - is_freeze 状态机
  - 关系冻结
oid: 1
scope:
  databases: []
sources:
  - "code:LocalTypeUserController.java#freeze"
  - "code:LocalTypeUserController.java#active"
  - "code:UserFacade.java#updateListFreezeFlag"
  - "code:PlatFormUserApplication.java#freezeOrThawOperatorUser"
contract_version: "0.1"
---

# 用户冻结状态（sys_cust_user_rel.is_freeze）

业务定位：以企业-用户关系为主体的冻结状态机。冻结/解冻是「SSO 侧先动、本地关系后动」的两段式操作，影响用户能否登录以及在某产品下的可用性（见 [[rules/freeze-unfreeze-user]]）。

## 需求背景

平台需要支持只冻结某产品下关联而不冻结登录的能力，因此冻结落在关系维度；同时存在幂等重置逻辑：`addDefaultCustUserRel` 只要发现 isFreeze 不为 "N" 就重置为 "N"，保证新增/补关系不会把历史冻结带进来。与账号级状态的关系见 [[concepts/user-freeze-flag]] 与 [[processes/sys-user-status]]；关系级查询口径见 [[calibers/not-frozen-cust-user-rel]]。

## 版本演进

v0 记录 freeze/active 与 freezeOrThawOperatorUser 两条入口的流转证据，未见版本演进证据。

```ground:process
name: 用户冻结状态
field: sys_cust_user_rel.is_freeze
states:
  - value: "N"
    label: 激活/未冻结
    source: code_enum
  - value: "Y"
    label: 冻结
    source: code_enum
transitions:
  - from: "N"
    event: freeze
    to: "Y"
    evidence: "code_path:LocalTypeUserController.java#freeze + UserFacade.java#updateListFreezeFlag(UserFreezeEnum.FREEZE)"
  - from: "Y"
    event: active
    to: "N"
    evidence: "code_path:LocalTypeUserController.java#active + UserFacade.java#updateListFreezeFlag(UserFreezeEnum.UN_FROZEN)"
  - from: "Y/N"
    event: addDefaultCustUserRel 幂等重置
    to: "N"
    evidence: "code_path:UserFacade.java#addDefaultCustUserRel(if !\"N\".equals(isFreeze) 则 setIsFreeze(\"N\"))"
  - from: "N"
    event: freezeOrThawOperatorUser(FREEZE)
    to: "Y"
    evidence: "code_path:PlatFormUserApplication.java#freezeOrThawOperatorUser(setIsFreeze(\"Y\"))"
  - from: "Y"
    event: freezeOrThawOperatorUser(THAW)
    to: "N"
    evidence: "code_path:PlatFormUserApplication.java#freezeOrThawOperatorUser(setIsFreeze(\"N\"))"
```
---END FILE---

---FILE: processes/sys-user-status.md ---
---
type: process
title: 全局用户状态（sys_user.user_status）
page_key: process:sys-user-status
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 全局用户状态机
  - UserStatusEnum
  - user_status 状态机
oid: 1
scope:
  databases: []
sources:
  - "code:SaaSAuthController.java#init"
  - "code:UserFacade.java#getUserStatusEnum"
contract_version: "0.1"
---

# 全局用户状态（sys_user.user_status）

业务定位：账号级状态机，由 UserStatusEnum 承载（NORMAL / INIT / FREEZE）。SSO 登录成功会把 INIT 推进到 NORMAL；对外展示状态则由关系冻结与账号状态合成，见 [[concepts/user-freeze-flag]]。

## 需求背景

`UserFacade#getUserStatusEnum` 承担合成职责：isFreeze 为 Y 时对外返回 FREEZE，isFreeze 为空或标记异常时回落 INIT。因此 user_status 的落库值与对外展示值可能不一致，排查登录问题时要同时看 [[tables/sys_user]] 与 [[tables/sys_cust_user_rel]]。初始化入口见 [[rules/login-init-flow]]。

## 版本演进

v0 记录 init、冻结与异常回落三类流转证据，未见版本演进证据。

```ground:process
name: 全局用户状态
field: sys_user.user_status
states:
  - value: "NORMAL"
    label: 正常
    source: code_enum
  - value: "INIT"
    label: 初始/未知
    source: code_enum
  - value: "FREEZE"
    label: 冻结
    source: code_enum
transitions:
  - from: "INIT"
    event: SSO 登录成功初始化
    to: "NORMAL"
    evidence: "code_path:SaaSAuthController.java#init(ssoFacade.updateSysUserStatus(userId, UserStatusEnum.NORMAL))"
  - from: "NORMAL"
    event: 冻结用户
    to: "FREEZE"
    evidence: "code_path:UserFacade.java#getUserStatusEnum(isFreeze=Y → FREEZE)"
  - from: "任何"
    event: isFreeze 为空/异常标记
    to: "INIT"
    evidence: "code_path:UserFacade.java#getUserStatusEnum(默认返回 INIT)"
```
---END FILE---

---FILE: processes/cust-person-status.md ---
---
type: process
title: 企业联系人状态（cust_person_info.status）
page_key: process:cust-person-status
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 企业联系人状态机
  - 经办人生效状态
  - makePersonEffect
oid: 1
scope:
  databases: []
sources:
  - "code:SaaSAuthController.java#makePersonEffect"
  - "code:SaaSAuthController.java#changeCompany"
contract_version: "0.1"
---

# 企业联系人状态（cust_person_info.status）

业务定位：企业联系人在企业下的生效状态机，当前实测只有 ADD（新增待生效）与 EFFECT（生效）两档。联系人被加入后处于 ADD，直到用户登录或切换公司才转 EFFECT。

## 需求背景

历史数据中联系人可能先落库、后由用户首次登录激活，因此查询经办人/管理员时既要看生效状态，也要叠加 [[calibers/valid-cust-person]] 的 enable 条件。切换公司的上下文机制见 [[concepts/company-switch]]；被冻结用户时 enable 也可能被置 N（见 [[rules/freeze-unfreeze-user]]）。

## 版本演进

v0 仅见 ADD→EFFECT 证据，未观察到回退或失效状态，需后续补充。

```ground:process
name: 企业联系人状态
field: cust_person_info.status
states:
  - value: "ADD"
    label: 新增待生效
    source: code_enum
  - value: "EFFECT"
    label: 生效
    source: code_enum
transitions:
  - from: "ADD"
    event: 登录后联系人转生效
    to: "EFFECT"
    evidence: "code_path:SaaSAuthController.java#makePersonEffect(if \"ADD\".equals(one.getStatus()) setStatus(\"EFFECT\"))"
  - from: "ADD"
    event: 切换公司后转生效
    to: "EFFECT"
    evidence: "code_path:SaaSAuthController.java#changeCompany(调用 makePersonEffect)"
```
---END FILE---

---FILE: processes/cust-build-status.md ---
---
type: process
title: 企业认证/建档状态（cust_company_info.cust_build_status）
page_key: process:cust-build-status
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 企业建档状态机
  - CustBuildStatusEnum
  - 认证状态流转
oid: 1
scope:
  databases: []
sources:
  - "code:CustCompanyInfoApplication.java#getCustBuildStatus"
  - "code:CustCompanyInfoApplication.java#updateCustBuildStatus"
  - "code:CustCompanyInfoApplication.java#submitForSimpleAuth"
contract_version: "0.1"
---

# 企业认证/建档状态（cust_company_info.cust_build_status）

业务定位：企业主档的认证/建档生命周期，决定是否可初始化组织、是否可赋管理员。提交时的目标状态由认证方式 identify_style 决定，审核通过/退回由运营中台驱动。

## 需求背景

同一套状态机服务多条认证路径：INVITE_AGW 直接进 CUST_BUILDING，INVITE/SELF 先到 CUST_CONFIRM_AWAIT 等客户确认，SIMPLE 则落到 AWAIT_CUST_CONFIRM。状态条件更新时会叠加主数据与启用条件，见 [[calibers/main-data-company]]；组织初始化的入口条件是建档成功，见 [[calibers/build-success-company]]。字段语义见 [[tables/cust_company_info]]。

## 版本演进

v0 记录六态与七条流转证据；AWAIT_CUST_CONFIRM 与其他状态的后续收敛路径未在本次分析中出现。

```ground:process
name: 企业认证/建档状态
field: cust_company_info.cust_build_status
states:
  - value: "INIT"
    label: 初始
    source: code_enum
  - value: "CUST_CONFIRM_AWAIT"
    label: 待客户确认
    source: code_enum
  - value: "CUST_BUILDING"
    label: 审核中
    source: code_enum
  - value: "BUILD_SUCCESS"
    label: 建档成功
    source: code_enum
  - value: "BUILD_FAIL"
    label: 建档失败/拒绝
    source: code_enum
  - value: "AWAIT_CUST_CONFIRM"
    label: 待客户确认(简易)
    source: code_enum
transitions:
  - from: "任何"
    event: INVITE_AGW 提交
    to: "CUST_BUILDING"
    evidence: "code_path:CustCompanyInfoApplication.java#getCustBuildStatus(INVITE_AGW → CUST_BUILDING)"
  - from: "任何"
    event: INVITE/SELF 提交
    to: "CUST_CONFIRM_AWAIT"
    evidence: "code_path:CustCompanyInfoApplication.java#getCustBuildStatus(INVITE/SELF → CUST_CONFIRM_AWAIT)"
  - from: "CUST_CONFIRM_AWAIT"
    event: 客户确认提交
    to: "CUST_BUILDING"
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(before=CUST_CONFIRM_AWAIT && after=CUST_BUILDING)"
  - from: "CUST_BUILDING"
    event: 运营中台审核退回
    to: "CUST_CONFIRM_AWAIT"
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(before=CUST_BUILDING && after=CUST_CONFIRM_AWAIT)"
  - from: "CUST_BUILDING"
    event: 审核通过
    to: "BUILD_SUCCESS"
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(after=BUILD_SUCCESS)"
  - from: "CUST_BUILDING"
    event: 审核拒绝
    to: "BUILD_FAIL"
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(after=BUILD_FAIL)"
  - from: "INIT"
    event: 简易认证提交
    to: "AWAIT_CUST_CONFIRM"
    evidence: "code_path:CustCompanyInfoApplication.java#submitForSimpleAuth(setCustBuildStatus(AWAIT_CUST_CONFIRM))"
```
---END FILE---

---FILE: processes/sso-channel-sync-status.md ---
---
type: process
title: SSO 渠道同步状态（open_sso_channel.sso_sync_status）
page_key: process:sso-channel-sync-status
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 渠道同步状态机
  - sso_sync_status
  - 渠道同步
oid: 1
scope:
  databases: []
sources:
  - "db:open_sso_channel.sso_sync_status"
contract_version: "0.1"
---

# SSO 渠道同步状态（open_sso_channel.sso_sync_status）

业务定位：描述一条 SSO 渠道配置是否已经同步到 SSO 侧。当前仅有实测分布证据（SYNCED），未在代码中找到驱动该状态的服务实现，因此本页是「观测到的状态」而非完整状态机。

## 需求背景

渠道同步结果直接决定渠道能否被登录链路选用，查询口径见 [[calibers/channel-sync-success]]；失败原因落在 sso_sync_msg（见 [[tables/open_sso_channel]]）。渠道标识的判读见 [[concepts/sso-channel-identifier]]。

## 版本演进

v0 仅记录 SYNCED 一态；同步中/同步失败等状态与驱动服务在本次语义分析中无证据，待补充。

```ground:process
name: SSO 渠道同步状态
field: open_sso_channel.sso_sync_status
states:
  - value: "SYNCED"
    label: 已同步
    source: db_dist
transitions:
  - from: "unknown"
    event: 渠道同步 SSO 完成
    to: "SYNCED"
    evidence: "code_path:open_sso_channel 表实测分布（无对应 service 代码可见）"
```
---END FILE---

---FILE: calibers/valid-sso-channel.md ---
---
type: caliber
title: 有效 SSO 渠道
page_key: caliber:valid-sso-channel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 有效SSO渠道口径
  - enable=Y 渠道
oid: 1
scope:
  databases: []
sources:
  - "db:open_sso_channel.enable(Y/N)"
contract_version: "0.1"
---

# 有效 SSO 渠道

业务定位：判断一条 SSO 渠道配置是否处于启用状态。enable 为 Y 的渠道才会参与登录链路的候选。字段语义见 [[tables/open_sso_channel]]。

## 需求背景

渠道启停是运营侧控制登录入口的手段；启用状态与同步状态是两个独立维度，同步成功但被停用的渠道仍不可用，需同时看 [[calibers/channel-sync-success]]。

## 版本演进

v0 定义当前口径，未见演进证据。

```ground:caliber
name: 有效 SSO 渠道
predicate: "open_sso_channel.enable = 'Y'"
scope: "SSO 渠道启停"
evidence: "db:open_sso_channel.enable(Y/N)"
```
---END FILE---

---FILE: calibers/channel-sync-success.md ---
---
type: caliber
title: 渠道同步成功
page_key: caliber:channel-sync-success
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 渠道同步成功口径
  - SYNCED 渠道
oid: 1
scope:
  databases: []
sources:
  - "db:open_sso_channel.sso_sync_status(SYNCED)"
contract_version: "0.1"
---

# 渠道同步成功

业务定位：以 sso_sync_status = SYNCED 判定渠道是否已同步到 SSO。用于渠道可用性判定的同步维度。

## 需求背景

同步失败的描述落在 sso_sync_msg，排查时应结合 [[tables/open_sso_channel]] 的该字段；该状态的驱动服务在语义分析中无代码证据，状态机见 [[processes/sso-channel-sync-status]]。与启用口径 [[calibers/valid-sso-channel]] 需并用。

## 版本演进

v0 依据实测分布定义，未见演进证据。

```ground:caliber
name: 渠道同步成功
predicate: "open_sso_channel.sso_sync_status = 'SYNCED'"
scope: "渠道同步状态判定"
evidence: "db:open_sso_channel.sso_sync_status(SYNCED)"
```
---END FILE---

---FILE: calibers/active-operation-user.md ---
---
type: caliber
title: 未删除运营人员
page_key: caliber:active-operation-user
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 有效运营人员口径
  - 未删除运营人员
oid: 1
scope:
  databases: []
sources:
  - "db:operation_user.deleted(N/Y)"
  - "db:operation_user.enable(N/Y)"
contract_version: "0.1"
---

# 未删除运营人员

业务定位：运营中台人员查询的有效集合口径：未逻辑删除且处于启用状态。

## 需求背景

运营人员会参与冻结/解冻等操作入口（见 [[rules/freeze-unfreeze-user]]），查询时必须同时叠加 deleted 与 enable 两个条件，避免已删除或已停用人员被再次操作。字段语义见 [[tables/operation_user]]。

## 版本演进

v0 定义当前口径，未见演进证据。

```ground:caliber
name: 未删除运营人员
predicate: "operation_user.deleted = 'N' AND operation_user.enable = 'Y'"
scope: "运营中台人员查询"
evidence: "db:operation_user.deleted(N/Y),enable(N/Y)"
```
---END FILE---

---FILE: calibers/valid-tenant-setting.md ---
---
type: caliber
title: 有效租户配置
page_key: caliber:valid-tenant-setting
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 有效租户配置口径
  - TenantSettingConfigDO.enable
oid: 1
scope:
  databases: []
sources:
  - "code:SaaSAuthController.java#getTenantSetting"
contract_version: "0.1"
---

# 有效租户配置

业务定位：登录、注销、租户配置查询时取租户配置的有效性条件，代码中以 TenantSettingConfigDO.enable = BooleanEnum.Y 表达。

## 需求背景

租户配置承载 SSO 渠道、DBAss 应用标识等关键字段（见 [[tables/tenant_setting_config]]）；只有启用的配置才可用于登录与注销链路。AGW 客户端另有兜底逻辑，见 [[calibers/agw-client]]。

## 版本演进

v0 定义当前口径，未见演进证据。

```ground:caliber
name: 有效租户配置
predicate: "tenant_setting_config.enable = 'Y'"
scope: "登录、注销、租户配置查询"
evidence: "code:SaaSAuthController.java#getTenantSetting(TenantSettingConfigDO.enable=BooleanEnum.Y)"
```
---END FILE---

---FILE: calibers/valid-cust-person.md ---
---
type: caliber
title: 有效企业联系人
page_key: caliber:valid-cust-person
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 有效经办人口径
  - enable=Y 联系人
oid: 1
scope:
  databases: []
sources:
  - "code:UserFacade.java#handUserList"
contract_version: "0.1"
---

# 有效企业联系人

业务定位：查询经办人、管理员、登录用户列表时的有效性条件，统一以 cust_person_info.enable = Y 过滤。

## 需求背景

冻结用户时若清空某产品下的全部关系，会把 enable 置 N，解冻时恢复 Y（见 [[rules/freeze-unfreeze-user]]），因此 enable 并不等同于业务意义上的离职。联系人生效状态另见 [[processes/cust-person-status]]，字段见 [[tables/cust_person_info]]。

## 版本演进

v0 定义当前口径，未见演进证据。

```ground:caliber
name: 有效企业联系人
predicate: "cust_person_info.enable = 'Y'"
scope: "经办人/管理员/登录用户列表查询"
evidence: "code:UserFacade.java#handUserList(eq(enable, YesOrNoEnum.YES))"
```
---END FILE---

---FILE: calibers/not-frozen-cust-user-rel.md ---
---
type: caliber
title: 未冻结企业-用户关系
page_key: caliber:not-frozen-cust-user-rel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 未冻结关系口径
  - is_freeze=N
oid: 1
scope:
  databases: []
sources:
  - "code:UserFacade.java#querySysCustUserList"
contract_version: "0.1"
---

# 未冻结企业-用户关系

业务定位：判断用户在某产品/企业下是否可登录可用的核心口径：sys_cust_user_rel.is_freeze = 'N'。

## 需求背景

冻结语义落在关系维度，因此「是否可用」必须按关系而非账号判断；代码中通过 `"N".equals(isFreeze)` 过滤（见 [[rules/freeze-unfreeze-user]]）。与账号级状态的区别见 [[concepts/user-freeze-flag]] 与 [[processes/user-freeze-state]]。

## 版本演进

v0 定义当前口径，未见演进证据。

```ground:caliber
name: 未冻结企业-用户关系
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: "判断用户在产品/企业下是否可登录可用"
evidence: "code:UserFacade.java#querySysCustUserList(filter \"N\".equals(isFreeze))"
```
---END FILE---

---FILE: calibers/pre-delete-user-check.md ---
---
type: caliber
title: 删除用户前判定
page_key: caliber:pre-delete-user-check
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 用户级联删除判定
  - 企业删除前判定
oid: 1
scope:
  databases: []
sources:
  - "code:CustCompanyInfoApplication.java#deleteCustInfo"
contract_version: "0.1"
---

# 删除用户前判定

业务定位：企业删除后是否级联删除 sys_user 的判定口径——当该用户名下不存在 is_freeze = 'N' 的关系时，才允许级联删除账号。

## 需求背景

该口径复用了关系冻结语义（见 [[calibers/not-frozen-cust-user-rel]]、[[tables/sys_cust_user_rel]]），把「还有可用关系」视为不可删除的保护条件，避免误删仍可登录的账号。

## 版本演进

v0 定义当前口径，未见演进证据。

```ground:caliber
name: 删除用户前判定
predicate: "sys_cust_user_rel.is_freeze = 'N' 的关系为空"
scope: "企业删除后是否级联删除 sys_user"
evidence: "code:CustCompanyInfoApplication.java#deleteCustInfo"
```
---END FILE---

---FILE: calibers/main-data-company.md ---
---
type: caliber
title: 主数据企业
page_key: caliber:main-data-company
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 主数据企业口径
  - data_type=MAIN
oid: 1
scope:
  databases: []
sources:
  - "code:CustCompanyInfoApplication.java#appendUpdateCustBuildStatus"
contract_version: "0.1"
---

# 主数据企业

业务定位：企业认证状态条件更新时的主数据过滤口径：data_type = 'MAIN' 且 enable = 'Y'。

## 需求背景

只有主数据企业才允许被认证/建档状态的条件更新命中，避免污染非主数据记录；状态机见 [[processes/cust-build-status]]，表见 [[tables/cust_company_info]]。

## 版本演进

v0 定义当前口径，未见演进证据。

```ground:caliber
name: 主数据企业
predicate: "cust_company_info.data_type = 'MAIN' AND enable = 'Y'"
scope: "企业认证状态条件更新"
evidence: "code:CustCompanyInfoApplication.java#appendUpdateCustBuildStatus"
```
---END FILE---

---FILE: calibers/build-success-company.md ---
---
type: caliber
title: 建档成功企业
page_key: caliber:build-success-company
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 建档成功企业口径
  - BUILD_SUCCESS 企业
oid: 1
scope:
  databases: []
sources:
  - "code:CustSysOrgApplication.java#listBuildSuccessCusts"
contract_version: "0.1"
---

# 建档成功企业

业务定位：组织架构初始化（含批量初始化根组织）的企业选取口径：cust_build_status = 'BUILD_SUCCESS' 且 enable = 'Y'。

## 需求背景

组织初始化必须在企业建档成功之后进行，因此以该口径圈定可初始化企业集合；状态来源见 [[processes/cust-build-status]]，表见 [[tables/cust_company_info]]。

## 版本演进

v0 定义当前口径，未见演进证据。

```ground:caliber
name: 建档成功企业
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND enable = 'Y'"
scope: "组织架构初始化/批量初始化根组织"
evidence: "code:CustSysOrgApplication.java#listBuildSuccessCusts"
```
---END FILE---

---FILE: calibers/agw-client.md ---
---
type: caliber
title: AGW 客户端
page_key: caliber:agw-client
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - AGW客户端口径
  - clientType=AGW
oid: 1
scope:
  databases: []
sources:
  - "code:SaaSAuthController.java#getTenantSetting"
contract_version: "0.1"
---

# AGW 客户端

业务定位：以请求头 clientType = 'AGW' 识别网关（AGW）客户端的分支口径，用于租户配置兜底与简易认证返回。

## 需求背景

AGW 分支下，租户配置的 SSO 渠道会被兜底赋为 scpr-pplatform-agw（见 [[concepts/sso-channel-identifier]]）；同时与有效租户配置口径 [[calibers/valid-tenant-setting]] 配合使用。

## 版本演进

v0 定义当前口径，未见演进证据。

```ground:caliber
name: AGW 客户端
predicate: "header clientType = 'AGW'"
scope: "租户配置兜底、简易认证返回"
evidence: "code:SaaSAuthController.java#getTenantSetting(\"AGW\".equals(clientType))"
```
---END FILE---

---FILE: concepts/sso-channel-identifier.md ---
---
type: concept
title: SSO 渠道标识
page_key: concept:sso-channel-identifier
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sysChannel
  - ssoSysChannel
  - ssoTenantChanel
  - sys_channel
  - SsoSysChannel
oid: 1
scope:
  databases: []
sources:
  - "code:SaaSAuthController.java#getTenantSetting"
  - "db:open_sso_channel"
contract_version: "0.1"
maps_to: "open_sso_channel.sys_channel / sso_system.sysChannel / tenant_setting_config.ssoSysChannel / ssoTenantChanel"
field_targets:
  - open_sso_channel.sys_channel
  - sso_system.sysChannel
  - tenant_setting_config.ssoSysChannel
  - tenant_setting_config.ssoTenantChanel
adjudication: boundary
also_confused_with:
  - channel_code
  - sys_type
  - app_id
  - sysChannelList
boundary: 'sysChannel/ssoSysChannel 指 SSO 系统渠道（SsoSystemDO.sysChannel，如 scpr-pplatform-pc），ssoTenantChanel 指租户绑定的 SSO 渠道（TenantDTO/ TenantSettingConfigDO，注意拼写少一个 n），二者在 SaaSAuthController#getTenantSetting 中对 AGW 客户端被赋同一值 scpr-pplatform-agw；channel_code 是业务/OpenAPI 渠道码（实测 longteng），sys_type（scpr-pplatform-pc_org...）是 SSO 系统类型，均不等同于 sysChannel。'
---

# SSO 渠道标识

业务定位：登录链路中「渠道」一词在多个层出现：SSO 系统层的 sysChannel、租户配置层的 ssoSysChannel 与 ssoTenantChanel、渠道配置表的 sys_channel。它们是同一条链路上的不同层级，不是同义词。相关表见 [[tables/sso_system]]、[[tables/tenant_setting_config]]、[[tables/open_sso_channel]]。

## 需求背景

登录、发邀请码、同步用户时以租户配置的 ssoTenantChanel 作为 sysChannel 使用；注销、登录验证码开关、渠道判优使用 ssoSysChannel。渠道配置表则按 sys_channel 一行一渠道地维护 clientId/secret 与 appId。对 AGW 客户端，租户配置取值会被兜底为 scpr-pplatform-agw（见 [[calibers/agw-client]]）。

## 版本演进

v0 记录该术语的边界与易混字段；ssoTenantChanel 的拼写来自历史字段命名，未见修正证据。

判读要点：channel_code 是业务/OpenAPI 渠道码（实测 longteng），sys_type 是 SSO 系统类型，app_id 是开放平台应用标识，三者均不等同于 sysChannel。渠道同步状态另见 [[processes/sso-channel-sync-status]]，启停口径见 [[calibers/valid-sso-channel]]。
---END FILE---

---FILE: concepts/tenant-identifier.md ---
---
type: concept
title: 租户标识
page_key: concept:tenant-identifier
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - dbTenantCode
  - db_tenant_code
  - tenantCode
oid: 1
scope:
  databases: []
sources:
  - "code:SaaSAuthController.java#register"
  - "code:MetaDataThreadLocalConfig"
contract_version: "0.1"
maps_to: "sys_user.tenant_code / cust_person_info.db_tenant_code / MetaDataThreadLocalConfig.getDbTenantCode() / cookie dbtenantCode"
field_targets:
  - sys_user.tenant_code
  - cust_person_info.db_tenant_code
adjudication: boundary
also_confused_with:
  - appTenantCode
  - app_tenant_code
  - tenantCode(RPC)
boundary: 'dbTenantCode 是数据租户标识，用于数据隔离、RPC 头 RPC_TENANT_KEY 与登录 cookie dbtenantCode；appTenantCode（app_tenant_code）是逻辑租户标识，两者在 SaaSAuthController#register 中分别取 MetaDataThreadLocalConfig.getDbTenantCode() 与 getAppTenantCode() 后一并写入注册请求。'
---

# 租户标识

业务定位：区分两个租户维度——数据租户（dbTenantCode，决定数据隔离与查询过滤）与逻辑租户（appTenantCode，决定应用侧归属）。涉及表见 [[tables/sys_user]]、[[tables/cust_person_info]]。

## 需求背景

跨租户读取 sso_user、企业联系人时必须用 dbTenantCode 过滤（见 [[tables/sys_user]] 的 tenant_code）；登录时数据租户写入 cookie dbtenantCode 与 RPC 头 RPC_TENANT_KEY。注册链路中两个租户标识被一并写入注册请求，因此排障时要明确当前断言的是哪一个。

## 版本演进

v0 记录两租户维度的边界，未见演进证据。

容易混淆的是 RPC 上下文里简称 tenantCode 的取值——需回到 MetaDataThreadLocalConfig.getDbTenantCode() 与 getAppTenantCode() 判定来源。
---END FILE---

---FILE: concepts/company-switch.md ---
---
type: concept
title: 公司/企业切换
page_key: concept:company-switch
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - changeCompany
  - companyId
  - custId
  - fbpccid
oid: 1
scope:
  databases: []
sources:
  - "code:SaaSAuthController.java#changeCompany"
  - "code:SaaSAuthController.java#makePersonEffect"
contract_version: "0.1"
maps_to: "当前登录用户在多企业间切换上下文（cookie dbtenantCode/fbpccid/fbpcctype/fbpccname/fbpcccode + 重写 redis 用户信息）"
field_targets:
  - sys_user.tenant_code
  - cust_person_info.status
adjudication: synonym
also_confused_with:
  - companyType
  - changeDefaultCompany
boundary: 'changeCompany 切换当前企业并刷新菜单（写 cookie + setReisUserInfo），changeDefaultCompany 只把某企业设为默认（default_flag=Y），两者都需 (companyId, companyType) 二元组定位企业。'
---

# 公司/企业切换

业务定位：用户在多家企业之间切换当前工作上下文的动作，通过写 cookie（dbtenantCode/fbpccid/fbpcctype/fbpccname/fbpcccode）并重写 Redis 登录用户信息来实现。切换后会把该公司下处于 ADD 的联系人置为 EFFECT（见 [[processes/cust-person-status]]）。

## 需求背景

企业定位需要 (companyId, companyType) 二元组，因为同一企业在不同企业角色下是不同上下文（见 [[concepts/company-type]]）。切换公司（changeCompany）与设置默认公司（changeDefaultCompany，default_flag=Y）是两种不同动作；登录时的默认企业初始化见 [[rules/login-init-flow]]，涉及表 [[tables/cust_person_info]]。

## 版本演进

v0 记录两个动作的边界与依赖的 cookie 键，未见演进证据。
---END FILE---

---FILE: concepts/user-freeze-flag.md ---
---
type: concept
title: 用户冻结标记
page_key: concept:user-freeze-flag
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - isFreeze
  - is_freeze
  - freezeFlag
  - FREEZE
  - UN_FROZEN
oid: 1
scope:
  databases: []
sources:
  - "code:UserFacade.java#getUserStatusEnum"
  - "code:UserFacade.java#updateListFreezeFlag"
contract_version: "0.1"
maps_to: "sys_cust_user_rel.is_freeze（Y=冻结，N=激活）"
field_targets:
  - sys_cust_user_rel.is_freeze
  - sys_user.user_status
  - cust_person_info.enable
adjudication: boundary
also_confused_with:
  - sys_user.user_status
  - UserStatusEnum.FREEZE
  - cust_status
boundary: 'is_freeze 是『企业-用户关系』维度的冻结，可只冻结某产品下的关联而不冻结登录；user_status 是全局用户状态；UserFacade#getUserStatusEnum 用 is_freeze + user_status 合成对外展示状态（N+FREEZE→INIT，Y→FREEZE）。'
---

# 用户冻结标记

业务定位：「冻结」在两个层级存在：关系级 is_freeze（企业-用户关系，Y=冻结/N=激活）与账号级 user_status（全局）。二者由 UserFacade#getUserStatusEnum 合成为对外展示状态。涉及表 [[tables/sys_cust_user_rel]]、[[tables/sys_user]]、[[tables/cust_person_info]]。

## 需求背景

产品需要支持只冻结某产品下关联而不影响登录，因此冻结语义下沉到关系维度；同时冻结/解冻是两段式操作，先动 SSO 侧再改本地（见 [[processes/user-freeze-state]]、[[rules/freeze-unfreeze-user]]）。合成规则：is_freeze=Y → FREEZE；user_status=FREEZE 且 is_freeze=N → INIT；is_freeze 为空或异常 → INIT。查询可用性口径见 [[calibers/not-frozen-cust-user-rel]]。

## 版本演进

v0 记录两级冻结的边界与合成规则，未见演进证据。
---END FILE---

---FILE: concepts/default-product-role.md ---
---
type: concept
title: 产融默认角色
page_key: concept:default-product-role
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - accountNormal
  - ROLE_CODE_NORMAL
  - 产融客户端普通用户
  - accountGuest
  - ROLE_CODE_VISITOR
  - 产融客户端游客
oid: 1
scope:
  databases: []
sources:
  - "code:UserFacade.java#addDefaultCustUserRel"
  - "code:SsoFacade.java#addUser"
  - "code:UserInfoFacade.java#initAddUserToSsoAndSys"
contract_version: "0.1"
maps_to: "sys_role 中的角色编码（ACCOUNT_PRODUCT 系统下）"
field_targets:
  - sys_cust_user_rel.role_id
  - sys_user_role.role_id
adjudication: boundary
also_confused_with:
  - authRoleCode
  - ROLE_CODE_NORMAL 常量在多处重复定义
boundary: '通过客户端/接口新增用户默认绑定普通用户角色 accountNormal；通过注册（register/SsoFacade.addUser）默认绑定游客角色 accountGuest；UserInfoFacade 与 UserFacade/UserRoleConstant 各自持有 ROLE_CODE_VISITOR/ROLE_CODE_NORMAL 常量。'
---

# 产融默认角色

业务定位：新用户进入系统时默认绑定的产融客户端角色，分两条路径：客户端/接口新增用户绑定普通用户角色（accountNormal），注册路径绑定游客角色（accountGuest）。角色编码存放在 sys_role，关系落在 sys_cust_user_rel.role_id / sys_user_role.role_id。

## 需求背景

默认角色决定新用户的初始菜单与待办可见性（见 [[rules/default-cust-user-role-binding]]）。常量在多处重复定义（UserInfoFacade 与 UserFacade/UserRoleConstant），排查角色问题时需要注意常量来源不同，避免误判。

## 版本演进

v0 记录两条默认角色路径与常量重复现状，未见演进证据。
---END FILE---

---FILE: concepts/company-type.md ---
---
type: concept
title: 企业角色 companyType
page_key: concept:company-type
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - companyType
  - custCompanyType
  - custType
  - CustCompanyTypeEnum
oid: 1
scope:
  databases: []
sources:
  - "code:CustCompanyInfoApplication.java"
contract_version: "0.1"
maps_to: "cust_company_info.cust_company_type（JSON 数组字符串）/ cust_role_info.role_type"
field_targets:
  - cust_company_info.cust_company_type
  - cust_role_info.role_type
adjudication: boundary
also_confused_with:
  - "CustCompanyTypeEnum（SUPPLIER/FINANCE/DEALER/PLATFORM_OPERATOR_COMPANY/CORPORATION_COMPANY 等）"
boundary: 'cust_company_type 存的是 JSON 数组（代码中 ["..."] 形式），单个企业可有多个企业角色，查组织/管理员时需按 companyType 逐类处理。'
---

# 企业角色 companyType

业务定位：描述企业在平台上的角色类型集合（如 SUPPLIER/FINANCE/DEALER/PLATFORM_OPERATOR_COMPANY/CORPORATION_COMPANY）。字段以 JSON 数组字符串形式存储，因此一个企业可以同时具备多个企业角色。

## 需求背景

企业定位与上下文切换需要 (companyId, companyType) 二元组（见 [[concepts/company-switch]]）；查询组织、管理员时必须按 companyType 逐类处理，不能把 JSON 数组当成单值使用。表见 [[tables/cust_company_info]]。

## 版本演进

v0 记录该字段的多值存储形态与逐类处理要求，未见演进证据。
---END FILE---

---FILE: rules/login-init-flow.md ---
---
type: rule
title: 登录初始化流程
page_key: rule:login-init-flow
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - /sys-web/user/init
  - 登录初始化
  - init 流程
oid: 1
scope:
  databases: []
sources:
  - "code:SaaSAuthController.java#init"
contract_version: "0.1"
---

# 登录初始化流程

业务定位：SSO 登录成功后的收口流程，决定登录后可见的企业上下文、菜单权限与用户状态。入口为 `/sys-web/user/init`。

## 需求背景

流程依次为：取当前 LoginUser → 初始化默认企业 → 取默认企业（getDefaultCompany）→ 写 cookie（fbpccid/fbpcctype/fbpcname/dbtenantCode/fbpcccode）→ 刷新登录用户信息到 Redis（setReisUserInfo）→ 将 sys_user 状态置 NORMAL 并把联系人 ADD 置 EFFECT。userId 为空时抛「用户未开通此系统!」。相关口径见 [[calibers/valid-tenant-setting]]，涉及表 [[tables/sys_user]]、[[tables/cust_person_info]]、[[tables/tenant_setting_config]]；默认企业上下文见 [[concepts/company-switch]]。

## 版本演进

v0 记录当前流程步骤与失败提示，未见演进证据。

```ground:rule
name: 登录初始化流程
content: "SSO 登录成功后调用 /sys-web/user/init：取当前 LoginUser → 初始化默认企业 → 取默认企业（getDefaultCompany）→ 写 cookie(fbpccid/fbpcctype/fbpcname/dbtenantCode/fbpcccode) → 刷新登录用户信息到 Redis(setReisUserInfo) → 将 sys_user 状态置 NORMAL 并把联系人 ADD 置 EFFECT。userId 为空抛『用户未开通此系统!』。"
impact: "决定登录后可见的企业上下文、菜单权限与用户状态"
field_targets:
  - sys_user.user_status
  - cust_person_info.status
evidence: "code_path:SaaSAuthController.java#init"
```
---END FILE---

---FILE: rules/freeze-unfreeze-user.md ---
---
type: rule
title: 冻结/解冻用户
page_key: rule:freeze-unfreeze-user
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - freeze/active
  - 冻结解冻
  - updateListFreezeFlag
oid: 1
scope:
  databases: []
sources:
  - "code:LocalTypeUserController.java#freeze"
  - "code:LocalTypeUserController.java#active"
  - "code:UserFacade.java#updateListFreezeFlag"
  - "code:PlatFormUserApplication.java#freezeOrThawOperatorUser"
contract_version: "0.1"
---

# 冻结/解冻用户

业务定位：用户冻结与解冻的执行规则，采用「SSO 先动、本地关系后动」的两段式，并联动企业联系人的 enable。

## 需求背景

冻结先调 saaSAuthService.freezePerson 冻结 SSO 侧，再 updateListFreezeFlag(..., FREEZE) 更新关系表；解冻先 activePerson 再 UN_FROZEN。freeze/active 时若清空某产品下所有关系，会把 cust_person_info.enable 置 N，解冻时恢复为 Y；运营人员侧走 freezeOrThawOperatorUser。状态流转见 [[processes/user-freeze-state]]，可用性口径见 [[calibers/not-frozen-cust-user-rel]]，涉及表 [[tables/sys_cust_user_rel]]、[[tables/cust_person_info]]、[[tables/operation_user]]。

## 版本演进

v0 记录两条入口的当前执行顺序与联动行为，未见演进证据。

```ground:rule
name: 冻结/解冻用户
content: "冻结先调 saaSAuthService.freezePerson 冻结 SSO 侧，再 updateListFreezeFlag(..., FREEZE) 更新关系表；解冻先 activePerson 再 UN_FROZEN。freeze/active 时若清空某产品下所有关系则把 cust_person_info.enable 置 N，解冻时恢复为 Y。"
impact: "影响用户能否登录及在某产品下的可用性"
field_targets:
  - sys_cust_user_rel.is_freeze
  - cust_person_info.enable
  - sys_user.user_status
evidence: "code_path:LocalTypeUserController.java#freeze/#active + UserFacade.java#updateListFreezeFlag + PlatFormUserApplication.java#freezeOrThawOperatorUser"
```
---END FILE---

---FILE: rules/default-cust-user-role-binding.md ---
---
type: rule
title: 默认企业-角色绑定
page_key: rule:default-cust-user-role-binding
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - addDefaultCustUserRel
  - 默认角色绑定
  - 默认企业用户关系
oid: 1
scope:
  databases: []
sources:
  - "code:UserFacade.java#addDefaultCustUserRel"
  - "code:SsoFacade.java#addUser"
  - "code:UserInfoFacade.java#initAddUserToSsoAndSys"
contract_version: "0.1"
---

# 默认企业-角色绑定

业务定位：新增用户时建立企业与角色关联的规则，决定新用户的初始菜单与待办可见性。两条路径的默认角色不同（见 [[concepts/default-product-role]]）。

## 需求背景

通过客户端新增用户时默认绑定产融客户端普通用户角色 accountNormal；若关系已存在则把 is_freeze 重置为 N（该幂等行为也是冻结状态机的入口之一，见 [[processes/user-freeze-state]]）。注册路径（SsoFacade.addUser / UserInfoFacade）默认绑定游客角色 accountGuest 并绑定 ACCOUNT_PRODUCT 系统关系。涉及表 [[tables/sys_cust_user_rel]] 与角色表 sys_role / sys_user_role。

## 版本演进

v0 记录两条路径的默认角色与幂等重置行为，未见演进证据。

```ground:rule
name: 默认企业-角色绑定
content: "通过客户端新增用户时默认绑定产融客户端普通用户角色 accountNormal；若已存在关系则把 is_freeze 重置为 N。注册路径（SsoFacade.addUser / UserInfoFacade）默认绑定游客角色 accountGuest 并绑定 ACCOUNT_PRODUCT 系统关系。"
impact: "决定新用户初始菜单/待办可见性"
field_targets:
  - sys_cust_user_rel.role_id
  - sys_user_role.role_id
evidence: "code_path:UserFacade.java#addDefaultCustUserRel + SsoFacade.java#addUser + UserInfoFacade.java#initAddUserToSsoAndSys"
```
---END FILE---

---REVIEW: rule | 一个租户一个手机号可关联多企业---
语义分析中该规则的 content 被截断（原文止于「同一租户下手机号」），且未提供 evidence 与 field_targets，无法逐字还原主张，因此不产出 rule 页。

待确认事项：
1. 该规则完整的判定主体与判定条件（手机号 / 租户 / 企业的关系数量约束）为何；
2. 是否属于约束（唯一性/多重性）而非流程规则，若是则应落到 caliber 或 table 页；
3. 代码锚点（controller/service 方法）与涉及的物理表。
---END REVIEW---

---REVIEW: table | scope.databases 物理库名缺失---
本次语义分析的所有 table 页 field_semantics 证据仅标注 `db` / `code`，未给出物理库名，因此全部页面的 `scope.databases` 暂置为空列表，未做任何推断填充。

待确认事项：
1. DBAss/SSO 登录与通道主题涉及的物理库名（open_sso_channel、sso_system、sso_user、sys_user、sys_cust_user_rel、cust_person_info、cust_company_info、tenant_setting_config、operation_user 分属哪个库）；
2. 上述表是否跨库（若跨库，各页 scope.databases 需分别补齐）。
---END REVIEW---