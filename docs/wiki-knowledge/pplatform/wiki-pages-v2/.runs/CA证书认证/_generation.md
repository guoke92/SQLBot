---FILE: tables/ca_certification_info.md ---
---
type: table
title: ca_certification_info
page_key: table/ca_certification_info
domain: CA证书认证
status: draft
aliases: [CA认证信息表, CA认证行]
oid: 1
scope:
  databases: [unknown]
sources: [db, code]
contract_version: "0.1"
---

ca_certification_info 是 CA 证书认证（CFCA 一证四步）的主过程表。每一行代表某企业（cust_id）在某个数据日期（data_date）下、按是否总公司行（head_company_data）区分的一条认证登记记录，承载协议告知、实名核验、意愿认证、附件引用与签章中台请求响应原文等留痕，并用 submit_status 跟踪上送签章中台的进展。

行粒度上的幂等键是（cust_id, data_date, head_company_data, submit_status=PENDING），详见 [[calibers/ca_row_idempotent_key]] 与 [[rules/ca_row_idempotent]]。成功上送后的最新一行是下游查询的取值口径，见 [[calibers/latest_success_report]]。分公司场景下同一企业会同时存在 head_company_data=N 与 Y 两行，见 [[rules/branch_dual_row]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。表结构与字段语义由两类证据支撑：编码型字段（cust_type、op_type、data_source、head_company_data、submit_status）取值来自代码枚举，id、cust_id、enable 等来自库结构。四类核验留痕字段（enterprise_four_json、police_two_json、intent_sms_json、intent_h_face_json）分别对应 [[concepts/one_cert_four_steps]] 中的实名核验与意愿认证环节；file_refs_json 与 notify_agreement_json 是上送签章中台的前置材料。

## 版本演进

暂无文档化的版本演进证据。与提交行为相关的规则可从代码路径观察：提交前的完整性校验（[[rules/submit_sign_center_completeness]]）、data 字段超长截断（[[rules/data_field_truncate]]）、提交状态流转（[[processes/ca_certification_submit_status]]）。另一张表 [[tables/ca_cfca_upgrade_report]] 记录证书升级过程中的异常上报，与本表通过企业标识关联。

```ground:table
table: ca_certification_info
fields:
  - name: id
    meaning: 表主键
    evidence: db
  - name: cust_id
    meaning: 企业ID（产融企业主键）
    evidence: db
  - name: cust_type
    meaning: "客户类型：COMPANY（企业）/ PERSON（个人）"
    evidence: code
  - name: data_date
    meaning: 数据日期，格式 yyyyMMdd
    evidence: code
  - name: op_type
    meaning: "操作类型：INSERT（新增）/ UPDATE（更新）"
    evidence: code
  - name: batch_no
    meaning: "批次号/唯一流水号，格式 INC_yyyyMMddHHmmssSSS_6位hex"
    evidence: code
  - name: data_source
    meaning: "数据来源：CHANNEL_OPENAPI（渠道API）/ FBP_PORTAL（产融门户）/ OPERATION_PLATFORM（运营中台）"
    evidence: code
  - name: head_company_data
    meaning: "是否总公司行：Y（总公司行）/ N（分公司自身行）"
    evidence: code
  - name: submit_status
    meaning: "提交状态：PENDING（待提交）/ SUCCESS（提交成功）/ FAIL（提交失败）"
    evidence: code
  - name: enable
    meaning: "启用标识：Y（有效）/ N（无效）"
    evidence: db
  - name: notify_agreement_json
    meaning: 协议告知 JSON 数组，记录各协议签署留痕
    evidence: code
  - name: enterprise_four_json
    meaning: 企业四要素/三要素核验 JSON（verifyMethod=ENTERPRISE_FOUR 或 ENTERPRISE_THREE）
    evidence: code
  - name: police_two_json
    meaning: 公安二要素核验 JSON（verifyMethod=POLICE_TWO）
    evidence: code
  - name: intent_sms_json
    meaning: 短信意愿认证 JSON（authType=SMS_CODE）
    evidence: code
  - name: intent_h_face_json
    meaning: H5刷脸意愿认证 JSON（authType=H5_FACE）
    evidence: code
  - name: file_refs_json
    meaning: 附件引用 JSON，包含 embeddedFiles 列表（multipartField + path）
    evidence: code
  - name: sign_platform_result
    meaning: 签章中台请求与响应原文（含异常信息），完整保留
    evidence: code
  - name: submit_time
    meaning: 最近一次提交签章中台的时间
    evidence: code
```

相关页面：[[processes/ca_certification_submit_status]]、[[concepts/ca]]、[[concepts/data_source]]、[[concepts/head_company_data]]。

---END FILE---

---FILE: tables/ca_cfca_upgrade_report.md ---
---
type: table
title: ca_cfca_upgrade_report
page_key: table/ca_cfca_upgrade_report
domain: CA证书认证
status: draft
aliases: [CFCA证书升级异常上报表]
oid: 1
scope:
  databases: [unknown]
sources: [db]
contract_version: "0.1"
---

ca_cfca_upgrade_report 记录 CFCA 证书升级过程中的异常上报信息：哪一类模块（biz_module）、来自哪个来源系统（source_system）、标题是什么（title）、对应企业与统一社会信用代码（company_id、certification_no）、被授权人（authorized_user_name）、是否曾触发待办/消息（todo_triggered），以及异常内容与透传报文（content、pass_info）。

该表是升级链路的观测面：当签章中台证书登记名与运营中台企业名不一致时，需要走在线盖章的升级授权书流程（[[rules/upgrade_auth_online_seal]]）；证书状态被归一化为 CANCELLED/EXPIRED/FAIL 或名称不匹配时会回写企业侧标识（[[rules/ca_invalidate_writeback]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。本页字段语义全部来自库结构证据（db），biz_module、source_system、title 的取值体现了同一升级事件的多种书写形态（例如 CFCA_CA_UPGRADE 与「CFCA证书升级」），与 [[concepts/ca]] 的术语归属相关但不能等同于证书本身的状态。

## 版本演进

暂无文档化的版本演进证据。可作为后续核对的锚点是 todo_triggered 字段：它记录该异常是否曾触发待办或消息，但本页不推断其触发时机与触发条件。

```ground:table
table: ca_cfca_upgrade_report
fields:
  - name: biz_module
    meaning: 所属模块，如 CFCA_CA_UPGRADE / CFCA证书升级
    evidence: db
  - name: source_system
    meaning: 来源系统，如 ACFLOW / ORDER / RVSFACTOR_PC / 国内信用证
    evidence: db
  - name: title
    meaning: 异常标题，如 CFCA证书升级 / 【CFCA证书升级】
    evidence: db
  - name: todo_triggered
    meaning: "是否曾触发待办/消息：Y / N"
    evidence: db
  - name: authorized_user_name
    meaning: 被授权人姓名
    evidence: db
  - name: company_id
    meaning: 企业ID
    evidence: db
  - name: certification_no
    meaning: 统一社会信用代码
    evidence: db
  - name: content
    meaning: 异常内容（单层 JSON）
    evidence: db
  - name: pass_info
    meaning: 透传 JSON
    evidence: db
```

相关页面：[[tables/ca_certification_info]]、[[rules/upgrade_auth_online_seal]]。

---END FILE---

---FILE: processes/ca_certification_submit_status.md ---
---
type: process
title: CA认证提交状态机
page_key: process/ca_certification_submit_status
domain: CA证书认证
status: draft
aliases: [submit_status 状态流转, CA上送签章中台状态]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
---

本状态机描述 ca_certification_info 行在「上送签章中台」这条链路上的生命周期。状态字段为 ca_certification_info.submit_status，三个取值 PENDING / SUCCESS / FAIL 均为代码枚举。

正常路径是：认证行以 PENDING 创建（幂等口径见 [[calibers/ca_row_idempotent_key]]），由 submitToSignCenter 上送签章中台；上送成功置 SUCCESS，上送失败置 FAIL。已经进入 FAIL 的行允许再次上送，成功即回到 SUCCESS；也存在不经上送、由运营侧手动标记失败进入 FAIL 的入口（markFailed）。

上送前的准入条件不在本状态机内表达，而由完整性校验规则约束（[[rules/submit_sign_center_completeness]]），超长 data 字段会在打包上送报文时被截断（[[rules/data_field_truncate]]）。SUCCESS 与 enable=Y 共同构成下游取数口径（[[calibers/latest_success_report]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。三态取值与四条流转的判定点均来自代码枚举与代码路径证据。

## 版本演进

暂无文档化的版本演进证据。当前可见的流转入口集中在 CaCertificationInfoAppServiceImpl 的 submitToSignCenter 与 markFailed 两个方法，尚无其他状态取值出现在分析证据中。

```ground:process
name: CA认证提交状态机
field: ca_certification_info.submit_status
states:
  - value: PENDING
    label: 待提交
    source: code_enum
  - value: SUCCESS
    label: 提交成功
    source: code_enum
  - value: FAIL
    label: 提交失败
    source: code_enum
transitions:
  - from: PENDING
    event: 提交签章中台成功
    to: SUCCESS
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:submitToSignCenter"
  - from: PENDING
    event: 提交签章中台失败
    to: FAIL
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:submitToSignCenter"
  - from: PENDING
    event: 手动标记失败
    to: FAIL
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:markFailed"
  - from: FAIL
    event: 重新提交签章中台成功
    to: SUCCESS
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:submitToSignCenter"
```

相关页面：[[tables/ca_certification_info]]、[[rules/submit_sign_center_completeness]]、[[concepts/ca]]。

---END FILE---

---FILE: calibers/latest_success_report.md ---
---
type: caliber
title: 最新成功上报数据
page_key: caliber/latest_success_report
domain: CA证书认证
status: draft
aliases: [最近一次成功上送, findLatestSuccessRow]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:findLatestSuccessRow"]
contract_version: "0.1"
---

口径含义：查询某企业最近一次成功上送签章中台的 CA 认证数据。过滤条件是 submit_status='SUCCESS' 且 enable='Y'，排序取 submit_time DESC、id DESC 的第一条。

这条口径是「结果态」而非「过程态」：PENDING 与 FAIL 的行都不进入结果集（状态语义见 [[processes/ca_certification_submit_status]]），被置为无效（enable='N'）的成功行同样被排除。调用方语义上应把该行视为该企业当前生效的 CA 认证事实。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。口径的谓词与排序字段均逐字来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。与口径相邻的另一条判定是 ca_register_status 的回写（[[rules/ca_invalidate_writeback]]）：当签章中台侧证书状态异常或登记名不一致时，企业侧标识被置为 N，前端据此引导重新开通，因此本口径的调用方需要与企业侧标识联合判断。

```ground:caliber
name: 最新成功上报数据
predicate: "ca_certification_info.submit_status = 'SUCCESS' 且 ca_certification_info.enable = 'Y'"
scope: 查询企业最近一次成功上送签章中台的数据，按 submit_time DESC, id DESC 取第一条
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:findLatestSuccessRow"
```

相关页面：[[tables/ca_certification_info]]、[[rules/ca_invalidate_writeback]]。

---END FILE---

---FILE: calibers/ca_row_idempotent_key.md ---
---
type: caliber
title: CA认证行幂等创建
page_key: caliber/ca_row_idempotent_key
domain: CA证书认证
status: draft
aliases: [createOrGetByKey 口径, CA认证行幂等键]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:createOrGetByKey"]
contract_version: "0.1"
---

口径含义：创建或获取 CA 认证行时，以（cust_id, data_date, head_company_data, submit_status='PENDING'）作为幂等键；若已存在 PENDING 行则复用，否则新建一行。

该口径的作用域只在 PENDING 态有效——已进入 SUCCESS 或 FAIL 的行不参与复用（状态语义见 [[processes/ca_certification_submit_status]]），因此同一企业同一天可能既有历史 SUCCESS 行又有新的 PENDING 行。head_company_data 进入幂等键，是分公司双行场景能够成立的前提（[[rules/branch_dual_row]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。键的四个组成字段与复用/新建分支均来自代码路径证据；对应的业务规则见 [[rules/ca_row_idempotent]]，其中还包含 batch_no 的生成约定。

## 版本演进

暂无文档化的版本演进证据。

```ground:caliber
name: CA认证行幂等创建
predicate: "ca_certification_info.cust_id = ? 且 ca_certification_info.data_date = ? 且 ca_certification_info.head_company_data = ? 且 ca_certification_info.submit_status = 'PENDING'"
scope: 创建或获取CA认证行时，若存在PENDING行则复用，否则新建
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:createOrGetByKey"
```

相关页面：[[tables/ca_certification_info]]、[[rules/ca_row_idempotent]]、[[concepts/head_company_data]]。

---END FILE---

---FILE: calibers/legacy_package_company_scope.md ---
---
type: caliber
title: 存量CA数据打包企业范围
page_key: caliber/legacy_package_company_scope
domain: CA证书认证
status: draft
aliases: [queryEligibleCompanies 口径, 存量打包企业范围]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CfcaOneCertFourStepPackageApplication.java:queryEligibleCompanies"]
contract_version: "0.1"
---

口径含义：存量 CFCA 一证四步离线打包任务在 cust_company_info 上筛选符合条件的企业——enable='Y'、ca_register_status='Y'、update_time >= 起始时间、且 identify_style != 'SIMPLE'。

四个条件分别承担不同职责：enable 过滤有效企业，ca_register_status 只取已开通 CA 的企业，update_time 限定增量窗口，identify_style != 'SIMPLE' 排除简易建档企业——这与简易认证强制不开通 CA 的规则相互印证（[[rules/simple_auth_force_no_ca]]）。企业范围确定后逐企业打包，打包内容与 [[concepts/one_cert_four_steps]] 的流程步骤对应。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。谓词字段与比较方向均逐字来自代码路径证据；对应的实现规则见 [[rules/legacy_package_query]]。

## 版本演进

暂无文档化的版本演进证据。

```ground:caliber
name: 存量CA数据打包企业范围
predicate: "cust_company_info.enable = 'Y' 且 cust_company_info.ca_register_status = 'Y' 且 cust_company_info.update_time >= ? 且 cust_company_info.identify_style != 'SIMPLE'"
scope: 存量CFCA一证四步离线打包任务查询符合条件的企业
evidence: "code_path:CfcaOneCertFourStepPackageApplication.java:queryEligibleCompanies"
```

相关页面：[[rules/legacy_package_query]]、[[rules/simple_auth_force_no_ca]]、[[concepts/one_cert_four_steps]]。

---END FILE---

---FILE: concepts/ca.md ---
---
type: concept
title: CA
page_key: concept/ca
domain: CA证书认证
status: draft
aliases: [CFCA, 数字证书, 电子签章]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
maps_to: CFCA数字证书认证服务
adjudication: boundary
also_confused_with: [电子签名, 上上签]
field_targets: []
---

「CA」在本主题中特指 CFCA 数字证书认证，是围绕企业数字证书开通、升级与失效回写的一整套服务，落地在 [[tables/ca_certification_info]]（开通链路）与 [[tables/ca_cfca_upgrade_report]]（升级异常上报）两张表上。

## 边界与辨析

- CA 特指 CFCA 数字证书认证；「电子签章」指签章中台提供的签章服务，是 CA 认证通过后调用的下游能力（例如上送签章中台、生成升级授权书，见 [[rules/upgrade_auth_online_seal]]）。
- 「上上签」是另一家第三方签章机构，代码中通过 SignAgency 区分，不属于本主题的 CA 范畴。
- 「电子签名」是更宽泛的行为描述，不指向具体机构与证书；本页的 CA 始终绑定 CFCA 证书。

因此在本契约中，CA 相关页面描述的是证书本体与认证流程，签章服务只在「上送」「盖章」等动作上被引用，不作为 CA 的同义词。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。术语映射与边界结论来自代码中的枚举与分支（data_source、verifyMethod、authType、SignAgency 等标识）。

## 版本演进

暂无文档化的版本演进证据。若后续出现其他 CA 机构接入，本页的 boundary 结论需要重新裁定。

相关页面：[[concepts/one_cert_four_steps]]、[[concepts/data_source]]、[[processes/ca_certification_submit_status]]。

---END FILE---

---FILE: concepts/one_cert_four_steps.md ---
---
type: concept
title: 一证四步
page_key: concept/one_cert_four_steps
domain: CA证书认证
status: draft
aliases: [CFCA一证四步]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
maps_to: 企业四要素/三要素核验 + 公安二要素核验 + 意愿认证（短信/H5刷脸） + 协议签署与上送签章中台
adjudication: synonym
also_confused_with: [实名认证]
field_targets:
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
  - ca_certification_info.notify_agreement_json
---

「一证四步」是 CFCA CA 开通的完整流程，四个步骤在 [[tables/ca_certification_info]] 上各有留痕字段：企业四要素/三要素核验（enterprise_four_json，verifyMethod=ENTERPRISE_FOUR 或 ENTERPRISE_THREE）、公安二要素核验（police_two_json，verifyMethod=POLICE_TWO）、意愿认证（intent_sms_json，authType=SMS_CODE；intent_h_face_json，authType=H5_FACE）、协议签署与上送签章中台（notify_agreement_json 留痕协议签署，file_refs_json 提供附件引用）。

## 边界与辨析

「一证四步」与「实名认证」是包含关系而非同义关系：实名认证仅指其中的核验环节（企业要素核验与公安二要素核验），不覆盖意愿认证、协议签署与上送。因此当需求文档提到「完成实名认证」时，不能直接推定为「完成一证四步」。

上送签章中台是否要求意愿认证留痕与数据来源有关：data_source=CHANNEL_OPENAPI 时可豁免意愿 JSON，见 [[rules/submit_sign_center_completeness]] 与 [[concepts/data_source]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。流程步骤与字段的对应关系来自代码中 verifyMethod 与 authType 的枚举取值。

## 版本演进

暂无文档化的版本演进证据。存量数据打包任务同样按一证四步口径筛选企业，见 [[calibers/legacy_package_company_scope]]。

相关页面：[[tables/ca_certification_info]]、[[rules/submit_sign_center_completeness]]、[[concepts/ca]]。

---END FILE---

---FILE: concepts/data_source.md ---
---
type: concept
title: data_source
page_key: concept/data_source
domain: CA证书认证
status: draft
aliases: [数据来源]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
maps_to: CA认证数据来源枚举
adjudication: boundary
also_confused_with: []
field_targets:
  - ca_certification_info.data_source
---

data_source 标识一条 CA 认证数据是从哪个入口产生的，落在 [[tables/ca_certification_info]] 的 data_source 字段上，取值在代码中固定为三种。

## 边界与辨析

- CHANNEL_OPENAPI：渠道 API。经该来源进入的认证在上送签章中台时，意愿认证 JSON 可豁免（见 [[rules/submit_sign_center_completeness]]）。
- FBP_PORTAL：产融门户。
- OPERATION_PLATFORM：运营中台。运营中台侧的企业名与签章中台证书登记名可能不一致，这会触发升级授权书流程（[[rules/upgrade_auth_online_seal]]）。

三个取值是互斥的入口归属，不代表数据质量或可信度差异；把它与「来源系统」（如 [[tables/ca_cfca_upgrade_report]] 的 source_system）混用会丢失粒度，后者描述上报异常来自哪个业务系统。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。三个取值的含义来自代码枚举证据。

## 版本演进

暂无文档化的版本演进证据。

相关页面：[[tables/ca_certification_info]]、[[rules/submit_sign_center_completeness]]、[[concepts/one_cert_four_steps]]。

---END FILE---

---FILE: concepts/head_company_data.md ---
---
type: concept
title: headCompanyData
page_key: concept/head_company_data
domain: CA证书认证
status: draft
aliases: [是否总公司行]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
maps_to: ca_certification_info行标识
adjudication: boundary
also_confused_with: [headCompany]
field_targets:
  - ca_certification_info.head_company_data
---

headCompanyData 是 [[tables/ca_certification_info]] 上的行标识，回答「这一行代表的是分公司自身，还是总公司」：Y 表示总公司行，N 表示分公司自身行。它同时是行幂等键的组成部分（[[calibers/ca_row_idempotent_key]]）。

## 边界与辨析

- headCompanyData 标识 CA 认证行是分公司自身（N）还是总公司（Y）；headCompany 是 cust_company_info 的字段，表示企业本身是否总公司。两者语义层级不同：前者是「这次认证为谁办」，后者是「这家企业是什么性质」，不能互相替换。
- 分公司场景下同一企业会同时产生 headCompanyData=N 与 Y 两行并分别上送签章中台，见 [[rules/branch_dual_row]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。字段取值 Y/N 与双行行为均来自代码证据。

## 版本演进

暂无文档化的版本演进证据。

相关页面：[[calibers/ca_row_idempotent_key]]、[[rules/branch_dual_row]]、[[tables/ca_certification_info]]。

---END FILE---

---FILE: rules/ca_row_idempotent.md ---
---
type: rule
title: CA认证行创建幂等规则
page_key: rule/ca_row_idempotent
domain: CA证书认证
status: draft
aliases: [createOrGetByKey 规则]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:createOrGetByKey"]
contract_version: "0.1"
---

规则要求：以（custId, dataDate, headCompanyData, submitStatus=PENDING）为幂等键创建 [[tables/ca_certification_info]] 行，已存在 PENDING 行则复用，否则新建，并生成唯一 batchNo。影响是避免同一企业同一天同一总公司标记下重复创建 CA 认证行。

复用的边界只在 PENDING 态：一旦行进入 SUCCESS 或 FAIL，新的提交会落到另一行（状态语义见 [[processes/ca_certification_submit_status]]）。batchNo 的格式约束为 INC_yyyyMMddHHmmssSSS_6位hex，是这条规则的可观测产出。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。幂等键、复用条件与 batchNo 生成均由代码路径证据支撑；对应的查询口径见 [[calibers/ca_row_idempotent_key]]。

## 版本演进

暂无文档化的版本演进证据。

```ground:rule
name: CA认证行创建幂等规则
content: 以(custId, dataDate, headCompanyData, submitStatus=PENDING)为幂等键，已存在PENDING则复用，否则新建，并生成唯一batchNo。
impact: 避免同一企业同一天同一总公司标记下重复创建CA认证行
field_targets:
  - ca_certification_info.cust_id
  - ca_certification_info.data_date
  - ca_certification_info.head_company_data
  - ca_certification_info.submit_status
  - ca_certification_info.batch_no
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:createOrGetByKey"
```

相关页面：[[calibers/ca_row_idempotent_key]]、[[concepts/head_company_data]]、[[rules/branch_dual_row]]。

---END FILE---

---FILE: rules/submit_sign_center_completeness.md ---
---
type: rule
title: 提交签章中台完整性校验
page_key: rule/submit_sign_center_completeness
domain: CA证书认证
status: draft
aliases: [assertCompleteForSubmit 规则, CA_CERT_INFO_INCOMPLETE]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:assertCompleteForSubmit"]
contract_version: "0.1"
---

规则要求：上送签章中台前，[[tables/ca_certification_info]] 行必须满足——notify_agreement_json 非空；至少一项实名 JSON（enterprise_four_json 或 police_two_json）；至少一项意愿 JSON（intent_sms_json 或 intent_h_face_json），除非 data_source=CHANNEL_OPENAPI；file_refs_json 非空。不满足时抛出 CA_CERT_INFO_INCOMPLETE 异常，阻止上送。

这是一条准入型规则，位于 [[processes/ca_certification_submit_status]] 的 PENDING 出口之前：校验不通过的行会保持 PENDING 或转入 FAIL，而不会进入 SUCCESS。意愿认证的豁免只针对渠道 API 来源，其余两个来源（FBP_PORTAL、OPERATION_PLATFORM）仍需意愿留痕，见 [[concepts/data_source]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。五项校验条件、豁免条件与异常码均来自代码路径证据；四类核验 JSON 的业务含义见 [[concepts/one_cert_four_steps]]。

## 版本演进

暂无文档化的版本演进证据。与该规则相邻的上送处理是 data 字段超长截断（[[rules/data_field_truncate]]）：前者决定「能不能送」，后者决定「报文能不能被接收」。

```ground:rule
name: 提交签章中台完整性校验
content: 上送签章中台前必须满足：notify_agreement_json非空；至少一项实名JSON（enterprise_four_json或police_two_json）；至少一项意愿JSON（intent_sms_json或intent_h_face_json），除非data_source=CHANNEL_OPENAPI；file_refs_json非空。
impact: 不满足则抛出CA_CERT_INFO_INCOMPLETE异常，阻止上送
field_targets:
  - ca_certification_info.notify_agreement_json
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
  - ca_certification_info.file_refs_json
  - ca_certification_info.data_source
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:assertCompleteForSubmit"
```

相关页面：[[processes/ca_certification_submit_status]]、[[concepts/one_cert_four_steps]]、[[rules/data_field_truncate]]。

---END FILE---

---FILE: rules/data_field_truncate.md ---
---
type: rule
title: data字段超长截断规则
page_key: rule/data_field_truncate
domain: CA证书认证
status: draft
aliases: [truncateOversizedDataFieldsInSubmitPayload 规则, data 超长截断]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:truncateOversizedDataFieldsInSubmitPayload"]
contract_version: "0.1"
---

规则要求：上送签章中台时，authRealNameJson 与 intentJson 下的 data 字段若超过 1000 字符，按叶子节点从长到短删除直至不超长；非 JSON 则硬截断。影响是避免签章中台因 data 超长拒绝，保证上送成功。

截断发生在报文打包阶段，作用于四类核验 JSON 所对应的 data 内容，属于「为了保证送达而牺牲部分字段完整度」的妥协：截断后的报文体不会被回写到 [[tables/ca_certification_info]] 的原始 JSON 字段中，原始留痕仍以列值为准；签章中台的请求与响应原文另存于 sign_platform_result。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。1000 字符阈值、叶子节点删除顺序与非 JSON 硬截断三个要点均来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。本规则是 [[rules/submit_sign_center_completeness]] 的补充：完整性校验保证字段存在，截断规则保证字段可被接收。

```ground:rule
name: data字段超长截断规则
content: 上送签章中台时，authRealNameJson和intentJson下的data字段若超过1000字符，按叶子节点从长到短删除直至不超长；非JSON则硬截断。
impact: 避免签章中台因data超长拒绝，保证上送成功
field_targets:
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:truncateOversizedDataFieldsInSubmitPayload"
```

相关页面：[[rules/submit_sign_center_completeness]]、[[tables/ca_certification_info]]、[[concepts/one_cert_four_steps]]。

---END FILE---

---FILE: rules/block_ca_on_change_status.md ---
---
type: rule
title: 变更态拦截CA开通
page_key: rule/block_ca_on_change_status
domain: CA证书认证
status: draft
aliases: [assertCompanyNotInChange]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationPreCheckApplication.java:assertCompanyNotInChange"]
contract_version: "0.1"
---

规则要求：企业在变更态时禁止进入一证四步——cust_company_info.cust_status=CHANGE 或 cust_company_info.cust_build_status=CUST_CHANGE 都会触发拦截，抛出异常提示先完成变更流程。

拦截发生在认证前置检查阶段，早于 [[tables/ca_certification_info]] 的建行与上送，因此不会产生 PENDING 行（对比 [[calibers/ca_row_idempotent_key]]）。其业务动因是：企业身份信息在变更中，此时核验与证书登记名都不可靠，开通后极易触发名称不一致的回写（[[rules/ca_invalidate_writeback]]）与升级授权书补签（[[rules/upgrade_auth_online_seal]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。两个触发字段与取值来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。同一前置检查类中还包含管理员校验（[[rules/admin_check]]）。

```ground:rule
name: 变更态拦截CA开通
content: 企业cust_status=CHANGE或cust_build_status=CUST_CHANGE时，禁止进入一证四步。
impact: 抛出异常提示先完成变更流程
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.cust_build_status
evidence: "code_path:CaCertificationPreCheckApplication.java:assertCompanyNotInChange"
```

相关页面：[[rules/admin_check]]、[[rules/ca_invalidate_writeback]]、[[concepts/one_cert_four_steps]]。

---END FILE---

---FILE: rules/admin_check.md ---
---
type: rule
title: 管理员校验规则
page_key: rule/admin_check
domain: CA证书认证
status: draft
aliases: [assertCurrentUserIsAdmin, CA_CERT_NOT_ADMIN]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationPreCheckApplication.java:assertCurrentUserIsAdmin"]
contract_version: "0.1"
---

规则要求：当前登录用户必须是企业管理员，需同时满足 cust_person_info.user_type=admin、enable=Y、ref_cust_company_info=当前企业 code、company_type=当前登录企业类型、phone=当前登录手机号。任一不满足即抛出 CA_CERT_NOT_ADMIN 异常，无法开通 CA。

五个条件构成一次「人-企业-手机号」三重一致性确认：既校验操作者角色，也校验其归属企业与企业类型，并用手机号与登录态对齐，避免借用他人账号代开证书。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。五项条件、比对方向与异常码均来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。该规则与变更态拦截同属前置检查阶段（[[rules/block_ca_on_change_status]]）。

```ground:rule
name: 管理员校验规则
content: 当前登录用户必须是企业管理员：cust_person_info.user_type=admin且enable=Y且ref_cust_company_info=当前企业code且company_type=当前登录企业类型且phone=当前登录手机号。
impact: 非管理员抛出CA_CERT_NOT_ADMIN异常，无法开通CA
field_targets:
  - cust_person_info.user_type
  - cust_person_info.enable
  - cust_person_info.ref_cust_company_info
  - cust_person_info.company_type
  - cust_person_info.phone
evidence: "code_path:CaCertificationPreCheckApplication.java:assertCurrentUserIsAdmin"
```

相关页面：[[rules/block_ca_on_change_status]]、[[concepts/ca]]。

---END FILE---

---FILE: rules/ca_invalidate_writeback.md ---
---
type: rule
title: CA失效回写ca_register_status=N
page_key: rule/ca_invalidate_writeback
domain: CA证书认证
status: draft
aliases: [resetCaRegisterStatusToN, CA 回写失效]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationPreCheckApplication.java:resetCaRegisterStatusToN"]
contract_version: "0.1"
---

规则要求：当签章中台证书状态归一化为 CANCELLED/EXPIRED/FAIL，或登记企业名与库中名称不一致时，将 cust_company_info.ca_register_status 置为 N。影响是前端据此引导用户重新发起 CA 开通。

这条回写把「外部证书状态」翻译成「企业侧开通标识」，是本主题里唯一把签章中台状态向企业主数据反向传播的规则。它使得 [[calibers/latest_success_report]] 的结果与企业侧标识可能短暂背离：历史成功行仍在，但企业已被判为未开通，直到重新认证成功。名称不一致的分支还衔接在线盖章的升级授权书流程（[[rules/upgrade_auth_online_seal]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。三个失效状态取值、名称不一致条件与目标字段均来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。需要注意的是 ca_register_status 同时被多条规则写入：本规则置 N，简易认证规则也会校正其取值（[[rules/simple_auth_force_no_ca]]），存量打包口径则以 ca_register_status='Y' 为筛选条件（[[calibers/legacy_package_company_scope]]）。

```ground:rule
name: CA失效回写ca_register_status=N
content: 签章中台证书状态归一化为CANCELLED/EXPIRED/FAIL或登记企业名与库中名称不一致时，将cust_company_info.ca_register_status置为N。
impact: 前端引导用户重新发起CA开通
field_targets:
  - cust_company_info.ca_register_status
evidence: "code_path:CaCertificationPreCheckApplication.java:resetCaRegisterStatusToN"
```

相关页面：[[calibers/latest_success_report]]、[[rules/upgrade_auth_online_seal]]、[[rules/simple_auth_force_no_ca]]。

---END FILE---

---FILE: rules/simple_auth_force_no_ca.md ---
---
type: rule
title: 简易认证强制不开通CA
page_key: rule/simple_auth_force_no_ca
domain: CA证书认证
status: draft
aliases: [submitForSimpleAuth 校正规则]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CustCompanyInfoApplication.java:submitForSimpleAuth"]
contract_version: "0.1"
---

规则要求：简易认证提交时，若 cust_company_info.need_register_ca=Y，强制校正为 N 并落库，同时校正 ca_register_status、need_register_bs、bs_register_status。影响是简易建档不支持开通电子签章。

这是一条「上游强制收敛」规则：调用方即使传入了开通意图，也会在落库时被改写，因此简易企业不会进入一证四步（[[concepts/one_cert_four_steps]]），也不会产生 [[tables/ca_certification_info]] 的认证行。它同时校正 BS 侧的注册标识，说明 CA 与 BS 的开通开关在简易场景下被一并关闭。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。校正字段清单与强制方向来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。本规则与存量打包口径中的 identify_style != 'SIMPLE' 条件互相印证（[[calibers/legacy_package_company_scope]]）。

```ground:rule
name: 简易认证强制不开通CA
content: 简易认证提交时，若need_register_ca=Y，强制校正为N并落库，同时校正ca_register_status、need_register_bs、bs_register_status。
impact: 简易建档不支持开通电子签章
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_company_info.need_register_bs
  - cust_company_info.bs_register_status
evidence: "code_path:CustCompanyInfoApplication.java:submitForSimpleAuth"
```

相关页面：[[calibers/legacy_package_company_scope]]、[[rules/ca_invalidate_writeback]]、[[concepts/one_cert_four_steps]]。

---END FILE---

---FILE: rules/legacy_package_query.md ---
---
type: rule
title: 存量打包查询规则
page_key: rule/legacy_package_query
domain: CA证书认证
status: draft
aliases: [queryEligibleCompanies 规则]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CfcaOneCertFourStepPackageApplication.java:queryEligibleCompanies"]
contract_version: "0.1"
---

规则要求：查询 enable='Y'、ca_register_status='Y'、update_time>=since、identify_style!=SIMPLE 的企业，可选租户过滤。影响是确定存量 CA 数据打包的企业范围。

四个条件中，ca_register_status='Y' 表示只打包企业侧自认为已开通的证书，而 update_time 窗口使任务可以增量重跑。可选租户过滤意味着同一套查询可在多租户部署下复用。该查询对应的正式口径描述见 [[calibers/legacy_package_company_scope]]，打包内容对应一证四步（[[concepts/one_cert_four_steps]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。四个筛选条件与可选租户过滤来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。由于 ca_register_status 会被失效回写置 N（[[rules/ca_invalidate_writeback]]），打包范围会随证书状态变化而收缩。

```ground:rule
name: 存量打包查询规则
content: 查询enable=Y、ca_register_status=Y、update_time>=since、identify_style!=SIMPLE的企业，可选租户过滤。
impact: 确定存量CA数据打包的企业范围
field_targets:
  - cust_company_info.enable
  - cust_company_info.ca_register_status
  - cust_company_info.update_time
  - cust_company_info.identify_style
evidence: "code_path:CfcaOneCertFourStepPackageApplication.java:queryEligibleCompanies"
```

相关页面：[[calibers/legacy_package_company_scope]]、[[rules/ca_invalidate_writeback]]、[[rules/simple_auth_force_no_ca]]。

---END FILE---

---FILE: rules/upgrade_auth_online_seal.md ---
---
type: rule
title: 升级授权书在线盖章条件
page_key: rule/upgrade_auth_online_seal
domain: CA证书认证
status: draft
aliases: [processUpgradeAuthOnOpsNameChange]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaUpgradeAuthApplication.java:processUpgradeAuthOnOpsNameChange"]
contract_version: "0.1"
---

规则要求：当签章中台证书登记名与运营中台企业名不一致且证书状态为 NORMAL 时，在线签署升级授权书，并上传运营中台与产融影像，回写 file_refs_json。影响是企业名称变更后重新开通 CA 需签署升级授权书。

判定条件是「名称不一致 + 证书仍 NORMAL」这一组合：名称不一致但证书已失效时走的是失效回写路径（[[rules/ca_invalidate_writeback]]），而不是补签授权书。签名与影像材料的落点是 [[tables/ca_certification_info]] 的 file_refs_json，该字段同时是上送签章中台的前置材料（[[rules/submit_sign_center_completeness]]）。名称来源区分运营中台与产融两个影像渠道，与 data_source 的入口语义不同（[[concepts/data_source]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。触发条件、上传来源与回写字段来自代码路径证据。升级过程的异常会上报到 [[tables/ca_cfca_upgrade_report]]。

## 版本演进

暂无文档化的版本演进证据。

```ground:rule
name: 升级授权书在线盖章条件
content: 签章中台证书登记名与运营中台企业名不一致且证书状态为NORMAL时，在线签署升级授权书，并上传运营中台与产融影像，回写file_refs_json。
impact: 企业名称变更后重新开通CA需签署升级授权书
field_targets:
  - ca_certification_info.file_refs_json
  - ca_certification_info.notify_agreement_json
evidence: "code_path:CaUpgradeAuthApplication.java:processUpgradeAuthOnOpsNameChange"
```

相关页面：[[rules/ca_invalidate_writeback]]、[[tables/ca_cfca_upgrade_report]]、[[concepts/ca]]。

---END FILE---

---FILE: rules/branch_dual_row.md ---
---
type: rule
title: 分公司双行处理规则
page_key: rule/branch_dual_row
domain: CA证书认证
status: draft
aliases: [persistActivateData 双行规则]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaActivationApplication.java:persistActivateData"]
contract_version: "0.1"
---

规则要求：分公司场景下，CaActivationApplication 会创建两行 [[tables/ca_certification_info]]——headCompanyData=N（本企业）与 headCompanyData=Y（总公司），并分别提交签章中台；openCa 注册时自动双笔注册。影响是支持分公司代总公司完成 CA 认证。

双行意味着同一 cust_id、同一 data_date 下可以并存两条认证行，因此行标识 head_company_data 必须进入幂等键，否则两行会互相覆盖（[[calibers/ca_row_idempotent_key]]、[[rules/ca_row_idempotent]]）。两行各自独立走提交状态机（[[processes/ca_certification_submit_status]]），状态可能不一致，下游按企业取「最新成功上报数据」时需要明确是取哪一行（[[calibers/latest_success_report]]）。术语层面 headCompanyData 与 headCompany 的分工见 [[concepts/head_company_data]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。双行创建与分别上送的行为来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。

```ground:rule
name: 分公司双行处理规则
content: 分公司场景下，CaActivationApplication 会创建两行ca_certification_info：headCompanyData=N（本企业）和headCompanyData=Y（总公司），并分别提交签章中台；openCa注册时自动双笔注册。
impact: 支持分公司代总公司完成CA认证
field_targets:
  - ca_certification_info.head_company_data
  - ca_certification_info.cust_id
evidence: "code_path:CaActivationApplication.java:persistActivateData"
```

相关页面：[[calibers/ca_row_idempotent_key]]、[[rules/ca_row_idempotent]]、[[concepts/head_company_data]]、[[processes/ca_certification_submit_status]]。

---END FILE---

---REVIEW: table | 物理库名缺失（scope.databases）---
语义分析未给出任何物理库名，但 frontmatter 要求 scope.databases: [<物理库名>]。为避免发明事实，全部页面的 scope.databases 暂填 unknown。

待确认：
1. ca_certification_info、ca_cfca_upgrade_report、cust_company_info、cust_person_info 是否同库？若不同，需要按页拆分 scope.databases。
2. ~~是否存在分库/分表或租户维度隔离~~（存量打包查询提到「可选租户过滤」，租户维度是否体现在物理库上待确认）。
3. 分析中 ca_certification_info 只在 field_semantics 中给出，其库结构证据标记为 db；确认该标记是否指向同一物理库。
---END REVIEW---