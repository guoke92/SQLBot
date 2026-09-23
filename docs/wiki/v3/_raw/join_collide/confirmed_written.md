# Confirmed EQUI_JOIN after semantic revise (9)

- generated_at: `2026-09-22T10:34:58.625033+00:00`
- B↔C allowed when same-semantic AND high overlap; homonyms never

- `cust_company_info.certification_no` → `ca_cfca_upgrade_report.certification_no` host=`ca_cfca_upgrade_report` — 
- `cust_company_info.certification_no` → `ca_fee_order.certification_no` host=`ca_fee_order` — 
- `tenant_migarory_log.platform_product_code` → `tenant_migarory_log_bak.platform_product_code` host=`tenant_migarory_log_bak` — 
- `tenant_product.platform_product_code` → `tenant_project.platform_product_code` host=`tenant_project` — 同语义产品业务码；父子场景重合高
- `tenant_interworking_product.platform_product_code` → `tenant_interworking_project.platform_product_code` host=`tenant_interworking_project` — 互通产品/项目同语义业务码；重合高
- `cust_interworking_product.platform_product_code` → `tenant_interworking_product.platform_product_code` host=`tenant_interworking_product` — 企业互通与租户互通产品业务码；重合高可连
- `authorization_agreement.platform_product_code` → `tenant_product.platform_product_code` host=`tenant_product` — 授权书与租户产品业务码；fk_like
- `authorization_agreement.platform_product_code` → `cust_auth_application.platform_product_code` host=`cust_auth_application` — 授权书与开通申请业务码；fk_like
- `cust_auth_application.platform_product_code` → `tenant_product.platform_product_code` host=`tenant_product` — 开通申请与租户产品业务码；fk_like
