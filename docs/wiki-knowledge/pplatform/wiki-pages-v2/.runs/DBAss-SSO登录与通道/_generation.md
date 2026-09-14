---FILE: tables/open_sso_channel.md---
---
type: table
title: open_sso_channel
page_key: open_sso_channel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 开放SSO渠道配置表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:open_sso_channel
  - code:SaaSAuthController.java:resolveNeedLoginCaptcha
contract_version: "0.1"
---

开放平台 SSO 渠道配置表，登记业务渠道与 SSO 平台侧系统渠道（[[sys_channel]]）的绑定关系，
承载 appId、clientId/secret、机构编码（[[org_code]]）与同步状态，是登录、登出、图形验证码策略
与渠道初始化的配置来源。本表与 [[tenant_setting_config]] 语义相邻：租户配置的统码
（[[tenant_sso_chanel]]）在代码中被直接当作 sysChannel 使用（`byCode.getSsoTenantChanel()` → `userDTO.setSsoSysChannel`），
二者存储位置不同，不可互换。

## 需求背景

各业务渠道接入 SSO 单点登录前，需在 SSO 平台登记系统渠道并同步渠道码、密钥、所属机构。
本表保存该绑定关系与同步结果：登录链路据此判断图形验证码策略（[[login_captcha_policy]]），
渠道同步异常通过 sso_sync_msg 记录失败原因（[[sso_channel_sync_state]]）。

## 版本演进

- v0（草稿）：字段语义来自 DB 实测值 + 代码引用，字段类型与物理库名未在语义分析中给出，见 REVIEW。

```ground:table
table: open_sso_channel
fields:
  - name: sys_channel
    type: unknown
    desc: "SSO 系统渠道编码（sysChannel），SSO 平台侧系统标识；DB 实测形如 scpr-pplatform-pc 或被追加机构后缀 scpr-pplatform-pc_org{统一社会信用代码}"
    dict: ""
  - name: sys_type
    type: unknown
    desc: "SSO sysType；DB 实测值与 sys_channel 同域（scpr-pplatform-pc_org...），用于区分系统类型/机构维度"
    dict: ""
  - name: channel_code
    type: unknown
    desc: "业务/OpenAPI 渠道码；DB 实测 longteng"
    dict: ""
  - name: channel_kind
    type: unknown
    desc: "渠道类型；DB 实测 LOCAL_SYS（本地系统）"
    dict: ""
  - name: channel_name
    type: unknown
    desc: "渠道名称；DB 实测 龙腾"
    dict: ""
  - name: app_id
    type: unknown
    desc: "开放平台 appId；DB 实测 73d62771729e4ffba7f263cb6012746d"
    dict: ""
  - name: sso_client_id
    type: unknown
    desc: "渠道独立 SSO clientId；DB 实测 r6n8u7p3"
    dict: ""
  - name: sso_client_secret
    type: unknown
    desc: "SSO 密钥"
    dict: ""
  - name: org_code
    type: unknown
    desc: "同步 SSO 机构编码；代码中以 RpcContext attachment（ContextHelper.orgCodeKey）在调用 SSO 前透传"
    dict: ""
  - name: sso_sync_status
    type: unknown
    desc: "SSO 同步状态；DB 实测 SYNCED（已同步）"
    dict: ""
  - name: sso_sync_msg
    type: unknown
    desc: "SSO 同步描述/失败原因；DB 实测“找不到此系统渠道：scpr-pplatform-pc_org91130421356828213h”"
    dict: ""
  - name: open_mode_default
    type: unknown
    desc: "默认打开形态，枚举语义 EMBED/TOP；DB 实测 EMBED"
    dict: ""
  - name: enable
    type: unknown
    desc: "启用标记 Y/N；DB 实测 N=1、Y=1"
    dict: ""
  - name: db_tenant_code
    type: unknown
    desc: "数据租户标识"
    dict: ""
  - name: app_tenant_code
    type: unknown
    desc: "逻辑租户标识（区别于 db_tenant_code）"
    dict: ""
```

相关：[[sys_channel]]、[[tenant_sso_chanel]]、[[org_code]]、[[sso_channel_sync_state]]、[[login_captcha_policy]]。
---END FILE---

---FILE: tables/operation_user.md---
---
type: table
title: operation_user
page_key: operation_user
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 运营中台人员表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:operation_user
contract_version: "0.1"
---

运营中台人员表，保存运营侧人员主数据与启用/删除标记。其 operation_id 为外部系统主键，
与登录用户表 [[sys_user]] 不是同一实体，勿按“用户”语义混用；数据租户维度见 [[db_tenant_code]]。

## 需求背景

运营中台人员的账号需与业务登录账号区分管理：删除用 deleted、启停用 enable 双标记，
另有 status 记录人员用户状态（DB 未给出取值分布）。

## 版本演进

- v0（草稿）：字段语义来自 DB 实测，status 取值域未获得证据。

```ground:table
table: operation_user
fields:
  - name: status
    type: unknown
    desc: "运营中台人员用户状态标识（DB 未给出取值分布）"
    dict: ""
  - name: deleted
    type: unknown
    desc: "删除标识；DB 实测 N=119、Y=22"
    dict: ""
  - name: enable
    type: unknown
    desc: "启用标记 Y/N；DB 实测 Y=132、N=9"
    dict: ""
  - name: operation_group
    type: unknown
    desc: "运营组别"
    dict: ""
  - name: operation_id
    type: unknown
    desc: "运营中台人员 id（外部系统主键）"
    dict: ""
  - name: db_tenant_code
    type: unknown
    desc: "数据租户标识；DB 实测 base"
    dict: ""
```
---END FILE---

---FILE: tables/sys_cust_user_rel.md---
---
type: table
title: sys_cust_user_rel
page_key: sys_cust_user_rel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 企业用户产品角色关联表
oid: 1
scope:
  databases: [unknown]
sources:
  - code:UserFacade.java:updateListFreezeFlag
  - code:UserFacade.java:getUserStatusEnum
contract_version: "0.1"
---

企业-用户-产品-角色关联表，本主题只使用其冻结标记 [[sys_cust_user_rel.is_freeze]]：
N=激活、Y=冻结（代码注释“冻结标记,N表示激活,Y表示冻结”），由 `UserFreezeEnum.getDictKey()` 写入。
该标记是 [[user_not_frozen]] 口径的过滤依据，并与 [[login_user_status_state]] 中 sys_user.user_status
的 FREEZE 态存在映射关系。

## 需求背景

冻结/解冻必须在 SSO 侧与本地关联表两侧同时生效，见规则 [[freeze_active_dual_write]]；
只改一侧会出现“能登录但无权限”或相反的不一致。

## 版本演进

- v0（草稿）：字段语义来自代码注释与写入点，无 DB 取值分布证据。

