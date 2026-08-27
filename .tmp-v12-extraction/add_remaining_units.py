# -*- coding: utf-8 -*-
"""Add remaining units to pplatform-web-v12 so every active table is covered."""
import yaml
from pathlib import Path

PKG = Path("/Users/fanjunwei/Projects/SQLBot/data/knowledge-packages/v12")
SRC = "src-pplatform-web"

def ev(eid, kind, locator, claim):
    return {"evidence_id": eid, "source_id": SRC, "evidence_kind": kind, "locator": locator, "claim": claim}

def fld(field_id, name, dtype, desc, dictionary=None, refs=None):
    d = {"field_id": field_id, "name": name, "data_type": dtype, "description": desc}
    if dictionary:
        d["dictionary"] = dictionary
    if refs:
        d["evidence_refs"] = refs
    return d

def dset(dataset_id, name, desc, fields, refs=None):
    d = {"dataset_id": dataset_id, "name": name, "description": desc, "database": "lowcode_pplatform", "inactive": False, "fields": fields}
    if refs:
        d["evidence_refs"] = refs
    return d

def de(op, dataset, fields, condition, desc, refs):
    return {"operation": op, "dataset": dataset, "fields": fields, "condition": condition, "description": desc, "evidence_refs": refs}

def concept(cid, name, definition, dataset, field, dictionary=None, aliases=None, refs=None):
    d = {"concept_id": cid, "name": name, "aliases": aliases or [], "definition": definition,
         "dictionary": dictionary or {}, "field_targets": [{"dataset": dataset, "field": field}],
         "evidence_refs": refs or []}
    return d

def stage(sid, name, desc, trigger, effects, next_stages=None, refs=None):
    return {"stage_id": sid, "name": name, "description": desc, "trigger": trigger,
            "enter_conditions": [], "exit_conditions": [], "next_stages": next_stages or [],
            "data_effects": effects, "evidence_refs": refs or []}

def caliber(cid, label, desc, predicate, targets, refs):
    return {"caliber_id": cid, "label": label, "description": desc,
            "contract_fragment": {"predicate": predicate, "scope": desc}, "field_targets": targets,
            "evidence_refs": refs}

def metric(mid, name, desc, dataset, field, refs, filters=None):
    return {"metric_id": mid, "name": name, "description": desc, "aggregation": "COUNT",
            "field": {"dataset": dataset, "field": field}, "grain": [{"dataset": dataset, "field": field}],
            "filters": filters or [], "evidence_refs": refs}

def rule(rid, label, content, applicability, query_impact, targets, refs):
    return {"rule_id": rid, "label": label, "content": content, "applicability": applicability,
            "query_impact": query_impact, "field_targets": targets, "evidence_refs": refs}

def pattern(pid, question, query, spec, refs):
    return {"pattern_id": pid, "question": question, "query": query,
            "intended_specification": spec, "verification": {"status": "PENDING_VALIDATION"}, "evidence_refs": refs}

def unit(uid, title, domain, applicability, desc, concepts, processes, datasets, metrics, calibers, rules, patterns, assumptions=None):
    return {"unit_id": uid, "revision": 1, "title": title, "aliases": [], "domain": domain,
            "applicability": applicability, "description": desc,
            "content": {"concepts": concepts, "processes": processes, "datasets": datasets,
                        "relationships": [], "metrics": metrics, "calibers": calibers,
                        "domain_rules": rules, "verified_query_patterns": patterns},
            "evidence_refs": [], "unit_links": [], "assumptions": assumptions or [], "conflicts": [], "confidence": 0.7}

new_evidence = []
new_units = []

