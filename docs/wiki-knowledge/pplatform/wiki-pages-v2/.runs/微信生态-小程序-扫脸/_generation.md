---FILE: tables/ca_certification_info.md ---
---
type: table
title: ca_certification_info（CFCA 一证四步认证与上送表）
page_key: ca_certification_info
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - ca_certification_info
  - CFCA 认证信息表
  - 一证四步认证表
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
---

# ca_certification_info（CFCA 一证四步认证与上送表）

## 业务定位

本表是「扫脸」意愿认证与签章中台上送的落库底座：企业工商核验、法人/人员公安二要素核验、短信意愿、H5 刷脸意愿、附件清单五类数据块各自独立成列，最终由 [[processes/ca_submit_status|CFCA 上送状态]] 驱动上报。行的幂等由 `cust_id`、`data_date`、`head_company_data` 等共同决定，总公司与分公司在分公司双行场景下共用 `custId` 但以 `head_company_data` 区分。上送前需先满足 [[calibers/face_verify_passed|人脸认证通过]] 口径，`intent_h5_face_json` 由 [[processes/certification_verify_status|人脸/实名认证结果状态]] 通过后回填。

## 需求背景

CFCA 一证四步认证要求把核验原文与意愿原文完整留痕后上报签章中台，因此本表以 JSON 列承载上送报文素材：`notify_agreement_json` 上送时包装为 `notifyAgreementList + notifyTextList`；`enterprise_four_json` 与 `enterprise_three_json` 按 `verifyMethod` 路由上送键；`file_refs_json` 中 `embeddedFiles.path` 存 COS key，上送前转 HTTP 下载链。上送结果与失败原因统一记入 `sign_platform_result`。

## 版本演进

从代码证据可见：首次落库固定 `op_type = INSERT`；随后引入 `head_company_data` 支持总分公司双行幂等；`submit_status` 经 [[processes/ca_submit_status|CFCA 上送状态]] 收敛为 `PENDING/SUCCESS/FAIL`，且 `markFailed` 在失败态追加原因而不改变状态值。

```ground:table
table: ca_certification_info
fields:
  - name: id
    type: bigint
    desc: "CFCA 一证四步认证主键，落库后用于回填 intent_h5_face_json / file_refs_json 等 JSON 块"
    dict: null
  - name: cust_id
    type: bigint
    desc: "产融企业 id；总公司/分公司行按同一 custId 但 headCompanyData 区分"
    dict: null
  - name: cust_type
    type: varchar(32)
    desc: "客户类型，默认 COMPANY（企业）"
    dict: null
  - name: data_date
    type: char(8)
    desc: "数据日期 yyyyMMdd，幂等键之一"
    dict: null
  - name: op_type
    type: varchar(16)
    desc: "上报操作类型，首次落库固定 INSERT"
    dict: null
  - name: batch_no
    type: varchar(64)
    desc: "上报流水号，INC_yyyyMMddHHmmssSSS_6位hex，总分公司各自独立"
    dict: null
  - name: data_source
    type: varchar(32)
    desc: "CFCA 认证数据来源，路由不同业务场景"
    dict: null
  - name: head_company_data
    type: char(1)
    desc: "是否总公司数据，Y/N；分公司双行场景用于幂等键"
    dict: null
  - name: submit_status
    type: varchar(32)
    desc: "上送签章中台状态：PENDING/SUCCESS/FAIL（CaSubmitStatusEnum.name()）"
    dict: CaSubmitStatusEnum
  - name: notify_agreement_json
    type: text
    desc: "协议告知 JSON 列，上送时包装为 notifyAgreementList + notifyTextList"
    dict: null
  - name: enterprise_four_json
    type: text
    desc: "企业工商核验 JSON 列；按 verifyMethod 在 enterprise_four_json 与 enterprise_three_json 上送键间路由"
    dict: null
  - name: police_two_json
    type: text
    desc: "法人/人员公安二要素核验 JSON 列"
    dict: null
  - name: intent_sms_json
    type: text
    desc: "短信验证码意愿认证 JSON 列"
    dict: null
  - name: intent_h5_face_json
    type: text
    desc: "H5 刷脸意愿认证 JSON 列；FaceVerifyController 在人脸通过时回填 DBaaS 请求/响应原文"
    dict: null
  - name: file_refs_json
    type: text
    desc: "附件清单 JSON 列；embeddedFiles.path 存 COS key，上送前转 HTTP 下载链"
    dict: null
  - name: sign_platform_result
    type: text
    desc: "签章中台请求+响应原文，异常/markFailed 追加"
    dict: null
```

关联页面：[[calibers/ca_submit_success|CA 上送成功]]、[[calibers/ca_submit_pending|CA 待上送]]、[[calibers/head_company_data|总公司数据]]、[[calibers/branch_company_data|分公司数据]]、[[concepts/h5_face_intent|H5刷脸意愿]]。

---REVIEW: table | ca_certification_info---
1) 物理库名：语义分析只给出代码模块路径 `lowcode-pplatform-customer-management`，未给出物理库名，`scope.databases` 按模块名推断为 `lowcode_pplatform_cust`，待 DBA/DDL 确认。
2) 字段类型：语义分析未提供 DDL，`type` 列按字段命名与用法推断（主键/外键 bigint、JSON 列 text、Y/N 标记 char(1)），需以实际 DDL 校准后覆盖。
3) `cust_type` 默认 COMPANY、`data_source` 取值域未在本次分析中枚举，保持描述性文字，不新增字典键。
---END REVIEW---

---END FILE---

---FILE: tables/cust_certification_info.md ---
---
type: table
title: cust_certification_info（企业认证记录表）
page_key: cust_certification_info
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - cust_certification_info
  - 认证记录表
  - 企业四要素认证记录表
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
---