```ground:table
table: sys_cust_user_rel
fields:
  - name: is_freeze
    type: unknown
    desc: "企业-用户-产品-角色关联的冻结标记：N=激活、Y=冻结（代码注释“冻结标记,N表示激活,Y表示冻结”），由 UserFreezeEnum.getDictKey() 写入"
    dict: ""
```

相关：[[sys_cust_user_rel_freeze_state]]、[[user_not_frozen]]、[[freeze_active_dual_write]]。
---END FILE---

---FILE: tables/cust_person_info.md---
---
type: table
title: cust_person_info
page_key: cust_person_info
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 企业经办人表
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:makePersonEffect
  - code:UserFacade.java:handUserList
contract_version: "0.1"
---

企业经办人（联系人）表。status 以字面量写入 ADD/EFFECT（新增待生效 → 生效），
enable 查询以 'Y' 过滤（[[enabled_person_contact]]）。注意：语义分析中的 StatusEnum（EFFECTIVE/INVALID）
未参与本链路，见 REVIEW。

## 需求背景

用户列表需要补全用户类型/邮箱，经办人联系人须为启用态；SSO 登录初始化/切换企业时把
ADD 态经办人置为 EFFECT（[[cust_person_info_status_state]]）。

## 版本演进

- v0（草稿）：字段语义来自代码写值点与查询条件，无 DB 取值分布证据。

```ground:table
table: cust_person_info
fields:
  - name: status
    type: unknown
    desc: "企业经办人状态，代码以字面量写入：ADD（新增待生效）/EFFECT（生效）"
    dict: ""
  - name: enable
    type: unknown
    desc: "联系人启用标记，查询以 'Y' 过滤"
    dict: ""
```

相关：[[cust_person_info_status_state]]、[[enabled_person_contact]]。
---END FILE---

---FILE: tables/tenant_setting_config.md---
---
type: table
title: tenant_setting_config
page_key: tenant_setting_config
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 租户配置表
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getTenantSetting
  - code:SaaSAuthController.java:logout
  - code:UserFacade.java:getSsoTenantChannel
contract_version: "0.1"
---

租户配置表，按 db_tenant_code 维度保存 SSO 渠道相关配置：sso_sys_channel（logout 传参、
验证码策略判断、DTO 返回）、sso_tenant_chanel（[[tenant_sso_chanel]]，代码中直接赋给 DTO 的
ssoSysChannel）、dbass_app_id（DBAss 接入凭据，返回前端前显式置 null 脱敏）。与 [[open_sso_channel]]
通过“统码≈sysChannel”的语义映射相邻，无物理外键。

## 需求背景

登录/登出、菜单、验证码策略均需按租户取配置，且只认启用态：见 [[valid_tenant_setting]]、
[[tenant_setting_by_db_tenant_code]]、[[login_captcha_policy]]。

## 版本演进

- v0（草稿）：字段语义来自代码引用点，无 DB 取值分布证据。

```ground:table
table: tenant_setting_config
fields:
  - name: sso_sys_channel
    type: unknown
    desc: "租户配置的 SSO 系统渠道编码，用于 logout 传参、验证码策略判断、DTO 返回"
    dict: ""
  - name: sso_tenant_chanel
    type: unknown
    desc: "租户 SSO 统码/渠道（代码中被直接赋给 DTO 的 ssoSysChannel 使用）"
    dict: ""
  - name: db_tenant_code
    type: unknown
    desc: "数据租户标识，租户配置查询主键条件"
    dict: ""
  - name: enable
    type: unknown
    desc: "启用标记，查询条件固定 'Y'"
    dict: ""
  - name: dbass_app_id
    type: unknown
    desc: "DBAss appId，返回前端前被显式置 null（脱敏）"
    dict: ""
```

相关：[[tenant_sso_chanel]]、[[sys_channel]]、[[dbass]]、[[valid_tenant_setting]]。
---END FILE---

---FILE: tables/cust_company_info.md---
---
type: table
title: cust_company_info
page_key: cust_company_info
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 企业主数据表
oid: 1
scope:
  databases: [unknown]
sources:
  - code:LocalTypeUserController.java:getDbTenantCodeById
  - code:SaaSAuthController.java:getCurrentCustList
contract_version: "0.1"
---

企业主数据表，在本主题中承担“企业 → 数据租户编码”的桥接：由 custId 反查
[[cust_company_info.db_tenant_code]]，再据此查询租户配置（[[tenant_setting_config]]）与
SSO 渠道（[[open_sso_channel]]）。多公司列表以 (companyId + companyType) 去重取默认，
见规则 [[multi_company_dedup_default]]。

## 需求背景

登录初始化需把当前企业上下文（companyId/companyType/companyName/companyCode 及 dbtenantCode）
写入 Cookie 与 Redis（[[login_init_cookie]]）；注册并发控制也以 dbTenantCode 为锁维度
（[[register_distributed_lock]]）。

## 版本演进

- v0（草稿）：字段语义来自代码反查与去重逻辑，无 DB 取值分布证据。

```ground:table
table: cust_company_info
fields:
  - name: id
    type: unknown
    desc: "企业主键；getDbTenantCodeById 以 id 反查 db_tenant_code，getCurrentCustList 以 (companyId+companyType) 去重"
    dict: ""
  - name: cust_company_type
    type: unknown
    desc: "企业类型，与 companyId 共同作为多公司列表去重键"
    dict: ""
  - name: db_tenant_code
    type: unknown
    desc: "企业所属数据租户编码，由 custId 反查得到，是后续租户配置/SSO 渠道的桥梁"
    dict: ""
```

相关：[[db_tenant_code]]、[[list_user_page_tenant_channel_backfill]]、[[multi_company_dedup_default]]。
---END FILE---

---FILE: tables/cust_project_rel.md---
---
type: table
title: cust_project_rel
page_key: cust_project_rel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 企业项目关联表
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getPclogPath
contract_version: "0.1"
---

企业-项目关联表。关联企业使用 code（非 id）字段
[[cust_project_rel.ref_cust_project_rel_cust_company_info]]，并与 db_tenant_code 联合过滤企业项目；
登录取项目 logo 时要求 enable='Y'（[[valid_cust_project_rel]]）。

## 需求背景

登录成功后需按当前企业与租户拿到项目 logo（经 cosFileUtil 转为下载 URL，最终落到
[[tenant_project.logo_path]]），关联关系必须为启用态。

## 版本演进

- v0（草稿）：字段语义来自代码查询条件，无 DB 取值分布证据。

```ground:table
table: cust_project_rel
fields:
  - name: ref_cust_project_rel_cust_company_info
    type: unknown
    desc: "关联企业 code（非 id），与 db_tenant_code 联合过滤企业项目"
    dict: ""
  - name: db_tenant_code
    type: unknown
    desc: "数据租户标识，企业项目关联按租户编码过滤"
    dict: ""
  - name: enable
    type: unknown
    desc: "启用标记，查询固定 'Y'"
    dict: ""
```

