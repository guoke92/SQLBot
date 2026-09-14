---FILE: tables/tenant_migarory_log.md ---
---
type: table
title: tenant_migarory_log（迁移/推数流水表）
page_key: tenant_migarory_log
domain: 租户迁移
status: draft
aliases: [迁移日志表, 推数日志表, tenant_migarory_log]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "db:tenant_migarory_log"
  - "code:TenantMigaroryLogDaoImpl.java:87"
  - "code:MigratoryPointServiceImpl.java#pushByLog"
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
contract_version: "0.1"
---

`tenant_migarory_log` 是 [[迁移]] 与 [[同步]]（推数）共用的一条流水线：业务系统把存量数据推进产融（入向）与产融反向把数据推给业务系统（出向）都落这张表，靠 [[迁移|type]] 与 [[同步|direction]] 两个维度区分，不能只按接口名或中文动作名判断归属。表的幂等与重推入口是 `req_no`（唯一键 `uk_req_no`）与 `pushByLog(reqNo)`，重推只覆盖 `direction=OUT` 的记录，见口径 [[outbound_push]] 与 [[failed_migratory_log]]。表名在库中拼写为 `migarory`（非 migratory），引用时须以物理名为准。

```ground:table
table: tenant_migarory_log
fields:
  - name: type
    type: varchar
    desc: "推数/迁移接口标识。入向为迁移 RPC 名称（migratoryTenant/migratoryProject/migratoryCust/migratoryOnTheWayCust，配合 name 中的中文『迁移租户/迁移项目/迁移客户/迁移在途客户信息』）；出向为 RpcPoint 名称（TENANT_SYNC/PROJECT_SYNC/PRODUCT_SYNC/CUST_PRODUCT_SYNC/PROJECT_QUERY）及其校验器 *_SYNC_VALIDATE、syncProduct/syncProject"
    dict: null
  - name: name
    type: varchar
    desc: "业务动作/事件名称。中文族=迁移类接口入向（迁移项目 92213、迁移客户 13228、迁移租户 363、迁移在途客户信息 293、同步产品 640、同步项目 16668）；英文族=事件类型（CREATED/EFFECTED/CHANGED/INVALID/DELETED/QUERY/ACTIVE_CFCA_SIGN/ACTIVE_BS_SIGN）"
    dict: null
  - name: direction
    type: varchar
    desc: "数据方向：IN=外部业务系统调用产融迁移/同步接口（123405 条为主流）；OUT=产融反向推数给业务系统（29764 条），pushByLog 只处理 direction=OUT 的重推"
    dict: null
  - name: status
    type: varchar
    desc: "处理状态：Y=处理成功（145743），N=未成功/待重试（7426，DB 默认 N）。写入点为 BooleanEnum 字典键，非 StatusEnum"
    dict: BooleanEnum
  - name: platform_product_code
    type: varchar
    desc: "推数目标产品编码，一个事件可横向铺开到多个产品（productCodes 数组），与 product_code 的租户开通产品对应"
    dict: null
  - name: req_no
    type: varchar
    desc: "单次推数请求编号，唯一键 uk_req_no；pushByLog(reqNo) 以此为幂等/重推依据"
    dict: null
  - name: req_sn
    type: varchar
    desc: "业务流水号（非唯一），迁移记录里用于关联同批业务"
    dict: null
  - name: batch_no
    type: varchar
    desc: "批次号，用于分批迁移标记；代码链路中未见写入点"
    dict: null
  - name: request
    type: text
    desc: "出/入向报文原文（EventNode JSON），重推时被反序列化成 EventNode"
    dict: null
  - name: response
    type: text
    desc: "推数返回体，logOut 落库"
    dict: null
  - name: data
    type: text
    desc: "迁移数据快照（迁移企业/项目/租户主体内容）"
    dict: null
  - name: message
    type: varchar
    desc: "错误信息（bizErrorMsg 提取 detailMessage 后写入类字段）"
    dict: null
  - name: act_procinst_id
    type: varchar
    desc: "外部审批流程实例ID，用于把审批结果回写到推数记录"
    dict: null
  - name: db_tenant_code
    type: varchar
    desc: "数据租户标识，推数白名单短路判定用（命中 platformPointServiceExcludeDbTenantCode 的租户不产生推数记录）"
    dict: null
```

## 需求背景

迁移期业务系统与产融之间是双向流动：入向把存量企业、人员、项目推到产融，出向把产融侧变更推回业务系统。两侧都需要可追溯、可重推的流水，因此共用一张表；运营与排障时须先用 direction 判定方向、再用 type/name 定位具体动作，否则会把入向迁移量（123405）误读为出向推数量级。

## 版本演进

出向推数逐步引入 RpcPoint 枚举与 `*_SYNC_VALIDATE` 校验器记录；`platform_product_code` 从单产品扩展为一个事件横向铺开到多产品（productCodes 数组）。`status` 默认值 N 充当"待重试池"，是 [[failed_migratory_log]] 与重推链路的判定基础。

相关：[[sync]]、[[迁移]]、[[migratory_log_status]]、[[outbound_push]]、[[cust_company_info]]。

---END FILE---

---FILE: tables/migratory_user_record.md ---
---
type: table
title: migratory_user_record（迁移存量用户记录表）
page_key: migratory_user_record
domain: 租户迁移
status: draft
aliases: [迁移用户记录表, migratory_user_record]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "db:migratory_user_record"
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
  - "code:CustMigratoryService.java#loginAfterEjectMsg"
contract_version: "0.1"
---

本表是"迁移存量用户是否已登录过产融"的判定载体，服务于迁移期 [[migratory_user_first_login]] 的一次性升级提示。记录在迁移落库时创建（`is_login="N"`），登录后由 `/cust-web/migratory/isEjectMsg` 翻转，状态机见 [[migratory_user_login_prompt]]。注意 `user_id` 存的是产融用户ID（FBP），不是 `sys_user` 主键的直接引用。

```ground:table
table: migratory_user_record
fields:
  - name: user_id
    type: varchar
    desc: "迁移存量用户对应的产融用户ID（企业管理员/经办人落库时 person.getUserId()，即 FBP/产融用户ID），非 sys_user 主键直接引用"
    dict: null
  - name: is_login
    type: varchar
    desc: "该迁移用户是否已在产融登录过：N=未登录（5228，首次登录弹升级提示），Y=已登录（1433，不再弹）。迁移落库时硬编码写 \"N\""
    dict: null
  - name: db_tenant_code
    type: varchar
    desc: "数据租户标识，与 user_id 组成迁移用户判定条件"
    dict: null
```

## 需求背景

存量用户首次登录（当前迁移批次内）需弹出『【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务』，且一个用户仅弹一次。产品侧据此要求：迁移落库时就必须为每个迁移人员预置一条"未登录"记录，登录后置为已登录，作为"只弹一次"的唯一依据。

## 版本演进

落库时的 `is_login` 由硬编码 `"N"` 写入，暂无中间态；查询侧以 `user_id + db_tenant_code` 作为组合判定条件。相关规则：[[migratory_user_record_insert]]；口径：[[migratory_user_first_login]]。

---END FILE---

---FILE: tables/argeement_migratory_record.md ---
---
type: table
title: argeement_migratory_record（迁移协议待拉取记录表）
page_key: argeement_migratory_record
domain: 租户迁移
status: draft
aliases: [迁移协议记录表, argeement_migratory_record]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "db:argeement_migratory_record"
  - "code:PlatFormMigratoryApplication.java#setAgreementMigratory"
  - "code:AgreementMigratoryService.java#pull"
contract_version: "0.1"
---

迁移时不为客户直接搬协议原文，而是先生成"待拉取清单"，再由定时任务按产品/客户分组去业务系统拉取协议文件并归档。本表既是清单也是重试状态机，见 [[agreement_pull_status]]、口径 [[pending_agreement_pull]] 与规则 [[agreement_migratory_init]]、[[agreement_pull_throttle]]。