# cust_certification_info（企业认证记录表）

## 业务定位

本表记录企业主体在各认证类型下的核查结论与次数，是 [[processes/certification_verify_status|人脸/实名认证结果状态]] 的载体表。企业四要素认证（`COMPANY_FOUR_ELEMENTS`）与扫脸意愿认证（`FACE_VERIFY`）通过 `certification_type` 区分，`ref_cust_company_info` 回指 [[tables/cust_company_info|企业主表]] 的 `code`。人脸识别业务流水号落在 `face_business_no`，供影像查询使用。

## 需求背景

扫脸链路需要把「自动核查」与「人工核查」两条结果通路分开留痕：自动核查通过由 `AutoVerifyServiceImpl:saveOrUpdate` 写入 `auto_verify_status` 并累加 `auto_verify_count`；人工核查通过由 `saveManual` 写入 `manual_verify_status`。下游取数口径见 [[calibers/face_verify_passed|人脸认证通过]] 与 [[calibers/manual_verify_passed|人工认证通过]]。

## 版本演进

自动核查失败后再次通过可回写为通过；人工核查通过后 `verifyThree` 会短路返回已通过结论。写入路径使用字典 `getDictParam()`、人脸通过判断使用 `getDictKey()`，二者存在读写键不一致风险，见 [[rules/verify_status_dict_key_consistency|核查状态字典键一致性规则]]。

```ground:table
table: cust_certification_info
fields:
  - name: ref_cust_company_info
    type: varchar(64)
    desc: "关联企业 code；与企业主表 code 对应"
    dict: null
  - name: certification_type
    type: varchar(64)
    desc: "认证类型（COMPANY_FOUR_ELEMENTS / FACE_VERIFY 等），写入用 CustCertificationTypeEnum.getDictParam()"
    dict: CustCertificationTypeEnum
  - name: auto_verify_status
    type: varchar(64)
    desc: "自动核查结果；写入用 getDictParam()，人脸通过判断用 getDictKey()，存在读写键不一致风险"
    dict: null
  - name: manual_verify_status
    type: varchar(64)
    desc: "人工核查结果；写入用 getDictParam()，人脸通过判断用 getDictKey()"
    dict: null
  - name: auto_verify_count
    type: int
    desc: "自动核查次数，saveOrUpdate 每次 +1"
    dict: null
  - name: face_business_no
    type: varchar(64)
    desc: "人脸识别业务流水号，用于影像查询"
    dict: null
```

关联页面：[[concepts/face_auth_passed|人脸认证通过（术语）]]、[[concepts/saolian|扫脸]]。

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info（企业联系人表）
page_key: cust_person_info
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - cust_person_info
  - 联系人表
  - 经办人表
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java
contract_version: "0.1"
---

# cust_person_info（企业联系人表）

## 业务定位

本表承载企业下的联系人/经办人，是小程序扫脸实名结果的落点：`face_status` 记人脸认证结果，`phone_realname_status` 记手机号实名状态，`real_name_result` 由两者计算得到的综合实名结果。`user_type` 以 `UserTypeEnum.getDictKey()` 区分 admin/operator/guest，`company_type` 表示客户角色并与企业类型匹配。

## 需求背景

企业联系人查询要求只返回有效联系人：逻辑删除位 `enable = 'Y'`，账号状态 `status` 限定在 `ADD/EFFECT`，产品关系需未冻结，合称 [[calibers/company_user_valid|企业联系人有效]] 与 [[calibers/product_rel_not_frozen|产品关系未冻结]]。经办人需要推送的系统以逗号分隔存于 `operator_push_system`。

## 版本演进

从代码可见的演进点：实名结论由单字段演进为 `face_status + phone_realname_status` 计算出的 `real_name_result`；人脸与手机实名写入均取字典 `getDictKey()`，与 [[tables/cust_certification_info|认证记录表]] 中 `getDictParam()` 的写值口径不一致。

```ground:table
table: cust_person_info
fields:
  - name: face_status
    type: varchar(32)
    desc: "人脸认证结果；finishedVerifyFace 写入 CustCertificationResultTypeEnum.getDictKey()"
    dict: CustCertificationResultTypeEnum
  - name: phone_realname_status
    type: varchar(32)
    desc: "手机号实名状态；verifyThree/finishedVerifyFace 写入 getDictKey()"
    dict: null
  - name: real_name_result
    type: varchar(32)
    desc: "综合实名结果；由 face_status + phone_realname_status 计算 getDictKey()"
    dict: null
  - name: operator_push_system
    type: varchar(255)
    desc: "经办人需推送的系统列表，逗号分隔"
    dict: null
  - name: ref_cust_company_info
    type: varchar(64)
    desc: "关联企业 code"
    dict: null
  - name: company_type
    type: varchar(64)
    desc: "客户角色，与企业类型匹配"
    dict: null
  - name: user_type
    type: varchar(32)
    desc: "联系人类型：admin/operator/guest 等（UserTypeEnum.getDictKey()）"
    dict: UserTypeEnum
  - name: enable
    type: char(1)
    desc: "逻辑 enable：Y/N"
    dict: null
  - name: status
    type: varchar(32)
    desc: "联系人账号状态，listCompanyUser 过滤 ADD/EFFECT"
    dict: null
```

关联页面：[[tables/cust_company_info|企业主表]]、[[tables/sys_cust_user_rel|产品-用户关系表]]、[[concepts/saolian|扫脸]]。

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（企业主表）
page_key: cust_company_info
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - cust_company_info
  - 企业主表
  - 产融企业表
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java
contract_version: "0.1"
---

# cust_company_info（企业主表）

## 业务定位

