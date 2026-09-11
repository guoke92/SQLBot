---FILE: tables/cust_company_info.md ---
---
type: table
title: 客户企业信息表
page_key: tables/cust_company_info
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_company_info
  - CustCompanyInfoDO
  - 客户企业信息
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustCompanyInfoDO
  - code:CustAccessApplication
  - code:TianmaService#companyArchive
  - code:AlipayAntArchiveService#channelArchive
contract_version: "0.1"
---

# 客户企业信息表 cust_company_info

## 业务定位

`cust_company_info` 是客户企业主数据表，是外部渠道（天马、支付宝蚂蚁）入站建档与标准开放接口建档/变更落库的最终载体。它同时承担三种职责：以 `certification_no`（统一社会信用代码）承担企业唯一识别键，以 `db_tenant_code` 承担多租户隔离键，以 `cust_status` / `cust_build_status` / `check_status` 三列承担互相独立的流程状态。子表（person / role / account / projectRel）通过 `refCustCompanyInfo` 关联本表的业务编码 `code`，而不是主键 `id`。

渠道入站场景下，本表记录由渠道密钥表（`cust_access_secret`）反查得到的租户写入，因此单条记录的归属租户由记录自身字段决定，而非由请求上下文决定。

## 需求背景

外部渠道与银行对接要求：同一套企业主数据需要同时服务标准开放接口（自主建档 `independentReg` / 挂靠建档 `dependentReg`）、天马入站建档（`companyArchiveOfTianma`）与渠道统一入站建档（`channelArchive`）三条入口。三条入口共用本表，因此本表需要通过 `cust_build_status` 表达"是否已建档/是否建档失败可复用"、通过 `check_status` 表达审核进度、通过 `cust_status` 表达企业生命周期（新增/变更/注销），并通过 `enable` 承担"有效企业"这一最基础的过滤口径。建档来源与录入方式分别由 `cust_source` / `cust_from` / `identify_style` 区分（自主建档为 `INVITE`，挂靠建档为 `INVITE_AGW`）。

## 版本演进

- v0.1（本页首版）：全部内容来自代码语义分析，尚无需求文档或变更单佐证。

```ground:field
table: cust_company_info
fields:
  - name: id
    meaning: 表主键，雪花ID（@TableId IdType.ASSIGN_ID）
    evidence: code
  - name: code
    meaning: 客户业务编码；子表（person/role/account/projectRel）通过 refCustCompanyInfo 关联此编码
    evidence: code
  - name: name
    meaning: 客户名称（企业全称），建档重复校验的第一匹配键
    evidence: code
  - name: certification_no
    meaning: 统一社会信用代码，法人/企业唯一标识，建档重复校验与银行账户查询的主键之一
    evidence: code
  - name: cust_company_type
    meaning: 企业角色，JSON 数组字符串（如 ["SUPPLIER"]），查询时用 like 模糊匹配（query/batchQuery/changeCompanyInfo）
    evidence: code
  - name: cust_status
    meaning: 客户状态：ADD / CHANGE / WRITEOFF（CustStatusConstant、CustStatusEnum）
    evidence: code
  - name: cust_build_status
    meaning: 建档/认证状态（DO 注解为『认证状态』），值取自 CustBuildStatusEnum/CustBuildStatusConstant：INIT / BUILDING / CUST_CONFIRM_AWAIT / BUILD_SUCCESS / BUILD_FAIL
    evidence: code
  - name: check_status
    meaning: 审核状态，值取自 OperApiConstants.CheckStatus：CUST_CHECK_INIT / CUST_CHECK_CHECKING / CUST_CHECK_PASS / CUST_CHECK_REJECT / CUST_BACK / CUST_CHECK_BACKTOCUSTOM
    evidence: code
  - name: db_tenant_code
    meaning: 数据租户标识（多租户隔离键）；渠道入站/开放接口建档时被强制置为 'all' 或由渠道密钥决定
    evidence: code
  - name: app_tenant_code
    meaning: 逻辑租户标识
    evidence: code
  - name: remark
    meaning: 备注；开放接口查询建档状态时作为 checkDesc（退回原因）回传
    evidence: code
  - name: enable
    meaning: 启用标识 Y/N（EnableEnum），所有查询均带 enable='Y'
    evidence: code
  - name: identify_style
    meaning: 认证方式/录入方式：IdentifyTypeConstant.INVITE（企业录入）、INVITE_AGW（系统录入）；自主建档为 INVITE，挂靠建档为 INVITE_AGW
    evidence: code
  - name: third_auth_status
    meaning: 第三方认证状态，建档时取自入参 authStatus
    evidence: code
  - name: ca_register_status
    meaning: CA 开通状态，建档初始化固定写 EnableEnum.N
    evidence: code
  - name: bs_register_status
    meaning: 上上签开通状态
    evidence: code
  - name: need_register_ca
    meaning: 是否开通电子签章，建档初始化固定写 EnableEnum.Y
    evidence: code
  - name: need_register_bs
    meaning: 是否需要开通上上签
    evidence: code
  - name: time_permanent
    meaning: 营业执照有效期 JSON：{"start":null,"end":yyyy-MM-dd,"status":"YES|NO"}；end 以 9999 开头视为长期，status=YES
    evidence: code
  - name: legal_time_permanent
    meaning: 法人证件有效期 JSON，结构同 time_permanent（end/status 语义一致）
    evidence: code
  - name: business_license_start_time
    meaning: 企业营业执照开始时间（结构化列，与 time_permanent 同步写）
    evidence: code
  - name: business_license_end_time
    meaning: 企业营业执照结束时间
    evidence: code
  - name: legal_certification_start_time
    meaning: 法人证件开始日期
    evidence: code
  - name: legal_certification_end_time
    meaning: 法人证件结束日期
    evidence: code
  - name: legal_name
    meaning: 法人姓名
    evidence: code
  - name: legal_certification_no
    meaning: 法人证件号
    evidence: code
  - name: legal_certification_type
    meaning: 法人证件类型，由 IDTypeEnum 映射（默认 CRET_ID）
    evidence: code
  - name: legal_phone
    meaning: 法人手机号；变更场景未传/空白时不覆盖库中值
    evidence: code
  - name: company_ext_data
    meaning: 企业拓展字段 JSON；天马建档写入 interestRate（CompantExtConstants.INTEREST_RATE，综合利率），怡亚通租户写入 BUILD_STYPE=INVITE_AGW
    evidence: code
  - name: head_company
    meaning: 是否总公司，建档初始化固定写 Y
    evidence: code
  - name: platform_cust_id
    meaning: 运营中台客户 ID（另可由 cust_build_record.plat_cust_id、cust_role_info.platform_cust_id 解析）
    evidence: code
  - name: cust_source
    meaning: 建档数据来源
    evidence: code
  - name: cust_from
    meaning: 客户来源
    evidence: code
  - name: data_type
    meaning: 数据类型：'1' 主数据、'0' 记录数据
    evidence: code
  - name: main_data_id
    meaning: 主数据 id
    evidence: code
  - name: regist_city
    meaning: 注册市名称；city_code/parent_code 由 address 表（AddressDO.fullName）反查填充
    evidence: code
  - name: regist_city_code
    meaning: 注册城市代码
    evidence: code
  - name: regist_province
    meaning: 注册省份
    evidence: code
  - name: regist_province_code
    meaning: 注册省份代码
    evidence: code
  - name: regist_province_city
    meaning: 注册省市 JSON（province/provinceName/city/cityName）
    evidence: code
  - name: registered_address
    meaning: 注册地址
    evidence: code
  - name: cust_short_name
    meaning: 企业简称
    evidence: code
  - name: cust_english_name
    meaning: 客户英文名称
    evidence: code
  - name: cust_former_name
    meaning: 曾用名
    evidence: code
```