```ground:table
table: argeement_migratory_record
fields:
  - name: cust_id
    type: varchar
    desc: "协议归属客户，与 platform_product_code、agreement_type 一起构成去重键（count 为 0 才插入）"
    dict: null
  - name: platform_product_code
    type: varchar
    desc: "协议所属产品编码，拉取任务按产品分组"
    dict: null
  - name: agreement_type
    type: varchar
    desc: "协议类型：CA授权(CFCA/BS)、产品协议、企业授权书、用户协议、隐私政策（AgreementDocType）"
    dict: AgreementDocType
  - name: status
    type: varchar
    desc: "协议拉取状态：N=待拉取（字典键 BooleanEnum.no），Y=已拉取/已确认无协议"
    dict: BooleanEnum
  - name: pull_num
    type: int
    desc: "已拉取次数，pull_num<pullNum(默认20) 才继续拉取；失败时 +1 且 status 保持 N"
    dict: null
  - name: is_new
    type: varchar
    desc: "新/旧渠道协议标记，代码用 isNew.name() 落库（与同表 status 用 getDictKey 写法不一致）"
    dict: null
  - name: enable
    type: varchar
    desc: "拉取任务过滤条件之一，enable='Y' 的记录才参与本轮拉取"
    dict: null
  - name: agreement_path
    type: varchar
    desc: "协议文件落地路径，path 非空才 migrateConctract 写入合同记录"
    dict: null
  - name: agreement_no
    type: varchar
    desc: "协议/合同编号，与客户一起判重，已存在同客户+同编号的跳过归档"
    dict: null
```

## 需求背景

需求要求迁移企业协议不丢失：CA 授权书、产品协议、企业授权书、用户协议、隐私政策五类协议需在迁移后逐步从业务系统拉回并归档，其中已确认业务系统无该协议的记录也允许置为已完成，不得无限重试。

## 版本演进

初始 `status='N'`、`pull_num=0`、`is_new=Y`；拉取成功后 `status='Y'`，失败仅 `pull_num+1` 并保持 N 等下一轮。`enable` 与 `excludeProductCode` 用于灰度与例外产品隔离。`is_new` 的落库写法与 `status` 不一致（`isNew.name()` vs `getDictKey`），属历史遗留。

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（客户企业表）
page_key: cust_company_info
domain: 租户迁移
status: draft
aliases: [客户企业表, cust_company_info]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "db:cust_company_info"
  - "code:PlatFormMigratoryApplication.java#setCompany"
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
  - "code:PlatFormMigratoryApplication.java#openCa"
  - "code:CustAccessAsyncApplication.java#openCa"
contract_version: "0.1"
---

迁移落库的企业主体表。迁移侧对它的核心约束是"来源可识别（cust_source）、状态可映射（cust_status→cust_build_status/check_status）、旧数据不回溯覆盖（update_time）"。相关规则：[[migratory_source_company]] 口径下的 [[migratory_company_status_mapping]]、[[no_backtrack_overwrite]]、[[migratory_company_redis_lock]]、[[migratory_open_ca_idempotent]]。

```ground:table
table: cust_company_info
fields:
  - name: name
    type: varchar
    desc: "企业名称，与 db_tenant_code、certification_no 组成迁移防重锁 key"
    dict: null
  - name: certification_no
    type: varchar
    desc: "统一社会信用代码，AMS 迁移去重首选条件（为空时按名称模糊反查）"
    dict: null
  - name: db_tenant_code
    type: varchar
    desc: "数据租户标识，迁移防重锁与已存在企业查询的隔离边界"
    dict: null
  - name: tenant_flg_en
    type: varchar
    desc: "项目标识/产融渠道码，与数据库租户标识、逻辑租户标识均不同"
    dict: null
  - name: cust_source
    type: varchar
    desc: "企业来源，迁移落库固定写 CustSourceEnum.MIGRATORY"
    dict: CustSourceEnum
  - name: cust_status
    type: varchar
    desc: "迁移时直接采用上游推送值：EFFECT=已生效、ADD=在途（未生效）"
    dict: null
  - name: cust_build_status
    type: varchar
    desc: "迁移映射：cust_status=EFFECT→BUILD_SUCCESS；cust_status=ADD→INIT"
    dict: null
  - name: check_status
    type: varchar
    desc: "迁移映射：cust_status=EFFECT→CUST_CHECK_PASS；cust_status=ADD→置 null"
    dict: null
  - name: need_register_ca
    type: varchar
    desc: "是否开通CFCA：先写上游 openCa，随后被 \"Y\"/\"N\" 字面量覆盖；openCa 链路开启后写 ca_register_status=\"Y\""
    dict: null
  - name: ca_register_status
    type: varchar
    desc: "CFCA 注册状态，非 AMS 产品开 CA 的幂等判定列；'Y' 表示已注册"
    dict: null
  - name: bs_register_status
    type: varchar
    desc: "BS 签章注册状态，AMS 产品开 CA 的幂等判定列；AMS 开通后与 ca_register_status 同时置 'Y'"
    dict: null
  - name: migarory_auth_aggrement_flag
    type: varchar
    desc: "迁移授权书标记：新渠道(Y) 时 supplement_flag 置 N（无需补签），旧渠道(N) 时 supplement_flag 置 Y（需展示补签）"
    dict: null
  - name: auth_aggrement_supplement_flag
    type: varchar
    desc: "授权书补签标记，与 migarory_auth_aggrement_flag 成对写入，控制是否展示补签入口"
    dict: null
  - name: update_time
    type: datetime
    desc: "与上游 updateTime 比较，判断是否『以系统为准，不更新』"
    dict: null
```

## 需求背景

迁移要在"不覆盖产融侧已更新数据"的前提下把存量企业搬进来：同一租户同企业只能有一条有效记录，在途企业不能误入生效口径，签章注册与授权书补签也不能因重复迁移被反复触发。

## 版本演进

`cust_build_status`/`check_status` 由 `cust_status` 单向映射得出，迁移不引入独立状态机；签章相关列随签章中台对接从 `need_register_ca` 演进为 `ca_register_status`/`bs_register_status` 双列判定，AMS 与非 AMS 走不同幂等列。

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info（客户人员表）
page_key: cust_person_info
domain: 租户迁移
status: draft
aliases: [客户人员表, cust_person_info]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "db:cust_person_info"
  - "code:PlatFormMigratoryApplication.java#setPersonAdm"
  - "code:PlatFormMigratoryApplication.java#setPersonOper"
contract_version: "0.1"
---

迁移时企业管理员与经办人的落库载体。人员侧两条硬约束：在途企业的管理员/经办人状态一律强制初始化，不复用上游推送状态（[[on_the_way_person_status_force]]）；手机号为加密列，去重与覆盖必须走加密匹配（[[migratory_person_phone_encrypt_match]]）。

```ground:table
table: cust_person_info
fields:
  - name: phone
    type: varchar
    desc: "手机号，加密列：以 encryptAndBase64Str(phone) 后 eq 查询，已存在则先删旧记录再插"
    dict: null
  - name: company_type
    type: varchar
    desc: "企业类型，与手机号一起用于迁移人员的增量过滤条件"
    dict: null
  - name: user_type
    type: varchar
    desc: "人员用户类型，与手机号、company_type 共同组成人员去重条件"
    dict: null
  - name: status
    type: varchar
    desc: "人员状态，company.cust_status=ADD 时强制置 CustPersonStatusConstant.ADD，不采信上游推送值"
    dict: null
  - name: ref_cust_company_info
    type: varchar
    desc: "所属企业引用，落库时随企业主体写入"
    dict: null
```

## 需求背景

存量企业迁移时人员必须与企业状态一致：在途企业的人员不得显示为已生效；AMS 已有建档时，人员按手机号+企业类型+用户类型过滤出增量并走客户变更流程补齐。

## 版本演进

人员去重条件由早期字段比对演进为加密手机号匹配；人员状态由"采信上游"改为"按企业状态强制覆写"。

---END FILE---

---FILE: tables/tenant_setting_config.md ---
---
type: table
title: tenant_setting_config（租户配置表）
page_key: tenant_setting_config
domain: 租户迁移
status: draft
aliases: [租户配置表, tenant_setting_config]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "db:tenant_setting_config"
  - "code:MigratoryPointServiceImpl.java#push"
  - "code:CustMigratoryService.java#loginAfterEjectMsg"
contract_version: "0.1"
---

本表在迁移主题中只作为"外部配置来源"出现：推数白名单（[[push_whitelist_tenant]]）按数据租户标识短路，登录升级提示的品牌名取自租户配置（[[贴牌]]）。