企业主表以 `code` 作为企业编码，被 [[tables/cust_person_info|联系人表]] 与 [[tables/cust_certification_info|认证记录表]] 的 `ref_cust_company_info` 引用；`certification_no` 为统一社会信用代码。CA 开通状态（`ca_register_status`）与是否需要开通签章（`need_register_ca`）决定经办人授权书是否走在线签署与签署前 CA 前置校验。

## 需求背景

扫脸影像的同步需要主数据来源：`main_data_id` 记录主数据 id，同步人脸影像时从主数据企业复制到当前企业。租户隔离与 sso channel 解析依赖 `db_tenant_code`。

## 版本演进

从代码可见：`need_register_ca = 'Y'` 时签署前做 CA 状态前置校验，`ca_register_status = 'Y'` 时签署经办人授权书走在线签署；人脸影像同步引入 `main_data_id` 作为主数据锚点。

```ground:table
table: cust_company_info
fields:
  - name: code
    type: varchar(64)
    desc: "企业编码，被 cust_person_info.ref_cust_company_info / cust_certification_info.ref_cust_company_info 引用"
    dict: null
  - name: certification_no
    type: varchar(64)
    desc: "统一社会信用代码"
    dict: null
  - name: ca_register_status
    type: char(1)
    desc: "CA 开通状态，Y 时签署经办人授权书走在线签署"
    dict: null
  - name: need_register_ca
    type: char(1)
    desc: "是否需要开通签章，Y 时签署前做 CA 状态前置校验"
    dict: null
  - name: db_tenant_code
    type: varchar(64)
    desc: "数据租户标识，用于租户隔离和 sso channel 解析"
    dict: null
  - name: main_data_id
    type: bigint
    desc: "主数据 id，同步人脸影像时从主数据企业复制到当前企业"
    dict: null
```

关联页面：[[tables/ca_certification_info|CFCA 认证与上送表]]、[[calibers/company_user_valid|企业联系人有效]]。

---END FILE---

---FILE: tables/sys_cust_user_rel.md ---
---
type: table
title: sys_cust_user_rel（产品-用户关系表）
page_key: sys_cust_user_rel
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - sys_cust_user_rel
  - 产品用户关系表
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java
contract_version: "0.1"
---

# sys_cust_user_rel（产品-用户关系表）

## 业务定位

记录用户与产品（企业）之间的关系，`is_freeze` 为冻结标记（Y/N）。企业联系人按产品过滤有效用户时，需满足 [[calibers/product_rel_not_frozen|产品关系未冻结]]，与 [[calibers/company_user_valid|企业联系人有效]] 组合成 `listCompanyUser` 的完整过滤条件。

## 需求背景

在扫脸/实名链路中，联系人的可用性判断必须同时覆盖账号维度（`cust_person_info.enable`、`status`）与产品维度（`is_freeze`），避免已冻结产品下仍被拉取为有效经办人。

## 版本演进

从代码证据可见，`is_freeze = 'N'` 是 `listCompanyUser` 过滤有效用户的固定条件，暂未见其他取值语义。

```ground:table
table: sys_cust_user_rel
fields:
  - name: is_freeze
    type: char(1)
    desc: "产品-用户关系冻结标记，Y/N"
    dict: null
```

关联页面：[[tables/cust_person_info|联系人表]]、[[calibers/product_rel_not_frozen|产品关系未冻结]]。

---END FILE---

---FILE: processes/certification_verify_status.md ---
---
type: process
title: 人脸/实名认证结果状态机
page_key: certification_verify_status
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 人脸认证结果状态
  - 实名认证结果状态
  - auto_verify_status 状态机
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
---

# 人脸/实名认证结果状态机

## 业务定位

描述 [[tables/cust_certification_info|认证记录表]] 中 `auto_verify_status` 与 `manual_verify_status` 的取值与流转：自动核查通过/失败、人工核查通过三态。该状态机是 [[calibers/face_verify_passed|人脸认证通过]] 与 [[calibers/manual_verify_passed|人工认证通过]] 两个口径的直接来源，通过后由 [[processes/ca_submit_status|CFCA 上送状态]] 链路把结果用于意愿数据回填。

## 需求背景

自动核查失败不是终态：再次自动核查通过可回写为自动通过；也可由人工核查兜底为人工通过。`verifyThree` 在人工认证已通过时短路返回，避免重复核查。人脸查询侧 `isFaceVerifyPassed` 只要自动或人工任一通过即视为人脸通过，从而触发 `intent_h5_face_json` 回填。

## 版本演进

从代码可见：状态值使用枚举名（code_enum）形式写入；随后出现「人工通过短路」的优化分支；需注意写入用 `getDictParam()`、判断用 `getDictKey()` 的读写键不一致风险，见 [[rules/verify_status_dict_key_consistency|核查状态字典键一致性规则]]。

```ground:process
name: 人脸/实名认证结果状态
field: cust_certification_info.auto_verify_status / cust_certification_info.manual_verify_status
states:
  - value: AUTOMATIC_AUTHENTICATION_PASSED
    label: 自动认证通过
    source: code_enum
  - value: AUTOMATIC_AUTHENTICATION_FAILED
    label: 自动认证失败
    source: code_enum
  - value: MANUAL_AUTHENTICATION_PASSED
    label: 人工认证通过
    source: code_enum
transitions:
  - from: AUTOMATIC_AUTHENTICATION_FAILED
    event: 自动核查再次通过
    to: AUTOMATIC_AUTHENTICATION_PASSED
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveOrUpdate
  - from: AUTOMATIC_AUTHENTICATION_FAILED
    event: 人工核查通过
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveManual
  - from: 未通过
    event: 人脸查询结果自动或人工任一通过
    to: 人脸认证通过
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java:isFaceVerifyPassed
  - from: 未通过
    event: 人工认证已通过时短路返回
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:verifyThree
```