# =========================================================================
# 1. customer-change 客户变更
# =========================================================================
new_evidence += [
    ev("ev-cust-change-cfg-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustChangeCfgDO.java", "cust_change_cfg 表字段定义"),
    ev("ev-cust-change-record-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustChangeRecordDO.java", "cust_change_record 表字段定义"),
    ev("ev-cust-oper-change-record-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustOperChangeRecordDO.java", "cust_oper_change_record 表字段定义"),
    ev("ev-cust-change-cfg-list", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustChangeApplication.java:68-109", "按端类型/认证方式/客户类型/是否总公司查询变更配置项"),
    ev("ev-cust-change-record-write", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustCompanyInfoApplication.java:7396-7417", "创建/更新客户变更记录并同步运营中台"),
    ev("ev-cust-change-record-query", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustCompanyInfoApplication.java:8166-8178", "按企业+状态+变更类型查询变更记录"),
    ev("ev-cust-oper-change-record-query", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/OperChangeRecordApplication.java:41-49", "按联系人 id 查询运营变更记录"),
]
cc_cfg_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-change-cfg-schema"]),
    fld("item_code","item_code","varchar","变更项编码", refs=["ev-cust-change-cfg-schema"]),
    fld("plat_item","plat_item","varchar","平台变更项", refs=["ev-cust-change-cfg-schema"]),
    fld("oper_item","oper_item","varchar","运营中台变更项", refs=["ev-cust-change-cfg-schema"]),
    fld("cust_type","cust_type","varchar","客户类型", refs=["ev-cust-change-cfg-schema"]),
    fld("identify_style","identify_style","varchar","认证方式", refs=["ev-cust-change-cfg-schema"]),
    fld("client_type","client_type","varchar","端类型", refs=["ev-cust-change-cfg-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-change-cfg-schema"]),
]
cc_record_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-change-record-schema"]),
    fld("cust_id","cust_id","bigint","客户记录id", refs=["ev-cust-change-record-schema"]),
    fld("alter_type","alter_type","varchar","变更类型", refs=["ev-cust-change-record-schema"]),
    fld("status","status","varchar","变更状态", refs=["ev-cust-change-record-schema"]),
    fld("alter_mode","alter_mode","varchar","变更方式", refs=["ev-cust-change-record-schema"]),
    fld("oper_app_no","oper_app_no","varchar","运营中台流程编号", refs=["ev-cust-change-record-schema"]),
    fld("need_cust_confirm","need_cust_confirm","varchar","是否需要客户确认", refs=["ev-cust-change-record-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-change-record-schema"]),
]
oper_record_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-oper-change-record-schema"]),
    fld("person_id","person_id","bigint","企业联系人id", refs=["ev-cust-oper-change-record-schema"]),
    fld("company_id","company_id","bigint","企业ID", refs=["ev-cust-oper-change-record-schema"]),
    fld("before_operator_id","before_operator_id","varchar","变更前运营人员ID", refs=["ev-cust-oper-change-record-schema"]),
    fld("after_operator_id","after_operator_id","varchar","变更后运营人员ID", refs=["ev-cust-oper-change-record-schema"]),
    fld("change_type","change_type","varchar","变更类型", refs=["ev-cust-oper-change-record-schema"]),
    fld("change_reason","change_reason","varchar","变更原因", refs=["ev-cust-oper-change-record-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-oper-change-record-schema"]),
]
new_units.append(unit(
    "customer-change", "客户变更", "customer",
    "企业关键/非关键信息变更配置、变更记录与运营人员变更记录场景",
    "穿透 CustChangeApplication 查询变更配置，CustCompanyInfoApplication 创建/更新变更记录，OperChangeRecordApplication 查询运营变更记录。",
    [
        concept("cust-change-cfg","客户变更配置","企业变更项配置 cust_change_cfg","cust_change_cfg","id",refs=["ev-cust-change-cfg-schema"]),
        concept("cust-change-record","客户变更记录","企业变更记录 cust_change_record","cust_change_record","id",refs=["ev-cust-change-record-schema"]),
        concept("cust-oper-change-record","运营变更记录","企业联系人运营人员变更记录 cust_oper_change_record","cust_oper_change_record","id",refs=["ev-cust-oper-change-record-schema"]),
    ],
    [
        stage("change-config-query","变更配置查询","按端类型/认证方式/客户类型/是否总公司查询变更项配置","CustChangeApplication.list",
             [de("read","cust_change_cfg",["id","item_code","plat_item","oper_item","cust_type","identify_style","client_type","enable"],"client_type=:clientType AND identify_style=:identifyStyle AND cust_type=:custType AND enable='Y'","读变更项配置",["ev-cust-change-cfg-list"])],
             next_stages=["change-record-write"], refs=["ev-cust-change-cfg-list"]),
        stage("change-record-write","变更记录写入","创建/更新企业变更记录并同步运营中台","CustCompanyInfoApplication 变更流程",
             [de("read","cust_change_record",["id","cust_id","alter_type","status","enable"],"cust_id=:companyId AND status != 'CUST_CHECK_PASS'","查在途变更记录",["ev-cust-change-record-write"]),
              de("upsert","cust_change_record",["cust_id","alter_type","status","alter_mode","oper_app_no","need_cust_confirm","enable"],"变更流程创建/更新","保存企业变更记录",["ev-cust-change-record-write"])],
             next_stages=["oper-change-query"], refs=["ev-cust-change-record-write"]),
        stage("oper-change-query","运营人员变更记录查询","按联系人 id 查询运营人员变更记录","OperChangeRecordApplication.queryByPersonId",
             [de("read","cust_oper_change_record",["id","person_id","company_id","before_operator_id","after_operator_id","change_type","change_reason","enable"],"person_id=:personId AND enable='Y' ORDER BY create_time DESC","读运营人员变更记录",["ev-cust-oper-change-record-query"])],
             refs=["ev-cust-oper-change-record-query"]),
    ],
    [
        dset("cust_change_cfg","cust_change_cfg","客户变更项配置",cc_cfg_fields,refs=["ev-cust-change-cfg-schema"]),
        dset("cust_change_record","cust_change_record","客户变更记录",cc_record_fields,refs=["ev-cust-change-record-schema"]),
        dset("cust_oper_change_record","cust_oper_change_record","运营人员变更记录",oper_record_fields,refs=["ev-cust-oper-change-record-schema"]),
    ],
    [
        metric("metric-cust-change-record-count","客户变更记录数","企业变更记录数","cust_change_record","id",["ev-cust-change-record-write"]),
        metric("metric-cust-oper-change-record-count","运营人员变更记录数","联系人运营人员变更记录数","cust_oper_change_record","id",["ev-cust-oper-change-record-query"]),
    ],
    [
        caliber("cal-cust-change-inflight","在途变更","status 非 CUST_CHECK_PASS/REJECT 的变更记录视为在途","status NOT IN ('CUST_CHECK_PASS','CUST_CHECK_REJECT')",[{"dataset":"cust_change_record","field":"status"}],["ev-cust-change-record-write"]),
        caliber("cal-cust-change-active-config","生效变更配置","enable=Y 的变更项配置","enable = 'Y'",[{"dataset":"cust_change_cfg","field":"enable"}],["ev-cust-change-cfg-list"]),
    ],
    [
        rule("rule-change-config-match","变更配置按客户维度精确匹配","变更配置按 clientType + identifyStyle + custType + headCompany 维度匹配，headCompany 为空时也回退查询非总公司配置。","CustChangeApplication.list","查询企业可变更项时必须带上端类型、认证方式、客户类型和是否总公司四个维度。",[{"dataset":"cust_change_cfg","field":"client_type"},{"dataset":"cust_change_cfg","field":"cust_type"},{"dataset":"cust_change_cfg","field":"identify_style"}],["ev-cust-change-cfg-list"]),
        rule("rule-change-record-status","变更记录审核状态流转","变更记录 status 在 CUST_CHECK_* 审核状态间流转，查询增加企业角色时只统计 status=CUST_CHECK_PASS 的记录。","CustCompanyInfoApplication 变更记录写入","查询已生效变更时按 status=CUST_CHECK_PASS 过滤。",[{"dataset":"cust_change_record","field":"status"}],["ev-cust-change-record-write"]),
    ],
    [
        pattern("pat-change-config-list","查企业可变更项配置","SELECT * FROM cust_change_cfg WHERE client_type=:clientType AND identify_style=:identifyStyle AND cust_type=:custType AND enable='Y'",{"caliber_id":"cal-cust-change-active-config"},["ev-cust-change-cfg-list"]),
        pattern("pat-change-record-by-cust","查企业变更记录","SELECT * FROM cust_change_record WHERE cust_id=:custId AND enable='Y'",{"caliber_id":"cal-cust-change-inflight"},["ev-cust-change-record-write"]),
    ],
    assumptions=["变更配置项通过运营中台同步，本地只读配置"],
))

# =========================================================================
# 2. ca-certification CA 认证/实名认证
# =========================================================================
new_evidence += [
    ev("ev-ca-cert-info-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CaCertificationInfoDO.java", "ca_certification_info 表字段定义"),
    ev("ev-cust-cert-info-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustCertificationInfoDO.java", "cust_certification_info 表字段定义"),
    ev("ev-ca-cert-create", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:125-223", "创建/查询 CA 认证记录并更新协议通知"),
    ev("ev-ca-cert-submit", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:418-506", "提交认证到签章中心并更新 submit_status"),
    ev("ev-ca-cert-mark-failed", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:519-540", "失败时标记 submit_status=FAIL"),
    ev("ev-cust-cert-face-query", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java:124-135", "按 custId 查询人脸认证快照"),
]
ca_cert_fields = [
    fld("id","id","bigint","表主键", refs=["ev-ca-cert-info-schema"]),
    fld("cust_id","cust_id","bigint","企业Id", refs=["ev-ca-cert-info-schema"]),
    fld("cust_type","cust_type","varchar","PERSON / COMPANY", refs=["ev-ca-cert-info-schema"]),
    fld("submit_status","submit_status","varchar","PENDING / SUCCESS / FAIL", dictionary={"PENDING":"待提交","SUCCESS":"成功","FAIL":"失败"}, refs=["ev-ca-cert-info-schema"]),
    fld("sign_platform_result","sign_platform_result","varchar","中台返回结果", refs=["ev-ca-cert-info-schema"]),
    fld("submit_time","submit_time","datetime","提交时间", refs=["ev-ca-cert-info-schema"]),
    fld("data_source","data_source","varchar","数据来源", refs=["ev-ca-cert-info-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-ca-cert-info-schema"]),
]
cust_cert_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-cert-info-schema"]),
    fld("ref_cust_company_info","ref_cust_company_info","varchar","关联企业", refs=["ev-cust-cert-info-schema"]),
    fld("certification_type","certification_type","varchar","认证类型", refs=["ev-cust-cert-info-schema"]),
    fld("auto_verify_status","auto_verify_status","varchar","自动核查状态", refs=["ev-cust-cert-info-schema"]),
    fld("auto_verify_msg","auto_verify_msg","varchar","自动核查结果", refs=["ev-cust-cert-info-schema"]),
    fld("manual_verify_status","manual_verify_status","varchar","人工核查状态", refs=["ev-cust-cert-info-schema"]),
    fld("face_business_no","face_business_no","varchar","人脸业务号", refs=["ev-cust-cert-info-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-cert-info-schema"]),
]
new_units.append(unit(
    "ca-certification", "CA 认证/实名认证", "customer",
    "CA 认证记录提交签章中心、失败标记；企业实名/人脸认证快照查询场景",
    "穿透 CaCertificationInfoAppServiceImpl 的 CA 认证记录创建、提交、失败标记；FaceVerifyController 查询企业认证快照。",
    [
        concept("ca-certification-record","CA 认证记录","CA 认证记录 ca_certification_info","ca_certification_info","id",refs=["ev-ca-cert-info-schema"]),
        concept("cust-certification-snapshot","企业认证快照","企业实名/人脸认证快照 cust_certification_info","cust_certification_info","id",refs=["ev-cust-cert-info-schema"]),
        concept("ca-cert-failed","CA 认证失败","submit_status=FAIL 的 CA 认证记录","ca_certification_info","submit_status",{"FAIL":"失败"},refs=["ev-ca-cert-mark-failed"]),
    ],
    [
        stage("ca-cert-create","CA 认证记录创建","创建或按 key 查询 CA 认证记录，更新协议通知/实名/意愿/附件信息","CaCertificationInfoAppServiceImpl.createOrGetByKey",
             [de("read","ca_certification_info",["id","cust_id","cust_type","submit_status","data_source","enable"],"cust_id=:custId AND cust_type=:custType","按企业+类型查认证记录",["ev-ca-cert-create"]),
              de("upsert","ca_certification_info",["cust_id","cust_type","submit_status","data_source","enable"],"不存在则创建","创建 CA 认证记录",["ev-ca-cert-create"])],
             next_stages=["ca-cert-submit"], refs=["ev-ca-cert-create"]),
        stage("ca-cert-submit","提交签章中心","提交认证数据到签章中心，更新 submit_status 与中台结果","CaCertificationInfoAppServiceImpl.submitToSignCenter",
             [de("read","ca_certification_info",["id","cust_id","submit_status"],"id=:id","读认证记录",["ev-ca-cert-submit"]),
              de("update","ca_certification_info",["submit_status","sign_platform_result","submit_time"],"提交后回写","更新提交状态与中台结果",["ev-ca-cert-submit"]),
              de("update","ca_certification_info",["submit_status"],"失败时","标记 submit_status=FAIL",["ev-ca-cert-mark-failed"])],
             next_stages=["cust-cert-query"], refs=["ev-ca-cert-submit"]),
        stage("cust-cert-query","企业认证快照查询","按企业 id 查询实名/人脸认证快照","FaceVerifyController.faceVerifyQuery",
             [de("read","cust_certification_info",["id","ref_cust_company_info","certification_type","auto_verify_status","auto_verify_msg","manual_verify_status","face_business_no","enable"],"custId=:custId","读企业认证快照",["ev-cust-cert-face-query"])],
             refs=["ev-cust-cert-face-query"]),
    ],
    [
        dset("ca_certification_info","ca_certification_info","CA 认证记录",ca_cert_fields,refs=["ev-ca-cert-info-schema"]),
        dset("cust_certification_info","cust_certification_info","企业实名/人脸认证快照",cust_cert_fields,refs=["ev-cust-cert-info-schema"]),
    ],
    [
        metric("metric-ca-cert-record-count","CA 认证记录数","CA 认证记录数","ca_certification_info","id",["ev-ca-cert-create"]),
        metric("metric-cust-cert-snapshot-count","企业认证快照数","企业实名/人脸认证快照数","cust_certification_info","id",["ev-cust-cert-face-query"]),
    ],
    [
        caliber("cal-ca-cert-failed","CA 认证失败","submit_status=FAIL 的 CA 认证记录","submit_status = 'FAIL'",[{"dataset":"ca_certification_info","field":"submit_status"}],["ev-ca-cert-mark-failed"]),
        caliber("cal-ca-cert-success","CA 认证成功","submit_status=SUCCESS 的 CA 认证记录","submit_status = 'SUCCESS'",[{"dataset":"ca_certification_info","field":"submit_status"}],["ev-ca-cert-submit"]),
    ],
    [
        rule("rule-ca-cert-fail-mark","CA 提交失败标记","签章中心提交失败时标记 submit_status=FAIL 并记录错误信息。","CaCertificationInfoAppServiceImpl.markFailed","查询认证失败记录时按 submit_status=FAIL 过滤。",[{"dataset":"ca_certification_info","field":"submit_status"}],["ev-ca-cert-mark-failed"]),
        rule("rule-cust-cert-snapshot-query","企业认证快照按企业查询","人脸认证结果按 custId 查询当前认证快照。","FaceVerifyController.faceVerifyQuery","查询企业认证结果时关联 cust_certification_info 而非仅 CA 认证表。",[{"dataset":"cust_certification_info","field":"ref_cust_company_info"}],["ev-cust-cert-face-query"]),
    ],
    [
        pattern("pat-ca-cert-failed-list","查 CA 认证失败记录","SELECT * FROM ca_certification_info WHERE submit_status='FAIL' AND enable='Y'",{"caliber_id":"cal-ca-cert-failed"},["ev-ca-cert-mark-failed"]),
        pattern("pat-cust-cert-by-company","查企业认证快照","SELECT * FROM cust_certification_info WHERE ref_cust_company_info=:companyCode AND enable='Y'",{"metric_id":"metric-cust-cert-snapshot-count"},["ev-cust-cert-face-query"]),
    ],
    assumptions=["签章中心/CFCA 为外部服务，不落本地知识表"],
))

# =========================================================================
# 3. ca-fee CA 费用
# =========================================================================
new_evidence += [
    ev("ev-ca-fee-company-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CaFeeCompanyDO.java","ca_fee_company 表字段定义"),
    ev("ev-ca-fee-order-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CaFeeOrderDO.java","ca_fee_order 表字段定义"),
    ev("ev-ca-fee-project-config-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CaFeeProjectConfigDO.java","ca_fee_project_config 表字段定义"),
    ev("ev-ca-fee-company-status","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cafee/CaFeeCompanyCaStatusApplication.java:59-111","按统一信用代码查询/更新 CA 签章状态"),
    ev("ev-ca-fee-order-create","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cafee/CaFeeOrderApplication.java:47-79","创建/关闭/支付/签署 CA 收费订单"),
    ev("ev-ca-fee-project-config","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cafee/CaFeeProjectConfigApplication.java:29-60","项目 CA 收费配置查询/保存/开关切换"),
]
fee_company_fields = [
    fld("id","id","bigint","表主键", refs=["ev-ca-fee-company-schema"]),
    fld("certification_no","certification_no","varchar","统一社会信用代码", refs=["ev-ca-fee-company-schema"]),
    fld("company_name","company_name","varchar","企业名称", refs=["ev-ca-fee-company-schema"]),
    fld("pay_status","pay_status","varchar","缴费状态", dictionary={"PAID":"已缴费","UNPAID":"未缴费"}, refs=["ev-ca-fee-company-schema"]),
    fld("fee_locked","fee_locked","varchar","是否已锁定年费标准", dictionary={"Y":"是","N":"否"}, refs=["ev-ca-fee-company-schema"]),
    fld("ca_status","ca_status","varchar","CA签章状态", refs=["ev-ca-fee-company-schema"]),
    fld("locked_annual_fee","locked_annual_fee","int","锁定的年费标准（元）", refs=["ev-ca-fee-company-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-ca-fee-company-schema"]),
]
fee_order_fields = [
    fld("id","id","bigint","表主键", refs=["ev-ca-fee-order-schema"]),
    fld("order_no","order_no","varchar","订单号，唯一键", refs=["ev-ca-fee-order-schema"]),
    fld("company_id","company_id","bigint","企业 ID", refs=["ev-ca-fee-order-schema"]),
    fld("project_id","project_id","bigint","触发项目 ID", refs=["ev-ca-fee-order-schema"]),
    fld("order_type","order_type","varchar","订单类型", refs=["ev-ca-fee-order-schema"]),
    fld("order_status","order_status","varchar","订单状态", refs=["ev-ca-fee-order-schema"]),
    fld("annual_fee","annual_fee","int","应缴年费（元）", refs=["ev-ca-fee-order-schema"]),
    fld("pay_amount","pay_amount","int","实缴金额（元）", refs=["ev-ca-fee-order-schema"]),
    fld("pay_method","pay_method","varchar","支付方式", refs=["ev-ca-fee-order-schema"]),
    fld("invoice_status","invoice_status","varchar","发票状态", refs=["ev-ca-fee-order-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-ca-fee-order-schema"]),
]
fee_project_config_fields = [
    fld("id","id","bigint","表主键", refs=["ev-ca-fee-project-config-schema"]),
    fld("project_id","project_id","bigint","项目ID", refs=["ev-ca-fee-project-config-schema"]),
    fld("tenant_id","tenant_id","bigint","所属租户", refs=["ev-ca-fee-project-config-schema"]),
    fld("charge_enabled","charge_enabled","varchar","是否开启CA收费", dictionary={"Y":"是","N":"否"}, refs=["ev-ca-fee-project-config-schema"]),
    fld("supplier_annual_fee","supplier_annual_fee","decimal","供应商角色年费（元）", refs=["ev-ca-fee-project-config-schema"]),
    fld("core_annual_fee","core_annual_fee","decimal","核心企业角色年费（元）", refs=["ev-ca-fee-project-config-schema"]),
    fld("agreement_version","agreement_version","varchar","当前绑定收费协议版本号", refs=["ev-ca-fee-project-config-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-ca-fee-project-config-schema"]),
]
new_units.append(unit(
    "ca-fee", "CA 费用管理", "ca-fee",
    "CA 服务费企业锁定、收费订单创建/支付/开票、项目收费配置场景",
    "穿透 CaFeeCompanyCaStatusApplication、CaFeeOrderApplication、CaFeeProjectConfigApplication：企业 CA 状态查询/更新、订单全生命周期、项目收费开关与年费标准。",
    [
        concept("ca-fee-company","CA 费用企业","CA 服务费企业 ca_fee_company","ca_fee_company","id",refs=["ev-ca-fee-company-schema"]),
        concept("ca-fee-order","CA 收费订单","CA 收费订单 ca_fee_order","ca_fee_order","id",refs=["ev-ca-fee-order-schema"]),
        concept("ca-fee-project-config","项目 CA 收费配置","项目 CA 收费配置 ca_fee_project_config","ca_fee_project_config","id",refs=["ev-ca-fee-project-config-schema"]),
    ],
    [
        stage("fee-company-status","企业 CA 状态维护","按统一信用代码查询/更新企业 CA 签章状态与缴费状态","CaFeeCompanyCaStatusApplication",
             [de("read","ca_fee_company",["id","certification_no","company_name","pay_status","fee_locked","ca_status","locked_annual_fee","enable"],"certification_no=:certificationNo","读企业 CA 费用状态",["ev-ca-fee-company-status"]),
              de("update","ca_fee_company",["pay_status","ca_status","fee_locked","locked_annual_fee"],"按业务更新","更新企业缴费/签章/锁价状态",["ev-ca-fee-company-status"])],
             next_stages=["fee-order-manage"], refs=["ev-ca-fee-company-status"]),
        stage("fee-order-manage","收费订单管理","创建/关闭/支付/签署 CA 收费订单，记录支付与发票状态","CaFeeOrderApplication",
             [de("read","ca_fee_order",["id","order_no","company_id","project_id","order_type","order_status","annual_fee","pay_amount","pay_method","invoice_status","enable"],"order_no=:orderNo","读订单",["ev-ca-fee-order-create"]),
              de("upsert","ca_fee_order",["order_no","company_id","project_id","order_type","order_status","annual_fee","pay_amount","pay_method","invoice_status","enable"],"创建/更新订单","保存 CA 收费订单",["ev-ca-fee-order-create"])],
             next_stages=["fee-project-config"], refs=["ev-ca-fee-order-create"]),
        stage("fee-project-config","项目收费配置","查询/保存项目 CA 收费配置，切换收费开关并记录时间","CaFeeProjectConfigApplication",
             [de("read","ca_fee_project_config",["id","project_id","tenant_id","charge_enabled","supplier_annual_fee","core_annual_fee","agreement_version","enable"],"project_id=:projectId","读项目收费配置",["ev-ca-fee-project-config"]),
              de("upsert","ca_fee_project_config",["project_id","tenant_id","charge_enabled","supplier_annual_fee","core_annual_fee","agreement_version","enable"],"保存配置","保存项目 CA 收费配置",["ev-ca-fee-project-config"])],
             refs=["ev-ca-fee-project-config"]),
    ],
    [
        dset("ca_fee_company","ca_fee_company","CA 服务费企业",fee_company_fields,refs=["ev-ca-fee-company-schema"]),
        dset("ca_fee_order","ca_fee_order","CA 收费订单",fee_order_fields,refs=["ev-ca-fee-order-schema"]),
        dset("ca_fee_project_config","ca_fee_project_config","项目 CA 收费配置",fee_project_config_fields,refs=["ev-ca-fee-project-config-schema"]),
    ],
    [
        metric("metric-ca-fee-company-count","CA 费用企业数","CA 服务费企业数","ca_fee_company","id",["ev-ca-fee-company-status"]),
        metric("metric-ca-fee-order-count","CA 收费订单数","CA 收费订单数","ca_fee_order","id",["ev-ca-fee-order-create"]),
    ],
    [
        caliber("cal-ca-fee-unpaid","未缴费企业","pay_status=UNPAID 的 CA 服务费企业","pay_status = 'UNPAID'",[{"dataset":"ca_fee_company","field":"pay_status"}],["ev-ca-fee-company-status"]),
        caliber("cal-ca-fee-charge-enabled","开启收费项目","charge_enabled=Y 的项目 CA 收费配置","charge_enabled = 'Y'",[{"dataset":"ca_fee_project_config","field":"charge_enabled"}],["ev-ca-fee-project-config"]),
    ],
    [
        rule("rule-ca-fee-lock-annual","首次缴费成功后锁定年费标准","企业首次缴费成功后锁定 locked_annual_fee 与 fee_locked=Y，后续续费按锁定标准执行。","CaFeeCompanyCaStatusApplication","查询企业年费标准时应优先取 locked_annual_fee，且仅在 fee_locked=Y 时生效。",[{"dataset":"ca_fee_company","field":"fee_locked"},{"dataset":"ca_fee_company","field":"locked_annual_fee"}],["ev-ca-fee-company-status"]),
        rule("rule-ca-fee-project-charge-toggle","项目收费开关切换","项目收费配置支持开启/关闭 CA 收费，并记录 last_toggle_time 与当前协议版本号。","CaFeeProjectConfigApplication","按项目查询是否收费时以 charge_enabled 为准。",[{"dataset":"ca_fee_project_config","field":"charge_enabled"}],["ev-ca-fee-project-config"]),
    ],
    [
        pattern("pat-ca-fee-unpaid-company","查未缴费 CA 费用企业","SELECT * FROM ca_fee_company WHERE pay_status='UNPAID' AND enable='Y'",{"caliber_id":"cal-ca-fee-unpaid"},["ev-ca-fee-company-status"]),
        pattern("pat-ca-fee-order-by-company","查企业 CA 收费订单","SELECT * FROM ca_fee_order WHERE company_id=:companyId AND enable='Y'",{"metric_id":"metric-ca-fee-order-count"},["ev-ca-fee-order-create"]),
    ],
    assumptions=["交e保支付渠道为外部支付服务，支付状态通过回调/查询同步"],
))

# =========================================================================
# 4. customer-auth-product 客户产品授权/定制/互通
# =========================================================================
new_evidence += [
    ev("ev-cust-auth-app-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustAuthApplicationDO.java","cust_auth_application 表字段定义"),
    ev("ev-cust-customized-product-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustCustomizedProductDO.java","cust_customized_product 表字段定义"),
    ev("ev-cust-interworking-product-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustInterworkingProductDO.java","cust_interworking_product 表字段定义"),
    ev("ev-cust-auth-app-save","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/SubmitCustInfoEnhanceService.java:114-157","保存企业产品授权应用，避免重复授权"),
    ev("ev-cust-customized-product-save","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/controller/client/ClientAppController.java:372-389","客户端新增/更新快捷入口产品"),
    ev("ev-cust-interworking-product-query","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustCompanyUtilApplication.java:261-270","查询企业开通的互通产品"),
]
auth_app_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-auth-app-schema"]),
    fld("application","application","varchar","产品应用", refs=["ev-cust-auth-app-schema"]),
    fld("open_status","open_status","varchar","开通状态", refs=["ev-cust-auth-app-schema"]),
    fld("ref_cust_company_info","ref_cust_company_info","varchar","客户应用", refs=["ev-cust-auth-app-schema"]),
    fld("platform_product_code","platform_product_code","varchar","平台产品编码", refs=["ev-cust-auth-app-schema"]),
    fld("ref_cust_auth_application_tenant_product","ref_cust_auth_application_tenant_product","varchar","关联应用", refs=["ev-cust-auth-app-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-auth-app-schema"]),
]
customized_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-customized-product-schema"]),
    fld("name","name","varchar","产品名称", refs=["ev-cust-customized-product-schema"]),
    fld("cust_id","cust_id","bigint","企业id", refs=["ev-cust-customized-product-schema"]),
    fld("url","url","varchar","跳转链接", refs=["ev-cust-customized-product-schema"]),
    fld("logo_icon_url","logo_icon_url","varchar","图标", refs=["ev-cust-customized-product-schema"]),
    fld("view_order","view_order","int","显示顺序", refs=["ev-cust-customized-product-schema"]),
    fld("ref_cust_customized_product_cust_company_info","ref_cust_customized_product_cust_company_info","varchar","客户关联自定义产品配置", refs=["ev-cust-customized-product-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-customized-product-schema"]),
]
interworking_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-interworking-product-schema"]),
    fld("open_status","open_status","varchar","开通状态", refs=["ev-cust-interworking-product-schema"]),
    fld("cust_id","cust_id","bigint","企业id", refs=["ev-cust-interworking-product-schema"]),
    fld("platform_product_code","platform_product_code","varchar","平台产品编码", refs=["ev-cust-interworking-product-schema"]),
    fld("product_id","product_id","bigint","互通产品id", refs=["ev-cust-interworking-product-schema"]),
    fld("ref_cust_interworking_product_cust_company_info","ref_cust_interworking_product_cust_company_info","varchar","关联企业", refs=["ev-cust-interworking-product-schema"]),
    fld("ref_cust_interworking_product_tenant_interworking_product","ref_cust_interworking_product_tenant_interworking_product","varchar","关联互通产品", refs=["ev-cust-interworking-product-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-interworking-product-schema"]),
]
new_units.append(unit(
    "customer-auth-product", "客户产品授权与快捷入口", "product",
    "企业产品授权应用开通、客户端快捷入口定制、客户互通产品查询场景",
    "穿透 SubmitCustInfoEnhanceService.custAuthApplication、ClientAppController 定制产品、CustCompanyUtilApplication 查询互通产品。",
    [
        concept("cust-auth-application","产品授权应用","企业产品授权应用 cust_auth_application","cust_auth_application","id",refs=["ev-cust-auth-app-schema"]),
        concept("cust-customized-product","快捷入口产品","客户端快捷入口产品 cust_customized_product","cust_customized_product","id",refs=["ev-cust-customized-product-schema"]),
        concept("cust-interworking-product","客户互通产品","客户开通的互通产品 cust_interworking_product","cust_interworking_product","id",refs=["ev-cust-interworking-product-schema"]),
    ],
    [
        stage("auth-app-save","产品授权应用保存","按企业可开通产品列表保存授权应用，已存在则跳过","SubmitCustInfoEnhanceService.custAuthApplication",
             [de("read","cust_auth_application",["id","application","ref_cust_company_info","platform_product_code","ref_cust_auth_application_tenant_product","enable"],"ref_cust_company_info=:companyCode AND ref_cust_auth_application_tenant_product=:tenantProductCode","查重",["ev-cust-auth-app-save"]),
              de("insert","cust_auth_application",["application","open_status","ref_cust_company_info","platform_product_code","ref_cust_auth_application_tenant_product","enable"],"不存在时插入","保存产品授权应用",["ev-cust-auth-app-save"])],
             next_stages=["customized-product-save"], refs=["ev-cust-auth-app-save"]),
        stage("customized-product-save","快捷入口产品定制","新增/更新客户端快捷入口产品","ClientAppController.create/change",
             [de("read","cust_customized_product",["id","name","cust_id","url","logo_icon_url","view_order","ref_cust_customized_product_cust_company_info","enable"],"cust_id=:custId","读现有快捷入口配置",["ev-cust-customized-product-save"]),
              de("upsert","cust_customized_product",["name","cust_id","url","logo_icon_url","view_order","ref_cust_customized_product_cust_company_info","enable"],"保存快捷入口产品","新增/更新快捷入口产品",["ev-cust-customized-product-save"])],
             next_stages=["interworking-product-query"], refs=["ev-cust-customized-product-save"]),
        stage("interworking-product-query","客户互通产品查询","按企业 code 查询客户开通的互通产品","CustCompanyUtilApplication 查询",
             [de("read","cust_interworking_product",["id","open_status","cust_id","platform_product_code","product_id","ref_cust_interworking_product_cust_company_info","ref_cust_interworking_product_tenant_interworking_product","enable"],"ref_cust_interworking_product_cust_company_info=:companyCode AND enable='Y'","读客户互通产品",["ev-cust-interworking-product-query"])],
             refs=["ev-cust-interworking-product-query"]),
    ],
    [
        dset("cust_auth_application","cust_auth_application","企业产品授权应用",auth_app_fields,refs=["ev-cust-auth-app-schema"]),
        dset("cust_customized_product","cust_customized_product","客户端快捷入口产品",customized_fields,refs=["ev-cust-customized-product-schema"]),
        dset("cust_interworking_product","cust_interworking_product","客户互通产品",interworking_fields,refs=["ev-cust-interworking-product-schema"]),
    ],
    [
        metric("metric-auth-app-count","产品授权应用数","企业产品授权应用数","cust_auth_application","id",["ev-cust-auth-app-save"]),
        metric("metric-customized-product-count","快捷入口产品数","客户端快捷入口产品数","cust_customized_product","id",["ev-cust-customized-product-save"]),
        metric("metric-interworking-product-count","客户互通产品数","客户互通产品数","cust_interworking_product","id",["ev-cust-interworking-product-query"]),
    ],
    [
        caliber("cal-auth-app-open","已开通授权应用","open_status=Y 的产品授权应用","open_status = 'Y'",[{"dataset":"cust_auth_application","field":"open_status"}],["ev-cust-auth-app-save"]),
        caliber("cal-interworking-product-open","已开通互通产品","open_status=Y 的客户互通产品","open_status = 'Y'",[{"dataset":"cust_interworking_product","field":"open_status"}],["ev-cust-interworking-product-query"]),
    ],
    [
        rule("rule-auth-app-no-duplicate","产品授权应用不重复开通","按 ref_cust_company_info + ref_cust_auth_application_tenant_product 查重，已存在不重复插入。","SubmitCustInfoEnhanceService.custAuthApplication","查询企业授权应用时同一租户产品最多一条。",[{"dataset":"cust_auth_application","field":"ref_cust_company_info"},{"dataset":"cust_auth_application","field":"ref_cust_auth_application_tenant_product"}],["ev-cust-auth-app-save"]),
        rule("rule-customized-product-by-cust","快捷入口按企业隔离","客户端快捷入口产品按 cust_id 隔离，查询时按当前企业过滤。","ClientAppController.listMyCustomizedProduct","查询快捷入口产品必须带 cust_id。",[{"dataset":"cust_customized_product","field":"cust_id"}],["ev-cust-customized-product-save"]),
    ],
    [
        pattern("pat-auth-app-by-company","查企业产品授权应用","SELECT * FROM cust_auth_application WHERE ref_cust_company_info=:companyCode AND enable='Y'",{"caliber_id":"cal-auth-app-open"},["ev-cust-auth-app-save"]),
        pattern("pat-interworking-product-by-company","查企业互通产品","SELECT * FROM cust_interworking_product WHERE ref_cust_interworking_product_cust_company_info=:companyCode AND enable='Y'",{"caliber_id":"cal-interworking-product-open"},["ev-cust-interworking-product-query"]),
    ],
))

# =========================================================================
# 5. customer-group 客户集团关系
# =========================================================================
new_evidence += [
    ev("ev-cust-group-rel-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustGroupRelDO.java","cust_group_rel 表字段定义"),
    ev("ev-cust-group-rel-save","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupRelApplication.java:92-118","新增集团关系并计算根/父企业"),
    ev("ev-cust-group-rel-query","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupRelApplication.java:122-138","查询集团企业关系树"),
]
group_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-group-rel-schema"]),
    fld("cust_id","cust_id","bigint","企业id", refs=["ev-cust-group-rel-schema"]),
    fld("parent_cust_id","parent_cust_id","bigint","父企业id", refs=["ev-cust-group-rel-schema"]),
    fld("root_cust_id","root_cust_id","bigint","根企业id", refs=["ev-cust-group-rel-schema"]),
    fld("root_flag","root_flag","varchar","是否集团企业", dictionary={"Y":"是","N":"不是"}, refs=["ev-cust-group-rel-schema"]),
    fld("level","level","int","层级", refs=["ev-cust-group-rel-schema"]),
    fld("cust_type","cust_type","varchar","企业角色", refs=["ev-cust-group-rel-schema"]),
    fld("status","status","varchar","状态", dictionary={"EFFECTIVE":"已生效","INEFFECTIVE":"未生效","REJECTED":"已拒绝"}, refs=["ev-cust-group-rel-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-group-rel-schema"]),
]
new_units.append(unit(
    "customer-group", "客户集团关系", "customer",
    "集团企业成员关系的创建、生效/拒绝与树查询场景",
    "穿透 CustGroupRelApplication：创建集团关系时计算 root/parent/level，查询集团成员关系。",
    [
        concept("cust-group-rel","集团关系","企业集团成员关系 cust_group_rel","cust_group_rel","id",refs=["ev-cust-group-rel-schema"]),
        concept("group-root","集团根企业","root_flag=Y 的集团根企业关系","cust_group_rel","root_flag",{"Y":"集团企业"},refs=["ev-cust-group-rel-schema"]),
    ],
    [
        stage("group-rel-save","集团关系保存","新增集团成员关系，计算根企业/父企业/层级","CustGroupRelApplication 新增",
             [de("read","cust_group_rel",["id","cust_id","parent_cust_id","root_cust_id","root_flag","level","status"],"cust_id=:custId","查已有集团关系",["ev-cust-group-rel-save"]),
              de("insert","cust_group_rel",["cust_id","parent_cust_id","root_cust_id","root_flag","level","cust_type","status","enable"],"新增集团关系","保存集团关系",["ev-cust-group-rel-save"])],
             next_stages=["group-rel-query"], refs=["ev-cust-group-rel-save"]),
        stage("group-rel-query","集团关系查询","按根企业/父企业查询集团成员关系","CustGroupRelApplication 查询",
             [de("read","cust_group_rel",["id","cust_id","parent_cust_id","root_cust_id","root_flag","level","cust_type","status","enable"],"root_cust_id=:rootCustId OR parent_cust_id=:custId","读集团关系",["ev-cust-group-rel-query"])],
             refs=["ev-cust-group-rel-query"]),
    ],
    [
        dset("cust_group_rel","cust_group_rel","企业集团关系",group_fields,refs=["ev-cust-group-rel-schema"]),
    ],
    [
        metric("metric-cust-group-rel-count","集团关系数","企业集团成员关系数","cust_group_rel","id",["ev-cust-group-rel-query"]),
    ],
    [
        caliber("cal-cust-group-effective","生效集团关系","status=EFFECTIVE 的集团成员关系","status = 'EFFECTIVE'",[{"dataset":"cust_group_rel","field":"status"}],["ev-cust-group-rel-save"]),
        caliber("cal-cust-group-root","集团根企业","root_flag=Y 的集团关系","root_flag = 'Y'",[{"dataset":"cust_group_rel","field":"root_flag"}],["ev-cust-group-rel-schema"]),
    ],
    [
        rule("rule-cust-group-root-calc","集团关系保存时计算根企业","保存集团关系时按父企业链路计算 root_cust_id 和 level；root_flag=Y 表示集团企业。","CustGroupRelApplication 新增","查询集团成员时以 root_cust_id 聚合。",[{"dataset":"cust_group_rel","field":"root_cust_id"},{"dataset":"cust_group_rel","field":"root_flag"}],["ev-cust-group-rel-save"]),
    ],
    [
        pattern("pat-cust-group-by-root","查集团成员","SELECT * FROM cust_group_rel WHERE root_cust_id=:rootCustId AND enable='Y'",{"caliber_id":"cal-cust-group-effective"},["ev-cust-group-rel-query"]),
    ],
))