## 关联页面

- 术语：[[concepts/channel]]、[[concepts/reg_archive]]、[[concepts/company_status_fields]]、[[concepts/tianma_inbound_outbound]]
- 流程：[[processes/cust_build_status_machine]]、[[processes/cust_check_status_machine]]、[[processes/cust_status_machine]]
- 口径：[[calibers/channel_tenant_mapping]]、[[calibers/all_tenant_context]]、[[calibers/cust_company_info_enable_active]]
- 规则：[[rules/channel_archive_unified_entry]]、[[rules/nonstandard_inbound_all_tenant]]

---REVIEW: table | 客户企业信息表---
`scope.databases` 暂填 `unknown`：语义分析仅提供代码侧证据（DO 类名与字段语义），未给出 `cust_company_info` 的物理库名。请在拿到数据源配置或建表 DDL 后回填物理库名，并把 `contract_version` 提升到 0.2。
---END REVIEW---

---END FILE---

---FILE: processes/cust_build_status_machine.md ---
---
type: process
title: 客户建档/认证状态机
page_key: processes/cust_build_status_machine
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_build_status
  - CustBuildStatusEnum
  - CustBuildStatusConstant
  - 建档状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustBuildStatusEnum
  - code:CustBuildStatusConstant
  - code:CustAccessApplication#terminateBuildingFlow
contract_version: "0.1"
---

# 客户建档/认证状态机

## 业务定位

该状态机由 `cust_company_info.cust_build_status` 承载，字段在 DO 中注解为「认证状态」，是外部渠道与标准接口判断"这家企业是否已经完成建档、是否还能被重新建档"的核心依据。它决定了重复建档校验是否放行：只有 `BUILD_FAIL` 状态允许复用旧企业记录覆盖写（详见 [[calibers/build_fail_reusable]]），`BUILD_SUCCESS` 则会被 [[calibers/standard_api_registered]] 拦截并抛 `REG_EXIST_EXCEPTION`。

## 需求背景

渠道重新建档会出现"上一次流程还挂在建档中/待企业确认"的悬挂情况。为让渠道侧可以重开流程，标准接口在建档前会做旧流程终止：若存在运营流程（`hasOperFlow` 分支），调用运营中台 `completeRejectProcess` 终止旧流程，随后在本地落状态。这一终止动作是当前代码中唯一可确认的 `cust_build_status` 状态迁移来源。

## 版本演进

- v0.1（本页首版）：状态枚举与唯一迁移均来自代码语义分析，尚无需求文档或变更单佐证。

```ground:state_machine
name: 客户建档/认证状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 建档初始化
    source: code_enum
  - value: BUILDING
    label: 建档中
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待企业确认
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败（可重新建档）
    source: code_enum
transitions:
  - from: "BUILDING|CUST_CONFIRM_AWAIT"
    event: 标准接口重新建档时终止旧流程（hasOperFlow 分支调用运营中台 completeRejectProcess，随后本地落状态）
    to: BUILD_FAIL
    evidence: "code_path:lowcode-pplatform-customer-management/.../cust/application/CustAccessApplication.java#terminateBuildingFlow"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 口径：[[calibers/build_fail_reusable]]、[[calibers/standard_api_registered]]、[[calibers/cust_company_info_enable_active]]
- 术语：[[concepts/reg_archive]]、[[concepts/company_status_fields]]
- 规则：[[rules/channel_archive_unified_entry]]

---END FILE---

---FILE: processes/cust_check_status_machine.md ---
---
type: process
title: 客户审核状态机
page_key: processes/cust_check_status_machine
domain: 外部渠道与银行对接
status: draft
aliases:
  - check_status
  - OperApiConstants.CheckStatus
  - 审核状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:OperApiConstants.CheckStatus
  - code:CustAccessApplication#terminateBuildingFlow
  - code:CustAccessApplication#terminateChangingFlow
contract_version: "0.1"
---

# 客户审核状态机

## 业务定位

该状态机由 `cust_company_info.check_status` 承载，取值为 `OperApiConstants.CheckStatus` 下的 `CUST_CHECK_*` 常量族，描述企业建档资料在审核链路上的位置。它与建档状态（[[processes/cust_build_status_machine]]）彼此独立：同一企业可以"建档成功但审核退回"。

对外接口并不直接回传库内枚举，而是先做 `CheckStatus → RegStatus` 映射（`CUSTS001~CUSTS005` / `CUST404`）后再返回，因此 `CUSTS*` 属于开放接口协议值，不能当库存值使用（见 [[concepts/company_status_fields]]）。

## 需求背景

渠道重新建档或重新变更时，旧流程可能停在 `CUST_CHECK_CHECKING`。标准接口终止旧流程后统一落到 `CUST_CHECK_REJECT`：终止建档流程走 `terminateBuildingFlow`，终止运营变更流程走 `terminateChangingFlow`（该方法内注释说明 `changeRejectProcess` 已在库中落 `CUST_CHECK_REJECT`）。`remark` 字段在开放接口查询建档状态时作为 `checkDesc`（退回原因）回传。

## 版本演进

- v0.1（本页首版）：状态枚举与两条迁移均来自代码语义分析，尚无需求文档或变更单佐证。

```ground:state_machine
name: 客户审核状态机
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
    label: 审核拒绝/退回
    source: code_enum
  - value: CUST_BACK
    label: 退回
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户补充
    source: code_enum
transitions:
  - from: CUST_CHECK_CHECKING
    event: 标准接口终止旧建档流程
    to: CUST_CHECK_REJECT
    evidence: "code_path:lowcode-pplatform-customer-management/.../cust/application/CustAccessApplication.java#terminateBuildingFlow"
  - from: CUST_CHECK_CHECKING
    event: 标准接口终止运营变更流程（changeRejectProcess 落库）
    to: CUST_CHECK_REJECT
    evidence: "code_path:lowcode-pplatform-customer-management/.../cust/application/CustAccessApplication.java#terminateChangingFlow（方法内注释：changeRejectProcess 已在库中落 CUST_CHECK_REJECT）"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 流程：[[processes/cust_build_status_machine]]、[[processes/cust_status_machine]]
- 术语：[[concepts/company_status_fields]]、[[concepts/reg_archive]]
- 口径：[[calibers/standard_api_registered]]

---END FILE---

---FILE: processes/cust_status_machine.md ---
---
type: process
title: 客户状态机
page_key: processes/cust_status_machine
domain: 外部渠道与银行对接
status: draft
aliases:
  - cust_status
  - CustStatusEnum
  - CustStatusConstant
  - 客户状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustStatusEnum
  - code:CustStatusConstant
  - code:CustAccessApplication#validateSetValueOfTianma
contract_version: "0.1"
---

# 客户状态机

## 业务定位

该状态机由 `cust_company_info.cust_status` 承载，取值 `ADD`（新增/建档态）、`CHANGE`（变更态）、`WRITEOFF`（注销态），描述企业在客户主数据中的生命周期位置。它与建档状态、审核状态是三列互不相同的状态（见 [[concepts/company_status_fields]]）。