关联页面：[[concepts/face_auth_passed|人脸认证通过（术语）]]、[[calibers/manual_verify_passed|人工认证通过]]。

---REVIEW: process | 人脸/实名认证结果状态机---
第 3、4 条流转的 from/to 使用业务标签「未通过 / 人脸认证通过」「MANUAL_AUTHENTICATION_PASSED」，语义分析未给出对应的枚举 value（如人脸通过的统一 value），因此按标签原样保留，待枚举口径补充后再对齐 value。
---END REVIEW---

---END FILE---

---FILE: processes/ca_submit_status.md ---
---
type: process
title: CFCA 上送状态机
page_key: ca_submit_status
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 上送状态机
  - submit_status 状态机
  - 签章中台上送状态
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# CFCA 上送状态机

## 业务定位

描述 [[tables/ca_certification_info|CFCA 认证与上送表]] 中 `submit_status` 的三态流转：`PENDING`（待上送）、`SUCCESS`（上送成功）、`FAIL`（上送失败），取值来自 `CaSubmitStatusEnum.name()`。该状态机与 [[calibers/ca_submit_success|CA 上送成功]]、[[calibers/ca_submit_pending|CA 待上送]] 两个口径配套使用，实现重复上送的幂等跳过。

## 需求背景

上送签章中台要求：命中待上送行时直接复用不重复建行；命中成功行时不重复上送；调用 `cbsSubmitBizData` 成功（DBaaS `code=0/200` 且 `biz.status=SAVED`）回写成功，异常或失败回写失败并记录原因。

## 版本演进

从代码可见：`createOrGetByKey` 建立初始 `PENDING` 行；`submitToSignCenter` 支持成功后重复调用仍保持 `SUCCESS`（幂等）；`writeSubmitResult`/`markFailed` 在失败态追加原因而不改状态值。

```ground:process
name: CFCA 上送状态
field: ca_certification_info.submit_status
states:
  - value: PENDING
    label: 待上送
    source: code_enum
  - value: SUCCESS
    label: 上送成功
    source: code_enum
  - value: FAIL
    label: 上送失败
    source: code_enum
transitions:
  - from: 无
    event: createOrGetByKey 新建行
    to: PENDING
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:createOrGetByKey
  - from: PENDING
    event: cbsSubmitBizData 成功，DBaaS code=0/200 且 biz.status=SAVED
    to: SUCCESS
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:submitToSignCenter
  - from: PENDING
    event: cbsSubmitBizData 异常或失败
    to: FAIL
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:writeSubmitResult
  - from: SUCCESS
    event: 再次 submitToSignCenter
    to: SUCCESS
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:submitToSignCenter
  - from: FAIL
    event: markFailed 追加上送失败原因
    to: FAIL
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:markFailed
```

关联页面：[[concepts/submit_success|上送成功（术语）]]、[[rules/ca_submit_idempotency|CA 上送幂等规则]]。

---END FILE---

---FILE: calibers/face_verify_passed.md ---
---
type: caliber
title: 人脸认证通过
page_key: face_verify_passed
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 人脸通过判断
  - isFaceVerifyPassed
  - 扫脸通过
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
---

# 人脸认证通过

## 业务定位

「人脸认证通过」是扫脸链路的准入口径：自动核查通过或人工核查通过任一成立即为通过。它决定 `faceVerifyQuery` 是否把 DBaaS 请求/响应原文回填到 [[tables/ca_certification_info|CFCA 认证与上送表]] 的 `intent_h5_face_json`（见 [[concepts/h5_face_intent|H5刷脸意愿]]）。

## 需求背景

人脸查询接口在返回结果前需判断认证是否通过，只有通过才允许落意愿认证块，避免未通过数据被上报签章中台（见 [[processes/ca_submit_status|CFCA 上送状态]]）。

## 版本演进

从代码可见，该口径以「自动 OR 人工」的并集形式实现，与 [[calibers/manual_verify_passed|人工认证通过]] 的单一条件形成上下位关系；状态值来源见 [[processes/certification_verify_status|人脸/实名认证结果状态]]。

```ground:caliber
name: 人脸认证通过
predicate: "cust_certification_info.auto_verify_status = 'AUTOMATIC_AUTHENTICATION_PASSED' OR cust_certification_info.manual_verify_status = 'MANUAL_AUTHENTICATION_PASSED'"
scope: faceVerifyQuery 回填 CFCA H5_FACE 意愿数据前的人脸通过判断
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java:isFaceVerifyPassed
```

关联页面：[[tables/cust_certification_info|认证记录表]]、[[concepts/saolian|扫脸]]。

---END FILE---

---FILE: calibers/manual_verify_passed.md ---
---
type: caliber
title: 人工认证通过
page_key: manual_verify_passed
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 人工核查通过
  - manual passed
  - saveManual
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
contract_version: "0.1"
---

# 人工认证通过

## 业务定位

只认 `manual_verify_status` 的人工通过态，用于人工核查落库与实名流程的短路返回：一旦人工通过，`verifyThree` 直接返回通过结论，不再走后续核查。

## 需求背景

自动核查可能失败，需人工兜底；人工通过后若继续走自动核查会产生无意义的调用与计数增长（见 [[tables/cust_certification_info|认证记录表]] 的 `auto_verify_count`）。

## 版本演进

从证据可见，人工通过与自动通过是并列两列，二者并集构成 [[calibers/face_verify_passed|人脸认证通过]]；状态含义见 [[processes/certification_verify_status|人脸/实名认证结果状态]]。

```ground:caliber
name: 人工认证通过
predicate: "cust_certification_info.manual_verify_status = 'MANUAL_AUTHENTICATION_PASSED'"
scope: 人工核查与实名短路返回
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveManual
```