# =========================================================================
# 6. customer-company-extra 企业补充信息（总公司/股东/生命周期）
# =========================================================================
new_evidence += [
    ev("ev-cust-head-company-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustHeadCompanyInfoDO.java","cust_head_company_info 表字段定义"),
    ev("ev-cust-shareholder-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustShareholderInfoDO.java","cust_shareholder_info 表字段定义"),
    ev("ev-cust-lifecycle-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustCompanyLifecycleInfoDO.java","cust_company_lifecycle_info 表字段定义"),
    ev("ev-cust-head-company-save","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/migratory/appliaction/PlatFormMigratoryApplication.java:1755-1768","保存/更新总公司信息"),
    ev("ev-cust-shareholder-save","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ApplyCompanyInfoApplication.java:189-192","查询并复制股东信息"),
    ev("ev-cust-lifecycle-write","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustCompanyInfoApplication.java:7070-7138","冻结/解冻生命周期记录查询与写入"),
]
head_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-head-company-schema"]),
    fld("name","name","varchar","企业名称", refs=["ev-cust-head-company-schema"]),
    fld("certification_no","certification_no","varchar","统一社会信用代码", refs=["ev-cust-head-company-schema"]),
    fld("legal_name","legal_name","varchar","法人姓名", refs=["ev-cust-head-company-schema"]),
    fld("ref_cust_head_company_info_cust_company_info","ref_cust_head_company_info_cust_company_info","varchar","客户信息和总公司信息", refs=["ev-cust-head-company-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-head-company-schema"]),
]
shareholder_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-shareholder-schema"]),
    fld("name","name","varchar","关联方名称", refs=["ev-cust-shareholder-schema"]),
    fld("ref_cust_company_info","ref_cust_company_info","varchar","客户股东信息", refs=["ev-cust-shareholder-schema"]),
    fld("certification_type","certification_type","varchar","证件类型", refs=["ev-cust-shareholder-schema"]),
    fld("certification_no","certification_no","varchar","证件号码", refs=["ev-cust-shareholder-schema"]),
    fld("fund_scale","fund_scale","varchar","出资比例（%）", refs=["ev-cust-shareholder-schema"]),
    fld("relation_type","relation_type","varchar","关联方类型", refs=["ev-cust-shareholder-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-shareholder-schema"]),
]
lifecycle_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-lifecycle-schema"]),
    fld("company_id","company_id","bigint","企业id", refs=["ev-cust-lifecycle-schema"]),
    fld("type","type","varchar","类型", refs=["ev-cust-lifecycle-schema"]),
    fld("reason","reason","varchar","冻结原因", refs=["ev-cust-lifecycle-schema"]),
    fld("attach","attach","varchar","冻结附件路径集合", refs=["ev-cust-lifecycle-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-lifecycle-schema"]),
]
new_units.append(unit(
    "customer-company-extra", "企业补充信息", "customer",
    "总公司信息、股东/关联方信息、企业冻结/解冻生命周期记录场景",
    "穿透 PlatFormMigratoryApplication 保存总公司，ApplyCompanyInfoApplication 维护股东，CustCompanyInfoApplication 写生命周期记录。",
    [
        concept("cust-head-company","总公司信息","企业总公司信息 cust_head_company_info","cust_head_company_info","id",refs=["ev-cust-head-company-schema"]),
        concept("cust-shareholder","股东信息","企业股东/关联方信息 cust_shareholder_info","cust_shareholder_info","id",refs=["ev-cust-shareholder-schema"]),
        concept("cust-lifecycle","企业生命周期","企业冻结/解冻生命周期 cust_company_lifecycle_info","cust_company_lifecycle_info","id",refs=["ev-cust-lifecycle-schema"]),
    ],
    [
        stage("head-company-save","总公司信息保存","保存/更新企业总公司信息","PlatFormMigratoryApplication.setHeadCompany",
             [de("read","cust_head_company_info",["id","name","certification_no","legal_name","ref_cust_head_company_info_cust_company_info","enable"],"certification_no=:certificationNo","查总公司",["ev-cust-head-company-save"]),
              de("upsert","cust_head_company_info",["name","certification_no","legal_name","ref_cust_head_company_info_cust_company_info","enable"],"不存在则新增","保存总公司信息",["ev-cust-head-company-save"])],
             next_stages=["shareholder-save"], refs=["ev-cust-head-company-save"]),
        stage("shareholder-save","股东信息维护","按企业查询并复制股东/关联方信息","ApplyCompanyInfoApplication",
             [de("read","cust_shareholder_info",["id","name","ref_cust_company_info","certification_type","certification_no","fund_scale","relation_type","enable"],"ref_cust_company_info=:companyCode","读股东信息",["ev-cust-shareholder-save"]),
              de("upsert","cust_shareholder_info",["name","ref_cust_company_info","certification_type","certification_no","fund_scale","relation_type","enable"],"复制/保存股东信息","维护股东信息",["ev-cust-shareholder-save"])],
             next_stages=["lifecycle-write"], refs=["ev-cust-shareholder-save"]),
        stage("lifecycle-write","生命周期记录写入","企业冻结/解冻时写入生命周期记录","CustCompanyInfoApplication 冻结/解冻",
             [de("read","cust_company_lifecycle_info",["id","company_id","type","reason","attach","enable"],"company_id=:companyId AND type=:type","查生命周期记录",["ev-cust-lifecycle-write"]),
              de("upsert","cust_company_lifecycle_info",["company_id","type","reason","attach","enable"],"冻结/解冻时写入","保存生命周期记录",["ev-cust-lifecycle-write"])],
             refs=["ev-cust-lifecycle-write"]),
    ],
    [
        dset("cust_head_company_info","cust_head_company_info","企业总公司信息",head_fields,refs=["ev-cust-head-company-schema"]),
        dset("cust_shareholder_info","cust_shareholder_info","企业股东/关联方信息",shareholder_fields,refs=["ev-cust-shareholder-schema"]),
        dset("cust_company_lifecycle_info","cust_company_lifecycle_info","企业生命周期记录",lifecycle_fields,refs=["ev-cust-lifecycle-schema"]),
    ],
    [
        metric("metric-head-company-count","总公司信息数","总公司信息记录数","cust_head_company_info","id",["ev-cust-head-company-save"]),
        metric("metric-shareholder-count","股东信息数","企业股东/关联方记录数","cust_shareholder_info","id",["ev-cust-shareholder-save"]),
    ],
    [
        caliber("cal-shareholder-by-company","企业股东范围","ref_cust_company_info 指定企业的股东/关联方记录","ref_cust_company_info = :companyCode",[{"dataset":"cust_shareholder_info","field":"ref_cust_company_info"}],["ev-cust-shareholder-save"]),
        caliber("cal-lifecycle-freeze","冻结生命周期","type=冻结 的企业生命周期记录","type = 'FREEZE'",[{"dataset":"cust_company_lifecycle_info","field":"type"}],["ev-cust-lifecycle-write"]),
    ],
    [
        rule("rule-head-company-unique","总公司按企业唯一","总公司信息通过 ref_cust_head_company_info_cust_company_info 关联企业，保存时按企业查重。","PlatFormMigratoryApplication.setHeadCompany","查询企业总公司时按 ref_cust_head_company_info_cust_company_info 关联。",[{"dataset":"cust_head_company_info","field":"ref_cust_head_company_info_cust_company_info"}],["ev-cust-head-company-save"]),
        rule("rule-lifecycle-freeze-record","冻结记录留存","企业冻结/解冻时记录 reason 与附件，查询冻结状态时按 type 过滤。","CustCompanyInfoApplication 冻结/解冻","查询企业冻结历史时按 type 和 enable 过滤。",[{"dataset":"cust_company_lifecycle_info","field":"type"}],["ev-cust-lifecycle-write"]),
    ],
    [
        pattern("pat-shareholder-by-company","查企业股东信息","SELECT * FROM cust_shareholder_info WHERE ref_cust_company_info=:companyCode AND enable='Y'",{"caliber_id":"cal-shareholder-by-company"},["ev-cust-shareholder-save"]),
        pattern("pat-head-company-by-company","查企业总公司信息","SELECT * FROM cust_head_company_info WHERE ref_cust_head_company_info_cust_company_info=:companyCode AND enable='Y'",{"metric_id":"metric-head-company-count"},["ev-cust-head-company-save"]),
    ],
))