```ground:table
table: tenant_setting_config
fields:
  - name: db_tenant_code
    type: varchar
    desc: "数据租户标识，platformPointServiceExcludeDbTenantCode 命中的租户直接 return，不推数"
    dict: null
  - name: band_name
    type: varchar
    desc: "贴牌名（代码中 bandName/platName），用于展示与推送字段填充"
    dict: null
```

## 需求背景

推数需要按租户灰度：特定租户在迁移期不参与推送；登录升级提示文案需要带贴牌名称，名称为空时的兜底行为需求未明确。

## 版本演进

白名单已从硬编码演进为租户配置驱动；贴牌名仅作为展示/推送字段存在，尚无独立的"假贴牌/二级贴牌"标识字段（见 REVIEW）。

---END FILE---

---FILE: processes/migratory_user_login_prompt.md ---
---
type: process
title: 迁移存量用户登录提示状态机
page_key: migratory_user_login_prompt
domain: 租户迁移
status: draft
aliases: [首登弹提示状态机, is_login 状态机]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:CustMigratoryService.java#loginAfterEjectMsg"
  - "code:CustMigratoryController.java#isEjectMsg"
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
  - "db:migratory_user_record"
contract_version: "0.1"
---

状态机只有两个状态，但入口与出口都很硬：迁移落库时一定是 N，登录后的 `isEjectMsg` 判定命中才翻转为 Y，翻转后同一用户不再弹。它同时是企业侧与用户侧的"迁移已完成提示"开关，见口径 [[migratory_user_first_login]]、规则 [[migratory_user_record_insert]]。

```ground:process
name: 迁移存量用户登录提示状态
field: migratory_user_record.is_login
states:
  - value: N
    label: "迁移存量用户、尚未登录（可弹升级提示）"
    source: db_dist
  - value: Y
    label: "已登录过（不再弹提示）"
    source: db_dist
transitions:
  - from: N
    event: "登录后调用 /cust-web/migratory/isEjectMsg（isExist 且 hasNotLogin）"
    to: Y
    evidence: "code_path:CustMigratoryService.java#loginAfterEjectMsg"
  - from: 新增
    event: '迁移落库时为每个迁移人员创建记录并写 is_login="N"'
    to: N
    evidence: "code_path:PlatFormMigratoryApplication.java#migratoryCust"
```

## 需求背景

存量用户首次登录（当前迁移批次内）弹出『【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务』，一个用户仅弹一次。因此状态必须由服务端持久化，不能依赖前端本地标记；记录不存在视为非迁移用户，不弹提示。

## 版本演进

`is_login` 初值硬编码 `"N"`；查询条件由单 user_id 演进为 `user_id + db_tenant_code`（见 [[tenant_code]]）。记录不存在时不补建（不回溯弹窗）。

---END FILE---

---FILE: processes/migratory_log_status.md ---
---
type: process
title: 推数/迁移记录处理状态机
page_key: migratory_log_status
domain: 租户迁移
status: draft
aliases: [推数记录状态机, tenant_migarory_log.status 状态机]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:TenantMigaroryLogDaoImpl.java:87"
  - "code:MigratoryPointServiceImpl.java#pushByLog"
  - "db:tenant_migarory_log"
contract_version: "0.1"
---

流水行的处理状态：落库默认 N，`logOut` 回写 BooleanEnum 字典键置 Y；未成功的行不会被自动丢弃，而是作为重试池由 `pushByLog` 按 `reqNo` 再推一次。相关口径：[[failed_migratory_log]]、[[outbound_push]]、[[push_whitelist_tenant]]。

```ground:process
name: 推数/迁移记录处理状态
field: tenant_migarory_log.status
states:
  - value: N
    label: "未成功/待重试（DB 默认 N）"
    source: db_dist
  - value: Y
    label: "处理成功"
    source: db_dist
transitions:
  - from: N
    event: "推数执行并 logOut 回写（BooleanEnum 字典键）"
    to: Y
    evidence: "code_path:TenantMigaroryLogDaoImpl.java:87"
  - from: N
    event: "按 reqNo 重新推送 pushByLog（仅 direction=OUT 且非 *_SYNC_VALIDATE）"
    to: Y
    evidence: "code_path:MigratoryPointServiceImpl.java#pushByLog"
```

## 需求背景

迁移/推数期业务系统偶发不可用，失败记录必须可追溯且可重放；重放必须幂等（同一 `req_no` 不产生重复推送），且不得把入向迁移记录与出向校验器记录纳入重推范围。

## 版本演进

状态值从多状态收敛为布尔语义（BooleanEnum 字典键 Y/N），DB 默认值 N 使"漏回写"天然进入待重试集合；重推入口统一收敛到 `pushByLog`。

---END FILE---

---FILE: processes/agreement_pull_status.md ---
---
type: process
title: 迁移协议拉取状态机
page_key: agreement_pull_status
domain: 租户迁移
status: draft
aliases: [协议拉取状态机, argeement_migratory_record.status 状态机]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:AgreementMigratoryService.java#pull"
  - "code:AgreementMigratoryService.java#updateAgreement"
  - "code:AgreementMigratoryService.java#updateAgreementPullNum"
  - "code:AgreementMigratoryService.java#syncAgreementDoc"
  - "db:argeement_migratory_record"
contract_version: "0.1"
---

协议记录的拉取状态机：N 是待办，Y 是终态（拉到、或确认业务系统没有、或已通过推送同步补齐）。N 状态允许通过 `pull_num` 累加多次重试，直到达到上限（默认 20）。相关：[[pending_agreement_pull]]、[[agreement_pull_throttle]]、[[agreement_file_contract_archive]]。

```ground:process
name: 迁移协议拉取状态
field: argeement_migratory_record.status
states:
  - value: N
    label: "待拉取（BooleanEnum.no）"
    source: code_enum
  - value: Y
    label: "已拉取完成 / 客户端确认无该协议"
    source: code_enum
transitions:
  - from: N
    event: "定时任务 pull() 按产品+客户分组拉取到协议并写回"
    to: Y
    evidence: "code_path:AgreementMigratoryService.java#updateAgreement"
  - from: N
    event: "拉取失败（pull_num+1，状态保持 N，等待下一轮）"
    to: N
    evidence: "code_path:AgreementMigratoryService.java#updateAgreementPullNum"
  - from: N
    event: "协议推送同步 syncAgreementDoc"
    to: Y
    evidence: "code_path:AgreementMigratoryService.java#syncAgreementDoc"
```

## 需求背景

迁移时只登记"待拉取清单"，协议文件在迁移后按批补拉并归档；业务系统明确无该协议时也必须能置为完成，避免清单永久滞留。

## 版本演进

重试由无限重试收敛为 `pull_num < pullNum(默认20)` 节流；状态机的出口从"仅拉取成功"扩展出"客户端确认无协议"与"推送同步"两条完成路径。

---END FILE---

---FILE: calibers/pending_agreement_pull.md ---
---
type: caliber
title: 待拉取协议集合
page_key: pending_agreement_pull
domain: 租户迁移
status: draft
aliases: [待拉取协议口径, status=N 协议集合]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:AgreementMigratoryService.java#pull"
contract_version: "0.1"
---

本口径决定"这一轮要去业务系统拉哪些协议"，是一个多条件叠加的集合，不是简单单项过滤：状态为 N 只是必要条件，还需 enable='Y'、未超过重试上限、且不属于排除产品。口径实现见 [[agreement_pull_throttle]]，状态流转见 [[agreement_pull_status]]。

```ground:caliber
name: 待拉取协议集合
predicate: "argeement_migratory_record.status = 'N'"
scope: "协议拉取定时任务 pull()：叠加 enable='Y'、pull_num < pullNum(默认20)、排除 excludeProductCode 产品"
evidence: "code:AgreementMigratoryService.java#pull"
```

## 需求背景

迁移协议需要按产品分批、按客户分组回捞，控制对业务系统接口的调用频次；被排除的产品在迁移期不应产生拉取流量。

## 版本演进

过滤条件由 status 单项演进为四项叠加；`pullNum` 默认 20 作为失败退出阈值，达到上限后记录保持 N 但不再被选中（属人工介入场景）。

---END FILE---