关联页面：[[tables/cust_certification_info|认证记录表]]、[[concepts/face_auth_passed|人脸认证通过（术语）]]。

---END FILE---

---FILE: calibers/company_user_valid.md ---
---
type: caliber
title: 企业联系人有效
page_key: company_user_valid
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 有效联系人
  - listCompanyUser 过滤
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java
contract_version: "0.1"
---

# 企业联系人有效

## 业务定位

定义 [[tables/cust_person_info|联系人表]] 中「有效联系人」的判定：逻辑未删除（`enable = 'Y'`）且账号状态处于 `ADD/EFFECT`。该口径用于 `listCompanyUser` 查询企业联系人。

## 需求背景

扫脸与实名需要拉取真实可用的经办人/联系人，历史逻辑删除行与未进入生效态的行不能参与业务。

## 版本演进

从代码可见，`status` 的取值域在查询侧收敛为 `ADD/EFFECT` 两项；与产品维度的 [[calibers/product_rel_not_frozen|产品关系未冻结]] 联合使用。

```ground:caliber
name: 企业联系人有效
predicate: "cust_person_info.enable = 'Y' AND cust_person_info.status IN ('ADD','EFFECT')"
scope: listCompanyUser 查询企业联系人
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java:listCompanyUser
```

关联页面：[[tables/sys_cust_user_rel|产品-用户关系表]]。

---END FILE---

---FILE: calibers/product_rel_not_frozen.md ---
---
type: caliber
title: 产品关系未冻结
page_key: product_rel_not_frozen
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - is_freeze=N
  - 未冻结产品关系
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java
contract_version: "0.1"
---

# 产品关系未冻结

## 业务定位

[[tables/sys_cust_user_rel|产品-用户关系表]] 中 `is_freeze = 'N'` 表示关系未冻结，是企业联系人按产品过滤有效用户的必要条件。

## 需求背景

企业联系人的可用性同时受账号状态与产品关系状态约束，冻结关系下的用户不应出现在可选经办人列表中。

## 版本演进

从代码可见，该条件固定出现在 `listCompanyUser` 的过滤逻辑中，与 [[calibers/company_user_valid|企业联系人有效]] 并列。

```ground:caliber
name: 产品关系未冻结
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 企业联系人按产品过滤有效用户
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java:listCompanyUser
```

关联页面：[[tables/cust_person_info|联系人表]]。

---END FILE---

---FILE: calibers/ca_submit_success.md ---
---
type: caliber
title: CA 上送成功
page_key: ca_submit_success
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - submit_status=SUCCESS
  - 上送成功行
  - findLatestSuccessRow
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# CA 上送成功

## 业务定位

`ca_certification_info.submit_status = 'SUCCESS'` 表示该行已成功上送签章中台。用于取企业最新成功上报数据，以及幂等跳过重复上送。

## 需求背景

同一企业在同一幂等键下已成功上送后不应重复上报，避免签章中台重复受理；同时「最新成功行」也是查询企业当前有效认证数据的口径。

## 版本演进

从代码可见，`findLatestSuccessRow` 承接该口径；成功态可被再次 `submitToSignCenter` 覆盖为 `SUCCESS`，见 [[processes/ca_submit_status|CFCA 上送状态]] 与 [[rules/ca_submit_idempotency|CA 上送幂等规则]]。

```ground:caliber
name: CA 上送成功
predicate: "ca_certification_info.submit_status = 'SUCCESS'"
scope: 取企业最新成功上报数据、幂等跳过重复上送
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:findLatestSuccessRow
```

关联页面：[[tables/ca_certification_info|CFCA 认证与上送表]]、[[concepts/submit_success|上送成功（术语）]]。

---END FILE---

---FILE: calibers/ca_submit_pending.md ---
---
type: caliber
title: CA 待上送
page_key: ca_submit_pending
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - submit_status=PENDING
  - 待上送行
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# CA 待上送

## 业务定位

`ca_certification_info.submit_status = 'PENDING'` 表示该行尚未上送签章中台，是 `createOrGetByKey` 幂等命中的条件：已存在待上送行时直接复用，不再新建。

## 需求背景

同一幂等键（含 `cust_id`、`data_date`、`head_company_data` 等）下反复触发上送准备时，必须复用未上送行，避免产生重复待上送数据。

## 版本演进

从代码可见，新建行的初始状态固定为 `PENDING`，该状态是 [[processes/ca_submit_status|CFCA 上送状态]] 的起点；与 [[calibers/ca_submit_success|CA 上送成功]] 共同支撑幂等。

```ground:caliber
name: CA 待上送
predicate: "ca_certification_info.submit_status = 'PENDING'"
scope: createOrGetByKey 幂等命中
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:createOrGetByKey
```

关联页面：[[tables/ca_certification_info|CFCA 认证与上送表]]、[[rules/ca_submit_idempotency|CA 上送幂等规则]]。

---END FILE---

---FILE: calibers/head_company_data.md ---
---
type: caliber
title: 总公司数据
page_key: head_company_data
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - headCompanyData=Y
  - 总公司行
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# 总公司数据

## 业务定位

`ca_certification_info.head_company_data = 'Y'` 标识分公司双行场景中的总公司行，是幂等键的组成部分。

## 需求背景

总公司与分公司在同一 `custId` 下需要各自独立上报（`batch_no` 各自独立），必须以 `head_company_data` 区分，否则会互相覆盖或误判幂等。

## 版本演进

从代码可见，`normalizeHeadCompanyData` 统一规范化该字段取值；与之相对的是 [[calibers/branch_company_data|分公司数据]]，语义辨析见 [[concepts/head_company_data|总公司数据（术语）]]。

