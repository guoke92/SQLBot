# Join collide (cartesian TopK)

Stage-1 recall: keep any pair with non-zero TopK value presence; drop zero-hit. Refine later.

## Stats

```yaml
endpoints: 2216
pairs_total: 1237081
pairs_pending: 1237081
pairs_resumed: 0
k: 50
workers: 12
distinct_cached: 1539
hit_sample_intersect: 64767
hit_distinct_cache: 18414
hit_sql: 13205
miss_zero: 1140695
empty_bag: 0
query_error: 0
survivors_raw: 96386
survivors_new: 96295
skipped_removed: 2
skipped_existing: 89
elapsed_sec: 330.4
```

## Sample survivors (first 80 new)

| left | right | how | hit_count |
|---|---|---|---|
| `argeement_migratory_record.agreement_name` | `authorization_agreement.act_procinst_id` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `authorization_agreement.code` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `authorization_agreement.cust_manager_id` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `authorization_agreement.cust_manager_name` | distinct_intersect | 6 |
| `argeement_migratory_record.agreement_name` | `authorization_agreement.cust_name` | sql_left_in_right | 2 |
| `argeement_migratory_record.agreement_name` | `authorization_agreement.id` | sql_left_in_right | 4 |
| `argeement_migratory_record.agreement_name` | `authorization_agreement.name` | sql_left_in_right | 2 |
| `argeement_migratory_record.agreement_name` | `ca_fee_company.locked_annual_fee` | sample_intersect | 2 |
| `argeement_migratory_record.agreement_name` | `ca_fee_company.special_annual_fee` | sample_intersect | 2 |
| `argeement_migratory_record.agreement_name` | `ca_fee_order.annual_fee` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `ca_fee_order.pay_amount` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `ca_fee_order.version` | sample_intersect | 2 |
| `argeement_migratory_record.agreement_name` | `ca_fee_project_config.core_annual_fee` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `ca_fee_project_config.supplier_annual_fee` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `ca_fee_special_config.annual_fee` | sample_intersect | 3 |
| `argeement_migratory_record.agreement_name` | `ca_fee_special_config.remark` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `client_api_sync_error.retry_num` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_access_secret.id` | sample_intersect | 4 |
| `argeement_migratory_record.agreement_name` | `cust_access_secret.key_num` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_access_secret.name` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_account_info.account_name` | distinct_intersect | 5 |
| `argeement_migratory_record.agreement_name` | `cust_account_info.account_no` | sql_left_in_right | 4 |
| `argeement_migratory_record.agreement_name` | `cust_account_info.bank_province_code` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_account_info.payment_remaining_count` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_certification_info.auto_verify_count` | sample_intersect | 4 |
| `argeement_migratory_record.agreement_name` | `cust_change_cfg.cust_type` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_change_cfg.data_desc` | distinct_intersect | 3 |
| `argeement_migratory_record.agreement_name` | `cust_change_cfg.id` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_change_cfg.oper_item` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_change_cfg.plat_item` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_change_record.alter_mode` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_change_record.alter_type` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_change_record.alter_type_id` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_change_record.cust_id` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_change_record.cust_type` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.bank_branch` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.business_status` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.certification_no` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.cust_former_name` | distinct_intersect | 3 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.cust_short_name` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.data_type` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.finance_org_code` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.legal_name` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.legal_name_english` | sample_intersect | 2 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.legal_name_english_end` | distinct_intersect | 4 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.name` | sql_left_in_right | 2 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.regist_city_english` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.registered_address` | distinct_intersect | 6 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.remark` | distinct_intersect | 6 |
| `argeement_migratory_record.agreement_name` | `cust_company_info.tenant_flg_en` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_company_lifecycle_info.reason` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_config_mapping.code` | sample_intersect | 5 |
| `argeement_migratory_record.agreement_name` | `cust_config_mapping.id` | sample_intersect | 5 |
| `argeement_migratory_record.agreement_name` | `cust_config_mapping.inner_name` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_config_mapping.name` | sample_intersect | 5 |
| `argeement_migratory_record.agreement_name` | `cust_config_mapping.outer_name` | distinct_intersect | 2 |
| `argeement_migratory_record.agreement_name` | `cust_head_company_info.legal_name` | distinct_intersect | 2 |
| `argeement_migratory_record.agreement_name` | `cust_invite_info.channel_code` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_invite_info.contact_name` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_invite_info.name` | distinct_intersect | 2 |
| `argeement_migratory_record.agreement_name` | `cust_oper_change_record.person_name` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.certification_no` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.cust_company_id` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.email` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.en_name` | distinct_intersect | 4 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.en_name_end` | sample_intersect | 2 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.id` | sql_left_in_right | 2 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.name` | sql_left_in_right | 3 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.operator_id` | distinct_intersect | 2 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.phone` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.user_id` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `cust_person_info.user_name` | sql_left_in_right | 2 |
| `argeement_migratory_record.agreement_name` | `cust_project_code_record.channel_code` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_project_pushcust.id` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_project_rel.create_user` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_project_rel.id` | sql_left_in_right | 1 |
| `argeement_migratory_record.agreement_name` | `cust_project_rel.op_contact_a_group` | sample_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_project_rel.product_id` | distinct_intersect | 3 |
| `argeement_migratory_record.agreement_name` | `cust_project_rel.tenant_flg_en` | distinct_intersect | 1 |
| `argeement_migratory_record.agreement_name` | `cust_project_rel.update_user` | distinct_intersect | 1 |

## Priority for refine

`priority_candidates.jsonl`: **3632** (same_name / *_id→id / *_code). Full recall: `hits.jsonl` (96386).