---FILE: calibers/migratory_user_first_login.md ---
---
type: caliber
title: 存量迁移用户首登提示口径
page_key: migratory_user_first_login
domain: 租户迁移
status: draft
aliases: [首登弹提示口径, is_login=N 口径]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:CustMigratoryService.java#loginAfterEjectMsg"
  - "code:CustMigratoryController.java#isEjectMsg"
  - "db:migratory_user_record"
contract_version: "0.1"
---

判定"该用户是否应弹升级提示"的口径：记录存在且 `is_login='N'` 才弹，弹完立即置 Y。数据分布上未登录 5228 条、已登录 1433 条，说明多数迁移用户尚未完成首登。状态流转见 [[migratory_user_login_prompt]]。

```ground:caliber
name: 存量迁移用户首登提示口径
predicate: "migratory_user_record.is_login = 'N'"
scope: "登录后 isEjectMsg 判定：记录存在且未登录才弹『平台已升级…』，弹后置 Y"
evidence: "code:CustMigratoryService.java#loginAfterEjectMsg + db(N:5228/Y:1433) + reqdoc:migratory-first-login-eject-msg"
```

## 需求背景

存量用户首次登录（当前迁移批次内）弹出『【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务』，一个用户仅弹一次。贴牌名称取自租户配置（见 [[贴牌]]），文案中的名称缺失时的兜底行为需求未明确。

## 版本演进

由"每次登录都提示"演进为"仅弹一次"，判定依据由内存/前端标记改为服务端 `is_login` 持久列。

---END FILE---

---FILE: calibers/migratory_source_company.md ---
---
type: caliber
title: 迁移来源企业
page_key: migratory_source_company
domain: 租户迁移
status: draft
aliases: [迁移企业口径, cust_source=MIGRATORY]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
contract_version: "0.1"
---

所有经迁移接口落库的企业统一打上来源标记，用于把迁移企业同平台建档、邀请建档区分开，是迁移范围统计与批量处理的基础口径。业务状态另行由 [[on_the_way_company]] 区分。

```ground:caliber
name: 迁移来源企业
predicate: "cust_company_info.cust_source = 'MIGRATORY'"
scope: "迁移接口落库企业统一标记来源，区别于平台建档/邀请建档"
evidence: "code:PlatFormMigratoryApplication.java#setCompany"
```

## 需求背景

迁移企业需要与平台自建企业区分，以便后续批量补签授权书、批量拉取协议、统计迁移进度。

## 版本演进

来源标记由代码固定写入枚举值，未开放给上游指定；迁移来源企业的后续治理动作（补签、协议）均由该标记驱动。

---END FILE---

---FILE: calibers/on_the_way_company.md ---
---
type: caliber
title: 在途（未生效）迁移企业
page_key: on_the_way_company
domain: 租户迁移
status: draft
aliases: [在途企业口径, cust_status=ADD]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
  - "code:PlatFormMigratoryApplication.java#setPersonAdm"
  - "code:PlatFormMigratoryApplication.java#setPersonOper"
contract_version: "0.1"
---

在途口径覆盖企业主体、人员、影像三条链路：企业建档状态 INIT、审核状态 null、人员状态强制 ADD、影像不接收授权书（CATGID_A0004 跳过）。与生效企业（EFFECT→BUILD_SUCCESS + CUST_CHECK_PASS）走完全不同分支，详见 [[在途]]、[[migratory_company_status_mapping]]、[[on_the_way_person_status_force]]。

```ground:caliber
name: 在途（未生效）迁移企业
predicate: "cust_company_info.cust_status = 'ADD'"
scope: "cust_build_status 置 INIT、check_status 置 null；人员 status 强制置 CustPersonStatusConstant.ADD，不采信上游推送状态"
evidence: "code:PlatFormMigratoryApplication.java#setCompany,#setPersonAdm,#setPersonOper"
```

## 需求背景

上游业务系统里"已建档未生效"的企业推过来时，不能直接进入产融生效口径（否则会误开通产品、误进入审核通过集合），需保持与上游一致的"在途"语义。

## 版本演进

早期由上游推送状态直落，现改为按 `cust_status` 派生本地状态并对人员状态强制覆写。

---END FILE---

---FILE: calibers/outbound_push.md ---
---
type: caliber
title: 出向推数口径
page_key: outbound_push
domain: 租户迁移
status: draft
aliases: [推数口径, direction=OUT]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:MigratoryPointServiceImpl.java#pushByLog"
  - "db:tenant_migarory_log"
contract_version: "0.1"
---

出向推数的判定口径：`direction='OUT'` 且 type 不含 `SYNC_VALIDATE`。数据量上入向 123405 条远大于出向 29764 条，因此不能用记录数判断迁移与同步的业务重要性。该口径是 [[failed_migratory_log]] 重试的前置条件。

```ground:caliber
name: 出向推数口径
predicate: "tenant_migarory_log.direction = 'OUT'"
scope: "pushByLog 只重推 OUT 方向、且 type 不含 SYNC_VALIDATE 的记录"
evidence: "code:MigratoryPointServiceImpl.java#pushByLog + db(IN:123405/OUT:29764)"
```

## 需求背景

推数失败需要能按请求号重放，但校验器类记录（`*_SYNC_VALIDATE`）只反映校验结果，不承载可重放的业务载荷，重放会污染业务系统，须排除在口径外。

## 版本演进

早期重推未区分方向与校验器，现通过 direction + type 双条件收窄；详见 [[同步]]。

---END FILE---

---FILE: calibers/failed_migratory_log.md ---
---
type: caliber
title: 未成功推数/迁移记录
page_key: failed_migratory_log
domain: 租户迁移
status: draft
aliases: [待重试记录口径, status=N 流水]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:TenantMigaroryLogDaoImpl.java:87"
  - "db:tenant_migarory_log"
contract_version: "0.1"
---

以默认值 N 表征的"待重试集合"（7426 条）。此口径同时是排查口径与重试口径，但仅与 [[outbound_push]] 取交集后才构成可重推集合。状态流转见 [[migratory_log_status]]。

```ground:caliber
name: 未成功推数/迁移记录
predicate: "tenant_migarory_log.status = 'N'"
scope: "默认值 N，作为待重试集合（7426 条）"
evidence: "db+code:TenantMigaroryLogDaoImpl.java:87"
```

## 需求背景

状态默认值必须能表达"未成功"，使回写失败、进程中断等异常天然落入待重试集合，避免漏推且无法发现。

## 版本演进

由显式写入失败状态演进为 DB 默认值 + 成功才回写 Y 的写法；同一字段的字典键来自 BooleanEnum，见 [[migratory_log_status]]。

---END FILE---

---FILE: calibers/push_whitelist_tenant.md ---
---
type: caliber
title: 推数白名单租户
page_key: push_whitelist_tenant
domain: 租户迁移
status: draft
aliases: [推数白名单口径, platformPointServiceExcludeDbTenantCode]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:MigratoryPointServiceImpl.java#push"
  - "code:MigratoryPointServiceImpl.java#call"
contract_version: "0.1"
---

用于灰度与隔离：命中白名单配置的数据租户在执行推数前直接 return，既不推送也不产生流水记录，因此该租户在 [[failed_migratory_log]] 与出向统计中都不可见。

```ground:caliber
name: 推数白名单租户
predicate: "tenant_setting_config.db_tenant_code = '<白名单值>'"
scope: "platformPointServiceExcludeDbTenantCode 命中的租户直接 return，不推数"
evidence: "code:MigratoryPointServiceImpl.java#push"
```

## 需求背景

迁移期间部分租户的业务系统尚未准备好接收出向数据，需要按租户粒度暂停推数而不影响其他租户。

## 版本演进

由代码内固定列表演进为配置项（`tenant_setting_config`）驱动；白名单命中无流水留痕，排障时须先确认配置再怀疑推送链路。

---END FILE---

---FILE: concepts/迁移.md ---
---
type: concept
title: 迁移
page_key: 迁移
domain: 租户迁移
status: draft
aliases: [migratory, 迁移租户, 迁移项目, 迁移客户, 迁移在途客户信息, migratoryTenant, migratoryProject, migratoryCust, migratoryOnTheWayCust]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "db:tenant_migarory_log"
  - "code:PlatFormMigratoryProvider.java"