相关：[[valid_cust_project_rel]]、[[tenant_project]]、[[db_tenant_code]]。
---END FILE---

---FILE: tables/tenant_project.md---
---
type: table
title: tenant_project
page_key: tenant_project
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 租户项目表
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getPclogPath
contract_version: "0.1"
---

租户项目表。登录取项目 logo 时使用其 [[tenant_project.logo_path]]，并经 cosFileUtil 转换为下载 URL；
项目须为启用态（[[valid_tenant_project]]）。

## 需求背景

登录返回的 logo 路径需可直接供前端下载，代码侧统一做 COS 路径→URL 的转换，
因此库内保存的是路径而非完整 URL。

## 版本演进

- v0（草稿）：字段语义来自代码引用点，无 DB 取值分布证据。

```ground:table
table: tenant_project
fields:
  - name: logo_path
    type: unknown
    desc: "项目 logo 路径，经 cosFileUtil 转换为下载 URL"
    dict: ""
  - name: enable
    type: unknown
    desc: "启用标记，查询固定 'Y'"
    dict: ""
```

相关：[[valid_tenant_project]]、[[cust_project_rel]]。
---END FILE---

---FILE: tables/sys_user.md---
---
type: table
title: sys_user
page_key: sys_user
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 登录用户表
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:init
  - code:UserFacade.java:getUserStatusEnum
  - code:UserInfoFacade.java:updateCustPerson
contract_version: "0.1"
---

登录用户表，本主题涉及用户系统状态 [[sys_user.user_status]]（INIT/NORMAL/FREEZE，见
[[login_user_status_state]]）、手机号与邮箱（验证码发送 key 与场景降级，见
[[send_login_code_idempotent_lock]]）、sso_user_id（非空时参与 SSO 邮箱回写，见
[[update_cust_person_sso_email]]）。与 [[operation_user]] 不是同一实体。

## 需求背景

SSO 登录初始化把 INIT 置为 NORMAL；企业/用户冻结（is_freeze=Y）映射为 FREEZE。
AGW 网关还可在不校验登录态的情况下代更新邮箱（[[update_agw_login_email]]）。

## 版本演进

- v0（草稿）：字段语义来自代码写值点与查询条件，无 DB 取值分布证据。

```ground:table
table: sys_user
fields:
  - name: user_status
    type: unknown
    desc: "登录用户系统状态；代码枚举 INIT（初始）/NORMAL（正常）/FREEZE（冻结）"
    dict: ""
  - name: mobile
    type: unknown
    desc: "用户手机号，验证码发送锁 key 与空值场景降级判定使用"
    dict: ""
  - name: email
    type: unknown
    desc: "用户邮箱；验证码发送可按场景降级为邮箱场景，updateCustPerson 更新后回写 SSO"
    dict: ""
  - name: sso_user_id
    type: unknown
    desc: "SSO 侧用户标识，非空时参与 sso_user.email 回写"
    dict: ""
  - name: tenant_code
    type: unknown
    desc: "租户编码；企业 db_tenant_code 用于定位同租户下用户（CustSysOrgApplication.bindCustOrgUser）"
    dict: ""
```

相关：[[login_user_status_state]]、[[send_login_code_idempotent_lock]]、[[update_agw_login_email]]。
---END FILE---

---FILE: processes/sys_cust_user_rel_freeze_state.md---
---
type: process
title: 企业用户冻结状态
page_key: sys_cust_user_rel_freeze_state
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - is_freeze 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - code:LocalTypeUserController.java:freeze
  - code:LocalTypeUserController.java:active
  - code:UserFacade.java:updateListFreezeFlag
contract_version: "0.1"
---

企业-用户-产品-角色关联的冻结状态机，作用于 [[sys_cust_user_rel.is_freeze]]：N=激活、Y=冻结。
两个迁移都必须先调 SSO 再改本地关联表，见规则 [[freeze_active_dual_write]]，
过滤未冻结的口径见 [[user_not_frozen]]。

## 需求背景

冻结/解冻是跨系统操作：SSO 侧负责登录态，本地表负责权限过滤，两侧必须一致，
否则出现“能登录但无权限”或相反的不一致。

## 版本演进

- v0（草稿）：状态值来自代码常量，迁移来自控制层与 Facade 调用点。

```ground:process
name: 企业用户冻结状态
field: sys_cust_user_rel.is_freeze
states:
  - value: N
    label: 激活（未冻结）
    source: code_const
  - value: Y
    label: 冻结
    source: code_const
transitions:
  - from: N
    event: POST /sys-web/user/freeze（先 SSO freezePerson，再 updateListFreezeFlag）
    to: Y
    evidence: "code_path:LocalTypeUserController.java:freeze + UserFacade.java:updateListFreezeFlag"
  - from: Y
    event: POST /sys-web/user/active（先 SSO activePerson，再 updateListFreezeFlag）
    to: N
    evidence: "code_path:LocalTypeUserController.java:active + UserFacade.java:updateListFreezeFlag"
```

相关：[[sys_cust_user_rel]]、[[freeze_active_dual_write]]、[[user_not_frozen]]、[[login_user_status_state]]。
---END FILE---

---FILE: processes/cust_person_info_status_state.md---
---
type: process
title: 企业经办人状态
page_key: cust_person_info_status_state
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - cust_person_info.status 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:makePersonEffect
contract_version: "0.1"
---

企业经办人状态机，作用于 [[cust_person_info.status]]：字面量 ADD（新增待生效）→ EFFECT（生效），
由 SSO 登录初始化 / 切换企业触发。启用态联系人过滤见 [[enabled_person_contact]]。

## 需求背景

经办人新增后需在用户真实登录并确认企业上下文时才转为生效，避免未验证的经办人参与用户列表补全。

文档中“切换公司 = SaaSAuthController.changeCompany → SaaSAuthService.change(ChangeCompanyDTO) → SsoFacade 切换租户上下文并刷新缓存”
的链路与代码不符（refuted）：实际 changeCompany 调用 `saaSAuthService.getCompanyByUserAndCode(userId, companyId, companyType)`，
再改写 Cookie、`roleFacade.getAuthUrls` 并 `setReisUserInfo`，未见 change(ChangeCompanyDTO)/SsoFacade 切换。
该主张仅作业务叙述保留，不作为契约。

## 版本演进

- v0（草稿）：状态值来自代码字面量写值点；切换企业链路以代码为准。

