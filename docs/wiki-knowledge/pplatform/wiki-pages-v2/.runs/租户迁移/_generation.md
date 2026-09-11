---FILE: tables/tenant_migarory_log.md ---
---
type: table
title: tenant_migarory_log（租户迁移日志表）
page_key: tenant_migarory_log
domain: 租户迁移
status: draft
aliases: [租户迁移日志, 迁移日志表, tenant_migratory_log]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
---

tenant_migarory_log 是租户迁移/同步主链路上的日志表：每一次迁移或同步动作都会在本表留下一条记录，记录本次请求的方向（入向/出向）、操作类型与事件名称、请求编号与流水编码、产品与租户标识、迁移数据载荷、请求/响应报文，以及成功、失败与总量三个计数。它是判断“某个租户/项目/客户迁移是否成功”的第一事实来源，也是 [[migration_tenant_log]]、[[migration_project_log]]、[[migration_cust_log]] 三个口径的承载表。

```ground:table
table: tenant_migarory_log
fields:
  - name: status
    meaning: 迁移状态，N 表示未完成或失败，Y 表示成功
    evidence: db
  - name: direction
    meaning: 数据方向，IN 表示入向，OUT 表示出向
    evidence: db
  - name: name
    meaning: 事件名称，如迁移租户、迁移项目、迁移客户、同步产品等
    evidence: db
  - name: type
    meaning: 操作类型，如 migratoryTenant、migratoryProject、migratoryCust、TENANT_SYNC、PROJECT_SYNC 等
    evidence: db
  - name: req_no
    meaning: 请求编号，唯一标识一次迁移请求
    evidence: db
  - name: req_sn
    meaning: 请求流水编码
    evidence: db
  - name: platform_product_code
    meaning: 产品编码
    evidence: db
  - name: app_tenant_code
    meaning: 逻辑租户标识
    evidence: db
  - name: db_tenant_code
    meaning: 数据租户标识
    evidence: db
  - name: data
    meaning: 迁移数据内容
    evidence: db
  - name: request
    meaning: 请求数据
    evidence: db
  - name: response
    meaning: 返回数据
    evidence: db
  - name: success_number
    meaning: 成功数量
    evidence: db
  - name: falied_number
    meaning: 失败数量
    evidence: db
  - name: total_number
    meaning: 总数量
    evidence: db
```

## 需求背景

本表的字段语义全部来自 DB 值分布证据（evidence: db），没有代码侧证据，因此“type 与 name 双写同一业务含义”的现象需要在口径层显式收口，见 [[migration_tenant_log]] / [[migration_project_log]] / [[migration_cust_log]]。字段拼写 `falied_number` 为库中实际列名，按逐字原则保留，不在本页做纠错推断；`tenant_migarory_log` 的表名拼写同理。

## 版本演进

- v0（草稿）：以 DB 值分布还原 15 个字段的业务含义；status 的 N/Y 语义归入 [[migration_log_success]] 口径，direction 的 IN/OUT 语义仅在本页记录，尚未建立独立口径页。

关联页面：[[migratory_user_record]]、[[migratory_tenant]]、[[migratory_project]]、[[migratory_cust]]。

---END FILE---

---FILE: tables/migratory_user_record.md ---
---
type: table
title: migratory_user_record（迁移用户记录表）
page_key: migratory_user_record
domain: 租户迁移
status: draft
aliases: [迁移用户记录, 存量用户记录表]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
contract_version: "0.1"
---

migratory_user_record 记录“哪些用户是迁移来的存量用户”。它把用户（user_id，关联企业人员）与数据租户（db_tenant_code）绑定，并用 is_login 与 enable 两个标志位驱动登录后的升级提示逻辑。它是 [[existing_user]] 这一术语在数据上的落点，也是 [[migratory_user_login_state]] 状态机与 [[eject_msg_once]] 规则的载体。

