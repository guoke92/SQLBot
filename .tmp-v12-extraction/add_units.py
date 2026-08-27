# -*- coding: utf-8 -*-
"""Add second batch units to pplatform-web-v12 package."""
import yaml
from pathlib import Path

PKG = Path("/Users/fanjunwei/Projects/SQLBot/data/knowledge-packages/v12")
SRC = "src-pplatform-web"

# ---------------------------------------------------------------------------
# new evidence entries
# ---------------------------------------------------------------------------
def ev(eid, kind, locator, claim):
    return {"evidence_id": eid, "source_id": SRC, "evidence_kind": kind, "locator": locator, "claim": claim}

new_evidence = [
    ev("ev-fund-exception-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/FundingExceptionResolutionDO.java", "funding_exception_resolution 表字段定义"),
    ev("ev-fund-exception-import", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java:103-160", "资方异常解析导入：Excel 读取 + productCode/对接方标识校验，全部通过才 upsert"),
    ev("ev-fund-exception-upsert", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java:291-328", "资方异常解析 upsert：按 productCode+fundingPartyCode+errorKeyword+enable 保存"),
    ev("ev-fund-exception-export", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java:356-388", "资方异常解析分页导出，enable=Y，上限 50000"),
    ev("ev-fund-exception-delete", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java:408-415", "按 id 批量删除异常解析记录"),
    ev("ev-fund-exception-check", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java:522-540", "保存前校验同一产品+资方+报错关键字唯一"),

    ev("ev-account-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustAccountInfoDO.java", "cust_account_info 表字段定义"),
    ev("ev-role-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustRoleInfoDO.java", "cust_role_info 表字段定义"),
    ev("ev-user-rel-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustUserRelDO.java", "cust_user_rel 表字段定义"),
    ev("ev-account-check-before", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:65-83", "保存账户前查重：account_no + ref_cust_company_info 唯一"),
    ev("ev-account-set-default", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:85-107", "设置默认账户：先取消旧默认再置新默认"),
    ev("ev-account-after-save", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:125-155", "保存后处理：无默认账户时将当前账户置默认"),
    ev("ev-account-get-by-cust", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:306-315", "按企业 id 查银行账户列表"),
    ev("ev-account-delete-other", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:352-370", "删除其他账户：查 id 列表后按主键批量删除避免死锁"),
    ev("ev-role-status-change", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustRoleApplication.java:63-96", "客户角色冻结/解冻/注销"),
    ev("ev-role-update-status-by-company", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustRoleApplication.java:112-136", "按企业 code 批量更新角色状态，WRITEOFF 跳过"),
    ev("ev-role-add-role-info", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustRoleApplication.java:138-181", "新增企业角色：先删旧角色再批量插入，并回写 cust_project_rel.company_type"),
    ev("ev-user-rel-save", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/SubmitCustInfoEnhanceService.java:161-185", "按企业角色和联系人生成 cust_user_rel 记录"),
    ev("ev-user-rel-get", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustCompanyIfoEnchanceService.java:565-567", "按 userId+companyId+companyType 查询企业用户关系"),

    ev("ev-tenant-product-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProductDO.java", "tenant_product 表字段定义"),
    ev("ev-platform-product-cust-role-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/PlatformProductCustRoleDO.java", "platform_product_cust_role 表字段定义"),
    ev("ev-tenant-product-all-by-cust-type", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:119-149", "按租户+企业角色过滤适配产品，读取 platform_product_cust_role"),
    ev("ev-tenant-product-create", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:306-317", "租户创建产品入口"),
    ev("ev-tenant-product-active", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:318-342", "租户产品开通：Y 直接返回；ACFLOW/ORDER 置 P；其他置 Y 并推送"),
    ev("ev-tenant-product-cancel", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantProductApplication.java:380-390", "取消开通入口"),
    ev("ev-tenant-product-domain-create", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/TenantProductDomainService.java:133-183", "租户产品创建：每个租户每个平台产品只保留一条，按平台产品复制字段"),
    ev("ev-tenant-product-domain-active", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/TenantProductDomainService.java:184-200", "租户产品开通落库：open_status=Y"),
    ev("ev-tenant-product-domain-cancel", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/TenantProductDomainService.java:88-113", "租户产品取消：open_status=N"),
    ev("ev-tenant-product-check-on-way", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/TenantProductDomainService.java:115-131", "取消前校验：已关联项目/企业不允许取消"),
]

# dictionaries
OPEN_STATUS_DICT = {"Y": "已开通", "P": "开通中", "N": "未开通"}
ROLE_STATUS_DICT = {"ADD": "新增", "EFFECT": "生效", "FREEZE": "冻结", "WRITEOFF": "注销"}

def fld(field_id, name, dtype, desc, dictionary=None, refs=None):
    d = {"field_id": field_id, "name": name, "data_type": dtype, "description": desc}
    if dictionary:
        d["dictionary"] = dictionary
    if refs:
        d["evidence_refs"] = refs
    return d

def dset(dataset_id, name, desc, fields, database="lowcode_pplatform", inactive=False, refs=None):
    d = {"dataset_id": dataset_id, "name": name, "description": desc, "database": database, "inactive": inactive, "fields": fields}
    if refs:
        d["evidence_refs"] = refs
    return d

# ---------------------------------------------------------------------------
# Unit: funding-exception-resolution
# ---------------------------------------------------------------------------
exception_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-fund-exception-schema"]),
    fld("exception_no", "exception_no", "varchar", "异常编号", refs=["ev-fund-exception-schema"]),
    fld("funding_party_code", "funding_party_code", "varchar", "对接方标识", refs=["ev-fund-exception-schema"]),
    fld("funding_party_name", "funding_party_name", "varchar", "资金方名称", refs=["ev-fund-exception-schema"]),
    fld("error_keyword", "error_keyword", "varchar", "报错关键字", refs=["ev-fund-exception-schema"]),
    fld("error_reason", "error_reason", "varchar", "报错原因", refs=["ev-fund-exception-schema"]),
    fld("suggestion", "suggestion", "varchar", "建议处理方案", refs=["ev-fund-exception-schema"]),
    fld("product_code", "product_code", "varchar", "产品code", refs=["ev-fund-exception-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-fund-exception-schema"]),
]
exception_unit = {
    "unit_id": "funding-exception-resolution",
    "revision": 1,
    "title": "资金方异常解决",
    "aliases": ["资方异常解析", "异常处理建议"],
    "domain": "funding",
    "applicability": "资金方异常报错关键字与处理建议的导入/保存/查询/导出场景",
    "description": "穿透 ExceptionResolutionApplication：Excel 导入校验（产品编码+对接方标识 RPC）→ 单事务 upsert → 按 id 批量删除/分页导出；保存前校验同产品+资方+报错关键字唯一。",
    "content": {
        "concepts": [
            {
                "concept_id": "funding-exception-resolution",
                "name": "资金方异常解决记录",
                "aliases": ["异常解析", "异常处理建议"],
                "definition": "资金方异常解决表 funding_exception_resolution，以主键 id 锚定。",
                "field_targets": [{"dataset": "funding_exception_resolution", "field": "id"}],
                "evidence_refs": ["ev-fund-exception-schema"],
            },
            {
                "concept_id": "error-keyword",
                "name": "报错关键字",
                "aliases": ["异常关键字"],
                "definition": "资金方异常解决记录的报错关键字，同产品+资方下唯一。",
                "dictionary": {},
                "field_targets": [{"dataset": "funding_exception_resolution", "field": "error_keyword"}],
                "evidence_refs": ["ev-fund-exception-check"],
            },
        ],
        "processes": [
            {
                "stage_id": "exception-import",
                "name": "异常解决导入/保存",
                "description": "Excel 导入逐行校验（必填、productCode 枚举、对接方标识 RPC）全部通过后单事务 upsert；单条保存前校验关键字唯一。",
                "trigger": "ExceptionResolutionApplication.importRecords / checkBeforeSave + afterSave",
                "enter_conditions": ["Excel 内容非空", "productCode 合法", "对接方标识存在"],
                "exit_conditions": ["全部错误返回或 upsert 完成"],
                "next_stages": ["exception-query"],
                "data_effects": [
                    {"operation": "read", "dataset": "funding_exception_resolution", "fields": ["id", "product_code", "funding_party_code", "error_keyword"], "condition": "product_code = :productCode AND funding_party_code = :fundingPartyCode AND error_keyword = :errorKeyword AND id != :id", "description": "保存前查重，报错关键字已存在则拒绝", "evidence_refs": ["ev-fund-exception-check"]},
                    {"operation": "upsert", "dataset": "funding_exception_resolution", "fields": ["exception_no", "product_code", "funding_party_code", "funding_party_name", "error_keyword", "error_reason", "suggestion", "enable"], "condition": "校验通过后按行 upsert", "description": "导入/保存异常解决记录，enable=Y", "evidence_refs": ["ev-fund-exception-import", "ev-fund-exception-upsert"]},
                ],
                "evidence_refs": ["ev-fund-exception-import"],
            },
            {
                "stage_id": "exception-query",
                "name": "异常解决查询/导出",
                "description": "按查询条件分页读取 enable=Y 记录并导出 Excel，单次导出上限 50000 行。",
                "trigger": "ExceptionResolutionApplication.exportRecords / Controller 查询",
                "enter_conditions": ["查询条件合法"],
                "exit_conditions": ["分页导出完成"],
                "next_stages": [],
                "data_effects": [
                    {"operation": "read", "dataset": "funding_exception_resolution", "fields": ["id", "exception_no", "product_code", "funding_party_code", "funding_party_name", "error_keyword", "error_reason", "suggestion", "enable"], "condition": "enable='Y' + 查询条件", "description": "分页读取异常解决记录", "evidence_refs": ["ev-fund-exception-export"]},
                ],
                "evidence_refs": ["ev-fund-exception-export"],
            },
            {
                "stage_id": "exception-delete",
                "name": "异常解决删除",
                "description": "按 id 列表批量删除异常解决记录。",
                "trigger": "FundingPartyExceptionResolutionController.batchDel -> ExceptionResolutionApplication.batchDelete",
                "enter_conditions": ["ids 非空"],
                "exit_conditions": ["记录已删除"],
                "next_stages": [],
                "data_effects": [
                    {"operation": "delete", "dataset": "funding_exception_resolution", "fields": ["id"], "condition": "id IN :ids", "description": "按主键批量删除", "evidence_refs": ["ev-fund-exception-delete"]},
                ],
                "evidence_refs": ["ev-fund-exception-delete"],
            },
        ],
        "datasets": [
            dset("funding_exception_resolution", "funding_exception_resolution", "资金方异常解析及建议", exception_fields, refs=["ev-fund-exception-schema"]),
        ],
        "relationships": [],
        "metrics": [
            {
                "metric_id": "metric-exception-count",
                "name": "资金方异常解决记录数",
                "description": "异常解析及建议记录数。",
                "aggregation": "COUNT",
                "field": {"dataset": "funding_exception_resolution", "field": "id"},
                "grain": [{"dataset": "funding_exception_resolution", "field": "id"}],
                "filters": [],
                "evidence_refs": ["ev-fund-exception-export"],
            },
        ],
        "calibers": [
            {
                "caliber_id": "cal-exception-active",
                "label": "有效异常解决记录",
                "description": "enable=Y 的资金方异常解决记录。",
                "contract_fragment": {"predicate": "enable = 'Y'", "scope": "funding_exception_resolution 全局定义"},
                "field_targets": [{"dataset": "funding_exception_resolution", "field": "enable"}],
                "evidence_refs": ["ev-fund-exception-export"],
            },
            {
                "caliber_id": "cal-exception-unique",
                "label": "同产品+资方+报错关键字唯一范围",
                "description": "同一 product_code + funding_party_code + error_keyword 下仅允许一条 enable=Y 记录。",
                "contract_fragment": {"predicate": "product_code = :productCode AND funding_party_code = :fundingPartyCode AND error_keyword = :errorKeyword AND enable = 'Y'", "scope": "checkBeforeSave 与导入 upsert 共同遵守"},
                "field_targets": [
                    {"dataset": "funding_exception_resolution", "field": "product_code"},
                    {"dataset": "funding_exception_resolution", "field": "funding_party_code"},
                    {"dataset": "funding_exception_resolution", "field": "error_keyword"},
                ],
                "evidence_refs": ["ev-fund-exception-check", "ev-fund-exception-upsert"],
            },
        ],
        "domain_rules": [
            {
                "rule_id": "rule-exception-import-all-or-nothing",
                "label": "导入校验全部通过才保存",
                "content": "Excel 导入存在任一必填/产品编码/对接方标识错误时直接返回全部错误，不执行保存；全部通过后单事务 upsert，任一条失败整体回滚。",
                "applicability": "ExceptionResolutionApplication.importRecords",
                "query_impact": "异常解决表不会出现导入失败的半批数据；查询时无需区分导入成功/失败状态。",
                "field_targets": [
                    {"dataset": "funding_exception_resolution", "field": "product_code"},
                    {"dataset": "funding_exception_resolution", "field": "funding_party_code"},
                ],
                "evidence_refs": ["ev-fund-exception-import"],
            },
            {
                "rule_id": "rule-exception-export-max",
                "label": "异常解决导出上限 50000 行",
                "content": "单次导出最多 50000 行，超过上限抛出业务异常要求缩小查询范围。",
                "applicability": "ExceptionResolutionApplication.exportRecords",
                "query_impact": "导出/查询超过 50000 行时应提示缩小范围，不应尝试一次取全量。",
                "field_targets": [{"dataset": "funding_exception_resolution", "field": "id"}],
                "evidence_refs": ["ev-fund-exception-export"],
            },
        ],
        "verified_query_patterns": [
            {
                "pattern_id": "pat-exception-by-product-party",
                "question": "查某产品+资金方的异常处理建议",
                "query": "SELECT * FROM funding_exception_resolution WHERE product_code = :productCode AND funding_party_code = :fundingPartyCode AND enable = 'Y'",
                "intended_specification": {"caliber_id": "cal-exception-active", "metric_id": "metric-exception-count"},
                "verification": {"status": "PENDING_VALIDATION"},
                "evidence_refs": ["ev-fund-exception-export"],
            },
            {
                "pattern_id": "pat-exception-by-keyword",
                "question": "按报错关键字查异常处理建议",
                "query": "SELECT * FROM funding_exception_resolution WHERE error_keyword LIKE CONCAT('%', :keyword, '%') AND enable = 'Y'",
                "intended_specification": {"caliber_id": "cal-exception-active"},
                "verification": {"status": "PENDING_VALIDATION"},
                "evidence_refs": ["ev-fund-exception-export"],
            },
        ],
    },
    "evidence_refs": ["ev-fund-exception-import"],
    "unit_links": [],
    "assumptions": ["对接方列表来自 clientQueryFunderCodeService RPC，不落本地知识表"],
    "conflicts": [],
    "confidence": 0.7,
}

# ---------------------------------------------------------------------------
# Unit: customer-account-role
# ---------------------------------------------------------------------------
account_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-account-schema"]),
    fld("account_no", "account_no", "varchar", "账户账号", refs=["ev-account-schema"]),
    fld("default_account_flag", "default_account_flag", "varchar", "是否为默认账户", dictionary={"0": "非默认", "1": "默认"}, refs=["ev-account-schema"]),
    fld("account_type", "account_type", "varchar", "账户类型", refs=["ev-account-schema"]),
    fld("account_name", "account_name", "varchar", "账户名称", refs=["ev-account-schema"]),
    fld("bank_no", "bank_no", "varchar", "联行号", refs=["ev-account-schema"]),
    fld("bank_branch_name", "bank_branch_name", "varchar", "账户开户行", refs=["ev-account-schema"]),
    fld("status", "status", "varchar", "账户状态", refs=["ev-account-schema"]),
    fld("ref_cust_company_info", "ref_cust_company_info", "varchar", "客户账号信息", refs=["ev-account-schema"]),
    fld("db_tenant_code", "db_tenant_code", "varchar", "数据租户标识", refs=["ev-account-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-account-schema"]),
]
role_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-role-schema"]),
    fld("status", "status", "varchar", "状态", dictionary=ROLE_STATUS_DICT, refs=["ev-role-schema"]),
    fld("platform_cust_id", "platform_cust_id", "bigint", "关联平台企业ID", refs=["ev-role-schema"]),
    fld("ref_cust_company_info", "ref_cust_company_info", "varchar", "客户类型", refs=["ev-role-schema"]),
    fld("role_type", "role_type", "varchar", "角色类型", refs=["ev-role-schema"]),
    fld("db_tenant_code", "db_tenant_code", "varchar", "数据租户标识", refs=["ev-role-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-role-schema"]),
]
user_rel_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-user-rel-schema"]),
    fld("user_id", "user_id", "bigint", "用户id", refs=["ev-user-rel-schema"]),
    fld("company_id", "company_id", "bigint", "企业id", refs=["ev-user-rel-schema"]),
    fld("company_name", "company_name", "varchar", "企业名称", refs=["ev-user-rel-schema"]),
    fld("company_type", "company_type", "varchar", "企业类型", refs=["ev-user-rel-schema"]),
    fld("type_status", "type_status", "varchar", "客户角色", refs=["ev-user-rel-schema"]),
    fld("user_type", "user_type", "varchar", "联系人类型", refs=["ev-user-rel-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-user-rel-schema"]),
]

account_role_unit = {
    "unit_id": "customer-account-role",
    "revision": 1,
    "title": "客户银行账户与角色关系",
    "aliases": ["企业账户", "客户角色", "企业用户关系"],
    "domain": "customer",
    "applicability": "企业银行账户维护、客户角色新增/冻结/解冻/注销、企业用户关系生成与查询场景",
    "description": "穿透 CustAccountApplication / CustRoleApplication / SubmitCustInfoEnhanceService：账户查重与默认账户切换、角色批量新增与状态变更、按企业角色生成 cust_user_rel。",
    "content": {
        "concepts": [
            {
                "concept_id": "cust-bank-account",
                "name": "企业银行账户",
                "aliases": ["银行账户", "还款账户"],
                "definition": "企业银行账户表 cust_account_info，以主键 id 锚定。",
                "field_targets": [{"dataset": "cust_account", "field": "id"}],
                "evidence_refs": ["ev-account-schema"],
            },
            {
                "concept_id": "default-account",
                "name": "默认账户",
                "aliases": ["默认还款账户"],
                "definition": "default_account_flag=1 的企业银行账户。",
                "dictionary": {"1": "默认"},
                "field_targets": [{"dataset": "cust_account", "field": "default_account_flag"}],
                "evidence_refs": ["ev-account-set-default"],
            },
            {
                "concept_id": "cust-role",
                "name": "客户角色",
                "aliases": ["企业角色"],
                "definition": "客户角色表 cust_role_info，以主键 id 锚定。",
                "field_targets": [{"dataset": "cust_role", "field": "id"}],
                "evidence_refs": ["ev-role-schema"],
            },
            {
                "concept_id": "cust-user-rel",
                "name": "企业用户关系",
                "aliases": ["用户企业关系"],
                "definition": "企业用户关系表 cust_user_rel，以主键 id 锚定。",
                "field_targets": [{"dataset": "cust_user_rel", "field": "id"}],
                "evidence_refs": ["ev-user-rel-schema"],
            },
        ],
        "processes": [
            {
                "stage_id": "account-save",
                "name": "银行账户保存",
                "description": "保存账户前按 account_no + ref_cust_company_info 查重；保存后无默认账户时自动将当前账户置为默认。",
                "trigger": "CustAccountApplication.checkBefore / afterSave",
                "enter_conditions": ["account_no 非空", "企业存在"],
                "exit_conditions": ["账户已保存且存在默认账户"],
                "next_stages": ["account-default"],
                "data_effects": [
                    {"operation": "read", "dataset": "cust_account", "fields": ["id", "account_no", "ref_cust_company_info"], "condition": "account_no = :accountNo AND ref_cust_company_info = :companyCode", "description": "保存前查重", "evidence_refs": ["ev-account-check-before"]},
                    {"operation": "read", "dataset": "cust_account", "fields": ["id", "default_account_flag", "ref_cust_company_info"], "condition": "default_account_flag = '1' AND ref_cust_company_info = :companyCode", "description": "检查是否已有默认账户", "evidence_refs": ["ev-account-after-save"]},
                    {"operation": "insert", "dataset": "cust_account", "fields": ["account_no", "account_type", "account_name", "bank_no", "bank_branch_name", "status", "ref_cust_company_info", "db_tenant_code", "enable"], "condition": "查重通过后插入", "description": "新增企业银行账户", "evidence_refs": ["ev-account-check-before"]},
                    {"operation": "update", "dataset": "cust_account", "fields": ["default_account_flag"], "condition": "无默认账户时", "description": "将当前账户置为默认", "evidence_refs": ["ev-account-after-save"]},
                ],
                "evidence_refs": ["ev-account-check-before"],
            },
            {
                "stage_id": "account-default",
                "name": "设置默认账户",
                "description": "将指定账户置为默认，原默认账户取消默认。",
                "trigger": "CustAccountApplication.setDefaultFlag",
                "enter_conditions": ["指定账户存在"],
                "exit_conditions": ["指定账户 default_account_flag=1"],
                "next_stages": [],
                "data_effects": [
                    {"operation": "read", "dataset": "cust_account", "fields": ["id", "default_account_flag", "ref_cust_company_info"], "condition": "default_account_flag = '1' AND ref_cust_company_info = :companyCode", "description": "查旧默认账户", "evidence_refs": ["ev-account-set-default"]},
                    {"operation": "update", "dataset": "cust_account", "fields": ["default_account_flag"], "condition": "旧默认账户 id = :oldId", "description": "取消旧默认账户", "evidence_refs": ["ev-account-set-default"]},
                    {"operation": "update", "dataset": "cust_account", "fields": ["default_account_flag"], "condition": "id = :accountId", "description": "将新账户置为默认", "evidence_refs": ["ev-account-set-default"]},
                ],
                "evidence_refs": ["ev-account-set-default"],
            },
            {
                "stage_id": "role-manage",
                "name": "客户角色维护",
                "description": "角色新增：先删旧角色再批量插入并回写项目关联 company_type；状态变更：冻结/解冻/注销，或按企业批量更新非注销角色状态。",
                "trigger": "CustRoleApplication.addRoleInfo / freeze / unFreeze / logout",
                "enter_conditions": ["企业存在"],
                "exit_conditions": ["角色已保存或状态已更新"],
                "next_stages": ["user-rel-rebuild"],
                "data_effects": [
                    {"operation": "read", "dataset": "cust_role", "fields": ["id", "status", "ref_cust_company_info", "role_type"], "condition": "ref_cust_company_info = :companyCode", "description": "读企业现有角色", "evidence_refs": ["ev-role-add-role-info", "ev-role-update-status-by-company"]},
                    {"operation": "delete", "dataset": "cust_role", "fields": ["id", "ref_cust_company_info"], "condition": "ref_cust_company_info = :companyCode", "description": "新增前先删除旧角色", "evidence_refs": ["ev-role-add-role-info"]},
                    {"operation": "insert", "dataset": "cust_role", "fields": ["status", "platform_cust_id", "ref_cust_company_info", "role_type", "db_tenant_code", "enable"], "condition": "按 roleTypes 批量插入", "description": "批量保存企业角色", "evidence_refs": ["ev-role-add-role-info"]},
                    {"operation": "update", "dataset": "cust_role", "fields": ["status"], "condition": "id = :roleId 或 ref_cust_company_info = :companyCode 且 status != WRITEOFF", "description": "冻结/解冻/注销/批量状态更新", "evidence_refs": ["ev-role-status-change", "ev-role-update-status-by-company"]},
                ],
                "evidence_refs": ["ev-role-add-role-info"],
            },
            {
                "stage_id": "user-rel-rebuild",
                "name": "企业用户关系生成/查询",
                "description": "按企业角色列表和联系人列表生成 cust_user_rel；也支持按 userId+companyId+companyType 查询当前用户企业关系。",
                "trigger": "SubmitCustInfoEnhanceService.custUserRel / CustCompanyIfoEnchanceService.getCustUserRel",
                "enter_conditions": ["企业角色列表非空", "联系人列表非空"],
                "exit_conditions": ["cust_user_rel 已生成/可查询"],
                "next_stages": [],
                "data_effects": [
                    {"operation": "read", "dataset": "cust_user_rel", "fields": ["id", "user_id", "company_id", "company_type", "enable"], "condition": "user_id = :userId AND company_id = :companyId AND company_type = :companyType AND enable='Y'", "description": "查询当前用户企业关系", "evidence_refs": ["ev-user-rel-get"]},
                    {"operation": "insert", "dataset": "cust_user_rel", "fields": ["user_id", "company_id", "company_name", "company_type", "type_status", "user_type", "enable"], "condition": "按企业角色 x 联系人生成", "description": "批量生成企业用户关系", "evidence_refs": ["ev-user-rel-save"]},
                ],
                "evidence_refs": ["ev-user-rel-save"],
            },
        ],
        "datasets": [
            dset("cust_account", "cust_account_info", "企业银行账户", account_fields, refs=["ev-account-schema"]),
            dset("cust_role", "cust_role_info", "客户角色", role_fields, refs=["ev-role-schema"]),
            dset("cust_user_rel", "cust_user_rel", "企业用户关系", user_rel_fields, refs=["ev-user-rel-schema"]),
        ],
        "relationships": [
            {
                "relationship_id": "rel-account-company",
                "left": {"dataset": "cust_account", "field": "ref_cust_company_info"},
                "right": {"dataset": "company", "field": "code"},
                "relationship_type": "EQUI_JOIN",
                "cardinality": "many_to_one",
                "business_meaning": "银行账户通过企业编码关联企业主数据",
                "status": "proposed",
                "evidence_refs": ["ev-account-check-before"],
            },
            {
                "relationship_id": "rel-role-company",
                "left": {"dataset": "cust_role", "field": "ref_cust_company_info"},
                "right": {"dataset": "company", "field": "code"},
                "relationship_type": "EQUI_JOIN",
                "cardinality": "many_to_one",
                "business_meaning": "客户角色通过企业编码关联企业主数据",
                "status": "proposed",
                "evidence_refs": ["ev-role-add-role-info"],
            },
            {
                "relationship_id": "rel-user-rel-company",
                "left": {"dataset": "cust_user_rel", "field": "company_id"},
                "right": {"dataset": "company", "field": "id"},
                "relationship_type": "EQUI_JOIN",
                "cardinality": "many_to_one",
                "business_meaning": "企业用户关系通过 company_id 关联企业主数据",
                "status": "proposed",
                "evidence_refs": ["ev-user-rel-save"],
            },
        ],
        "metrics": [
            {
                "metric_id": "metric-cust-account-count",
                "name": "企业银行账户数",
                "description": "企业银行账户记录数。",
                "aggregation": "COUNT",
                "field": {"dataset": "cust_account", "field": "id"},
                "grain": [{"dataset": "cust_account", "field": "id"}],
                "filters": [],
                "evidence_refs": ["ev-account-get-by-cust"],
            },
            {
                "metric_id": "metric-cust-role-count",
                "name": "客户角色数",
                "description": "客户角色记录数。",
                "aggregation": "COUNT",
                "field": {"dataset": "cust_role", "field": "id"},
                "grain": [{"dataset": "cust_role", "field": "id"}],
                "filters": [],
                "evidence_refs": ["ev-role-add-role-info"],
            },
            {
                "metric_id": "metric-cust-user-rel-count",
                "name": "企业用户关系数",
                "description": "企业用户关系记录数。",
                "aggregation": "COUNT",
                "field": {"dataset": "cust_user_rel", "field": "id"},
                "grain": [{"dataset": "cust_user_rel", "field": "id"}],
                "filters": [],
                "evidence_refs": ["ev-user-rel-save"],
            },
        ],
        "calibers": [
            {
                "caliber_id": "cal-default-account",
                "label": "默认账户",
                "description": "default_account_flag=1 的企业银行账户。",
                "contract_fragment": {"predicate": "default_account_flag = '1'", "scope": "cust_account_info 全局定义"},
                "field_targets": [{"dataset": "cust_account", "field": "default_account_flag"}],
                "evidence_refs": ["ev-account-set-default"],
            },
            {
                "caliber_id": "cal-active-role",
                "label": "非注销客户角色",
                "description": "status != WRITEOFF 且 enable=Y 的客户角色。",
                "contract_fragment": {"predicate": "status != 'WRITEOFF' AND enable = 'Y'", "scope": "cust_role_info 全局定义"},
                "field_targets": [{"dataset": "cust_role", "field": "status"}, {"dataset": "cust_role", "field": "enable"}],
                "evidence_refs": ["ev-role-update-status-by-company"],
            },
            {
                "caliber_id": "cal-user-rel-scope",
                "label": "企业用户关系范围",
                "description": "按 userId + companyId + companyType 唯一定位企业用户关系。",
                "contract_fragment": {"predicate": "user_id = :userId AND company_id = :companyId AND company_type = :companyType", "scope": "getCustUserRel 查询范围"},
                "field_targets": [
                    {"dataset": "cust_user_rel", "field": "user_id"},
                    {"dataset": "cust_user_rel", "field": "company_id"},
                    {"dataset": "cust_user_rel", "field": "company_type"},
                ],
                "evidence_refs": ["ev-user-rel-get"],
            },
        ],
        "domain_rules": [
            {
                "rule_id": "rule-account-unique",
                "label": "企业账户不能重复添加",
                "content": "同一 account_no + ref_cust_company_info 已存在时禁止重复添加。",
                "applicability": "CustAccountApplication.checkBefore",
                "query_impact": "查询企业账户时 account_no 在企业内唯一，可按 account_no 定位唯一账户。",
                "field_targets": [
                    {"dataset": "cust_account", "field": "account_no"},
                    {"dataset": "cust_account", "field": "ref_cust_company_info"},
                ],
                "evidence_refs": ["ev-account-check-before"],
            },
            {
                "rule_id": "rule-default-account-switch",
                "label": "默认账户唯一切换",
                "content": "设置默认账户时先将原默认账户 default_account_flag 置 0，再将目标账户置 1。",
                "applicability": "CustAccountApplication.setDefaultFlag",
                "query_impact": "同一企业下默认账户始终唯一；查询默认账户时加 default_account_flag='1' 即可。",
                "field_targets": [{"dataset": "cust_account", "field": "default_account_flag"}],
                "evidence_refs": ["ev-account-set-default"],
            },
            {
                "rule_id": "rule-role-add-delete-first",
                "label": "新增角色先删旧角色",
                "content": "新增客户角色时先按 ref_cust_company_info 删除旧角色，再批量插入新角色，并同步回写 cust_project_rel.company_type 与项目联系人。",
                "applicability": "CustRoleApplication.addRoleInfo",
                "query_impact": "企业当前角色以最新一次保存为准；角色变更会联动客户项目关系 company_type。",
                "field_targets": [{"dataset": "cust_role", "field": "ref_cust_company_info"}],
                "evidence_refs": ["ev-role-add-role-info"],
            },
            {
                "rule_id": "rule-account-delete-by-primary-key",
                "label": "删除其他账户使用主键批量删除",
                "content": "先按企业 code 查询需删除账户的 id 列表，再按主键 removeBatchByIds，避免非主键条件删除导致死锁。",
                "applicability": "CustAccountApplication.deleteOtherCustAccount",
                "query_impact": "删除其他账户后企业只保留指定账户；查询时不会出现死锁导致的中间态。",
                "field_targets": [{"dataset": "cust_account", "field": "id"}],
                "evidence_refs": ["ev-account-delete-other"],
            },
        ],
        "verified_query_patterns": [
            {
                "pattern_id": "pat-account-by-company",
                "question": "按企业查银行账户",
                "query": "SELECT * FROM cust_account_info WHERE ref_cust_company_info = :companyCode AND enable = 'Y'",
                "intended_specification": {"metric_id": "metric-cust-account-count"},
                "verification": {"status": "PENDING_VALIDATION"},
                "evidence_refs": ["ev-account-get-by-cust"],
            },
            {
                "pattern_id": "pat-role-by-company",
                "question": "按企业查客户角色",
                "query": "SELECT * FROM cust_role_info WHERE ref_cust_company_info = :companyCode AND enable = 'Y'",
                "intended_specification": {"caliber_id": "cal-active-role"},
                "verification": {"status": "PENDING_VALIDATION"},
                "evidence_refs": ["ev-role-add-role-info"],
            },
            {
                "pattern_id": "pat-user-rel-current",
                "question": "查当前用户的企业关系",
                "query": "SELECT * FROM cust_user_rel WHERE user_id = :userId AND company_id = :companyId AND company_type = :companyType AND enable = 'Y'",
                "intended_specification": {"caliber_id": "cal-user-rel-scope"},
                "verification": {"status": "PENDING_VALIDATION"},
                "evidence_refs": ["ev-user-rel-get"],
            },
        ],
    },
    "evidence_refs": ["ev-account-check-before"],
    "unit_links": [],
    "assumptions": ["用户系统侧角色关系（SysCustUserRelDO）在外部系统，本地 cust_user_rel 为业务侧冗余关系"],
    "conflicts": [],
    "confidence": 0.7,
}

# ---------------------------------------------------------------------------
# Unit: tenant-product
# ---------------------------------------------------------------------------
tenant_product_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-tenant-product-schema"]),
    fld("name", "name", "varchar", "名称", refs=["ev-tenant-product-schema"]),
    fld("platform_product_id", "platform_product_id", "bigint", "平台产品id", refs=["ev-tenant-product-schema"]),
    fld("tenant_id", "tenant_id", "bigint", "租户id", refs=["ev-tenant-product-schema"]),
    fld("open_status", "open_status", "varchar", "产品开通状态", dictionary=OPEN_STATUS_DICT, refs=["ev-tenant-product-schema"]),
    fld("platform_product_code", "platform_product_code", "varchar", "平台产品编号", refs=["ev-tenant-product-schema"]),
    fld("ref_tenant_product_tenant_setting_config", "ref_tenant_product_tenant_setting_config", "varchar", "租户-产品", refs=["ev-tenant-product-schema"]),
    fld("ref_tenant_product_project_code", "ref_tenant_product_project_code", "varchar", "租户产品-平台产品", refs=["ev-tenant-product-schema"]),
    fld("db_tenant_code", "db_tenant_code", "varchar", "数据租户标识", refs=["ev-tenant-product-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-tenant-product-schema"]),
]
platform_product_min_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-platform-product-schema"]),
    fld("product_code", "product_code", "varchar", "产品编码", refs=["ev-platform-product-schema"]),
    fld("name", "name", "varchar", "名称", refs=["ev-platform-product-schema"]),
]
cust_role_product_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-platform-product-cust-role-schema"]),
    fld("product_code", "product_code", "varchar", "产品编码", refs=["ev-platform-product-cust-role-schema"]),
    fld("company_type_code", "company_type_code", "varchar", "企业角色编码", refs=["ev-platform-product-cust-role-schema"]),
    fld("company_type_name", "company_type_name", "varchar", "企业角色名称", refs=["ev-platform-product-cust-role-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-platform-product-cust-role-schema"]),
]

tenant_product_unit = {
    "unit_id": "tenant-product",
    "revision": 1,
    "title": "租户产品开通",
    "aliases": ["租户产品", "产品开通"],
    "domain": "product",
    "applicability": "租户产品创建/开通/取消/按企业角色筛选适配产品的场景",
    "description": "穿透 TenantProductApplication 与 TenantProductDomainService：租户创建产品（每租户每平台产品唯一）、开通/取消（校验关联项目/企业）、按企业角色过滤适配产品。",
    "content": {
        "concepts": [
            {
                "concept_id": "tenant-product",
                "name": "租户产品",
                "aliases": ["开通产品"],
                "definition": "租户产品表 tenant_product，以主键 id 锚定。",
                "field_targets": [{"dataset": "tenant_product", "field": "id"}],
                "evidence_refs": ["ev-tenant-product-schema"],
            },
            {
                "concept_id": "tenant-product-open",
                "name": "产品已开通",
                "aliases": ["已开通产品"],
                "definition": "租户产品 open_status=Y。",
                "dictionary": {"Y": "已开通"},
                "field_targets": [{"dataset": "tenant_product", "field": "open_status"}],
                "evidence_refs": ["ev-tenant-product-domain-active"],
            },
            {
                "concept_id": "tenant-product-opening",
                "name": "产品开通中",
                "aliases": ["开通中产品"],
                "definition": "租户产品 open_status=P（ACFLOW/ORDER 等多级回调产品）。",
                "dictionary": {"P": "开通中"},
                "field_targets": [{"dataset": "tenant_product", "field": "open_status"}],
                "evidence_refs": ["ev-tenant-product-active"],
            },
            {
                "concept_id": "product-cust-role",
                "name": "产品适配企业角色",
                "aliases": ["产品角色适配"],
                "definition": "平台产品与客户角色适配关系 platform_product_cust_role，以主键 id 锚定。",
                "field_targets": [{"dataset": "platform_product_cust_role", "field": "id"}],
                "evidence_refs": ["ev-platform-product-cust-role-schema"],
            },
        ],
        "processes": [
            {
                "stage_id": "tenant-product-create",
                "name": "创建租户产品",
                "description": "按租户+平台产品创建租户产品；已存在则直接返回。从平台产品复制产品字段并保存。",
                "trigger": "TenantProductApplication.create / syncTenantProduct",
                "enter_conditions": ["tenantId 与 platformProductId 非空"],
                "exit_conditions": ["tenant_product 已保存"],
                "next_stages": ["tenant-product-active"],
                "data_effects": [
                    {"operation": "read", "dataset": "platform_product", "fields": ["id", "product_code", "name"], "condition": "id = :platformProductId 或 product_code = :platformProductCode", "description": "读平台产品基础信息", "evidence_refs": ["ev-tenant-product-create", "ev-tenant-product-domain-create"]},
                    {"operation": "read", "dataset": "tenant_product", "fields": ["id", "tenant_id", "platform_product_code", "platform_product_id"], "condition": "tenant_id = :tenantId AND platform_product_code = :platformProductCode", "description": "校验是否已存在租户产品", "evidence_refs": ["ev-tenant-product-domain-create"]},
                    {"operation": "upsert", "dataset": "tenant_product", "fields": ["name", "platform_product_id", "tenant_id", "open_status", "platform_product_code", "ref_tenant_product_tenant_setting_config", "ref_tenant_product_project_code", "db_tenant_code", "enable"], "condition": "不存在则插入，存在则更新", "description": "创建/更新租户产品", "evidence_refs": ["ev-tenant-product-domain-create"]},
                ],
                "evidence_refs": ["ev-tenant-product-create"],
            },
            {
                "stage_id": "tenant-product-active",
                "name": "开通租户产品",
                "description": "开通产品：已开通直接返回；ACFLOW/ORDER 等多级回调产品先置 P，其余置 Y 并推送开通事件。",
                "trigger": "TenantProductApplication.activeAndNotify",
                "enter_conditions": ["tenant_product 存在"],
                "exit_conditions": ["open_status=Y 或 P"],
                "next_stages": ["tenant-product-query"],
                "data_effects": [
                    {"operation": "read", "dataset": "tenant_product", "fields": ["id", "tenant_id", "open_status", "platform_product_code", "platform_product_id"], "condition": "id = :id", "description": "读租户产品当前开通状态", "evidence_refs": ["ev-tenant-product-active"]},
                    {"operation": "update", "dataset": "tenant_product", "fields": ["open_status"], "condition": "ACFLOW/ORDER 产品置 P，其他置 Y", "description": "更新产品开通状态", "evidence_refs": ["ev-tenant-product-active", "ev-tenant-product-domain-active"]},
                ],
                "evidence_refs": ["ev-tenant-product-active"],
            },
            {
                "stage_id": "tenant-product-cancel",
                "name": "取消开通租户产品",
                "description": "取消开通前校验是否已有关联项目/企业，有关联不允许取消；通过后 open_status 置 N。",
                "trigger": "TenantProductApplication.cancel -> TenantProductDomainService.cancel",
                "enter_conditions": ["tenant_product 存在"],
                "exit_conditions": ["open_status=N 或校验不通过"],
                "next_stages": [],
                "data_effects": [
                    {"operation": "read", "dataset": "tenant_product", "fields": ["id", "tenant_id", "platform_product_id", "open_status"], "condition": "id = :id", "description": "读租户产品", "evidence_refs": ["ev-tenant-product-domain-cancel"]},
                    {"operation": "update", "dataset": "tenant_product", "fields": ["open_status"], "condition": "无关联项目/企业时", "description": "取消开通，open_status=N", "evidence_refs": ["ev-tenant-product-domain-cancel"]},
                ],
                "evidence_refs": ["ev-tenant-product-cancel"],
            },
            {
                "stage_id": "tenant-product-query",
                "name": "按企业角色查询适配产品",
                "description": "查询租户全部产品，并按 platform_product_cust_role 过滤出指定企业角色可开通的产品。",
                "trigger": "TenantProductApplication.allProductByTenantAndCustType",
                "enter_conditions": ["tenantCode 非空", "custCompanyType 非空"],
                "exit_conditions": ["返回适配产品列表"],
                "next_stages": [],
                "data_effects": [
                    {"operation": "read", "dataset": "tenant_product", "fields": ["id", "name", "platform_product_id", "tenant_id", "open_status", "platform_product_code", "enable"], "condition": "tenant_id = :tenantId 或 db_tenant_code = :tenantCode", "description": "读租户全部产品", "evidence_refs": ["ev-tenant-product-all-by-cust-type"]},
                    {"operation": "read", "dataset": "platform_product", "fields": ["id", "product_code", "name"], "condition": "1=1", "description": "读平台产品名称映射", "evidence_refs": ["ev-tenant-product-all-by-cust-type"]},
                    {"operation": "read", "dataset": "platform_product_cust_role", "fields": ["id", "product_code", "company_type_code", "company_type_name", "enable"], "condition": "company_type_code = :custCompanyType AND enable='Y'", "description": "按企业角色读产品适配关系并过滤", "evidence_refs": ["ev-tenant-product-all-by-cust-type"]},
                ],
                "evidence_refs": ["ev-tenant-product-all-by-cust-type"],
            },
        ],
        "datasets": [
            dset("tenant_product", "tenant_product", "租户产品", tenant_product_fields, refs=["ev-tenant-product-schema"]),
            dset("platform_product_cust_role", "platform_product_cust_role", "平台产品-企业角色适配", cust_role_product_fields, refs=["ev-platform-product-cust-role-schema"]),
            dset("platform_product", "platform_product", "平台产品", platform_product_min_fields, refs=["ev-platform-product-schema"]),
        ],
        "relationships": [
            {
                "relationship_id": "rel-tenant-product-platform-product",
                "left": {"dataset": "tenant_product", "field": "platform_product_id"},
                "right": {"dataset": "platform_product", "field": "id"},
                "relationship_type": "EQUI_JOIN",
                "cardinality": "many_to_one",
                "business_meaning": "租户产品通过 platform_product_id 关联平台产品",
                "status": "proposed",
                "evidence_refs": ["ev-tenant-product-domain-create"],
            },
            {
                "relationship_id": "rel-tenant-product-cust-role-product",
                "left": {"dataset": "platform_product_cust_role", "field": "product_code"},
                "right": {"dataset": "platform_product", "field": "product_code"},
                "relationship_type": "EQUI_JOIN",
                "cardinality": "many_to_one",
                "business_meaning": "产品角色适配通过 product_code 关联平台产品",
                "status": "proposed",
                "evidence_refs": ["ev-tenant-product-all-by-cust-type"],
            },
        ],
        "metrics": [
            {
                "metric_id": "metric-tenant-product-count",
                "name": "租户产品数",
                "description": "租户产品记录数。",
                "aggregation": "COUNT",
                "field": {"dataset": "tenant_product", "field": "id"},
                "grain": [{"dataset": "tenant_product", "field": "id"}],
                "filters": [],
                "evidence_refs": ["ev-tenant-product-all-by-cust-type"],
            },
            {
                "metric_id": "metric-tenant-product-open-count",
                "name": "已开通租户产品数",
                "description": "open_status=Y 的租户产品数。",
                "aggregation": "COUNT",
                "field": {"dataset": "tenant_product", "field": "id"},
                "grain": [{"dataset": "tenant_product", "field": "id"}],
                "filters": [{"field": "open_status", "op": "=", "value": "Y"}],
                "evidence_refs": ["ev-tenant-product-domain-active"],
            },
            {
                "metric_id": "metric-product-cust-role-count",
                "name": "产品适配企业角色数",
                "description": "产品-企业角色适配记录数。",
                "aggregation": "COUNT",
                "field": {"dataset": "platform_product_cust_role", "field": "id"},
                "grain": [{"dataset": "platform_product_cust_role", "field": "id"}],
                "filters": [],
                "evidence_refs": ["ev-tenant-product-all-by-cust-type"],
            },
        ],
        "calibers": [
            {
                "caliber_id": "cal-tenant-product-open",
                "label": "已开通产品",
                "description": "open_status=Y 的租户产品。",
                "contract_fragment": {"predicate": "open_status = 'Y'", "scope": "tenant_product 全局定义"},
                "field_targets": [{"dataset": "tenant_product", "field": "open_status"}],
                "evidence_refs": ["ev-tenant-product-domain-active"],
            },
            {
                "caliber_id": "cal-tenant-product-opening",
                "label": "开通中产品",
                "description": "open_status=P 的租户产品（ACFLOW/ORDER 等多级回调产品）。",
                "contract_fragment": {"predicate": "open_status = 'P'", "scope": "tenant_product 全局定义"},
                "field_targets": [{"dataset": "tenant_product", "field": "open_status"}],
                "evidence_refs": ["ev-tenant-product-active"],
            },
            {
                "caliber_id": "cal-tenant-product-not-open",
                "label": "未开通产品",
                "description": "open_status=N 的租户产品。",
                "contract_fragment": {"predicate": "open_status = 'N'", "scope": "tenant_product 全局定义"},
                "field_targets": [{"dataset": "tenant_product", "field": "open_status"}],
                "evidence_refs": ["ev-tenant-product-domain-cancel"],
            },
            {
                "caliber_id": "cal-product-cust-role-scope",
                "label": "产品适配企业角色范围",
                "description": "按 company_type_code 过滤指定企业角色可开通的产品编码集合。",
                "contract_fragment": {"predicate": "company_type_code = :custCompanyType AND enable = 'Y'", "scope": "platform_product_cust_role"},
                "field_targets": [{"dataset": "platform_product_cust_role", "field": "company_type_code"}],
                "evidence_refs": ["ev-tenant-product-all-by-cust-type"],
            },
        ],
        "domain_rules": [
            {
                "rule_id": "rule-tenant-product-unique",
                "label": "每租户每平台产品只保留一条",
                "content": "创建租户产品时按 tenantId + platformProductCode 查重，已存在直接返回，不允许重复开通。",
                "applicability": "TenantProductDomainService.create",
                "query_impact": "tenant_product 在 (tenant_id, platform_product_code) 维度唯一，查询无需去重。",
                "field_targets": [
                    {"dataset": "tenant_product", "field": "tenant_id"},
                    {"dataset": "tenant_product", "field": "platform_product_code"},
                ],
                "evidence_refs": ["ev-tenant-product-domain-create"],
            },
            {
                "rule_id": "rule-tenant-product-cancel-check",
                "label": "有关联项目或企业不允许取消开通",
                "content": "取消开通前检查是否有生效项目或已开通企业，存在任一关联则拒绝取消。",
                "applicability": "TenantProductDomainService.checkOnTheWay",
                "query_impact": "查询可取消产品时需排除已关联项目/企业的产品；取消操作不是纯状态更新。",
                "field_targets": [{"dataset": "tenant_product", "field": "open_status"}],
                "evidence_refs": ["ev-tenant-product-check-on-way"],
            },
            {
                "rule_id": "rule-tenant-product-acflow-order-pending",
                "label": "ACFLOW/ORDER 产品开通先置 P",
                "content": "ACFLOW 或 ORDER 平台产品开通时先置 open_status=P，多级回调后置为成功；其他产品直接置 Y。",
                "applicability": "TenantProductApplication.activeAndNotify",
                "query_impact": "查询开通中产品时，ACFLOW/ORDER 产品会在 P 状态停留，需按 open_status=P 识别。",
                "field_targets": [{"dataset": "tenant_product", "field": "open_status"}, {"dataset": "tenant_product", "field": "platform_product_code"}],
                "evidence_refs": ["ev-tenant-product-active"],
            },
        ],
        "verified_query_patterns": [
            {
                "pattern_id": "pat-tenant-product-open-by-tenant",
                "question": "按租户查已开通产品",
                "query": "SELECT * FROM tenant_product WHERE tenant_id = :tenantId AND open_status = 'Y' AND enable = 'Y'",
                "intended_specification": {"caliber_id": "cal-tenant-product-open", "metric_id": "metric-tenant-product-open-count"},
                "verification": {"status": "PENDING_VALIDATION"},
                "evidence_refs": ["ev-tenant-product-all-by-cust-type"],
            },
            {
                "pattern_id": "pat-tenant-product-by-cust-type",
                "question": "按企业角色查可开通产品",
                "query": "SELECT tp.* FROM tenant_product tp JOIN platform_product_cust_role pcr ON pcr.product_code = tp.platform_product_code WHERE tp.tenant_id = :tenantId AND pcr.company_type_code = :custCompanyType AND pcr.enable = 'Y'",
                "intended_specification": {"caliber_id": "cal-product-cust-role-scope"},
                "verification": {"status": "PENDING_VALIDATION"},
                "evidence_refs": ["ev-tenant-product-all-by-cust-type"],
            },
        ],
    },
    "evidence_refs": ["ev-tenant-product-create"],
    "unit_links": [],
    "assumptions": ["平台产品主数据 platform_product 由 onboarding 单元权威声明，本单元最小声明 id/product_code/name"],
    "conflicts": [],
    "confidence": 0.7,
}

# ---------------------------------------------------------------------------
# write unit files
# ---------------------------------------------------------------------------
(units_dir := PKG / "units").mkdir(exist_ok=True)

def write_yaml(path, data):
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")

write_yaml(units_dir / "funding-exception-resolution.yaml", exception_unit)
write_yaml(units_dir / "customer-account-role.yaml", account_role_unit)
write_yaml(units_dir / "tenant-product.yaml", tenant_product_unit)

# ---------------------------------------------------------------------------
# update manifest
# ---------------------------------------------------------------------------
manifest_path = PKG / "knowledge-package.yaml"
manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
existing_ids = {e["evidence_id"] for e in manifest["evidence"]}
for e in new_evidence:
    if e["evidence_id"] not in existing_ids:
        manifest["evidence"].append(e)
        existing_ids.add(e["evidence_id"])

new_unit_paths = [
    "units/funding-exception-resolution.yaml",
    "units/customer-account-role.yaml",
    "units/tenant-product.yaml",
]
for p in new_unit_paths:
    if p not in manifest["units"]:
        manifest["units"].append(p)

write_yaml(manifest_path, manifest)

# ---------------------------------------------------------------------------
# update relationships.yaml
# ---------------------------------------------------------------------------
rel_path = PKG / "relationships.yaml"
rel_doc = yaml.safe_load(rel_path.read_text(encoding="utf-8"))
rels = rel_doc["relationships"]
new_rels = [
    {"left_table": "cust_account_info", "left_field": "ref_cust_company_info", "right_table": "cust_company_info", "right_field": "code", "evidence": "read-flow/write-flow:CustAccountApplication.java:72,132", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "cust_role_info", "left_field": "ref_cust_company_info", "right_table": "cust_company_info", "right_field": "code", "evidence": "write-flow:CustRoleApplication.java:143", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "cust_user_rel", "left_field": "company_id", "right_table": "cust_company_info", "right_field": "id", "evidence": "write-flow:SubmitCustInfoEnhanceService.java:174", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_product", "left_field": "platform_product_id", "right_table": "platform_product", "right_field": "id", "evidence": "write-flow:TenantProductDomainService.java:147", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "platform_product_cust_role", "left_field": "product_code", "right_table": "platform_product", "right_field": "product_code", "evidence": "read-flow:TenantProductApplication.java:132-133", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
]
seen = {(r["left_table"], r["left_field"], r["right_table"], r["right_field"]) for r in rels}
for r in new_rels:
    key = (r["left_table"], r["left_field"], r["right_table"], r["right_field"])
    if key not in seen:
        rels.append(r)
        seen.add(key)
write_yaml(rel_path, rel_doc)

print("added 3 units, evidence total", len(manifest["evidence"]), "units", len(manifest["units"]), "relationships", len(rels))
