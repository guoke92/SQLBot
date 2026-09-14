---FILE: tables/cust_company_info.md ---
---
type: table
title: 客户企业主表
page_key: cust_company_info
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_company_info
  - 客户企业主表
  - 企业主表
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication
  - code:TianmaService
  - code:TianmaController
  - code:AlipayAntArchiveController
contract_version: "0.1"
---

cust_company_info 是外部渠道（天马、支付宝蚂蚁）与银行/清分对接链路的企业主数据落点，承载企业身份（统一社会信用代码）、企业角色、渠道来源以及三套状态字段（建档/审核/客户状态）。它同时是 [[cust_build_status]]、[[cust_check_status]]、[[cust_status]] 三个状态机的宿主表。

## 需求背景
渠道建档的核心是「先跨租户检索、再按渠道秘钥落租户」：入站请求进入时 ThreadLocal 租户被置为 `all`（见 [[inbound_all_tenant_context]]），企业查重与定位以 certification_no 为主匹配键（见 [[company_certification_tenant_match]]），最终落库租户取自渠道秘钥配置。企业号的可用性还取决于 [[build_fail_reusable]] 与 [[writeoff_excluded]] 两个豁免口径，日常查询则统一受 [[company_enable_filter]] 约束。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_company_info
fields:
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识；入站渠道建档期间 ThreadLocal 被置为 'all' 以跨租户查询，业务租户由 cust_access_secret.channel 反查得到
    dict: ""
  - name: certification_no
    type: unknown
    desc: 统一社会信用代码，渠道建档/查重/查询的主匹配键（socialUnifiedCode → certificationNo）
    dict: ""
  - name: cust_company_type
    type: unknown
    desc: 企业角色，JSON 数组字符串（如 ["SUPPLIER"]）；查询用 like 模糊匹配，故单值比对不可靠
    dict: SUPPLIER|CORE|FINANCE|PLATFORM_OPERATOR_COMPANY
  - name: cust_build_status
    type: unknown
    desc: 建档（认证）状态，落库键取自 CustBuildStatusEnum.getDictKey()/CustBuildStatusConstant，如 INIT/BUILDING/CUST_CONFIRM_AWAIT/BUILD_SUCCESS/BUILD_FAIL
    dict: INIT|BUILDING|CUST_CONFIRM_AWAIT|BUILD_SUCCESS|BUILD_FAIL
  - name: check_status
    type: unknown
    desc: 审核状态，落库为 OperApiConstants.CheckStatus 的 .name()（CUST_CHECK_INIT/CHECKING/PASS/REJECT/BACKTOCUSTOM/CUST_BACK），读取用 CheckStatus.getByName
    dict: CUST_CHECK_INIT|CUST_CHECK_CHECKING|CUST_CHECK_PASS|CUST_CHECK_REJECT|CUST_CHECK_BACKTOCUSTOM|CUST_BACK
  - name: cust_status
    type: unknown
    desc: 客户状态：ADD(新增)/CHANGE(变更中)/WRITEOFF(作废)；变更流程仅在 CHANGE 态才允许终止
    dict: ADD|CHANGE|WRITEOFF
  - name: identify_style
    type: unknown
    desc: 认证方式：INVITE(自主认证) / INVITE_AGW(自主建档-渠道)；怡亚通等特定租户被强制改写为 INVITE
    dict: INVITE|INVITE_AGW
  - name: time_permanent
    type: json
    desc: 营业执照有效期 JSON {start,end,status}；end 以 9999 开头时 status=YES 表示长期
    dict: YES|NO
  - name: legal_time_permanent
    type: json
    desc: 法人身份证有效期 JSON {start,end,status}，规则同上
    dict: YES|NO
  - name: company_ext_data
    type: json
    desc: 企业扩展 JSON：天马写入 INTEREST_RATE(综合利率)，怡亚通写入 BUILD_STYPE=INVITE_AGW
    dict: INTEREST_RATE|BUILD_STYPE
  - name: ca_register_status
    type: unknown
    desc: CA 开通状态，建档初始化固定为 EnableEnum.N.name()（未开通）
    dict: EnableEnum.N.name()
  - name: legal_phone
    type: unknown
    desc: 法人手机号；企业变更时若入参为空/空白则不覆盖库中值，防止在途建档推运营为空
    dict: ""
  - name: enable
    type: unknown
    desc: 启用标识；企业查询/变更/批量查询均排除停用企业（口径 predicate: cust_company_info.enable = 'Y'）
    dict: "Y"
  - name: app_tenant_code
    type: unknown
    desc: 逻辑租户标识，与数据租户 db_tenant_code 语义不同
    dict: ""
  - name: cust_from
    type: unknown
    desc: 企业来源展示字段，不可用作渠道路由
    dict: ""
  - name: cust_source
    type: unknown
    desc: 企业来源展示字段，不可用作渠道路由
    dict: ""
  - name: invoicing_taxpayer_no
    type: unknown
    desc: 开票纳税人识别号，与统一社会信用代码 certification_no 为两个字段
    dict: ""
  - name: business_license_end_time
    type: unknown
    desc: 营业执照到期日，由 time_permanent 的 end 同步写入
    dict: ""
  - name: legal_certification_end_time
    type: unknown
    desc: 法人证件到期日，由 legal_time_permanent 的 end 同步写入
    dict: ""
```
---END FILE---

---FILE: tables/cust_access_secret.md ---
---
type: table
title: 渠道接入秘钥表
page_key: cust_access_secret
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_access_secret
  - 渠道秘钥表
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication
contract_version: "0.1"
---

cust_access_secret 保存外部渠道的接入秘钥与租户映射，是「渠道 → 数据租户」定位与渠道鉴权的唯一依据（见 [[channel]]、[[tenant]]）。

## 需求背景
渠道入站请求先以 `all` 租户检索（[[inbound_all_tenant_context]]），再由本表的 channel + enable 联查反查真实 dbTenantCode；渠道未启用或匹配不到时按 [[channel_enable_filter]] 直接拒绝。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_access_secret
fields:
  - name: channel
    type: unknown
    desc: 渠道标识（天马 CloudChannel.TIANMA.getDictKey() 等），与 enable 联查后决定该渠道的 dbTenantCode，是渠道鉴权+租户定位的唯一依据
    dict: CloudChannel.TIANMA.getDictKey()
  - name: db_tenant_code
    type: unknown
    desc: 渠道对应的数据租户，入站建档落库租户的来源（落库租户须取本表值）
    dict: ""
  - name: enable
    type: unknown
    desc: 渠道启用标识；渠道鉴权、渠道→租户定位、变更渠道校验均以 enable='Y' 为前置口径
    dict: "Y"
```
---END FILE---