# =========================================================================
# 7. customer-survey-invite-settings 问卷/邀请/客户设置
# =========================================================================
new_evidence += [
    ev("ev-cust-invite-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustInviteInfoDO.java","cust_invite_info 表字段定义"),
    ev("ev-cust-survey-state-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustCompanySurveyStateDO.java","cust_company_survey_state 表字段定义"),
    ev("ev-cust-survey-whitelist-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustCompanySurveyWhitelistDO.java","cust_company_survey_whitelist 表字段定义"),
    ev("ev-cust-survey-answer-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustSurveyAnswerDO.java","cust_survey_answer 表字段定义"),
    ev("ev-cust-setting-config-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustSettingConfigDO.java","cust_setting_config 表字段定义"),
    ev("ev-cust-invite-save","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/CustCompanyInfoController.java:1584-1610","邀请检查/保存/创建客户"),
    ev("ev-cust-survey-state-claim","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/wenjuan/WenjuanDisplayService.java:45-123","问卷弹窗/首访用户与转盘展示状态"),
    ev("ev-cust-survey-whitelist-check","code_path","lowcode-pplatform-common/lowcode-pplatform-common-dao/src/main/java/com/lls/lowcode/pplatform/common/db/dao/cust/CustCompanySurveyWhitelistDao.java:19-20","按企业查询问卷白名单"),
    ev("ev-cust-survey-answer-submit","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/survey/CustSurveyAnswerService.java:86-96","提交调研答案"),
    ev("ev-cust-setting-get","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/CustSettingConfigController.java:43-45","读取建档配置信息"),
]
invite_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-invite-schema"]),
    fld("progress","progress","varchar","进度", refs=["ev-cust-invite-schema"]),
    fld("contact_name","contact_name","varchar","联系人", refs=["ev-cust-invite-schema"]),
    fld("contact_phone","contact_phone","varchar","联系人手机号码", refs=["ev-cust-invite-schema"]),
    fld("channel_code","channel_code","varchar","渠道码", refs=["ev-cust-invite-schema"]),
    fld("invite_from","invite_from","varchar","邀请主体", refs=["ev-cust-invite-schema"]),
    fld("invite_cust_id","invite_cust_id","bigint","邀请客户id", refs=["ev-cust-invite-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-invite-schema"]),
]
survey_state_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-survey-state-schema"]),
    fld("company_id","company_id","bigint","企业ID", refs=["ev-cust-survey-state-schema"]),
    fld("first_visitor_user_id","first_visitor_user_id","bigint","首个进入产融首页的用户ID", refs=["ev-cust-survey-state-schema"]),
    fld("first_visit_time","first_visit_time","datetime","首次访问时间", refs=["ev-cust-survey-state-schema"]),
    fld("first_visitor_lottery_shown","first_visitor_lottery_shown","varchar","转盘抽奖是否已展示", dictionary={"Y":"是","N":"否"}, refs=["ev-cust-survey-state-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-survey-state-schema"]),
]
survey_whitelist_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-survey-whitelist-schema"]),
    fld("company_id","company_id","bigint","企业id", refs=["ev-cust-survey-whitelist-schema"]),
    fld("company_name","company_name","varchar","企业名称", refs=["ev-cust-survey-whitelist-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-survey-whitelist-schema"]),
]
survey_answer_fields = [
    fld("id","id","bigint","表主键（雪花ID）", refs=["ev-cust-survey-answer-schema"]),
    fld("survey_code","survey_code","varchar","调研编码", refs=["ev-cust-survey-answer-schema"]),
    fld("company_id","company_id","bigint","当前登录企业ID", refs=["ev-cust-survey-answer-schema"]),
    fld("user_id","user_id","bigint","当前登录用户ID", refs=["ev-cust-survey-answer-schema"]),
    fld("question_no","question_no","int","题号", refs=["ev-cust-survey-answer-schema"]),
    fld("answer_value","answer_value","varchar","选项明文", refs=["ev-cust-survey-answer-schema"]),
    fld("submit_time","submit_time","datetime","提交时间", refs=["ev-cust-survey-answer-schema"]),
]
setting_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-setting-config-schema"]),
    fld("key_word","key_word","varchar","企业关键信息", refs=["ev-cust-setting-config-schema"]),
    fld("need_verify_no_key","need_verify_no_key","varchar","企业非关键信息变更审核", refs=["ev-cust-setting-config-schema"]),
    fld("invitation_code_period","invitation_code_period","int","邀请码有效期", refs=["ev-cust-setting-config-schema"]),
    fld("payment_maximum_number","payment_maximum_number","int","最多申请打款次数", refs=["ev-cust-setting-config-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-setting-config-schema"]),
]
new_units.append(unit(
    "customer-survey-invite-settings", "问卷/邀请/客户设置", "customer",
    "企业邀请码、问卷调研白名单与答案、首访问卷弹窗状态、建档配置信息场景",
    "穿透 CustCompanyInfoController 邀请保存、WenjuanDisplayService 首访状态、CustSurveyAnswerService 提交答案、CustSettingConfigController 读取配置。",
    [
        concept("cust-invite","企业邀请","企业邀请信息 cust_invite_info","cust_invite_info","id",refs=["ev-cust-invite-schema"]),
        concept("survey-state","问卷首访状态","企业问卷首访状态 cust_company_survey_state","cust_company_survey_state","id",refs=["ev-cust-survey-state-schema"]),
        concept("survey-whitelist","问卷白名单","企业问卷白名单 cust_company_survey_whitelist","cust_company_survey_whitelist","id",refs=["ev-cust-survey-whitelist-schema"]),
        concept("survey-answer","调研答案","企业调研答案 cust_survey_answer","cust_survey_answer","id",refs=["ev-cust-survey-answer-schema"]),
        concept("cust-setting-config","建档配置","企业建档配置 cust_setting_config","cust_setting_config","id",refs=["ev-cust-setting-config-schema"]),
    ],
    [
        stage("invite-save","邀请信息保存","企业邀请检查/保存/创建客户","CustCompanyInfoController.inviteCheck/inviteSave",
             [de("read","cust_invite_info",["id","contact_phone","channel_code","invite_from","invite_cust_id","enable"],"contact_phone=:contactPhone","邀请查重",["ev-cust-invite-save"]),
              de("upsert","cust_invite_info",["progress","contact_name","contact_phone","channel_code","invite_from","invite_cust_id","enable"],"保存邀请","保存企业邀请信息",["ev-cust-invite-save"])],
             next_stages=["survey-state-claim"], refs=["ev-cust-invite-save"]),
        stage("survey-state-claim","问卷首访状态","查询/抢占企业首个访问用户与转盘展示状态","WenjuanDisplayService",
             [de("read","cust_company_survey_state",["id","company_id","first_visitor_user_id","first_visit_time","first_visitor_lottery_shown","enable"],"company_id=:companyId","读首访状态",["ev-cust-survey-state-claim"]),
              de("upsert","cust_company_survey_state",["company_id","first_visitor_user_id","first_visit_time","first_visitor_lottery_shown","enable"],"首访时插入/更新","保存首访状态",["ev-cust-survey-state-claim"]),
              de("read","cust_company_survey_whitelist",["id","company_id","company_name","enable"],"company_id=:companyId AND enable='Y'","读问卷白名单",["ev-cust-survey-whitelist-check"])],
             next_stages=["survey-answer-submit"], refs=["ev-cust-survey-state-claim"]),
        stage("survey-answer-submit","调研答案提交","企业用户提交调研问卷答案","CustSurveyAnswerService.submit",
             [de("insert","cust_survey_answer",["survey_code","company_id","user_id","question_no","answer_value","submit_time"],"提交答案","保存调研答案",["ev-cust-survey-answer-submit"])],
             next_stages=["setting-read"], refs=["ev-cust-survey-answer-submit"]),
        stage("setting-read","建档配置读取","读取企业建档配置（关键信息/邀请码/打款次数等）","CustSettingConfigController.getConfig",
             [de("read","cust_setting_config",["id","key_word","need_verify_no_key","invitation_code_period","payment_maximum_number","enable"],"enable='Y'","读建档配置",["ev-cust-setting-get"])],
             refs=["ev-cust-setting-get"]),
    ],
    [
        dset("cust_invite_info","cust_invite_info","企业邀请信息",invite_fields,refs=["ev-cust-invite-schema"]),
        dset("cust_company_survey_state","cust_company_survey_state","企业问卷首访状态",survey_state_fields,refs=["ev-cust-survey-state-schema"]),
        dset("cust_company_survey_whitelist","cust_company_survey_whitelist","企业问卷白名单",survey_whitelist_fields,refs=["ev-cust-survey-whitelist-schema"]),
        dset("cust_survey_answer","cust_survey_answer","企业调研答案",survey_answer_fields,refs=["ev-cust-survey-answer-schema"]),
        dset("cust_setting_config","cust_setting_config","企业建档配置",setting_fields,refs=["ev-cust-setting-config-schema"]),
    ],
    [
        metric("metric-invite-count","企业邀请数","企业邀请记录数","cust_invite_info","id",["ev-cust-invite-save"]),
        metric("metric-survey-answer-count","调研答案数","企业调研答案数","cust_survey_answer","id",["ev-cust-survey-answer-submit"]),
    ],
    [
        caliber("cal-survey-whitelisted","问卷白名单企业","enable=Y 的问卷白名单企业","enable = 'Y'",[{"dataset":"cust_company_survey_whitelist","field":"enable"}],["ev-cust-survey-whitelist-check"]),
        caliber("cal-lottery-not-shown","转盘未展示","first_visitor_lottery_shown=N 的首访记录","first_visitor_lottery_shown = 'N'",[{"dataset":"cust_company_survey_state","field":"first_visitor_lottery_shown"}],["ev-cust-survey-state-claim"]),
    ],
    [
        rule("rule-survey-whitelist-gate","问卷仅白名单企业可见","问卷弹窗/调研入口只对 cust_company_survey_whitelist 中 enable=Y 的企业展示。","WenjuanDisplayService","查询问卷可见企业时必须关联白名单表。",[{"dataset":"cust_company_survey_whitelist","field":"company_id"}],["ev-cust-survey-whitelist-check"]),
        rule("rule-first-visitor-lottery","首访用户转盘展示只一次","首访用户转盘抽奖展示后置 first_visitor_lottery_shown=Y，后续访问不再展示。","WenjuanDisplayService","查询转盘展示状态时按 first_visitor_lottery_shown 判断。",[{"dataset":"cust_company_survey_state","field":"first_visitor_lottery_shown"}],["ev-cust-survey-state-claim"]),
    ],
    [
        pattern("pat-survey-whitelist-by-company","查问卷白名单企业","SELECT * FROM cust_company_survey_whitelist WHERE company_id=:companyId AND enable='Y'",{"caliber_id":"cal-survey-whitelisted"},["ev-cust-survey-whitelist-check"]),
        pattern("pat-survey-answer-by-company","查企业调研答案","SELECT * FROM cust_survey_answer WHERE company_id=:companyId ORDER BY submit_time DESC",{"metric_id":"metric-survey-answer-count"},["ev-cust-survey-answer-submit"]),
    ],
    assumptions=["问卷星为外部问卷服务，只落本地白名单/首访状态/答案记录"],
))