```ground:table
table: migratory_user_record
fields:
  - name: user_id
    meaning: 用户ID（关联企业人员）
    evidence: code
  - name: db_tenant_code
    meaning: 数据租户标识
    evidence: code
  - name: is_login
    meaning: 是否已登录，N 未登录，Y 已登录
    evidence: db
  - name: enable
    meaning: 启用标记，Y 有效
    evidence: db
  - name: 记录初始化规则
    meaning: 迁移客户时对保存的人员，若本表不存在该用户在该租户下的记录则创建记录，is_login 初始化为 'N'
    evidence: code_path:PlatFormMigratoryApplication.java:migratoryCust
```

## 需求背景

本表的存在意义是为“迁移用户登录后只弹一次升级消息”提供幂等依据：弹出由 is_login 的 N→Y 翻转来去重，见 [[eject_msg_once]] 与 [[migratory_user_not_login]]。user_id 与 db_tenant_code 的语义来自代码证据，说明本表由迁移客户流程（`PlatFormMigratoryApplication.java:migratoryCust`）写入，而非独立维护的配置表。

## 版本演进

- v0（草稿）：字段语义来自 db（is_login / enable）与 code（user_id / db_tenant_code）两类证据；记录初始化行为不在本页展开，归入 [[migratory_user_record_init]]。

关联页面：[[migratory_user_login_state]]、[[existing_user]]、[[eject_msg_once]]。

---END FILE---

---FILE: processes/migratory_user_login_state.md ---
---
type: process
title: 迁移用户登录状态（is_login N→Y）
page_key: migratory_user_login_state
domain: 租户迁移
status: draft
aliases: [迁移用户登录状态机, is_login 状态流转]
oid: 1
scope:
  databases: [未提供]
sources:
  - db_dist
  - code_path:CustMigratoryService.java:loginAfterEjectMsg
contract_version: "0.1"
---

本页描述迁移用户的登录状态流转：迁移用户在 [[migratory_user_record]] 中以 `is_login` 标记是否已经过“登录后弹出升级消息”这一动作。状态只有两个取值，迁移客户时记录被初始化为未登录，用户登录并触发弹出接口后翻转为已登录，从而在数据层面实现“仅弹一次”。

```ground:process
name: 迁移用户登录状态
field: migratory_user_record.is_login
states:
  - value: "N"
    label: 未登录
    source: db_dist
  - value: "Y"
    label: 已登录
    source: db_dist
transitions:
  - from: "N"
    event: 用户登录后调用 /cust-web/migratory/isEjectMsg
    to: "Y"
    evidence: "code_path:CustMigratoryService.java:loginAfterEjectMsg"
```

## 需求背景

流转的入口条件是“未登录且有效”的迁移用户，判定口径见 [[migratory_user_not_login]]；翻转动作对应的业务规则（弹出一次升级消息）见 [[eject_msg_once]]。需求文档《产融平台数据迁移涉及的改造需求V1.2》中的锚定主张——“登录后弹出提示‘【贴牌名称】平台已升级，新增【产品中心】……’（通过公告配置实现即可，一个用户仅弹出一次即可）”——与代码证据 `CustMigratoryService.java:loginAfterEjectMsg` 指向同一动作，该主张的双源证据落在 [[eject_msg_once]] 页。

## 版本演进

- v0（草稿）：状态与迁移边来自 db_dist 值分布与 `CustMigratoryService.java:loginAfterEjectMsg`；仅覆盖 N→Y 单向流转，未观察到 Y→N 的回退路径。

关联页面：[[migratory_user_record]]、[[existing_user]]、[[migratory_user_record_init]]。

---END FILE---

---FILE: calibers/migratory_user_not_login.md ---
---
type: caliber
title: 未登录的迁移用户
page_key: migratory_user_not_login
domain: 租户迁移
status: draft
aliases: [未登录迁移用户口径, 待弹窗迁移用户]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:CustMigratoryService.java:loginAfterEjectMsg
contract_version: "0.1"
---

“未登录的迁移用户”是登录后弹出升级消息这一动作的判定集合：只有同时满足“迁移记录标记为未登录”和“记录有效”的用户才会被纳入。