contract_version: "0.1"
maps_to: tenant_migarory_log.type
field_targets:
  - tenant_migarory_log.type
  - tenant_migarory_log.name
  - tenant_migarory_log.direction
adjudication: boundary
also_confused_with:
  - 同步
  - syncProduct
  - PROJECT_SYNC
boundary: "『迁移』=业务系统把存量数据推到产融的一次性入向接口（direction=IN，PlatFormMigratoryProvider）；『同步/推数』=产融反向推给业务系统的出向事件（direction=OUT，RpcPoint）。二者共用 tenant_migarory_log，必须靠 direction+type 区分，不能按中文名混用"
---

迁移指业务系统把存量企业、人员、项目、在途客户一次性推进产融的入向接口族（`migratoryTenant`/`migratoryProject`/`migratoryCust`/`migratoryOnTheWayCust`），落库时 `direction=IN`。它与 [[同步]] 共用 [[tenant_migarory_log]]，因此本词条的唯一判定依据是 direction+type，而不是接口中文名。

## 需求背景

迁移是"一次性搬存量"，与"持续双向同步"是两类数据流；需求中的"迁移租户/迁移项目/迁移客户"是入向动作名称，不能与出向 `*_SYNC` 事件混为一谈。迁移企业的落库规则见 [[migratory_company_status_mapping]]。

## 版本演进

迁移接口从单一迁移租户扩展为租户/项目/客户/在途客户四类；在途客户的引入使迁移范围覆盖未生效企业，见 [[在途]]。

---END FILE---

---FILE: concepts/同步.md ---
---
type: concept
title: 同步（推数）
page_key: 同步
domain: 租户迁移
status: draft
aliases: [推数, push, syncProduct, syncProject, TENANT_SYNC, PROJECT_SYNC, PRODUCT_SYNC]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "db:tenant_migarory_log"
  - "code:MigratoryPointServiceImpl.java#pushByLog"
contract_version: "0.1"
maps_to: tenant_migarory_log.direction
field_targets:
  - tenant_migarory_log.direction
  - tenant_migarory_log.type
adjudication: boundary
also_confused_with:
  - 迁移
boundary: "出向推数以 direction=OUT 标识，含 *_SYNC_VALIDATE 校验器记录；迁移类记录 direction=IN。数据量上 IN 远大于 OUT，不能按记录数判断业务重要性"
---

同步（推数）指产融把侧写数据反向推给业务系统的出向事件，含 `TENANT_SYNC`/`PROJECT_SYNC`/`PRODUCT_SYNC`/`CUST_PRODUCT_SYNC`/`PROJECT_QUERY` 以及 `*_SYNC_VALIDATE` 校验器记录，`direction=OUT`，可重推。与 [[迁移]] 的边界见口径 [[outbound_push]]。

## 需求背景

出向推数需要可重放与可灰度：失败记录按 `req_no` 重推（[[failed_migratory_log]]），特定租户按白名单短路（[[push_whitelist_tenant]]）。

## 版本演进

事件集合从少数同步点扩展出查询类与校验器类记录；重推范围收敛为 OUT 且非校验器。

---END FILE---

---FILE: concepts/租户标识.md ---
---
type: concept
title: 租户标识
page_key: 租户标识
domain: 租户迁移
status: draft
aliases: [dbTenantCode, db_tenant_code, tenantCode]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
  - "code:MigratoryPointServiceImpl.java#push"
contract_version: "0.1"
maps_to: cust_company_info.db_tenant_code
field_targets:
  - cust_company_info.db_tenant_code
  - cust_company_info.tenant_flg_en
  - tenant_setting_config.db_tenant_code
adjudication: boundary
also_confused_with:
  - app_tenant_code
  - tenant_id
  - tenant_flg_en
boundary: "db_tenant_code=数据租户标识（业务数据隔离边界，迁移/推数/锁键都用它）；app_tenant_code=逻辑租户标识（DB 分布仅 base/common）；tenant_id=租户配置主键（查租户产品用）；tenant_flg_en=项目标识/产融渠道码（存于 cust_company_info.tenant_flg_en）"
---

迁移链路里所有"租户"实际上指数据租户标识：防重锁 key、已存在企业查询、推数白名单、迁移用户记录判定都使用它。它不是逻辑租户、不是租户配置主键、也不是项目标识。

## 需求背景

多租户隔离要求迁移数据写入与查询不得跨租户；锁与幂等判定必须包含租户维度，否则不同租户的同名企业会被误判重复。

## 版本演进

租户维度由早期仅用于数据分布，逐步成为迁移锁、推数白名单、用户记录判定的统一隔离键。

---END FILE---

---FILE: concepts/在途.md ---
---
type: concept
title: 在途
page_key: 在途
domain: 租户迁移
status: draft
aliases: [在途企业, 在途客户, migratoryOnTheWayCust, 迁移在途客户信息]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
  - "code:PlatFormMigratoryApplication.java#setPersonAdm"
contract_version: "0.1"
maps_to: cust_company_info.cust_status
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.cust_build_status
  - cust_company_info.check_status
adjudication: boundary
also_confused_with:
  - EFFECT 生效企业
boundary: "在途=迁移时 cust_status='ADD' 的企业：建档状态 INIT、审核状态 null、人员状态强制 ADD、影像不接收授权书（CATGID_A0004 跳过）；与生效迁移企业（EFFECT→BUILD_SUCCESS+CUST_CHECK_PASS）走不同分支"
---

在途描述迁移时"已建档但未生效"的企业，是 `cust_status='ADD'` 的派生语义，会影响企业建档状态、审核状态、人员状态与影像接收四条链路。判定与规则见 [[on_the_way_company]]、[[migratory_company_status_mapping]]、[[on_the_way_person_status_force]]。

## 需求背景

上游建档流程存在"先建档、后审核生效"的阶段，迁移不能把此阶段的企业当作已生效企业处理。

## 版本演进

在途分支从仅映射企业状态，扩展为同时强制覆写人员状态、跳过授权书影像接收。

---END FILE---

---FILE: concepts/贴牌.md ---
---
type: concept
title: 贴牌
page_key: 贴牌
domain: 租户迁移
status: draft
aliases: [品牌, bandName, platName]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:CustMigratoryService.java#loginAfterEjectMsg"
  - "code:PlatFormMigratoryApplication.java#openCa"
contract_version: "0.1"
maps_to: tenant_setting_config.band_name
field_targets:
  - tenant_setting_config.band_name
  - cust_company_info.tenant_flg_en
adjudication: boundary
also_confused_with:
  - app_tenant_code
  - tenant_flg_en
boundary: "代码中贴牌名仅作为展示/推送字段出现（tenantDTO.getBandName() 填 PlatClientOpenCaReq.brand；租户配置 platName 拼登录提示语）；需求侧『假贴牌/二级贴牌』无独立字段与标识，只有 app_tenant_code、tenant_flg_en 等近似字段，属 REVIEW"
---

在迁移主题中，贴牌只作为展示与推送字段存在：登录升级提示文案里的品牌名、开 CA 推送请求中的 `brand`。它没有独立的标识字段，因此不能用来做业务分支判断，见 [[tenant_code]] 的边界说明与 [[migratory_user_first_login]]。

## 需求背景

升级提示需带客户看到的品牌名；需求中提到的"假贴牌/二级贴牌"若需落地为标识，当前表结构尚不支撑（见页末 REVIEW）。

## 版本演进

贴牌名来源由单一配置项演进为租户配置读取；仍无二级贴牌维度。

---END FILE---

---FILE: concepts/产品编码.md ---
---
type: concept
title: 产品编码
page_key: 产品编码
domain: 租户迁移
status: draft
aliases: [platformProductCode, productAppId, productCode]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "db:tenant_migarory_log"
  - "code:MigratoryPointServiceImpl.java#deduceProductCodes"
  - "code:PlatFormMigratoryApplication.java#setAgreementMigratory"
contract_version: "0.1"
maps_to: tenant_migarory_log.platform_product_code
field_targets:
  - tenant_migarory_log.platform_product_code
  - argeement_migratory_record.platform_product_code
adjudication: boundary
also_confused_with:
  - platformProductId
  - tenant_product.id
  - productId