```ground:process
name: 企业经办人状态
field: cust_person_info.status
states:
  - value: ADD
    label: 新增待生效
    source: code_const
  - value: EFFECT
    label: 生效
    source: code_const
transitions:
  - from: ADD
    event: SSO 登录初始化/切换企业（init / changeCompany）
    to: EFFECT
    evidence: "code_path:SaaSAuthController.java:makePersonEffect"
```

相关：[[cust_person_info]]、[[enabled_person_contact]]、[[login_init_cookie]]。
---END FILE---

---FILE: processes/sso_channel_sync_state.md---
---
type: process
title: SSO 渠道同步状态
page_key: sso_channel_sync_state
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sso_sync_status 状态
oid: 1
scope:
  databases: [unknown]
sources:
  - db:open_sso_channel.sso_sync_status
  - db:open_sso_channel.sso_sync_msg
contract_version: "0.1"
---

[[open_sso_channel.sso_sync_status]] 目前只观测到 SYNCED（已同步）一个取值（DB 实测），
失败信息落在 [[open_sso_channel.sso_sync_msg]]，例如“找不到此系统渠道：scpr-pplatform-pc_org91130421356828213h”，
说明存在“渠道未在 SSO 平台登记/机构后缀不匹配”的失败场景。

## 需求背景

渠道配置需要从业务侧同步到 SSO 平台，同步结果直接决定该渠道能否完成单点登录；
同步失败原因必须可见以支持排查（文档主张的初始化服务链路见 REVIEW）。

## 版本演进

- v0（草稿）：只有 DB 实测状态值，未观测到状态迁移证据，故不登记 transitions。

```ground:process
name: SSO 渠道同步状态
field: open_sso_channel.sso_sync_status
states:
  - value: SYNCED
    label: 已同步
    source: db_dist
transitions: []
```

相关：[[open_sso_channel]]、[[sys_channel]]、[[login_captcha_policy]]。
---END FILE---

---FILE: processes/login_user_status_state.md---
---
type: process
title: 登录用户系统状态
page_key: login_user_status_state
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sys_user.user_status 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:init
  - code:UserFacade.java:getUserStatusEnum
contract_version: "0.1"
---

（document_claim，未证实）文档主张“SaaS 登录：SaaSAuthService.login → SsoBlackWhiteListService 黑白名单校验 →
SSO 返回 token → UserFacade 加载用户 → LocalTypeMenuService 加载菜单”，该链路在给定语义分析中为 uncovered，
本文仅作为版本演进记录，不作为契约。

登录用户系统状态机，作用于 [[sys_user.user_status]]：INIT（初始）→ NORMAL（正常）→ FREEZE（冻结）。
初始化由 SSO 登录 init 写入 NORMAL；企业冻结/用户冻结（[[sys_cust_user_rel.is_freeze]]=Y 映射）置 FREEZE。
菜单接口与验证码策略见 [[get_user_menu_perm_list]]、[[login_captcha_policy]]。

## 需求背景

用户首次登录处于 INIT，完成企业上下文初始化后才可正常使用；一旦企业或用户被冻结，
登录用户需同步进入 FREEZE，与本地关联表冻结标记保持一致。

## 版本演进

- v0（草稿）：状态值来自代码枚举，迁移来自 init 与状态映射代码。
- （document_claim，未证实）登录全链路（login / SsoBlackWhiteListService / token / UserFacade / LocalTypeMenuService）待代码核实。

```ground:process
name: 登录用户系统状态
field: sys_user.user_status
states:
  - value: INIT
    label: 初始
    source: code_enum
  - value: NORMAL
    label: 正常
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
transitions:
  - from: INIT
    event: SSO 登录初始化 init
    to: NORMAL
    evidence: "code_path:SaaSAuthController.java:init(ssoFacade.updateSysUserStatus(...,UserStatusEnum.NORMAL))"
  - from: NORMAL
    event: 企业冻结/用户冻结（is_freeze=Y 映射）
    to: FREEZE
    evidence: "code_path:UserFacade.java:getUserStatusEnum"
```

相关：[[sys_user]]、[[sys_cust_user_rel_freeze_state]]、[[freeze_active_dual_write]]。
---END FILE---

---FILE: calibers/valid_tenant_setting.md---
---
type: caliber
title: 有效租户配置
page_key: valid_tenant_setting
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 启用态租户配置
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getTenantSetting
  - code:SaaSAuthController.java:logout
contract_version: "0.1"
---

口径“有效租户配置”用于登录/登出取租户配置：只有 enable='Y' 的 [[tenant_setting_config]] 记录可用。

## 需求背景

租户配置存在历史数据与停用记录，登录/登出、菜单、验证码策略都必须只认启用态，
否则会取到过期的 SSO 渠道或统码。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 有效租户配置
predicate: "tenant_setting_config.enable = 'Y'"
scope: getTenantSetting / logout 查询租户配置
evidence: "code_path:SaaSAuthController.java:getTenantSetting + SaaSAuthController.java:logout"
```

相关：[[tenant_setting_config]]、[[tenant_setting_by_db_tenant_code]]、[[login_captcha_policy]]。
---END FILE---

---FILE: calibers/tenant_setting_by_db_tenant_code.md---
---
type: caliber
title: 按数据租户查询租户配置
page_key: tenant_setting_by_db_tenant_code
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 租户配置查库键
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getTenantSetting
contract_version: "0.1"
---

口径“按数据租户查询租户配置”：以当前线程租户编码
（`MetaDataThreadLocalConfig.getDbTenantCode()`）匹配 [[tenant_setting_config.db_tenant_code]]，
再叠加启用态（[[valid_tenant_setting]]）。

## 需求背景

登录/登出、菜单与验证码策略需要在多租户下正确取到本租户配置，租户键必须来自线程上下文而非入参，
避免跨租户取值。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 按数据租户查询租户配置
predicate: "tenant_setting_config.db_tenant_code = MetaDataThreadLocalConfig.getDbTenantCode()"
scope: 登录/登出、菜单、验证码策略
evidence: "code_path:SaaSAuthController.java:getTenantSetting"
```

相关：[[tenant_setting_config]]、[[db_tenant_code]]、[[valid_tenant_setting]]。
---END FILE---

---FILE: calibers/valid_cust_project_rel.md---
---
type: caliber
title: 有效项目关联
page_key: valid_cust_project_rel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 启用态企业项目关联
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getPclogPath
contract_version: "0.1"
---

口径“有效项目关联”：登录取企业/项目 logo 时，只使用 enable='Y' 的 [[cust_project_rel]] 记录，
并与 db_tenant_code 联合过滤。

## 需求背景

