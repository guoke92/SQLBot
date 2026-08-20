# 示例：建档场景的完整提取

以 `pplatform-web` 的「自主注册建档」为例，演示一个场景从代码穿透到知识落点的全过程。

## 1. 入口与链路

```
OperCustFacade.regSelfOld(companyId, personId)   # 自主注册建档（事务）
  → getCustCompany(companyId)                    # 读 cust_company_info
  → getCustPerson(cust.getCode(), personId)      # 读 cust_person_info（按 ref_cust_company_info）
  → setCustProjectInfo(cust, rq, true)
      → custProjectRelService.lambdaQuery()      # 读 cust_project_rel（按 ref_cust_project_rel_cust_company_info）
      → tenantService.getFirstByDbTenantCode()   # 读 tenant_setting_config
      → tenantProjectService.getById()           # 读 tenant_project
      → platformProductService.getOne()          # 读 platform_product（按 platform_product_code）
      → saveCustProjectRelDO()                   # 写 cust_project_rel
  → updateCustCompany(cust)                      # 写 cust_company_info.check_status
  → updateCustUser(...)                          # 写 cust_person_info.platform_user_id
  → saveCustBuildRecord(companyId, personId, ...) # 写 cust_build_record
```

## 2. 关系清单（9 条，全部 proposed）

| left | right | 类型 | 备注 |
|---|---|---|---|
| `cust_person_info.ref_cust_company_info` | `cust_company_info.code` | many_to_one | 读+写，全库最高频主外键 |
| `cust_project_rel.ref_cust_project_rel_cust_company_info` | `cust_company_info.code` | many_to_one | 读+写 |
| `cust_role_info.ref_cust_company_info` | `cust_company_info.code` | many_to_one | 读+写 |
| `cust_account_info.ref_cust_company_info` | `cust_company_info.code` | many_to_one | 读 |
| `cust_project_rel.project_id` | `tenant_project.id` | many_to_one | `cast: long_to_string`（`setProjectId(""+projectDO.getId())`） |
| `cust_project_rel.product_id` | — | derived_copy | `= tenant_project.product_id`；真 FK 是 `tenant_project.product_id → tenant_product.id` |
| `tenant_project.platform_product_code` | `platform_product.product_code` | many_to_one | 读 |
| `cust_build_record.cust_id` | `cust_company_info.id` | many_to_one | 写（形参 `companyId` 传播） |
| `cust_build_record.person_id` | `cust_person_info.id` | many_to_one | 写（形参 `personId` 传播） |

## 3. 读写流转（processes）

```text
读链路：cust_company_info(by id)
        → .code → cust_person_info(ref_cust_company_info)
        → .code → cust_project_rel(ref_cust_project_rel_cust_company_info)
        → .db_tenant_code → tenant_setting_config → default_project_id
        → tenant_project(by id) → .platform_product_code → platform_product(product_code)

写链路（按业务顺序）：
        1. update cust_person_info.user_type
        2. insert cust_project_rel { project_id ← tenant_project.id, product_id ← tenant_project.product_id(派生),
                                     ref_cust_project_rel_cust_company_info ← cust.code }
        3. update cust_company_info.check_status
        4. update cust_person_info.platform_user_id
        5. insert cust_build_record { cust_id ← companyId, person_id ← personId }
```

## 4. 其余维度清单（关系之外必须提）

### 4.1 枚举（field.dictionary）——两平面

**业务枚举（字段已在包内 + 值有业务语义，进包）：**