## 需求背景

`WRITEOFF` 在外部渠道入站场景中承担过滤职责：天马建档的重复校验使用 `notIn CustStatusConstant.WRITEOFF`，即已注销企业不参与重复判定，可被重新建档；同时 [[calibers/build_fail_reusable]] 允许 `BUILD_FAIL` 或 `WRITEOFF` 的旧记录被覆盖写。

## 版本演进

- v0.1（本页首版）：状态枚举来自代码语义分析；语义分析中该状态机的 `transitions` 为空，即当前代码未提供可确认的迁移证据，尚无需求文档或变更单佐证。

```ground:state_machine
name: 客户状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/建档态
    source: code_enum
  - value: CHANGE
    label: 变更态
    source: code_enum
  - value: WRITEOFF
    label: 注销态
    source: code_enum
transitions: []
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 口径：[[calibers/non_writeoff]]、[[calibers/build_fail_reusable]]
- 流程：[[processes/cust_build_status_machine]]、[[processes/cust_check_status_machine]]
- 术语：[[concepts/company_status_fields]]

---END FILE---

---FILE: calibers/cust_company_info_enable_active.md ---
---
type: caliber
title: 企业有效口径
page_key: calibers/cust_company_info_enable_active
domain: 外部渠道与银行对接
status: draft
aliases:
  - 企业有效口径
  - enable=Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#query
  - code:CustAccessApplication#batchQuery
  - code:CustAccessApplication#changeCompanyInfo
contract_version: "0.1"
---

# 企业有效口径

## 业务定位

`enable = 'Y'` 是 `cust_company_info` 上最基础、覆盖最广的过滤口径：所有标准开放接口的查询 / 变更 / 重复校验都带该条件，取值来自 `EnableEnum`。它回答的是"这条企业记录当前是否有效"，与 `cust_status`（新增/变更/注销）不是一回事——注销企业仍可能是 `enable='Y'` 的有效记录。

## 需求背景

渠道与银行对接场景下，企业记录存在覆盖写、复用等写路径（见 [[calibers/build_fail_reusable]]），因此查询侧需要一个稳定的"有效记录"锚点，避免把历史失效记录读出来。`enable` 承担该职责，所有查询均带 `enable='Y'`。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 企业有效口径
predicate: "cust_company_info.enable = 'Y'"
scope: 所有标准开放接口查询/变更/重复校验
evidence: "code:CustAccessApplication#query / #batchQuery / #changeCompanyInfo（eq(CustCompanyInfoDO::getEnable, EnableEnum.Y.name())）"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/non_writeoff]]、[[calibers/standard_api_registered]]、[[calibers/batch_query_limit]]
- 术语：[[concepts/company_status_fields]]

---END FILE---

---FILE: calibers/non_writeoff.md ---
---
type: caliber
title: 非注销企业口径
page_key: calibers/non_writeoff
domain: 外部渠道与银行对接
status: draft
aliases:
  - 非注销企业口径
  - notIn WRITEOFF
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#validateSetValueOfTianma
  - code:CustStatusConstant
contract_version: "0.1"
---

# 非注销企业口径

## 业务定位

该口径规定：天马渠道建档做企业重复校验时，需排除 `cust_status = 'WRITEOFF'`（已注销）的企业记录。它限定的是"哪些记录算作可冲突的存量企业"，只作用于天马建档校验路径 `validateSetValueOfTianma`，不是全局查询条件。

## 需求背景

天马入站建档需要允许对已注销企业重新建档，因此重复校验必须以 `notIn CustStatusConstant.WRITEOFF` 缩小存量集合；与它配合的是 [[calibers/build_fail_reusable]]（`BUILD_FAIL` 也放行）。二者共同决定天马渠道的"可复用/可重开"边界。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 非注销企业口径
predicate: "cust_company_info.cust_status <> 'WRITEOFF'"
scope: 天马建档重复校验（notIn CustStatusConstant.WRITEOFF）
evidence: "code:CustAccessApplication#validateSetValueOfTianma"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/build_fail_reusable]]、[[calibers/cust_company_info_enable_active]]
- 流程：[[processes/cust_status_machine]]
- 术语：[[concepts/tianma_inbound_outbound]]

---END FILE---

---FILE: calibers/build_fail_reusable.md ---
---
type: caliber
title: 建档失败可复用口径
page_key: calibers/build_fail_reusable
domain: 外部渠道与银行对接
status: draft
aliases:
  - 建档失败可复用口径
  - BUILD_FAIL 复用
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#initCust
  - code:CustAccessApplication#initCustOfTianma
  - code:CustAccessApplication#validateSetValueOfTianma
contract_version: "0.1"
---

# 建档失败可复用口径

## 业务定位

该口径规定：当存量企业记录的 `cust_build_status = 'BUILD_FAIL'` 时，建档初始化允许复用这条旧记录覆盖写，而不是新建一条企业记录。天马渠道的重复校验也对 `BUILD_FAIL` 放行。它是渠道重复建档能"重开一次"的数据层基础。

## 需求背景

渠道入站建档可能中途失败，若每次重试都新建记录，会产生同一统一社会信用代码下的多条企业记录。因此在 `initCust` / `initCustOfTianma` 中把 `BUILD_FAIL`（以及 `WRITEOFF`，见 [[calibers/non_writeoff]]）旧记录纳入可覆盖写的范围。与之相对的拦截口径是 [[calibers/standard_api_registered]]。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 建档失败可复用口径
predicate: "cust_company_info.cust_build_status = 'BUILD_FAIL'"
scope: initCust/initCustOfTianma 允许复用旧企业记录（BUILD_FAIL 或 WRITEOFF）覆盖写；天马重复校验对 BUILD_FAIL 放行
evidence: "code:CustAccessApplication#initCust / #initCustOfTianma / #validateSetValueOfTianma"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 流程：[[processes/cust_build_status_machine]]
- 相关口径：[[calibers/standard_api_registered]]、[[calibers/non_writeoff]]、[[calibers/cust_company_info_enable_active]]
- 术语：[[concepts/reg_archive]]

---END FILE---

---FILE: calibers/standard_api_registered.md ---
---
type: caliber
title: 标准接口已建档口径
page_key: calibers/standard_api_registered
domain: 外部渠道与银行对接
status: draft
aliases:
  - 标准接口已建档口径
  - 企业已建档！
  - REG_EXIST_EXCEPTION
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#validateSetValue
contract_version: "0.1"
---

# 标准接口已建档口径

## 业务定位

该口径是标准开放接口建档的前置校验：以「统一社会信用代码 + 数据租户」为组合键统计存量记录，且排除 `cust_build_status = 'BUILD_FAIL'` 的记录；命中即判定"企业已建档"，抛 `REG_EXIST_EXCEPTION`（提示语『企业已建档！』）。它是 `independentReg` / `dependentReg` 两条入口共用的拦截规则。

## 需求背景

同一租户下同一统一社会信用代码只允许存在一条有效建档记录，否则后续银行账户查询、清分配置等以 `certification_no` 为键的下游能力会出现歧义（参见 [[calibers/bocom_account_existence]]）。因此标准接口在入口处即做拦截，而不依赖下游。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 标准接口已建档口径
predicate: "count(cust_company_info.certification_no = ? AND cust_company_info.db_tenant_code = ? AND cust_company_info.cust_build_status <> 'BUILD_FAIL') <> 0"
scope: independentReg/dependentReg 前置校验，命中抛 REG_EXIST_EXCEPTION『企业已建档！』
evidence: "code:CustAccessApplication#validateSetValue"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/build_fail_reusable]]、[[calibers/channel_tenant_mapping]]、[[calibers/cust_company_info_enable_active]]
- 术语：[[concepts/reg_archive]]、[[concepts/company_status_fields]]

---END FILE---

---FILE: calibers/channel_tenant_mapping.md ---
---
type: caliber
title: 渠道-租户映射口径
page_key: calibers/channel_tenant_mapping
domain: 外部渠道与银行对接
status: draft
aliases:
  - 渠道-租户映射口径
  - cust_access_secret
  - 渠道不存在
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#validateSetValue
  - code:CustAccessApplication#getDbTenantCode
  - code:CustAccessApplication#validateChangeChannelAndTenant
contract_version: "0.1"
---

# 渠道-租户映射口径

## 业务定位

该口径规定：外部渠道入站的企业数据必须落在哪个租户，不由请求参数决定，而是由渠道密钥表反查决定——以 `cust_access_secret.channel = ? AND enable = 'Y'` 查到映射行，取其 `db_tenant_code` 作为本次写入/查询的租户。查不到则抛『渠道不存在』。建档、查询、变更三条路径均使用该口径。

## 需求背景

渠道（天马、支付宝蚂蚁）与租户之间是多对一/一对多的关系，渠道方不应也无法自行指定租户；把租户归属收敛到渠道密钥表，可以让平台侧通过配置开关渠道数据去向，避免渠道伪造租户。相关写入字段见 [[tables/cust_company_info]] 的 `db_tenant_code`。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 渠道-租户映射口径
predicate: "cust_access_secret.channel = ? AND cust_access_secret.enable = 'Y' → db_tenant_code"
scope: 渠道入站建档、查询、变更均以渠道密钥表反查租户；查不到抛『渠道不存在』
evidence: "code:CustAccessApplication#validateSetValue / #getDbTenantCode / #validateChangeChannelAndTenant"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 术语：[[concepts/channel]]
- 相关口径：[[calibers/all_tenant_context]]、[[calibers/standard_api_registered]]
- 规则：[[rules/tianma_channel_key]]、[[rules/channel_archive_unified_entry]]

---END FILE---

---FILE: calibers/all_tenant_context.md ---
---
type: caliber
title: 全租户上下文口径
page_key: calibers/all_tenant_context
domain: 外部渠道与银行对接
status: draft
aliases:
  - 全租户上下文口径
  - dbTenantCode = all
  - MethDataThreadLocalConfig
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaController#companyArchive
  - code:AlipayAntArchiveController#channelArchive
  - code:CustAccessApplication#reg
  - code:CustAccessApplication#query
  - code:CustAccessApplication#batchQuery
  - code:CustAccessApplication#changeCompanyInfo
contract_version: "0.1"
---

# 全租户上下文口径

## 业务定位

该口径规定：渠道入站与标准开放接口在处理前，把线程上下文租户置为 `"all"`（`MethDataThreadLocalConfig.setDbTenantCode("all")`），从而使跨租户检索/写入成为可能；`changeCompanyInfo` 则在 `finally` 中还原原租户。它约束的是"这次操作能看见哪些租户的数据"，而不是数据最终落在哪个租户。

## 需求背景

渠道方在入站时并不知道目标租户，且同一渠道可能服务多个租户，因此必须以全租户上下文执行查询与落库；真正的租户归属由 [[calibers/channel_tenant_mapping]] 从渠道密钥表解析后写入记录自身字段。两者是"检索可见范围"与"数据归属"的分工，不可混淆。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 全租户上下文口径
predicate: "dbTenantCode = 'all'"
scope: "MethDataThreadLocalConfig.setDbTenantCode(\"all\")，用于渠道入站与开放接口跨租户检索；changeCompanyInfo 在 finally 中还原原租户"
evidence: "code:TianmaController#companyArchive / AlipayAntArchiveController#channelArchive / CustAccessApplication#reg、#query、#batchQuery、#changeCompanyInfo"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/channel_tenant_mapping]]
- 规则：[[rules/nonstandard_inbound_all_tenant]]、[[rules/channel_archive_unified_entry]]
- 术语：[[concepts/channel]]

---END FILE---

---FILE: calibers/batch_query_limit.md ---
---
type: caliber
title: 批量查询条数上限口径
page_key: calibers/batch_query_limit
domain: 外部渠道与银行对接
status: draft
aliases:
  - 批量查询条数上限口径
  - batchQuery 100
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#batchQuery
contract_version: "0.1"
---

# 批量查询条数上限口径

## 业务定位

该口径规定标准开放接口批量查询 `batchQuery` 的单次入参条数上限为 100 条（`size(queryReqs) <= 100`），是接口层的入参校验约束。

## 需求背景

批量查询要在全租户上下文（[[calibers/all_tenant_context]]）下按企业维度展开，单次条数不设上限会放大跨租户检索的压力；100 条是当前代码中唯一可确认的阈值。渠道接入方需按此上限拆分请求。

## 版本演进

- v0.1（本页首版）：阈值来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 批量查询条数上限口径
predicate: "size(queryReqs) <= 100"
scope: batchQuery 入参校验
evidence: "code:CustAccessApplication#batchQuery"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/all_tenant_context]]、[[calibers/cust_company_info_enable_active]]
- 规则：[[rules/nonstandard_inbound_all_tenant]]

---END FILE---

---FILE: calibers/bocom_clearing_product.md ---
---
type: caliber
title: 交e保清分产品口径
page_key: calibers/bocom_clearing_product
domain: 外部渠道与银行对接
status: draft
aliases:
  - 交e保清分产品口径
  - bocom.clearing.allowedProductCodes
  - ACFLOW
  - RVSFACTOR_PC
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CpcnBankProviderImpl#listXylCustAccountBanks
contract_version: "0.1"
---

# 交e保清分产品口径

## 业务定位

该口径规定交e保（Cpcn）银行对接在查询/遍历客户的清分银行卡时，需要按配置的产品集合逐产品查询：`productCode IN ${bocom.clearing.allowedProductCodes:ACFLOW,RVSFACTOR_PC}`。该集合由 Nacos 配置项 `bocom.clearing.allowedProductCodes` 提供，缺省为 `ACFLOW,RVSFACTOR_PC`。

## 需求背景

同一客户可能同时开通多个产品的清分账户，因此银行侧账户查询必须以产品为维度展开；把产品集合做成可配置项，可以在不发布代码的前提下调整交e保清分覆盖的产品范围。该口径与 [[calibers/alipay_clearing_default_product]] 共同构成清分产品选择规则，`productCode` 的语义见 [[concepts/product_code]]。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 交e保清分产品口径
predicate: "productCode IN ${bocom.clearing.allowedProductCodes:ACFLOW,RVSFACTOR_PC}"
scope: CpcnBankProviderImpl.listXylCustAccountBanks 遍历该集合逐产品查清分银行卡
evidence: "code:CpcnBankProviderImpl（@NacosValue bocom.clearing.allowedProductCodes）"
```

