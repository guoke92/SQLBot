# Semantic vs EQUI_JOIN（修订）

- generated_at: 2026-09-22（按用户澄清修订）

## 原则（纠正）

1. **同名异义**：列名同、含义不同 → 分建术语 + `also_confused_with`，**禁止**跨义 EQUI_JOIN。  
   例：项目邀请码 `channel_code` ≠ SSO/建档渠道 `channel_code`。对照页：[[concepts/channel_code_homonym_bundle]]（见 wiki）。
2. **同名同义**：多表同一业务字段 → **必须**挂业务术语（`field_targets`）；JOIN **看值域**：
   - 重合高（`fk_like` / 实质 `shared_domain`）→ **可以**强关联，**包括** `A.x→B`、`A.x→C` 以及 **B↔C**；
   - 重合低（阶段/场景切片）→ 只留术语，不强连。
3. 代码已否决（内存 contains、明确 gap）的仍不编 JOIN。

## 术语登记

权威 YAML：`docs/wiki/v3/_raw/l1_intermediate/docs/field_semantics.yaml`

| 类型 | concept | 说明 |
|---|---|---|
| 同义 | `platform_product_code_term` | 平台产品业务码及各表拷贝 |
| 同义 | `funding_product_code_term` | 资方规则产品码 |
| 同义 | `tenant_menu_product_code_term` | 菜单/按钮产品码 |
| 同义 | `certification_no_term` | 企业统码 |
| 同义 | `channel_code_term` | 项目邀请码（含关联表拷贝） |
| 同义 | `channel_archive_longteng` | SSO/建档渠道码对齐 |
| 异义索引 | `channel_code_homonym_bundle` | channel_code / code / sp_no / product_code 消歧 |

## JOIN patterns

见 `docs/wiki/v3/_raw/join_validation/join_patterns.md` §8（已改「B↔C 重合高可连」）。