企业-项目关联存在解绑/停用记录，登录返回的项目信息必须只取有效关联，
避免给前端返回已停用项目的 logo。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 有效项目关联
predicate: "cust_project_rel.enable = 'Y'"
scope: 登录取企业/项目 logo
evidence: "code_path:SaaSAuthController.java:getPclogPath"
```

相关：[[cust_project_rel]]、[[valid_tenant_project]]、[[tenant_project]]。
---END FILE---

---FILE: calibers/valid_tenant_project.md---
---
type: caliber
title: 有效项目
page_key: valid_tenant_project
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 启用态项目
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getPclogPath
contract_version: "0.1"
---

口径“有效项目”：登录取项目 logo 时只使用 enable='Y' 的 [[tenant_project]] 记录。

## 需求背景

项目停用后不应再返回其 logo；项目 logo 取自 [[tenant_project.logo_path]] 并转换为下载 URL。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 有效项目
predicate: "tenant_project.enable = 'Y'"
scope: 登录取项目 logo
evidence: "code_path:SaaSAuthController.java:getPclogPath"
```

相关：[[tenant_project]]、[[valid_cust_project_rel]]。
---END FILE---

---FILE: calibers/user_not_frozen.md---
---
type: caliber
title: 用户未冻结
page_key: user_not_frozen
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 未冻结用户
oid: 1
scope:
  databases: [unknown]
sources:
  - code:UserFacade.java:updateListFreezeFlag
contract_version: "0.1"
---

口径“用户未冻结”：用户列表/角色查询过滤 [[sys_cust_user_rel.is_freeze]] = 'N' 的记录。

## 需求背景

冻结用户不应出现在用户列表与角色授权结果中；冻结状态本身由 SSO 与本地双写维护
（[[freeze_active_dual_write]]、[[sys_cust_user_rel_freeze_state]]）。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 用户未冻结
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 用户列表/角色查询过滤未冻结
evidence: "code_path:UserFacade.java:updateListFreezeFlag"
```

相关：[[sys_cust_user_rel]]、[[sys_cust_user_rel_freeze_state]]、[[login_user_status_state]]。
---END FILE---

---FILE: calibers/enabled_person_contact.md---
---
type: caliber
title: 启用联系人
page_key: enabled_person_contact
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 有效经办人
oid: 1
scope:
  databases: [unknown]
sources:
  - code:UserFacade.java:handUserList
contract_version: "0.1"
---

口径“启用联系人”：用户列表补全用户类型/邮箱时，只取 [[cust_person_info.enable]] = 'Y' 的经办人（联系人）记录。

## 需求背景

用户列表需要补全用户类型与邮箱，只有启用态联系人参与补全；经办人状态另有
ADD/EFFECT 生命周期（[[cust_person_info_status_state]]）。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 启用联系人
predicate: "cust_person_info.enable = 'Y'"
scope: 用户列表补全用户类型/邮箱
evidence: "code_path:UserFacade.java:handUserList"
```

相关：[[cust_person_info]]、[[cust_person_info_status_state]]。
---END FILE---

---FILE: concepts/sys_channel.md---
---
type: concept
title: sysChannel
page_key: sys_channel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sys_channel
  - ssoSysChannel
  - SsoSystemDO.sysChannel
oid: 1
scope:
  databases: [unknown]
sources:
  - db:open_sso_channel.sys_channel
  - code:SaaSAuthController.java:resolveNeedLoginCaptcha
  - code:LocalTypeUserController.java:listUserPage
contract_version: "0.1"
maps_to: open_sso_channel.sys_channel
also_confused_with:
  - tenant_setting_config.sso_tenant_chanel
adjudication: boundary
---

sysChannel 指 SSO 平台侧系统渠道编码，落在 [[open_sso_channel.sys_channel]]；
SsoSystemDO.sysChannel 与 ssoSysChannel（DTO 字段）都是它的代码侧投影。
DB 实测形如 scpr-pplatform-pc，或带机构后缀 scpr-pplatform-pc_org{统一社会信用代码}。

## 需求背景

登录链路以 sysChannel 作为与 SSO 平台对话的系统标识：验证码策略查询 SsoSystemDO.captcha
（[[login_captcha_policy]]），租户配置回填 DTO 时也复用它。

## 版本演进

- v0（草稿）：术语边界来自代码赋值点与 DB 实测值。

边界：sysChannel 指 SSO 平台侧系统渠道编码；[[tenant_sso_chanel]]（tenant_setting_config.sso_tenant_chanel）
是租户配置的 SSO 统码，代码中常被直接赋给 DTO.ssoSysChannel（LocalTypeUserController.listUserPage 中
`byCode.getSsoTenantChanel()` → `setSsoSysChannel`），二者语义相邻但存储位置不同，不可互换。
另注意 [[org_code]] 是机构编码，不是渠道编码。
---END FILE---

---FILE: concepts/tenant_sso_chanel.md---
---
type: concept
title: 租户统码
page_key: tenant_sso_chanel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sso_tenant_chanel
  - ssoTenantChanel
  - ssoTenantChannel
oid: 1
scope:
  databases: [unknown]
sources:
  - code:UserFacade.java:getSsoTenantChannel
  - code:UserInfoFacade.java:getSsoTenantChannel
  - code:LocalTypeUserController.java:listUserPage
contract_version: "0.1"
maps_to: tenant_setting_config.sso_tenant_chanel
also_confused_with:
  - open_sso_channel.sys_channel
adjudication: boundary
---

租户统码（sso_tenant_chanel / ssoTenantChanel）是租户配置里的 SSO 渠道统码，落在
[[tenant_setting_config.sso_tenant_chanel]]。

## 需求背景

用户/联系人同步 SSO 时，租户统码被作为 sysChannel 传入（UserFacade.getSsoTenantChannel、
UserInfoFacade.getSsoTenantChannel）；用户列表也把它回填到 userDTO.ssoSysChannel
（[[list_user_page_tenant_channel_backfill]]）。

## 版本演进

- v0（草稿）：术语边界来自代码赋值点。

边界：租户统码来自租户配置表，被当作 sysChannel 使用，但两者存储位置不同；不可与
[[sys_channel]]（open_sso_channel.sys_channel）互换，也不可等同于 [[db_tenant_code]]。
---END FILE---

---FILE: concepts/db_tenant_code.md---
---
type: concept
title: dbTenantCode
page_key: db_tenant_code
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - db_tenant_code
  - dbtenantCode
oid: 1
scope:
  databases: [unknown]
sources:
  - code:LocalTypeUserController.java:getDbTenantCodeById
  - code:SaaSAuthController.java:getTenantSetting
contract_version: "0.1"
maps_to: cust_company_info.db_tenant_code
also_confused_with:
  - open_sso_channel.app_tenant_code
adjudication: boundary
---

dbTenantCode 是数据租户标识，决定数据隔离；在本主题中以
[[cust_company_info.db_tenant_code]] 为代表字段（其他表如 tenant_setting_config、
cust_project_rel、cust_project_rel 同名字段语义一致）。