boundary: "platformProductCode/productAppId 是字符串产品码（AMS/ACFLOW/ORDER…），用于推数与协议类型分支；platformProductId、cust_project_rel.product_id 是数值主键。setCustProjectRel 中仅金融机构角色才把 product_id 换成 tenant_product.id"
---

产品编码在迁移里决定三件事：推数落到哪些业务系统（[[push_product_scope_deduce]]）、协议按什么类型初始化和拉取（[[agreement_migratory_init]]）、AMS 走哪条去重分支（[[ams_migratory_dedup]]）。它是字符串业务码，与数值主键类字段不可互换。

## 需求背景

一个迁移事件可能同时涉及多个产品（productCodes 数组横向铺开），未指定时需按租户已开通产品推导。

## 版本演进

由单一产品编码扩展为数组式多产品推数；AMS 由普通产品演进出特殊的合并与签章分支。

---END FILE---

---FILE: rules/migratory_company_redis_lock.md ---
---
type: rule
title: 迁移企业防重锁
page_key: migratory_company_redis_lock
domain: 租户迁移
status: draft
aliases: [迁移企业防重, 企业迁移锁]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
contract_version: "0.1"
---

同一租户下同名同证件企业的迁移是串行化的：先抢 Redis 锁再落库，抢不到直接抛 `SyncException`（『迁移企业信息重复同步』），方法级事务回滚，不留半成品数据。锁键包含租户维度，见 [[tenant_code]]。

```ground:rule
name: 迁移企业防重锁
content: "迁移企业加 Redis 锁，key = dbTenantCode + '_' + companyName + '_' + socialUnifiedCode；获取失败直接抛 SyncException『迁移企业信息重复同步』，方法级 @Transactional 回滚"
impact: "保证同一租户下同名同证件企业不被并发/重复迁移"
field_targets:
  - cust_company_info.db_tenant_code
  - cust_company_info.name
  - cust_company_info.certification_no
evidence: "code:PlatFormMigratoryApplication.java#migratoryCust"
```

## 需求背景

业务系统在迁移期可能重发迁移报文，产融侧必须保证幂等，不能产生两条企业主体或一条半成品主体。

## 版本演进

由数据库唯一约束兜底演进为 Redis 前置锁 + 事务回滚，减少无效写入与脏数据。

相关：[[cust_company_info]]、[[ams_migratory_dedup]]。

---END FILE---

---FILE: rules/ams_migratory_dedup.md ---
---
type: rule
title: AMS 迁移去重（企业已存在则只补人员）
page_key: ams_migratory_dedup
domain: 租户迁移
status: draft
aliases: [AMS 迁移合并, 企业已存在只补人员]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
contract_version: "0.1"
---

**（document_claim，未证实）** 需求侧"讯易链与 AMS 都建过档的存量企业需做数据合并"的主张在语义分析中原文截断，尚未与代码逐条对齐。

`productAppId=AMS` 时不重建企业：先用统一社会信用代码（为空则按名称模糊反查）+ `db_tenant_code` 查已存在企业，命中后仅按 手机号+companyType+userType 过滤出增量管理员/经办人、按 roleType 过滤增量角色，走客户变更流程补齐。人员匹配涉及加密列，见 [[migratory_person_phone_encrypt_match]]。

```ground:rule
name: AMS 迁移去重（企业已存在则只补人员）
content: "productAppId=AMS 时，先用统一社会信用代码（为空则 companyNameVagueCheckService 按名称反查）+dbTenantCode 查已存在企业；命中则不重建企业，只按 手机号+companyType+userType 过滤出增量管理员/经办人、按 roleType 过滤增量角色，走客户变更流程补齐"
impact: "实现『讯易链与 AMS 都有建档时保留一条』的企业合并"
field_targets:
  - cust_company_info.certification_no
  - cust_person_info.phone
  - cust_person_info.company_type
  - cust_person_info.user_type
  - cust_role_info.role_type
evidence: "code:PlatFormMigratoryApplication.java#migratoryCust"
```

## 需求背景

同一家企业在两个业务系统都有建档（如讯易链与 AMS）时，迁移后只应保留一条企业主体，人员以增量方式补齐，避免重复主体与重复人员。

## 版本演进

由"一律新建"演进为"命中即合并只补人员"；合并粒度从企业级下沉到人员级（手机号+企业类型+用户类型）与角色级（roleType）。需求文档中关于合并范围与保留规则的表述在语义分析中截断（document_claim，未证实），需回原文确认。

相关：[[cust_company_info]]、[[cust_person_info]]、[[产品编码]]。

---END FILE---

---FILE: rules/migratory_company_status_mapping.md ---
---
type: rule
title: 迁移企业状态映射
page_key: migratory_company_status_mapping
domain: 租户迁移
status: draft
aliases: [cust_status 映射, 迁移企业状态派生]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
contract_version: "0.1"
---

`cust_status` 是上游推送的事实，`cust_build_status`/`check_status` 是产融侧派生结果，映射只有两条：EFFECT→BUILD_SUCCESS + CUST_CHECK_PASS；ADD→INIT + null。派生口径见 [[on_the_way_company]]。

```ground:rule
name: 迁移企业状态映射
content: "cust_status=EFFECT → cust_build_status=BUILD_SUCCESS 且 check_status=CUST_CHECK_PASS；cust_status=ADD → cust_build_status=INIT 且 check_status=null"
impact: "在途企业不计入生效口径，避免误开通产品与审核状态"
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.cust_build_status
  - cust_company_info.check_status
evidence: "code:PlatFormMigratoryApplication.java#setCompany"
```

## 需求背景

上游状态字典与产融内部状态字典不同，迁移必须做单向映射，绝不能让在途企业进入审核通过集合。

## 版本演进

映射规则固定为两条分支，未引入中间态；后续若增加上游状态需同步扩展映射并回归生效口径。

相关：[[cust_company_info]]、[[在途]]。

---END FILE---

---FILE: rules/no_backtrack_overwrite.md ---
---
type: rule
title: 已存在企业不回溯覆盖
page_key: no_backtrack_overwrite
domain: 租户迁移
status: draft
aliases: [不回溯覆盖, 以系统为准不更新]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
contract_version: "0.1"
---

当上游报文比库内数据旧、且企业已是 BUILD_SUCCESS 时，直接返回不更新，落"以系统为准"。这条规则是迁移与日常变更的边界：迁移不能把产融侧更新过的企业信息回退成旧值。

```ground:rule
name: 已存在企业不回溯覆盖
content: "若上游 updateTime 早于库内 update_time 且 cust_build_status=BUILD_SUCCESS，则『以系统为准，不更新』直接返回"
impact: "防止迁移把产融侧更新的企业信息回退成旧值"
field_targets:
  - cust_company_info.update_time
  - cust_company_info.cust_build_status
evidence: "code:PlatFormMigratoryApplication.java#setCompany"
```

## 需求背景

迁移报文可能包含历史时点数据，若直接覆盖会覆盖掉迁移后在产融侧发生的合法变更。

## 版本演进

由"按字段存在即更新"演进为"以 update_time 比较 + 生效状态判断"的双条件保护；尚未覆盖未生效企业的回溯场景。

相关：[[cust_company_info]]、[[migratory_company_status_mapping]]。

---END FILE---

---FILE: rules/on_the_way_person_status_force.md ---
---
type: rule
title: 在途企业人员状态强制初始化
page_key: on_the_way_person_status_force
domain: 租户迁移
status: draft
aliases: [在途人员状态强制 ADD]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setPersonAdm"
  - "code:PlatFormMigratoryApplication.java#setPersonOper"
contract_version: "0.1"
---

在途企业（`cust_status=ADD`）的管理员与经办人，状态一律覆写为 `CustPersonStatusConstant.ADD`，不采用上游报文里的状态值。这是 [[on_the_way_company]] 口径在人员链路的落地。

```ground:rule
name: 在途企业人员状态强制初始化
content: "company.cust_status=ADD 时，管理员/经办人 status 一律置 CustPersonStatusConstant.ADD，不采用上游推送状态"
impact: "防止在途数据把人员置为已生效"
field_targets:
  - cust_person_info.status
  - cust_company_info.cust_status
evidence: "code:PlatFormMigratoryApplication.java#setPersonAdm,#setPersonOper"
```

