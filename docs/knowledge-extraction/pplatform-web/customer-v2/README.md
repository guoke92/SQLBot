# pplatform-web 客户中心 2.0 知识单元包

样本仓：`/Users/fanjunwei/IdeaProjects/pplatform-web`  
分支 / 提交：`dev-v1.33.0` / `ee434954e`  
提取日期：2026-08-17  
导入形态：仅 `knowledge-package.yaml`（KnowledgePackage 2.0）。不升格 `enterprise-onboarding-v1` / `system-knowledge-v3` 的 1.0 items。

权威顺序：**库字段实际值 > 当前代码 > 业务文档 > skill**。文档与 skill 只做场景导航，不单独认证口径。

---

## 第一遍：场景索引（不写单元）

来源：`.cursor/skills/*`、`.dev-standards/knowledge/business/*.md`。本遍只建目录，不把规范原文写进 `domain_rules`。

| 业务域 | 候选场景 | 问数适用性 | 本包处理 |
|---|---|---|---|
| 客户管理 | 企业建档（提交→推运营→回调→主数据生效） | 高：企业数、建档进度、有效企业 | **已闭环为单元** `enterprise-onboarding` |
| 客户管理 | 企业变更（CUST_CHANGE / CHANGE） | 中：与“有效企业”口径冲突 | 只在建档单元标冲突，不单独成包 |
| 客户管理 | 邀请 / 自主 / 简易 / AGW 认证分流 | 中：影响流程与首次提交时间 | 吸收进建档单元的 `identify_style` |
| 客户管理 | 用户邀请与管理员 | 中：人员表双引用路径 | 未提取 |
| 产品与项目 | 租户项目生命周期（创建→配置→生效） | 高：已生效项目 | **已闭环为单元** `project-enterprise-rel` 的项目侧 |
| 产品与项目 | 企业关联项目（角色+产品+项目） | 高：项目成员企业、开通状态 | **已闭环为单元** `project-enterprise-rel` |
| 租户管理 | 租户 / 租户产品 | 中：跨租户金融机构例外 | 仅作为关联校验背景，未单独成单元 |
| 运营中台对接 | OperCustFacade 推数与回调 | 导航，不是口径 | 证据，不进规则 |
| 协议 / CA / OpenAPI | 签章、授权、渠道建档 | 低（本轮） | 未提取 |
| 平台规范 / 前后端边界 | 开发约束 | 无问数价值 | **不进包** |

既有 1.0 材料只吸收事实，不兼容导入：

- `enterprise-onboarding-v1/`：建档穿透最完整，事实已按当前 DO/Mapper 复核
- `system-knowledge-v3/`：拆成术语/口径/关系，无法还原场景，故重写为单元

---

## 第二遍：代码闭环

| 单元 | 入口 | 写路径 | 表 |
|---|---|---|---|
| 企业建档 | `POST /cust-web/custInfo/submitCust`、`/checkBuild` | `CustCompanyInfoApplication` → `OperCustFacade` → `RegAsyncService` → `CustSyncEventProcessor` | `cust_company_info`、`cust_build_record` |
| 项目关联 | `POST /cust-web/custInfo/relateProject` | `CustCompanyInfoApplication#relateProject` | `cust_project_rel`、`tenant_project`，经 `cust_company_info.code` 拼接 |

主链（代码，不是文档流程图）：

```text
提交/检查建档
  → 向运营推送成功后 check_status = CUST_CHECK_INIT   （不是建档成功）
  → 事务后异步：推影像 / 启流程 / 写 cust_build_record
  → 运营回调 check_status
        BACKTOCUSTOM → cust_build_status = CUST_CONFIRM_AWAIT
        INIT / CHECKING → CUST_BUILDING
        REJECT + 建档流程 CHECK → BUILD_FAIL
        REJECT + 变更流程 CHANGE → 仍保持 BUILD_SUCCESS
        PASS → BUILD_SUCCESS，并 effectCust 写 cust_status = EFFECT
```

文档写的 `POST /app-web/custCompanyInfo/relateProject` 与代码不符；问数以 Controller 映射为准。

---

## 单元与问数边界

| unit_id | 适用 | 不要用来回答 |
|---|---|---|
| `enterprise-onboarding` | 有效已建档企业、建档中/失败、推送过程 | 项目成员清点、开通产品数 |
| `project-enterprise-rel` | 企业加入了哪些项目、某项目下企业、开通状态 | 建档成功企业总数（应用建档口径去重，不要数关系行） |

两单元靠共享表名 / 字段名拼接，不另建单元图。

---

## 冲突与假设

1. **建档成功时间**：没有统一“审核通过时间”字段。`create_time` 是行创建时间；`cust_first_submit_auth` 仅 SELF/INVITE 且原值为空时写入。问数不得用 `create_time` 顶替建档成功日。
2. **“有效企业”有两套 Mapper 口径**：严格已建档是 `BUILD_SUCCESS + EFFECT`；`listEffectCompanyByCustType` 还包含 `CUST_CHANGE + CHANGE`。用户未说明“含变更中”时用严格口径，冲突时澄清。
3. **枚举展示名**：`BUILD_SUCCESS` 字典展示是「认证成功」，业务口语常说「建档成功」。值以库字段为准。
4. **简易建档**：`SIMPLE` 且不走工作流时，本地直接写 `BUILD_SUCCESS + EFFECT`，不经运营 PASS 回调。
5. **关系未做库画像**：`cust_id` / `code` 关联均为 `proposed`。`cust_project_rel.project_id` 存的是 `tenant_project.id` 的字符串，JOIN 需显式转换。
6. **主数据过滤**：`data_type='1'`（`CustDataTypeConstant.DATA_TYPE_MAIN`）且 `enable='Y'` 视为正式企业行；未连库复核空值率。

---

## 未提取（有意）

- 一张表一个单元
- 人员 / 角色 / 认证检查 / CA / 协议全流程
- 1.0 items 兼容导入
- 把 skill 或开发规范写成 `domain_rules`
- 未在目标库执行的查询（`verified_query_patterns` 仅为 proposed 范例，绑定后才验证）
