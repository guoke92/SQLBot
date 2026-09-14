---FILE: tables/gpt_learn_poster_log.md ---
---
type: table
title: 智能审核引流卡片埋点记录表
page_key: gpt_learn_poster_log
domain: 客户管理
status: draft
aliases: [引流埋点表, GP学习埋点表, poster_log]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:checkPosterStatus
  - code_path:GptLearnService.java:recordPosterClick
  - code_path:GptLearnPosterLogDao.countByUserAndCompany
  - db:gpt_learn_poster_log
contract_version: "0.1"
---

本表是「智能审核引流卡片」链路的埋点记录表：一次卡片弹出写入一行（`popup_time` 有值），用户点击卡片后回写点击时间（`click_time` 有值）。`id` 会被 `checkPosterStatus` 返回给前端作为 `recordId`，点击时回传，因此它同时承担埋点主键与前端交互令牌两个角色。业务概念见 [[concepts/gpt_learn]]，生命周期见 [[processes/gpt_learn_poster_log_lifecycle]]。

写入路径受三条规则约束：[[rules/gpt_learn_finance_only]]（仅金融机构企业）、[[rules/poster_allowed_tenant]]（仅白名单租户）、[[rules/poster_popup_max_count]]（同一用户+企业弹出次数上限）。`user_name` / `company_name` 为弹出时刻的快照字段，其中企业名称来自 [[tables/cust_company_info]]。

## 需求背景

该卡片并非在线学习业务，而是向外部 SaaS 中登同步登录信息后做引流跳转的埋点链路，因此本表字段口径围绕「是否弹出」「是否点击」「属于哪个用户与企业」「落在哪个租户」四件事展开。需求/系统文档层（客户管理平台业务规则文档、运营配置管理业务规则文档）未出现 GP学习引流相关规则表述，本表当前全部主张为代码 + DB 单源立据（详见 [[concepts/gpt_learn]] 的版本演进）。

## 版本演进

- 当前观测：全表 252 行埋点，`enable` 全为 `Y`，`db_tenant_code` 实测仅 `beehive-scf.qhhrly.cn` 一个值，与 `isPosterAllowedTenant` 的灰度口径对应。
- `click_time` 由 `recordPosterClick` 在校验通过后写入；未匹配时抛「埋点记录不存在或已记录点击」，即点击回写是单次幂等的。
- 字段物理类型未在语义分析证据中给出，下方锚点块的 `type` 统一记为 `unknown`。

```ground:table
table: gpt_learn_poster_log
fields:
  - name: id
    type: unknown
    desc: "智能审核引流卡片埋点记录主键，checkPosterStatus 返回给前端作为 recordId，点击时回传"
    dict: "-"
  - name: user_id
    type: unknown
    desc: "埋点归属用户ID（登录用户 userId，Long.valueOf(currentUser.getUserId())）"
    dict: "-"
  - name: company_id
    type: unknown
    desc: "埋点归属企业ID（登录企业 companyId）"
    dict: "-"
  - name: user_name
    type: unknown
    desc: "弹出时写入的用户真实姓名（currentUser.getRealName()），非登录账号"
    dict: "-"
  - name: company_name
    type: unknown
    desc: "弹出时写入的企业名称（cust_company_info.name）"
    dict: "-"
  - name: popup_time
    type: unknown
    desc: "卡片弹出时间；有值即视为已弹出，弹出次数统计口径"
    dict: "-"
  - name: click_time
    type: unknown
    desc: "卡片点击时间；recordClick 成功即写入，全表仅 252 行埋点"
    dict: "-"
  - name: db_tenant_code
    type: unknown
    desc: "数据租户标识；实测仅 beehive-scf.qhhrly.cn 一个值，与 isPosterAllowedTenant 灰度口径对应"
    dict: "-"
  - name: enable
    type: unknown
    desc: "逻辑有效标记，实测全为 Y"
    dict: "DB default 'Y'"
```

---END FILE---

---FILE: tables/cust_survey_answer.md ---
---
type: table
title: 调研问卷答案表
page_key: cust_survey_answer
domain: 客户管理
status: draft
aliases: [调研答案, 问卷答案表, survey_answer]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_survey_answer
  - code_path:CustSurveyController.java:submit
  - pplatform-apaas-service/CustSurveyAnswerService.java
  - db:cust_survey_answer.db_tenant_code
contract_version: "0.1"
---

本表存放落库题库问卷的作答明细：一行一个选项，多选时同一 `question_no` 会出现多行。它是「调研问卷」这条链路的答案载体，与外部问卷星的答卷数据互不读写，两者的边界见 [[concepts/wenjuan]]。当前唯一在用的问卷见口径 [[calibers/survey_code_xyl_2024_q1]]，跨租户口径见 [[calibers/survey_answer_all_tenant]]，有效记录口径见 [[calibers/cust_survey_answer_enabled]]。

## 需求背景

答案表按 `company_id + survey_code` 组成普通索引，作答主体是「当前登录企业 + 当前登录用户」，因此同一企业可以有多个用户各自提交多行答案；`other_text` 承载「其他」选项的自由文本，实测存在 '1'、'hjhh'、'饿啊讽德诵功' 等脏数据，说明该列未做输入约束。

落库路径本身未被本链路覆盖：`CustSurveyController.submit` 调用 `custSurveyAnswerService.submit(req, companyId, userId)`，但 apaas 侧 `CustSurveyAnswerService` 仅提供通用 BaseService/查询 helper，无 submit/checkPopup 实现，写值规则不可验证（见 [[rules/survey_answer_write_path_review]]）。

## 版本演进

- 当前观测：338 行，`survey_code` 恒为 `XYL_2024_Q1`，`db_tenant_code` 唯一值 `all`，`enable` 全为 `Y`。
- 代码链路中未见 `survey_code` 的常量定义，问卷范围属数据驱动。
- 字段物理类型未在语义分析证据中给出，锚点块 `type` 记为 `unknown`。

```ground:table
table: cust_survey_answer
fields:
  - name: survey_code
    type: unknown
    desc: "问卷编码；实测全表唯一值 XYL_2024_Q1，代码链路中未见常量定义"
    dict: "-"
  - name: question_no
    type: unknown
    desc: "题号（1~N）；实测 1-6 题各约 56 行"
    dict: "-"
  - name: answer_value
    type: unknown
    desc: "选项明文，多选时每个选项单独一行"
    dict: "-"
  - name: other_text
    type: unknown
    desc: "选项为「其他」时填写的自由文本；实测存在 '1'、'hjhh'、'饿啊讽德诵功' 等脏数据"
    dict: "-"
  - name: company_id
    type: unknown
    desc: "答题企业ID（当前登录企业），与 survey_code 组成普通索引"
    dict: "-"
  - name: user_id
    type: unknown
    desc: "答题用户ID（当前登录用户）"
    dict: "-"
  - name: submit_time
    type: unknown
    desc: "问卷提交时间"
    dict: "-"
  - name: enable
    type: unknown
    desc: "有效记录标记；调研答案有效记录口径为 enable = 'Y'（实测 338 行全 Y）"
    dict: "-"
```

---END FILE---

---FILE: tables/cust_company_survey_state.md ---
---
type: table
title: 企业级问卷活动状态表
page_key: cust_company_survey_state
domain: 客户管理
status: draft
aliases: [问卷活动状态表, survey_state]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_company_survey_state
  - code_path:WenjuanController.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
contract_version: "0.1"
---

本表是问卷星活动的企业级状态：以 `company_id` 为键，记录该企业首个用户首次访问时间，以及首个用户转盘抽奖是否已展示。它是「谁是企业首个访问用户」这一判定的落点，但判定结果本身不落用户字段，只落一个展示标记，概念边界见 [[concepts/first_visitor]]。状态机见 [[processes/first_visitor_lottery_shown]]。

## 需求背景

活动的展示对象被收窄到「企业首个访问用户」：同一企业的其他用户首页不展示抽奖、指引与右下角入口（[[rules/first_visitor_only_ui]]）。为防止刷新重复展示转盘，前端动效结束后回调 `mark-lottery-shown`，由服务端把 `first_visitor_lottery_shown` 单向置 `Y`（[[rules/lottery_shown_idempotent]]）。整个链路读写前强制 `MetaDataThreadLocalConfig.setDbTenantCode("all")`（[[rules/wenjuan_all_tenant_fallback]]、[[calibers/wenjuan_all_tenant]]）。