## 关联页面

- 相关口径：[[calibers/alipay_clearing_default_product]]、[[calibers/bocom_account_existence]]
- 术语：[[concepts/product_code]]
- 载体表：[[tables/cust_company_info]]

---END FILE---

---FILE: calibers/alipay_clearing_default_product.md ---
---
type: caliber
title: 支付宝清分默认产品口径
page_key: calibers/alipay_clearing_default_product
domain: 外部渠道与银行对接
status: draft
aliases:
  - 支付宝清分默认产品口径
  - 支付宝清分兜底 ACFLOW
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectAlipayClearingConfigApplication#isAlipayClearingConfigured
  - code:ClientProjectAlipayClearingConfigSyncService#getAppId
contract_version: "0.1"
---

# 支付宝清分默认产品口径

## 业务定位

该口径规定：在判断项目是否已配置支付宝清分、以及获取 `appId` 时，若产品编码入参为空，则用 `ACFLOW` 兜底。相同口径同时出现在 `ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured` 与 `ClientProjectAlipayClearingConfigSyncService.getAppId` 两处，须保持一致。

## 需求背景

支付宝渠道的清分配置是按项目+产品维度维护的，调用方在老项目中可能不传 `productCode`；为避免因缺参导致"未配置"误判，代码统一以 `ACFLOW` 作为默认产品。该默认值与交e保侧的缺省集合 [[calibers/bocom_clearing_product]] 的首项一致，二者共同把 `ACFLOW` 定位为默认清分产品（语义见 [[concepts/product_code]]）。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 支付宝清分默认产品口径
predicate: "productCode = 'ACFLOW'（入参为空时兜底）"
scope: ProjectAlipayClearingConfigApplication.isAlipayClearingConfigured；ClientProjectAlipayClearingConfigSyncService.getAppId 同口径
evidence: "code:ProjectAlipayClearingConfigApplication#isAlipayClearingConfigured"
```

## 关联页面

- 相关口径：[[calibers/bocom_clearing_product]]、[[calibers/bocom_account_existence]]
- 术语：[[concepts/product_code]]
- 载体表：[[tables/cust_company_info]]

---END FILE---

---FILE: calibers/bocom_account_existence.md ---
---
type: caliber
title: 交e保账户存在性口径
page_key: calibers/bocom_account_existence
domain: 外部渠道与银行对接
status: draft
aliases:
  - 交e保账户存在性口径
  - BocomFacade.existBocomAccount
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:BocomFacade#existBocomAccount
contract_version: "0.1"
---

# 交e保账户存在性口径

## 业务定位

该口径规定判断企业是否已开立交e保账户时的完整条件：以 `cust_company_info.certification_no` 作为 `certificationNos` 查询键，同时限定 `dbTenantCode = cust_company_info.db_tenant_code`、`platformCode='pplatform'`、`productCode='ACFLOW'`、`readLocalFlag=true`。五个条件同时满足才算"已存在交e保账户"。

## 需求背景

银行账户存在性判断必须锚定到具体的租户与产品，否则跨租户同名企业或同企业的其他产品账户会造成误判；`readLocalFlag=true` 表示只读本地数据、不外呼银行接口。该口径把 [[tables/cust_company_info]] 的 `certification_no` 与 `db_tenant_code` 作为跨系统对齐键，见 [[concepts/product_code]]。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 交e保账户存在性口径
predicate: "certificationNos = [cust_company_info.certification_no] AND dbTenantCode = cust_company_info.db_tenant_code AND platformCode='pplatform' AND productCode='ACFLOW' AND readLocalFlag=true"
scope: BocomFacade.existBocomAccount
evidence: "code:BocomFacade#existBocomAccount"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/bocom_clearing_product]]、[[calibers/channel_tenant_mapping]]
- 术语：[[concepts/product_code]]

---END FILE---

---FILE: concepts/channel.md ---
---
type: concept
title: 渠道（channel）
page_key: concepts/channel
domain: 外部渠道与银行对接
status: draft
aliases:
  - channel
  - CloudChannel
  - AlipayAntCloudChannel
  - cust_access_secret.channel
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CloudChannel
  - code:AlipayAntCloudChannel
  - code:AlipayAntArchiveController
contract_version: "0.1"
maps_to: "渠道字典键：代码中可见 CloudChannel.TIANMA.getDictKey()（天马）与 AlipayAntCloudChannel.ALIPAY_ANT（支付宝蚂蚁）；同时用作 cust_access_secret 的渠道键与 SFTP 配置（cust_sftp.channel）的键"
field_targets:
  - cust_company_info.db_tenant_code
adjudication: boundary
boundary: "渠道 ≠ URL 路径：AlipayAntArchiveController 注释明确『路径与 channel 无关，channel 完全由请求体决定』，而天马走独立 /tianma 路径。判定渠道应以渠道密钥表/请求体 channel 字段为准"
also_confused_with:
  - HTTP 路径（/tianma、/cloud/std/cust/channelArchive）
---

# 渠道（channel）

## 业务定位

"渠道"指的是外部接入来源的字典键，在代码中表现为 `CloudChannel.TIANMA.getDictKey()` 与 `AlipayAntCloudChannel.ALIPAY_ANT`。它同时是三个地方的键：渠道密钥表 `cust_access_secret` 的渠道键、SFTP 配置 `cust_sftp.channel` 的键，以及入站报文中标识来源的字段。渠道决定企业数据落到哪个租户，落库字段为 `cust_company_info.db_tenant_code`（见 [[calibers/channel_tenant_mapping]]）。

## 需求背景

平台需要以统一方式承载多个外部渠道（天马、支付宝蚂蚁等）的建档与查询请求。为避免每接一个渠道就改一次网关与路径，渠道被设计为"由请求体携带的字段"而非"由 URL 携带的字段"：统一入站入口见 [[rules/channel_archive_unified_entry]]，租户解析见 [[calibers/channel_tenant_mapping]]。

## 边界澄清

渠道 ≠ HTTP 路径。`AlipayAntArchiveController` 的类注释明确『路径与 channel 无关，channel 完全由请求体决定』，而天马渠道走的是独立 `/tianma` 路径。做渠道判定时应以渠道密钥表或请求体 `channel` 字段为准，不能以 URL 前缀推断。渠道建档与标准建档的入口差异见 [[concepts/reg_archive]]。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 口径：[[calibers/channel_tenant_mapping]]、[[calibers/all_tenant_context]]
- 规则：[[rules/channel_archive_unified_entry]]、[[rules/tianma_channel_key]]
- 概念：[[concepts/reg_archive]]、[[concepts/tianma_inbound_outbound]]
- 载体表：[[tables/cust_company_info]]

---END FILE---

---FILE: concepts/reg_archive.md ---
---
type: concept
title: 建档
page_key: concepts/reg_archive
domain: 外部渠道与银行对接
status: draft
aliases:
  - reg
  - independentReg
  - dependentReg
  - companyArchiveOfTianma
  - channelArchive
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#reg
  - code:CustAccessApplication#companyArchiveOfTianma
  - code:ChannelArchiveProvider
  - code:ChannelCustArchiveOrchestrator
contract_version: "0.1"
maps_to: "cust_company_info 建档流程：CustAccessApplication#reg(isIndependent=true/false)、#companyArchiveOfTianma、以及 ChannelArchiveProvider#execute→ChannelCustArchiveOrchestrator"
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.certification_no
adjudication: boundary
boundary: "ChannelArchiveProvider 注释明确『Orchestrator 编排，不经过 reg / companyArchiveOfTianma』，是与标准建档并列的第三条入口；天马入站走 companyArchiveOfTianma，蚂蚁入站走 ChannelArchiveProvider"
also_confused_with:
  - 渠道建档（channelArchive）
  - 天马建档（companyArchiveOfTianma）
  - 运营中台建档（submitCust）
---

# 建档

## 业务定位

"建档"指在 `cust_company_info` 中创建/初始化一条企业记录并推动其进入建档状态机的动作。它在代码中对应三条并列入口：标准开放接口的 `reg(isIndependent=true/false)`（自主建档 `independentReg` / 挂靠建档 `dependentReg`）、天马入站 `companyArchiveOfTianma`、以及渠道统一入站 `ChannelArchiveProvider#execute → ChannelCustArchiveOrchestrator`。