| 字段 | 取值 | 来源 | 用户会问 |
|---|---|---|---|
| `cust_company_info.cust_build_status` | INIT/TO_BE_BUILD/BUILDING/BUILD_SUCCESS/BUILD_FAIL/BUILD_BACK/BUILD_ACTIVATE/CUST_CONFIRM_AWAIT/CUST_AUDIT_AWAIT/CUST_BUILDING/CUST_BUILD_SUCCESS/CUST_BUILD_FAIL/CUST_CHANGE/AWAIT_CUST_CONFIRM | `CustBuildStatusEnum` | "建档成功的/在建的企业" |
| `cust_company_info.cust_status` | ADD/EFFECT/FAILURE/WRITEOFF/FREEZE/CHANGE | `CustStatusEnum` | "生效的/注销的企业" |
| `cust_company_info.check_status` | CUST_CHECK_INIT/CUST_CHECK_PASS/CUST_CHECK_REJECT | `CheckStatus` | "审核通过/驳回的" |
| `cust_person_info.user_type` | admin/… | `UserTypeEnum` | "管理员" |
| `cust_project_rel.company_type` | CORE/FINANCE/SUPPLIER/PLATFORM_OPERATOR_COMPANY | `CustCompanyTypeEnum` | "核心企业/供应商/资金方" |

**系统枚举（留 `enums.yaml` 参考，不进包）：**

| 字段 | 取值 | 为什么不进包 |
|---|---|---|
| `time_unit` | year/month/day/hour/minute/second | 技术单位，用户不问 |
| `sign_mode` | 01/02/03 | 内部编码 |
| `ca_fee_redirect_type` | CA_FEE_PAY/CA_RENEW/… | 内部路由 |
| `ca_fee_todo_ensure_trigger` | CA_AUTH_SUCCESS/BUILD_APPROVED/… | 内部触发 |

> 判定口诀：**字段在不在包内 + 用户会不会用自然语言指代这个值**。两者都满足才写 `field.dictionary`，否则留在 `enums.yaml` 当参考。

### 4.2 状态机（processes.next_stages）

建档有**两套 build 语义，必须区分**：

- **认证流**（CA 认证）：`INIT/TO_BE_BUILD → BUILDING → BUILD_SUCCESS / BUILD_FAIL / BUILD_BACK`
- **审核流**：`CUST_AUDIT_AWAIT → CUST_BUILDING → CUST_BUILD_SUCCESS / CUST_BUILD_FAIL`
- `check_status`：`CUST_CHECK_INIT → CUST_CHECK_PASS / CUST_CHECK_REJECT`

### 4.3 口径（calibers）

- 有效企业 = `(cust_build_status=BUILD_SUCCESS AND cust_status=EFFECT) OR (cust_build_status=CUST_CHANGE AND cust_status=CHANGE)`
- 在途建档 = `check_status IS NOT NULL AND check_status != CUST_CHECK_REJECT`
- 「认证成功」(BUILD_SUCCESS) ≠ 「审核通过」(CUST_BUILD_SUCCESS)

### 4.4 指标（metrics）

- 建档企业数：`COUNT(cust_company_info)`，按阶段口径拆分——创建 / 提交认证 / 进入审核 / 认证成功 是四个不同 COUNT（需澄清）。
- 建档记录数：`COUNT(cust_build_record)`
- 项目企业数：`COUNT(cust_project_rel)`

### 4.5 业务规则（domain_rules）

- 自主注册建档需分布式锁 + 二次校验，防在途重复（`check_status` 非空且非 REJECT 即视为在途）。
- 建档推送失败 → 回滚 `cust_build_status=INIT`。
- 无项目码时自动绑定租户默认项目（`tenant_setting_config.default_project_id`）。
- 供应商 + ACFLOW/ORDER 产品 → `cust_project_rel.status='1'`。

## 5. 提炼要点

1. 「建档」不是单一状态字段，而是**认证流 + 审核流两套状态机**。
2. 「本月建档了多少企业」本身歧义：按创建时间 / 提交认证 / 审核通过 / 认证成功，是四个不同 COUNT——这正是要提取的指标口径差异，也是 SQLBot 澄清的触发点。
3. 关系要区分「真 FK」「派生拷贝（derived_copy）」「外部引用（external_ref）」，不能一视同仁标直连。
