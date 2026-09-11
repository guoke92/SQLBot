# Pplatform Wiki v2 vs v1 横向对比

> 日期：2026-09-10  
> 提取规范：[`docs/wiki-knowledge/Wiki知识提取规范指南-v1.md`](../Wiki知识提取规范指南-v1.md)  
> 源码钉死：`pplatform-web@ee434954e465713176e5bd52119eedde5ebe531b`  
> 库：`lowcode_pplatform`（E2 当日刷新：78 表 / 933 列画像）  
> **切流状态：未切换。** 运行时仍应指向旧 `wiki-pages/`，待本报告裁决后再动。

独立重提过程**未读取**旧问数 wiki 正文。本文件是第一次打开旧树做差集。

---

## 1. 执行摘要

| 项 | v1（旧） | v2（本轮独立重提） |
|---|---|---|
| 页面总数 | 566 | 678（draft） |
| table | 75 | **86**（对齐当日 DB 78 张业务表 + 若干跨库/代码可见表页） |
| enum | 34 | 32（基线绑定；`product_type`/`user_type` 未再单独成页） |
| concept | 112 | 128 |
| process | 37 | 65 |
| caliber | 118 | 187 |
| rule | 190 | 180 |
| lint 硬错误 | （旧树已 publish 过） | **72**（阻断切流） |
| 断链 `BROKEN_LINK` | — | 2388（软，多为生成期互指未落页） |
| REVIEW 文件 | 历史 `.runs` | 82 项待处置 |
| 计划单元 | 历史 29 域目录 | Step A **26** 单元，25 单元有语义页；`DBAss/SSO登录与通道` 整批拒写 |

**最伤规划器、且 v2 已纠正的真值**

- `cust_build_type`：`PC_BUILD=客户录入`，`AGW_BUILD=平台录入`（枚举页来自常量注释）。v2 concept `build_type` 散文写成「客户端录入」，与枚举页略不一致 → `CMP-BUILD-TYPE-01`。
- 认证状态簇在 v2 显式 `boundary`：`auth_status` → `cust_build_status`，并与客户状态/审核状态拆开。
- 企业角色仍多页（v2 比 v1 更敢写 boundary，但 `maps_to` 尚未收敛到单一权威句）。

**建议**：以 v2 为**下一版主树候选**，但 **P0 先清 lint 硬错误 + 补 SSO 单元 + 收敛企业角色簇**，再考虑切流。旧树独有的 concept slug 不要丢，按 `maps_to` 合并别名。

---

## 2. 横切术语矩阵

| 用户说法 | v2 裁决 | 物理锚 | vs v1 | verdict_proposal |
|---|---|---|---|---|
| 认证状态 / 建档状态 | `auth_status` boundary | `cust_company_info.cust_build_status` | v1 同时有 `auth-status`（企业）与 `auth-state`（账户打款），边界已有；v2 账户侧需确认是否另有 concept | prefer_v2 企业侧；账户 `auth_state` 查 v2 是否遗漏 |
| 客户状态 | 与认证状态拆开（`company_status_fields`） | `cust_company_info.cust_status` | v1 `concept_cust_status` | merge 别名 |
| 录入方式 / 平台录入 | enum 真值正确 | `cust_company_info.cust_build_type` | v1 已按 159 病例修过 | prefer_v2 enum；修正 v2 散文「客户端录入」→「客户录入」 |
| 认证方式 | 待与 `identify_style` 对表 | 须 `identify_style` ≠ `cust_build_type` | v1 有 `concept_identify_style` | needs_human 若 v2 锚漂移 |
| 企业角色 / companyType | **仍多页**：`company-role` `companyType` `company_type` `cust-type` `company_role_type`… | JSON 数组 vs 单值 vs 角色行 | v1 同样碎（4+ 页争「企业角色」） | **needs_human**：指定一页权威 + 其余 synonym 互链 |
| 统码 | 标题重合 16 个共有业务名之一 | 应对 `certification_no` | v1 `certification_no` / `unified_social_credit_code` | merge 别名进 v2 锚页 |
| 租户码 / dbTenantCode | 共有 title `dbTenantCode` | 须 boundary vs `app_tenant_code` | v1 已有拆页 | prefer_v2 若 maps_to 正确；核租户隔离非 JOIN |