# =========================================================================
# 8. customer-project-tools 项目码记录/推送配置/项目文件
# =========================================================================
new_evidence += [
    ev("ev-cust-project-code-record-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustProjectCodeRecordDO.java","cust_project_code_record 表字段定义"),
    ev("ev-cust-project-pushcust-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustProjectPushcustDO.java","cust_project_pushcust 表字段定义"),
    ev("ev-project-file-info-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/ProjectFileInfoDO.java","project_file_info 表字段定义"),
    ev("ev-cust-project-code-save","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustProjectRelEnhanceService.java:362-371","保存企业项目码校验记录"),
    ev("ev-cust-project-code-query","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustProjectRelEnhanceService.java:406-408","按企业查询项目码记录"),
    ev("ev-cust-project-push-query","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustProjectCustpushApplication.java:22-23","按来源/目标渠道查询项目跳转配置"),
    ev("ev-project-file-save","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/ProjectFileController.java:46-51","保存/更新项目文件"),
    ev("ev-project-file-detail","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/ProjectFileController.java:73","按 id 查询项目文件详情"),
]
code_record_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-project-code-record-schema"]),
    fld("company_id","company_id","bigint","企业id", refs=["ev-cust-project-code-record-schema"]),
    fld("use_id","use_id","bigint","用户id", refs=["ev-cust-project-code-record-schema"]),
    fld("channel_code","channel_code","varchar","渠道码", refs=["ev-cust-project-code-record-schema"]),
    fld("status","status","varchar","是否正确状态", refs=["ev-cust-project-code-record-schema"]),
    fld("company_type","company_type","varchar","企业角色", refs=["ev-cust-project-code-record-schema"]),
    fld("type","type","varchar","类型", refs=["ev-cust-project-code-record-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-project-code-record-schema"]),
]
pushcust_fields = [
    fld("id","id","bigint","表主键", refs=["ev-cust-project-pushcust-schema"]),
    fld("source_sso_channel","source_sso_channel","varchar","起始系统的SSO渠道", refs=["ev-cust-project-pushcust-schema"]),
    fld("target_sso_channel","target_sso_channel","varchar","跳转系统的SSO渠道", refs=["ev-cust-project-pushcust-schema"]),
    fld("project_id","project_id","varchar","项目id", refs=["ev-cust-project-pushcust-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-cust-project-pushcust-schema"]),
]
project_file_fields = [
    fld("id","id","bigint","表主键", refs=["ev-project-file-info-schema"]),
    fld("title","title","varchar","标题", refs=["ev-project-file-info-schema"]),
    fld("content","content","varchar","描述", refs=["ev-project-file-info-schema"]),
    fld("file_type","file_type","varchar","文件模块类型", refs=["ev-project-file-info-schema"]),
    fld("project_id","project_id","bigint","关联项目ID", refs=["ev-project-file-info-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-project-file-info-schema"]),
]
new_units.append(unit(
    "customer-project-tools", "项目码与项目文件", "product",
    "企业项目码校验记录、项目跳转渠道配置、项目文件保存/详情场景",
    "穿透 CustProjectRelEnhanceService 项目码记录、CustProjectCustpushApplication 渠道配置、ProjectFileController 文件保存/详情。",
    [
        concept("project-code-record","项目码记录","企业项目码校验记录 cust_project_code_record","cust_project_code_record","id",refs=["ev-cust-project-code-record-schema"]),
        concept("project-pushcust","项目跳转配置","项目客户跳转渠道配置 cust_project_pushcust","cust_project_pushcust","id",refs=["ev-cust-project-pushcust-schema"]),
        concept("project-file","项目文件","项目文件信息 project_file_info","project_file_info","id",refs=["ev-project-file-info-schema"]),
    ],
    [
        stage("project-code-save","项目码记录保存","企业提交项目码时保存校验记录","CustProjectRelEnhanceService",
             [de("read","cust_project_code_record",["id","company_id","channel_code","status","company_type","type","enable"],"company_id=:companyId AND channel_code=:channelCode","查项目码记录",["ev-cust-project-code-query"]),
              de("upsert","cust_project_code_record",["company_id","use_id","channel_code","status","company_type","type","enable"],"保存项目码记录","保存项目码校验记录",["ev-cust-project-code-save"])],
             next_stages=["project-push-query"], refs=["ev-cust-project-code-save"]),
        stage("project-push-query","项目跳转配置查询","按来源/目标 SSO 渠道查询项目跳转配置","CustProjectCustpushApplication.getDOBySourceTargetChannel",
             [de("read","cust_project_pushcust",["id","source_sso_channel","target_sso_channel","project_id","enable"],"source_sso_channel=:source AND target_sso_channel=:target","读跳转配置",["ev-cust-project-push-query"])],
             next_stages=["project-file-save"], refs=["ev-cust-project-push-query"]),
        stage("project-file-save","项目文件保存/详情","保存/更新项目文件，按 id 查询详情","ProjectFileController.saveOrUpdate/detail",
             [de("read","project_file_info",["id","title","content","file_type","project_id","enable"],"id=:id","读项目文件",["ev-project-file-detail"]),
              de("upsert","project_file_info",["title","content","file_type","project_id","enable"],"保存/更新项目文件","保存项目文件",["ev-project-file-save"])],
             refs=["ev-project-file-save"]),
    ],
    [
        dset("cust_project_code_record","cust_project_code_record","企业项目码记录",code_record_fields,refs=["ev-cust-project-code-record-schema"]),
        dset("cust_project_pushcust","cust_project_pushcust","项目客户跳转配置",pushcust_fields,refs=["ev-cust-project-pushcust-schema"]),
        dset("project_file_info","project_file_info","项目文件信息",project_file_fields,refs=["ev-project-file-info-schema"]),
    ],
    [
        metric("metric-project-code-record-count","项目码记录数","项目码校验记录数","cust_project_code_record","id",["ev-cust-project-code-save"]),
        metric("metric-project-file-count","项目文件数","项目文件记录数","project_file_info","id",["ev-project-file-save"]),
    ],
    [
        caliber("cal-project-code-by-channel","项目码渠道范围","按 channel_code + company_id 定位项目码记录","channel_code = :channelCode AND company_id = :companyId",[{"dataset":"cust_project_code_record","field":"channel_code"},{"dataset":"cust_project_code_record","field":"company_id"}],["ev-cust-project-code-query"]),
        caliber("cal-project-file-by-project","项目文件范围","按 project_id 查询项目文件","project_id = :projectId",[{"dataset":"project_file_info","field":"project_id"}],["ev-project-file-save"]),
    ],
    [
        rule("rule-project-code-validate","项目码校验结果留痕","企业提交项目码时按渠道码校验并保存 status 与类型，查询时按渠道码+企业过滤。","CustProjectRelEnhanceService","查询项目码提交记录时按 channel_code+company_id 过滤。",[{"dataset":"cust_project_code_record","field":"status"}],["ev-cust-project-code-save"]),
        rule("rule-project-push-channel","项目跳转按 SSO 渠道路由","项目客户推送按 source_sso_channel + target_sso_channel 定位唯一跳转配置。","CustProjectCustpushApplication.getDOBySourceTargetChannel","查询项目跳转目标时按来源+目标渠道匹配。",[{"dataset":"cust_project_pushcust","field":"source_sso_channel"},{"dataset":"cust_project_pushcust","field":"target_sso_channel"}],["ev-cust-project-push-query"]),
    ],
    [
        pattern("pat-project-code-by-company","查企业项目码记录","SELECT * FROM cust_project_code_record WHERE company_id=:companyId AND enable='Y'",{"caliber_id":"cal-project-code-by-channel"},["ev-cust-project-code-query"]),
        pattern("pat-project-file-by-project","查项目文件","SELECT * FROM project_file_info WHERE project_id=:projectId AND enable='Y'",{"caliber_id":"cal-project-file-by-project"},["ev-project-file-save"]),
    ],
))