## 需求背景

企业 → 租户编码 → 租户配置/SSO 渠道是同一条桥接链：由 custId 反查 db_tenant_code
（getDbTenantCodeById），再查租户配置与统码（[[tenant_setting_by_db_tenant_code]]、
[[list_user_page_tenant_channel_backfill]]）；注册锁维度也使用它（[[register_distributed_lock]]）。

## 版本演进

- v0（草稿）：术语边界来自代码反查链路。

边界：db_tenant_code 为数据租户标识（决定数据隔离）；[[open_sso_channel.app_tenant_code]]
为逻辑租户标识，二者不同层级，不可互换。企业租户编码还用于定位同租户下用户
（cust_company_info.db_tenant_code → sys_user.tenant_code，derived，无物理外键）。
---END FILE---

---FILE: concepts/org_code.md---
---
type: concept
title: orgCode
page_key: org_code
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - org_code
  - ContextHelper.orgCodeKey
oid: 1
scope:
  databases: [unknown]
sources:
  - db:open_sso_channel.org_code
  - code:UserInfoFacade.java:updateCustPerson
contract_version: "0.1"
maps_to: open_sso_channel.org_code
also_confused_with:
  - open_sso_channel.sys_channel
adjudication: boundary
---

orgCode 是同步到 SSO 的机构编码，落在 [[open_sso_channel.org_code]]，代码中经
RpcContext attachment（ContextHelper.orgCodeKey）在调用 SSO 前透传。

## 需求背景

用户/联系人与邮箱同步 SSO 时都要带上机构编码，以保证更新落到正确的 SSO 机构下
（[[update_cust_person_sso_email]]）。

## 版本演进

- v0（草稿）：术语边界来自代码透传点。

边界：orgCode 是机构编码，不是渠道编码本身；不可与 [[sys_channel]] 互换。
---END FILE---

---FILE: concepts/app_id.md---
---
type: concept
title: appId
page_key: app_id
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - app_id
  - dbassAppId
oid: 1
scope:
  databases: [unknown]
sources:
  - db:open_sso_channel.app_id
  - code:SaaSAuthController.java:getTenantSetting
contract_version: "0.1"
maps_to: open_sso_channel.app_id
also_confused_with:
  - tenant_setting_config.dbass_app_id
adjudication: boundary
---

appId 在开放平台渠道语境下指 [[open_sso_channel.app_id]]（开放平台 appId，DB 实测
73d62771729e4ffba7f263cb6012746d）。

## 需求背景

渠道接入开放平台需要 appId；租户配置里另有 DBAss 侧 appId（tenant_setting_config.dbass_app_id），
返回前端前被显式置 null 脱敏。

## 版本演进

- v0（草稿）：术语边界来自 DB 实测与脱敏代码。

边界：open_sso_channel.app_id 是开放平台 appId；tenant_setting_config.dbass_app_id 是 DBAss 侧 appId，
两者来源与用途不同，不可互换（见 [[dbass]]）。
---END FILE---

---FILE: concepts/dbass.md---
---
type: concept
title: DBAss
page_key: dbass
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - dbass
  - DBaaS
  - DbassProvider
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getTenantSetting
  - code:DbassProviderImpl
contract_version: "0.1"
maps_to: tenant_setting_config.dbass_app_id
also_confused_with:
  - open_sso_channel.app_id
adjudication: boundary
---

（document_claim，未证实）文档主张存在通道初始化链路：
SsoSysChannelInitService.initDbassAndSsoConfig(configId) → DBAss 写 dbass appId →
PlatformTenantLineServiceImpl 同步平台线路 → PlatformComponentFacade 调 SSO 通道初始化。
该主张在给定语义分析中为 uncovered，仅作版本演进记录，不作为契约。

DBAss 在本主题中以租户侧接入凭据体现：[[tenant_setting_config.dbass_app_id]]（另有 dbass_private_key）。

## 需求背景

DBAss 能力（本主题中体现为营业执照 OCR / 行业查询）需要租户级接入凭据；
凭据返回前端前必须脱敏（dbassAppId 置 null）。

## 版本演进

- v0（草稿）：术语边界来自代码与脱敏点。
- （document_claim，未证实）initDbassAndSsoConfig / PlatformTenantLineServiceImpl / PlatformComponentFacade 初始化链路未见代码证据，待核实。

边界：本主题中 DbassProvider 实际提供营业执照 OCR（getCompanyIndustry/ocrBizLicense）能力，
与 SSO 渠道初始化并非同一套配置；tenant_setting_config 的 dbass_app_id/dbass_private_key
才是 DBAss 接入凭据，不可与 [[app_id]]（open_sso_channel.app_id）混用。
---END FILE---

---FILE: rules/login_init_cookie.md---
---
type: rule
title: 登录初始化写入企业上下文 Cookie
page_key: login_init_cookie
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - init 写 Cookie
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:init
contract_version: "0.1"
---

SSO 登录初始化成功后，必须把当前企业上下文写入 Cookie 与缓存。

## 需求背景

前端与网关后续请求依赖这些 Cookie/缓存识别当前企业与租户；企业上下文来自
[[cust_company_info.db_tenant_code]]，并与 [[login_user_status_state]] 的 NORMAL 态同步产生。

## 版本演进

- v0（草稿）：规则来自 init 代码证据。

```ground:rule
name: 登录初始化写入企业上下文 Cookie
content: "init 成功后写 fbpccid/fbpcctype/fbpccname(URL编码)/dbtenantCode/fbpcccode 五个 Cookie，并把 companyId/companyType/companyName/companyCode 回填 LoginUser 并写入 Redis。"
impact: "前端与网关后续请求依赖这些 Cookie/缓存识别当前企业与租户。"
field_targets:
  - cust_company_info.db_tenant_code
  - sys_cust_user_rel.is_freeze
evidence: "code_path:SaaSAuthController.java:init"
```

相关：[[login_user_status_state]]、[[cust_company_info]]、[[db_tenant_code]]。
---END FILE---

---FILE: rules/freeze_active_dual_write.md---
---
type: rule
title: 冻结/解冻双写 SSO 与本地关联表
page_key: freeze_active_dual_write
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 冻结解冻双写
oid: 1
scope:
  databases: [unknown]
sources:
  - code:LocalTypeUserController.java:freeze
  - code:LocalTypeUserController.java:active
contract_version: "0.1"
---

冻结与解冻必须先在 SSO 侧生效，再更新本地关联表冻结标记。

## 需求背景

SSO 登录状态与产融关联表冻结标记必须一致，否则出现能登录但无权限 / 相反的不一致；
过滤口径见 [[user_not_frozen]]，状态机见 [[sys_cust_user_rel_freeze_state]]。

## 版本演进

- v0（草稿）：规则来自控制层调用顺序证据。