同名 concept title：v1 **7** 组重复，v2 **1** 组（结构上更干净，但企业角色改用不同 title 拆页，问题转为 maps 分散）。

---

## 3. 覆盖差集

### 3.1 表

- v1 表页 ⊆ v2（`only_v1 = 0`）。
- v2 多出（DB `db_only` + 代码可见）：  
  `cust_app_channel_config` `cust_message_send_policy` `open_sso_channel` `media_file`  
  `sys_cust_org_user_permission` `sys_cust_user_rel` `sys_user` `sys_user_sso_user`  
  `wechat_project_approval_apply_field_history` `wechat_project_approval_flow_file` `wx_work_user`
- 代码有、库无（不建权威表页）：`funding_party_rule_*`、`tenant_product_ext_field*`（见 `substrate-v2/tmp/table-reconcile.yaml`）。

```yaml
id: CMP-TABLE-01
severity: P1
kind: V2_ONLY
v1_pages: []
v2_pages: [cust_app_channel_config, open_sso_channel, sys_user, ...]
evidence: {db: "db-catalog 78 tables 2026-09-10"}
verdict_proposal: prefer_v2
```

### 3.2 枚举

- v1 独有页：`product_type`、`user_type`（v2 可能并入表字段 dict 或 unbound）。
- v2 `enum-unbound.yaml`：**69** 个未绑字段枚举 → 语义层未全部建页，属预期 REVIEW，不是幻觉。

```yaml
id: CMP-ENUM-01
severity: P1
kind: V1_ONLY
v1_pages: [product_type, user_type]
v2_pages: []
evidence: {code: extract-enums.yaml}
verdict_proposal: needs_human  # 确认是否系统实现枚举、应否建页
```

### 3.3 语义页（page_key 几乎不重叠）

独立重提导致 slug 重写：concept `both` 仅约 14 个 key；**title 共有 16**（交e保、企业角色、统码、认证方式、认证状态…）。不能用 page_key 当同一实体。合并必须以 `maps_to` / `表.字段` 为键。

`maps_to` 字符串完全相同的仅 **11** 条 → 大量同义页需要人工/二次对齐。

```yaml
id: CMP-SLUG-01
severity: P1
kind: SYN_IMPROVED
finding: 两边描述同一业务，key 不同；切流前要建 maps_to 对齐表，把 v1 aliases 并入 v2
verdict_proposal: merge
```

---

## 4. 明显冲突 / 错误

```yaml
id: CMP-BUILD-TYPE-01
severity: P0
kind: CONFLICT
v2_pages: [enums/cust_build_type, concepts/build_type]
evidence:
  code_comment: CustBuildTypeConstant PC_BUILD=客户录入 AGW_BUILD=平台录入
finding: 枚举页 label 正确；concept 散文写 PC_BUILD=客户端录入
verdict_proposal: prefer_v2 enum；改 concept 散文与 aliases
```

```yaml
id: CMP-SSO-01
severity: P0
kind: OMISSION_V2
v2_pages: []
finding: 单元「DBAss/SSO登录与通道」接受 0 / 拒绝 33。模型把 page_key 写成 table:xxx / concept:xxx，契约拒写。
verdict_proposal: 重跑该 topic（--only）并在生成提示收紧 page_key=裸 slug
```

```yaml
id: CMP-LINT-01
severity: P0
kind: CONFLICT
finding: v2 lint hard_errors=72（REF_TARGET_MISSING 67、ENUM_GENERIC_COLUMN 3、CONCEPT_UNANCHORED 1、GROUND_PARSE_FAILED 1）。典型失败= field_targets 写成 YAML 对象/驼峰字段名/非表名。
verdict_proposal: 修锚点格式后再 publish；当前禁止切流
```