---FILE: tables/cust_sftp.md ---
---
type: table
title: 渠道影像 SFTP 通道配置表
page_key: cust_sftp
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_sftp
  - SFTP 通道配置
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.initSftp
contract_version: "0.1"
---

cust_sftp 保存渠道影像文件传输通道的连接配置，按 channel + enable 联查，用于影像下载/回传。

## 需求背景
非自主建档强制要求提交营业执照、法人证件、经办人证件与授权书影像（见 [[independent_archive_validation]]），影像落地依赖本表通道；通道匹配不到时按 [[sftp_channel_enable]] 直接抛 SERVER_BUSY。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_sftp
fields:
  - name: channel
    type: unknown
    desc: 渠道影像 SFTP 通道配置（host/port/userName/password），按 channel+enable 联查，用于影像下载/回传
    dict: ""
  - name: enable
    type: unknown
    desc: 通道启用标识；影像 SFTP 通道初始化口径为 cust_sftp.enable = 'Y'
    dict: "Y"
  - name: host
    type: unknown
    desc: SFTP 通道连接配置项之一（影像下载/回传）
    dict: ""
  - name: port
    type: unknown
    desc: SFTP 通道连接配置项之一（影像下载/回传）
    dict: ""
  - name: userName
    type: unknown
    desc: SFTP 通道连接配置项之一（影像下载/回传）
    dict: ""
  - name: password
    type: unknown
    desc: SFTP 通道连接配置项之一（影像下载/回传）
    dict: ""
```
---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: 企业人员信息表
page_key: cust_person_info
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_person_info
  - 企业人员表
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.getCurrentAdmin
contract_version: "0.1"
---

cust_person_info 保存企业下的人员（含管理员）信息，与主表为 code 级软关联。

## 需求背景
建档结果推送与运营流程需要定位企业管理员，取数口径为「enable='Y' 且 user_type=admin，按 create_time 倒序取 1 条」（见 [[person_enable_filter]]）；人员自身的 company_type 与主表企业角色不同，参见 [[company_type]]。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_person_info
fields:
  - name: ref_cust_company_info
    type: unknown
    desc: 归属企业 code（非主键 id），企业-人员为 code 级软关联
    dict: ""
  - name: company_type
    type: unknown
    desc: 人员维度的企业类型，与主表 cust_company_info.cust_company_type 语义不同
    dict: ""
  - name: user_type
    type: unknown
    desc: 人员类型；定位企业管理员时取 user_type=admin
    dict: admin
  - name: enable
    type: unknown
    desc: 人员启用标识；定位企业管理员口径为 cust_person_info.enable = 'Y'
    dict: "Y"
  - name: create_time
    type: unknown
    desc: 创建时间；定位管理员时按 create_time 倒序 limit 1
    dict: ""
```
---END FILE---

---FILE: tables/cust_account_info.md ---
---
type: table
title: 企业银行账户信息表
page_key: cust_account_info
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_account_info
  - 企业银行账户表
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateBank
  - code:BocomQueryAccountByXylClientService
  - code:CpcnBankProviderImpl
contract_version: "0.1"
---

cust_account_info 保存企业银行账户信息，是供应商建档的银行三要素落点，也是各清分渠道（支付宝清分、交e保、中金）对接后的账户回填目标（见 [[clearing]]）。

## 需求背景
非自主建档强制校验供应商银行三要素（见 [[independent_archive_validation]]）；供应商建档时按联行号联查银行信息回填 bank_branch_name/bank_code/bank_no。清分渠道的账户数据不落产融库，仅回填本表。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_account_info
fields:
  - name: ref_cust_company_info
    type: unknown
    desc: 归属企业 code；供应商建档时按联行号查银行信息回填 bank_branch_name/bank_code/bank_no
    dict: ""
  - name: bank_no
    type: unknown
    desc: 联行号(unitedBankNumber)，建档必填校验项之一
    dict: ""
  - name: bank_branch_name
    type: unknown
    desc: 开户支行名称，由联行号联查银行信息回填
    dict: ""
  - name: bank_code
    type: unknown
    desc: 银行编码，由联行号联查银行信息回填
    dict: ""
  - name: account_no
    type: unknown
    desc: 账户号；清分（clearing）主题的账户数据落点
    dict: ""
```
---END FILE---

---FILE: tables/cust_role_info.md ---
---
type: table
title: 企业角色关系表
page_key: cust_role_info
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_role_info
  - 企业角色表
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.resolveBuildPlatformCustIdForOper
contract_version: "0.1"
---

cust_role_info 保存企业与运营中台的身份关系，其中 platform_cust_id 是运营流程拉起/终止判定的权威来源。

## 需求背景
当 cust_build_record.plat_cust_id 与本表 platform_cust_id 不一致时，按 [[oper_platform_id_priority]] 以本表为准并告警，该判定直接决定是否拉起或终止中台流程；本表 role_type 与主表企业角色语义不同，参见 [[company_type]]。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_role_info
fields:
  - name: platform_cust_id
    type: unknown
    desc: 运营中台企业 ID；与 cust_build_record.plat_cust_id 冲突时以本表为准
    dict: ""
  - name: role_type
    type: unknown
    desc: 角色类型，与主表 cust_company_type 的企业角色语义不同
    dict: ""
```
---END FILE---

---FILE: tables/cust_project_rel.md ---
---
type: table
title: 企业与租户项目关联表
page_key: cust_project_rel
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_project_rel
  - 企业项目关联表
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication
contract_version: "0.1"
---

cust_project_rel 记录企业与租户项目之间的关联，为 code 级软关联。

## 需求背景
天马渠道建档时 projectId 由外部项目校验服务返回后再建立关联，因此本表数据依赖上游校验结果而非本地推导。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_project_rel
fields:
  - name: ref_cust_project_rel_cust_company_info
    type: unknown
    desc: 企业与租户项目的关联（code 级），天马建档时 projectId 由外部项目校验服务返回
    dict: ""
```
---END FILE---

---FILE: tables/cust_build_record.md ---
---
type: table
title: 建档记录表
page_key: cust_build_record
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_build_record
  - 建档记录
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.resolveBuildPlatformCustIdForOper
contract_version: "0.1"
---

cust_build_record 记录每次建档流程的过程数据，其中 plat_cust_id 用于与运营中台对齐企业身份。

## 需求背景
该表 plat_cust_id 与 [[cust_role_info]].platform_cust_id 不一致时，按 [[oper_platform_id_priority]] 以角色表为准，避免在错误的运营主体上拉起或终止流程。

## 版本演进
暂无版本演进记录。

```ground:table
table: cust_build_record
fields:
  - name: plat_cust_id
    type: unknown
    desc: 运营中台企业 ID（建档记录维度）；与 cust_role_info.platform_cust_id 冲突时以 cust_role_info 为准并告警
    dict: ""