```ground:rule
name: 冻结/解冻双写 SSO 与本地关联表
content: "freeze 先调 saaSAuthService.freezePerson(custId, idList, companyType) 同步 SSO，再 userFacade.updateListFreezeFlag(..., UserFreezeEnum.FREEZE) 置 sys_cust_user_rel.is_freeze；active 反向。"
impact: "SSO 登录状态与产融关联表冻结标记必须一致，否则出现能登录但无权限/相反的不一致。"
field_targets:
  - sys_cust_user_rel.is_freeze
evidence: "code_path:LocalTypeUserController.java:freeze/active"
```

相关：[[sys_cust_user_rel]]、[[sys_cust_user_rel_freeze_state]]、[[user_not_frozen]]。
---END FILE---

---FILE: rules/multi_company_dedup_default.md---
---
type: rule
title: 多公司列表去重取默认
page_key: multi_company_dedup_default
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 多公司去重
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getCurrentCustList
contract_version: "0.1"
---

用户拥有多家公司时，当前企业列表需按 (companyId + companyType) 去重，重复取默认记录。

## 需求背景

同一企业在多角色下只展示一条，默认企业优先，避免选择公司与后续企业上下文写入
（[[login_init_cookie]]）出现歧义。

## 版本演进

- v0（草稿）：规则来自代码去重逻辑。

```ground:rule
name: 多公司列表去重取默认
content: "getCurrentCustList 按 (companyId+companyType) 去重，重复时取 default_flag='Y' 的记录，其余取首条。"
impact: "同一企业在多角色下只展示一条，默认企业优先。"
field_targets:
  - cust_company_info.id
  - cust_company_info.cust_company_type
evidence: "code_path:SaaSAuthController.java:getCurrentCustList"
```

相关：[[cust_company_info]]、[[login_init_cookie]]。
---END FILE---

---FILE: rules/login_captcha_policy.md---
---
type: rule
title: 登录图形验证码策略
page_key: login_captcha_policy
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 图形验证码策略
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:resolveNeedLoginCaptcha
  - reqdoc:login-captcha-scene
contract_version: "0.1"
---

登录是否需要图形验证码由环境与 SSO 系统渠道配置共同决定。

## 需求背景

文档主张“登录验证码场景：测试环境可配置 SSO 系统 captcha 决定是否需要图形验证码”，
代码已确认：非 qa/qa2 一律需要验证码；qa/qa2 查 [[sys_channel]] 对应 SsoSystemDO.captcha，
captcha==0 可免验证码。生产始终开启，测试环境按渠道配置放开。

## 版本演进

- v0（草稿）：规则同时有代码与需求文档来源（双源）。

```ground:rule
name: 登录图形验证码策略
content: "非 qa/qa2 环境一律需要验证码；qa/qa2 下查 SsoSystemDO.captcha，captcha==0 表示可不加验证码（返回 false），其余（含查询异常）返回 true。"
impact: "仅测试环境允许免图形验证码，生产始终开启。"
field_targets:
  - open_sso_channel.sys_channel
evidence: "code_path:SaaSAuthController.java:resolveNeedLoginCaptcha + reqdoc:login-captcha-scene"
```

相关：[[open_sso_channel]]、[[sys_channel]]、[[tenant_setting_config]]。
---END FILE---

---FILE: rules/register_distributed_lock.md---
---
type: rule
title: 注册分布式锁
page_key: register_distributed_lock
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 注册防重锁
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:register
contract_version: "0.1"
---

注册按“租户 + 手机号”加分布式锁，防止并发重复提交。

## 需求背景

同一租户下同一手机号的并发注册必须串行化，锁维度取 [[cust_company_info.db_tenant_code]]
（见 [[db_tenant_code]]）；密码用 RSA 私钥解密后再落库。

## 版本演进

- v0（草稿）：规则来自代码锁实现。

```ground:rule
name: 注册分布式锁
content: "register 使用 Redis 锁 saas:register:{dbTenantCode}:{cellphone}，未取到锁抛“注册处理中，请勿重复提交”；密码用 RSA 私钥解密。"
impact: "防止同租户同手机并发注册。"
field_targets:
  - cust_company_info.db_tenant_code
evidence: "code_path:SaaSAuthController.java:register"
```

相关：[[cust_company_info]]、[[db_tenant_code]]。
---END FILE---

---FILE: rules/send_login_code_idempotent_lock.md---
---
type: rule
title: 验证码发送幂等锁
page_key: send_login_code_idempotent_lock
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 登录验证码发送限频
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:sendLoginCode
contract_version: "0.1"
---

登录验证码发送以场景 + 业务 id 为 key 抢锁，实现幂等与限频，并在手机号为空时自动降级为邮箱场景。

## 需求背景

短信/邮件发送需要幂等与场景自动降级：LANDED_PHONE→LANDED_EMAIL、resetpassword→resetpasswordemail，
涉及 [[sys_user.mobile]] 与 [[sys_user.email]]。

## 版本演进

- v0（草稿）：规则来自代码锁与场景切换实现。

```ground:rule
name: 验证码发送幂等锁
content: "sendLoginCode 以 scenesType+businessId 作为 key 抢 RedisSmsLock，抢不到抛“调用频率过快”；手机号为空时按场景切换为邮箱场景（LANDED_PHONE→LANDED_EMAIL、resetpassword→resetpasswordemail）。"
impact: "短信/邮件发送幂等与场景自动降级。"
field_targets:
  - sys_user.mobile
  - sys_user.email
evidence: "code_path:SaaSAuthController.java:sendLoginCode"
```

相关：[[sys_user]]、[[update_agw_login_email]]。
---END FILE---

---FILE: rules/list_user_page_tenant_channel_backfill.md---
---
type: rule
title: 租户 SSO 渠道回填用户查询
page_key: list_user_page_tenant_channel_backfill
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 用户列表回填统码
oid: 1
scope:
  databases: [unknown]
sources:
  - code:LocalTypeUserController.java:listUserPage
  - code:LocalTypeUserController.java:getDbTenantCodeById
contract_version: "0.1"
---

用户列表查询需由 custId 反查租户编码，再取租户统码回填 DTO，供下游跨系统查询用户。

## 需求背景

用户列表跨租户/跨 SSO 系统查询依赖该回填：企业 → [[cust_company_info.db_tenant_code]] →
租户统码 [[tenant_setting_config.sso_tenant_chanel]] → userDTO.ssoSysChannel
（术语边界见 [[tenant_sso_chanel]]、[[sys_channel]]）。

## 版本演进

- v0（草稿）：规则来自代码回填链路。