# =========================================================================
# 9. tenant-interworking 租户互通产品/项目
# =========================================================================
new_evidence += [
    ev("ev-tenant-interworking-product-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantInterworkingProductDO.java","tenant_interworking_product 表字段定义"),
    ev("ev-tenant-interworking-project-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantInterworkingProjectDO.java","tenant_interworking_project 表字段定义"),
    ev("ev-tenant-interworking-product-create","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/controller/TenantInterworkingProductController.java:77-79","租户创建互通产品"),
    ev("ev-tenant-interworking-product-active","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/producttype/TenantInterworkingProductApplication.java:86-98","租户开通互通产品"),
    ev("ev-tenant-interworking-project-rel","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/TenantInterworkingProjectApplicationService.java:42-58","保存互通产品关联项目"),
    ev("ev-tenant-interworking-project-query","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/controller/TenantInterworkingProductController.java:142-143","按产品查询关联项目"),
]
inter_product_fields = [
    fld("id","id","bigint","表主键", refs=["ev-tenant-interworking-product-schema"]),
    fld("name","name","varchar","名称", refs=["ev-tenant-interworking-product-schema"]),
    fld("platform_product_id","platform_product_id","bigint","平台产品id", refs=["ev-tenant-interworking-product-schema"]),
    fld("tenant_id","tenant_id","bigint","租户id", refs=["ev-tenant-interworking-product-schema"]),
    fld("open_status","open_status","varchar","产品开通状态", dictionary={"Y":"已开通","P":"开通中","N":"未开通"}, refs=["ev-tenant-interworking-product-schema"]),
    fld("platform_product_code","platform_product_code","varchar","平台产品编号", refs=["ev-tenant-interworking-product-schema"]),
    fld("ref_tenant_interworking_product_tenant_setting_config","ref_tenant_interworking_product_tenant_setting_config","varchar","关联租户", refs=["ev-tenant-interworking-product-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-tenant-interworking-product-schema"]),
]
inter_project_fields = [
    fld("id","id","bigint","表主键", refs=["ev-tenant-interworking-project-schema"]),
    fld("product_id","product_id","bigint","产品id", refs=["ev-tenant-interworking-project-schema"]),
    fld("tenant_id","tenant_id","bigint","租户id", refs=["ev-tenant-interworking-project-schema"]),
    fld("platform_product_code","platform_product_code","varchar","平台产品编码", refs=["ev-tenant-interworking-project-schema"]),
    fld("project_id","project_id","bigint","项目id", refs=["ev-tenant-interworking-project-schema"]),
    fld("ref_tenant_interworking_project_tenant_interworking_product","ref_tenant_interworking_project_tenant_interworking_product","varchar","租户产品项目", refs=["ev-tenant-interworking-project-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-tenant-interworking-project-schema"]),
]
new_units.append(unit(
    "tenant-interworking", "租户互通产品与项目", "product",
    "租户互通产品创建/开通/取消、互通产品关联项目场景",
    "穿透 TenantInterworkingProductController 与 TenantInterworkingProductApplication、TenantInterworkingProjectApplicationService。",
    [
        concept("tenant-interworking-product","租户互通产品","租户互通产品 tenant_interworking_product","tenant_interworking_product","id",refs=["ev-tenant-interworking-product-schema"]),
        concept("tenant-interworking-project","互通产品项目","互通产品关联项目 tenant_interworking_project","tenant_interworking_project","id",refs=["ev-tenant-interworking-project-schema"]),
    ],
    [
        stage("inter-product-create","互通产品创建/开通","租户创建并开通互通产品","TenantInterworkingProductApplication.create/active",
             [de("read","tenant_interworking_product",["id","name","platform_product_id","tenant_id","open_status","platform_product_code","ref_tenant_interworking_product_tenant_setting_config","enable"],"tenant_id=:tenantId AND platform_product_id=:platformProductId","查重",["ev-tenant-interworking-product-create"]),
              de("upsert","tenant_interworking_product",["name","platform_product_id","tenant_id","open_status","platform_product_code","ref_tenant_interworking_product_tenant_setting_config","enable"],"创建/开通互通产品","保存互通产品",["ev-tenant-interworking-product-create","ev-tenant-interworking-product-active"])],
             next_stages=["inter-project-rel"], refs=["ev-tenant-interworking-product-create"]),
        stage("inter-project-rel","互通产品关联项目","保存/查询互通产品关联的项目","TenantInterworkingProjectApplicationService.relTenantProject",
             [de("read","tenant_interworking_project",["id","product_id","tenant_id","platform_product_code","project_id","ref_tenant_interworking_project_tenant_interworking_product","enable"],"product_id=:productId","读关联项目",["ev-tenant-interworking-project-query"]),
              de("upsert","tenant_interworking_project",["product_id","tenant_id","platform_product_code","project_id","ref_tenant_interworking_project_tenant_interworking_product","enable"],"保存关联项目","保存互通产品项目关系",["ev-tenant-interworking-project-rel"])],
             refs=["ev-tenant-interworking-project-rel"]),
    ],
    [
        dset("tenant_interworking_product","tenant_interworking_product","租户互通产品",inter_product_fields,refs=["ev-tenant-interworking-product-schema"]),
        dset("tenant_interworking_project","tenant_interworking_project","互通产品项目",inter_project_fields,refs=["ev-tenant-interworking-project-schema"]),
    ],
    [
        metric("metric-tenant-inter-product-count","互通产品数","租户互通产品数","tenant_interworking_product","id",["ev-tenant-interworking-product-create"]),
        metric("metric-tenant-inter-project-count","互通产品项目数","互通产品关联项目数","tenant_interworking_project","id",["ev-tenant-interworking-project-rel"]),
    ],
    [
        caliber("cal-tenant-inter-product-open","已开通互通产品","open_status=Y 的租户互通产品","open_status = 'Y'",[{"dataset":"tenant_interworking_product","field":"open_status"}],["ev-tenant-interworking-product-active"]),
        caliber("cal-tenant-inter-project-by-product","互通产品项目范围","按 product_id 查询互通产品关联项目","product_id = :productId",[{"dataset":"tenant_interworking_project","field":"product_id"}],["ev-tenant-interworking-project-query"]),
    ],
    [
        rule("rule-tenant-inter-product-unique","互通产品每租户每平台产品唯一","创建互通产品时按 tenantId + platformProductId 查重，已存在直接返回。","TenantInterworkingProductApplication.create","查询租户互通产品时同一平台产品最多一条。",[{"dataset":"tenant_interworking_product","field":"tenant_id"},{"dataset":"tenant_interworking_product","field":"platform_product_id"}],["ev-tenant-interworking-product-create"]),
        rule("rule-tenant-inter-project-rel","互通产品项目关系按产品维护","保存互通产品项目关系时先按产品清理旧关系再写入新关系。","TenantInterworkingProjectApplicationService.relTenantProject","查询互通产品项目时以产品维度聚合。",[{"dataset":"tenant_interworking_project","field":"product_id"}],["ev-tenant-interworking-project-rel"]),
    ],
    [
        pattern("pat-tenant-inter-product-open","查已开通互通产品","SELECT * FROM tenant_interworking_product WHERE tenant_id=:tenantId AND open_status='Y' AND enable='Y'",{"caliber_id":"cal-tenant-inter-product-open"},["ev-tenant-interworking-product-create"]),
        pattern("pat-tenant-inter-project-by-product","查互通产品项目","SELECT * FROM tenant_interworking_project WHERE product_id=:productId AND enable='Y'",{"caliber_id":"cal-tenant-inter-project-by-product"},["ev-tenant-interworking-project-query"]),
    ],
))