```
---END FILE---

---FILE: processes/cust_build_status.md ---
---
type: process
title: 企业建档（认证）状态机
page_key: cust_build_status
domain: 外部渠道与银行对接
status: draft
aliases:
  - 建档状态
  - custBuildStatus
  - CustBuildStatusEnum
  - CustBuildStatusConstant
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.setCustCompany
  - code:CustAccessApplication.initCustOfTianma
  - code:CustAccessApplication.query
  - code:CustAccessApplication.terminateBuildingFlow
contract_version: "0.1"
---

建档状态刻画企业本地初始化到建档结果产生的全过程，落库字段为 [[cust_company_info]].cust_build_status，与运营侧的 [[cust_check_status]] 是两条独立主线（参见 [[company_archive]]）。

## 需求背景
入站渠道建档先置租户上下文为 `all`（[[inbound_all_tenant_context]]）并完成查重，查重时失败件可复用（[[build_fail_reusable]]）、作废件允许重建（[[writeoff_excluded]]）；对外查询时 BUILDING 被映射为 CUSTS002(对外建档中)。

## 版本演进
暂无版本演进记录。

```ground:process
name: 企业建档(认证)状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化
    source: code_const
  - value: BUILDING
    label: 建档中
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败
    source: code_enum
transitions:
  - from: "*"
    event: 建档初始化(自主/非自主/天马)
    to: INIT
    evidence: "code_path:CustAccessApplication.setCustCompany / initCustOfTianma → company.setCustBuildStatus(CustBuildStatusConstant.INIT)"
  - from: BUILD_FAIL
    event: 同企业重新建档(复用旧 id/code)
    to: INIT
    evidence: "code_path:CustAccessApplication.initCust / initCustOfTianma → query custBuildStatus=BUILD_FAIL or custStatus=WRITEOFF 后复用"
  - from: BUILDING
    event: 对外查询状态
    to: CUSTS002(对外建档中)
    evidence: "code_path:CustAccessApplication.query → CustBuildStatusEnum.BUILDING.getDictKey() 分支"
  - from: "*"
    event: 运营/标准接口终止建档流程 terminateBuildingFlow
    to: BUILD_FAIL
    evidence: "code_path:CustAccessApplication.terminateBuildingFlow → update.setCustBuildStatus(CustBuildStatusEnum.BUILD_FAIL.getDictKey())"
```
---END FILE---

---FILE: processes/cust_check_status.md ---
---
type: process
title: 企业审核状态机
page_key: cust_check_status
domain: 外部渠道与银行对接
status: draft
aliases:
  - 审核状态
  - checkStatus
  - CheckStatus
  - CUST_CHECK_*
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.terminateBuildingFlow
  - code:CustAccessApplication.getCheckStatus
contract_version: "0.1"
---

审核状态是运营流程侧的状态主线，落库字段为 [[cust_company_info]].check_status，落库值为 CheckStatus 的 `.name()`、读取用 `CheckStatus.getByName`。

## 需求背景
对外状态查询以 check_status 优先映射（CUST_CHECK_PASS→CUSTS003+AUTH0003 等），为空时才回落到建档状态兜底；终止建档流程会把审核置为 CUST_CHECK_REJECT。终止后若未拉起中台流程，还需按 [[build_terminated_todo_compensation]] 补偿待办。与建档状态的边界见 [[check_status]] 与 [[company_archive]]。

## 版本演进
暂无版本演进记录。

```ground:process
name: 企业审核状态
field: cust_company_info.check_status
states:
  - value: CUST_CHECK_INIT
    label: 审核初始化
    source: code_enum
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_enum
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户补件
    source: code_enum
  - value: CUST_BACK
    label: 退回
    source: code_enum
transitions:
  - from: "*"
    event: 终止建档流程
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustAccessApplication.terminateBuildingFlow → update.setCheckStatus(CheckStatus.CUST_CHECK_REJECT.name())"
  - from: CUST_CHECK_PASS
    event: 对外状态映射
    to: CUSTS003 + AUTH0003
    evidence: "code_path:CustAccessApplication.getCheckStatus → case CUST_CHECK_PASS"
  - from: CUST_CHECK_CHECKING
    event: 对外状态映射
    to: CUSTS002 + AUTH0001
    evidence: "code_path:CustAccessApplication.getCheckStatus → case CUST_CHECK_CHECKING"
  - from: CUST_CHECK_REJECT
    event: 对外状态映射
    to: CUSTS004 + AUTH0001
    evidence: "code_path:CustAccessApplication.getCheckStatus → case CUST_CHECK_REJECT"
```
---END FILE---

---FILE: processes/cust_status.md ---
---
type: process
title: 客户状态机
page_key: cust_status
domain: 外部渠道与银行对接
status: draft
aliases:
  - 客户状态
  - CustStatusEnum
  - CustStatusConstant
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.setCustCompany
  - code:CustAccessApplication.terminateChangingFlow
contract_version: "0.1"
---

客户状态表示企业在库生命周期（新增/变更中/作废），落库字段为 [[cust_company_info]].cust_status。

## 需求背景
建档落库即置为 ADD；标准 OpenAPI 发起企业变更后进入 CHANGE，只有 CHANGE 态才允许终止变更流程，这是变更流程终止的前置校验。作废态在查重时被排除，允许重新建档（[[writeoff_excluded]]）。

## 版本演进
暂无版本演进记录。

```ground:process
name: 客户状态
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/在库
    source: code_const
  - value: CHANGE
    label: 变更中
    source: code_enum
  - value: WRITEOFF
    label: 作废
    source: code_const
transitions:
  - from: "*"
    event: 建档落库
    to: ADD
    evidence: "code_path:CustAccessApplication.setCustCompany → company.setCustStatus(CustStatusConstant.ADD)"
  - from: ADD
    event: 标准 OpenAPI 发起企业变更
    to: CHANGE(经运营变更流程)
    evidence: "code_path:CustAccessApplication.terminateChangingFlow 前置判断 CustStatusEnum.CHANGE.getDictKey().equals(company.getCustStatus())"