答卷完成态不在本表：`syncAndResolve` 每次实时调问卷星查 `isSurveyCompleted`，接口注释明确「答卷状态不落库」（[[rules/survey_status_not_persisted]]）。

## 版本演进

- 当前观测：`first_visitor_lottery_shown` 11 行全为 `Y`，无 `N` 样本，`N` 仅由代码语义推断（见 [[enums/first_visitor_lottery_shown]]）。
- `db_tenant_code` 实测 `all`(10) 与 `LN1`(1) 并存，代码在 Wenjuan 链路强制写 `all`，该行属口径外历史/异常数据（[[enums/cust_company_survey_state_db_tenant_code]]）。
- 字段物理类型未在语义分析证据中给出，锚点块 `type` 记为 `unknown`；表结构证据在 `respondent` 之后出现截断，是否存在独立的「首个访问用户ID」列无法从现有证据确认（见 REVIEW）。

```ground:table
table: cust_company_survey_state
fields:
  - name: company_id
    type: unknown
    desc: "企业ID，问卷活动「首个访问用户」claim 的判定键"
    dict: "-"
  - name: respondent
    type: unknown
    desc: "问卷星答题人标识；实现写入的是 String.valueOf(companyId)，即企业ID字符串，并非答题人ID"
    dict: "-"
  - name: first_visit_time
    type: unknown
    desc: "企业首个用户首次访问时间"
    dict: "-"
  - name: first_visitor_lottery_shown
    type: unknown
    desc: "首个用户转盘抽奖是否已展示（Y/N）；实测 11 行全为 Y，无 N 样本"
    dict: "字面量 Y/N（无枚举类）"
  - name: db_tenant_code
    type: unknown
    desc: "数据租户标识；实测 all(10) 与 LN1(1) 并存，与代码强制 setDbTenantCode(\"all\") 存在不一致样本"
    dict: "-"
```

---END FILE---

---FILE: tables/cust_company_survey_whitelist.md ---
---
type: table
title: 问卷活动企业白名单表
page_key: cust_company_survey_whitelist
domain: 客户管理
status: draft
aliases: [问卷白名单, survey_whitelist]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:isParticipating
  - code_path:WenjuanDisplayService.java:getSurveyUrl
  - db:cust_company_survey_whitelist
contract_version: "0.1"
---

白名单表决定哪些企业能参与问卷星活动：`isParticipating(companyId)` 以其为判定键，不在名单内时首页直接返回 `NONE`，`getSurveyUrl` 抛「企业不在白名单列表中！」。口径定义见 [[calibers/wenjuan_whitelist_enabled]]，规则见 [[rules/wenjuan_whitelist_participation]]。企业名称快照与 [[tables/cust_company_info]] 的 `name` 同源。

## 需求背景

活动投放采取「名单制 + 首用户可见」两层收窄：先由本表限定企业范围，再由 [[tables/cust_company_survey_state]] 的 claim 判定限定到企业首个访问用户（[[concepts/first_visitor]]）。实测 11 家，含「测试抽奖企业」系列测试数据，说明名单在投产前经历过测试配置。

## 版本演进

- 当前观测：11 行，`enable` 全为 `Y`，尚无失效样例可验证 `enable='N'` 的行为。
- 字段物理类型未在语义分析证据中给出，锚点块 `type` 记为 `unknown`。

```ground:table
table: cust_company_survey_whitelist
fields:
  - name: company_id
    type: unknown
    desc: "参与问卷活动白名单的企业ID（isParticipating 判定键）"
    dict: "-"
  - name: company_name
    type: unknown
    desc: "白名单企业名称；实测 11 家，含「测试抽奖企业」系列测试数据"
    dict: "-"
  - name: enable
    type: unknown
    desc: "白名单有效标记，实测全为 Y"
    dict: "-"
```

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: 客户企业信息表
page_key: cust_company_info
domain: 客户管理
status: draft
aliases: [企业信息表, company_info]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:validateFinanceUser
  - code_path:GptLearnService.java:checkPosterStatus
  - code_path:ProfileController.java:getAppId
  - db:cust_company_info
contract_version: "0.1"
---

本表是企业的基本信息来源，在本次范围内只被两条链路读取：GP学习引流用它判断企业角色（`cust_company_type` 必须为 FINANCE）并取企业名称与数据租户；问卷/画像链路用它取企业名称与租户。企业角色判定见 [[rules/gpt_learn_finance_only]]，租户灰度见 [[rules/poster_allowed_tenant]]。术语桥见 [[concepts/company_profile]]。

## 需求背景

引流入口的白名单不是按企业逐个配置，而是按企业角色 + 数据租户两个维度过滤，因此本表的 `cust_company_type` 与 `db_tenant_code` 是两个关键判定位：`cust_company_type` 是 JSON 数组字符串（如 `["FINANCE"]`），代码用 `CustCompanyTypeEnum.FINANCE.getDictKey()` 与之比较；`db_tenant_code` 作为 `isPosterAllowedTenant` 的入参来源。

`name` 被写入 [[tables/gpt_learn_poster_log]] 的 `company_name` 与 [[tables/cust_company_survey_whitelist]] 的 `company_name`，属快照式引用。

## 版本演进

- 本次范围内未见企业画像业务实现：`ProfileController` 的 @Api 标注为「性能测试接口」，路径 `/profile-web/`，仅提供取企业简要信息、按 dbTenantCode 取租户、分页用户、取 token 四个测试能力（见 [[concepts/company_profile]]）。
- 字段物理类型未在语义分析证据中给出，锚点块 `type` 记为 `unknown`。

```ground:table
table: cust_company_info
fields:
  - name: id
    type: unknown
    desc: "企业主键；「企业画像 / Profile」术语桥以 cust_company_info.id 为锚点字段"
    dict: "-"
  - name: cust_company_type
    type: unknown
    desc: "企业角色，JSON 数组字符串（如 [\"FINANCE\"]）；GP学习引流要求必须为 FINANCE，代码用 CustCompanyTypeEnum.FINANCE.getDictKey() 比较"
    dict: "CustCompanyTypeEnum"
  - name: name
    type: unknown
    desc: "企业名称，被写入 gpt_learn_poster_log.company_name 与 cust_company_survey_whitelist.company_name"
    dict: "-"
  - name: db_tenant_code
    type: unknown
    desc: "企业所属数据租户标识；isPosterAllowedTenant(companyInfo.getDbTenantCode()) 的入参来源"
    dict: "-"
```

---END FILE---

---FILE: processes/wenjuan_home_display_scene.md ---
---
type: process
title: 问卷星活动首页展示场景决策
page_key: wenjuan_home_display_scene
domain: 客户管理
status: draft
aliases: [displayScene, 首页展示场景, 活动UI决策]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - code_path:WenjuanController.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:markLotteryShown
contract_version: "0.1"
---

这是接口返回的展示决策，不落库：`WenjuanHomeDisplayConfigDTO.displayScene` 由 `resolveHomeDisplay` 每次实时计算，取值集合见 [[enums/wenjuan_home_display_scene]]。决策依赖白名单（[[calibers/wenjuan_whitelist_enabled]]）、企业首个访问用户判定（[[concepts/first_visitor]]）以及外部问卷星的完成态（[[rules/survey_status_not_persisted]]）。

## 需求背景

首页活动 UI 分三档：完全不出活动（`NONE`）、只出指引弹窗 + 右下角问卷入口（`GUIDE_ONLY`）、抽奖转盘 + 中奖弹窗 + 右下角入口（`FIRST_VISITOR_LOTTERY`）。转盘只在「白名单企业 + 企业首个访问用户 + 转盘未展示」三者同时成立时给出，前端动效结束后回调 `mark-lottery-shown` 降档为 `GUIDE_ONLY`，实现防刷新重复。活动企业的首个访问用户还会被留在产融首页（[[rules/stay_on_home_for_survey]]）。