```ground:caliber
name: 总公司数据
predicate: "ca_certification_info.head_company_data = 'Y'"
scope: 分公司双行场景总公司行
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:normalizeHeadCompanyData
```

关联页面：[[tables/ca_certification_info|CFCA 认证与上送表]]、[[rules/head_company_two_row_idempotency|总分公司双行幂等规则]]。

---END FILE---

---FILE: calibers/branch_company_data.md ---
---
type: caliber
title: 分公司数据
page_key: branch_company_data
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - headCompanyData=N
  - 分公司行
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# 分公司数据

## 业务定位

`ca_certification_info.head_company_data = 'N'` 标识分公司双行场景中的分公司行。

## 需求背景

分公司行与总公司行共用 `custId` 但上报流水号独立、核验内容可能不同，需在读取「最新成功行」时按该口径正确区分，避免取到另一侧数据。

## 版本演进

从代码可见，该取值与 [[calibers/head_company_data|总公司数据]] 成对出现，由 `normalizeHeadCompanyData` 规范化，见 [[processes/ca_submit_status|CFCA 上送状态]]。

```ground:caliber
name: 分公司数据
predicate: "ca_certification_info.head_company_data = 'N'"
scope: 分公司双行场景分公司行
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:normalizeHeadCompanyData
```

关联页面：[[tables/ca_certification_info|CFCA 认证与上送表]]。

---END FILE---

---FILE: concepts/saolian.md ---
---
type: concept
title: 扫脸
page_key: saolian
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 人脸认证
  - 人脸识别
  - H5刷脸
  - CFCA H5_FACE
  - 意愿认证H5_FACE
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:扫脸"
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
contract_version: "0.1"
maps_to: cust_certification_info.certification_type='FACE_VERIFY'
field_targets:
  - cust_certification_info.certification_type
adjudication: boundary
also_confused_with:
  - cust_certification_info.auto_verify_status
  - ca_certification_info.intent_h5_face_json
---

# 扫脸

## 业务定位

「扫脸」在本域内指意愿认证/活体人脸链路，落点为认证类型 `FACE_VERIFY` 的认证记录，随企业一证四步链路把 H5 刷脸意愿数据上报签章中台。参见 [[tables/cust_certification_info|认证记录表]]、[[tables/ca_certification_info|CFCA 认证与上送表]]。

## 需求背景

小程序/H5 刷脸是 CFCA 一证四步中的意愿认证环节，必须与核查结果、上报报文块区分清楚，否则会出现「以核查状态代替意愿证据」的取数错误。

## 版本演进

从代码可见，扫脸链路与实名核查链路共用联系人表与认证记录表，但语义不同：前者产出意愿块，后者产出核查状态。

## 边界

- 扫脸（`certification_type = FACE_VERIFY`）是意愿/活体链路。
- `auto_verify_status` 是核查结果状态，见 [[processes/certification_verify_status|人脸/实名认证结果状态]]。
- `intent_h5_face_json` 是 CFCA 上报意愿块，见 [[concepts/h5_face_intent|H5刷脸意愿]]。
- 三者不等同于实名认证结果。

---END FILE---

---FILE: concepts/h5_face_intent.md ---
---
type: concept
title: H5刷脸意愿
page_key: h5_face_intent
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - CFCA 一证四步意愿认证
  - intent_h5_face_json
  - authType=H5_FACE
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:H5刷脸意愿"
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
maps_to: ca_certification_info.intent_h5_face_json
field_targets:
  - ca_certification_info.intent_h5_face_json
adjudication: boundary
also_confused_with:
  - ca_certification_info.intent_sms_json
  - cust_certification_info.auto_verify_status
---

# H5刷脸意愿

## 业务定位

指 CFCA 签章中台意愿认证中的 H5 刷脸块（`authType = H5_FACE`），以 [[tables/ca_certification_info|CFCA 认证与上送表]] 的 `intent_h5_face_json` 列承载 DBaaS 请求/响应原文，由人脸通过后在 `faceVerifyQuery` 中回填。

## 需求背景

上报报文要求意愿证据可追溯，故刷脸意愿必须与短信意愿分列留痕，且只能在 [[calibers/face_verify_passed|人脸认证通过]] 之后写入。

## 版本演进

从代码可见，回填动作绑定在 `FaceVerifyController` 的人脸通过分支上，写入口径与 [[processes/certification_verify_status|人脸/实名认证结果状态]] 的通过判断耦合。

## 边界

- H5_FACE 是签章中台意愿认证块。
- 短信意愿写 `intent_sms_json`，两者不可混用。
- 人脸核查结果写 [[tables/cust_certification_info|认证记录表]]，不是意愿块。

---END FILE---

---FILE: concepts/face_auth_passed.md ---
---
type: concept
title: 人脸认证通过（术语）
page_key: face_auth_passed
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 核查通过
  - automatic passed
  - manual passed
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:人脸认证通过"
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
maps_to: cust_certification_info.auto_verify_status
field_targets:
  - cust_certification_info.auto_verify_status
  - cust_certification_info.manual_verify_status
adjudication: boundary
also_confused_with:
  - cust_certification_info.manual_verify_status
  - cust_person_info.phone_realname_status
---

# 人脸认证通过（术语）

## 业务定位

口头语「核查通过 / 人脸通过」在库内有两条落点：自动通过写 `auto_verify_status`，人工通过写 `manual_verify_status`。查询判定使用二者并集，见 [[calibers/face_verify_passed|人脸认证通过]]。

## 需求背景

业务方常以「人脸认证通过」同时指代自动与人工两种来源，取数时必须明确落到哪一列，避免只查 `auto_verify_status` 而漏掉人工兜底通过的记录。

## 版本演进