## 需求背景

三条入口最终都写同一张企业表（[[tables/cust_company_info]]），因此需要共享同一套重复校验与状态口径：已建档拦截见 [[calibers/standard_api_registered]]，失败可复用见 [[calibers/build_fail_reusable]]，状态流转见 [[processes/cust_build_status_machine]]。

## 边界澄清

"渠道建档（channelArchive）"是一条独立入口，不与 `reg` / `companyArchiveOfTianma` 复用同一方法链：`ChannelArchiveProvider` 的注释明确『Orchestrator 编排，不经过 reg / companyArchiveOfTianma』。天马渠道入站走 `companyArchiveOfTianma`，蚂蚁渠道入站走 `ChannelArchiveProvider`。讨论建档行为时必须先区分入口，再看落库字段。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 概念：[[concepts/channel]]、[[concepts/tianma_inbound_outbound]]、[[concepts/company_status_fields]]
- 口径：[[calibers/standard_api_registered]]、[[calibers/build_fail_reusable]]
- 流程：[[processes/cust_build_status_machine]]
- 规则：[[rules/channel_archive_unified_entry]]、[[rules/tianma_inbound_validation]]

---END FILE---

---FILE: concepts/company_status_fields.md ---
---
type: concept
title: 企业状态三字段
page_key: concepts/company_status_fields
domain: 外部渠道与银行对接
status: draft
aliases:
  - custStatus
  - custBuildStatus
  - checkStatus
  - cust_status / cust_build_status / check_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustStatusConstant
  - code:CustBuildStatusEnum
  - code:OperApiConstants.CheckStatus