# =========================================================================
# 10. wechat-project-statistics 微信项目审批与统计
# =========================================================================
new_evidence += [
    ev("ev-wechat-approval-apply-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/WechatProjectApprovalApplyDO.java","wechat_project_approval_apply 表字段定义"),
    ev("ev-wechat-approval-history-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/WechatProjectApprovalFieldHistoryDO.java","wechat_project_approval_field_history 表字段定义"),
    ev("ev-wec-project-operation-rel-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/WecProjectOperationRelDO.java","wec_project_operation_rel 表字段定义"),
    ev("ev-wec-project-cust-operation-rel-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/WecProjectCustOperationRelDO.java","wec_project_cust_operation_rel 表字段定义"),
    ev("ev-operation-user-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/OperationUserDO.java","operation_user 表字段定义"),
    ev("ev-wechat-approval-import","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/WechatProjectApprovalApplication.java:148-209","微信项目立项审批数据导入"),
    ev("ev-wechat-approval-update-group","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/WechatProjectApprovalApplication.java:878-884","更新微信项目立项审批分组"),
    ev("ev-wechat-approval-history","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ProjectStatisticsApplication.java:713-718","按 applyId 查询方案经理变更历史"),
    ev("ev-wec-operation-rel-query","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/ProjectReportController.java:1552-1558","按项目查询微企链运营关系"),
    ev("ev-wec-cust-operation-rel-query","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/ProjectReportController.java:1810-1831","按项目查询微企链客户运营关系"),
    ev("ev-operation-user-query","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/ProjectReportController.java:1477-1479","按运营中台 id 查询运营人员"),
]
wechat_apply_fields = [
    fld("id","id","bigint","表主键", refs=["ev-wechat-approval-apply-schema"]),
    fld("sp_no","sp_no","varchar","企微审批编号", refs=["ev-wechat-approval-apply-schema"]),
    fld("sp_type","sp_type","varchar","类型", refs=["ev-wechat-approval-apply-schema"]),
    fld("project_approval_name","project_approval_name","varchar","立项名称", refs=["ev-wechat-approval-apply-schema"]),
    fld("sp_pass_time","sp_pass_time","datetime","立项审批通过时间", refs=["ev-wechat-approval-apply-schema"]),
    fld("solution_manager","solution_manager","varchar","方案经理", refs=["ev-wechat-approval-apply-schema"]),
    fld("business_manager","business_manager","varchar","业务经理", refs=["ev-wechat-approval-apply-schema"]),
    fld("project_id","project_id","bigint","关联的项目id", refs=["ev-wechat-approval-apply-schema"]),
    fld("data_source","data_source","varchar","数据来源", refs=["ev-wechat-approval-apply-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-wechat-approval-apply-schema"]),
]
wechat_history_fields = [
    fld("id","id","bigint","表主键", refs=["ev-wechat-approval-history-schema"]),
    fld("apply_id","apply_id","bigint","关联 wechat_project_approval_apply.id", refs=["ev-wechat-approval-history-schema"]),
    fld("sp_no","sp_no","varchar","审批编号", refs=["ev-wechat-approval-history-schema"]),
    fld("field_name","field_name","varchar","列名", refs=["ev-wechat-approval-history-schema"]),
    fld("field_label","field_label","varchar","中文标签", refs=["ev-wechat-approval-history-schema"]),
    fld("old_value","old_value","varchar","变更前值", refs=["ev-wechat-approval-history-schema"]),
    fld("new_value","new_value","varchar","变更后值", refs=["ev-wechat-approval-history-schema"]),
    fld("change_source","change_source","varchar","变更来源", refs=["ev-wechat-approval-history-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-wechat-approval-history-schema"]),
]
wec_project_fields = [
    fld("id","id","bigint","表主键", refs=["ev-wec-project-operation-rel-schema"]),
    fld("wec_project_id","wec_project_id","varchar","微企链项目id", refs=["ev-wec-project-operation-rel-schema"]),
    fld("wechat_audit_no","wechat_audit_no","varchar","企微审批编号", refs=["ev-wec-project-operation-rel-schema"]),
    fld("solution_manager","solution_manager","varchar","方案经理", refs=["ev-wec-project-operation-rel-schema"]),
    fld("business_manager","business_manager","varchar","业务经理", refs=["ev-wec-project-operation-rel-schema"]),
    fld("first_settlement_time","first_settlement_time","datetime","首笔落地时间", refs=["ev-wec-project-operation-rel-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-wec-project-operation-rel-schema"]),
]
wec_cust_fields = [
    fld("id","id","bigint","表主键", refs=["ev-wec-project-cust-operation-rel-schema"]),
    fld("wec_rel_id","wec_rel_id","varchar","微企链关联关系id", refs=["ev-wec-project-cust-operation-rel-schema"]),
    fld("company_id","company_id","varchar","微企链企业id", refs=["ev-wec-project-cust-operation-rel-schema"]),
    fld("company_type","company_type","varchar","微企链企业角色", refs=["ev-wec-project-cust-operation-rel-schema"]),
    fld("project_id","project_id","varchar","微企链项目id", refs=["ev-wec-project-cust-operation-rel-schema"]),
    fld("top_flag","top_flag","varchar","置顶标识", refs=["ev-wec-project-cust-operation-rel-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-wec-project-cust-operation-rel-schema"]),
]
operation_user_fields = [
    fld("id","id","bigint","表主键", refs=["ev-operation-user-schema"]),
    fld("operation_id","operation_id","varchar","运营中台id", refs=["ev-operation-user-schema"]),
    fld("operation_name","operation_name","varchar","运营人员姓名", refs=["ev-operation-user-schema"]),
    fld("operation_group","operation_group","varchar","运营组别", refs=["ev-operation-user-schema"]),
    fld("status","status","varchar","用户状态标识", refs=["ev-operation-user-schema"]),
    fld("deleted","deleted","varchar","删除标识", refs=["ev-operation-user-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-operation-user-schema"]),
]
new_units.append(unit(
    "wechat-project-statistics", "微信项目审批与统计", "project",
    "微信项目立项审批数据导入/更新、字段变更历史、微企链运营关系、运营人员查询场景",
    "穿透 WechatProjectApprovalApplication 导入/更新，ProjectStatisticsApplication 查询字段历史，ProjectReportController 查询微企链运营关系与运营人员。",
    [
        concept("wechat-project-approval-apply","微信项目立项审批","微信项目立项审批数据 wechat_project_approval_apply","wechat_project_approval_apply","id",refs=["ev-wechat-approval-apply-schema"]),
        concept("wechat-project-approval-history","立项审批字段历史","立项审批字段变更历史 wechat_project_approval_field_history","wechat_project_approval_field_history","id",refs=["ev-wechat-approval-history-schema"]),
        concept("wec-project-operation","微企链项目运营关系","微企链项目运营关系 wec_project_operation_rel","wec_project_operation_rel","id",refs=["ev-wec-project-operation-rel-schema"]),
        concept("wec-project-cust-operation","微企链客户运营关系","微企链客户运营关系 wec_project_cust_operation_rel","wec_project_cust_operation_rel","id",refs=["ev-wec-project-cust-operation-rel-schema"]),
        concept("operation-user","运营人员","运营人员 operation_user","operation_user","id",refs=["ev-operation-user-schema"]),
    ],
    [
        stage("wechat-approval-import","微信立项审批导入/更新","导入微信项目立项审批数据，更新分组与方案经理","WechatProjectApprovalApplication.importWechatApprovalInfo",
             [de("read","wechat_project_approval_apply",["id","sp_no","sp_type","project_approval_name","sp_pass_time","solution_manager","business_manager","project_id","data_source","enable"],"sp_no=:spNo","查重",["ev-wechat-approval-import"]),
              de("upsert","wechat_project_approval_apply",["sp_no","sp_type","project_approval_name","sp_pass_time","solution_manager","business_manager","project_id","data_source","enable"],"导入/更新","保存微信立项审批数据",["ev-wechat-approval-import","ev-wechat-approval-update-group"])],
             next_stages=["history-query"], refs=["ev-wechat-approval-import"]),
        stage("history-query","字段变更历史查询","按 applyId/spNo 查询方案经理等字段变更历史","ProjectStatisticsApplication 查询",
             [de("read","wechat_project_approval_field_history",["id","apply_id","sp_no","field_name","field_label","old_value","new_value","change_source","enable"],"apply_id=:applyId AND field_name=:fieldName","读字段历史",["ev-wechat-approval-history"])],
             next_stages=["wec-operation-query"], refs=["ev-wechat-approval-history"]),
        stage("wec-operation-query","微企链运营关系查询","按项目查询微企链项目/客户运营关系及运营人员","ProjectReportController",
             [de("read","wec_project_operation_rel",["id","wec_project_id","wechat_audit_no","solution_manager","business_manager","first_settlement_time","enable"],"wec_project_id=:wecProjectId","读项目运营关系",["ev-wec-operation-rel-query"]),
              de("read","wec_project_cust_operation_rel",["id","wec_rel_id","company_id","company_type","project_id","top_flag","enable"],"project_id=:wecProjectId","读客户运营关系",["ev-wec-cust-operation-rel-query"]),
              de("read","operation_user",["id","operation_id","operation_name","operation_group","status","deleted","enable"],"operation_id=:operationId","读运营人员",["ev-operation-user-query"])],
             refs=["ev-wec-operation-rel-query"]),
    ],
    [
        dset("wechat_project_approval_apply","wechat_project_approval_apply","微信项目立项审批数据",wechat_apply_fields,refs=["ev-wechat-approval-apply-schema"]),
        dset("wechat_project_approval_field_history","wechat_project_approval_field_history","微信项目立项审批字段历史",wechat_history_fields,refs=["ev-wechat-approval-history-schema"]),
        dset("wec_project_operation_rel","wec_project_operation_rel","微企链项目运营关系",wec_project_fields,refs=["ev-wec-project-operation-rel-schema"]),
        dset("wec_project_cust_operation_rel","wec_project_cust_operation_rel","微企链客户运营关系",wec_cust_fields,refs=["ev-wec-project-cust-operation-rel-schema"]),
        dset("operation_user","operation_user","运营人员",operation_user_fields,refs=["ev-operation-user-schema"]),
    ],
    [
        metric("metric-wechat-approval-count","微信立项审批数","微信项目立项审批记录数","wechat_project_approval_apply","id",["ev-wechat-approval-import"]),
        metric("metric-wechat-history-count","字段历史数","立项审批字段变更历史数","wechat_project_approval_field_history","id",["ev-wechat-approval-history"]),
        metric("metric-operation-user-count","运营人员数","运营人员记录数","operation_user","id",["ev-operation-user-query"]),
    ],
    [
        caliber("cal-wechat-approval-by-sp","微信立项审批范围","按 sp_no 定位微信立项审批","sp_no = :spNo",[{"dataset":"wechat_project_approval_apply","field":"sp_no"}],["ev-wechat-approval-import"]),
        caliber("cal-history-by-apply","立项审批字段历史范围","按 apply_id 查询字段变更历史","apply_id = :applyId",[{"dataset":"wechat_project_approval_field_history","field":"apply_id"}],["ev-wechat-approval-history"]),
        caliber("cal-operation-user-active","有效运营人员","deleted != 'Y' 且 enable='Y' 的运营人员","deleted <> 'Y' AND enable = 'Y'",[{"dataset":"operation_user","field":"deleted"},{"dataset":"operation_user","field":"enable"}],["ev-operation-user-query"]),
    ],
    [
        rule("rule-wechat-approval-upsert","微信立项审批按 sp_no upsert","微信项目立项审批导入按 sp_no 查重，存在则更新分组/方案经理/统计字段。","WechatProjectApprovalApplication.importWechatApprovalInfo","查询立项审批时 sp_no 唯一。",[{"dataset":"wechat_project_approval_apply","field":"sp_no"}],["ev-wechat-approval-import"]),
        rule("rule-history-field-source","字段历史记录变更来源","字段变更历史由 FieldHistoryWriter 按列写入 change_source 与新旧值。","ProjectStatisticsApplication","查询字段历史时按 apply_id+field_name 过滤，old/new 成对出现。",[{"dataset":"wechat_project_approval_field_history","field":"field_name"},{"dataset":"wechat_project_approval_field_history","field":"change_source"}],["ev-wechat-approval-history"]),
        rule("rule-wec-cust-top","微企链客户运营置顶","微企链客户运营关系按 project_id 查询，top_flag=1 为置顶企业。","ProjectReportController","查询项目客户运营关系时可用 top_flag 排序。",[{"dataset":"wec_project_cust_operation_rel","field":"top_flag"}],["ev-wec-cust-operation-rel-query"]),
    ],
    [
        pattern("pat-wechat-approval-by-sp","查微信立项审批","SELECT * FROM wechat_project_approval_apply WHERE sp_no=:spNo AND enable='Y'",{"caliber_id":"cal-wechat-approval-by-sp"},["ev-wechat-approval-import"]),
        pattern("pat-wechat-history-by-apply","查立项审批字段历史","SELECT * FROM wechat_project_approval_field_history WHERE apply_id=:applyId ORDER BY create_time DESC",{"caliber_id":"cal-history-by-apply"},["ev-wechat-approval-history"]),
    ],
    assumptions=["微企链为外部数据源，wec_* 关系表为本地同步副本"],
))