```ground:caliber
name: 未登录的迁移用户
predicate: "migratory_user_record.is_login = 'N' AND migratory_user_record.enable = 'Y'"
scope: 迁移用户登录弹出消息判断
evidence: "code:CustMigratoryService.loginAfterEjectMsg"
```

## 需求背景

该口径服务于用户触达类需求，落地为 [[eject_msg_once]] 规则的前置条件，并与 [[migratory_user_login_state]] 的 N 态一一对应。语料中未出现与该口径同名的其他写法，暂不设置消歧条目。

## 版本演进

- v0（草稿）：口径由代码证据（`CustMigratoryService.loginAfterEjectMsg`）直接给出，尚无数据侧统计量。

关联页面：[[migratory_user_record]]、[[processes/migratory_user_login_state]]、[[eject_msg_once]]。

---END FILE---

---FILE: calibers/migration_log_success.md ---
---
type: caliber
title: 迁移日志成功
page_key: migration_log_success
domain: 租户迁移
status: draft
aliases: [迁移成功口径, status=Y]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
---

“迁移日志成功”把 [[tenant_migarory_log]] 的 status 取值收敛为可统计的成功集合，是迁移成功率、失败排查类指标的基数来源。

```ground:caliber
name: 迁移日志成功
predicate: "tenant_migarory_log.status = 'Y'"
scope: 迁移操作结果统计
evidence: "db:值分布"
```

## 需求背景

status 为单字符标志位，N 同时覆盖“未完成”与“失败”两种情形，因此“非成功”不等于“失败”，统计失败量时应显式排除未完成态——此边界目前只能依赖值分布观察，未在代码中找到状态写入分支，属待确认事项。

## 版本演进

- v0（草稿）：口径来自 db 值分布；未与 success_number / falied_number / total_number 三个计数列做交叉校验。

关联页面：[[tenant_migarory_log]]、[[migration_tenant_log]]、[[migration_project_log]]、[[migration_cust_log]]。

---END FILE---

---FILE: calibers/migration_tenant_log.md ---
---
type: caliber
title: 迁移租户类型日志
page_key: migration_tenant_log
domain: 租户迁移
status: draft
aliases: [租户迁移日志口径, migratoryTenant 日志]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
---

租户迁移监控的最小集合：在 [[tenant_migarory_log]] 中，租户迁移既可能以操作类型 `migratoryTenant` 记录，也可能以事件名称“迁移租户”记录，因此口径必须双字段取并。

```ground:caliber
name: 迁移租户类型日志
predicate: "tenant_migarory_log.type = 'migratoryTenant' OR tenant_migarory_log.name = '迁移租户'"
scope: 租户迁移监控
evidence: "db:值分布"
```

## 需求背景

type 与 name 的双写是历史脏数据形态而非两种业务，术语层面的等价关系记录在 [[migratory_tenant]]。漏用 OR 条件会导致迁移租户量被系统性低估。

## 版本演进

- v0（草稿）：口径来自 db 值分布，未确认是否所有租户迁移记录都同时写满 type 与 name。

关联页面：[[tenant_migarory_log]]、[[migratory_tenant]]、[[migration_log_success]]。

---END FILE---

---FILE: calibers/migration_project_log.md ---
---
type: caliber
title: 迁移项目类型日志
page_key: migration_project_log
domain: 租户迁移
status: draft
aliases: [项目迁移日志口径, migratoryProject 日志]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
---

项目迁移监控的取数口径：在 [[tenant_migarory_log]] 中同时接受操作类型 `migratoryProject` 与事件名称“迁移项目”。

```ground:caliber
name: 迁移项目类型日志
predicate: "tenant_migarory_log.type = 'migratoryProject' OR tenant_migarory_log.name = '迁移项目'"
scope: 项目迁移监控
evidence: "db:值分布"
```

## 需求背景

与租户迁移口径同构，术语等价关系见 [[migratory_project]]。需求文档中另有关于“定制项目标识/租户与定制项目映射表”的主张，目前无代码证据，不在本口径内展开，见 [[migratory_project]] 的版本演进说明。

## 版本演进

- v0（草稿）：口径来自 db 值分布；未区分项目迁移与项目同步（`PROJECT_SYNC`）。