从代码可见，自动核查与人工核查由不同方法写入（`saveOrUpdate` / `saveManual`），状态取值见 [[processes/certification_verify_status|人脸/实名认证结果状态]]。

## 边界

- 自动通过：`cust_certification_info.auto_verify_status`。
- 人工通过：`cust_certification_info.manual_verify_status`，见 [[calibers/manual_verify_passed|人工认证通过]]。
- 联系人手机号实名写 [[tables/cust_person_info|联系人表]] 的 `phone_realname_status`，与本术语不同层。

---END FILE---

---FILE: concepts/wechat_contact_user.md ---
---
type: concept
title: 企微人员
page_key: wechat_contact_user
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 企微通讯录
  - WechatUserDTO
  - 审批人下拉
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:企微人员"
contract_version: "0.1"
maps_to: tenant_project_approval_flow.approver_user_id
field_targets:
  - tenant_project_approval_flow.approver_user_id
adjudication: boundary
also_confused_with:
  - sys_user.id
---

# 企微人员

## 业务定位

项目审批流中的审批人下拉选项来自企业微信通讯录，落库值为 `tenant_project_approval_flow.approver_user_id`，即企微 userId。

## 需求背景

审批人必须是企微通讯录中真实存在的成员，选择时经 `WechatContactFacade.existsUser` 校验；若误用平台账号体系 id，会出现审批消息下发失败。

## 版本演进

从语义桥证据可见，该字段与平台用户体系是两套标识，未发现二者互转的落库证据。

## 边界

- `approver_user_id` 是企微 userId，需经企微通讯录校验。
- 不是平台 `sys_user.id`。
- 相关消息下发链路见 [[concepts/wechat_message|企微消息]]。

---REVIEW: concept | 企微人员---
语义分析仅给出术语桥，未给出 `tenant_project_approval_flow` 的字段清单与 DDL 证据，本页只登记术语映射与边界；`WechatContactFacade.existsUser` 的具体类路径待补证后写入 sources。
---END REVIEW---

---END FILE---

---FILE: concepts/wechat_message.md ---
---
type: concept
title: 企微消息
page_key: wechat_message
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 企业微信消息
  - textcard
  - 待办提醒
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:企微消息"
contract_version: "0.1"
maps_to: tenant_project_approval_flow.approver_user_id
field_targets:
  - tenant_project_approval_flow.approver_user_id
adjudication: boundary
also_confused_with:
  - 微信服务号消息
  - DBASS 微信通知 WechatNotificationService
---

# 企微消息

## 业务定位

项目审批待办提醒走企业微信消息通道（`message/send`，textcard 形式），接收方由 `tenant_project_approval_flow.approver_user_id` 决定，见 [[concepts/wechat_contact_user|企微人员]]。

## 需求背景

同一业务存在多条微信触达链路，混用会导致消息发到错误通道或错误接收人，因此需要在术语层明确区分。

## 版本演进

从语义桥证据可见，企微消息直连企业微信接口；服务号通知与 DBASS 的 `IWeiXinApi` / `WechatNotificationService` 属于另一链路。

## 边界

- 企微消息：企业微信应用消息，接收人为企微 userId。
- 微信服务号消息：另一套模板消息链路。
- DBASS 微信通知：`WechatNotificationService` / `IWeiXinApi` 链路，不可与企微消息互换。

---REVIEW: concept | 企微消息---
语义桥未给出企微消息发送实现类路径与消息模板字段，本页只登记术语边界；具体 `message/send` 调用点待补证。
---END REVIEW---

---END FILE---

---FILE: concepts/head_company_data.md ---
---
type: concept
title: 总公司数据（术语）
page_key: head_company_data
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - headCompanyData=Y
  - 总公司行
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:总公司数据"
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
maps_to: ca_certification_info.head_company_data='Y'
field_targets:
  - ca_certification_info.head_company_data
adjudication: boundary
also_confused_with:
  - ca_certification_info.head_company_data='N'
---

# 总公司数据（术语）

## 业务定位

「总公司数据」是 [[tables/ca_certification_info|CFCA 认证与上送表]] 中 `head_company_data = 'Y'` 的业务叫法，用于分公司双行场景标记总公司行。

## 需求背景

总公司与分公司在同一 `custId` 下各自上报，幂等键需带上该标记才能区分两行，避免互相命中。

## 版本演进

从代码可见，该字段经 `normalizeHeadCompanyData` 规范化；取值口径见 [[calibers/head_company_data|总公司数据]] 与 [[calibers/branch_company_data|分公司数据]]。

## 边界

- `Y` 表示总公司行，`N` 表示分公司行。
- 分公司场景两行共用幂等键，但 `headCompanyData` 不同。
- 幂等实现见 [[rules/head_company_two_row_idempotency|总分公司双行幂等规则]]。

---END FILE---

---FILE: concepts/submit_success.md ---
---
type: concept
title: 上送成功（术语）
page_key: submit_success
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - SUCCESS
  - cbsSubmitBizData 成功
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:上送成功"
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
maps_to: ca_certification_info.submit_status='SUCCESS'
field_targets:
  - ca_certification_info.submit_status
adjudication: boundary
also_confused_with:
  - ca_certification_info.submit_status='PENDING'
  - ca_certification_info.submit_status='FAIL'
---

# 上送成功（术语）

## 业务定位

「上送成功」指签章中台接收成功并落库成功，对应 `ca_certification_info.submit_status = 'SUCCESS'`，判定条件为 `cbsSubmitBizData` 返回 DBaaS `code = 0/200` 且 `biz.status = SAVED`。

## 需求背景

业务口径中的「成功」容易被理解为「请求已发出」，而系统口径是「DBaaS 受理并保存成功」，因此需要区分 `PENDING` 与 `FAIL`。

