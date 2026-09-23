# JOIN patterns (from live validation + code)

- generated_at: `2026-09-22T08:06:43.933903+00:00`

## Hard rules

1. **`ref_cust_company_info` / `ref_*_cust_company_info` → `cust_company_info.code`**（不是 `id`）。
   Live + code（如 OperCustFacade）一致；`id→ref_*` 与 `code→ref_*` 冲突时删 id 侧。
2. **`*_id` / `cust_id` / `company_id` → 对端表主键 `id`**（雪花 Long）。
3. **`ref_*` / `*_code` 业务码列 → 对端 `code`**（UUID/业务编码字符串）。
4. **`platform_product.code`（UUID）≠ `*.platform_product_code`（业务码如 ACFLOW）** — 已全部剔除。
5. **同表对共享端点原则**：若未定边 `A.a↔B.x`，而 `A.a↔B.y` 或 `A.b↔B.x` 已 confirmed，则移除未定边。
6. **双轨可并存**：同一对表可同时有 `id↔*_id` 与 `code↔ref_*/*_code`（如 person、oper_change、tenant_product↔project、interworking）。
7. **审批族**：子表 `ref_*_project_approval` → `tenant_project_approval.code`；
   `approval.flow_code` → `tenant_project_approval_flow_config.flow_code`（不是 flow 表 code/id）。
8. **同名字段：先辨语义，再谈 JOIN（2026-09-22，已修订）**：
   - **同名异义**（homonym）：列名相同、业务含义不同 → **禁止** EQUI_JOIN。例：`tenant_project.channel_code`（项目邀请码）≠ `open_sso_channel.channel_code` / `cust_company_info.channel_code`（SSO/建档渠道）。须落 **不同 concept**，`also_confused_with` 互指。
   - **同名同义**（same semantic）：多表冗余/拷贝同一业务字段 → 先落 **业务术语（concept）** 标注 `field_targets`；是否 EQUI_JOIN 看值域：
     - 重合高（`fk_like` / 实质 `shared_domain`）→ **可以** 强关联（含枢纽 `A.x→B`、`A.x→C`，以及 **B↔C**）。
     - 重合低（阶段/场景切片导致值域出入）→ **不**强连，术语层知同一语义即可。
   - 代码已否决的例外（内存 contains、CSV notIn、明确 gap）仍不编 JOIN，即使列名相同。
   - 术语与对照：`docs/wiki/v3/_raw/l1_intermediate/docs/field_semantics.yaml`；审计见 `join_collide/semantic_vs_join_audit.md`。

## Confirmed right-column → left endpoints

- `*.apply_id` ← `wechat_project_approval_apply.id`
- `*.certification_no` ← `ca_fee_company.certification_no`, `cust_company_info.certification_no`
- `*.company_code` ← `cust_company_info.code`
- `*.company_id` ← `cust_company_info.id`
- `*.cust_company_id` ← `cust_company_info.id`
- `*.cust_id` ← `cust_company_info.id`
- `*.default_project_id` ← `tenant_project.id`
- `*.fund_rule_code_ref` ← `funding_rule_info.code`
- `*.invite_cust_id` ← `cust_company_info.id`
- `*.person_id` ← `cust_person_info.id`
- `*.platform_product_id` ← `platform_product.id`
- `*.product_id` ← `tenant_interworking_product.id`, `tenant_product.id`
- `*.project_approval_id` ← `tenant_project_approval.id`
- `*.project_id` ← `tenant_project.id`
- `*.ref_cust_company_info` ← `cust_company_info.code`
- `*.ref_cust_head_company_info_cust_company_info` ← `cust_company_info.code`
- `*.ref_cust_interworking_product_cust_company_info` ← `cust_company_info.code`
- `*.ref_cust_project_rel_cust_company_info` ← `cust_company_info.code`
- `*.ref_tenant_interworking_project_tenant_interworking_product` ← `tenant_interworking_product.code`
- `*.ref_tenant_product_tenant_setting_config` ← `tenant_setting_config.code`
- `*.ref_tenant_project_approval_business_info_project_approval` ← `tenant_project_approval.code`
- `*.ref_tenant_project_approval_flow_comment_approval` ← `tenant_project_approval.code`
- `*.ref_tenant_project_approval_flow_credit_project_approval` ← `tenant_project_approval.code`
- `*.ref_tenant_project_approval_flow_credit_project_approval_node` ← `tenant_project_approval_flow_node.code`
- `*.ref_tenant_project_approval_flow_file_comment` ← `tenant_project_approval_flow_comment.code`
- `*.ref_tenant_project_approval_flow_file_project_approval` ← `tenant_project_approval.code`
- `*.ref_tenant_project_approval_flow_file_project_approval_flow_node` ← `tenant_project_approval_flow_node.code`
- `*.ref_tenant_project_approval_flow_node_project_approval` ← `tenant_project_approval.code`
- `*.ref_tenant_project_approval_flow_node_project_approval_flow` ← `tenant_project_approval_flow.code`
- `*.ref_tenant_project_approval_flow_tenant_project_approval` ← `tenant_project_approval.code`
- `*.ref_tenant_project_approval_tenant_project` ← `tenant_project.code`
- `*.ref_tenant_project_product_code` ← `tenant_product.code`
- `*.ref_tenant_project_tenant_code` ← `tenant_setting_config.code`
- `*.rule_info_id` ← `funding_rule_info.id`
- `*.source_project_id` ← `tenant_project.id`
- `*.tenant_id` ← `tenant_setting_config.id`

## Dual-track table pairs (both kept)

- **cust_company_info ↔ cust_interworking_product**
  - `cust_company_info.id` → `cust_interworking_product.cust_id`
  - `cust_company_info.code` → `cust_interworking_product.ref_cust_interworking_product_cust_company_info`
- **cust_company_info ↔ cust_oper_change_record**
  - `cust_company_info.id` → `cust_oper_change_record.company_id`
  - `cust_company_info.code` → `cust_oper_change_record.company_code`
- **cust_company_info ↔ cust_person_info**
  - `cust_company_info.code` → `cust_person_info.ref_cust_company_info`
  - `cust_company_info.id` → `cust_person_info.cust_company_id`
- **funding_rule_detail ↔ funding_rule_info**
  - `funding_rule_info.id` → `funding_rule_detail.rule_info_id`
  - `funding_rule_info.code` → `funding_rule_detail.fund_rule_code_ref`
- **tenant_interworking_product ↔ tenant_interworking_project**
  - `tenant_interworking_product.id` → `tenant_interworking_project.product_id`
  - `tenant_interworking_product.code` → `tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product`
- **tenant_product ↔ tenant_project**
  - `tenant_product.id` → `tenant_project.product_id`
  - `tenant_product.code` → `tenant_project.ref_tenant_project_product_code`
- **tenant_product ↔ tenant_setting_config**
  - `tenant_setting_config.id` → `tenant_product.tenant_id`
  - `tenant_setting_config.code` → `tenant_product.ref_tenant_product_tenant_setting_config`
- **tenant_project ↔ tenant_project_approval**
  - `tenant_project_approval.id` → `tenant_project.project_approval_id`
  - `tenant_project.code` → `tenant_project_approval.ref_tenant_project_approval_tenant_project`
- **tenant_project ↔ tenant_setting_config**
  - `tenant_setting_config.id` → `tenant_project.tenant_id`
  - `tenant_setting_config.code` → `tenant_project.ref_tenant_project_tenant_code`
  - `tenant_project.id` → `tenant_setting_config.default_project_id`