关联页面：[[tenant_migarory_log]]、[[migratory_project]]、[[migration_log_success]]。

---END FILE---

---FILE: calibers/migration_cust_log.md ---
---
type: caliber
title: 迁移客户类型日志
page_key: migration_cust_log
domain: 租户迁移
status: draft
aliases: [客户迁移日志口径, migratoryCust 日志]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
---

客户迁移监控的取数口径：在 [[tenant_migarory_log]] 中同时接受操作类型 `migratoryCust` 与事件名称“迁移客户”。

```ground:caliber
name: 迁移客户类型日志
predicate: "tenant_migarory_log.type = 'migratoryCust' OR tenant_migarory_log.name = '迁移客户'"
scope: 客户迁移监控
evidence: "db:值分布"
```

## 需求背景

本口径是 [[existing_user]]（存量用户）形成过程的观测入口：客户迁移动作同时会初始化 [[migratory_user_record]]，相关规则见 [[migratory_user_record_init]] 与 [[ams_company_merge]]。术语等价关系见 [[migratory_cust]]。

## 版本演进

- v0（草稿）：口径来自 db 值分布；与客户合并迁移（AMS 分支）的记录形态是否一致尚未验证。

关联页面：[[tenant_migarory_log]]、[[migratory_cust]]、[[ams_company_merge]]。

---END FILE---

---FILE: concepts/migratory_tenant.md ---
---
type: concept
title: 迁移租户
page_key: migratory_tenant
domain: 租户迁移
status: draft
aliases: [migratoryTenant]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
maps_to: "tenant_migarory_log.type = 'migratoryTenant' 或 name = '迁移租户'"
field_targets:
  - tenant_migarory_log.type
  - tenant_migarory_log.name
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
---

“迁移租户”是业务侧对租户级迁移动作的称呼，代码与库中以类型码 `migratoryTenant` 出现，二者为同义关系（adjudication: synonym），在 [[tenant_migarory_log]] 上分别落在 type 与 name 两个字段。取数时不要只匹配其一，口径见 [[migration_tenant_log]]。

## 需求背景

该术语的判定完全依赖 DB 值分布证据（db），未在代码中找到枚举常量定义；因此本页不给出枚举页，字段取值以值分布为准。

## 版本演进

- v0（草稿）：synonym 判定成立，别名集合仅 `migratoryTenant`。

关联页面：[[tenant_migarory_log]]、[[migration_tenant_log]]、[[migratory_project]]、[[migratory_cust]]。

---END FILE---

---FILE: concepts/migratory_project.md ---
---
type: concept
title: 迁移项目
page_key: migratory_project
domain: 租户迁移
status: draft
aliases: [migratoryProject]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
maps_to: "tenant_migarory_log.type = 'migratoryProject' 或 name = '迁移项目'"
field_targets:
  - tenant_migarory_log.type
  - tenant_migarory_log.name
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
---

“迁移项目”是业务侧对项目级迁移动作的称呼，库中以类型码 `migratoryProject` 出现，二者同义（adjudication: synonym），在 [[tenant_migarory_log]] 上分列 type 与 name，取数口径见 [[migration_project_log]]。

## 需求背景

术语映射来自 DB 值分布；注意与项目**同步**（`PROJECT_SYNC`）区分：同步是数据方向上的动作，不改变本术语的迁移语义。

## 版本演进

- v0（草稿）：synonym 判定成立。
- (document_claim，未证实) 需求文档《产融平台数据迁移涉及的改造需求V1.2》提及“产融新建租户和定制项目映射表；新增项目时选择产品后需选择定制项目标识；租户迁移接口需调整，自营租户存储映射关系；项目迁移存储定制项目标志；项目同步接口添加项目标志；运营方多项目测试数据的打标处理”。该主张在语义分析中标记为 uncovered（无代码证据），本页仅作记录，不产生锚点，也不改变现有 `migratoryProject` 映射。

关联页面：[[tenant_migarory_log]]、[[migration_project_log]]、[[migratory_tenant]]。

---END FILE---