```yaml
id: CMP-ROLE-01
severity: P1
kind: SYN_CLUSTER
v2_pages: [company-role, companyType, company_type, cust-type, company_role_type, company_role_bridge, port]
finding: 企业角色仍多页；有的 maps_to 是散文枚举列表而非 表.字段。比 v1 边界说明更好，锚点纪律更差。
verdict_proposal: needs_human — 指定权威 maps_to（建议 cust_company_info.cust_company_type JSON 数组为「企业多角色」；cust_role_info.role_type 为行级；其余 synonym + boundary）
```

```yaml
id: CMP-PAGEKEY-01
severity: P2
kind: CONFLICT
finding: 部分 v2 页 page_key 带 concept. / table: 前缀（parse 盖章后磁盘名与 frontmatter 可能不一致），召回别名会飘。
verdict_proposal: prefer_v2 内容；程序洗 page_key
```

---

## 5. 可能遗漏（v2）

| 缺口 | 说明 | 严重度 |
|---|---|---|
| SSO/DBAss 语义页 | 整单元拒写 | P0 |
| 账户级 `auth_state` 打款验证 | 需确认 v2 是否单独成 concept（企业认证已覆盖） | P1 |
| v1 独有 ~98 concept keys | 多数是 slug 更名；用 maps_to 对齐后剩余才是真遗漏 | P1 |
| pattern / metric | 两边都几乎没有；问数最小完备集未含 | P2 |
| `ground:relation` | baseline 仍不产；靠 enrich `## 关联表` | 已知债 |
| 69 unbound enums | 无 setter 绑定，未建 enum 页 | P2 |

db-enum-reconcile：**34** 个字段出现代码枚举外的库值（如 `async_io_task.status` 的 FAILED/RUNNING/SUCCESS、`cust_change_record.status` 脏值）。v2 部分 enum 已用 `SIMPLE` note 标 db 基线外值，应用同一模式铺开。

---

## 6. 建议改页批次（确认后才执行）

1. **P0 契约**：清洗 `field_targets`/`maps_to` 为 `表.字段`；去掉 `table:` 前缀；修 GROUND_PARSE；`--only DBAss/SSO登录与通道` 重跑。
2. **P0 真值**：`build_type` 散文与 enum 对齐；扫一遍 label 脑补。
3. **P1 术语簇**：企业角色、租户码、认证/客户/审核三状态、录入 vs 认证方式 — 每簇一权威页 + 互链。
4. **P1 从 v1 并入**：按 maps_to 把旧 aliases / also_confused_with 合并进 v2（**这是唯一允许读旧 wiki 来改 v2 的步骤**）。
5. **P1 lint**：BROKEN_LINK 用 enrich --force 再补一轮；剩余进 REVIEW。
6. **P2**：unbound enums、db-only 值、pattern 页。
7. 人确认后：`wiki_admin publish` 选择性发布 → 改运行时语料根。

---

## 7. 待你确认

1. 是否接受「v2 为主树、v1 只作别名矿」？
2. 企业角色权威锚点是否定为 `cust_company_info.cust_company_type`（多值）+ `cust_role_info.role_type`（行级）双锚 boundary？
3. SSO 单元是否立即 `--only` 重跑，还是下一迭代？
4. **在 1–3 完成前不要切流。**

---

## 8. 本轮产物路径

| 产物 | 路径 |
|---|---|
| 提取规范 | `docs/wiki-knowledge/Wiki知识提取规范指南-v1.md` |
| 底稿 | `docs/wiki-knowledge/pplatform/substrate-v2/` |
| DB 三件套 | `docs/wiki-knowledge/pplatform/db/`（已刷新） |
| 需求索引 | `docs/wiki-knowledge/pplatform/req-index/`（Desktop 优先切片 + Test-wiki 概念/实体） |
| 新 wiki | `docs/wiki-knowledge/pplatform/wiki-pages-v2/`（status=draft） |
| 计划 | `substrate-v2/tmp/page-plan.yaml`（26 单元） |
| 对账 | `substrate-v2/tmp/table-reconcile.yaml`、`db-enum-reconcile.yaml` |

管道小修（为独立重提可完成）：`ingest.py` 在零 FILE 块时重试一次；`pipeline.py` 把 topic 名中的 `/` 换成 `-` 以免 `_done` 断点失效，并落 `_analysis.yaml` / `_generation.md`。