# =========================================================================
# 11. authorization-agreement 授权协议
# =========================================================================
new_evidence += [
    ev("ev-authorization-agreement-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/AuthorizationAgreementDO.java","authorization_agreement 表字段定义"),
    ev("ev-authorization-agreement-check","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/CustAuthAgreementDomainService.java:125-146","查询企业产品授权书认证状态"),
    ev("ev-authorization-agreement-save","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/CustAuthAgreementDomainService.java:246-283","保存/更新授权协议认证状态"),
]
auth_agreement_fields = [
    fld("id","id","bigint","表主键", refs=["ev-authorization-agreement-schema"]),
    fld("cust_id","cust_id","bigint","企业id", refs=["ev-authorization-agreement-schema"]),
    fld("cust_manager_id","cust_manager_id","bigint","企业管理员id", refs=["ev-authorization-agreement-schema"]),
    fld("platform_product_code","platform_product_code","varchar","平台产品id", refs=["ev-authorization-agreement-schema"]),
    fld("authed_status","authed_status","varchar","授权书认证状态", refs=["ev-authorization-agreement-schema"]),
    fld("company_type","company_type","varchar","企业角色", refs=["ev-authorization-agreement-schema"]),
    fld("creation_type","creation_type","varchar","授权创建类型", refs=["ev-authorization-agreement-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-authorization-agreement-schema"]),
]
new_units.append(unit(
    "authorization-agreement", "授权协议", "product",
    "企业产品授权书认证状态查询、保存/更新场景",
    "穿透 CustAuthAgreementDomainService：查询企业管理员在各平台产品下的授权书认证状态，保存/更新授权协议。",
    [
        concept("authorization-agreement","授权协议","企业产品授权书 authorization_agreement","authorization_agreement","id",refs=["ev-authorization-agreement-schema"]),
        concept("authorization-authed","已授权","authed_status=Y 的授权协议","authorization_agreement","authed_status",{"Y":"已授权","N":"未授权"},refs=["ev-authorization-agreement-check"]),
    ],
    [
        stage("auth-agreement-check","授权状态检查","按企业管理员+产品查询授权书认证状态","CustAuthAgreementDomainService.listAuthorizationAgreement",
             [de("read","authorization_agreement",["id","cust_id","cust_manager_id","platform_product_code","authed_status","company_type","creation_type","enable"],"cust_id=:companyId AND cust_manager_id=:managerUserId","读授权状态",["ev-authorization-agreement-check"])],
             next_stages=["auth-agreement-save"], refs=["ev-authorization-agreement-check"]),
        stage("auth-agreement-save","授权状态保存","保存/更新授权协议，按产品维度更新认证状态","CustAuthAgreementDomainService",
             [de("read","authorization_agreement",["id","cust_id","cust_manager_id","platform_product_code","authed_status","enable"],"cust_id=:companyId AND cust_manager_id=:managerUserId AND platform_product_code=:productCode","读指定产品授权",["ev-authorization-agreement-save"]),
              de("upsert","authorization_agreement",["cust_id","cust_manager_id","platform_product_code","authed_status","company_type","creation_type","enable"],"保存/更新","保存授权协议",["ev-authorization-agreement-save"])],
             refs=["ev-authorization-agreement-save"]),
    ],
    [
        dset("authorization_agreement","authorization_agreement","企业产品授权书",auth_agreement_fields,refs=["ev-authorization-agreement-schema"]),
    ],
    [
        metric("metric-auth-agreement-count","授权协议数","企业产品授权书记录数","authorization_agreement","id",["ev-authorization-agreement-check"]),
    ],
    [
        caliber("cal-auth-agreement-authed","已授权协议","authed_status=Y 的授权协议","authed_status = 'Y'",[{"dataset":"authorization_agreement","field":"authed_status"}],["ev-authorization-agreement-check"]),
    ],
    [
        rule("rule-auth-agreement-by-product","授权协议按产品认证","授权协议按平台产品维度保存，认证状态按产品独立判定。","CustAuthAgreementDomainService","查询企业授权状态时按平台产品过滤，不能只看企业维度。",[{"dataset":"authorization_agreement","field":"platform_product_code"}],["ev-authorization-agreement-check"]),
    ],
    [
        pattern("pat-auth-agreement-by-company","查企业授权协议","SELECT * FROM authorization_agreement WHERE cust_id=:custId AND enable='Y'",{"caliber_id":"cal-auth-agreement-authed"},["ev-authorization-agreement-check"]),
    ],
))

# =========================================================================
# 12. platform-product-client 平台产品客户端
# =========================================================================
new_evidence += [
    ev("ev-platform-product-client-schema","database_schema","pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/PlatformProductClientDO.java","platform_product_client 表字段定义"),
    ev("ev-platform-product-client-notice","code_path","lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustNoticeService.java:91-96","按平台产品配置客户端链接/类型"),
]
ppc_fields = [
    fld("id","id","bigint","表主键", refs=["ev-platform-product-client-schema"]),
    fld("platform_product_id","platform_product_id","bigint","平台产品id", refs=["ev-platform-product-client-schema"]),
    fld("url","url","varchar","产品url", refs=["ev-platform-product-client-schema"]),
    fld("client_type","client_type","varchar","客户端类型方式", refs=["ev-platform-product-client-schema"]),
    fld("status","status","varchar","启用状态", refs=["ev-platform-product-client-schema"]),
    fld("link_type","link_type","varchar","链接类型", refs=["ev-platform-product-client-schema"]),
    fld("wx_flag","wx_flag","varchar","是否小程序", refs=["ev-platform-product-client-schema"]),
    fld("enable","enable","varchar","enable", refs=["ev-platform-product-client-schema"]),
]
new_units.append(unit(
    "platform-product-client", "平台产品客户端", "product",
    "平台产品客户端入口配置（URL/客户端类型/链接类型/是否小程序）查询场景",
    "穿透 CustNoticeService 查询平台产品客户端配置并组装入口。",
    [
        concept("platform-product-client","平台产品客户端","平台产品客户端配置 platform_product_client","platform_product_client","id",refs=["ev-platform-product-client-schema"]),
    ],
    [
        stage("platform-product-client-query","客户端配置查询","按平台产品查询客户端入口配置","CustNoticeService",
             [de("read","platform_product_client",["id","platform_product_id","url","client_type","status","link_type","wx_flag","enable"],"platform_product_id=:platformProductId AND enable='Y'","读客户端配置",["ev-platform-product-client-notice"])],
             refs=["ev-platform-product-client-notice"]),
    ],
    [
        dset("platform_product_client","platform_product_client","平台产品客户端配置",ppc_fields,refs=["ev-platform-product-client-schema"]),
    ],
    [
        metric("metric-platform-product-client-count","平台产品客户端数","平台产品客户端配置数","platform_product_client","id",["ev-platform-product-client-notice"]),
    ],
    [
        caliber("cal-platform-product-client-active","启用客户端","status=Y 且 enable=Y 的平台产品客户端","status = 'Y' AND enable = 'Y'",[{"dataset":"platform_product_client","field":"status"},{"dataset":"platform_product_client","field":"enable"}],["ev-platform-product-client-notice"]),
    ],
    [
        rule("rule-platform-product-client-link","客户端链接按产品配置","平台产品客户端按 platform_product_id 配置 url/link_type/wx_flag，查询入口时按产品过滤。","CustNoticeService","查询产品客户端入口时按平台产品 id 过滤。",[{"dataset":"platform_product_client","field":"platform_product_id"}],["ev-platform-product-client-notice"]),
    ],
    [
        pattern("pat-platform-product-client-by-product","查平台产品客户端","SELECT * FROM platform_product_client WHERE platform_product_id=:platformProductId AND status='Y' AND enable='Y'",{"caliber_id":"cal-platform-product-client-active"},["ev-platform-product-client-notice"]),
    ],
))

# =========================================================================
# write files / update manifest / relationships
# =========================================================================
(units_dir := PKG / "units").mkdir(exist_ok=True)
def write_yaml(path, data):
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")

for u in new_units:
    write_yaml(units_dir / f"{u['unit_id']}.yaml", u)

manifest_path = PKG / "knowledge-package.yaml"
manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
existing_ids = {e["evidence_id"] for e in manifest["evidence"]}
for e in new_evidence:
    if e["evidence_id"] not in existing_ids:
        manifest["evidence"].append(e)
        existing_ids.add(e["evidence_id"])
for u in new_units:
    p = f"units/{u['unit_id']}.yaml"
    if p not in manifest["units"]:
        manifest["units"].append(p)
write_yaml(manifest_path, manifest)

# package relationships
rel_path = PKG / "relationships.yaml"
rel_doc = yaml.safe_load(rel_path.read_text(encoding="utf-8"))
rels = rel_doc["relationships"]
new_rels = [
    {"left_table":"cust_change_record","left_field":"cust_id","right_table":"cust_company_info","right_field":"id","evidence":"write-flow:CustCompanyInfoApplication.java:7396","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"cust_oper_change_record","left_field":"company_id","right_table":"cust_company_info","right_field":"id","evidence":"read-flow:OperChangeRecordApplication.java:45","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"cust_head_company_info","left_field":"ref_cust_head_company_info_cust_company_info","right_table":"cust_company_info","right_field":"code","evidence":"write-flow:PlatFormMigratoryApplication.java:1765","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"cust_shareholder_info","left_field":"ref_cust_company_info","right_table":"cust_company_info","right_field":"code","evidence":"read-flow:ApplyCompanyInfoApplication.java:191","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"cust_company_lifecycle_info","left_field":"company_id","right_table":"cust_company_info","right_field":"id","evidence":"read-flow:CustCompanyInfoApplication.java:7136","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"cust_auth_application","left_field":"ref_cust_company_info","right_table":"cust_company_info","right_field":"code","evidence":"write-flow:SubmitCustInfoEnhanceService.java:136","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"cust_interworking_product","left_field":"ref_cust_interworking_product_cust_company_info","right_table":"cust_company_info","right_field":"code","evidence":"read-flow:CustCompanyUtilApplication.java:318","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"cust_group_rel","left_field":"cust_id","right_table":"cust_company_info","right_field":"id","evidence":"read-flow:CustProductApplicationService.java:218","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"cust_certification_info","left_field":"ref_cust_company_info","right_table":"cust_company_info","right_field":"code","evidence":"read-flow:FaceVerifyController.java:124","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"ca_certification_info","left_field":"cust_id","right_table":"cust_company_info","right_field":"id","evidence":"read-flow:CaCertificationInfoAppServiceImpl.java:125","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"ca_fee_company","left_field":"certification_no","right_table":"cust_company_info","right_field":"certification_no","evidence":"read-flow:CaFeeCompanyCaStatusApplication.java:59","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"ca_fee_order","left_field":"company_id","right_table":"cust_company_info","right_field":"id","evidence":"write-flow:CaFeeOrderApplication.java:47","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"ca_fee_project_config","left_field":"project_id","right_table":"tenant_project","right_field":"id","evidence":"read-flow:CaFeeProjectConfigApplication.java:29","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"tenant_interworking_product","left_field":"platform_product_id","right_table":"platform_product","right_field":"id","evidence":"write-flow:TenantInterworkingProductApplication.java:74","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"tenant_interworking_project","left_field":"product_id","right_table":"tenant_interworking_product","right_field":"id","evidence":"read-flow:TenantInterworkingProductController.java:142","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"wechat_project_approval_field_history","left_field":"apply_id","right_table":"wechat_project_approval_apply","right_field":"id","evidence":"read-flow:ProjectStatisticsApplication.java:713","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"authorization_agreement","left_field":"cust_id","right_table":"cust_company_info","right_field":"id","evidence":"read-flow:CustAuthAgreementDomainService.java:125","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"platform_product_client","left_field":"platform_product_id","right_table":"platform_product","right_field":"id","evidence":"read-flow:CustNoticeService.java:91","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
    {"left_table":"project_file_info","left_field":"project_id","right_table":"tenant_project","right_field":"id","evidence":"write-flow:ProjectFileController.java:46","relationship_type":"EQUI_JOIN","cardinality":"many_to_one"},
]
seen = {(r["left_table"], r["left_field"], r["right_table"], r["right_field"]) for r in rels}
for r in new_rels:
    key = (r["left_table"], r["left_field"], r["right_table"], r["right_field"])
    if key not in seen:
        rels.append(r)
        seen.add(key)
write_yaml(rel_path, rel_doc)

print("added units", len(new_units), "evidence total", len(manifest["evidence"]), "unit total", len(manifest["units"]), "relationships", len(rels))