---FILE: concepts/migratory_cust.md ---
---
type: concept
title: 迁移客户
page_key: migratory_cust
domain: 租户迁移
status: draft
aliases: [migratoryCust]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
maps_to: "tenant_migarory_log.type = 'migratoryCust' 或 name = '迁移客户'"
field_targets:
  - tenant_migarory_log.type
  - tenant_migarory_log.name
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
---

“迁移客户”是业务侧对客户（企业）级迁移动作的称呼，库中以类型码 `migratoryCust` 出现，二者同义（adjudication: synonym），取数口径见 [[migration_cust_log]]。该术语同时对应代码入口 `PlatFormMigratoryApplication.java:migratoryCust`，是同一动作在库与代码两侧的命名。

## 需求背景

客户迁移不仅写 [[tenant_migarory_log]]，还会初始化 [[migratory_user_record]] 并处理企业已存在时的合并分支，相关规则见 [[migratory_user_record_init]]、[[ams_company_merge]]、[[company_sync_lock]]。

## 版本演进

- v0（草稿）：DB 侧 synonym 判定成立；代码侧入口为 `PlatFormMigratoryApplication.java:migratoryCust`。

关联页面：[[tenant_migarory_log]]、[[migration_cust_log]]、[[existing_user]]。

---END FILE---

---FILE: concepts/fake_oem.md ---
---
type: concept
title: 假贴牌
page_key: fake_oem
domain: 租户迁移
status: draft
aliases: []
oid: 1
scope:
  databases: [未提供]
sources:
  - db
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
maps_to: "无直接代码/DB对应，需求文档提及"
adjudication: boundary
also_confused_with: [自营贴牌]
contract_version: "0.1"
---

(document_claim，未证实)

“假贴牌”出现在需求语料中，但语义分析明确标注为 boundary 判定：无直接代码/DB 对应。它与“自营贴牌”的边界是——假贴牌是自营下的二级贴牌，数据未隔离；代码中未找到“租户配置表单不可见”等实现。因此本页只承载术语边界，不承载任何字段锚点。

## 需求背景

(document_claim，未证实) 需求文档《产融平台数据迁移涉及的改造需求V1.2》主张：假贴牌迁移至产融平台后，在“租户配置”表单内不可见（仅存在于后台），作为自营贴牌的二级贴牌，内管端可正常创建该二级贴牌下的项目。该主张在语义分析中为 uncovered（无代码证据），仅作记录。

## 版本演进

- v0（草稿）：仅登记边界关系与别称缺失（aliases 为空）；一旦出现代码/库证据，应升级为带锚点的术语页或独立口径页。

关联页面：[[migratory_cust]]、[[migratory_tenant]]、[[tenant_migarory_log]]。

---END FILE---

---FILE: concepts/existing_user.md ---
---
type: concept
title: 存量用户
page_key: existing_user
domain: 租户迁移
status: draft
aliases: [迁移用户]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
maps_to: "migratory_user_record 中记录的用户"
field_targets:
  - migratory_user_record.user_id
  - migratory_user_record.db_tenant_code
  - migratory_user_record.is_login
adjudication: boundary
also_confused_with: [新用户]
contract_version: "0.1"
---

“存量用户”指迁移动作发生前已存在的用户，其判定在数据上是“在 [[migratory_user_record]] 中存在（user_id + db_tenant_code）记录”。与新用户的边界是：新用户没有该记录，因此不会被登录弹窗逻辑覆盖（见 [[migratory_user_not_login]]、[[eject_msg_once]]）。别称“迁移用户”在语料中与存量用户混用，按 boundary 处理：两者在本主题下同指。

## 需求背景

(document_claim 锚定，双源) 需求文档《产融平台数据迁移涉及的改造需求V1.2》主张：存量用户点击【登录】，输入用户、密码/短信验证码后可登录成功，进入到产融平台内页可以看到企业状态为“已认证”，产品中心处至少已经开通了一个产品。该主张 code_status=confirmed，双源证据为 `code_path:PlatFormMigratoryApplication.java:migratoryCust + reqdoc:产融平台数据迁移涉及的改造需求V1.2`——代码在迁移客户时自动开通产品（autoActiveProduct）并设置企业状态，与需求一致。本页为 concept 页，不作锚点块，双源证据登记于上方 frontmatter sources。