## 版本演进

- 答题完成态实时向问卷星查询，本地不缓存，因此同一用户在完成后再次进入首页会直接落到 `GUIDE_ONLY`。
- 状态判定键为 `WenjuanHomeDisplayConfigDTO.displayScene`，无对应落库字段。

```ground:process
name: 问卷星活动首页展示场景（非落库，接口返回的展示决策）
field: WenjuanHomeDisplayConfigDTO.displayScene
states:
  - value: NONE
    label: 不展示任何活动UI
    source: code_enum
  - value: FIRST_VISITOR_LOTTERY
    label: 转盘抽奖+中奖弹窗+右下角问卷入口
    source: code_enum
  - value: GUIDE_ONLY
    label: 指引弹窗+右下角问卷入口
    source: code_enum
transitions:
  - from: NONE
    event: 活动未配置 / userId或companyId为空 / 企业不在白名单
    to: NONE
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
  - from: NONE
    event: 白名单企业但非企业首个访问用户
    to: NONE
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
  - from: NONE
    event: 白名单企业 + 首个访问用户 + 转盘未展示
    to: FIRST_VISITOR_LOTTERY
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
  - from: FIRST_VISITOR_LOTTERY
    event: 前端动效结束调用 /cust-web/wenjuan/mark-lottery-shown
    to: GUIDE_ONLY
    evidence: "code_path:WenjuanController.java:markLotteryShown + WenjuanDisplayService.java:markLotteryShown"
  - from: FIRST_VISITOR_LOTTERY
    event: 转盘已展示且问卷星 isSurveyCompleted=true（只留右下角入口，不弹指引）
    to: GUIDE_ONLY
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
```

---END FILE---

---FILE: processes/first_visitor_lottery_shown.md ---
---
type: process
title: 首个用户转盘抽奖展示标记
page_key: first_visitor_lottery_shown
domain: 客户管理
status: draft
aliases: [转盘展示标记, lottery_shown, 防刷新标记]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:markLotteryShown
  - db:cust_company_survey_state.first_visitor_lottery_shown
contract_version: "0.1"
---

该状态机描述 `cust_company_survey_state.first_visitor_lottery_shown` 的单向翻转：代码只会把标记置 `Y`，不存在置回 `N` 的路径。取值见 [[enums/first_visitor_lottery_shown]]，规则见 [[rules/lottery_shown_idempotent]]，落点表见 [[tables/cust_company_survey_state]]。

## 需求背景

转盘抽奖是「首个访问用户」独占的权益（[[concepts/first_visitor]]），刷新首页不能重复展示，因此用一个企业级标记做幂等：前端动效播完后调 `POST /cust-web/wenjuan/mark-lottery-shown`，服务端先 `setDbTenantCode("all")`，再异步执行 `markFirstVisitorLotteryShownIfMatch(userId, companyId)`，只对企业首个用户生效。该幂等标记是 `NONE → FIRST_VISITOR_LOTTERY` 之后不回落的关键（见 [[processes/wenjuan_home_display_scene]]）。

## 版本演进

- 当前观测：11 行全为 `Y`，DB 未出现 `N` 样本；`N` 作为初始态仅由代码语义推断。
- 写入为异步线程，且写前强制跨租户 `all`（[[calibers/wenjuan_all_tenant]]、[[rules/wenjuan_all_tenant_fallback]]）。

```ground:process
name: 首个用户转盘抽奖展示标记
field: cust_company_survey_state.first_visitor_lottery_shown
states:
  - value: Y
    label: 已展示（防刷新重复）
    source: db_dist
  - value: N
    label: 未展示（初始态，代码仅单向置 Y，DB 未观测到 N 样本）
    source: code_const
transitions:
  - from: N
    event: POST /cust-web/wenjuan/mark-lottery-shown（异步线程执行，先 setDbTenantCode(all)）
    to: Y
    evidence: "code_path:WenjuanController.java:markLotteryShown + WenjuanDisplayService.java:markLotteryShown"
```

---END FILE---

---FILE: processes/gpt_learn_poster_log_lifecycle.md ---
---
type: process
title: 智能审核引流卡片埋点生命周期
page_key: gpt_learn_poster_log_lifecycle
domain: 客户管理
status: draft
aliases: [引流卡片生命周期, poster lifecycle, 弹窗状态机]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:validateFinanceUser
  - code_path:GptLearnService.java:checkPosterStatus
  - code_path:GptLearnService.java:recordPosterClick
  - db:gpt_learn_poster_log
contract_version: "0.1"
---

状态机的落点是 [[tables/gpt_learn_poster_log]] 的 `popup_time` / `click_time`：`SHOWN` 等价于新写入一行且 `popup_time` 有值，`CLICKED` 等价于该行 `click_time` 有值。前置校验对应三条规则：[[rules/gpt_learn_finance_only]]、[[rules/poster_allowed_tenant]]、[[rules/poster_popup_max_count]]；术语见 [[concepts/gpt_learn]]。

## 需求背景

卡片按「打扰频次可控、投放范围可控」设计：不弹（`NOT_SHOW`）由三类原因造成——企业不是金融机构、租户不在灰度名单、同一用户在该企业的弹出次数已达上限；只有全部通过才落埋点并返回 `recordId`。点击回写要求 `recordId + userId + companyId` 三者匹配，否则抛「埋点记录不存在或已记录点击」，因此 `CLICKED` 是单次可达的终态。

## 版本演进

- 当前观测：全表 252 行，`enable` 全 `Y`，`db_tenant_code` 仅 `beehive-scf.qhhrly.cn`，说明投产投放面很窄。
- `INIT` / `NOT_SHOW` / `SHOWN` / `CLICKED` 为代码语义状态，字典中无对应落库枚举列，仅 `popup_time`/`click_time` 有无值可判定。

```ground:process
name: 智能审核引流卡片埋点生命周期
field: gpt_learn_poster_log.popup_time / gpt_learn_poster_log.click_time
states:
  - value: INIT
    label: 未评估
    source: code_const
  - value: NOT_SHOW
    label: 不弹出（非金融机构 / 租户不允许 / 已达弹出上限）
    source: code_const
  - value: SHOWN
    label: 已弹出并落埋点（popup_time 有值）
    source: code_const
  - value: CLICKED
    label: 已点击（click_time 有值）
    source: code_const
transitions:
  - from: INIT
    event: 企业类型非 CustCompanyTypeEnum.FINANCE（validateFinanceUser 抛「仅金融机构用户可使用」）
    to: NOT_SHOW
    evidence: "code_path:GptLearnService.java:validateFinanceUser"
  - from: INIT
    event: isPosterAllowedTenant(dbTenantCode)=false
    to: NOT_SHOW
    evidence: "code_path:GptLearnService.java:checkPosterStatus"
  - from: INIT
    event: countByUserAndCompany(userId,companyId) >= maxPosterCount
    to: NOT_SHOW
    evidence: "code_path:GptLearnService.java:checkPosterStatus"
  - from: INIT
    event: 校验通过，createPopupRecord 写入 gpt_learn_poster_log(popup_time)
    to: SHOWN
    evidence: "code_path:GptLearnService.java:checkPosterStatus"
  - from: SHOWN
    event: POST /app-web/gptlearn/recordPosterClick(recordId) 且 recordId+userId+companyId 匹配成功
    to: CLICKED
    evidence: "code_path:GptLearnService.java:recordPosterClick"
  - from: SHOWN
    event: recordClick 未匹配（抛「埋点记录不存在或已记录点击」）
    to: SHOWN
    evidence: "code_path:GptLearnService.java:recordPosterClick"
```

---END FILE---

