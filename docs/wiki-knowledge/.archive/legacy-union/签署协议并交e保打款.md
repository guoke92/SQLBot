---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: process
title: 签署协议并交e保打款
page_key: 签署协议并交e保打款
domain: cafee
aliases: []
---
# 签署协议并交e保打款



```ground:process
process: 签署协议并交e保打款
stages:
- stage: 签署协议并交e保打款
  trigger: 企业端协议签署、交e保开户、确认打款
  effects:
  - op: update
    table: ca_fee_order
    fields:
    - agreement_signed
    - agreement_version
    - agreement_sign_time
    - agreement_file_path
    - pay_method
    - pay_amount
    - pay_time
    - order_status
    - invoice_status
    - bocom_plfm_ser_no
    - bocom_plfm_bsn_id
    - bocom_req_sn
    - bocom_txn_sts
    - invoice_no
    - invoice_file_path
    - close_reason
  - op: upsert
    table: ca_fee_company
    fields:
    - certification_no
    - company_name
    - tenant_id
    - locked_annual_fee
    - fee_locked
    - pay_status
    - service_start
    - service_end
    - source_project_id
    - source_company_type
    - special_config_flag
    - special_annual_fee
  transitions: []
```

## 关联
- [[ca_fee_company]]
- [[ca_fee_order]]