## 版本演进

- v0（草稿）：boundary 判定成立，别称“迁移用户”与 [[migratory_user_record]] 记录一一对应。
- (document_claim，未证实) 需求文档另提及“注册/登录入口统一到产融平台”，语义分析标记为 uncovered（无代码证据），仅作记录，不影响本页映射。

关联页面：[[migratory_user_record]]、[[migratory_user_login_state]]、[[eject_msg_once]]、[[migratory_cust]]。

---END FILE---

---FILE: rules/eject_msg_once.md ---
---
type: rule
title: 迁移用户登录后仅弹出一次升级消息
page_key: eject_msg_once
domain: 租户迁移
status: draft
aliases: [升级消息仅弹一次, isEjectMsg 规则]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:CustMigratoryService.java:loginAfterEjectMsg
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
contract_version: "0.1"
---

本规则决定存量用户登录时的触达行为：命中“未登录的迁移用户”后返回弹出标志，并立刻把登录状态置为已登录，从而保证一个用户只被弹一次。

```ground:rule
name: 迁移用户登录后仅弹出一次升级消息
content: 迁移用户（存在于 migratory_user_record 且 is_login='N'）登录后，调用 /cust-web/migratory/isEjectMsg 接口，返回弹出标志，并将 is_login 更新为 'Y'，确保仅弹出一次。
impact: 用户触达
field_targets:
  - migratory_user_record.is_login
evidence: "code_path:CustMigratoryService.java:loginAfterEjectMsg + reqdoc:产融平台数据迁移涉及的改造需求V1.2"
```

## 需求背景

需求文档《产融平台数据迁移涉及的改造需求V1.2》的锚定主张为：登录后弹出提示“【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务。”（通过公告配置实现即可，一个用户仅弹出一次即可）。该主张 code_status=confirmed，与代码证据 `CustMigratoryService.java:loginAfterEjectMsg` 指向同一动作，故按双源写入锚点块。前置集合定义见 [[migratory_user_not_login]]，状态流转见 [[migratory_user_login_state]]。

## 版本演进

- v0（草稿）：规则以代码加需求文档双源固定；提示文案的具体渲染归公告配置，不在本规则内建模。

关联页面：[[migratory_user_record]]、[[migratory_user_login_state]]、[[existing_user]]。

---END FILE---

---FILE: rules/company_sync_lock.md ---
---
type: rule
title: 迁移企业防重复同步锁
page_key: company_sync_lock
domain: 租户迁移
status: draft
aliases: [企业重复同步锁, dbTenantCode+companyName+socialUnifiedCode 锁]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
contract_version: "0.1"
---

本规则用于挡住同一次企业信息的重复同步：以数据租户编码、企业名称、统一社会信用代码三者拼接作为锁标识，取锁失败即判定为重复同步并抛错，从而保证企业迁移的幂等性。

```ground:rule
name: 迁移企业防重复同步锁
content: 迁移企业信息时，使用 Redis 锁，锁 key 由 dbTenantCode + companyName + socialUnifiedCode 拼接，若获取锁失败则抛出重复同步异常。
impact: 数据一致性
field_targets:
  - redis:lockName
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust"
```

## 需求背景

该规则是 [[ams_company_merge]] 的前置保护：并发的企业迁移请求会在锁层被拒绝，避免同一企业在合并分支上被并发改写。锁粒度由业务三要素决定，而非请求编号，说明设计意图是“企业维度”去重。

## 版本演进

- v0（草稿）：规则来自代码证据 `PlatFormMigratoryApplication.java:migratoryCust`；锁过期与释放策略未在证据中体现，待确认。

关联页面：[[ams_company_merge]]、[[migratory_cust]]、[[migration_cust_log]]。

---END FILE---