---FILE: calibers/wenjuan_whitelist_enabled.md ---
---
type: caliber
title: 问卷活动参与企业白名单口径
page_key: wenjuan_whitelist_enabled
domain: 客户管理
status: draft
aliases: [白名单口径, isParticipating 口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - db:cust_company_survey_whitelist.enable
contract_version: "0.1"
---

活动可见范围的判定口径：企业需同时满足「在 [[tables/cust_company_survey_whitelist]] 中登记」且 `enable = 'Y'`。对应规则 [[rules/wenjuan_whitelist_participation]]，影响首页展示决策 [[processes/wenjuan_home_display_scene]] 与专属答题链接获取。

## 需求背景

白名单是活动投放的第一道闸门：未命中的企业首页返回 `NONE`，直接调 `getSurveyUrl` 也会被拒绝。DB 观测 11 行 `enable` 全为 `Y`，尚无失效样例。

## 版本演进

- 当前观测：`enable` 全 `Y`（11 行），`enable='N'` 的实际行为未被验证。

```ground:caliber
name: 问卷活动参与企业白名单
predicate: cust_company_survey_whitelist.enable = 'Y'
scope: WenjuanDisplayService.isParticipating(companyId) 判定是否展示活动与获取专属答题链接
evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay + db:cust_company_survey_whitelist.enable 全 Y（11 行）"
```

---END FILE---

---FILE: calibers/gpt_learn_poster_log_enabled.md ---
---
type: caliber
title: 引流卡片埋点有效记录口径
page_key: gpt_learn_poster_log_enabled
domain: 客户管理
status: draft
aliases: [埋点有效口径, poster enable 口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:checkPosterStatus
  - db:gpt_learn_poster_log.enable
contract_version: "0.1"
---

[[tables/gpt_learn_poster_log]] 的有效记录口径为 `enable = 'Y'`：弹出次数统计 `countByUserAndCompany` 与点击记录 `recordClick` 都以此为准，直接影响 [[rules/poster_popup_max_count]] 的计数结果与 [[processes/gpt_learn_poster_log_lifecycle]] 的状态推进。

## 需求背景

弹出上限按「同一用户 + 同一企业」累计，若无效记录被计入会提前触发 `NOT_SHOW`，因此有效标记是计数口径的一部分。当前实测 252 行全为 `Y`，逻辑删除尚未被实际使用。

## 版本演进

- 当前观测：`enable` 全 `Y`（252 行），与 [[enums/gpt_learn_poster_log_enable]] 一致。

```ground:caliber
name: 引流卡片埋点有效记录
predicate: gpt_learn_poster_log.enable = 'Y'
scope: 弹出次数统计 countByUserAndCompany 与点击记录 recordClick
evidence: "code_path:GptLearnService.java:checkPosterStatus + db:gpt_learn_poster_log.enable 全 Y（252 行）"
```

---END FILE---

---FILE: calibers/cust_survey_answer_enabled.md ---
---
type: caliber
title: 调研答案有效记录口径
page_key: cust_survey_answer_enabled
domain: 客户管理
status: draft
aliases: [答案有效口径, answer enable 口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_survey_answer.enable
contract_version: "0.1"
---

[[tables/cust_survey_answer]] 的查询口径为 `enable = 'Y'`，用于调研问卷答案范围过滤。

## 需求背景

答案表按企业 + 问卷 + 用户组织，逻辑有效标记用于在不物理删除的前提下剔除历史/作废答案。写值点未在本链路给出（[[rules/survey_answer_write_path_review]]），因此 `enable` 的赋值行为无法核对。

## 版本演进

- 当前观测：338 行全为 `Y`，未见 `N` 样本。

```ground:caliber
name: 调研答案有效记录
predicate: cust_survey_answer.enable = 'Y'
scope: 调研问卷答案查询
evidence: "db:cust_survey_answer.enable 全 Y（338 行）"
```

---END FILE---

---FILE: calibers/wenjuan_all_tenant.md ---
---
type: caliber
title: 问卷活动数据跨租户口径（all）
page_key: wenjuan_all_tenant
domain: 客户管理
status: draft
aliases: [问卷 all 租户口径, setDbTenantCode all]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - db:cust_company_survey_state.db_tenant_code
contract_version: "0.1"
---

问卷活动链路的读写口径是「不按租户隔离」：`WenjuanController.markLotteryShown/surveyUrl` 与 `WenjuanDisplayService.resolveHomeDisplay/shouldStayOnHomeForGotoProduct` 均先 `MetaDataThreadLocalConfig.setDbTenantCode("all")`。对应规则 [[rules/wenjuan_all_tenant_fallback]]，落点表 [[tables/cust_company_survey_state]]。

## 需求背景

活动状态与答案被视为全租户统一数据，避免同一企业在不同租户下出现两套活动状态；代价是数据不再按租户隔离，历史遗留行可能落在非 `all` 租户下。

## 版本演进

- 当前观测：`cust_company_survey_state.db_tenant_code` 为 `all`(10) 与 `LN1`(1) 并存，`LN1` 行与代码强制口径不一致，属历史/异常数据，需人工核实（见 [[enums/cust_company_survey_state_db_tenant_code]]）。

```ground:caliber
name: 问卷活动数据跨租户口径（all）
predicate: cust_company_survey_state.db_tenant_code = 'all'
scope: 问卷活动首个访问用户 claim 与抽奖标记读写前强制 MetaDataThreadLocalConfig.setDbTenantCode("all")
evidence: "code_path:WenjuanController.java:markLotteryShown + WenjuanDisplayService.java:resolveHomeDisplay + db:cust_company_survey_state.db_tenant_code all=10"
```

---END FILE---

---FILE: calibers/survey_answer_all_tenant.md ---
---
type: caliber
title: 调研答案跨租户口径（all）
page_key: survey_answer_all_tenant
domain: 客户管理
status: draft
aliases: [答案 all 租户口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_survey_answer.db_tenant_code
contract_version: "0.1"
---

[[tables/cust_survey_answer]] 的数据被视为全租户统一，`db_tenant_code` 唯一值为 `all`（338 行）。

## 需求背景

调研答案不参与租户隔离，与 [[calibers/wenjuan_all_tenant]] 属同一设计取向：问卷类数据按「全局一份」管理。该口径由数据分布观察得到，代码侧写值点未在本链路给出（[[rules/survey_answer_write_path_review]]）。

## 版本演进

- 当前观测：`db_tenant_code` 唯一值 `all`，无其他租户样本。

```ground:caliber
name: 调研答案跨租户口径（all）
predicate: cust_survey_answer.db_tenant_code = 'all'
scope: 调研问卷答案为全租户统一数据
evidence: "db:cust_survey_answer.db_tenant_code 唯一值 all（338 行）"
```

---END FILE---

---FILE: calibers/survey_code_xyl_2024_q1.md ---
---
type: caliber
title: 当前唯一在用问卷口径
page_key: survey_code_xyl_2024_q1
domain: 客户管理
status: draft
aliases: [XYL_2024_Q1, 在用问卷口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_survey_answer.survey_code
contract_version: "0.1"
---

调研答案的问卷范围口径为 `survey_code = 'XYL_2024_Q1'`：全表唯一值，共 338 行。

## 需求背景

该问卷编码在代码链路中没有常量定义，属数据驱动——问卷的增删改由数据侧决定，代码无需发布即可切换问卷范围。术语边界见 [[concepts/wenjuan]]。

## 版本演进

- 当前观测：`survey_code` 唯一值 `XYL_2024_Q1`，尚无第二份问卷样本。

```ground:caliber
name: 当前唯一在用问卷
predicate: cust_survey_answer.survey_code = 'XYL_2024_Q1'
scope: 调研问卷答案范围（代码中未常量定义，属数据驱动）
evidence: "db:cust_survey_answer.survey_code 唯一值 XYL_2024_Q1（338 行）"
```

---END FILE---

---FILE: rules/gpt_learn_finance_only.md ---
---
type: rule
title: GP学习/智能审核引流仅限金融机构用户
page_key: gpt_learn_finance_only
domain: 客户管理
status: draft
aliases: [仅金融机构可引流, validateFinanceUser]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:validateFinanceUser
  - code_path:GptLearnService.java:checkPosterStatus
contract_version: "0.1"
---

三个入口 `syncLoginInfo` / `checkPosterStatus` / `recordPosterClick` 都先执行 `validateFinanceUser`：`currentUser` 非空且企业角色必须等于 `CustCompanyTypeEnum.FINANCE.getDictKey()`，否则抛「仅金融机构用户可使用」；企业信息不存在抛「企业信息不存在」。判定位来自 [[tables/cust_company_info]] 的 `cust_company_type`，效果是 [[processes/gpt_learn_poster_log_lifecycle]] 中的 `INIT → NOT_SHOW`。

## 需求背景

引流卡片面向金融机构用户投放，因此把企业角色作为最前置的准入条件，非 FINANCE 企业连埋点都不会产生。`cust_company_type` 存的是 JSON 数组字符串（如 `["FINANCE"]`），比较走字典 key。

## 版本演进

- 当前观测：`gpt_learn_poster_log` 仅 252 行且租户单一，与该规则叠加后投放面很窄。

```ground:rule
name: GP学习/智能审核引流仅限金融机构用户
content: "syncLoginInfo / checkPosterStatus / recordPosterClick 入口均先执行 validateFinanceUser：currentUser 非空且 companyType 必须等于 CustCompanyTypeEnum.FINANCE.getDictKey()，否则抛「仅金融机构用户可使用」；企业信息不存在抛「企业信息不存在」"
impact: 非 FINANCE 企业用户调用引流接口直接失败，不产生埋点
field_targets:
  - cust_company_info.cust_company_type
evidence: "code_path:GptLearnService.java:validateFinanceUser + GptLearnService.java:checkPosterStatus"
```

---END FILE---

---FILE: rules/poster_popup_max_count.md ---
---
type: rule
title: 引流卡片弹出次数上限
page_key: poster_popup_max_count
domain: 客户管理
status: draft
aliases: [弹出上限, maxPosterCount]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:checkPosterStatus
  - code_path:GptLearnPosterLogDao.countByUserAndCompany
contract_version: "0.1"
---

计数维度是 `user_id + company_id`：累计埋点行数达到 `gptLearnProperties.getMaxPosterCount()` 时返回 `notShow`，不再创建弹出记录。计数口径受 [[calibers/gpt_learn_poster_log_enabled]] 约束（只统计有效记录），状态效果见 [[processes/gpt_learn_poster_log_lifecycle]] 的 `INIT → NOT_SHOW`。

## 需求背景

该上限用来控制打扰频次，是「弹不弹」的最后一个校验点；达到上限是 `NOT_SHOW` 的第三种原因（另两种见 [[rules/gpt_learn_finance_only]] 与 [[rules/poster_allowed_tenant]]）。

## 版本演进

- 上限值由配置项 `gptLearnProperties.getMaxPosterCount()` 提供，语义分析未给出具体数值，不在本页断言。

```ground:rule
name: 引流卡片弹出次数上限
content: "同一 user_id + company_id 的埋点记录数 >= gptLearnProperties.getMaxPosterCount() 时返回 notShow，不再创建弹出记录"
impact: 控制打扰频次，决定是否新增 gpt_learn_poster_log 行
field_targets:
  - gpt_learn_poster_log.user_id
  - gpt_learn_poster_log.company_id
  - gpt_learn_poster_log.popup_time
evidence: "code_path:GptLearnService.java:checkPosterStatus + GptLearnPosterLogDao.countByUserAndCompany"
```

---END FILE---

---FILE: rules/poster_allowed_tenant.md ---
---
type: rule
title: 引流卡片仅白名单租户可弹
page_key: poster_allowed_tenant
domain: 客户管理
status: draft
aliases: [租户灰度, isPosterAllowedTenant]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:checkPosterStatus
  - db:gpt_learn_poster_log.db_tenant_code
contract_version: "0.1"
---

`isPosterAllowedTenant(companyInfo.getDbTenantCode())` 为 false 时 `checkPosterStatus` 直接返回 `notShow`。租户取自 [[tables/cust_company_info]]，落点字段是 [[tables/gpt_learn_poster_log]] 的 `db_tenant_code`（见 [[enums/gpt_learn_poster_log_db_tenant_code]]）。

## 需求背景

引流卡片按数据租户灰度投放。DB 实测埋点仅落在 `beehive-scf.qhhrly.cn` 一个租户值上，与该白名单机制吻合。

## 版本演进

- 当前观测：`db_tenant_code` 唯一值 `beehive-scf.qhhrly.cn`，白名单范围目前极窄。

```ground:rule
name: 引流卡片仅白名单租户可弹
content: isPosterAllowedTenant(companyInfo.getDbTenantCode()) 为 false 时直接 notShow
impact: 按 db_tenant_code 灰度投放引流卡片；DB 实测埋点仅落在 beehive-scf.qhhrly.cn
field_targets:
  - gpt_learn_poster_log.db_tenant_code
evidence: "code_path:GptLearnService.java:checkPosterStatus + db:gpt_learn_poster_log.db_tenant_code"
```

---END FILE---

---FILE: rules/wenjuan_whitelist_participation.md ---
---
type: rule
title: 问卷活动仅白名单企业参与
page_key: wenjuan_whitelist_participation
domain: 客户管理
status: draft
aliases: [问卷白名单规则, getSurveyUrl 拒绝]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - code_path:WenjuanDisplayService.java:getSurveyUrl
contract_version: "0.1"
---

`companySurveyWhitelistDao.isParticipating(companyId)` 为 false 时首页返回 `NONE`；`getSurveyUrl` 时抛「企业不在白名单列表中！」。判定位见 [[tables/cust_company_survey_whitelist]]，口径见 [[calibers/wenjuan_whitelist_enabled]]。

## 需求背景

白名单同时控制「看不看得见活动」与「拿不拿得到专属答题链接」两件事，是活动可见范围的第一道闸门；第二个闸门是首个访问用户判定（[[rules/first_visitor_only_ui]]）。

## 版本演进

- 当前观测：白名单 11 行全为有效，含测试数据。

```ground:rule
name: 问卷活动仅白名单企业参与
content: "companySurveyWhitelistDao.isParticipating(companyId) 为 false 时首页返回 NONE；getSurveyUrl 时抛「企业不在白名单列表中！」"
impact: 控制活动可见范围与专属答题链接获取
field_targets:
  - cust_company_survey_whitelist.company_id
  - cust_company_survey_whitelist.enable
evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay + WenjuanDisplayService.java:getSurveyUrl"
```

---END FILE---

---FILE: rules/first_visitor_only_ui.md ---
---
type: rule
title: 仅企业首个访问用户可见活动UI
page_key: first_visitor_only_ui
domain: 客户管理
status: draft
aliases: [首访用户可见, claimFirstVisitor 规则]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
contract_version: "0.1"
---

`claimFirstVisitor` 判定 `isFirstVisitor`；非首个访问用户时 `displayScene` 固定 `NONE`，抽奖、指引、右下角入口一律不展示。判定与落点见 [[tables/cust_company_survey_state]] 与 [[concepts/first_visitor]]，效果见 [[processes/wenjuan_home_display_scene]]。

## 需求背景

活动权益按企业独占给首个访问用户，避免同企业多人重复领取；该判定同时决定是否把用户留在产融首页（[[rules/stay_on_home_for_survey]]）。

## 版本演进

- 「首个用户」由 `claimFirstVisitor(companyId,userId,respondent,dbTenantCode)` 动态判定，判定结果不落用户字段。

```ground:rule
name: 仅企业首个访问用户可见活动UI
content: claimFirstVisitor 判定 isFirstVisitor；非首个访问用户时 displayScene 固定 NONE（不展示抽奖、指引、右下角入口）
impact: 同企业其他用户不展示任何活动 UI
field_targets:
  - cust_company_survey_state.company_id
evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
```

---END FILE---

---FILE: rules/survey_status_not_persisted.md ---
---
type: rule
title: 答卷完成态不落库，实时调问卷星
page_key: survey_status_not_persisted
domain: 客户管理
status: draft
aliases: [不落完成态, isSurveyCompleted 实时查询]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:syncAndDisplayConfig
  - code_path:WenjuanDisplayService.java:syncAndResolve
contract_version: "0.1"
---

`syncAndResolve` 即 `resolveHomeDisplay`，每次实时调 `wenjuanOpenApiClient.isSurveyCompleted(respondent)`；接口注释明确「答卷状态不落库」。

## 需求背景

答卷数据由外部问卷星持有，本地只保留企业级活动状态（[[tables/cust_company_survey_state]]），因此完成态无法离线判断，接口响应时间受外部依赖影响。`respondent` 实际存的是企业ID字符串，见 [[concepts/respondent]]。

## 版本演进

- 当前观测：`cust_company_survey_state` 中不存在问卷完成态字段，与「不落库」的说法一致。

```ground:rule
name: 答卷完成态不落库，实时调问卷星
content: syncAndResolve 即 resolveHomeDisplay，每次实时调 wenjuanOpenApiClient.isSurveyCompleted(respondent)；接口注释明确「答卷状态不落库」
impact: cust_company_survey_state 中不存在问卷完成态字段，本地无法离线判断完成情况
field_targets:
  - cust_company_survey_state.company_id
evidence: "code_path:WenjuanController.java:syncAndDisplayConfig + WenjuanDisplayService.java:syncAndResolve"
```

---END FILE---

---FILE: rules/lottery_shown_idempotent.md ---
---
type: rule
title: 转盘抽奖防刷新重复（幂等标记）
page_key: lottery_shown_idempotent
domain: 客户管理
status: draft
aliases: [防重复展示, mark-lottery-shown 规则]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:markLotteryShown
  - db:cust_company_survey_state.first_visitor_lottery_shown
contract_version: "0.1"
---

`mark-lottery-shown` 先 `setDbTenantCode(all)`，再异步执行 `markFirstVisitorLotteryShownIfMatch(userId, companyId)`，把 `first_visitor_lottery_shown` 置 `Y`（仅匹配当前企业首个用户）。状态机见 [[processes/first_visitor_lottery_shown]]，取值见 [[enums/first_visitor_lottery_shown]]。

## 需求背景

转盘只对首个访问用户发放（[[concepts/first_visitor]]），刷新首页不能重复播放，因此用一个企业级 `Y/N` 标记做幂等，且只有单向置 `Y` 的路径。

## 版本演进

- 当前观测：该字段 11 行全为 `Y`，无 `N` 样本。

```ground:rule
name: 转盘抽奖防刷新重复（幂等标记）
content: mark-lottery-shown 先 setDbTenantCode(all)，再异步执行 markFirstVisitorLotteryShownIfMatch(userId, companyId) 将 first_visitor_lottery_shown 置 Y（仅匹配当前企业首个用户）
impact: 刷新首页不重复展示转盘；DB 实测该字段 11 行全为 Y
field_targets:
  - cust_company_survey_state.first_visitor_lottery_shown
evidence: "code_path:WenjuanController.java:markLotteryShown + WenjuanDisplayService.java:markLotteryShown + db:cust_company_survey_state.first_visitor_lottery_shown"
```

---END FILE---

---FILE: rules/stay_on_home_for_survey.md ---
---
type: rule
title: 问卷活动留首页策略
page_key: stay_on_home_for_survey
domain: 客户管理
status: draft
aliases: [shouldStayOnHomeForGotoProduct, gotoProduct 不跳转]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:shouldStayOnHomeForGotoProduct
contract_version: "0.1"
---

`shouldStayOnHomeForGotoProduct`：活动有效 + 企业在白名单 + 问卷未完成 + 当前用户为企业首个访问用户时，`gotoProduct` 不自动跳转默认业务产品。

## 需求背景

为提高问卷完成率，首个访问用户被刻意留在产融首页（否则登录后会被自动带去默认业务产品）。四个条件分别对应 [[rules/wenjuan_whitelist_participation]]、[[rules/first_visitor_only_ui]]、[[rules/survey_status_not_persisted]] 与活动自身有效性。

## 版本演进

- 该策略与首页展示决策同源，均在 `dbTenantCode='all'` 口径下计算（[[calibers/wenjuan_all_tenant]]）。

```ground:rule
name: 问卷活动留首页策略
content: "shouldStayOnHomeForGotoProduct：活动有效 + 企业在白名单 + 问卷未完成 + 当前用户为企业首个访问用户时，gotoProduct 不自动跳转默认业务产品"
impact: 首个访问用户被停留在产融首页以完成问卷
field_targets:
  - cust_company_survey_state.company_id
  - cust_company_survey_whitelist.company_id
evidence: "code_path:WenjuanDisplayService.java:shouldStayOnHomeForGotoProduct"
```

---END FILE---

---FILE: rules/wenjuan_all_tenant_fallback.md ---
---
type: rule
title: 问卷活动数据跨租户兜底（all）
page_key: wenjuan_all_tenant_fallback
domain: 客户管理
status: draft
aliases: [all 租户兜底, 跨租户读写]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanController.java:markLotteryShown
  - db:cust_company_survey_state.db_tenant_code
contract_version: "0.1"
---

`WenjuanController.markLotteryShown/surveyUrl` 与 `WenjuanDisplayService.resolveHomeDisplay/shouldStayOnHomeForGotoProduct` 均先 `MetaDataThreadLocalConfig.setDbTenantCode("all")`。口径见 [[calibers/wenjuan_all_tenant]] 与 [[calibers/survey_answer_all_tenant]]。

## 需求背景

问卷活动状态与答案要做成全租户统一数据，因此链路内主动改写租户上下文；这让数据不再按租户隔离，也让历史遗留行成为口径外样本。

## 版本演进

- 当前观测：`cust_company_survey_state.db_tenant_code` 存在 `all`(10) 与 `LN1`(1) 并存，`LN1` 行与代码强制口径不一致，需人工核实（[[enums/cust_company_survey_state_db_tenant_code]]）。

```ground:rule
name: 问卷活动数据跨租户兜底(all)
content: "WenjuanController.markLotteryShown/surveyUrl 与 WenjuanDisplayService.resolveHomeDisplay/shouldStayOnHomeForGotoProduct 均先 MetaDataThreadLocalConfig.setDbTenantCode(\"all\")"
impact: 问卷活动状态与答案不按租户隔离；DB 实测 cust_company_survey_state 仍有 1 行 db_tenant_code=LN1，存在与代码口径不一致的历史数据
field_targets:
  - cust_company_survey_state.db_tenant_code
  - cust_survey_answer.db_tenant_code
evidence: "code_path:WenjuanController.java:markLotteryShown + db:cust_company_survey_state.db_tenant_code（all=10, LN1=1）"
```

---END FILE---

---FILE: rules/survey_answer_write_path_review.md ---
---
type: rule
title: 调研问卷答案落库路径未在本链路给出
page_key: survey_answer_write_path_review
domain: 客户管理
status: draft
aliases: [答案写值点缺失, submit 未实现]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:CustSurveyController.java:submit
  - pplatform-apaas-service/CustSurveyAnswerService.java
  - db:cust_survey_answer
contract_version: "0.1"
---

本页记录一条「无法闭环」的规则：`CustSurveyController.submit` 调用 `custSurveyAnswerService.submit(req, companyId, userId)`，`checkPopup` 调用 `checkPopup(companyId, currentCompanyType)`；但 apaas 侧 `CustSurveyAnswerService` 仅提供通用 BaseService/查询 helper，没有 submit / checkPopup 实现，因此写值点与 `answer_value` / `other_text` / `question_no` 的赋值逻辑无法核对。

## 需求背景

这条缺口的直接影响是：[[tables/cust_survey_answer]] 的 338 行数据「字段怎么填」不可验证；`checkPopup` 的「已过期或已填写则不弹」判定逻辑也不可验证。本页作为待核项保留，见页末 REVIEW。

## 版本演进

- 当前观测：答案表 338 行、`survey_code` 恒为 `XYL_2024_Q1`，但写入侧实现未见。

```ground:rule
name: 调研问卷答案落库路径未在本链路给出（REVIEW）
content: "CustSurveyController.submit 调用 custSurveyAnswerService.submit(req, companyId, userId)，checkPopup 调用 checkPopup(companyId, currentCompanyType)；apaas 侧 CustSurveyAnswerService 仅提供通用 BaseService/查询 helper，无 submit/checkPopup 实现，写值点与 answer_value/other_text/question_no 的赋值逻辑无法核对"
impact: cust_survey_answer 338 行数据字段填充规则不可验证，checkPopup 的「已过期或已填写则不弹」判定逻辑不可验证
field_targets:
  - cust_survey_answer.answer_value
  - cust_survey_answer.other_text
  - cust_survey_answer.question_no
  - cust_survey_answer.submit_time
evidence: "code_path:CustSurveyController.java:submit + pplatform-apaas-service/CustSurveyAnswerService.java + db:cust_survey_answer 338 行（survey_code 恒 XYL_2024_Q1）"
```

---END FILE---

---FILE: concepts/wenjuan.md ---
---
type: concept
title: 问卷（两套并存）
page_key: wenjuan
domain: 客户管理
status: draft
aliases: [Wenjuan, 问卷星活动, Survey, 调研问卷, 调研答案]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:CustSurveyController.java:submit
  - code_path:WenjuanController.java:syncAndDisplayConfig
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - db:cust_survey_answer
  - db:cust_company_survey_state
contract_version: "0.1"
maps_to: cust_survey_answer.survey_code
field_targets:
  - cust_survey_answer.survey_code
  - cust_company_survey_state.company_id
adjudication: boundary
also_confused_with:
  - cust_company_survey_state.company_id
  - cust_company_survey_whitelist.company_id
---

> (document_claim，未证实) 需求/系统文档层（客户管理平台业务规则文档、运营配置管理业务规则文档）通篇未出现 GP学习引流、问卷星活动、企业画像（Profile）的任何业务规则或流程表述，无法形成双源锚点。

「问卷」在本系统中是两套互不相干的实现，页面与接口前缀都会出现 "survey/wenjuan" 字样，极易混用。

- 落库题库问卷：`CustSurveyController`（`/cust-web/survey`），答案写 [[tables/cust_survey_answer]]，问卷范围见 [[calibers/survey_code_xyl_2024_q1]]，有效记录口径见 [[calibers/cust_survey_answer_enabled]]。
- 外部问卷星活动：`WenjuanController`（`/cust-web/wenjuan`），答卷完成态不落库（[[rules/survey_status_not_persisted]]），只落企业级活动状态 [[tables/cust_company_survey_state]]，白名单见 [[tables/cust_company_survey_whitelist]]、展示决策见 [[processes/wenjuan_home_display_scene]]。

## 需求背景

两套问卷的业务目标不同：前者是站内调研，答案留在本地便于统计；后者是运营活动（转盘抽奖 + 问卷入口），答卷由问卷星持有，本地只关心「谁是企业首个访问用户」与「转盘是否已展示」。因此不能把 `cust_survey_answer` 的行数、题号当作活动参与度，也不能用 `cust_company_survey_state` 判断调研是否完成。

## 版本演进

- 当前观测：落库问卷只有一份（`XYL_2024_Q1`，338 行，题号 1-6），活动侧企业状态 11 行、白名单 11 家。
- 文档侧无对应业务规则表述（见页首 document_claim，未证实）。

---END FILE---

---FILE: concepts/respondent.md ---
---
type: concept
title: respondent（受访者）
page_key: respondent
domain: 客户管理
status: draft
aliases: [答题人, 受访人]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:markLotteryShown
  - db:cust_company_survey_state.respondent
contract_version: "0.1"
maps_to: cust_company_survey_state.respondent
field_targets:
  - cust_company_survey_state.respondent
adjudication: boundary
also_confused_with:
  - cust_company_survey_state.company_id
---

字段名像个人，实际写入的是 `String.valueOf(companyId)`，即企业ID字符串。它是传给问卷星开放接口的「答题人」标识，与 [[tables/cust_company_survey_state]] 的 `company_id` 同值，DB 值形如 `1993860367081840641`，与 snowflake 企业ID量级一致。

## 需求背景

活动按企业独占给首个访问用户（[[concepts/first_visitor]]），问卷星侧的身份标识也只用企业维度，因此不需要真实答题人ID。使用方的典型误区是按 `respondent` 关联用户画像或做用户级去重——那会得到企业级结果。

## 版本演进

- 当前观测：`cust_company_survey_state` 中 `respondent` 与企业ID同值，无个人标识样本。
- 完成态查询 `isSurveyCompleted(respondent)` 实时调用外部接口（[[rules/survey_status_not_persisted]]）。

---END FILE---

---FILE: concepts/first_visitor.md ---
---
type: concept
title: 企业首个访问用户
page_key: first_visitor
domain: 客户管理
status: draft
aliases: [firstVisitor, first_visitor_user_id, claimFirstVisitor]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - code_path:WenjuanDisplayService.java:shouldStayOnHomeForGotoProduct
  - db:cust_company_survey_state
contract_version: "0.1"
maps_to: cust_company_survey_state.company_id
field_targets:
  - cust_company_survey_state.company_id
  - cust_company_survey_state.first_visitor_lottery_shown
adjudication: boundary
also_confused_with:
  - cust_survey_answer.user_id
---

「首个用户」由 `claimFirstVisitor(companyId, userId, respondent, dbTenantCode)` 动态判定，当前可见表结构中未出现独立的 `first_visitor_user_id` 列（表结构证据在该列后截断），判定结果不落用户字段，只落 `first_visitor_lottery_shown`。它与 [[tables/cust_survey_answer]] 的 `user_id`（答题人）不是同一概念。

## 需求背景

活动权益按企业级独占：同企业只有首个访问用户能看到活动 UI（[[rules/first_visitor_only_ui]]）、会被留在首页（[[rules/stay_on_home_for_survey]]）、会触发转盘抽奖与幂等标记（[[processes/first_visitor_lottery_shown]]）。

## 版本演进

- 当前观测：`cust_company_survey_state` 11 行状态记录，`first_visitor_lottery_shown` 全为 `Y`；表结构在该列附近出现截断，是否存在首访用户列待核实（见 REVIEW）。

---END FILE---

---FILE: concepts/gpt_learn.md ---
---
type: concept
title: GP学习 / 智能审核引流
page_key: gpt_learn
domain: 客户管理
status: draft
aliases: [GptLearn, 引流卡片, 智能审核, saas中登]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:checkPosterStatus
  - code_path:GptLearnService.java:recordPosterClick
  - code_path:GptLearnService.java:validateFinanceUser
  - db:gpt_learn_poster_log
contract_version: "0.1"
maps_to: gpt_learn_poster_log.id
field_targets:
  - gpt_learn_poster_log.id
  - gpt_learn_poster_log.popup_time
  - gpt_learn_poster_log.click_time
adjudication: boundary
also_confused_with:
  - cust_company_survey_state.company_id
---

> (document_claim，未证实) 需求/系统文档层（客户管理平台业务规则文档、运营配置管理业务规则文档）通篇未出现 GP学习引流、问卷星活动、企业画像（Profile）的任何业务规则或流程表述，无法形成双源锚点。

名称里有「学习」，但它不是在线的学习业务：实为向外部 SaaS 中登同步登录信息并引流跳转的埋点链路，`recordId` 就是 [[tables/gpt_learn_poster_log]] 的 `id`。仅对 FINANCE 企业开放（[[rules/gpt_learn_finance_only]]），并按租户灰度（[[rules/poster_allowed_tenant]]），生命周期见 [[processes/gpt_learn_poster_log_lifecycle]]。

## 需求背景

链路的三个入口——同步登录信息、查询是否弹卡、记录点击——都先做金融机构校验；弹卡还受租户白名单与弹出次数上限约束，点击则以 `recordId + userId + companyId` 匹配保证单次回写。业务目标是让目标企业用户在登录后看到引流卡片并点击跳转，因此埋点表同时是「频次控制表」和「点击回执表」。

## 版本演进

- 当前观测：埋点 252 行，`enable` 全 `Y`，租户仅 `beehive-scf.qhhrly.cn`，投放面很窄。
- 文档侧无对应业务规则表述（见页首 document_claim，未证实）。

---END FILE---

---FILE: concepts/company_profile.md ---
---
type: concept
title: 企业画像 / Profile
page_key: company_profile
domain: 客户管理
status: draft
aliases: [profile-web, 性能测试接口]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:ProfileController.java:getAppId
  - code_path:GptLearnService.java:checkPosterStatus
  - db:cust_company_info
contract_version: "0.1"
maps_to: cust_company_info.id
field_targets:
  - cust_company_info.id
adjudication: boundary
also_confused_with:
  - gpt_learn_poster_log.company_id
---

> (document_claim，未证实) 需求/系统文档层（客户管理平台业务规则文档、运营配置管理业务规则文档）通篇未出现 GP学习引流、问卷星活动、企业画像（Profile）的任何业务规则或流程表述，无法形成双源锚点。

主题名与实际实现不符：`ProfileController` 的 @Api 标注为「性能测试接口」，路径 `/profile-web/`，仅提供四个能力——取企业简要信息、按 `dbTenantCode` 取租户、分页用户、取 token。代码链路中不存在画像标签、画像表或画像计算实现。

## 需求背景

该主题下的接口是企业信息（[[tables/cust_company_info]]）的调试/测试入口，不应被当作「客户画像」能力引用；与之相邻的企业维度数据读取方还有 GP学习引流（按 `cust_company_info.cust_company_type` 与 `db_tenant_code` 过滤，见 [[rules/gpt_learn_finance_only]]、[[rules/poster_allowed_tenant]]）。

## 版本演进

- 当前观测：仅四个测试能力，无画像相关表与实现。
- 文档侧无对应业务规则表述（见页首 document_claim，未证实）。

---END FILE---

---FILE: enums/first_visitor_lottery_shown.md ---
---
type: enum
title: 首个用户转盘抽奖展示标记取值
page_key: first_visitor_lottery_shown
domain: 客户管理
status: draft
aliases: [lottery_shown 取值, 转盘展示 Y/N]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:markLotteryShown
  - db:cust_company_survey_state.first_visitor_lottery_shown
contract_version: "0.1"
---

[[tables/cust_company_survey_state]] 的展示标记取值。写出点为 `markFirstVisitorLotteryShownIfMatch`，是字面量 `'Y'`，不走 `getDictKey` 统一字典。

## 需求背景

标记用于转盘抽奖防刷新重复（[[rules/lottery_shown_idempotent]]），状态机见 [[processes/first_visitor_lottery_shown]]。

## 版本演进

- 当前观测：DB 11 行全为 `Y`，`N` 仅由代码语义推断。

```ground:enum
field: cust_company_survey_state.first_visitor_lottery_shown
values:
  - value: Y
    stored_as: 字面量 Y
    java_name: (字面量 'Y'，无枚举类)
    label: 首个用户转盘抽奖已展示
    note: "写出点为 markFirstVisitorLotteryShownIfMatch，非 getDictKey 统一字典"
  - value: N
    label: 未展示（初始态）
    note: DB 无 N 样本，N 仅由代码语义推断
```

---END FILE---

---FILE: enums/gpt_learn_poster_log_enable.md ---
---
type: enum
title: 引流埋点逻辑有效标记取值
page_key: gpt_learn_poster_log_enable
domain: 客户管理
status: draft
aliases: [埋点 enable 取值, poster enable Y]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:gpt_learn_poster_log.enable
contract_version: "0.1"
---

[[tables/gpt_learn_poster_log]] 的逻辑有效标记，DB default `'Y'`，无枚举类。

## 需求背景

该标记进入弹出次数统计口径（[[calibers/gpt_learn_poster_log_enabled]]）与点击记录校验。

## 版本演进

- 当前观测：252 行全为 `Y`。
- 语义分析的枚举审计条目在本字段处被截断，取值集合是否还存在其他值无法确认（见 REVIEW）。

```ground:enum
field: gpt_learn_poster_log.enable
values:
  - value: Y
    stored_as: 字面量 Y
    java_name: (DB default 'Y')
    label: 有效记录
    note: 实测 252 行全为 Y，无其他取值样本
```

---END FILE---

---FILE: enums/cust_company_survey_state_db_tenant_code.md ---
---
type: enum
title: 问卷活动状态表租户取值
page_key: cust_company_survey_state_db_tenant_code
domain: 客户管理
status: draft
aliases: [survey_state 租户取值, LN1 异常样本]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_company_survey_state.db_tenant_code
  - code_path:WenjuanController.java:markLotteryShown
contract_version: "0.1"
---

[[tables/cust_company_survey_state]] 的数据租户取值。代码在问卷链路强制 `setDbTenantCode("all")`（[[rules/wenjuan_all_tenant_fallback]]、[[calibers/wenjuan_all_tenant]]），因此 `LN1` 属口径外样本。

## 需求背景

问卷活动数据按全租户统一管理，租户列实际只应出现兜底值 `all`；出现其他值时需人工核实来源。

## 版本演进

- 当前观测：`all`(10) 与 `LN1`(1) 并存，`LN1` 行与代码口径不一致。

```ground:enum
field: cust_company_survey_state.db_tenant_code
values:
  - value: all
    stored_as: 字面量 all
    label: 问卷活动兜底租户（代码强制写入）
    note: 实测 10 行
  - value: LN1
    stored_as: 字面量 LN1
    java_name: (无)
    label: 非活动兜底租户样本
    note: 代码在 Wenjuan 链路强制 setDbTenantCode("all")，该行属口径外历史/异常数据，需人工核实；实测 1 行
```

---END FILE---

---FILE: enums/wenjuan_home_display_scene.md ---
---
type: enum
title: 问卷活动首页展示场景取值
page_key: wenjuan_home_display_scene
domain: 客户管理
status: draft
aliases: [displayScene 取值, 活动场景枚举]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - code_path:WenjuanController.java:markLotteryShown
contract_version: "0.1"
---

`WenjuanHomeDisplayConfigDTO.displayScene` 的取值集合，由 `resolveHomeDisplay` 实时计算，非落库字段。

## 需求背景

三档场景决定首页活动 UI 的组合，状态机与迁移见 [[processes/wenjuan_home_display_scene]]。

## 版本演进

- 该枚举为接口返回语义，DB 中无对应列，无法用数据分布校验。

```ground:enum
field: WenjuanHomeDisplayConfigDTO.displayScene
values:
  - value: NONE
    label: 不展示任何活动UI
    note: 非落库字段，接口返回语义
  - value: FIRST_VISITOR_LOTTERY
    label: 转盘抽奖+中奖弹窗+右下角问卷入口
    note: 非落库字段，接口返回语义
  - value: GUIDE_ONLY
    label: 指引弹窗+右下角问卷入口
    note: 非落库字段，接口返回语义
```

---END FILE---

---REVIEW: table | 物理库名未在语义分析中给出---
全部页面 frontmatter 的 `scope.databases` 暂记为 `unknown`：语义分析只给出 `db_tenant_code` 取值（`all` / `LN1` / `beehive-scf.qhhrly.cn`）与模块名（如 `pplatform-apaas-service`），未给出物理库名。`beehive-scf.qhhrly.cn` 是租户标识而非库名，未据此回填。
---END REVIEW---

---REVIEW: table | 表字段物理类型未知---
语义分析未提供任何字段的物理类型，table 页 `ground:table` 的 `type` 统一写 `unknown`，请在取得 DDL 后回填。
---END REVIEW---

---REVIEW: table | cust_company_survey_state 表结构截断---
术语桥「企业首个访问用户」指出「表结构在该列（respondent）后截断」，当前可见字段为 company_id / respondent / first_visit_time / first_visitor_lottery_shown / db_tenant_code。是否存在独立的 `first_visitor_user_id` 列无法确认，claimFirstVisitor 的判定结果是否另有落点待核实。
---END REVIEW---

---REVIEW: enum | gpt_learn_poster_log.enable 审计条目截断---
枚举审计中 `gpt_learn_poster_log.enable` 条目的 `stored_as` 值被截断（原文止于 "数"），该字段取值集合只保留 `Y`（DB default 'Y'）。是否存在其他取值需重新核对该字段的 DB 分布与代码赋值。
---END REVIEW---

---REVIEW: caliber | cust_company_survey_state.db_tenant_code 样本与代码口径不一致---
代码在 Wenjuan 链路强制 `setDbTenantCode("all")`，DB 实测仍有 1 行 `db_tenant_code=LN1`。该行来源（历史数据、其他链路写入、人工修数）未在证据中说明，需人工核实后再决定是否纳入口径。
---END REVIEW---