## 版本演进

从代码可见，成功态可重复上送而保持 `SUCCESS`；失败态由 `markFailed` 追加原因不改状态值，见 [[processes/ca_submit_status|CFCA 上送状态]]。

## 边界

- `SUCCESS`：上送成功，见 [[calibers/ca_submit_success|CA 上送成功]]。
- `PENDING`：仅落库未上送，见 [[calibers/ca_submit_pending|CA 待上送]]。
- `FAIL`：上送异常或失败，需重试时依赖幂等规则。

---END FILE---

---FILE: rules/ca_submit_idempotency.md ---
---
type: rule
title: CA 上送幂等规则
page_key: ca_submit_idempotency
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - createOrGetByKey 幂等
  - 幂等跳过重复上送
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# CA 上送幂等规则

## 业务定位

约束 [[tables/ca_certification_info|CFCA 认证与上送表]] 的建行与上送行为：建行时命中 [[calibers/ca_submit_pending|CA 待上送]] 行直接复用；上送前命中 [[calibers/ca_submit_success|CA 上送成功]] 行则跳过重复上送。

## 需求背景

签章中台上送不可重复受理；业务侧可能多次触发认证与上送准备，必须以库内状态作为幂等依据，而不是依赖调用方去重。

## 版本演进

从代码可见，`createOrGetByKey` 负责建行幂等，`findLatestSuccessRow` 负责上送前幂等判定；状态流转见 [[processes/ca_submit_status|CFCA 上送状态]]。

```ground:rule
name: CA 上送幂等
predicate: "createOrGetByKey 命中 ca_certification_info.submit_status = 'PENDING' 行则复用；findLatestSuccessRow 命中 ca_certification_info.submit_status = 'SUCCESS' 行则跳过重复上送"
scope: CFCA 上送签章中台的建行与上送前置判定
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:createOrGetByKey, lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:findLatestSuccessRow
```

关联页面：[[concepts/submit_success|上送成功（术语）]]、[[calibers/ca_submit_pending|CA 待上送]]。

---END FILE---

---FILE: rules/head_company_two_row_idempotency.md ---
---
type: rule
title: 总分公司双行幂等规则
page_key: head_company_two_row_idempotency
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - headCompanyData 幂等键
  - 分公司双行
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# 总分公司双行幂等规则

## 业务定位

约束 [[tables/ca_certification_info|CFCA 认证与上送表]] 在分公司场景下的行唯一性：总公司行与分公司行共用 `cust_id`，但以 `head_company_data`（`Y`/`N`）区分，形成两行独立数据；`batch_no` 亦各自独立生成。

## 需求背景

若不以 `head_company_data` 参与幂等键，总公司与分公司数据会互相命中，导致一侧数据被覆盖或上送错主体。

## 版本演进

从代码可见，`normalizeHeadCompanyData` 统一规范化取值，配套口径见 [[calibers/head_company_data|总公司数据]] 与 [[calibers/branch_company_data|分公司数据]]，术语边界见 [[concepts/head_company_data|总公司数据（术语）]]。

```ground:rule
name: 总分公司双行幂等
predicate: "ca_certification_info.cust_id 相同且 ca_certification_info.head_company_data = 'Y' / 'N' 区分总公司行与分公司行；ca_certification_info.data_date 与 ca_certification_info.batch_no 参与唯一性判定"
scope: 分公司双行场景建行与取数幂等
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:normalizeHeadCompanyData
```

关联页面：[[rules/ca_submit_idempotency|CA 上送幂等规则]]。

---END FILE---

---FILE: rules/verify_status_dict_key_consistency.md ---
---
type: rule
title: 核查状态字典键一致性规则
page_key: verify_status_dict_key_consistency
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - getDictParam 与 getDictKey 一致性
  - 读写键不一致风险
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
---

# 核查状态字典键一致性规则

## 业务定位

约束 [[tables/cust_certification_info|认证记录表]] 中核查状态字段的取值口径：`auto_verify_status` 与 `manual_verify_status` 写入使用 `getDictParam()`，而人脸通过判断读取使用 `getDictKey()`。

## 需求背景

同一字段存在写入键与读取键两套取值来源时，若字典 param 与 key 不相等，会出现「已写入通过但判断不通过」的取数偏差，进而阻断 [[concepts/h5_face_intent|H5刷脸意愿]] 回填与 [[processes/ca_submit_status|CFCA 上送状态]] 推进。

## 版本演进

从代码可见，写入路径（`saveOrUpdate` / `saveManual`）与判断路径（`isFaceVerifyPassed`）取值方法不同，构成读写键不一致风险；[[tables/cust_person_info|联系人表]] 的 `face_status`/`phone_realname_status` 采用 `getDictKey()` 写入，与之口径又不同。

```ground:rule
name: 核查状态字典键一致性
predicate: "cust_certification_info.auto_verify_status 与 cust_certification_info.manual_verify_status 写入取 CustCertificationTypeEnum 体系 getDictParam()，人脸通过判断取 getDictKey()；两者须指向同一字典值，否则判定失效"
scope: 认证记录写入与人脸通过判断链路
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveOrUpdate, lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveManual, lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java:isFaceVerifyPassed
```

关联页面：[[calibers/face_verify_passed|人脸认证通过]]、[[concepts/face_auth_passed|人脸认证通过（术语）]]。

---REVIEW: rule | 核查状态字典键一致性规则---
语义分析指出写入用 `getDictParam()`、判断用 `getDictKey()` 且「存在读写键不一致风险」，但未给出两个方法对应的具体字典键/参数值。本页按证据原样登记风险，predicate 中的枚举归属待与枚举写值点核对后修正（以写值点 + DB 为准）。
---END REVIEW---

---END FILE---