## 需求背景

人员生效状态直接关系到能否办理业务，迁移不能在在途企业下产出"已生效人员"。

## 版本演进

由采信上游人员状态改为按企业状态强制覆写，消除了上下游状态不一致导致的越权风险。

相关：[[cust_person_info]]、[[在途]]。

---END FILE---

---FILE: rules/migratory_user_record_insert.md ---
---
type: rule
title: 迁移用户记录落库
page_key: migratory_user_record_insert
domain: 租户迁移
status: draft
aliases: [迁移用户记录写入, is_login 初值 N]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
contract_version: "0.1"
---

人员落库后按 `user_id + db_tenant_code` 查 [[migratory_user_record]]，不存在则插入并置 `is_login='N'`。这条写入是首登提示状态机的来源动作，见 [[migratory_user_login_prompt]]。

```ground:rule
name: 迁移用户记录落库
content: "人员落库后，按 user_id+db_tenant_code 查 migratory_user_record，不存在则插入并置 is_login='N'"
impact: "为『首登弹升级提示、仅弹一次』提供判定依据"
field_targets:
  - migratory_user_record.user_id
  - migratory_user_record.db_tenant_code
  - migratory_user_record.is_login
evidence: "code:PlatFormMigratoryApplication.java#migratoryCust"
```

## 需求背景

存量用户首次登录（当前迁移批次内）弹出『【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务』，一个用户仅弹一次；因此迁移时须为每个迁移人员预置未登录记录。

## 版本演进

记录仅在不存在时插入（已存在不重置为 N），保证"只弹一次"不被重复迁移破坏；品牌名取自 [[贴牌]]。

相关：[[migratory_user_first_login]]、[[tenant_code]]。

---END FILE---

---FILE: rules/migratory_auth_supplement_flag.md ---
---
type: rule
title: 迁移授权书补签标记
page_key: migratory_auth_supplement_flag
domain: 租户迁移
status: draft
aliases: [授权书补签标记写入]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
contract_version: "0.1"
---

迁移时按渠道新旧决定是否展示授权书补签入口：新渠道无需补签，旧渠道需补签。两侧标记成对写入，互为反向。

```ground:rule
name: 迁移授权书补签标记
content: "newAuthAggrementFlag=true → migarory_auth_aggrement_flag=Y 且 auth_aggrement_supplement_flag=N；false → N 且 Y"
impact: "控制旧渠道企业是否展示授权书补签入口"
field_targets:
  - cust_company_info.migarory_auth_aggrement_flag
  - cust_company_info.auth_aggrement_supplement_flag
evidence: "code:PlatFormMigratoryApplication.java#setCompany"
```

## 需求背景

新渠道迁移时已具备合法授权书，旧渠道存量企业的授权书需要客户补签，因此迁移落库时就应决定入口是否展示，而不是等客户操作时再判断。

## 版本演进

由"全部展示补签入口"演进为按渠道标记区分；标记来源于上游 `newAuthAggrementFlag`。

相关：[[cust_company_info]]、[[pending_agreement_pull]]。

---END FILE---

---FILE: rules/agreement_migratory_init.md ---
---
type: rule
title: 迁移协议初始化（5 类，按客户+产品去重）
page_key: agreement_migratory_init
domain: 租户迁移
status: draft
aliases: [协议初始化, setAgreementMigratory]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setAgreementMigratory"
  - "code:AgreementMigratoryService.java#pull"
contract_version: "0.1"
---

对每个产品编码，逐类 `count(custId + platformProductCode + agreementType)` 为 0 才插入一条待拉取记录，初始 `status='N'`、`pull_num=0`、`is_new=Y`。协议类型分支见 [[产品编码]]，后续拉取见 [[agreement_pull_status]]。

```ground:rule
name: 迁移协议初始化（5 类，按客户+产品去重）
content: "对每个产品编码，逐一 count(custId+platformProductCode+agreementType) 为 0 才插入：CA授权（AMS→BS_AUTH，其他→CFCA_AUTH）、产品协议（按产品分支）、企业授权书、用户协议、隐私政策；初始 status='N'、pull_num=0、is_new=Y"
impact: "为后续协议拉取任务生成待办清单"
field_targets:
  - argeement_migratory_record.cust_id
  - argeement_migratory_record.platform_product_code
  - argeement_migratory_record.status
  - argeement_migratory_record.pull_num
evidence: "code:PlatFormMigratoryApplication.java#setAgreementMigratory + reqdoc:migratory-agreement-init"
```

## 需求背景

迁移时为迁移企业初始化协议待拉取记录，覆盖 CA 授权书、产品协议、企业授权书、用户协议、隐私政策五类；协议正文此时不搬，由后续任务回捞。

## 版本演进

CA 授权类型由单一类型演进为按产品分支（AMS→BS_AUTH，其他→CFCA_AUTH）；去重粒度固定为客户+产品+协议类型，保证重复迁移不产生重复待办。

相关：[[argeement_migratory_record]]、[[migratory_auth_supplement_flag]]。

---END FILE---

---FILE: rules/agreement_pull_throttle.md ---
---
type: rule
title: 协议拉取任务节流
page_key: agreement_pull_throttle
domain: 租户迁移
status: draft
aliases: [协议拉取定时任务, 拉取节流]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:AgreementMigratoryService.java#AreementPullTask"
  - "code:AgreementMigratoryService.java#pull"
contract_version: "0.1"
---

单线程调度器每 30 秒执行一次，先抢 Redis 锁 `cust_argeement_pull` 再取 [[pending_agreement_pull]] 集合，按产品分组→按客户分组拉取；成功置 Y，失败 `pull_num+1` 保持 N。

```ground:rule
name: 协议拉取任务节流
content: "应用启动后由单线程调度器每 30 秒执行 pull()；Redis 锁 cust_argeement_pull；查询 status='N'/enable='Y'/pull_num<pullNum(默认20)，按产品分组→按客户分组拉取，成功写 status='Y'，失败 pull_num+1"
impact: "控制对业务系统协议接口的调用频次与重试"
field_targets:
  - argeement_migratory_record.status
  - argeement_migratory_record.pull_num
evidence: "code:AgreementMigratoryService.java#AreementPullTask"
```

## 需求背景

迁移协议量较大，需在不压垮业务系统接口的前提下逐步补齐，并保证多实例部署时同一批记录不被重复拉取。

## 版本演进

由启动即全量拉取演进为定时 + 分布式锁 + 限量重试；30 秒周期与 20 次上限均为当前默认值。

相关：[[argeement_migratory_record]]、[[agreement_pull_status]]。

---END FILE---

---FILE: rules/agreement_file_contract_archive.md ---
---
type: rule
title: 协议文件落地与合同归档
page_key: agreement_file_contract_archive
domain: 租户迁移
status: draft
aliases: [协议归档, 文件落地 COS]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:AgreementMigratoryService.java#createContractInfo"
  - "code:AgreementMigratoryService.java#agreementExist"
contract_version: "0.1"
---

拉取到的 `fileUrl` 先本地落地再上传 COS（PROJECT=FBP_SYSTEM），`path` 非空才 `migrateConctract` 写合同记录；同客户+同协议编号已存在则跳过，保证协议影像不重复、不丢。

```ground:rule
name: 协议文件落地与合同归档
content: "拉取到的 fileUrl 先本地落地再上传 COS（PROJECT=FBP_SYSTEM），path 非空才 migrateConctract 写入合同记录；已存在同 客户+合同编号 的跳过"
impact: "保证影像/协议不重复、不丢"
field_targets:
  - argeement_migratory_record.agreement_path
  - argeement_migratory_record.agreement_no
evidence: "code:AgreementMigratoryService.java#createContractInfo,#agreementExist"
```

## 需求背景

迁移期协议文件需与产融合同影像体系对齐，客户在产融侧查看合同时应能看到迁移之前的协议。

## 版本演进

由"拉取即写库"演进为先落地再上传 COS、并以客户+编号判重；`path` 为空时不再生成合同记录，避免脏数据。

相关：[[argeement_migratory_record]]、[[agreement_pull_status]]。

---END FILE---