```
---END FILE---

---FILE: calibers/channel_enable_filter.md ---
---
type: caliber
title: 渠道启用过滤
page_key: channel_enable_filter
domain: 外部渠道与银行对接
status: draft
aliases:
  - 渠道启用口径
  - cust_access_secret.enable = 'Y'
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.validateChangeChannelAndTenant
  - code_path:lowcode-pplatform-openapi/lowcode-pplatform-openapi-non-standard-alipay-ant/.../controller/AlipayAntArchiveController.java#channelArchive
contract_version: "0.1"
---

渠道启用过滤是渠道鉴权与租户定位的前置口径：只有启用中的渠道才允许接入并解析出租户，否则直接拒绝。

## 需求背景
非标渠道建档复用统一入站 URL，channel 完全由请求体决定（首期支付宝蚂蚁），因此渠道有效性必须在解析请求体后立刻用本口径校验；命中后据 [[cust_access_secret]] 反查真实 dbTenantCode（见 [[tenant]]、[[channel]]）。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 渠道启用过滤
predicate: "cust_access_secret.enable = 'Y'"
scope: 渠道鉴权、渠道→租户(dbTenantCode)定位、变更渠道校验
evidence: "code:CustAccessApplication.validateSetValue / validateChangeChannelAndTenant + code_path:lowcode-pplatform-openapi/lowcode-pplatform-openapi-non-standard-alipay-ant/.../controller/AlipayAntArchiveController.java#channelArchive + reqdoc:non-standard-channel-unified-ingress-url"
```
---END FILE---

---FILE: calibers/company_enable_filter.md ---
---
type: caliber
title: 客户主表启用过滤
page_key: company_enable_filter
domain: 外部渠道与银行对接
status: draft
aliases:
  - 企业启用口径
  - cust_company_info.enable = 'Y'
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.query
  - code:CustAccessApplication.batchQuery
  - code:CustAccessApplication.changeCompanyInfo
contract_version: "0.1"
---

企业查询/变更/批量查询统一附加启用过滤，保证停用企业不会被渠道侧检索或变更。

## 需求背景
对渠道而言「查不到」与「查不到但存在停用件」的语义不同，统一过滤避免了渠道侧对无效企业发起变更；变更链路中该过滤与 [[company_certification_tenant_match]] 叠加使用。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 客户主表启用过滤
predicate: "cust_company_info.enable = 'Y'"
scope: 企业查询/变更/批量查询均排除停用企业
evidence: "code:CustAccessApplication.query / batchQuery / changeCompanyInfo"
```
---END FILE---

---FILE: calibers/build_fail_reusable.md ---
---
type: caliber
title: 建档失败可复用口径
page_key: build_fail_reusable
domain: 外部渠道与银行对接
status: draft
aliases:
  - 建档失败豁免
  - 失败件可重建
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.initCust
contract_version: "0.1"
---

建档失败（BUILD_FAIL）的企业在查重时被豁免，允许同企业重建并复用旧 id/code。

## 需求背景
渠道建档失败多为资料或网络原因，直接占用信用代码会导致企业无法再次提交。因此「已建档」判定为 `count(cust_build_status != BUILD_FAIL) != 0`，失败件不再计为已建档；重建后状态回到 INIT，见 [[cust_build_status]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 建档失败可复用口径
predicate: "cust_company_info.cust_build_status = 'BUILD_FAIL'"
scope: "查重时豁免：已建档判定为 count(cust_build_status != BUILD_FAIL) != 0，失败件允许重建"
evidence: "code:CustAccessApplication.validateSetValue / initCust"
```
---END FILE---

---FILE: calibers/writeoff_excluded.md ---
---
type: caliber
title: 作废客户排除
page_key: writeoff_excluded
domain: 外部渠道与银行对接
status: draft
aliases:
  - 作废件豁免
  - WRITEOFF 排除
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValueOfTianma
contract_version: "0.1"
---

作废（WRITEOFF）企业在天马撞库校验中被排除，允许以同一信用代码重新建档。