contract_version: "0.1"
maps_to: "cust_company_info 的三个独立状态列：cust_status（客户状态 ADD/CHANGE/WRITEOFF）、cust_build_status（建档/认证状态 INIT/BUILDING/BUILD_SUCCESS/BUILD_FAIL/CUST_CONFIRM_AWAIT）、check_status（审核状态 CUST_CHECK_*）"
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.cust_build_status
  - cust_company_info.check_status
adjudication: boundary
boundary: "对外查询接口不直接回传库内枚举，而是 CheckStatus→RegStatus 映射后再返回；CUSTS001~CUSTS005 属于开放接口协议值，不能当库存值使用"
also_confused_with:
  - RegStatus（对外编码 CUSTS001~CUSTS005/CUST404）
  - CompanyUserStatus（AUTH0001/AUTH0003）
---

# 企业状态三字段

## 业务定位

`cust_company_info` 上有三个互相独立的状态列，分别承载三台状态机：`cust_status`（企业生命周期：ADD / CHANGE / WRITEOFF，见 [[processes/cust_status_machine]]）、`cust_build_status`（建档/认证：INIT / BUILDING / CUST_CONFIRM_AWAIT / BUILD_SUCCESS / BUILD_FAIL，见 [[processes/cust_build_status_machine]]）、`check_status`（审核：CUST_CHECK_*，见 [[processes/cust_check_status_machine]]）。

## 需求背景

外部渠道对接需要同时回答三个不同问题："这家企业还在不在（未注销）"、"这家企业的建档有没有做完"、"这家企业的资料审核到哪一步了"。三个问题各自有独立的过滤与拦截口径（[[calibers/non_writeoff]]、[[calibers/build_fail_reusable]]、[[calibers/standard_api_registered]]），因此必须是三列而非一个复合状态，三者之间不存在强制的同步迁移关系。

## 边界澄清

对外查询接口不直接回传库内枚举：先做 `CheckStatus → RegStatus` 映射，再返回 `CUSTS001~CUSTS005` / `CUST404`。因此 `CUSTS*` 是开放接口协议值，不能当作库存值参与 SQL 过滤。同样地 `CompanyUserStatus`（`AUTH0001` / `AUTH0003`）描述的是用户侧状态，不属于本表三字段体系。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 流程：[[processes/cust_status_machine]]、[[processes/cust_build_status_machine]]、[[processes/cust_check_status_machine]]
- 口径：[[calibers/non_writeoff]]、[[calibers/standard_api_registered]]
- 概念：[[concepts/reg_archive]]

---END FILE---

---FILE: concepts/product_code.md ---
---
type: concept
title: 产品编码 productCode
page_key: concepts/product_code
domain: 外部渠道与银行对接
status: draft
aliases:
  - productCode
  - platformProductCode
  - ProductCodeEnum.ACFLOW
  - refPlatformProductCode
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#validateSetValue
  - code:ProjectAlipayClearingConfigApplication#isAlipayClearingConfigured
  - code:CpcnBankProviderImpl#listXylCustAccountBanks
contract_version: "0.1"
maps_to: "平台产品编码；RPC 路由（RpcAppVo.productAppId）与清分默认产品均以此为键，代码中默认值恒为 ACFLOW"
adjudication: synonym
boundary: "productCode 是编码字符串，platformProductId 是主键 ID；validateSetValue 中由 project→TenantProductDO→PlatformProductDO→pp.getCode()/getProductCode() 逐级解析，两者不可混用"
also_confused_with:
  - tenantProductId（租户产品主键）
  - platformProductId（平台产品主键）
---

# 产品编码 productCode

## 业务定位

`productCode` 是平台产品编码字符串，在渠道与银行对接链路中承担两类键值：RPC 路由（`RpcAppVo.productAppId`）与清分产品选择。代码中默认值恒为 `ACFLOW`，相关口径见 [[calibers/alipay_clearing_default_product]]（入参为空时兜底 `ACFLOW`）与 [[calibers/bocom_clearing_product]]（交e保按配置集合逐产品查询）。

## 需求背景

银行账户查询、清分配置、RPC 路由都要求以"产品"为维度隔离数据：同一企业在不同产品下的账户与配置互不相同（见 [[calibers/bocom_account_existence]] 中同时限定 `platformCode` 与 `productCode`）。因此需要一个稳定的编码字符串在各系统间传递，`ACFLOW` 被当作缺省产品。

## 边界澄清

`productCode`（编码字符串）与 `tenantProductId`（租户产品主键）、`platformProductId`（平台产品主键）不可混用。`validateSetValue` 中通过 project → `TenantProductDO` → `PlatformProductDO` 再取 `pp.getCode()` / `getProductCode()` 逐级解析得到编码，说明主键与编码之间是多级映射关系。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 口径：[[calibers/bocom_clearing_product]]、[[calibers/alipay_clearing_default_product]]、[[calibers/bocom_account_existence]]
- 载体表：[[tables/cust_company_info]]
- 概念：[[concepts/channel]]

---END FILE---