```ground:rule
name: 租户 SSO 渠道回填用户查询
content: "listUserPage 由 custId 反查 cust_company_info.db_tenant_code，再取租户 ssoTenantChanel 写入 userDTO.ssoSysChannel，供下游按租户统码跨系统查询用户。"
impact: "用户列表跨租户/跨 SSO 系统查询依赖该回填。"
field_targets:
  - cust_company_info.db_tenant_code
  - tenant_setting_config.sso_tenant_chanel
evidence: "code_path:LocalTypeUserController.java:listUserPage + getDbTenantCodeById"
```

相关：[[cust_company_info]]、[[tenant_setting_config]]、[[tenant_sso_chanel]]、[[sys_channel]]。
---END FILE---

---FILE: rules/update_cust_person_sso_email.md---
---
type: rule
title: 登录用户信息同步 SSO 邮箱
page_key: update_cust_person_sso_email
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 邮箱同步 SSO
oid: 1
scope:
  databases: [unknown]
sources:
  - code:UserInfoFacade.java:updateCustPerson
contract_version: "0.1"
---

更新用户邮箱后，需在满足条件时把邮箱回写 SSO 侧。

## 需求背景

保证 SSO 侧邮箱与 [[sys_user.email]] 一致：仅当 [[sys_user.sso_user_id]] 非空且 sso_user.email
为空时回写，并带 orgCode RpcContext 透传（[[org_code]]）。

## 版本演进

- v0（草稿）：规则来自代码回写条件。

```ground:rule
name: 登录用户信息同步 SSO 邮箱
content: "updateCustPerson 更新 sys_user 邮箱后，若 sys_user.sso_user_id 非空且 sso_user.email 为空，则回写 sso_user.email（带 orgCode RpcContext 透传）。"
impact: "保证 SSO 侧邮箱与 sys_user 一致。"
field_targets:
  - sys_user.email
  - sys_user.sso_user_id
evidence: "code_path:UserInfoFacade.java:updateCustPerson"
```

相关：[[sys_user]]、[[org_code]]、[[update_agw_login_email]]。
---END FILE---

---FILE: rules/update_agw_login_email.md---
---
type: rule
title: AGW 网关更新邮箱免登录态
page_key: update_agw_login_email
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 网关代更新邮箱
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:updateAgwLoginEmail
contract_version: "0.1"
---

AGW 网关侧更新邮箱接口直接用入参 userId 更新，不校验登录态；普通接口取当前登录用户。

## 需求背景

网关侧可代更新邮箱（[[sys_user.email]]），需注意越权风险；与自助更新
（updateLoginEmail 取当前登录用户）行为不同，两者不可混用。

## 版本演进

- v0（草稿）：规则来自代码实现差异。

```ground:rule
name: AGW 网关更新邮箱免登录态
content: "updateLoginEmail 取当前登录用户；updateAgwLoginEmail 直接以入参 userId 更新邮箱，不校验登录态。"
impact: "网关侧可代更新邮箱，需注意越权风险。"
field_targets:
  - sys_user.email
evidence: "code_path:SaaSAuthController.java:updateAgwLoginEmail"
```

相关：[[sys_user]]、[[update_cust_person_sso_email]]。
---END FILE---

---FILE: rules/get_user_menu_perm_list.md---
---
type: rule
title: 登录后获取菜单权限接口
page_key: get_user_menu_perm_list
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 登录菜单接口
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getUserMenuPermList
  - reqdoc:sso-login-menu-perm
contract_version: "0.1"
---

登录后菜单权限获取接口：SaaSAuthController.getUserMenuPermList(LoginMenuDTO) →
saaSAuthService.getUserMenuPermList。

## 需求背景

文档主张“登录后获取菜单接口：LocalTypeMenuService/UserFacade 返回 LoginMenuDTO”，
代码侧已确认控制层入口 getUserMenuPermList 及其服务调用；菜单数据加载在本次语义分析中
未展开到 LocalTypeMenuService/UserFacade 内部实现。

## 版本演进

- v0（草稿）：规则同时有代码与需求文档来源（双源）。

```ground:rule
name: 登录后获取菜单权限接口
content: "getUserMenuPermList(LoginMenuDTO) 由 SaaSAuthController 暴露，转 saaSAuthService.getUserMenuPermList 返回登录菜单权限。"
impact: "登录后前端菜单与权限入口，依赖当前登录用户与企业上下文（Cookie/缓存）。"
field_targets: []
evidence: "code_path:SaaSAuthController.java:getUserMenuPermList + reqdoc:sso-login-menu-perm"
```

相关：[[login_init_cookie]]、[[login_user_status_state]]。
---END FILE---

---REVIEW: table | 库表字段类型与物理库名缺失---
语义分析只提供了字段语义（meaning），未提供任何字段类型与物理库名。
因此所有 ground:table 的 type 统一写 unknown、scope.databases 写 [unknown]。
请补充每个字段的实际类型（含长度/精度）、是否可空、默认值，以及主题涉及的物理库名。
---END REVIEW---

---REVIEW: enum | StatusEnum 与 cust_person_info.status 写值不一致---
enum_audit 中 cust/enums/StatusEnum.java 的 EFFECTIVE/INVALID 两条判定为 reject：
给定 SSO/登录/用户链路未使用该枚举，cust_person_info.status 实际以字面量 ADD→EFFECT 写入
（SaaSAuthController.makePersonEffect），与 EFFECTIVE/INVALID 不一致。
故本主题不产出 enum 页；如需保留 StatusEnum，请确认其真实使用点，否则应从底稿移除。
---END REVIEW---

---REVIEW: concept | changeCompany 文档链路与代码不符（refuted）---
文档主张“SaaSAuthController.changeCompany → SaaSAuthService.change(ChangeCompanyDTO) → SsoFacade 切换租户上下文并刷新缓存”
为 refuted：代码实际调用 saaSAuthService.getCompanyByUserAndCode(userId, companyId, companyType)、
改写 Cookie、roleFacade.getAuthUrls、setReisUserInfo。已按 prose_only 写入
processes/cust_person_info_status_state.md 的业务叙述，请业务方确认是否修正文档。
---END REVIEW---

---REVIEW: process | 登录链路与通道初始化为 uncovered（document_claim，未证实）---
两条主张在给定语义分析中无代码证据：
(1) SaaS 登录全链路（SaaSAuthService.login → SsoBlackWhiteListService 黑白名单 → SSO token → UserFacade 加载用户 → LocalTypeMenuService 加载菜单）；
(2) SSO/DBAss 通道初始化（SsoSysChannelInitService.initDbassAndSsoConfig → DBAss 写 appId → PlatformTenantLineServiceImpl 同步线路 → PlatformComponentFacade 调 SSO 通道初始化）。
已分别以（document_claim，未证实）标注写入 processes/login_user_status_state.md 与 concepts/dbass.md 的版本演进。
请补充这两个链路的代码位置或修正文档。
---END REVIEW---