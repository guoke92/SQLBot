# -*- coding: utf-8 -*-
"""Build KnowledgePackageV2 v12 first 3 modules."""
import yaml
from pathlib import Path

ROOT = Path("/Users/fanjunwei/Projects/SQLBot/data/knowledge-packages/v12")
REPO = "/Users/fanjunwei/IdeaProjects/pplatform-web"
REV = "ee434954e465713176e5bd52119eedde5ebe531b"

SRC_ID = "src-pplatform-web"

def src(path, line=""):
    return path if not line else f"{path}:{line}"

# ---------------------------------------------------------------------------
# sources / evidence
# ---------------------------------------------------------------------------
sources = [
    {
        "source_id": SRC_ID,
        "kind": "git_repository",
        "locator": REPO,
        "repository_revision": REV,
        "content_hash": REV,
    }
]

# shorthand: evidence list built dynamically later
evidence = []

def ev(evidence_id, kind, locator, claim=""):
    return {
        "evidence_id": evidence_id,
        "source_id": SRC_ID,
        "evidence_kind": kind,
        "locator": locator,
        "claim": claim,
    }

# -- customer onboarding evidence --
ev_defs = [
    # schema
    ("ev-company-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustCompanyInfoDO.java", "cust_company_info 表字段定义（@TableName + @ApiModelProperty）"),
    ("ev-person-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustPersonInfoDO.java", "cust_person_info 表字段定义"),
    ("ev-build-record-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustBuildRecordDO.java", "cust_build_record 表字段定义"),
    ("ev-cust-project-rel-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/CustProjectRelDO.java", "cust_project_rel 表字段定义"),
    ("ev-tenant-project-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProjectDO.java", "tenant_project 表字段定义"),
    ("ev-platform-product-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/PlatformProductDO.java", "platform_product 表字段定义"),
    ("ev-tenant-setting-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantSettingConfigDO.java", "tenant_setting_config 表字段定义"),
    # enum evidence
    ("ev-cust-build-status-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/enums/CustBuildStatusEnum.java:14-30", "cust_build_status 业务枚举取值"),
    ("ev-cust-status-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/enums/CustStatusEnum.java:19-24", "cust_status 业务枚举取值"),
    ("ev-check-status-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/constants/OperApiConstants.java:202-209", "check_status 审核状态枚举取值"),
    ("ev-user-type-dict", "enum_source", "lowcode-pplatform-common/lowcode-pplatform-common-api/src/main/java/com/lls/lowcode/pplatform/common/enums/UserTypeEnum.java:15-17", "user_type 联系人类型枚举取值"),
    ("ev-company-type-dict", "enum_source", "lowcode-pplatform-common/lowcode-pplatform-common-api/src/main/java/com/lls/lowcode/pplatform/common/enums/CustCompanyTypeEnum.java:15-20", "cust_company_type 企业角色枚举取值"),
    ("ev-cust-source-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/enums/CustSourceEnum.java:1", "cust_source 建档数据来源枚举"),
    # code paths
    ("ev-onboarding-regself", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/facade/cust/OperCustFacade.java:959-1026", "自主注册建档入口：锁、在途校验、推送运营中台、写 check_status、保存建档记录"),
    ("ev-onboarding-get-company", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/BaseAccessOperProcess.java:176-177", "按 id 读 cust_company_info"),
    ("ev-onboarding-get-person", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/BaseAccessOperProcess.java:185-187", "按 id + ref_cust_company_info 读 cust_person_info"),
    ("ev-onboarding-update-company", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/BaseAccessOperProcess.java:199-200", "按主键更新 cust_company_info"),
    ("ev-onboarding-update-user", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/BaseAccessOperProcess.java:208-209", "按主键更新 cust_person_info"),
    ("ev-onboarding-set-project", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/facade/cust/OperCustFacade.java:1043-1075", "无项目码自动绑定默认项目，读 tenant_setting_config/tenant_project/platform_product"),
    ("ev-onboarding-save-project-rel", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/facade/cust/OperCustFacade.java:1078-1100", "保存 cust_project_rel，供应商+ACFLOW/ORDER 时 status=1"),
    ("ev-onboarding-build-record", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/facade/cust/OperCustFacade.java:889-900", "保存 cust_build_record（cust_id/person_id 来自形参传播）"),
    # project approval
    ("ev-proj-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProjectApprovalDO.java", "tenant_project_approval 表字段定义"),
    ("ev-proj-biz-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProjectApprovalBusinessInfoDO.java", "tenant_project_approval_business_info 表字段定义"),
    ("ev-proj-flow-config-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProjectApprovalFlowConfigDO.java", "tenant_project_approval_flow_config 表字段定义"),
    ("ev-proj-flow-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProjectApprovalFlowDO.java", "tenant_project_approval_flow 表字段定义"),
    ("ev-proj-node-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProjectApprovalFlowNodeDO.java", "tenant_project_approval_flow_node 表字段定义"),
    ("ev-proj-credit-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProjectApprovalFlowCreditDO.java", "tenant_project_approval_flow_credit 表字段定义"),
    ("ev-proj-file-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProjectApprovalFlowFileDO.java", "tenant_project_approval_flow_file 表字段定义"),
    ("ev-proj-wf-status-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/enums/ProjectApprovalWorkflowStatusEnum.java:1", "wf_status 工作流状态枚举"),
    ("ev-proj-node-status-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/enums/ProjectApprovalNodeStatusEnum.java:1", "node_status 节点状态枚举"),
    ("ev-proj-project-status-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/enums/ProjectStatusEnum.java:1", "project_status 项目状态枚举"),
    ("ev-proj-flow-code-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/enums/ProjectApprovalFlowCodeEnum.java:1", "flow_code 流程配置编码枚举"),
    ("ev-proj-project-type-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/enums/ProjectApprovalProjectTypeEnum.java:1", "project_type 项目类型枚举"),
    ("ev-proj-node-code-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/enums/ProjectApprovalNodeCodeEnum.java:1", "node_code 节点编码枚举"),
    ("ev-proj-operate-type-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/domain/enums/ProjectApprovalOperateTypeEnum.java:1", "operate_type 操作类型枚举"),
    ("ev-proj-create-approval", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:371-408", "创建项目上线审批：insert approval + 回写 project.project_approval_id"),
    ("ev-proj-copy-approval", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:994-1066", "复制审批：读原审批/流程/业务信息，生成新审批并置旧 is_latest=N"),
    ("ev-proj-list-flow-config", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:500-506", "按 flow_code 查询审批流程配置节点"),
    ("ev-proj-submit", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:549-647", "提交/暂存上线审批：先删后增 flow，回写 sp_no，更新 approval"),
    ("ev-proj-start-workflow", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:695-707", "启动工作流并更新 wf_status=RUNNING"),
    ("ev-proj-handle-status", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:716-777", "终态更新 approval.wf_status 并触发项目生效/AMS 推送"),
    ("ev-proj-effective", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:777-795", "审批通过后置 tenant_project 为已生效"),
    ("ev-proj-desk-agree", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalDeskApplication.java:112-196", "同意节点：insert flow_node，法务经办回写 is_low_risk，业务经理写入授信"),
    ("ev-proj-desk-back-reject", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalDeskApplication.java:198-271", "退回/驳回节点：insert flow_node + 更新 flow.node_status"),
    ("ev-proj-desk-build-node", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalDeskApplication.java:448-480", "构建 flow_node 并关联 approval.code / flow.code"),
    ("ev-proj-desk-save-credit", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalDeskApplication.java:485-510", "业务经理同意时写入/覆盖授信信息"),
    ("ev-proj-desk-media-file", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalDeskApplication.java:630-671", "审批文件落库 flow_file 并关联 approval/flow_node"),
    # funding rule
    ("ev-fund-info-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/FundingRuleInfoDO.java", "funding_rule_info 表字段定义"),
    ("ev-fund-detail-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/FundingRuleDetailDO.java", "funding_rule_detail 表字段定义"),
    ("ev-fund-front-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/FundingRuleFrontCfgDO.java", "funding_rule_front_cfg 表字段定义"),
    ("ev-fund-rule-status-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/enums/RuleStatusEnum.java:1", "rule_status 规则状态枚举"),
    ("ev-fund-rule-layer-dict", "enum_source", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/enums/RuleLayerEnum.java:1", "rule_layer 规则层枚举"),
    ("ev-fund-save-rule", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:415-533", "保存/更新资金方规则：新增查重、插入 info、按 front_cfg 匹配插入/更新 detail、更新 version"),
    ("ev-fund-active-rule", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:287-303", "生效规则：更新 rule_status=ACTIVE"),
    ("ev-fund-inactive-rule", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:308-317", "失效规则：更新 rule_status=INACTIVE"),
    ("ev-fund-query-front", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:322-345", "按产品查询前端规则页面配置"),
    ("ev-fund-query-detail", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:359-390", "按规则 id 查询 detail（rule_info_id=id）"),
    ("ev-fund-provider-query", "code_path", "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyRuleProviderImpl.java:89-130", "资金方规则查询：按资方标识+产品+ACTIVE 查询规则并组装分层明细"),
    # dormant schema evidence
    ("ev-party-cfg-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/FundingPartyRuleCfgDO.java", "funding_party_rule_cfg 休眠表声明"),
    ("ev-party-detail-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/FundingPartyRuleDetailDO.java", "funding_party_rule_detail 休眠表声明"),
    ("ev-party-front-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/FundingPartyRuleFrontDO.java", "funding_party_rule_front 休眠表声明"),
    ("ev-org-manage-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/OrgManageDO.java", "org_manage 休眠表声明"),
    ("ev-tenant-ext-field-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProductExtFieldDO.java", "tenant_product_ext_field 休眠表声明"),
    ("ev-tenant-ext-field-form-schema", "database_schema", "pplatform-apaas/pplatform-apaas-service-api/src/main/java/com/lls/lowcode/pplatform/pplatform/apaas/service/api/model/TenantProductExtFieldFormDO.java", "tenant_product_ext_field_form 休眠表声明"),
]
for eid, kind, loc, claim in ev_defs:
    evidence.append(ev(eid, kind, loc, claim))

# dictionaries
CUST_BUILD_STATUS_DICT = {
    "INIT": "初始化", "TO_BE_BUILD": "未建档", "BUILDING": "建档中",
    "BUILD_SUCCESS": "认证成功", "BUILD_FAIL": "认证失败", "BUILD_BACK": "退回",
    "BUILD_ACTIVATE": "待激活", "CUST_CONFIRM_AWAIT": "待客户认证",
    "CUST_AUDIT_AWAIT": "待审核", "CUST_BUILDING": "审核中",
    "CUST_BUILD_SUCCESS": "审核通过", "CUST_BUILD_FAIL": "审核拒绝",
    "CUST_CHANGE": "变更", "AWAIT_CUST_CONFIRM": "待客户确认",
}
CUST_STATUS_DICT = {"ADD": "新增", "EFFECT": "生效", "FAILURE": "失效", "WRITEOFF": "注销", "FREEZE": "冻结", "CHANGE": "变更"}
CHECK_STATUS_DICT = {
    "CUST_CHECK_INIT": "待审核", "CUST_CHECK_CHECKING": "审核中",
    "CUST_CHECK_PASS": "审核通过", "CUST_CHECK_REJECT": "审核不通过",
    "CUST_CHECK_BACKTOCUSTOM": "待客户确认", "CUST_BACK": "退回",
}
USER_TYPE_DICT = {"admin": "管理员", "operator": "经办人", "guest": "游客"}
COMPANY_TYPE_DICT = {
    "CORE": "核心企业", "SUPPLIER": "供应商", "FINANCE": "金融机构",
    "PLATFORM_OPERATOR_COMPANY": "平台运营方", "DEALER": "经销商", "PROJECT_COMPANY": "项目公司",
}
CUST_SOURCE_DICT = {"PLATFORM_PUSH": "运营中台推送", "MIGRATORY": "存量迁移企业", "PPLATFORM": "产融自建企业"}
PROJECT_STATUS_DICT = {"0": "待生效", "1": "已生效", "2": "已失效"}
WF_STATUS_DICT = {"PENDING": "待发起", "RUNNING": "审批中", "FINISHED": "审批通过", "TERMINATED": "审批拒绝"}
NODE_STATUS_DICT = {"PENDING": "待审批", "APPROVING": "审批中", "APPROVED": "已通过", "REJECTED": "已拒绝"}
FLOW_CODE_DICT = {"NO_ONLINE": "无需上线审批", "STANDARD": "标准项目流程", "REGULAR": "常规项目流程"}
PROJECT_TYPE_DICT = {"STANDARD": "标准项目", "REGULAR": "常规项目"}
NODE_CODE_DICT = {
    "PROJECT_CONFIG": "方案配置", "PROJECT_MANAGER": "方案经理", "LEGAL_PROCESS": "法务经办",
    "LEGAL_REVIEW": "法务复核", "BUSINESS_MANAGER": "业务经理审批", "OPERATION": "运营审批",
    "OTHER": "其他", "SUPPLEMENT_AGREEMENT": "补充协议",
}
OPERATE_TYPE_DICT = {"pass": "同意", "reject": "驳回", "back": "退回", "delegate": "转审"}
RULE_STATUS_DICT = {"PENDING": "待生效", "ACTIVE": "生效中", "INACTIVE": "已失效"}
RULE_LAYER_DICT = {"UNDERLYING": "底层规则", "FINANCING": "融资规则", "OTHER": "其他规则"}
YES_NO_DICT = {"Y": "是", "N": "否"}

def fld(field_id, name, dtype, desc, dictionary=None, refs=None):
    d = {"field_id": field_id, "name": name, "data_type": dtype, "description": desc}
    if dictionary:
        d["dictionary"] = dictionary
    if refs:
        d["evidence_refs"] = refs
    return d

def dset(dataset_id, name, desc, fields, database="lowcode_pplatform", inactive=False, refs=None):
    d = {
        "dataset_id": dataset_id,
        "name": name,
        "description": desc,
        "database": database,
        "inactive": inactive,
        "fields": fields,
    }
    if refs:
        d["evidence_refs"] = refs
    return d

# ---------------------------------------------------------------------------
# Unit 1: enterprise-onboarding
# ---------------------------------------------------------------------------
company_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-company-schema"]),
    fld("code", "code", "varchar", "编码", refs=["ev-company-schema"]),
    fld("certification_no", "certification_no", "varchar", "统一信用代码", refs=["ev-company-schema"]),
    fld("db_tenant_code", "db_tenant_code", "varchar", "数据租户标识", refs=["ev-company-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-company-schema"]),
    fld("check_status", "check_status", "varchar", "审核状态", dictionary=CHECK_STATUS_DICT, refs=["ev-company-schema", "ev-check-status-dict"]),
    fld("build_status", "cust_build_status", "varchar", "认证状态", dictionary=CUST_BUILD_STATUS_DICT, refs=["ev-company-schema", "ev-cust-build-status-dict"]),
    fld("cust_status", "cust_status", "varchar", "客户状态", dictionary=CUST_STATUS_DICT, refs=["ev-company-schema", "ev-cust-status-dict"]),
    fld("company_type", "cust_company_type", "varchar", "企业角色", dictionary=COMPANY_TYPE_DICT, refs=["ev-company-schema", "ev-company-type-dict"]),
    fld("cust_source", "cust_source", "varchar", "建档数据来源", dictionary=CUST_SOURCE_DICT, refs=["ev-company-schema", "ev-cust-source-dict"]),
]
person_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-person-schema"]),
    fld("name", "name", "varchar", "姓名", refs=["ev-person-schema"]),
    fld("ref_cust_company_info", "ref_cust_company_info", "varchar", "关联企业", refs=["ev-person-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-person-schema"]),
    fld("user_type", "user_type", "varchar", "联系人类型", dictionary=USER_TYPE_DICT, refs=["ev-person-schema", "ev-user-type-dict"]),
    fld("platform_user_id", "platform_user_id", "bigint", "运营系统用户id", refs=["ev-person-schema"]),
]
build_record_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-build-record-schema"]),
    fld("cust_id", "cust_id", "bigint", "企业ID", refs=["ev-build-record-schema"]),
    fld("person_id", "person_id", "bigint", "联系人ID", refs=["ev-build-record-schema"]),
    fld("channel", "channel", "varchar", "渠道", refs=["ev-build-record-schema"]),
    fld("return_data", "return_data", "varchar", "返回data", refs=["ev-build-record-schema"]),
    fld("db_tenant_code", "db_tenant_code", "varchar", "数据租户标识", refs=["ev-build-record-schema"]),
]
cust_project_rel_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-cust-project-rel-schema"]),
    fld("project_id", "project_id", "varchar", "项目id", refs=["ev-cust-project-rel-schema"]),
    fld("product_id", "product_id", "varchar", "产品", refs=["ev-cust-project-rel-schema"]),
    fld("company_type", "company_type", "varchar", "客户角色(只取一个)", dictionary=COMPANY_TYPE_DICT, refs=["ev-cust-project-rel-schema", "ev-company-type-dict"]),
    fld("status", "status", "varchar", "关联状态", refs=["ev-cust-project-rel-schema"]),
    fld("show_flag", "show_flag", "varchar", "展示标记", refs=["ev-cust-project-rel-schema"]),
    fld("ref_cust_project_rel_cust_company_info", "ref_cust_project_rel_cust_company_info", "varchar", "客户和项目关系", refs=["ev-cust-project-rel-schema"]),
    fld("db_tenant_code", "db_tenant_code", "varchar", "数据租户标识", refs=["ev-cust-project-rel-schema"]),
]
tenant_project_min_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-tenant-project-schema"]),
    fld("name", "name", "varchar", "名称", refs=["ev-tenant-project-schema"]),
    fld("platform_product_code", "platform_product_code", "varchar", "平台产品编码", refs=["ev-tenant-project-schema"]),
    fld("product_id", "product_id", "bigint", "产品编码", refs=["ev-tenant-project-schema"]),
]
platform_product_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-platform-product-schema"]),
    fld("product_code", "product_code", "varchar", "产品编码", refs=["ev-platform-product-schema"]),
    fld("name", "name", "varchar", "名称", refs=["ev-platform-product-schema"]),
]
tenant_setting_fields = [
    fld("db_tenant_code", "db_tenant_code", "varchar", "数据租户标识", refs=["ev-tenant-setting-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-tenant-setting-schema"]),
    fld("default_project_id", "default_project_id", "bigint", "默认项目", refs=["ev-tenant-setting-schema"]),
    fld("band_name", "band_name", "varchar", "贴牌平台名称", refs=["ev-tenant-setting-schema"]),
    fld("cust_service_number", "cust_service_number", "varchar", "客服电话", refs=["ev-tenant-setting-schema"]),
]

onboarding_datasets = [
    dset("company", "cust_company_info", "企业主数据/过程记录，一行一家企业", company_fields, refs=["ev-company-schema"]),
    dset("person", "cust_person_info", "企业联系人/用户信息", person_fields, refs=["ev-person-schema"]),
    dset("build_record", "cust_build_record", "建档推送运营中台记录", build_record_fields, refs=["ev-build-record-schema"]),
    dset("cust_project_rel", "cust_project_rel", "客户-项目关系", cust_project_rel_fields, refs=["ev-cust-project-rel-schema"]),
    dset("tenant_project", "tenant_project", "租户项目配置", tenant_project_min_fields, refs=["ev-tenant-project-schema"]),
    dset("platform_product", "platform_product", "平台产品", platform_product_fields, refs=["ev-platform-product-schema"]),
    dset("tenant_setting", "tenant_setting_config", "租户设置", tenant_setting_fields, refs=["ev-tenant-setting-schema"]),
]

onboarding_concepts = [
    {
        "concept_id": "build-success",
        "name": "建档成功",
        "aliases": ["认证成功", "有效已建档企业"],
        "definition": "主数据建档状态为 BUILD_SUCCESS 且企业生效（cust_status=EFFECT）。",
        "dictionary": {"BUILD_SUCCESS": "认证成功", "EFFECT": "生效"},
        "field_targets": [
            {"dataset": "company", "field": "build_status"},
            {"dataset": "company", "field": "cust_status"},
        ],
        "evidence_refs": ["ev-cust-build-status-dict", "ev-cust-status-dict"],
    },
    {
        "concept_id": "audit-passed",
        "name": "审核通过",
        "aliases": ["建档审核通过"],
        "definition": "建档审核流终态为 CUST_BUILD_SUCCESS（审核通过）。",
        "dictionary": {"CUST_BUILD_SUCCESS": "审核通过"},
        "field_targets": [{"dataset": "company", "field": "build_status"}],
        "evidence_refs": ["ev-cust-build-status-dict"],
    },
    {
        "concept_id": "await-cust-confirm",
        "name": "待客户确认",
        "aliases": ["待客户认证"],
        "definition": "建档状态为 CUST_CONFIRM_AWAIT，等待客户确认/补充资料。",
        "dictionary": {"CUST_CONFIRM_AWAIT": "待客户认证"},
        "field_targets": [{"dataset": "company", "field": "build_status"}],
        "evidence_refs": ["ev-cust-build-status-dict"],
    },
    {
        "concept_id": "effective-company",
        "name": "有效企业",
        "aliases": ["企业"],
        "definition": "企业主数据表 cust_company_info 的实体概念，以主键 id 锚定。",
        "field_targets": [{"dataset": "company", "field": "id"}],
        "evidence_refs": ["ev-company-schema"],
    },
    {
        "concept_id": "contact-person",
        "name": "企业联系人",
        "aliases": ["联系人"],
        "definition": "企业联系人表 cust_person_info 的实体概念，以主键 id 锚定。",
        "field_targets": [{"dataset": "person", "field": "id"}],
        "evidence_refs": ["ev-person-schema"],
    },
]

onboarding_processes = [
    {
        "stage_id": "onboarding-submit",
        "name": "自主注册建档提交",
        "description": "OperCustFacade.regSelfOld 事务链路：锁+在途校验 → 组装企业/用户数据 → 读项目配置 → 推送运营中台 → 写回状态并保存建档记录。",
        "trigger": "管理端/运营端调用 OperCustFacade.regSelfOld(companyId, personId)",
        "enter_conditions": ["companyId 对应企业存在", "check_status 为空或 CUST_CHECK_REJECT"],
        "exit_conditions": ["check_status=CUST_CHECK_INIT", "cust_build_record 已保存"],
        "next_stages": ["onboarding-audit"],
        "data_effects": [
            {"operation": "read", "dataset": "company", "fields": ["id", "code", "certification_no", "db_tenant_code", "enable", "check_status", "build_status", "company_type", "cust_source"], "condition": "id = companyId", "description": "两次读取企业主数据（锁前 + 锁后二次校验）", "evidence_refs": ["ev-onboarding-regself", "ev-onboarding-get-company"]},
            {"operation": "read", "dataset": "person", "fields": ["id", "name", "ref_cust_company_info", "enable", "user_type"], "condition": "id = personId AND ref_cust_company_info = company.code AND enable='Y'", "description": "按企业编码 + 联系人 id 读取联系人", "evidence_refs": ["ev-onboarding-get-person"]},
            {"operation": "read", "dataset": "cust_project_rel", "fields": ["id", "project_id", "ref_cust_project_rel_cust_company_info"], "condition": "ref_cust_project_rel_cust_company_info = company.code", "description": "判断企业是否已有项目关联", "evidence_refs": ["ev-onboarding-set-project"]},
            {"operation": "read", "dataset": "tenant_setting", "fields": ["db_tenant_code", "enable", "default_project_id", "band_name", "cust_service_number"], "condition": "db_tenant_code = company.db_tenant_code AND enable='Y'", "description": "读租户设置取默认项目/贴牌/客服信息", "evidence_refs": ["ev-onboarding-set-project"]},
            {"operation": "read", "dataset": "tenant_project", "fields": ["id", "name", "platform_product_code", "product_id"], "condition": "id = tenant_setting.default_project_id", "description": "读默认项目；已有项目关联时按 rel.project_id 读项目", "evidence_refs": ["ev-onboarding-set-project"]},
            {"operation": "read", "dataset": "platform_product", "fields": ["id", "product_code", "name"], "condition": "product_code = tenant_project.platform_product_code", "description": "按项目平台产品编码读产品名称", "evidence_refs": ["ev-onboarding-set-project"]},
            {"operation": "update", "dataset": "person", "fields": ["user_type"], "condition": "id = personId AND user_type != 'admin'", "description": "将联系人提升为管理员", "evidence_refs": ["ev-onboarding-regself"]},
            {"operation": "insert", "dataset": "cust_project_rel", "fields": ["project_id", "product_id", "company_type", "status", "show_flag", "ref_cust_project_rel_cust_company_info", "db_tenant_code"], "condition": "无项目码且存在默认项目时自动绑定", "description": "保存客户-项目关系；项目 id 以字符串写入（long_to_string CAST）", "evidence_refs": ["ev-onboarding-save-project-rel"]},
            {"operation": "update", "dataset": "company", "fields": ["check_status"], "condition": "id = companyId", "description": "推送成功后 check_status 置为 CUST_CHECK_INIT", "evidence_refs": ["ev-onboarding-regself", "ev-onboarding-update-company"]},
            {"operation": "update", "dataset": "person", "fields": ["platform_user_id"], "condition": "id = personId", "description": "回写运营系统用户 id", "evidence_refs": ["ev-onboarding-update-user"]},
            {"operation": "insert", "dataset": "build_record", "fields": ["cust_id", "person_id", "channel", "return_data", "db_tenant_code"], "condition": "建档推送完成后", "description": "保存建档记录（cust_id/person_id 来自方法形参传播）", "evidence_refs": ["ev-onboarding-build-record"]},
        ],
        "evidence_refs": ["ev-onboarding-regself"],
    },
    {
        "stage_id": "onboarding-audit",
        "name": "建档审核流转",
        "description": "运营中台审核回写：check_status 在 CUST_CHECK_INIT/CHECKING/PASS/REJECT 间流转，认证流与审核流分别落在 cust_build_status。",
        "trigger": "运营中台审核回调/审核结果同步",
        "enter_conditions": ["check_status=CUST_CHECK_INIT"],
        "exit_conditions": ["check_status=CUST_CHECK_PASS 或 CUST_CHECK_REJECT"],
        "next_stages": [],
        "data_effects": [
            {"operation": "read", "dataset": "company", "fields": ["id", "check_status", "build_status"], "condition": "id = companyId", "description": "读当前企业审核/认证状态", "evidence_refs": ["ev-onboarding-regself"]},
            {"operation": "update", "dataset": "company", "fields": ["check_status", "build_status"], "condition": "按审核结果写入", "description": "CUST_CHECK_INIT→CUST_CHECK_CHECKING→CUST_CHECK_PASS/REJECT；认证流 INIT/BUILDING/BUILD_SUCCESS/BUILD_FAIL 由推送结果更新", "evidence_refs": ["ev-onboarding-regself", "ev-check-status-dict", "ev-cust-build-status-dict"]},
        ],
        "evidence_refs": ["ev-onboarding-regself"],
    },
]

onboarding_relationships = [
    {
        "relationship_id": "rel-person-company-code",
        "left": {"dataset": "person", "field": "ref_cust_company_info"},
        "right": {"dataset": "company", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "联系人通过企业编码关联企业主数据",
        "status": "proposed",
        "evidence_refs": ["ev-onboarding-get-person"],
    },
    {
        "relationship_id": "rel-project-rel-company-code",
        "left": {"dataset": "cust_project_rel", "field": "ref_cust_project_rel_cust_company_info"},
        "right": {"dataset": "company", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "客户-项目关系通过企业编码关联企业",
        "status": "proposed",
        "evidence_refs": ["ev-onboarding-set-project", "ev-onboarding-save-project-rel"],
    },
    {
        "relationship_id": "rel-project-rel-project",
        "left": {"dataset": "cust_project_rel", "field": "project_id"},
        "right": {"dataset": "tenant_project", "field": "id"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "客户项目关系关联租户项目；project_id 为 varchar，tenant_project.id 为 bigint，需 CAST(long_to_string)",
        "status": "proposed",
        "evidence_refs": ["ev-onboarding-save-project-rel"],
    },
    {
        "relationship_id": "rel-tenant-project-platform-product",
        "left": {"dataset": "tenant_project", "field": "platform_product_code"},
        "right": {"dataset": "platform_product", "field": "product_code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "租户项目通过平台产品编码关联平台产品",
        "status": "proposed",
        "evidence_refs": ["ev-onboarding-set-project"],
    },
    {
        "relationship_id": "rel-build-record-company",
        "left": {"dataset": "build_record", "field": "cust_id"},
        "right": {"dataset": "company", "field": "id"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "建档记录归属企业",
        "status": "proposed",
        "evidence_refs": ["ev-onboarding-build-record"],
    },
    {
        "relationship_id": "rel-build-record-person",
        "left": {"dataset": "build_record", "field": "person_id"},
        "right": {"dataset": "person", "field": "id"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "建档记录归属联系人",
        "status": "proposed",
        "evidence_refs": ["ev-onboarding-build-record"],
    },
]

onboarding_calibers = [
    {
        "caliber_id": "cal-onboarding-inflight",
        "label": "在途建档",
        "description": "存在审核状态且审核状态非 CUST_CHECK_REJECT 的企业，视为在途建档，不允许重复发起。",
        "contract_fragment": {"predicate": "check_status IS NOT NULL AND check_status != 'CUST_CHECK_REJECT'", "scope": "全局定义，OperCustFacade.regSelfOld 锁后二次校验使用"},
        "field_targets": [{"dataset": "company", "field": "check_status"}],
        "evidence_refs": ["ev-onboarding-regself"],
    },
    {
        "caliber_id": "cal-build-success-company",
        "label": "认证成功企业",
        "description": "认证流成功且企业主数据生效：cust_build_status=BUILD_SUCCESS AND cust_status=EFFECT。",
        "contract_fragment": {"predicate": "cust_build_status = 'BUILD_SUCCESS' AND cust_status = 'EFFECT'", "scope": "全局定义"},
        "field_targets": [{"dataset": "company", "field": "build_status"}, {"dataset": "company", "field": "cust_status"}],
        "evidence_refs": ["ev-cust-build-status-dict", "ev-cust-status-dict"],
    },
    {
        "caliber_id": "cal-audit-passed-company",
        "label": "审核通过企业",
        "description": "建档审核流终态为审核通过：cust_build_status=CUST_BUILD_SUCCESS。",
        "contract_fragment": {"predicate": "cust_build_status = 'CUST_BUILD_SUCCESS'", "scope": "全局定义"},
        "field_targets": [{"dataset": "company", "field": "build_status"}],
        "evidence_refs": ["ev-cust-build-status-dict"],
    },
]

onboarding_metrics = [
    {
        "metric_id": "metric-build-company-count",
        "name": "建档企业数",
        "description": "按企业主数据计数；可按 caliber 拆分口径（创建/提交认证/审核通过/认证成功）。",
        "aggregation": "COUNT",
        "field": {"dataset": "company", "field": "id"},
        "grain": [{"dataset": "company", "field": "id"}],
        "filters": [],
        "evidence_refs": ["ev-onboarding-regself"],
    },
    {
        "metric_id": "metric-build-record-count",
        "name": "建档记录数",
        "description": "建档推送运营中台记录数。",
        "aggregation": "COUNT",
        "field": {"dataset": "build_record", "field": "id"},
        "grain": [{"dataset": "build_record", "field": "id"}],
        "filters": [],
        "evidence_refs": ["ev-onboarding-build-record"],
    },
    {
        "metric_id": "metric-project-rel-company-count",
        "name": "项目关联企业数",
        "description": "客户-项目关系记录数，按项目/企业维度去重需按 grain 澄清。",
        "aggregation": "COUNT",
        "field": {"dataset": "cust_project_rel", "field": "id"},
        "grain": [{"dataset": "cust_project_rel", "field": "id"}],
        "filters": [],
        "evidence_refs": ["ev-onboarding-save-project-rel"],
    },
]

onboarding_rules = [
    {
        "rule_id": "rule-onboarding-lock-inflight",
        "label": "自主注册建档在途锁与二次校验",
        "content": "按 certification_no 获取分布式锁，锁后二次读取企业并校验 check_status 非空且非 CUST_CHECK_REJECT 时拒绝重复发起。",
        "applicability": "OperCustFacade.regSelfOld 自主注册建档入口",
        "query_impact": "查询在途建档时必须同时看 check_status 非空与非 REJECT 两个条件；仅看 cust_build_status 会漏掉审核中数据。",
        "field_targets": [{"dataset": "company", "field": "check_status"}, {"dataset": "company", "field": "certification_no"}],
        "evidence_refs": ["ev-onboarding-regself"],
    },
    {
        "rule_id": "rule-onboarding-push-rollback",
        "label": "建档推送失败回滚 INIT",
        "content": "推送运营中台异常时，将 cust_build_status 回滚为 INIT。",
        "applicability": "OperCustFacade.regSelfOld 异常处理分支",
        "query_impact": "统计在途/成功建档时需排除 INIT 状态，且要理解失败会回滚到 INIT。",
        "field_targets": [{"dataset": "company", "field": "build_status"}],
        "evidence_refs": ["ev-onboarding-regself"],
    },
    {
        "rule_id": "rule-onboarding-default-project-bind",
        "label": "无项目码自动绑定租户默认项目",
        "content": "企业无客户-项目关系且为自助建档时，按 db_tenant_code 读取租户默认项目并自动创建 cust_project_rel。",
        "applicability": "OperCustFacade.setCustProjectInfo 分支",
        "query_impact": "查询企业项目归属时，没有显式项目码的企业可能落在租户默认项目上。",
        "field_targets": [{"dataset": "cust_project_rel", "field": "project_id"}, {"dataset": "tenant_setting", "field": "default_project_id"}],
        "evidence_refs": ["ev-onboarding-set-project"],
    },
    {
        "rule_id": "rule-onboarding-supplier-acflow-status",
        "label": "供应商+ACFLOW/ORDER 产品项目关联置 1",
        "content": "当企业角色为 SUPPLIER 且默认项目平台产品为 ACFLOW 或 ORDER 时，cust_project_rel.status 置为 '1'，否则 '0'。",
        "applicability": "OperCustFacade.saveCustProjectRelDO",
        "query_impact": "按项目关联状态筛选时，status=1 代表供应商在讯易链/订单融资产品下的关联，0 代表其他。",
        "field_targets": [{"dataset": "cust_project_rel", "field": "status"}, {"dataset": "cust_project_rel", "field": "company_type"}],
        "evidence_refs": ["ev-onboarding-save-project-rel"],
    },
]

onboarding_patterns = [
    {
        "pattern_id": "pat-onboarding-company-by-id",
        "question": "按企业ID查企业信息",
        "query": "SELECT id, code, name, cust_build_status, cust_status, check_status FROM cust_company_info WHERE id = :companyId",
        "intended_specification": {"entity": "company", "query_type": "detail_by_id"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-onboarding-get-company"],
    },
    {
        "pattern_id": "pat-onboarding-persons-by-company-code",
        "question": "按企业编码查联系人列表",
        "query": "SELECT id, name, user_type, platform_user_id FROM cust_person_info WHERE ref_cust_company_info = :companyCode AND enable = 'Y'",
        "intended_specification": {"entity": "person", "query_type": "list_by_company_code"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-onboarding-get-person"],
    },
    {
        "pattern_id": "pat-onboarding-success-company-count",
        "question": "建档成功企业有多少",
        "query": "SELECT COUNT(*) FROM cust_company_info WHERE cust_build_status = 'BUILD_SUCCESS' AND cust_status = 'EFFECT'",
        "intended_specification": {"caliber_id": "cal-build-success-company", "metric_id": "metric-build-company-count"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-cust-build-status-dict", "ev-cust-status-dict"],
    },
    {
        "pattern_id": "pat-onboarding-project-rel-count",
        "question": "项目关联企业有多少",
        "query": "SELECT COUNT(*) FROM cust_project_rel WHERE status = '1'",
        "intended_specification": {"metric_id": "metric-project-rel-company-count"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-onboarding-save-project-rel"],
    },
]

onboarding_unit = {
    "unit_id": "enterprise-onboarding",
    "revision": 1,
    "title": "企业建档与客户项目关联",
    "aliases": ["建档", "自主注册建档", "客户项目关联"],
    "domain": "customer",
    "applicability": "企业主数据/联系人/建档记录/客户项目关系的自助建档与审核场景",
    "description": "穿透 OperCustFacade.regSelfOld 入口：读取企业/联系人/租户项目配置，推送运营中台后写回审核状态、联系人平台用户ID与建档记录；覆盖在途锁、默认项目绑定、供应商项目关联状态规则。",
    "content": {
        "concepts": onboarding_concepts,
        "processes": onboarding_processes,
        "datasets": onboarding_datasets,
        "relationships": onboarding_relationships,
        "metrics": onboarding_metrics,
        "calibers": onboarding_calibers,
        "domain_rules": onboarding_rules,
        "verified_query_patterns": onboarding_patterns,
    },
    "evidence_refs": ["ev-onboarding-regself"],
    "unit_links": [],
    "assumptions": [],
    "conflicts": [],
    "confidence": 0.75,
}

# ---------------------------------------------------------------------------
# Unit 2: project-approval
# ---------------------------------------------------------------------------
project_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-tenant-project-schema"]),
    fld("code", "code", "varchar", "编码", refs=["ev-tenant-project-schema"]),
    fld("name", "name", "varchar", "名称", refs=["ev-tenant-project-schema"]),
    fld("project_status", "project_status", "varchar", "项目状态", dictionary=PROJECT_STATUS_DICT, refs=["ev-tenant-project-schema", "ev-proj-project-status-dict"]),
    fld("project_approval_id", "project_approval_id", "bigint", "项目上线审批ID", refs=["ev-tenant-project-schema"]),
    fld("wechat_audit_no", "wechat_audit_no", "varchar", "企微审批编号", refs=["ev-tenant-project-schema"]),
    fld("db_tenant_code", "db_tenant_code", "varchar", "数据租户标识", refs=["ev-tenant-project-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-tenant-project-schema"]),
]

approval_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-proj-schema"]),
    fld("code", "code", "varchar", "编码", refs=["ev-proj-schema"]),
    fld("name", "name", "varchar", "名称", refs=["ev-proj-schema"]),
    fld("approval_no", "approval_no", "varchar", "审批编号，格式：SX+yyyymmdd+xxx", refs=["ev-proj-schema"]),
    fld("sp_no", "sp_no", "varchar", "立项审批编号", refs=["ev-proj-schema"]),
    fld("wf_status", "wf_status", "varchar", "工作流状态", dictionary=WF_STATUS_DICT, refs=["ev-proj-schema", "ev-proj-wf-status-dict"]),
    fld("flow_code", "flow_code", "varchar", "流程配置编码", dictionary=FLOW_CODE_DICT, refs=["ev-proj-schema", "ev-proj-flow-code-dict"]),
    fld("project_type", "project_type", "varchar", "项目类型", dictionary=PROJECT_TYPE_DICT, refs=["ev-proj-schema", "ev-proj-project-type-dict"]),
    fld("is_low_risk", "is_low_risk", "varchar", "是否低风险项目", dictionary=YES_NO_DICT, refs=["ev-proj-schema"]),
    fld("is_add", "is_add", "varchar", "是否新增项目", dictionary=YES_NO_DICT, refs=["ev-proj-schema"]),
    fld("ref_tenant_project_approval_tenant_project", "ref_tenant_project_approval_tenant_project", "varchar", "关联租户项目", refs=["ev-proj-schema"]),
    fld("initiate_time", "initiate_time", "datetime", "发起时间", refs=["ev-proj-schema"]),
    fld("complete_time", "complete_time", "datetime", "完成时间", refs=["ev-proj-schema"]),
    fld("db_tenant_code", "db_tenant_code", "varchar", "数据租户标识", refs=["ev-proj-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-proj-schema"]),
]

biz_info_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-proj-biz-schema"]),
    fld("ref_tenant_project_approval_business_info_project_approval", "ref_tenant_project_approval_business_info_project_approval", "varchar", "关联项目审批", refs=["ev-proj-biz-schema"]),
    fld("product_code", "product_code", "varchar", "产品编码code", refs=["ev-proj-biz-schema"]),
    fld("source_system", "source_system", "varchar", "来源系统", dictionary={"ACFLOW": "讯易链", "RVSFACTOR_PC": "线上保理", "ORDER": "订单融资"}, refs=["ev-proj-biz-schema"]),
    fld("asset_list_mode", "asset_list_mode", "varchar", "资产清单模式", dictionary={"STANDARD_LIST": "标准清单", "SIMPLE_LIST": "简易清单"}, refs=["ev-proj-biz-schema"]),
    fld("business_flow_mode", "business_flow_mode", "varchar", "业务流程模式", dictionary={"CONFIRM_RIGHT_FIRST": "先确权", "CONFIRM_RIGHT_AFTER": "后确权"}, refs=["ev-proj-biz-schema"]),
    fld("service_fee_collector_financing", "service_fee_collector_financing", "varchar", "服务费收取方", dictionary={"PLATFORM": "平台方", "OPERATOR": "运营方"}, refs=["ev-proj-biz-schema"]),
    fld("service_fee_quote_type_financing", "service_fee_quote_type_financing", "varchar", "服务费报价类型", dictionary={"PLATFORM_SERVICE_RATE": "平台服务费率", "TOTAL_RATE": "总费率", "FIXED": "固定年化利率", "PAY_PER_VIEW": "非年化利率"}, refs=["ev-proj-biz-schema"]),
    fld("service_fee_collect_method_financing", "service_fee_collect_method_financing", "varchar", "服务费收取方式", dictionary={"ONLINE": "线上收取", "OFFLINE": "线下收取", "BOCOM_PAY": "交e保", "FREE": "免费"}, refs=["ev-proj-biz-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-proj-biz-schema"]),
]

flow_config_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-proj-flow-config-schema"]),
    fld("flow_code", "flow_code", "varchar", "流程编码", dictionary=FLOW_CODE_DICT, refs=["ev-proj-flow-config-schema", "ev-proj-flow-code-dict"]),
    fld("node_code", "node_code", "varchar", "节点编码字典", dictionary=NODE_CODE_DICT, refs=["ev-proj-flow-config-schema", "ev-proj-node-code-dict"]),
    fld("node_name", "node_name", "varchar", "节点名称（中文）", refs=["ev-proj-flow-config-schema"]),
    fld("node_order", "node_order", "int", "节点顺序", refs=["ev-proj-flow-config-schema"]),
    fld("is_optional", "is_optional", "varchar", "是否可选节点", dictionary=YES_NO_DICT, refs=["ev-proj-flow-config-schema"]),
    fld("is_operate", "is_operate", "varchar", "是否可操作", dictionary=YES_NO_DICT, refs=["ev-proj-flow-config-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-proj-flow-config-schema"]),
]

flow_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-proj-flow-schema"]),
    fld("code", "code", "varchar", "编码", refs=["ev-proj-flow-schema"]),
    fld("ref_tenant_project_approval_flow_tenant_project_approval", "ref_tenant_project_approval_flow_tenant_project_approval", "varchar", "关联项目审批", refs=["ev-proj-flow-schema"]),
    fld("node_code", "node_code", "varchar", "节点编码", dictionary=NODE_CODE_DICT, refs=["ev-proj-flow-schema", "ev-proj-node-code-dict"]),
    fld("node_name", "node_name", "varchar", "节点名称（中文）", refs=["ev-proj-flow-schema"]),
    fld("node_order", "node_order", "int", "节点顺序，从 1 开始", refs=["ev-proj-flow-schema"]),
    fld("node_status", "node_status", "varchar", "节点状态", dictionary=NODE_STATUS_DICT, refs=["ev-proj-flow-schema", "ev-proj-node-status-dict"]),
    fld("approver_user_id", "approver_user_id", "varchar", "审批人 userId", refs=["ev-proj-flow-schema"]),
    fld("approver_user_name", "approver_user_name", "varchar", "审批人姓名", refs=["ev-proj-flow-schema"]),
    fld("is_optional", "is_optional", "varchar", "是否可选节点", dictionary=YES_NO_DICT, refs=["ev-proj-flow-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-proj-flow-schema"]),
]

flow_node_fields = [
    fld("code", "code", "varchar", "编码", refs=["ev-proj-node-schema"]),
    fld("ref_tenant_project_approval_flow_node_project_approval", "ref_tenant_project_approval_flow_node_project_approval", "varchar", "关联项目审批", refs=["ev-proj-node-schema"]),
    fld("ref_tenant_project_approval_flow_node_project_approval_flow", "ref_tenant_project_approval_flow_node_project_approval_flow", "varchar", "关联项目审批流程", refs=["ev-proj-node-schema"]),
    fld("node_code", "node_code", "varchar", "节点编码", dictionary=NODE_CODE_DICT, refs=["ev-proj-node-schema", "ev-proj-node-code-dict"]),
    fld("node_order", "node_order", "int", "审批顺序，从1开始", refs=["ev-proj-node-schema"]),
    fld("operate_type", "operate_type", "varchar", "操作类型", dictionary=OPERATE_TYPE_DICT, refs=["ev-proj-node-schema", "ev-proj-operate-type-dict"]),
    fld("operator_user_id", "operator_user_id", "varchar", "操作人 userId", refs=["ev-proj-node-schema"]),
    fld("operator_user_name", "operator_user_name", "varchar", "操作人姓名", refs=["ev-proj-node-schema"]),
    fld("approve_comment", "approve_comment", "varchar", "审批意见", refs=["ev-proj-node-schema"]),
    fld("is_low_risk", "is_low_risk", "varchar", "是否低风险项目", dictionary=YES_NO_DICT, refs=["ev-proj-node-schema"]),
    fld("is_back_agreement", "is_back_agreement", "varchar", "是否后补合作协议", dictionary=YES_NO_DICT, refs=["ev-proj-node-schema"]),
    fld("operate_time", "operate_time", "datetime", "操作时间", refs=["ev-proj-node-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-proj-node-schema"]),
]

flow_credit_fields = [
    fld("ref_tenant_project_approval_flow_credit_project_approval", "ref_tenant_project_approval_flow_credit_project_approval", "varchar", "关联项目审批", refs=["ev-proj-credit-schema"]),
    fld("ref_tenant_project_approval_flow_credit_project_approval_node", "ref_tenant_project_approval_flow_credit_project_approval_node", "varchar", "关联项目审批流程节点", refs=["ev-proj-credit-schema"]),
    fld("credit_limit", "credit_limit", "decimal", "授信额度", refs=["ev-proj-credit-schema"]),
    fld("credited_cust_id", "credited_cust_id", "varchar", "被授信方（核心企业）id", refs=["ev-proj-credit-schema"]),
    fld("credited_cust_name", "credited_cust_name", "varchar", "被授信方（核心企业）", refs=["ev-proj-credit-schema"]),
    fld("crediting_cust_id", "crediting_cust_id", "varchar", "授信方（资金方）id", refs=["ev-proj-credit-schema"]),
    fld("crediting_cust_name", "crediting_cust_name", "varchar", "授信方（资金方）", refs=["ev-proj-credit-schema"]),
    fld("is_group_limit", "is_group_limit", "varchar", "是否为集团额度", dictionary=YES_NO_DICT, refs=["ev-proj-credit-schema"]),
    fld("limit_begin_date", "limit_begin_date", "date", "额度有效期开始", refs=["ev-proj-credit-schema"]),
    fld("limit_end_date", "limit_end_date", "date", "额度有效期结束", refs=["ev-proj-credit-schema"]),
    fld("is_recyclable", "is_recyclable", "varchar", "额度是否可循环", dictionary=YES_NO_DICT, refs=["ev-proj-credit-schema"]),
    fld("finance_email", "finance_email", "varchar", "资金方邮箱（需格式校验）", refs=["ev-proj-credit-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-proj-credit-schema"]),
]

flow_file_fields = [
    fld("ref_tenant_project_approval_flow_file_project_approval", "ref_tenant_project_approval_flow_file_project_approval", "varchar", "关联项目审批", refs=["ev-proj-file-schema"]),
    fld("ref_tenant_project_approval_flow_file_project_approval_flow_node", "ref_tenant_project_approval_flow_file_project_approval_flow_node", "varchar", "关联项目流程节点", refs=["ev-proj-file-schema"]),
    fld("catg_id", "catg_id", "varchar", "影像分类编码", refs=["ev-proj-file-schema"]),
    fld("catg_name", "catg_name", "varchar", "影像分类名称", refs=["ev-proj-file-schema"]),
    fld("file_id", "file_id", "varchar", "文件id", refs=["ev-proj-file-schema"]),
    fld("file_name", "file_name", "varchar", "文件名称", refs=["ev-proj-file-schema"]),
    fld("file_url", "file_url", "varchar", "文件url", refs=["ev-proj-file-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-proj-file-schema"]),
]

proj_datasets = [
    dset("tenant_project", "tenant_project", "租户项目配置", project_fields, refs=["ev-tenant-project-schema"]),
    dset("project_approval", "tenant_project_approval", "项目上线审批主记录", approval_fields, refs=["ev-proj-schema"]),
    dset("approval_business_info", "tenant_project_approval_business_info", "项目审批业务信息", biz_info_fields, refs=["ev-proj-biz-schema"]),
    dset("approval_flow_config", "tenant_project_approval_flow_config", "审批流程配置", flow_config_fields, refs=["ev-proj-flow-config-schema"]),
    dset("approval_flow", "tenant_project_approval_flow", "审批流程节点实例", flow_fields, refs=["ev-proj-flow-schema"]),
    dset("approval_flow_node", "tenant_project_approval_flow_node", "审批流程节点操作记录", flow_node_fields, refs=["ev-proj-node-schema"]),
    dset("approval_flow_credit", "tenant_project_approval_flow_credit", "审批授信信息", flow_credit_fields, refs=["ev-proj-credit-schema"]),
    dset("approval_flow_file", "tenant_project_approval_flow_file", "审批流程文件", flow_file_fields, refs=["ev-proj-file-schema"]),
]

proj_concepts = [
    {
        "concept_id": "project-approval",
        "name": "项目上线审批",
        "aliases": ["上线审批", "项目审批"],
        "definition": "项目上线审批主记录 tenant_project_approval，以主键 id 锚定。",
        "field_targets": [{"dataset": "project_approval", "field": "id"}],
        "evidence_refs": ["ev-proj-schema"],
    },
    {
        "concept_id": "approval-running",
        "name": "审批中",
        "aliases": ["项目审批中"],
        "definition": "项目上线审批工作流状态为 RUNNING。",
        "dictionary": {"RUNNING": "审批中"},
        "field_targets": [{"dataset": "project_approval", "field": "wf_status"}],
        "evidence_refs": ["ev-proj-wf-status-dict"],
    },
    {
        "concept_id": "approval-passed",
        "name": "审批通过",
        "aliases": ["上线审批通过"],
        "definition": "项目上线审批工作流状态为 FINISHED。",
        "dictionary": {"FINISHED": "审批通过"},
        "field_targets": [{"dataset": "project_approval", "field": "wf_status"}],
        "evidence_refs": ["ev-proj-wf-status-dict"],
    },
    {
        "concept_id": "approval-legal-process",
        "name": "法务经办节点",
        "aliases": ["法务经办"],
        "definition": "审批流程中 node_code=LEGAL_PROCESS 的节点，同意时必须填写是否低风险。",
        "dictionary": {"LEGAL_PROCESS": "法务经办"},
        "field_targets": [{"dataset": "approval_flow", "field": "node_code"}],
        "evidence_refs": ["ev-proj-node-code-dict"],
    },
]

proj_processes = [
    {
        "stage_id": "approval-create",
        "name": "创建项目上线审批",
        "description": "项目创建/复制审批：写审批主记录并回写项目 project_approval_id；复制场景读取原审批并复制业务信息/流程节点。",
        "trigger": "ProjectApprovalApplication.createInitialApproval / doCreateApproval",
        "enter_conditions": ["项目存在且 project.code 非空"],
        "exit_conditions": ["approval.wf_status=PENDING", "project.project_approval_id 已回写"],
        "next_stages": ["approval-prepare"],
        "data_effects": [
            {"operation": "read", "dataset": "tenant_project", "fields": ["id", "code", "name", "db_tenant_code"], "condition": "id = projectId 或 code = projectCode", "description": "读项目生成审批基础信息", "evidence_refs": ["ev-proj-create-approval"]},
            {"operation": "read", "dataset": "project_approval", "fields": ["id", "code", "enable", "ref_tenant_project_approval_tenant_project"], "condition": "code = refTenantProjectApprovalTenantProjectApproval 且 enable='Y'", "description": "复制场景读原审批", "evidence_refs": ["ev-proj-copy-approval"]},
            {"operation": "read", "dataset": "approval_business_info", "fields": ["id", "ref_tenant_project_approval_business_info_project_approval", "product_code", "source_system", "asset_list_mode", "business_flow_mode", "service_fee_collector_financing", "service_fee_quote_type_financing", "service_fee_collect_method_financing", "enable"], "condition": "ref_tenant_project_approval_business_info_project_approval = 原审批.code", "description": "复制场景读原审批业务信息", "evidence_refs": ["ev-proj-copy-approval"]},
            {"operation": "read", "dataset": "approval_flow", "fields": ["id", "ref_tenant_project_approval_flow_tenant_project_approval", "node_code", "node_name", "node_order", "node_status", "approver_user_id", "approver_user_name", "is_optional", "enable"], "condition": "ref_tenant_project_approval_flow_tenant_project_approval = 原审批.code", "description": "复制场景读原审批流程节点", "evidence_refs": ["ev-proj-copy-approval"]},
            {"operation": "insert", "dataset": "project_approval", "fields": ["code", "name", "approval_no", "wf_status", "flow_code", "project_type", "is_add", "ref_tenant_project_approval_tenant_project", "db_tenant_code", "enable"], "condition": "新建/复制审批主记录", "description": "写入项目上线审批主记录，wf_status=PENDING", "evidence_refs": ["ev-proj-create-approval", "ev-proj-copy-approval"]},
            {"operation": "update", "dataset": "tenant_project", "fields": ["project_approval_id"], "condition": "id = projectId", "description": "回写项目当前审批 id", "evidence_refs": ["ev-proj-create-approval"]},
        ],
        "evidence_refs": ["ev-proj-create-approval"],
    },
    {
        "stage_id": "approval-prepare",
        "name": "查询审批流程配置",
        "description": "发起审批前按 is_online_approval + project_type 推断 flow_code 并查询预设流程节点。",
        "trigger": "ProjectApprovalApplication.listFlowConfig",
        "enter_conditions": ["isOnlineApproval 合法", "projectType 合法"],
        "exit_conditions": ["返回该 flow_code 下有序节点列表"],
        "next_stages": ["approval-submit"],
        "data_effects": [
            {"operation": "read", "dataset": "approval_flow_config", "fields": ["id", "flow_code", "node_code", "node_name", "node_order", "is_optional", "is_operate", "enable"], "condition": "flow_code = :flowCode AND enable='Y' ORDER BY node_order", "description": "按流程编码读预设审批节点", "evidence_refs": ["ev-proj-list-flow-config"]},
        ],
        "evidence_refs": ["ev-proj-list-flow-config"],
    },
    {
        "stage_id": "approval-submit",
        "name": "提交/暂存上线审批",
        "description": "提交审批：先删后增流程节点实例、写入审批业务字段、回写项目立项编号、生成工作流定义。",
        "trigger": "ProjectApprovalApplication.submit",
        "enter_conditions": ["审批存在且 wf_status=PENDING"],
        "exit_conditions": ["approval 已更新，flow 节点实例已保存，project.wechat_audit_no 已回写（首次正式提交）"],
        "next_stages": ["approval-start"],
        "data_effects": [
            {"operation": "read", "dataset": "project_approval", "fields": ["id", "code", "wf_status", "ref_tenant_project_approval_tenant_project", "is_add", "sp_no", "flow_code", "project_type", "enable"], "condition": "id = approvalId AND enable='Y'", "description": "读审批主记录并校验 PENDING", "evidence_refs": ["ev-proj-submit"]},
            {"operation": "read", "dataset": "tenant_project", "fields": ["id", "code", "project_status", "wechat_audit_no", "enable"], "condition": "code = approval.ref_tenant_project_approval_tenant_project", "description": "读关联项目", "evidence_refs": ["ev-proj-submit"]},
            {"operation": "delete", "dataset": "approval_flow", "fields": ["id", "ref_tenant_project_approval_flow_tenant_project_approval"], "condition": "ref_tenant_project_approval_flow_tenant_project_approval = approval.code AND enable='Y'", "description": "先删旧节点实例（先删后增）", "evidence_refs": ["ev-proj-submit"]},
            {"operation": "insert", "dataset": "approval_flow", "fields": ["ref_tenant_project_approval_flow_tenant_project_approval", "node_code", "node_name", "node_order", "node_status", "approver_user_id", "approver_user_name", "is_optional", "enable"], "condition": "flowList 非空且有效审批人节点", "description": "保存本次提交的审批流程节点实例", "evidence_refs": ["ev-proj-submit"]},
            {"operation": "update", "dataset": "project_approval", "fields": ["name", "sp_no", "wf_status", "flow_code", "project_type", "is_low_risk"], "condition": "id = approvalId", "description": "将请求业务字段写入审批 DO，暂存时返回", "evidence_refs": ["ev-proj-submit"]},
            {"operation": "update", "dataset": "tenant_project", "fields": ["wechat_audit_no"], "condition": "is_add=Y 且首次发起且 sp_no 非空", "description": "新增项目首次正式提交回写立项编号", "evidence_refs": ["ev-proj-submit"]},
        ],
        "evidence_refs": ["ev-proj-submit"],
    },
    {
        "stage_id": "approval-start",
        "name": "启动工作流",
        "description": "事务外启动项目上线审批工作流，成功后更新 wf_status=RUNNING。",
        "trigger": "ProjectApprovalApplication.startWorkflowAndUpdateStatus",
        "enter_conditions": ["submit 事务已提交"],
        "exit_conditions": ["wf_status=RUNNING 或保持 PENDING（失败降级）"],
        "next_stages": ["approval-node"],
        "data_effects": [
            {"operation": "read", "dataset": "project_approval", "fields": ["id", "code", "wf_status", "db_tenant_code"], "condition": "id = approvalId", "description": "读审批轻详情用于启动工作流", "evidence_refs": ["ev-proj-start-workflow"]},
            {"operation": "update", "dataset": "project_approval", "fields": ["initiate_time", "wf_status"], "condition": "id = approvalId AND 启动成功", "description": "wf_status 置 RUNNING，记录发起时间", "evidence_refs": ["ev-proj-start-workflow"]},
        ],
        "evidence_refs": ["ev-proj-start-workflow"],
    },
    {
        "stage_id": "approval-node",
        "name": "审批节点操作",
        "description": "法务经办/业务经理/通用节点同意、退回、驳回、转审：写 flow_node 操作记录，更新 flow.node_status，按节点写入授信或 is_low_risk。",
        "trigger": "ProjectApprovalDeskApplication.agree/back/reject/transfer",
        "enter_conditions": ["审批存在且 enable='Y'", "flow.node_code 匹配"],
        "exit_conditions": ["flow_node 已保存，flow.node_status 已更新"],
        "next_stages": ["approval-finish"],
        "data_effects": [
            {"operation": "read", "dataset": "project_approval", "fields": ["id", "code", "db_tenant_code", "is_low_risk"], "condition": "id = approvalId AND enable='Y'", "description": "读审批主记录", "evidence_refs": ["ev-proj-desk-agree"]},
            {"operation": "read", "dataset": "approval_flow", "fields": ["id", "code", "ref_tenant_project_approval_flow_tenant_project_approval", "node_code", "node_status"], "condition": "ref_tenant_project_approval_flow_tenant_project_approval = approval.code AND node_code = :nodeCode AND enable='Y'", "description": "按审批编码和节点编码读流程节点实例", "evidence_refs": ["ev-proj-desk-agree"]},
            {"operation": "insert", "dataset": "approval_flow_node", "fields": ["ref_tenant_project_approval_flow_node_project_approval", "ref_tenant_project_approval_flow_node_project_approval_flow", "node_code", "node_order", "operate_type", "operator_user_id", "operator_user_name", "approve_comment", "is_low_risk", "is_back_agreement", "operate_time", "enable"], "condition": "每个审批动作落一条节点操作记录", "description": "保存审批节点操作记录（同意/退回/驳回/转审）", "evidence_refs": ["ev-proj-desk-build-node"]},
            {"operation": "update", "dataset": "approval_flow", "fields": ["node_status"], "condition": "id = flow.id", "description": "更新流程节点状态为 APPROVING/APPROVED/REJECTED", "evidence_refs": ["ev-proj-desk-agree", "ev-proj-desk-back-reject"]},
            {"operation": "insert", "dataset": "approval_flow_credit", "fields": ["ref_tenant_project_approval_flow_credit_project_approval", "ref_tenant_project_approval_flow_credit_project_approval_node", "credit_limit", "credited_cust_id", "credited_cust_name", "crediting_cust_id", "crediting_cust_name", "is_group_limit", "limit_begin_date", "limit_end_date", "is_recyclable", "finance_email", "enable"], "condition": "业务经理节点同意时", "description": "保存授信信息", "evidence_refs": ["ev-proj-desk-save-credit"]},
            {"operation": "update", "dataset": "project_approval", "fields": ["is_low_risk"], "condition": "法务经办节点同意时", "description": "回写主表 is_low_risk 供 AMS 判定", "evidence_refs": ["ev-proj-desk-agree"]},
            {"operation": "insert", "dataset": "approval_flow_file", "fields": ["ref_tenant_project_approval_flow_file_project_approval", "ref_tenant_project_approval_flow_file_project_approval_flow_node", "catg_id", "catg_name", "file_id", "file_name", "file_url", "enable"], "condition": "节点操作附带附件时", "description": "审批文件落库并关联审批/流程节点", "evidence_refs": ["ev-proj-desk-media-file"]},
        ],
        "evidence_refs": ["ev-proj-desk-agree"],
    },
    {
        "stage_id": "approval-finish",
        "name": "审批终态与项目生效",
        "description": "工作流终态（FINISHED/TERMINATED）回写审批主记录；FINISHED 时触发项目置为已生效并推送业务系统/AMS。",
        "trigger": "ProjectOnlineProcessOperateListener 流程结束通知 -> handleFlowAndNodeStatus",
        "enter_conditions": ["wfStatus ∈ {FINISHED, TERMINATED}"],
        "exit_conditions": ["approval.wf_status 终态已写，FINISHED 时 tenant_project.project_status=1"],
        "next_stages": [],
        "data_effects": [
            {"operation": "update", "dataset": "project_approval", "fields": ["wf_status", "complete_time"], "condition": "id = approvalId", "description": "更新审批主记录为 FINISHED/TERMINATED，记录完成时间", "evidence_refs": ["ev-proj-handle-status"]},
            {"operation": "update", "dataset": "tenant_project", "fields": ["project_status"], "condition": "wfStatus=FINISHED 且 projectId 非空", "description": "审批通过后将项目置为已生效", "evidence_refs": ["ev-proj-effective"]},
        ],
        "evidence_refs": ["ev-proj-handle-status"],
    },
]

proj_relationships = [
    {
        "relationship_id": "rel-approval-project",
        "left": {"dataset": "project_approval", "field": "ref_tenant_project_approval_tenant_project"},
        "right": {"dataset": "tenant_project", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "审批记录通过项目编码关联租户项目",
        "status": "proposed",
        "evidence_refs": ["ev-proj-create-approval"],
    },
    {
        "relationship_id": "rel-approval-flow-config",
        "left": {"dataset": "project_approval", "field": "flow_code"},
        "right": {"dataset": "approval_flow_config", "field": "flow_code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "审批记录通过流程编码关联流程配置",
        "status": "proposed",
        "evidence_refs": ["ev-proj-list-flow-config"],
    },
    {
        "relationship_id": "rel-approval-flow-approval",
        "left": {"dataset": "approval_flow", "field": "ref_tenant_project_approval_flow_tenant_project_approval"},
        "right": {"dataset": "project_approval", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "审批流程节点实例关联审批主记录",
        "status": "proposed",
        "evidence_refs": ["ev-proj-submit"],
    },
    {
        "relationship_id": "rel-flow-node-approval",
        "left": {"dataset": "approval_flow_node", "field": "ref_tenant_project_approval_flow_node_project_approval"},
        "right": {"dataset": "project_approval", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "节点操作记录关联审批主记录",
        "status": "proposed",
        "evidence_refs": ["ev-proj-desk-build-node"],
    },
    {
        "relationship_id": "rel-flow-node-flow",
        "left": {"dataset": "approval_flow_node", "field": "ref_tenant_project_approval_flow_node_project_approval_flow"},
        "right": {"dataset": "approval_flow", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "节点操作记录关联流程节点实例",
        "status": "proposed",
        "evidence_refs": ["ev-proj-desk-build-node"],
    },
    {
        "relationship_id": "rel-biz-info-approval",
        "left": {"dataset": "approval_business_info", "field": "ref_tenant_project_approval_business_info_project_approval"},
        "right": {"dataset": "project_approval", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "审批业务信息关联审批主记录",
        "status": "proposed",
        "evidence_refs": ["ev-proj-copy-approval"],
    },
    {
        "relationship_id": "rel-credit-approval",
        "left": {"dataset": "approval_flow_credit", "field": "ref_tenant_project_approval_flow_credit_project_approval"},
        "right": {"dataset": "project_approval", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "授信信息关联审批主记录",
        "status": "proposed",
        "evidence_refs": ["ev-proj-desk-save-credit"],
    },
    {
        "relationship_id": "rel-credit-node",
        "left": {"dataset": "approval_flow_credit", "field": "ref_tenant_project_approval_flow_credit_project_approval_node"},
        "right": {"dataset": "approval_flow_node", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "授信信息关联审批节点操作记录",
        "status": "proposed",
        "evidence_refs": ["ev-proj-desk-save-credit"],
    },
    {
        "relationship_id": "rel-file-approval",
        "left": {"dataset": "approval_flow_file", "field": "ref_tenant_project_approval_flow_file_project_approval"},
        "right": {"dataset": "project_approval", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "审批文件关联审批主记录",
        "status": "proposed",
        "evidence_refs": ["ev-proj-desk-media-file"],
    },
    {
        "relationship_id": "rel-file-node",
        "left": {"dataset": "approval_flow_file", "field": "ref_tenant_project_approval_flow_file_project_approval_flow_node"},
        "right": {"dataset": "approval_flow_node", "field": "code"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "审批文件关联审批节点操作记录",
        "status": "proposed",
        "evidence_refs": ["ev-proj-desk-media-file"],
    },
]

proj_calibers = [
    {
        "caliber_id": "cal-approval-pending",
        "label": "待发起审批",
        "description": "审批工作流状态为 PENDING。",
        "contract_fragment": {"predicate": "wf_status = 'PENDING'", "scope": "tenant_project_approval 全局定义"},
        "field_targets": [{"dataset": "project_approval", "field": "wf_status"}],
        "evidence_refs": ["ev-proj-wf-status-dict"],
    },
    {
        "caliber_id": "cal-approval-running",
        "label": "审批中",
        "description": "审批工作流状态为 RUNNING。",
        "contract_fragment": {"predicate": "wf_status = 'RUNNING'", "scope": "tenant_project_approval 全局定义"},
        "field_targets": [{"dataset": "project_approval", "field": "wf_status"}],
        "evidence_refs": ["ev-proj-wf-status-dict"],
    },
    {
        "caliber_id": "cal-approval-passed",
        "label": "审批通过",
        "description": "审批工作流状态为 FINISHED。",
        "contract_fragment": {"predicate": "wf_status = 'FINISHED'", "scope": "tenant_project_approval 全局定义"},
        "field_targets": [{"dataset": "project_approval", "field": "wf_status"}],
        "evidence_refs": ["ev-proj-wf-status-dict"],
    },
    {
        "caliber_id": "cal-approval-rejected",
        "label": "审批拒绝",
        "description": "审批工作流状态为 TERMINATED。",
        "contract_fragment": {"predicate": "wf_status = 'TERMINATED'", "scope": "tenant_project_approval 全局定义"},
        "field_targets": [{"dataset": "project_approval", "field": "wf_status"}],
        "evidence_refs": ["ev-proj-wf-status-dict"],
    },
]

proj_metrics = [
    {
        "metric_id": "metric-approval-count",
        "name": "项目上线审批数",
        "description": "项目上线审批主记录数。",
        "aggregation": "COUNT",
        "field": {"dataset": "project_approval", "field": "id"},
        "grain": [{"dataset": "project_approval", "field": "id"}],
        "filters": [],
        "evidence_refs": ["ev-proj-create-approval"],
    },
    {
        "metric_id": "metric-approval-passed-count",
        "name": "审批通过项目数",
        "description": "工作流状态为 FINISHED 的项目上线审批数。",
        "aggregation": "COUNT",
        "field": {"dataset": "project_approval", "field": "id"},
        "grain": [{"dataset": "project_approval", "field": "id"}],
        "filters": [{"field": "wf_status", "op": "=", "value": "FINISHED"}],
        "evidence_refs": ["ev-proj-handle-status"],
    },
    {
        "metric_id": "metric-approval-running-count",
        "name": "在途审批数",
        "description": "工作流状态为 RUNNING 的审批数。",
        "aggregation": "COUNT",
        "field": {"dataset": "project_approval", "field": "id"},
        "grain": [{"dataset": "project_approval", "field": "id"}],
        "filters": [{"field": "wf_status", "op": "=", "value": "RUNNING"}],
        "evidence_refs": ["ev-proj-start-workflow"],
    },
]

proj_rules = [
    {
        "rule_id": "rule-approval-historical-project-invalid",
        "label": "非新增项目发起审批时历史项目置失效",
        "content": "非新增项目（is_add != Y）正式发起上线审批，若项目 project_status 为已生效/已失效，先将项目置为已失效并同步业务系统。",
        "applicability": "ProjectApprovalApplication.submit -> invalidateHistoricalProjectOnSubmit",
        "query_impact": "查当前生效项目时需理解历史项目在重新发起审批时会被置为已失效，最新生效状态以最新审批为准。",
        "field_targets": [{"dataset": "tenant_project", "field": "project_status"}],
        "evidence_refs": ["ev-proj-submit"],
    },
    {
        "rule_id": "rule-approval-legal-low-risk-required",
        "label": "法务经办节点必须填写是否低风险",
        "content": "法务经办节点同意时 is_low_risk 必填且仅允许 Y/N，并同步更新审批主表 is_low_risk 供 AMS 判定。",
        "applicability": "ProjectApprovalDeskApplication.doAgreeLegalProcess",
        "query_impact": "标准项目/常规低风险项目的 AMS 推送判定依赖主表 is_low_risk；查询推送范围时需关联该字段。",
        "field_targets": [{"dataset": "project_approval", "field": "is_low_risk"}, {"dataset": "approval_flow_node", "field": "is_low_risk"}],
        "evidence_refs": ["ev-proj-desk-agree"],
    },
    {
        "rule_id": "rule-approval-biz-manager-credit",
        "label": "业务经理审批通过时写入授信信息",
        "content": "业务经理节点同意时校验并保存授信信息（授信额度、授信双方、有效期、是否循环等）到 approval_flow_credit。",
        "applicability": "ProjectApprovalDeskApplication.doAgreeBusinessManager",
        "query_impact": "查询项目授信额度时需关联 approval_flow_credit 并以最新审批节点记录为准。",
        "field_targets": [{"dataset": "approval_flow_credit", "field": "credit_limit"}],
        "evidence_refs": ["ev-proj-desk-save-credit"],
    },
    {
        "rule_id": "rule-approval-flow-valid",
        "label": "提交审批须有有效审批节点与 OA 文件",
        "content": "提交审批时至少一个有效审批节点；项目上线审批文件目录和 OA 商务报价目录下必须有上传文件，否则拒绝提交。",
        "applicability": "ProjectApprovalApplication.validateSubmitFlowApprovers",
        "query_impact": "判断审批是否可提交需要同时检查 flow 节点有效性和文件目录完整性，不能只看审批主表状态。",
        "field_targets": [{"dataset": "approval_flow", "field": "approver_user_id"}],
        "evidence_refs": ["ev-proj-submit"],
    },
]

proj_patterns = [
    {
        "pattern_id": "pat-approval-latest-by-project",
        "question": "按项目查最新上线审批",
        "query": "SELECT * FROM tenant_project_approval WHERE ref_tenant_project_approval_tenant_project = :projectCode AND is_latest = 'Y' AND enable = 'Y'",
        "intended_specification": {"entity": "project_approval", "query_type": "latest_by_project"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-proj-create-approval"],
    },
    {
        "pattern_id": "pat-approval-detail-by-no",
        "question": "按审批编号查项目审批详情",
        "query": "SELECT a.*, p.name AS project_name FROM tenant_project_approval a LEFT JOIN tenant_project p ON p.code = a.ref_tenant_project_approval_tenant_project WHERE a.approval_no = :approvalNo",
        "intended_specification": {"entity": "project_approval", "query_type": "detail_by_no"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-proj-submit"],
    },
    {
        "pattern_id": "pat-approval-passed-count",
        "question": "审批通过的项目有多少",
        "query": "SELECT COUNT(*) FROM tenant_project_approval WHERE wf_status = 'FINISHED' AND enable = 'Y'",
        "intended_specification": {"caliber_id": "cal-approval-passed", "metric_id": "metric-approval-passed-count"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-proj-handle-status"],
    },
]

proj_unit = {
    "unit_id": "project-approval",
    "revision": 1,
    "title": "项目上线审批",
    "aliases": ["项目审批", "上线审批"],
    "domain": "product",
    "applicability": "租户项目发起/复制/提交/审批/生效的上线审批闭环",
    "description": "穿透 ProjectApprovalApplication 与 ProjectApprovalDeskApplication：创建审批、查流程配置、提交审批（先删后增节点实例、回写立项编号）、启动工作流、节点审批（法务/业务经理/通用/退回/驳回/转审）、终态项目生效。",
    "content": {
        "concepts": proj_concepts,
        "processes": proj_processes,
        "datasets": proj_datasets,
        "relationships": proj_relationships,
        "metrics": proj_metrics,
        "calibers": proj_calibers,
        "domain_rules": proj_rules,
        "verified_query_patterns": proj_patterns,
    },
    "evidence_refs": ["ev-proj-submit"],
    "unit_links": [],
    "assumptions": ["工作流引擎（ProjectApprovalWorkflowAdapter）为外部工作流服务，不落本地知识表"],
    "conflicts": [],
    "confidence": 0.75,
}

# ---------------------------------------------------------------------------
# Unit 3: funding-rule
# ---------------------------------------------------------------------------
fund_info_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-fund-info-schema"]),
    fld("code", "code", "varchar", "编码", refs=["ev-fund-info-schema"]),
    fld("funding_party_mark", "funding_party_mark", "varchar", "资金方标识", refs=["ev-fund-info-schema"]),
    fld("funding_party_name", "funding_party_name", "varchar", "资方名称", refs=["ev-fund-info-schema"]),
    fld("product_code", "product_code", "varchar", "产品code", refs=["ev-fund-info-schema"]),
    fld("rule_status", "rule_status", "varchar", "规则状态 ACTIVE/INACTIVE/PENDING", dictionary=RULE_STATUS_DICT, refs=["ev-fund-info-schema", "ev-fund-rule-status-dict"]),
    fld("version", "version", "int", "版本号", refs=["ev-fund-info-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-fund-info-schema"]),
]

fund_detail_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-fund-detail-schema"]),
    fld("rule_info_id", "rule_info_id", "bigint", "关系规则信息ID", refs=["ev-fund-detail-schema"]),
    fld("rule_key", "rule_key", "varchar", "字段key 对应front_key", refs=["ev-fund-detail-schema"]),
    fld("rule_value", "rule_value", "varchar", "规则值", refs=["ev-fund-detail-schema"]),
    fld("fund_rule_code_ref", "fund_rule_code_ref", "varchar", "关联规则信息code", refs=["ev-fund-detail-schema"]),
    fld("rule_layer", "rule_layer", "varchar", "规则层", dictionary=RULE_LAYER_DICT, refs=["ev-fund-detail-schema", "ev-fund-rule-layer-dict"]),
    fld("version", "version", "int", "版本", refs=["ev-fund-detail-schema"]),
    fld("funding_party_mark", "funding_party_mark", "varchar", "资方标识", refs=["ev-fund-detail-schema"]),
    fld("product_code", "product_code", "varchar", "产品code", refs=["ev-fund-detail-schema"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-fund-detail-schema"]),
]

fund_front_fields = [
    fld("id", "id", "bigint", "表主键", refs=["ev-fund-front-schema"]),
    fld("product_code", "product_code", "varchar", "产品code", refs=["ev-fund-front-schema"]),
    fld("front_key", "front_key", "varchar", "前端字段key", refs=["ev-fund-front-schema"]),
    fld("key_name", "key_name", "varchar", "字段名称描述", refs=["ev-fund-front-schema"]),
    fld("key_type", "key_type", "varchar", "字段业务规则类型", refs=["ev-fund-front-schema"]),
    fld("rule_key", "rule_key", "varchar", "规则字段key", refs=["ev-fund-front-schema"]),
    fld("rule_layer", "rule_layer", "varchar", "规则层 UNDERLYING/FINANCING", dictionary=RULE_LAYER_DICT, refs=["ev-fund-front-schema", "ev-fund-rule-layer-dict"]),
    fld("enable", "enable", "varchar", "enable", refs=["ev-fund-front-schema"]),
]

# dormant datasets
dormant_tables = [
    ("funding_party_rule_cfg", "funding_party_rule_cfg", "资金方规则配置主表（休眠表：无入口调用链，仅登记）", "ev-party-cfg-schema"),
    ("funding_party_rule_detail", "funding_party_rule_detail", "资金方规则明细表（休眠表：无入口调用链，仅登记）", "ev-party-detail-schema"),
    ("funding_party_rule_front", "funding_party_rule_front", "资金方规则前端表（休眠表：无入口调用链，仅登记）", "ev-party-front-schema"),
]
dormant_fields = []
fund_dormant_ds_list = []
for dsid, name, desc, ref in dormant_tables:
    fund_dormant_ds_list.append(dset(dsid, name, desc, [], inactive=True, refs=[ref]))

fund_datasets = [
    dset("funding_rule_info", "funding_rule_info", "资金方规则主表", fund_info_fields, refs=["ev-fund-info-schema"]),
    dset("funding_rule_detail", "funding_rule_detail", "资金方规则明细表", fund_detail_fields, refs=["ev-fund-detail-schema"]),
    dset("funding_rule_front_cfg", "funding_rule_front_cfg", "资金方规则前端页面配置", fund_front_fields, refs=["ev-fund-front-schema"]),
] + fund_dormant_ds_list

fund_concepts = [
    {
        "concept_id": "funding-rule",
        "name": "资金方规则",
        "aliases": ["资方规则", "资金规则"],
        "definition": "资金方规则主表 funding_rule_info，以主键 id 锚定。",
        "field_targets": [{"dataset": "funding_rule_info", "field": "id"}],
        "evidence_refs": ["ev-fund-info-schema"],
    },
    {
        "concept_id": "funding-rule-active",
        "name": "生效中规则",
        "aliases": ["生效规则"],
        "definition": "资金方规则状态为 ACTIVE。",
        "dictionary": {"ACTIVE": "生效中"},
        "field_targets": [{"dataset": "funding_rule_info", "field": "rule_status"}],
        "evidence_refs": ["ev-fund-rule-status-dict"],
    },
    {
        "concept_id": "funding-rule-layer",
        "name": "规则分层",
        "aliases": ["底层规则", "融资规则"],
        "definition": "资金方规则明细按 rule_layer 分为底层规则/融资规则/其他规则。",
        "dictionary": RULE_LAYER_DICT,
        "field_targets": [{"dataset": "funding_rule_detail", "field": "rule_layer"}],
        "evidence_refs": ["ev-fund-rule-layer-dict"],
    },
]

fund_processes = [
    {
        "stage_id": "rule-maintain",
        "name": "保存/更新资金方规则",
        "description": "新增时查重并插入 funding_rule_info（rule_status=PENDING, version=1）；更新时 version 累加 1；按 front_key 匹配 front_cfg 后 saveOrUpdate 明细。",
        "trigger": "FundRuleInfoApplication.saveRuleInfo",
        "enter_conditions": ["productCode 非空", "fundingPartyMark 非空"],
        "exit_conditions": ["funding_rule_info 已保存/版本已递增", "funding_rule_detail 已按 front_cfg 匹配保存"],
        "next_stages": ["rule-effect"],
        "data_effects": [
            {"operation": "read", "dataset": "funding_rule_info", "fields": ["id", "code", "funding_party_mark", "product_code", "rule_status", "version"], "condition": "product_code = :productCode AND funding_party_mark = :fundingPartyMark", "description": "新增分支查重", "evidence_refs": ["ev-fund-save-rule"]},
            {"operation": "insert", "dataset": "funding_rule_info", "fields": ["code", "funding_party_mark", "funding_party_name", "product_code", "rule_status", "version", "enable"], "condition": "ruleInfoId 为空时插入", "description": "新增规则主记录，rule_status=PENDING, version=1", "evidence_refs": ["ev-fund-save-rule"]},
            {"operation": "update", "dataset": "funding_rule_info", "fields": ["version", "funding_party_name"], "condition": "ruleInfoId 非空时更新", "description": "更新分支 version 累加 1", "evidence_refs": ["ev-fund-save-rule"]},
            {"operation": "read", "dataset": "funding_rule_front_cfg", "fields": ["id", "product_code", "front_key", "key_name", "key_type", "rule_key", "rule_layer", "enable"], "condition": "product_code = :productCode", "description": "查询前端规则页面配置", "evidence_refs": ["ev-fund-save-rule"]},
            {"operation": "read", "dataset": "funding_rule_detail", "fields": ["id", "rule_info_id", "rule_key", "rule_value", "fund_rule_code_ref", "rule_layer", "version", "funding_party_mark", "product_code", "enable"], "condition": "rule_info_id = :ruleInfoId AND rule_key = :frontKey AND enable='Y'", "description": "匹配已有明细以便 update", "evidence_refs": ["ev-fund-save-rule"]},
            {"operation": "upsert", "dataset": "funding_rule_detail", "fields": ["rule_info_id", "rule_key", "rule_value", "fund_rule_code_ref", "rule_layer", "version", "funding_party_mark", "product_code", "enable"], "condition": "front_key 命中 front_cfg 的 ruleMap entry", "description": "保存/更新规则明细；未命中 front_key 的 entry 跳过", "evidence_refs": ["ev-fund-save-rule"]},
        ],
        "evidence_refs": ["ev-fund-save-rule"],
    },
    {
        "stage_id": "rule-effect",
        "name": "生效/失效规则",
        "description": "运营端将资金方规则状态在 ACTIVE/INACTIVE 之间切换。",
        "trigger": "FundRuleInfoApplication.activeRule / inActiveRule",
        "enter_conditions": ["规则记录存在"],
        "exit_conditions": ["rule_status=ACTIVE 或 INACTIVE"],
        "next_stages": [],
        "data_effects": [
            {"operation": "read", "dataset": "funding_rule_info", "fields": ["id", "rule_status"], "condition": "id = :id", "description": "读规则主记录", "evidence_refs": ["ev-fund-active-rule"]},
            {"operation": "update", "dataset": "funding_rule_info", "fields": ["rule_status"], "condition": "id = :id", "description": "更新规则状态为 ACTIVE/INACTIVE", "evidence_refs": ["ev-fund-active-rule", "ev-fund-inactive-rule"]},
        ],
        "evidence_refs": ["ev-fund-active-rule", "ev-fund-inactive-rule"],
    },
    {
        "stage_id": "rule-query",
        "name": "资金方规则查询",
        "description": "Dubbo 提供者按 fundingPartyMark + productCode + ACTIVE 查询规则主记录，再读 front_cfg 和 detail 组装分层规则结果。",
        "trigger": "FundingPartyRuleProviderImpl.queryFundingPartyRules",
        "enter_conditions": ["fundingPartyId 与 productCode 非空"],
        "exit_conditions": ["返回分层规则明细；无 ACTIVE 规则返回 null"],
        "next_stages": [],
        "data_effects": [
            {"operation": "read", "dataset": "funding_rule_info", "fields": ["id", "code", "funding_party_mark", "funding_party_name", "product_code", "rule_status", "version"], "condition": "funding_party_mark = :fundingPartyId AND product_code = :productCode AND rule_status='ACTIVE'", "description": "查生效规则主记录", "evidence_refs": ["ev-fund-provider-query"]},
            {"operation": "read", "dataset": "funding_rule_front_cfg", "fields": ["id", "product_code", "front_key", "key_name", "key_type", "rule_key", "rule_layer", "enable"], "condition": "product_code = :productCode AND enable='Y'", "description": "查前端规则页面配置", "evidence_refs": ["ev-fund-provider-query"]},
            {"operation": "read", "dataset": "funding_rule_detail", "fields": ["id", "rule_info_id", "rule_key", "rule_value", "fund_rule_code_ref", "rule_layer", "version", "funding_party_mark", "product_code", "enable"], "condition": "rule_info_id = ruleInfo.id AND enable='Y'", "description": "查规则明细并按 rule_layer 分组", "evidence_refs": ["ev-fund-provider-query"]},
        ],
        "evidence_refs": ["ev-fund-provider-query", "ev-fund-query-front"],
    },
]

fund_relationships = [
    {
        "relationship_id": "rel-fund-detail-info",
        "left": {"dataset": "funding_rule_detail", "field": "rule_info_id"},
        "right": {"dataset": "funding_rule_info", "field": "id"},
        "relationship_type": "EQUI_JOIN",
        "cardinality": "many_to_one",
        "business_meaning": "规则明细通过 rule_info_id 关联规则主记录",
        "status": "proposed",
        "evidence_refs": ["ev-fund-query-detail"],
    },
]

fund_calibers = [
    {
        "caliber_id": "cal-fund-rule-active",
        "label": "生效中规则",
        "description": "rule_status=ACTIVE 的资金方规则。",
        "contract_fragment": {"predicate": "rule_status = 'ACTIVE'", "scope": "funding_rule_info 全局定义"},
        "field_targets": [{"dataset": "funding_rule_info", "field": "rule_status"}],
        "evidence_refs": ["ev-fund-rule-status-dict"],
    },
    {
        "caliber_id": "cal-fund-rule-pending",
        "label": "待生效规则",
        "description": "rule_status=PENDING 的资金方规则。",
        "contract_fragment": {"predicate": "rule_status = 'PENDING'", "scope": "funding_rule_info 全局定义"},
        "field_targets": [{"dataset": "funding_rule_info", "field": "rule_status"}],
        "evidence_refs": ["ev-fund-rule-status-dict"],
    },
    {
        "caliber_id": "cal-fund-rule-product-party",
        "label": "产品+资方规则范围",
        "description": "查询资金方规则的标准范围：product_code + funding_party_mark + rule_status=ACTIVE。",
        "contract_fragment": {"predicate": "product_code = :productCode AND funding_party_mark = :fundingPartyMark AND rule_status = 'ACTIVE'", "scope": "FundingPartyRuleProviderImpl.queryFundingPartyRules"},
        "field_targets": [{"dataset": "funding_rule_info", "field": "product_code"}, {"dataset": "funding_rule_info", "field": "funding_party_mark"}, {"dataset": "funding_rule_info", "field": "rule_status"}],
        "evidence_refs": ["ev-fund-provider-query"],
    },
]

fund_metrics = [
    {
        "metric_id": "metric-fund-rule-count",
        "name": "资金方规则数",
        "description": "资金方规则主记录数。",
        "aggregation": "COUNT",
        "field": {"dataset": "funding_rule_info", "field": "id"},
        "grain": [{"dataset": "funding_rule_info", "field": "id"}],
        "filters": [],
        "evidence_refs": ["ev-fund-save-rule"],
    },
    {
        "metric_id": "metric-fund-rule-active-count",
        "name": "生效中规则数",
        "description": "rule_status=ACTIVE 的资金方规则数。",
        "aggregation": "COUNT",
        "field": {"dataset": "funding_rule_info", "field": "id"},
        "grain": [{"dataset": "funding_rule_info", "field": "id"}],
        "filters": [{"field": "rule_status", "op": "=", "value": "ACTIVE"}],
        "evidence_refs": ["ev-fund-active-rule"],
    },
    {
        "metric_id": "metric-fund-rule-detail-count",
        "name": "资金方规则明细数",
        "description": "资金方规则明细记录数。",
        "aggregation": "COUNT",
        "field": {"dataset": "funding_rule_detail", "field": "id"},
        "grain": [{"dataset": "funding_rule_detail", "field": "id"}],
        "filters": [],
        "evidence_refs": ["ev-fund-save-rule"],
    },
]

fund_rules = [
    {
        "rule_id": "rule-fund-unique-product-party",
        "label": "同一产品下同一资方规则唯一",
        "content": "新增规则时按 productCode + fundingPartyMark 查重，已存在则禁止新增。",
        "applicability": "FundRuleInfoApplication.saveRuleInfo 新增分支",
        "query_impact": "查询产品-资方规则时不会出现重复主记录，但历史版本可能有多条 detail（enable=Y 为当前有效）。",
        "field_targets": [{"dataset": "funding_rule_info", "field": "product_code"}, {"dataset": "funding_rule_info", "field": "funding_party_mark"}],
        "evidence_refs": ["ev-fund-save-rule"],
    },
    {
        "rule_id": "rule-fund-version-increment",
        "label": "更新规则版本累加 1",
        "content": "更新资金方规则时 version 在原值上累加 1，并将新值写入 funding_rule_info 与 funding_rule_detail。",
        "applicability": "FundRuleInfoApplication.saveRuleInfo 更新分支",
        "query_impact": "版本字段用于识别规则更新次数；查询最新规则应按 rule_status 和 enable=Y 明细，而非只按 version。",
        "field_targets": [{"dataset": "funding_rule_info", "field": "version"}, {"dataset": "funding_rule_detail", "field": "version"}],
        "evidence_refs": ["ev-fund-save-rule"],
    },
    {
        "rule_id": "rule-fund-detail-skip-unknown-front-key",
        "label": "未知 front_key 明细跳过",
        "content": "保存规则明细时，只有 front_key 命中该产品 funding_rule_front_cfg 的 entry 才入库，未知 key 跳过不中断。",
        "applicability": "FundRuleInfoApplication.saveRuleInfo 明细保存循环",
        "query_impact": "规则明细的 rule_key 集合受 front_cfg 约束，查询时以 front_cfg 为目录。",
        "field_targets": [{"dataset": "funding_rule_detail", "field": "rule_key"}],
        "evidence_refs": ["ev-fund-save-rule"],
    },
    {
        "rule_id": "rule-fund-provider-active-only",
        "label": "资金方规则查询只返回 ACTIVE",
        "content": "资金方规则查询接口只返回 rule_status=ACTIVE 的规则，无生效规则返回 null。",
        "applicability": "FundingPartyRuleProviderImpl.queryFundingPartyRules",
        "query_impact": "对客查询资金规则时默认只取生效中规则，PENDING/INACTIVE 不出现在结果中。",
        "field_targets": [{"dataset": "funding_rule_info", "field": "rule_status"}],
        "evidence_refs": ["ev-fund-provider-query"],
    },
]

fund_patterns = [
    {
        "pattern_id": "pat-fund-rule-by-product",
        "question": "查某产品下资金方规则列表",
        "query": "SELECT id, funding_party_mark, funding_party_name, product_code, rule_status, version FROM funding_rule_info WHERE product_code = :productCode AND enable = 'Y'",
        "intended_specification": {"entity": "funding_rule_info", "query_type": "list_by_product"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-fund-save-rule"],
    },
    {
        "pattern_id": "pat-fund-active-rule-detail",
        "question": "查某产品+资方生效规则明细",
        "query": "SELECT d.rule_key, d.rule_value, d.rule_layer FROM funding_rule_detail d JOIN funding_rule_info i ON i.id = d.rule_info_id WHERE i.funding_party_mark = :fundingPartyMark AND i.product_code = :productCode AND i.rule_status = 'ACTIVE' AND d.enable = 'Y'",
        "intended_specification": {"caliber_id": "cal-fund-rule-product-party", "metric_id": "metric-fund-rule-detail-count"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-fund-provider-query"],
    },
    {
        "pattern_id": "pat-fund-active-rule-count",
        "question": "生效中的资金方规则有多少",
        "query": "SELECT COUNT(*) FROM funding_rule_info WHERE rule_status = 'ACTIVE' AND enable = 'Y'",
        "intended_specification": {"caliber_id": "cal-fund-rule-active", "metric_id": "metric-fund-rule-active-count"},
        "verification": {"status": "PENDING_VALIDATION"},
        "evidence_refs": ["ev-fund-active-rule"],
    },
]

fund_unit = {
    "unit_id": "funding-rule",
    "revision": 1,
    "title": "资金方规则",
    "aliases": ["资方规则", "资金规则"],
    "domain": "funding",
    "applicability": "资金方规则维护（保存/生效/失效）与资金方规则对客查询场景",
    "description": "穿透 FundRuleInfoApplication.saveRuleInfo/activeRule/inActiveRule 与 FundingPartyRuleProviderImpl.queryFundingPartyRules：覆盖规则新增查重、版本累加、front_cfg 匹配明细、ACTIVE 查询口径；休眠资金方旧规则表仅登记。",
    "content": {
        "concepts": fund_concepts,
        "processes": fund_processes,
        "datasets": fund_datasets,
        "relationships": fund_relationships,
        "metrics": fund_metrics,
        "calibers": fund_calibers,
        "domain_rules": fund_rules,
        "verified_query_patterns": fund_patterns,
    },
    "evidence_refs": ["ev-fund-save-rule"],
    "unit_links": [],
    "assumptions": ["funding_party_rule_cfg/detail/front 为休眠表，按技能要求保留为 inactive 表级声明，不进维度引用"],
    "conflicts": [],
    "confidence": 0.75,
}

# ---------------------------------------------------------------------------
# Unit 4: dormant registration
# ---------------------------------------------------------------------------
dormant_datasets = [
    dset("org_manage", "org_manage", "组织管理表（休眠表：无入口调用链，仅登记）", [], inactive=True, refs=["ev-org-manage-schema"]),
    dset("tenant_product_ext_field", "tenant_product_ext_field", "租户产品扩展字段表（休眠表：无入口调用链，仅登记）", [], inactive=True, refs=["ev-tenant-ext-field-schema"]),
    dset("tenant_product_ext_field_form", "tenant_product_ext_field_form", "租户产品扩展字段表单表（休眠表：无入口调用链，仅登记）", [], inactive=True, refs=["ev-tenant-ext-field-form-schema"]),
]

dormant_unit = {
    "unit_id": "dormant-registration",
    "revision": 1,
    "title": "休眠表登记",
    "aliases": ["休眠表"],
    "domain": "inventory",
    "applicability": "pplatform-web 中无入口调用链的 @TableName 物理表登记",
    "description": "登记无入口调用链的休眠表（org_manage、tenant_product_ext_field、tenant_product_ext_field_form、funding_party_rule_*）。字段保留在 catalog，单元只做表级声明不参与问数。",
    "content": {
        "concepts": [],
        "processes": [],
        "datasets": dormant_datasets,
        "relationships": [],
        "metrics": [],
        "calibers": [],
        "domain_rules": [],
        "verified_query_patterns": [],
    },
    "evidence_refs": ["ev-org-manage-schema"],
    "unit_links": [],
    "assumptions": ["休眠表不参与维度引用，绑定时未匹配表/字段软失效"],
    "conflicts": [],
    "confidence": 0.6,
}

# ---------------------------------------------------------------------------
# manifest
# ---------------------------------------------------------------------------
manifest = {
    "schema_version": "2.0",
    "package": {
        "package_id": "pplatform-web-v12",
        "revision": 1,
        "title": "pplatform-web 业务知识包 v12（首批关键模块）",
        "namespace": "pplatform-web",
        "description": "从 pplatform-web @ ee434954e 提取首批 3 个关键模块：企业建档与客户项目关联、项目上线审批、资金方规则；另含休眠表登记。",
    },
    "sources": sources,
    "evidence": evidence,
    "units": [
        "units/enterprise-onboarding.yaml",
        "units/project-approval.yaml",
        "units/funding-rule.yaml",
        "units/dormant-registration.yaml",
    ],
}

# package-level physical relationships
package_relationships = [
    {"left_table": "cust_person_info", "left_field": "ref_cust_company_info", "right_table": "cust_company_info", "right_field": "code", "evidence": "read-flow:BaseAccessOperProcess.java:185", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "cust_project_rel", "left_field": "ref_cust_project_rel_cust_company_info", "right_table": "cust_company_info", "right_field": "code", "evidence": "read-flow/write-flow:OperCustFacade.java:1044,1085", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "cust_project_rel", "left_field": "project_id", "right_table": "tenant_project", "right_field": "id", "evidence": "write-flow:OperCustFacade.java:1080; cast:long_to_string", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project", "left_field": "platform_product_code", "right_table": "platform_product", "right_field": "product_code", "evidence": "read-flow:OperCustFacade.java:1068-1069", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "cust_build_record", "left_field": "cust_id", "right_table": "cust_company_info", "right_field": "id", "evidence": "write-flow:OperCustFacade.java:892", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "cust_build_record", "left_field": "person_id", "right_table": "cust_person_info", "right_field": "id", "evidence": "write-flow:OperCustFacade.java:893", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval", "left_field": "ref_tenant_project_approval_tenant_project", "right_table": "tenant_project", "right_field": "code", "evidence": "write-flow:ProjectApprovalApplication.java:391", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval", "left_field": "flow_code", "right_table": "tenant_project_approval_flow_config", "right_field": "flow_code", "evidence": "read-flow:ProjectApprovalApplication.java:502", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval_flow", "left_field": "ref_tenant_project_approval_flow_tenant_project_approval", "right_table": "tenant_project_approval", "right_field": "code", "evidence": "write-flow:ProjectApprovalApplication.java:891", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval_flow_node", "left_field": "ref_tenant_project_approval_flow_node_project_approval", "right_table": "tenant_project_approval", "right_field": "code", "evidence": "write-flow:ProjectApprovalDeskApplication.java:471", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval_flow_node", "left_field": "ref_tenant_project_approval_flow_node_project_approval_flow", "right_table": "tenant_project_approval_flow", "right_field": "code", "evidence": "write-flow:ProjectApprovalDeskApplication.java:472", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval_business_info", "left_field": "ref_tenant_project_approval_business_info_project_approval", "right_table": "tenant_project_approval", "right_field": "code", "evidence": "read-flow:ProjectApprovalApplication.java:1304", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval_flow_credit", "left_field": "ref_tenant_project_approval_flow_credit_project_approval", "right_table": "tenant_project_approval", "right_field": "code", "evidence": "write-flow:ProjectApprovalDeskApplication.java:497", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval_flow_credit", "left_field": "ref_tenant_project_approval_flow_credit_project_approval_node", "right_table": "tenant_project_approval_flow_node", "right_field": "code", "evidence": "write-flow:ProjectApprovalDeskApplication.java:498", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval_flow_file", "left_field": "ref_tenant_project_approval_flow_file_project_approval", "right_table": "tenant_project_approval", "right_field": "code", "evidence": "write-flow:ProjectApprovalDeskApplication.java:657", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "tenant_project_approval_flow_file", "left_field": "ref_tenant_project_approval_flow_file_project_approval_flow_node", "right_table": "tenant_project_approval_flow_node", "right_field": "code", "evidence": "write-flow:ProjectApprovalDeskApplication.java:656", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
    {"left_table": "funding_rule_detail", "left_field": "rule_info_id", "right_table": "funding_rule_info", "right_field": "id", "evidence": "read-flow:FundRuleInfoApplication.java:362-364", "relationship_type": "EQUI_JOIN", "cardinality": "many_to_one"},
]

# ---------------------------------------------------------------------------
# coverage
# ---------------------------------------------------------------------------
callgraph_path = Path("/Users/fanjunwei/Projects/SQLBot/.tmp-v12-extraction/callgraph.yaml")
with open(callgraph_path) as f:
    cg = yaml.safe_load(f)
all_tables = sorted(cg["tables"].keys())

covered_tables = {
    "cust_company_info", "cust_person_info", "cust_build_record", "cust_project_rel",
    "tenant_project", "platform_product", "tenant_setting_config",
    "tenant_project_approval", "tenant_project_approval_business_info",
    "tenant_project_approval_flow_config", "tenant_project_approval_flow",
    "tenant_project_approval_flow_node", "tenant_project_approval_flow_credit",
    "tenant_project_approval_flow_file",
    "funding_rule_info", "funding_rule_detail", "funding_rule_front_cfg",
    "funding_party_rule_cfg", "funding_party_rule_detail", "funding_party_rule_front",
    "org_manage", "tenant_product_ext_field", "tenant_product_ext_field_form",
}
inactive_tables = {
    "funding_party_rule_cfg": "无入口调用链证据，资金链路由 FundingPartyRuleProviderImpl 走 funding_rule_*",
    "funding_party_rule_detail": "无入口调用链证据",
    "funding_party_rule_front": "无入口调用链证据",
    "org_manage": "无入口调用链证据",
    "tenant_product_ext_field": "无入口调用链证据",
    "tenant_product_ext_field_form": "无入口调用链证据",
}
excluded_tables = {
    "argeement_migratory_record": "迁移日志表，无问数场景",
    "async_io_task": "异步任务技术表，无问数场景",
    "client_api_sync_error": "客户端 API 同步错误日志，无问数场景",
    "cust_access_secret": "接入密钥技术配置，无问数场景",
    "cust_config_mapping": "配置映射技术表，无问数场景",
    "cust_sftp": "SFTP 技术配置，无问数场景",
    "gpt_learn_poster_log": "GPT 学习海报点击日志，无问数场景",
    "migratory_user_record": "迁移用户记录日志，无问数场景",
    "short_link": "短链技术表，无问数场景",
    "tenant_migarory_log": "迁移日志表，无问数场景",
    "tenant_product_menu": "租户产品菜单技术配置，无问数场景",
    "tenant_product_menu_res": "租户产品菜单资源技术配置，无问数场景",
    "tenant_setting_config_share": "租户配置共享技术表，无问数场景",
}
coverage = {
    "schema_version": "1.0",
    "repository": "pplatform-web",
    "repository_revision": REV,
    "tables": all_tables,
    "excluded": excluded_tables,
    "inactive": inactive_tables,
}

# ---------------------------------------------------------------------------
# write files
# ---------------------------------------------------------------------------
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / "units").mkdir(parents=True, exist_ok=True)

def write_yaml(path, data):
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")

write_yaml(ROOT / "knowledge-package.yaml", manifest)
write_yaml(ROOT / "relationships.yaml", {"relationships": package_relationships})
write_yaml(ROOT / "coverage.yaml", coverage)
write_yaml(ROOT / "units" / "enterprise-onboarding.yaml", onboarding_unit)
write_yaml(ROOT / "units" / "project-approval.yaml", proj_unit)
write_yaml(ROOT / "units" / "funding-rule.yaml", fund_unit)
write_yaml(ROOT / "units" / "dormant-registration.yaml", dormant_unit)

print("written", ROOT)
print("tables", len(all_tables), "covered", len(covered_tables), "inactive", len(inactive_tables), "excluded", len(excluded_tables))
print("gaps", len(all_tables) - len(covered_tables) - len(excluded_tables))