---FILE: concepts/tianma_inbound_outbound.md ---
---
type: concept
title: 天马入站 / 天马出站
page_key: concepts/tianma_inbound_outbound
domain: 外部渠道与银行对接
status: draft
aliases:
  - TianmaService.companyArchive
  - TianmaService.companyArchiveDetail
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaService#companyArchive
  - code:TianmaService#companyArchiveDetail
  - code:TianmaConsumer
contract_version: "0.1"
maps_to: "companyArchive = 天马→产融入站建档；companyArchiveDetail = 产融→天马出站推送建档结果（baseUrl + TianmaConst.COMPANY_ARCHIVE_DETAIL）"
adjudication: boundary
boundary: "入站方法在 TianmaController 链路中真实生效；出站方法体存在，但其唯一调用方 TianmaConsumer 全类处于注释状态，出站链路当前不可用"
also_confused_with:
  - TianmaConsumer.platformCompanyAuditPassNotice（整类被注释）
---

# 天马入站 / 天马出站

## 业务定位

天马渠道有方向相反的两条链路，方法名相近但语义不同：`TianmaService.companyArchive` 是**入站**建档——天马侧把企业信息推进产融，落库到 [[tables/cust_company_info]]；`TianmaService.companyArchiveDetail` 是**出站**推送——产融把建档结果回推天马（`baseUrl` + `TianmaConst.COMPANY_ARCHIVE_DETAIL`）。

## 需求背景

入站链路需要一套严格的参数校验与默认值补齐（见 [[rules/tianma_inbound_validation]]、[[rules/tianma_default_company_type]]），并以渠道键反查租户（[[rules/tianma_channel_key]]、[[calibers/channel_tenant_mapping]]）。入站建档与标准建档、渠道统一建档是三条并列入口，参见 [[concepts/reg_archive]]。

## 边界澄清

入站方法在 `TianmaController` 链路中真实生效；出站方法体虽然存在，但其唯一调用方 `TianmaConsumer` 全类处于注释状态，出站链路当前不可用。因此涉及"天马建档结果回推"的需求时，不能假设出站已生效——需要先确认该消费者是否恢复启用。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 规则：[[rules/tianma_inbound_validation]]、[[rules/tianma_default_company_type]]、[[rules/tianma_channel_key]]
- 口径：[[calibers/channel_tenant_mapping]]、[[calibers/non_writeoff]]
- 概念：[[concepts/channel]]、[[concepts/reg_archive]]
- 载体表：[[tables/cust_company_info]]

---END FILE---

---FILE: rules/channel_archive_unified_entry.md ---
---
type: rule
title: 渠道建档统一入站入口
page_key: rules/channel_archive_unified_entry
domain: 外部渠道与银行对接
status: draft
aliases:
  - /cloud/std/cust/channelArchive
  - AlipayAntArchiveController
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:AlipayAntArchiveController
  - code:AlipayAntArchiveService#channelArchive
contract_version: "0.1"
---

# 渠道建档统一入站入口

## 业务定位

渠道建档统一使用与渠道无关的固定路径 `POST /cloud/std/cust/channelArchive`，由 `AlipayAntArchiveController`（`@RequestMapping("/cloud/std/cust")` + `@PostMapping("/channelArchive")`）承接；具体的 `channel` 由请求体决定，`AlipayAntArchiveService` 会强制 `setChannel(AlipayAntCloudChannel.ALIPAY_ANT)`。该入口刻意避开 `/cloud/std/cust/importNonIndependentCompanyInfo`。

## 需求背景

每接入一个新渠道都改网关与 URL 会带来路由与鉴权配置的重复维护。代码采取的方案是把渠道识别下沉到请求体，路径保持唯一，从而让新增渠道只需新增 Request / Service 层解析，网关与路径不需变更。这与"渠道 ≠ URL 路径"的边界判定一致，见 [[concepts/channel]]。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析，尚无需求文档或变更单佐证。

```ground:rule
name: 渠道建档统一入站入口
content: "渠道建档使用与渠道无关的固定路径 POST /cloud/std/cust/channelArchive，channel 由请求体决定（AlipayAntArchiveService 强制 setChannel(AlipayAntCloudChannel.ALIPAY_ANT)），便于后续渠道复用同一 URL；刻意避开 /cloud/std/cust/importNonIndependentCompanyInfo"
impact: 新增渠道只需新增 Request/Service 层解析，网关与路径不需变更
field_targets:
  - cust_company_info.db_tenant_code
evidence: "code:AlipayAntArchiveController（类注释 + @RequestMapping(\"/cloud/std/cust\") + @PostMapping(\"/channelArchive\")）, AlipayAntArchiveService#channelArchive"
```

## 关联页面

- 概念：[[concepts/channel]]、[[concepts/reg_archive]]
- 口径：[[calibers/channel_tenant_mapping]]、[[calibers/all_tenant_context]]
- 规则：[[rules/nonstandard_inbound_all_tenant]]
- 载体表：[[tables/cust_company_info]]

---END FILE---

---FILE: rules/nonstandard_inbound_all_tenant.md ---
---
type: rule
title: 非标入站强制全租户上下文
page_key: rules/nonstandard_inbound_all_tenant
domain: 外部渠道与银行对接
status: draft
aliases:
  - setDbTenantCode("all")
  - 非标入站全租户
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaController#companyArchive
  - code:AlipayAntArchiveController#channelArchive
  - code:CustAccessApplication#changeCompanyInfo
contract_version: "0.1"
---

# 非标入站强制全租户上下文

## 业务定位

`TianmaController` 与 `AlipayAntArchiveController` 在处理前调用 `MetaDataThreadLocalConfig.setDbTenantCode("all")`，使跨租户建档/查询可行；标准接口 `reg` / `query` / `batchQuery` 同样置 `all`，而 `changeCompanyInfo` 使用 `try/finally` 还原原租户。

## 需求背景

渠道方入站时并不携带目标租户信息，且同一渠道可能服务多个租户，因此必须在全租户可见的上下文中完成检索与落库。需要特别注意的是：全租户上下文只解决"看得见哪些租户"，数据最终归属仍由渠道密钥表解析（见 [[calibers/channel_tenant_mapping]]），并写入企业记录自身的 `db_tenant_code`。

## 影响与约束

渠道数据不落在单一租户上下文，因此后续操作涉及的租户必须由企业记录自身的 `db_tenant_code` 决定，而不能依赖线程上下文。对变更类接口，必须保证上下文的还原（`changeCompanyInfo` 的 `finally` 分支），否则会污染同一线程的后续请求。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析，尚无需求文档或变更单佐证。

```ground:rule
name: 非标入站强制全租户上下文
content: "TianmaController 与 AlipayAntArchiveController 在处理前调用 MetaDataThreadLocalConfig.setDbTenantCode(\"all\")，使跨租户建档/查询可行；标准接口 reg/query/batchQuery 同样置 all，changeCompanyInfo 使用 try/finally 还原原租户"
impact: 渠道数据不落在单一租户上下文，需由企业记录自身 db_tenant_code 决定后续操作租户
field_targets:
  - cust_company_info.db_tenant_code
evidence: "code:TianmaController#companyArchive, AlipayAntArchiveController#channelArchive, CustAccessApplication#changeCompanyInfo（finally 还原）"
```

## 关联页面

- 口径：[[calibers/all_tenant_context]]、[[calibers/channel_tenant_mapping]]、[[calibers/batch_query_limit]]
- 规则：[[rules/channel_archive_unified_entry]]
- 概念：[[concepts/channel]]
- 载体表：[[tables/cust_company_info]]