---FILE: rules/push_product_scope_deduce.md ---
---
type: rule
title: 推数产品范围推导
page_key: push_product_scope_deduce
domain: 租户迁移
status: draft
aliases: [产品范围推导, deduceProductCodes]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:MigratoryPointServiceImpl.java#deduceProductCodes"
  - "code:MigratoryPointServiceImpl.java#call"
contract_version: "0.1"
---

未显式指定 `productCodes` 时，用租户已开通产品推导；推租户同步时按平台产品推；企业存在 AMS 经办人或已开 AMS 互通产品时自动追加 AMS。产品码含义见 [[产品编码]]。

```ground:rule
name: 推数产品范围推导
content: "未指定 productCodes 时用租户已开通产品；推租户同步时按平台产品推；企业存在 AMS 经办人或已开 AMS 互通产品时自动追加 AMS"
impact: "决定迁移/推数落到哪些业务系统"
field_targets:
  - tenant_migarory_log.platform_product_code
evidence: "code:MigratoryPointServiceImpl.java#deduceProductCodes,#call"
```

## 需求背景

一个事件可能需同时推给多个业务系统；由调用方逐个指定产品码不可靠，故需服务端按租户开通情况与 AMS 互通情况自动推导。

## 版本演进

由调用方指定演进为服务端推导，并增加 AMS 自动追加逻辑；AMS 分支同时对应 [[ams_migratory_dedup]] 的合并行为。

相关：[[tenant_migarory_log]]、[[outbound_push]]。

---END FILE---

---FILE: rules/push_whitelist_shortcut.md ---
---
type: rule
title: 推数白名单短路
page_key: push_whitelist_shortcut
domain: 租户迁移
status: draft
aliases: [推数白名单, platformPointServiceExcludeDbTenantCode]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:MigratoryPointServiceImpl.java#push"
  - "code:MigratoryPointServiceImpl.java#call"
contract_version: "0.1"
---

租户对应的数据租户标识命中白名单配置时直接 return，既不推送也不产生流水记录。口径见 [[push_whitelist_tenant]]。

```ground:rule
name: 推数白名单短路
content: "tenantId 对应租户 dbTenantCode 命中 platformPointServiceExcludeDbTenantCode 时直接 return，不产生推数记录"
impact: "灰度/隔离特定租户的推数"
field_targets:
  - tenant_migarory_log.db_tenant_code
evidence: "code:MigratoryPointServiceImpl.java#push,#call"
```

## 需求背景

迁移期部分租户的业务系统尚未具备接收能力，需按租户粒度暂停出向推数，且不留下失败流水以免污染重试池。

## 版本演进

由无差别推送演进为配置化白名单短路；短路不落流水，是排障时"查不到记录"的常见原因（见 [[failed_migratory_log]]）。

相关：[[同步]]、[[tenant_setting_config]]。

---END FILE---

---FILE: rules/migratory_open_ca_idempotent.md ---
---
type: rule
title: 迁移企业开 CA 幂等
page_key: migratory_open_ca_idempotent
domain: 租户迁移
status: draft
aliases: [开 CA 幂等, openCa 判定]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#openCa"
  - "code:CustAccessAsyncApplication.java#openCa"
contract_version: "0.1"
---

开 CA 前按产品分支做幂等判定：AMS 看 `bs_register_status`，非 AMS 看 `ca_register_status`，已为 'Y' 直接返回；开通成功后 AMS 同时置 bs/ca 为 Y，其他仅置 ca 为 Y。这避免重复迁移时反复向签章中台注册。

```ground:rule
name: 迁移企业开 CA 幂等
content: "openCa 前判定：AMS 看 bs_register_status，非 AMS 看 ca_register_status，已为 'Y' 直接返回；开通成功后 AMS 同时置 bs/ca 为 Y，其他仅置 ca 为 Y"
impact: "避免重复向签章中台注册"
field_targets:
  - cust_company_info.ca_register_status
  - cust_company_info.bs_register_status
evidence: "code:PlatFormMigratoryApplication.java#openCa；CustAccessAsyncApplication.java#openCa"
```

## 需求背景

签章注册是有外部副作用的动作，重复迁移不得造成重复注册；同时 AMS 与自建签章体系并存，需分别判定。

## 版本演进

判定列由单列演进为按产品的双列（bs/ca），`need_register_ca` 仍会被上游值与字面量先后覆盖，判定口径以两列为准。

相关：[[cust_company_info]]、[[ams_migratory_dedup]]。

---END FILE---

---FILE: rules/migratory_person_phone_encrypt_match.md ---
---
type: rule
title: 迁移人员手机号加密匹配
page_key: migratory_person_phone_encrypt_match
domain: 租户迁移
status: draft
aliases: [手机号加密匹配, 加密列去重]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setPersonAdm"
  - "code:PlatFormMigratoryApplication.java#setPersonOper"
contract_version: "0.1"
---

人员去重与覆盖不能直接比明文：查询时以 `encryptAndBase64Str(phone)` 后 `eq` 匹配 `cust_person_info.phone`，命中则先删旧记录再插。相关表见 [[cust_person_info]]。

```ground:rule
name: 迁移人员手机号加密匹配
content: "以 metaDataEncryptionHandler/IMetaDataEncryptionService.encryptAndBase64Str(phone) 后 .eq 查询 cust_person_info.phone（已存在则先删旧记录再插）"
impact: "保证加密列上的去重与覆盖正确"
field_targets:
  - cust_person_info.phone
  - cust_person_info.ref_cust_company_info
evidence: "code:PlatFormMigratoryApplication.java#setPersonAdm,#setPersonOper"
```

## 需求背景

人员手机号属敏感信息，落库加密；迁移的增量判定必须与存储形态一致，否则会产生重复人员或漏更新。

## 版本演进

由明文匹配演进为加密匹配；覆盖方式为"删旧插新"，与 [[ams_migratory_dedup]] 的增量补齐逻辑配合使用。

相关：[[cust_person_info]]、[[ams_migratory_dedup]]。

---END FILE---

---REVIEW: table | tenant_migarory_log（物理库名与列类型待确认）---
语义分析未给出物理库名，`scope.databases` 暂以占位 `<待确认>` 承载；所有 `ground:table` 的 `type` 值（varchar/text/datetime/int）系依据值语义推断（编码/编号=VARCHAR，JSON 报文=TEXT，计数=INT），**非数据库实测**，需以 DDL 回填。
另：物理表名拼写为 `tenant_migarory_log`（migarory），疑为历史拼写错误，已按物理名逐字落页，勿在检索时自动纠正为 migratory。
---END REVIEW---

---REVIEW: enum | BooleanEnum（写值点与字典键名待核对）---
多处出现"BooleanEnum 字典键"，但语义分析只逐字给出 `BooleanEnum.no` 与 DB 侧 Y/N。字典键的 Java 常量名（no/yes 还是 N/Y）与库内实际存储值（Y/N）是否为同一形态未确认。
表页与状态机页按 DB 实测值 Y/N 写入，`dict: BooleanEnum` 仅表达字典归属，不代表键名。
另：`argeement_migratory_record.is_new` 用 `isNew.name()` 落库，而 `status` 用 `getDictKey`，同一表内两种写法并存，写入值形态可能不一致，待核对。
---END REVIEW---

---REVIEW: concept | 贴牌 ---
需求侧『假贴牌/二级贴牌』在语义分析中无独立字段与标识，仅有 `app_tenant_code`、`tenant_flg_en` 等近似字段，代码证据只支持展示/推送用途（bandName 填 brand、platName 拼提示语）。是否需新增二级贴牌标识字段属未决事项，本页按 boundary 处理，未落 ground 块。
---END REVIEW---

---REVIEW: rule | AMS 迁移去重（企业已存在则只补人员）---
reqdoc_claims 第三条原文截断（"讯易链与 AMS 都建过档的存量企业需做数据合并，保…"），`code_status` 与 `action` 缺失，无法判定为 anchor 还是 uncovered。当前处理：页面首行标注 (document_claim，未证实)，主张原文进 ## 版本演进；本页 ground:rule 仅承载代码证据。
另：前两条 anchor 主张的 `reqdoc:slug` 在语义分析中未给出，页内 evidence 中的 `reqdoc:migratory-first-login-eject-msg`、`reqdoc:migratory-agreement-init` 系按主张内容推导的占位 slug，需以需求库真实标识替换。
---END REVIEW---