## 需求背景
天马渠道建档查重按 notIn(WRITEOFF) 过滤，作废件不阻塞新申请；该口径与 [[build_fail_reusable]] 共同决定「同企业能否再次建档」，状态含义见 [[cust_status]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 作废客户排除
predicate: "cust_company_info.cust_status = 'WRITEOFF'"
scope: 天马撞库校验 notIn(WRITEOFF)，作废件允许重新建档
evidence: "code:CustAccessApplication.validateSetValueOfTianma"
```
---END FILE---

---FILE: calibers/company_certification_tenant_match.md ---
---
type: caliber
title: 企业+信用代码+租户三元匹配
page_key: company_certification_tenant_match
domain: 外部渠道与银行对接
status: draft
aliases:
  - 三元匹配口径
  - 信用代码定位企业
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.query
  - code:CustAccessApplication.changeCompanyInfo
contract_version: "0.1"
---

渠道查询与变更定位企业时，以统一社会信用代码为主键、叠加数据租户与企业角色条件，构成三元匹配。

## 需求背景
由于入站请求的租户上下文为 `all`（[[inbound_all_tenant_context]]），必须显式叠加 db_tenant_code 才能落到正确租户；企业角色列为 JSON 数组、只能用 like 模糊匹配，因此不参与等价性判定（见 [[company_type]]）。信用代码字段名映射见 [[social_unified_code]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 企业+信用代码+租户三元匹配
predicate: "cust_company_info.certification_no = '<socialUnifiedCode>'"
scope: 渠道查询/变更定位企业的核心条件（叠加 db_tenant_code 与 cust_company_type like）
evidence: "code:CustAccessApplication.query / changeCompanyInfo"
```
---END FILE---

---FILE: calibers/sftp_channel_enable.md ---
---
type: caliber
title: SFTP 渠道启用
page_key: sftp_channel_enable
domain: 外部渠道与银行对接
status: draft
aliases:
  - 影像通道启用口径
  - cust_sftp.enable = 'Y'
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.initSftp
contract_version: "0.1"
---

影像 SFTP 通道按 channel + enable 联查初始化，匹配不到即抛 SERVER_BUSY，建档流程不得降级继续。

## 需求背景
非自主建档必须提交营业执照、法人正反面、经办人正反面与授权书影像（[[independent_archive_validation]]），影像缺失会导致后续运营审核无法进行，因此通道不可用时快速失败。配置见 [[cust_sftp]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: SFTP 渠道启用
predicate: "cust_sftp.enable = 'Y'"
scope: 影像 SFTP 通道初始化，匹配不到直接抛 SERVER_BUSY
evidence: "code:CustAccessApplication.initSftp"
```
---END FILE---

---FILE: calibers/person_enable_filter.md ---
---
type: caliber
title: 人员启用过滤
page_key: person_enable_filter
domain: 外部渠道与银行对接
status: draft
aliases:
  - 管理员定位口径
  - cust_person_info.enable = 'Y'
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.getCurrentAdmin
contract_version: "0.1"
---

定位企业管理员时的取数口径：enable='Y' 且 user_type=admin，按 create_time 倒序取 1 条。

## 需求背景
管理员是建档结果推送与运营流程通知的收件人，必须唯一且有效；数据落点见 [[cust_person_info]]，与企业的 code 级软关联决定了查询需带 ref_cust_company_info。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 人员启用过滤
predicate: "cust_person_info.enable = 'Y'"
scope: 定位企业管理员（user_type=admin、按 create_time 倒序 limit 1）
evidence: "code:CustAccessApplication.getCurrentAdmin"
```
---END FILE---

---FILE: calibers/oper_platform_id_consistency.md ---
---
type: caliber
title: 运营企业ID一致性口径
page_key: oper_platform_id_consistency
domain: 外部渠道与银行对接
status: draft
aliases:
  - plat_cust_id 一致性
  - 运营企业ID对账口径
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.resolveBuildPlatformCustIdForOper
contract_version: "0.1"
---

运营中台企业 ID 在两个来源不一致时以 cust_role_info 为准并告警。

## 需求背景
该值决定是否拉起或终止中台流程，取错会造成流程挂空。冲突处理规则见 [[oper_platform_id_priority]]，两个来源表见 [[cust_build_record]] 与 [[cust_role_info]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 运营企业ID一致性口径
predicate: "cust_build_record.plat_cust_id = cust_role_info.platform_cust_id"
scope: 不一致时以 cust_role_info 为准并告警
evidence: "code:CustAccessApplication.resolveBuildPlatformCustIdForOper"
```
---END FILE---

---FILE: concepts/channel.md ---
---
type: concept
title: 渠道
page_key: channel
domain: 外部渠道与银行对接
status: draft
aliases:
  - channel
  - CloudChannel
  - AlipayAntCloudChannel
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:TianmaController
  - code:AlipayAntArchiveController
contract_version: "0.1"
maps_to: cust_access_secret.channel
also_confused_with:
  - cust_company_info.cust_from
  - cust_company_info.cust_source
adjudication: boundary
---

> (document_claim，未证实)

「渠道」在本文主题中特指接入方标识，它同时决定租户（dbTenantCode）与影像 SFTP 通道，是路由与鉴权的第一维度。

## 需求背景
渠道由请求体传入，非标渠道复用统一入站 URL `/cloud/std/cust/channelArchive`，首期只对接支付宝蚂蚁；天马则走独立入口 `/tianma/companyArchive`。渠道有效性、租户映射与影像通道分别由 [[channel_enable_filter]]、[[tenant]]、[[sftp_channel_enable]] 约束。

## 版本演进
- (document_claim，未证实) BR-003 签名校验：参数排序拼接 + app_secret + MD5 32 位小写，由 CryptoService 统一实现、各渠道复用 Md5Utils/TianmaUtil。本次链路仅见 TianmaUtil.post 的调用点（TianmaService.companyArchiveDetail），未见 CryptoService/Md5Utils 实现，且该主张在语义分析中记录不完整，保留待确认。
---END FILE---

---FILE: concepts/tenant.md ---
---
type: concept
title: 租户
page_key: tenant
domain: 外部渠道与银行对接
status: draft
aliases:
  - dbTenantCode
  - db_tenant_code
  - appTenantCode
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:MetaDataThreadLocalConfig
contract_version: "0.1"
maps_to: cust_company_info.db_tenant_code
also_confused_with:
  - cust_company_info.app_tenant_code
adjudication: boundary
---

「租户」在本主题中指数据租户（dbTenantCode），决定落库归属；它与逻辑租户 appTenantCode 不是同一概念。

## 需求背景
入站渠道建档先置 ThreadLocal 为 `all` 做跨租户检索（[[inbound_all_tenant_context]]），随后必须用渠道秘钥反查真实租户再落库，否则数据会落到错误租户；该反查依据见 [[cust_access_secret]]，落库字段见 [[cust_company_info]]。

## 版本演进
暂无版本演进记录。
---END FILE---

---FILE: concepts/company_type.md ---
---
type: concept
title: 企业类型/企业角色
page_key: company_type
domain: 外部渠道与银行对接
status: draft
aliases:
  - companyType
  - custCompanyType
  - CompanyType
  - SPY
  - CE
  - CPT
  - OPE
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.getCompanyType
  - code:TianmaService.companyArchive
contract_version: "0.1"
maps_to: cust_company_info.cust_company_type
also_confused_with:
  - cust_person_info.company_type
  - cust_role_info.role_type
adjudication: boundary
---

企业类型承担对外协议码与内部字典值的双向往返，是渠道建档中取值最容易混淆的维度。

## 需求背景
对外协议码（SPY/CE/CPT/OPE）与内部 dictKey（SUPPLIER/CORE/FINANCE/PLATFORM_OPERATOR_COMPANY）需经 getCompanyType 转换；天马请求 companyType 为空时按默认供应商处理（[[tianma_default_supplier]]）。主表以 JSON 数组存储，查询侧只能 like 模糊匹配（[[company_certification_tenant_match]]），因此不可用等值条件过滤角色。

## 版本演进
暂无版本演进记录。
---END FILE---

---FILE: concepts/social_unified_code.md ---
---
type: concept
title: 统一社会信用代码
page_key: social_unified_code
domain: 外部渠道与银行对接
status: draft
aliases:
  - socialUnifiedCode
  - certificationNo
  - certification_no
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.query
  - code:CustAccessApplication.validateSetValue
contract_version: "0.1"
maps_to: cust_company_info.certification_no
also_confused_with:
  - cust_company_info.invoicing_taxpayer_no
adjudication: synonym
---

对外协议中的 socialUnifiedCode 与落库列 certification_no 为同一概念，是企业查重与定位的主匹配键。

## 需求背景
渠道建档/查询/变更均以该字段定位企业，结合租户构成三元匹配（[[company_certification_tenant_match]]）；与开票纳税人识别号 invoicing_taxpayer_no 不可混用。

## 版本演进
暂无版本演进记录。
---END FILE---

---FILE: concepts/company_archive.md ---
---
type: concept
title: 建档
page_key: company_archive
domain: 外部渠道与银行对接
status: draft
aliases:
  - companyArchive
  - reg
  - channelArchive
  - 非自主建档
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.setCustCompany
  - code:CustAccessApplication.validateSetValue
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
also_confused_with:
  - cust_company_info.check_status
adjudication: boundary
---

「建档」指企业在本地的初始化过程及其状态机（cust_build_status），与运营侧的「审核」（check_status）是两条独立主线。

## 需求背景
建档分为自主（isIndependent=true）与非自主两类，校验强度不同（[[independent_archive_validation]]）；失败件与作废件均可重新建档（[[build_fail_reusable]]、[[writeoff_excluded]]）。对外查询的 status 以 check_status 优先映射，仅在 check_status 为空时才回落到建档状态兜底，因此两条状态线不可互相替代（参见 [[check_status]]）。

## 版本演进
暂无版本演进记录。
---END FILE---

---FILE: concepts/check_status.md ---
---
type: concept
title: 审核状态
page_key: check_status
domain: 外部渠道与银行对接
status: draft
aliases:
  - checkStatus
  - CheckStatus
  - CUST_CHECK_*
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.getCheckStatus
  - code:CustAccessApplication.terminateBuildingFlow
contract_version: "0.1"
maps_to: cust_company_info.check_status
also_confused_with:
  - cust_company_info.cust_build_status
adjudication: boundary
---

审核状态是运营流程状态，落库为枚举 `.name()`，读取用 `CheckStatus.getByName`。

## 需求背景
对外状态映射以本字段优先（PASS→CUSTS003+AUTH0003、CHECKING→CUSTS002+AUTH0001、REJECT→CUSTS004+AUTH0001），为空时回落到建档状态；终止建档会把审核置为 CUST_CHECK_REJECT。状态机见 [[cust_check_status]]，与建档的边界见 [[company_archive]]。

## 版本演进
暂无版本演进记录。
---END FILE---

---FILE: concepts/clearing.md ---
---
type: concept
title: 清分
page_key: clearing
domain: 外部渠道与银行对接
status: draft
aliases:
  - clearing
  - 交e保
  - 中金CFCA
  - 支付宝清分
  - 清分会员登记簿
oid: 1
scope:
  databases:
    - cust
sources:
  - code:AlipayClearingProvider
  - code:PayProvider
  - code:ICpcnApi
  - code:CpcnBankProviderImpl
contract_version: "0.1"
maps_to: cust_account_info.account_no
also_confused_with:
  - cust_company_info.company_ext_data
adjudication: boundary
---

「清分」在本主题中是对接银行/清分渠道的一类能力集合，三条链路各自独立：支付宝清分走 AlipayClearingProvider（registry=alipay），交e保走 PayProvider/ClearingProvider（registry=clearing），中金走 ICpcnApi。

## 需求背景
三者账户数据均不落产融库，只回填 [[cust_account_info]]；产品维度路由存在默认值兜底（[[default_product_route_acflow]]）。与主表扩展字段 company_ext_data 承载的利率/建档来源信息无关，不可相互替代。

## 版本演进
暂无版本演进记录。
---END FILE---

---FILE: concepts/archive_result_outbound.md ---
---
type: concept
title: 建档结果出站
page_key: archive_result_outbound
domain: 外部渠道与银行对接
status: draft
aliases:
  - archiveCallback
  - notifyArchiveResult
  - ITmCustEventListener
  - IAlipayAntArchiveEventListener
oid: 1
scope:
  databases:
    - cust
sources:
  - code:ITmCustEventListener
  - code:IAlipayAntArchiveEventListener
  - code:TianmaConsumer
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
also_confused_with:
  - cust_company_info.check_status
adjudication: boundary
---

> (document_claim，未证实)

「建档结果出站」指把本地建档结果回推给渠道方的能力，各渠道实现方式不同。

## 需求背景
蚂蚁渠道为 Dubbo 事件 → FBP 通知（有效）；天马渠道的出站逻辑仅存在于已整体注释的 TianmaConsumer，实际未生效，因此天马侧不能按有效链路理解。出站结果的状态依据是建档状态而非审核状态，二者边界见 [[company_archive]] 与 [[check_status]]。

## 版本演进
- (document_claim，未证实) 天马客户信息同步出站：产融内部事件 → TmCustEventListener → BeanUtils.copyProperties 至 CompanyArchivePushReq → 日期格式化为 yyyy-MM-dd → TianmaService.companyArchiveDetail → HTTP POST。该主张在代码侧被证伪：TianmaConsumer 整文件被块注释，@RabbitListener/@Component/@Autowired 均被注释，实际未生效。
- (document_claim，未证实) HSCC 蜂巢出站：WhhimService 组装 → Md5Utils 签名 → WhhimHttpClientOpenApiClient → 失败抛 WhhimOpenApiException。本次链路未覆盖对应类，待补证。
---END FILE---

---FILE: rules/inbound_all_tenant_context.md ---
---
type: rule
title: 入站渠道全租户上下文
page_key: inbound_all_tenant_context
domain: 外部渠道与银行对接
status: draft
aliases:
  - 入站租户上下文置 all
oid: 1
scope:
  databases:
    - cust
sources:
  - code:TianmaController.companyArchive
  - code:AlipayAntArchiveController.channelArchive
  - code:CustAccessApplication.validateSetValue
  - code_path:lowcode-pplatform-openapi/lowcode-pplatform-openapi-non-standard-tianma/.../controller/TianmaController.java#companyArchive
contract_version: "0.1"
---

天马与蚂蚁渠道入站控制器在入口处先把数据租户上下文置为 `all`，再依据渠道秘钥定位真实租户。

## 需求背景
跨租户检索是渠道建档查重的前提（同一信用代码可能已在其他租户下存在），但落库必须回到真实租户，否则归属错误。该规则是 [[channel_enable_filter]] 与 [[company_certification_tenant_match]] 的前置条件，租户语义见 [[tenant]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 入站渠道全租户上下文
content: 天马/蚂蚁渠道入站控制器入口先执行 MetaDataThreadLocalConfig.setDbTenantCode("all")，随后由渠道秘钥(cust_access_secret)定位真实租户
impact: 跨租户检索与落库租户归属
field_targets:
  - cust_company_info.db_tenant_code
  - cust_access_secret.channel
evidence: "code:TianmaController.companyArchive; AlipayAntArchiveController.channelArchive; CustAccessApplication.validateSetValue + code_path:lowcode-pplatform-openapi/lowcode-pplatform-openapi-non-standard-tianma/.../controller/TianmaController.java#companyArchive + reqdoc:tianma-supplier-company-archive-inbound"
```
---END FILE---

---FILE: rules/tianma_default_supplier.md ---
---
type: rule
title: 天马默认企业类型为供应商
page_key: tianma_default_supplier
domain: 外部渠道与银行对接
status: draft
aliases:
  - 天马默认 SPY
oid: 1
scope:
  databases:
    - cust
sources:
  - code:TianmaService.companyArchive
  - code:CustAccessApplication.getCompanyType
contract_version: "0.1"
---

天马建档请求未传 companyType 时，按供应商角色落库。

## 需求背景
天马渠道的业务场景以供应商建档为主，缺省即视为供应商可避免渠道侧必填改造；内部映射见 [[company_type]]，落库字段见 [[cust_company_info]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 天马默认企业类型为供应商
content: 天马建档请求 companyType 为空时按 CompanyType.SPY 落库（内部映射 CustCompanyTypeEnum.SUPPLIER）
impact: cust_company_info.cust_company_type 取值
field_targets:
  - cust_company_info.cust_company_type
evidence: "code:TianmaService.companyArchive; CustAccessApplication.getCompanyType"
```
---END FILE---

---FILE: rules/independent_archive_validation.md ---
---
type: rule
title: 自主/非自主建档校验分档
page_key: independent_archive_validation
domain: 外部渠道与银行对接
status: draft
aliases:
  - 建档校验分档
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.validateMedia
  - code:CustAccessApplication.validateBank
contract_version: "0.1"
---

建档校验按是否自主（isIndependent）分两档：自主建档对联系人/法人证件与手机号做非空后校验，非自主建档强制校验并须提交完整影像与供应商银行三要素。

## 需求背景
非自主建档由渠道代客提交，资料完整性完全依赖渠道，因此准入与影像要求更严；影像落地依赖 [[sftp_channel_enable]]，银行三要素落点见 [[cust_account_info]]，概念背景见 [[company_archive]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 自主/非自主建档校验分档
content: 自主建档(isIndependent=true)对联系人/法人证件与手机号做非空后校验；非自主建档强制校验且必须提交授权书+法人正反面+经办人正反面+营业执照影像及供应商银行三要素
impact: 建档准入与影像完整性
field_targets:
  - cust_company_info.certification_no
  - cust_account_info.bank_no
evidence: "code:CustAccessApplication.validateSetValue / validateMedia / validateBank"
```
---END FILE---

---FILE: rules/cert_expiry_9999_permanent.md ---
---
type: rule
title: 证件有效期 9999 视为长期
page_key: cert_expiry_9999_permanent
domain: 外部渠道与银行对接
status: draft
aliases:
  - 长期有效标识
  - timePermanent YES
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.setCustCompany
  - code:CustAccessApplication.initCustOfTianma
contract_version: "0.1"
---

证件有效期以 JSON 表达，到期日以 `9999` 开头时 status=YES 表示长期有效，否则 NO。

## 需求背景
营业执照与法人身份证共用同一表达方式，同时写入对应到期时间字段，便于运营侧直接索引；字段定义见 [[cust_company_info]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 证件有效期 9999 视为长期
content: 到期日以 9999 开头时 JSON status=YES，否则 NO；同时写 business_license_end_time / legal_certification_end_time
impact: 营业执照与法人证件有效期表达
field_targets:
  - cust_company_info.time_permanent
  - cust_company_info.legal_time_permanent
evidence: "code:CustAccessApplication.setCustCompany / initCustOfTianma"
```
---END FILE---

---FILE: rules/legal_phone_not_overwrite.md ---
---
type: rule
title: 变更时法人手机空值不覆盖
page_key: legal_phone_not_overwrite
domain: 外部渠道与银行对接
status: draft
aliases:
  - legalPhone 空值保护
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.updateSystemData
contract_version: "0.1"
---

企业变更时若法人手机号入参为空或空白，不覆盖库中旧值。

## 需求背景
在途建档会把法人手机号推送至运营，若变更请求携带空值直接落库会造成运营侧联系人缺失；因此保留旧值优先。字段见 [[cust_company_info]]，变更流程前置见 [[cust_status]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 变更时法人手机空值不覆盖
content: updateSystemData 中法人手机号为空/空白时保留库中旧值，避免在途建档推运营为空
impact: cust_company_info.legal_phone 不被清空
field_targets:
  - cust_company_info.legal_phone
evidence: "code:CustAccessApplication.updateSystemData"
```
---END FILE---

---FILE: rules/default_product_route_acflow.md ---
---
type: rule
title: 产品路由默认 ACFLOW
page_key: default_product_route_acflow
domain: 外部渠道与银行对接
status: draft
aliases:
  - 默认产品码 ACFLOW
  - allowedProductCodes
oid: 1
scope:
  databases:
    - cust
sources:
  - code:ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured
  - code:ClientProjectAlipayClearingConfigSyncService.getAppId
  - code:BocomQueryAccountByXylClientService.getAppId
  - code:CpcnBankProviderImpl.allowedProductCodes
contract_version: "0.1"
---

清分相关查询在 productCode 为空时按 ACFLOW 兜底；交e保清分银行卡查询的允许产品由 Nacos 配置 `bocom.clearing.allowedProductCodes` 控制，默认 ACFLOW、RVSFACTOR_PC。

## 需求背景
渠道请求常不带产品维度，缺省兜底保证路由可预测；配置化白名单则允许运营在不发版的前提下调整可查产品范围。业务背景见 [[clearing]]，回填落点见 [[cust_account_info]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 产品路由默认 ACFLOW
content: 支付宝清分配置查询 productCode 为空时默认 ACFLOW；交e保清分银行卡查询的允许产品为 Nacos 配置 bocom.clearing.allowedProductCodes(默认 ACFLOW,RVSFACTOR_PC)
impact: 渠道请求的产品维度与 RpcAppVo 路由
field_targets: []
evidence: "code:ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured; ClientProjectAlipayClearingConfigSyncService.getAppId; BocomQueryAccountByXylClientService.getAppId; CpcnBankProviderImpl.allowedProductCodes"
```
---END FILE---

---FILE: rules/ant_archive_error_mapping.md ---
---
type: rule
title: 蚂蚁建档错误码映射
page_key: ant_archive_error_mapping
domain: 外部渠道与银行对接
status: draft
aliases:
  - AntArchiveErrorMapper
  - 201110~201121
oid: 1
scope:
  databases:
    - cust
sources:
  - code:AntArchiveErrorMapper.toResponse
  - code:AntArchiveErrorMapper.mapCaOrBusinessCode
contract_version: "0.1"
---

蚂蚁渠道建档的异常按消息前缀映射为稳定错误码，便于渠道方定位问题。

## 需求背景
映射区间为 201110~201114（CA_CERT_PARAM_INVALID / INIT_PARAM_MISSING / INFO_INCOMPLETE / REALNAME_* / INTENT_UNSUPPORTED）、sftp 与影像类 201120、协议告知与影像类 201121；含「企业已建档」映射为 REG_EXIST_EXCEPTION，非业务异常统一 SERVER_BUSY。渠道侧语义见 [[channel]]，查重相关口径见 [[build_fail_reusable]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 蚂蚁建档错误码映射
content: 消息前缀 CA_CERT_PARAM_INVALID/INIT_PARAM_MISSING/INFO_INCOMPLETE/REALNAME_*/INTENT_UNSUPPORTED 依次映射 201110~201114，sftp/影像→201120，协议告知与影像→201121；含"企业已建档"→REG_EXIST_EXCEPTION；非业务异常→SERVER_BUSY
impact: 渠道方错误语义可读性
field_targets: []
evidence: "code:AntArchiveErrorMapper.toResponse / mapCaOrBusinessCode"
```
---END FILE---

---FILE: rules/zip_unzip_safety.md ---
---
type: rule
title: 影像 zip 解压安全阈值
page_key: zip_unzip_safety
domain: 外部渠道与银行对接
status: draft
aliases:
  - unzipSafely
  - zip 炸弹防护
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.unzipSafely
  - code:CustAccessApplication.resolveZipEntry
contract_version: "0.1"
---

渠道上传影像压缩包解压时设双重防护：解压总字节超过 512MB 主动中断；entry 归一化后必须落在目标目录内，防止 zip 炸弹与路径穿越。

## 需求背景
影像由外部渠道提供，属于不可信输入；该防护是非自主建档影像入库的前置条件（[[independent_archive_validation]]），通道配置见 [[cust_sftp]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 影像 zip 解压安全阈值
content: 解压总字节超过 512MB 主动中断；entry 归一化后必须落在目标目录内，防 zip 炸弹与路径穿越
impact: 渠道影像入库安全性
field_targets: []
evidence: "code:CustAccessApplication.unzipSafely / resolveZipEntry"
```
---END FILE---

---FILE: rules/oper_platform_id_priority.md ---
---
type: rule
title: 运营企业ID冲突以 cust_role_info 为准
page_key: oper_platform_id_priority
domain: 外部渠道与银行对接
status: draft
aliases:
  - plat_cust_id 冲突处理
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.resolveBuildPlatformCustIdForOper
contract_version: "0.1"
---

建档记录与角色表记录的运营中台企业 ID 不一致时，告警并取角色表值。

## 需求背景
该值决定是否拉起/终止中台流程，取错会导致流程挂空或误终止。涉及表见 [[cust_build_record]]、[[cust_role_info]]，判定口径见 [[oper_platform_id_consistency]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 运营企业ID冲突以 cust_role_info 为准
content: cust_build_record.plat_cust_id 与 cust_role_info.platform_cust_id 不一致时告警并取 role 值
impact: 是否拉起/终止中台流程的判定
field_targets:
  - cust_build_record.plat_cust_id
  - cust_role_info.platform_cust_id
evidence: "code:CustAccessApplication.resolveBuildPlatformCustIdForOper"
```
---END FILE---

---FILE: rules/build_terminated_todo_compensation.md ---
---
type: rule
title: 未拉起中台流程时的待办补偿
page_key: build_terminated_todo_compensation
domain: 外部渠道与银行对接
status: draft
aliases:
  - 终止建档待办关单
  - NOTICE_TASK_INVITE_AUTH_CUST_INPUT
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.completeBuildTerminatedWithoutOperTodos
contract_version: "0.1"
---

终止建档且 hasOperFlow=false 时，按 identify_style 映射待办场景主动关单，保证待办一致性。

## 需求背景
映射关系为 INVITE→NOTICE_TASK_INVITE_AUTH_CUST_INPUT、INVITE_AGW→NOTICE_TASK_INVITE_AUTH_SYS_INPUT、其余→NOTICE_COMPANY_BUILD_AUTH。identify_style 取值见 [[cust_company_info]]，终止后的状态走向见 [[cust_build_status]] 与 [[cust_check_status]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 未拉起中台流程时的待办补偿
content: 终止建档且 hasOperFlow=false 时按 identify_style 映射待办场景（INVITE→NOTICE_TASK_INVITE_AUTH_CUST_INPUT，INVITE_AGW→NOTICE_TASK_INVITE_AUTH_SYS_INPUT，其余→NOTICE_COMPANY_BUILD_AUTH）主动关单
impact: 渠道建档终止后的待办一致性
field_targets:
  - cust_company_info.identify_style
evidence: "code:CustAccessApplication.completeBuildTerminatedWithoutOperTodos"
```
---END FILE---

---REVIEW: process | 企业审核状态---
问题：语义分析中两处对 check_status 落库值的写法不一致。
- field_semantics.check_status：落库为 OperApiConstants.CheckStatus 的 .name()，值为 `CUST_CHECK_INIT/CHECKING/PASS/REJECT/BACKTOCUSTOM/CUST_BACK`（疑似省略前缀的简写）。
- state_machines[企业审核状态].states：`CUST_CHECK_INIT` / `CUST_CHECK_CHECKING` / `CUST_CHECK_PASS` / `CUST_CHECK_REJECT` / `CUST_CHECK_BACKTOCUSTOM` / `CUST_BACK`。
v0 页面（[[cust_check_status]]、[[cust_company_info]]）采用 state_machines 的全称写法，并以 `.name()` 作为落库形式。需以 OperApiConstants.CheckStatus 源码逐字确认枚举常量名后再固化 dict。
---END REVIEW---

---REVIEW: table | cust_company_info---
问题：语义分析未提供任何列的数据库物理类型，本页 fields[].type 仅对语义中明确写为 JSON 的字段标注 `json`，其余标注 `unknown`。字段 `enable` 的 dict 仅知 `Y`（口径 predicate），未证实是否存在其它取值；`cust_company_type` 的 dict 由 concept [[company_type]] 的内部 dictKey 列表推得，未逐字来自枚举源码。建议补采 DDL 与枚举源码后回填。
---END REVIEW---

---REVIEW: concept | 建档结果出站---
问题：reqdoc 主张「HSCC 蜂巢出站：WhhimService 组装 → Md5Utils 签名 → WhhimHttpClientOpenApiClient → 失败抛 WhhimOpenApiException」在本次代码链路中未被覆盖（未出现 WhhimService/WhhimOpenApiException 类），code_status=uncovered，action=review。已按未证实内容写入 [[archive_result_outbound]] 的「版本演进」并在页首标注 (document_claim，未证实)，未产出任何锚点块。需补充该出站链路的代码证据或明确废弃。
---END REVIEW---

---REVIEW: concept | 渠道---
问题：reqdoc 主张「BR-003 签名校验：参数排序拼接 + app_secret + MD5 32 位小写，由 CryptoService 统一实现，各渠道复用 Md5Utils/TianmaUtil」在语义分析中记录不完整（action 字段被截断），code_status=uncovered。本次链路仅见 TianmaUtil.post 的调用点（TianmaService.companyArchiveDetail），未见 CryptoService/Md5Utils 实现，故签名算法细节（排序规则、编码、是否含空值）全部待确认，未写入任何锚点块。同时该主张与「天马出站逻辑未生效」的结论存在交叉，需一并核实。
---END REVIEW---