---END FILE---

---FILE: rules/tianma_inbound_validation.md ---
---
type: rule
title: 天马入站参数强校验
page_key: rules/tianma_inbound_validation
domain: 外部渠道与银行对接
status: draft
aliases:
  - TianmaService#companyArchive 必填校验
  - PARAM_NULL
  - PARAM_ERROR
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaService#companyArchive
contract_version: "0.1"
---

# 天马入站参数强校验

## 业务定位

天马入站建档在 `TianmaService#companyArchive` 中以 `Assert` 串做必填校验，必填项为：`specifityCptSocialUnifiedCode`（资金方统一社会信用证）、`coreSocialUnifiedCode`（核心企业）、`companyName`、`socialUnifiedCode`（且长度必须为 18）、`authorizerPersonName`、`authorizerPersonCellphone`、`interestRate`（综合利率）。缺失分别抛 `CloudPcExceptionEnum.PARAM_NULL` / `PARAM_ERROR`。

## 需求背景

天马入站数据直接驱动建档落库：`socialUnifiedCode` 对应 `certification_no` 这一唯一识别键，`companyName` 对应重复校验的匹配键 `name`，`interestRate` 对应 `company_ext_data` 中的综合利率拓展字段。这些字段一旦缺失，后续重复校验、银行账户查询与清分配置都会失效，因此在入站即拒绝，不进建档流程。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析，尚无需求文档或变更单佐证。

```ground:rule
name: 天马入站参数强校验
content: "必填：specifityCptSocialUnifiedCode（资金方统一社会信用证）、coreSocialUnifiedCode（核心企业）、companyName、socialUnifiedCode（且长度必须为18）、authorizerPersonName、authorizerPersonCellphone、interestRate（综合利率）；缺失分别抛 CloudPcExceptionEnum.PARAM_NULL / PARAM_ERROR"
impact: 天马侧字段缺失或不合法会在入站即被拒绝，不进建档流程
field_targets:
  - cust_company_info.name
  - cust_company_info.certification_no
  - cust_company_info.company_ext_data
evidence: "code:TianmaService#companyArchive（Assert 串）"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 概念：[[concepts/tianma_inbound_outbound]]、[[concepts/reg_archive]]
- 规则：[[rules/tianma_default_company_type]]、[[rules/tianma_channel_key]]
- 口径：[[calibers/channel_tenant_mapping]]

---END FILE---

---FILE: rules/tianma_default_company_type.md ---
---
type: rule
title: 天马建档默认企业角色为供应商
page_key: rules/tianma_default_company_type
domain: 外部渠道与银行对接
status: draft
aliases:
  - CompanyType.SPY
  - 天马默认 SUPPLIER
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaService#companyArchive
  - code:CustAccessApplication#getCompanyType
contract_version: "0.1"
---

# 天马建档默认企业角色为供应商

## 业务定位

天马入站建档时，若 `req.getCompanyType()` 为空则写入 `CompanyType.SPY.name()`，否则取入参枚举名；随后 `CustAccessApplication#getCompanyType` 将 `SPY` 映射为 `CustCompanyTypeEnum.SUPPLIER` 落入 `cust_company_type`。

## 需求背景

天马场景下的入站企业默认为供应商角色。`cust_company_type` 是 JSON 数组字符串（如 `["SUPPLIER"]`），查询侧用 `like` 模糊匹配（`query` / `batchQuery` / `changeCompanyInfo`），因此写入值必须是对外约定的枚举名，不能写中文或自由文本。

## 影响与约束

天马入站企业若未显式传角色，会在库里被识别为供应商；下游按角色过滤的查询会据此命中。角色是查询键之一，出现"查不到"问题时应先核对本映射是否生效。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析，尚无需求文档或变更单佐证。

```ground:rule
name: 天马建档默认企业角色为供应商
content: "req.getCompanyType() 为空时写入 CompanyType.SPY.name()，否则取入参枚举名；随后 getCompanyType 将 SPY 映射为 CustCompanyTypeEnum.SUPPLIER"
impact: 天马入站默认识别为供应商角色
field_targets:
  - cust_company_info.cust_company_type
evidence: "code:TianmaService#companyArchive, CustAccessApplication#getCompanyType"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 概念：[[concepts/tianma_inbound_outbound]]
- 规则：[[rules/tianma_inbound_validation]]、[[rules/tianma_channel_key]]

---END FILE---

---FILE: rules/tianma_channel_key.md ---
---
type: rule
title: 天马渠道键写入
page_key: rules/tianma_channel_key
domain: 外部渠道与银行对接
status: draft
aliases:
  - CloudChannel.TIANMA.getDictKey()
  - 天马渠道键
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaService#companyArchive
  - code:CustAccessApplication#validateSetValueOfTianma
contract_version: "0.1"
---

# 天马渠道键写入

## 业务定位

天马入站建档会执行 `custDependentReqDto.setChannel(CloudChannel.TIANMA.getDictKey())`，把天马渠道键写入内部请求对象；随后由 `validateSetValueOfTianma` 用该渠道键反查 `cust_access_secret`，得到本次落库使用的 `db_tenant_code`。（本条规则的证据引用在语义分析原文中于方法名处被截断，方法名以 [[concepts/tianma_inbound_outbound]] 中相同引用为准。）

## 需求背景

天马渠道不能自行指定租户，租户必须由渠道密钥表配置决定（见 [[calibers/channel_tenant_mapping]]）。因此入站服务的第一步是把"我是天马"显式写入请求对象，再交给统一的校验/解析流程，避免渠道身份与租户解析散落在各分支里。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析；证据引用截断，已登记 REVIEW，尚无需求文档或变更单佐证。

```ground:rule
name: 天马渠道键写入
content: "custDependentReqDto.setChannel(CloudChannel.TIANMA.getDictKey())，由 validateSetValueOfTianma 用该渠道反查 cust_access_secret 得到 dbTenantCode"
impact: 天马入站租户由渠道密钥表决定，而非请求参数
field_targets:
  - cust_company_info.db_tenant_code
evidence: "code:TianmaService#companyArc"
```

## 关联页面

- 概念：[[concepts/tianma_inbound_outbound]]、[[concepts/channel]]
- 口径：[[calibers/channel_tenant_mapping]]、[[calibers/non_writeoff]]
- 规则：[[rules/channel_archive_unified_entry]]、[[rules/nonstandard_inbound_all_tenant]]
- 载体表：[[tables/cust_company_info]]

---END FILE---

---REVIEW: rule | 天马渠道键写入---
语义分析中本条规则的 `evidence` 字段在 `code:TianmaService#companyArc` 处被截断，方法名不完整，本页按原文逐字保留。同一文档中另有两条规则引用 `code:TianmaService#companyArchive`，可据此推定指向同一方法，但**推定值不得直接写入锚点块**。请补齐证据后把 `evidence` 修正为完整 `code_path`，并同步更新 `contract_version`。
---END REVIEW---

---REVIEW: process | 客户状态机---
`cust_status` 状态机在语义分析中 `transitions` 为空数组：`ADD` / `CHANGE` / `WRITEOFF` 之间的迁移事件没有代码证据。本页已将该状态机标注为"迁移未知"，请勿在未获证据前补写迁移边（例如常见的"建档成功→ADD"推断）。
---END REVIEW---