---FILE: rules/ams_company_merge.md ---
---
type: rule
title: AMS 企业合并迁移
page_key: ams_company_merge
domain: 租户迁移
status: draft
aliases: [AMS 企业已存在合并, 企业合并迁移规则]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
contract_version: "0.1"
---

当迁移过来的企业在目标侧已存在时，不能简单新建，而要走合并分支：在产品为 AMS 的前提下，补齐新增的管理员、操作员与角色，并处理协议与影像件迁移。

```ground:rule
name: AMS 企业合并迁移
content: 当产品为 AMS 且企业已存在时，执行合并逻辑：补充新增的管理员、操作员、角色，并处理协议和影像迁移。
impact: 企业数据合并
field_targets:
  - cust_company_info
  - cust_person_info
  - cust_role_info
  - cust_project_rel
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust"
```

## 需求背景

需求文档《产融平台数据迁移涉及的改造需求V1.2》提出了更激进的合并策略：先导出存在多条建档数据的企业，通过 RPA 抓取最新的企业关键字段，对比定位建档数据中最准确的一条；若关键字段都一致，则取建档时间最晚/变更时间最晚的一条，影像件也随之取对应的一套。语义分析将该主张标记为 prose_only，差异为：代码中对于 AMS 产品且企业已存在时确有合并逻辑（补充管理员、操作员、角色等），但未实现“RPA 抓取最新字段并对比选择最准确一条”的策略。**合并规则以代码为准**，需求描述仅作背景；该差异不写入锚点块。

## 版本演进

- v0（草稿）：以代码证据固定合并规则的实现范围；需求侧 RPA 择优策略未覆盖，待产品与研发确认是否演进。

关联页面：[[company_sync_lock]]、[[migratory_cust]]、[[migratory_user_record_init]]。

---END FILE---

---FILE: rules/migratory_user_record_init.md ---
---
type: rule
title: 迁移人员记录初始化
page_key: migratory_user_record_init
domain: 租户迁移
status: draft
aliases: [迁移用户记录初始化, migratory_user_record 建档]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
contract_version: "0.1"
---

本规则保证每一位被迁移过来的人员都有一条可追踪的迁移用户记录，且初始状态一定是“未登录”，为后续登录弹窗的一次性判断提供入口。

```ground:rule
name: 迁移人员记录初始化
content: 迁移客户时，对保存的人员，若 migratory_user_record 中不存在该用户在该租户下的记录，则创建记录，is_login 初始化为 'N'。
impact: 迁移用户跟踪
field_targets:
  - migratory_user_record
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust"
```

## 需求背景

初始化动作与 [[eject_msg_once]]、[[migratory_user_not_login]] 构成完整链路：迁移时建档（N）→ 登录时命中口径 → 弹出并翻转为 Y → 不再弹。去重键为“用户 + 租户”，与 [[migratory_user_record]] 的 user_id、db_tenant_code 字段对应。

## 版本演进

- v0（草稿）：规则来自代码证据；同一用户跨租户迁移时会各建一条记录，此行为符合当前映射，未观察到跨租户去重。

关联页面：[[migratory_user_record]]、[[existing_user]]、[[migratory_user_login_state]]、[[ams_company_merge]]。

---END FILE---

---REVIEW: table | tenant_migarory_log---
语义分析只给出 `evidence: db` / `evidence: code` 级别的来源标记，未提供**物理库名**，因此本批所有页面的 `scope.databases` 只能填占位值 `未提供`。需补充：tenant_migarory_log 与 migratory_user_record 所在的物理库名（是否同库、是否分库）。在此之前，跨库口径（如 migration_log_success 与 migratory_user_not_login 的联合使用）不得视为同库可 JOIN。
---END REVIEW---

---REVIEW: concept | 假贴牌---
“假贴牌 / 自营贴牌”仅有 boundary 判定，需求主张为 uncovered（无代码证据），且 aliases 为空。需确认：该术语是否仍属「租户迁移」主题（若属租户配置域，应迁出本主题）；以及是否需要在代码或库侧新增可锚定的标识（如贴牌层级字段）以便从 concept 升级为可验证口径。
---END REVIEW---