# pplatform-web 系统业务数据知识包 v4

样本仓：`/Users/fanjunwei/IdeaProjects/pplatform-web`  
分支 / 提交：`dev-v1.33.0` / `ee434954e`  
提取日期：2026-08-18  
唯一导入物：`knowledge-package.yaml`（KnowledgePackage 2.0）

权威顺序：**库字段实际值 > 当前代码 > 业务文档 > skill**。  
建档与项目关联两单元吸收自 `customer-v2/`，口径不重写。其余单元按 Controller → DO/枚举 → 只读画像闭环。

画像库：数据源「产融1」`lowcode_pplatform`（2026-08-18 只读 COUNT/GROUP BY）。关系一律 `proposed`。查询范例未在目标库逐条执行。

---

## 第一遍：场景目录

| 业务域 | 候选场景 | 问数适用性 | 本包 |
|---|---|---|---|
| 客户管理 | 企业建档（提交→推运营→回调→主数据生效） | 高 | 单元 `enterprise-onboarding`（吸收 v2） |
| 客户管理 | 企业变更（CUST_CHANGE / CHANGE） | 高 | 单元 `enterprise-change` |
| 客户管理 | 企业用户 / 管理员 | 高 | 单元 `person-user` |
| 客户管理 | 集团成员 | 中 | 单元 `company-group` |
| 客户管理 | 邀请记录 | 中 | 不成独立 grain；人员问数以 `person-user` 为准 |
| 产品与项目 | 企业按角色关联租户项目 | 高 | 单元 `project-enterprise-rel`（吸收 v2） |
| 产品与项目 | 租户产品开通 | 高 | 单元 `tenant-product-lifecycle` |
| 产品与项目 | 租户项目生效/失效 | 高 | 单元 `tenant-project-lifecycle` |
| 产品与项目 | 企业产品开通申请 | 中 | 单元 `company-product-auth` |
| 租户管理 | 租户配置开关 | 中 | 单元 `tenant-setting` |
| 运营配置 | 运营对接人 / 离职置顶 | 高 | 单元 `op-user-coverage`（画像 141 行，不再空表） |
| 资金方规则 | 产品规则版本生效 | 中 | 单元 `funding-rule` |
| CA 服务费 | 企业缴费与订单 | 中 | 单元 `ca-fee` |
| 协议 | 企业授权协议签署 | 中 | 并入 `company-product-auth` |
| OpenAPI | 渠道密钥与同步失败 | 中 | 单元 `openapi-access` |
| 清分 / 交e保额度 | 会员登记簿、循环额度 | 外部无本地表 | **不成单元** |
| 工作流引擎 | 待办/节点内部表 | 低 | **不成单元**（审批结果落业务表） |
| SSO / Job / 影像 / 低代码 / 加解密 | 工程能力 | 无 | **不成单元** |
| 菜单 / 短链 / 迁移日志 / 问卷过程 | 工具或运维 | 低 | **不成单元** |

跨单元靠共享表名拼接，不建单元关系图。召回上限仍是 2 个 ACTIVE。

本包 `knowledge-package.yaml` 共 13 个单元：吸收 2 个（`enterprise-onboarding`、`project-enterprise-rel`），新闭环 11 个。查询范例均为 `PENDING_VALIDATION`。

---

## 画像摘要（2026-08-18）

- `cust_company_info` 94074：`BUILD_SUCCESS` 49294，`INIT` 23371，`CUST_CHANGE` 631；`cust_status` `EFFECT` 49279 / `CHANGE` 641；`enable+data_type` 以 `Y`+`1` 为主（94023）。
- `cust_change_record` 5172：`CUST_CHECK_PASS` 2979，`CHECKING` 632，`REJECT` 1014；另有脏值 `1`、`returnCust-*`。
- `tenant_product` 494：`open_status` `Y` 394 / `P` 28 / `N` 72（不是 OPENED）。
- `tenant_project` 3373：`project_status` `0` 1400 / `1` 1964 / `2` 9；`top_flag='1'` 仅 12。
- `operation_user` 141：`deleted=N,enable=Y` 119；已删除 22。
- `cust_project_rel` 58645：角色以 SUPPLIER 为主；`top_flag='1'` 404；开通字段是 `project_open_status`。
- `cust_person_info` 60250：`ADD` 约 3.3 万、`EFFECT` 约 2.6 万。
- `cust_user_rel` **仅 1 行**，人员问数以 `cust_person_info` / `cust_role_info` 为准。
- `cust_auth_application.open_status` 库值为 `OPENED`/`OPENING`/`NOT_OPENED`（不是租户产品的 Y/P/N）。
- `funding_rule_info` 46：`ACTIVE` 16 / `PENDING` 25 / `INACTIVE` 5。
- `ca_fee_company` 882：`UNPAID` 826；`ca_fee_order` 含脏值 `PAIDING`。
- `client_api_sync_error` 2161 行全部 `enable=N`（已放弃重试）。
- 清分/bocom/limit：apaas 无 `@TableName`。

---

## 单元与问数边界

| unit_id | 用来回答 | 不要用来回答 |
|---|---|---|
| `enterprise-onboarding` | 有效已建档企业、建档进度 | 项目成员数、开通产品数 |
| `enterprise-change` | 变更中/通过/驳回的变更单 | 把变更拒绝计成建档失败 |
| `project-enterprise-rel` | 企业加入了哪些项目 | 建档成功企业总数 |
| `tenant-product-lifecycle` | 租户已开通产品数 | 企业侧 OPENED 申请 |
| `tenant-project-lifecycle` | 已生效/待生效项目 | 资金规则 PENDING/ACTIVE |
| `op-user-coverage` | 在职运营人员、置顶项目 | 把 top_flag 解释成离职风险分数 |
| `person-user` | 已激活联系人/管理员 | 用 1 行的 `cust_user_rel` 当事实表 |
| `company-group` | 已生效集团成员 | 把未生效成员算进集团企业数 |
| `tenant-setting` | 已生效租户配置 | SSO/DBAss 是否初始化 |
| `funding-rule` | 生效中的资金规则版本 | 项目 `project_status` |
| `ca-fee` | 未缴/已缴 CA 费企业与订单 | 交e保外部账户余额 |
| `company-product-auth` | 授权协议是否已认证、企业产品开通申请 | 租户产品 `open_status=Y` |
| `openapi-access` | 有效渠道密钥；同步失败历史 | 把 enable=N 的失败行当待重试 |

---

## 冲突与假设（包级）

1. **有效企业两套口径**：严格 `BUILD_SUCCESS+EFFECT`；部分 Mapper 含 `CUST_CHANGE+CHANGE`。未说明时用严格口径。
2. **建档成功时间**：无统一审核通过时间；不得用 `create_time`。
3. **`rule_status` 不是项目状态**：项目用 `tenant_project.project_status` 的 `0/1/2`；`PENDING/ACTIVE/INACTIVE` 属于 `funding_rule_info`。
4. **两套开通字典**：租户产品 `Y/P/N`；`cust_auth_application` 库值为 `OPENED/OPENING/NOT_OPENED`。
5. **变更单脏状态**：`cust_change_record.status` 存在 `1` 与 `returnCust-*`，问数只认 `CUST_CHECK_*`。
6. **`cust_project_rel.project_id`** 存 `tenant_project.id` 的字符串，JOIN 需 CAST。

未提取范围、低置信度关系见 `review-questions.md`。
