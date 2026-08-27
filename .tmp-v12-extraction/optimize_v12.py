# -*- coding: utf-8 -*-
"""Optimize v12 package against updated skill: FK classification, derived_from annotations, dataset code_path evidence, fixes."""
import yaml
from pathlib import Path

PKG = Path("/Users/fanjunwei/Projects/SQLBot/data/knowledge-packages/v12")
UNITS = PKG / "units"

def load(p):
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def save(p, d):
    p.write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")

def get_unit(uid):
    p = UNITS / f"{uid}.yaml"
    d = load(p)
    return p, d

def get_ds(unit, dsid):
    for ds in unit['content']['datasets']:
        if ds['dataset_id'] == dsid:
            return ds
    return None

def set_field_desc(unit, dsid, field_id, desc):
    ds = get_ds(unit, dsid)
    if ds:
        for f in ds['fields']:
            if f['field_id'] == field_id:
                f['description'] = desc
                return

def remove_field(unit, dsid, field_id):
    ds = get_ds(unit, dsid)
    if ds:
        ds['fields'] = [f for f in ds['fields'] if f['field_id'] != field_id]
        # also remove from data_effects fields
        for st in unit['content']['processes']:
            for de in st['data_effects']:
                if de['dataset'] == dsid and field_id in de['fields']:
                    de['fields'].remove(field_id)

def add_field(unit, dsid, f):
    ds = get_ds(unit, dsid)
    if ds:
        if not any(x['field_id'] == f['field_id'] for x in ds['fields']):
            ds['fields'].append(f)

# ---------------------------------------------------------------------------
# 1) fix business_manager physical name and description
# ---------------------------------------------------------------------------
p, u = get_unit('wechat-project-statistics')
set_field_desc(u, 'wechat_project_approval_apply', 'business_manager', '业务经理')
for f in get_ds(u, 'wechat_project_approval_apply')['fields']:
    if f['field_id'] == 'business_manager':
        f['field_id'] = 'bussiness_manager'
        f['name'] = 'bussiness_manager'
# update references from business_manager to bussiness_manager in this unit
def fix_refs(obj):
    if isinstance(obj, dict):
        for k,v in obj.items():
            if k == 'field' and isinstance(v, dict) and v.get('field') == 'business_manager':
                v['field'] = 'bussiness_manager'
            elif isinstance(v, (dict,list)):
                fix_refs(v)
    elif isinstance(obj, list):
        for x in obj:
            fix_refs(x)
# only in fields lists? easier: do string replacement in YAML later, but direct replace fields
for st in u['content']['processes']:
    for de in st['data_effects']:
        if 'business_manager' in de.get('fields',[]):
            de['fields'] = ['bussiness_manager' if x=='business_manager' else x for x in de['fields']]
# no concept/metric uses business_manager field id, fine
save(p, u)
print('fixed wechat bussiness_manager')

# ---------------------------------------------------------------------------
# 2) tenant_product: add code field; annotate derived copies
# ---------------------------------------------------------------------------
p, u = get_unit('tenant-product')
add_field(u, 'tenant_product', {
    'field_id': 'code', 'name': 'code', 'data_type': 'varchar', 'description': '编码',
    'evidence_refs': ['ev-tenant-product-schema']
})
set_field_desc(u, 'tenant_product', 'platform_product_code', '平台产品编号（冗余副本，derived_from platform_product.product_code）')
set_field_desc(u, 'tenant_product', 'ref_tenant_product_tenant_setting_config', '租户-产品（关联 tenant_setting_config.code）')
set_field_desc(u, 'tenant_product', 'ref_tenant_product_project_code', '租户产品-平台产品（冗余副本，derived_from platform_product.code）')
set_field_desc(u, 'tenant_product', 'tenant_id', '租户id（租户隔离字段，非关联）')
# add code to process create/read fields? Not necessary if package relationship references; but process uses fields list with no code
# Ensure code appears in create read/upsert? code set? Domain create doesn't set code explicitly but base model may. We'll reference via relationship only.
save(p, u)
print('tenant-product optimized')

# ---------------------------------------------------------------------------
# 3) tenant_setting_config: add code field (onboarding authoritative)
# ---------------------------------------------------------------------------
p, u = get_unit('enterprise-onboarding')
add_field(u, 'tenant_setting', {
    'field_id': 'code', 'name': 'code', 'data_type': 'varchar', 'description': '编码',
    'evidence_refs': ['ev-tenant-setting-schema']
})
# annotate tenant_project.product_id and default_project_id
set_field_desc(u, 'tenant_project', 'product_id', '产品编码（真 FK：tenant_project.product_id -> tenant_product.id）')
set_field_desc(u, 'tenant_setting', 'default_project_id', '默认项目（FK：tenant_setting_config.default_project_id -> tenant_project.id）')
set_field_desc(u, 'cust_project_rel', 'product_id', '产品（反规范化副本，derived_from tenant_project.product_id）')
set_field_desc(u, 'person', 'platform_user_id', '运营系统用户id（外部运营中台用户标识，非本库外键）')
save(p, u)
print('enterprise-onboarding optimized')

# ---------------------------------------------------------------------------
# 4) project-approval: annotate project_approval_id
# ---------------------------------------------------------------------------
p, u = get_unit('project-approval')
set_field_desc(u, 'tenant_project', 'project_approval_id', '项目上线审批ID（FK：tenant_project.project_approval_id -> tenant_project_approval.id）')
set_field_desc(u, 'approval_flow', 'approver_user_id', '审批人 userId（外部用户系统标识，非本库外键）')
set_field_desc(u, 'approval_flow_node', 'operator_user_id', '操作人 userId（外部用户系统标识，非本库外键）')
set_field_desc(u, 'approval_flow_credit', 'credited_cust_id', '被授信方（核心企业）id（业务标识，非本库外键）')
set_field_desc(u, 'approval_flow_credit', 'crediting_cust_id', '授信方（资金方）id（业务标识，非本库外键）')
set_field_desc(u, 'approval_flow_file', 'catg_id', '影像分类编码（外部影像系统分类标识）')
set_field_desc(u, 'approval_flow_file', 'file_id', '文件id（外部影像系统文件标识）')
save(p, u)
print('project-approval optimized')

# ---------------------------------------------------------------------------
# 5) funding-rule: annotate fund_rule_code_ref derived
# ---------------------------------------------------------------------------
p, u = get_unit('funding-rule')
set_field_desc(u, 'funding_rule_detail', 'fund_rule_code_ref', '关联规则信息code（冗余副本，derived_from funding_rule_info.code）')
set_field_desc(u, 'funding_rule_detail', 'product_code', '产品code（业务键，关联 platform_product.product_code）')
set_field_desc(u, 'funding_rule_info', 'product_code', '产品code（业务键，关联 platform_product.product_code）')
set_field_desc(u, 'funding_rule_front_cfg', 'product_code', '产品code（业务键，关联 platform_product.product_code）')
save(p, u)
print('funding-rule optimized')

# ---------------------------------------------------------------------------
# 6) funding-exception-resolution: annotate external codes
# ---------------------------------------------------------------------------
p, u = get_unit('funding-exception-resolution')
set_field_desc(u, 'funding_exception_resolution', 'funding_party_code', '对接方标识（外部资金方系统业务标识，非本库外键）')
set_field_desc(u, 'funding_exception_resolution', 'product_code', '产品code（业务键，关联 platform_product.product_code）')
save(p, u)
print('funding-exception optimized')

# ---------------------------------------------------------------------------
# 7) customer-account-role: annotate external ids
# ---------------------------------------------------------------------------
p, u = get_unit('customer-account-role')
set_field_desc(u, 'cust_role', 'platform_cust_id', '关联平台企业ID（外部运营中台企业标识，非本库外键）')
set_field_desc(u, 'cust_user_rel', 'user_id', '用户id（外部用户系统标识，非本库外键）')
save(p, u)
print('customer-account-role optimized')

# ---------------------------------------------------------------------------
# 8) customer-change: annotate external operator ids; person_id relationship handled in relationships
# ---------------------------------------------------------------------------
p, u = get_unit('customer-change')
set_field_desc(u, 'cust_oper_change_record', 'person_id', '企业联系人id（FK：cust_oper_change_record.person_id -> cust_person_info.id）')
set_field_desc(u, 'cust_oper_change_record', 'before_operator_id', '变更前运营人员ID（外部运营中台人员标识，非本库外键）')
set_field_desc(u, 'cust_oper_change_record', 'after_operator_id', '变更后运营人员ID（外部运营中台人员标识，非本库外键）')
save(p, u)
print('customer-change optimized')

# ---------------------------------------------------------------------------
# 9) ca-fee: annotate project_id and tenant_id
# ---------------------------------------------------------------------------
p, u = get_unit('ca-fee')
set_field_desc(u, 'ca_fee_order', 'project_id', '触发项目 ID（FK：ca_fee_order.project_id -> tenant_project.id）')
set_field_desc(u, 'ca_fee_project_config', 'tenant_id', '所属租户（租户隔离字段，非关联）')
save(p, u)
print('ca-fee optimized')

# ---------------------------------------------------------------------------
# 10) customer-auth-product: annotate and prepare relationships
# ---------------------------------------------------------------------------
p, u = get_unit('customer-auth-product')
set_field_desc(u, 'cust_auth_application', 'platform_product_code', '平台产品编码（冗余副本，derived_from tenant_product.platform_product_code）')
set_field_desc(u, 'cust_auth_application', 'ref_cust_auth_application_tenant_product', '关联应用（FK：-> tenant_product.code）')
set_field_desc(u, 'cust_customized_product', 'cust_id', '企业id（FK：-> cust_company_info.id）')
set_field_desc(u, 'cust_customized_product', 'ref_cust_customized_product_cust_company_info', '客户关联自定义产品配置（FK：-> cust_company_info.code）')
set_field_desc(u, 'cust_interworking_product', 'cust_id', '企业id（FK：-> cust_company_info.id）')
set_field_desc(u, 'cust_interworking_product', 'platform_product_code', '平台产品编码（冗余副本，derived_from platform_product.product_code）')
set_field_desc(u, 'cust_interworking_product', 'product_id', '互通产品id（FK：-> tenant_interworking_product.id）')
set_field_desc(u, 'cust_interworking_product', 'ref_cust_interworking_product_tenant_interworking_product', '关联互通产品（FK：-> tenant_interworking_product.code）')
save(p, u)
print('customer-auth-product optimized')

# ---------------------------------------------------------------------------
# 11) customer-group: annotate parent/root
# ---------------------------------------------------------------------------
p, u = get_unit('customer-group')
set_field_desc(u, 'cust_group_rel', 'parent_cust_id', '父企业id（FK：-> cust_company_info.id）')
set_field_desc(u, 'cust_group_rel', 'root_cust_id', '根企业id（FK：-> cust_company_info.id）')
save(p, u)
print('customer-group optimized')

# ---------------------------------------------------------------------------
# 12) customer-survey-invite-settings: annotate and remove user_id from survey_answer? keep with external desc
# ---------------------------------------------------------------------------
p, u = get_unit('customer-survey-invite-settings')
set_field_desc(u, 'cust_invite_info', 'invite_cust_id', '邀请客户id（FK：-> cust_company_info.id）')
set_field_desc(u, 'cust_invite_info', 'channel_code', '渠道码（渠道业务编码，非外键）')
set_field_desc(u, 'cust_company_survey_state', 'company_id', '企业ID（FK：-> cust_company_info.id）')
set_field_desc(u, 'cust_company_survey_state', 'first_visitor_user_id', '首个进入产融首页的用户ID（外部用户系统标识，非本库外键）')
set_field_desc(u, 'cust_company_survey_whitelist', 'company_id', '企业id（FK：-> cust_company_info.id）')
set_field_desc(u, 'cust_survey_answer', 'company_id', '当前登录企业ID（FK：-> cust_company_info.id）')
set_field_desc(u, 'cust_survey_answer', 'user_id', '当前登录用户ID（外部用户系统标识，非本库外键）')
set_field_desc(u, 'cust_survey_answer', 'survey_code', '调研编码（对应 Nacos 配置，非外键）')
save(p, u)
print('customer-survey optimized')

# ---------------------------------------------------------------------------
# 13) customer-project-tools: remove project_id from pushcust; annotate code_record
# ---------------------------------------------------------------------------
p, u = get_unit('customer-project-tools')
remove_field(u, 'cust_project_pushcust', 'project_id')
remove_field(u, 'cust_project_code_record', 'use_id')
set_field_desc(u, 'cust_project_code_record', 'company_id', '企业id（FK：-> cust_company_info.id）')
set_field_desc(u, 'cust_project_code_record', 'channel_code', '渠道码（渠道业务编码，非外键）')
save(p, u)
print('customer-project-tools optimized')

# ---------------------------------------------------------------------------
# 14) tenant-interworking: add code field to product; annotate
# ---------------------------------------------------------------------------
p, u = get_unit('tenant-interworking')
add_field(u, 'tenant_interworking_product', {
    'field_id': 'code', 'name': 'code', 'data_type': 'varchar', 'description': '编码',
    'evidence_refs': ['ev-tenant-interworking-product-schema']
})
set_field_desc(u, 'tenant_interworking_product', 'tenant_id', '租户id（租户隔离字段，非关联）')
set_field_desc(u, 'tenant_interworking_product', 'platform_product_code', '平台产品编号（冗余副本，derived_from platform_product.product_code）')
set_field_desc(u, 'tenant_interworking_product', 'ref_tenant_interworking_product_tenant_setting_config', '关联租户（FK：-> tenant_setting_config.code）')
set_field_desc(u, 'tenant_interworking_project', 'tenant_id', '租户id（租户隔离字段，非关联）')
set_field_desc(u, 'tenant_interworking_project', 'platform_product_code', '平台产品编码（冗余副本，derived_from tenant_interworking_product.platform_product_code）')
set_field_desc(u, 'tenant_interworking_project', 'project_id', '项目id（FK：-> tenant_project.id）')
set_field_desc(u, 'tenant_interworking_project', 'ref_tenant_interworking_project_tenant_interworking_product', '租户产品项目（FK：-> tenant_interworking_product.code）')
save(p, u)
print('tenant-interworking optimized')

# ---------------------------------------------------------------------------
# 15) wechat-project-statistics: annotate external wec/operation ids and project_id
# ---------------------------------------------------------------------------
p, u = get_unit('wechat-project-statistics')
set_field_desc(u, 'wechat_project_approval_apply', 'project_id', '关联的项目id（FK：-> tenant_project.id）')
set_field_desc(u, 'wec_project_operation_rel', 'wec_project_id', '微企链项目id（外部微企链系统标识，非本库外键）')
set_field_desc(u, 'wec_project_cust_operation_rel', 'wec_rel_id', '微企链关联关系id（外部微企链系统标识，非本库外键）')
set_field_desc(u, 'wec_project_cust_operation_rel', 'company_id', '微企链企业id（外部微企链系统标识，非本库外键）')
set_field_desc(u, 'wec_project_cust_operation_rel', 'project_id', '微企链项目id（外部微企链系统标识，非本库外键）')
set_field_desc(u, 'operation_user', 'operation_id', '运营中台id（外部运营中台业务标识，非本库外键）')
save(p, u)
print('wechat-project-statistics optimized')

# ---------------------------------------------------------------------------
# 16) authorization-agreement: annotate
# ---------------------------------------------------------------------------
p, u = get_unit('authorization-agreement')
set_field_desc(u, 'authorization_agreement', 'cust_manager_id', '企业管理员id（外部用户系统标识，非本库外键）')
set_field_desc(u, 'authorization_agreement', 'platform_product_code', '平台产品id（业务键，关联 platform_product.product_code）')
save(p, u)
print('authorization-agreement optimized')

# ---------------------------------------------------------------------------
# 17) add dataset-level code_path evidence to active datasets
# ---------------------------------------------------------------------------
for p in sorted(UNITS.glob('*.yaml')):
    u = load(p)
    changed = False
    # collect process evidence per dataset
    for ds in u['content']['datasets']:
        if ds.get('inactive'):
            continue
        refs = set(ds.get('evidence_refs', []))
        for st in u['content']['processes']:
            for de in st['data_effects']:
                if de['dataset'] == ds['dataset_id']:
                    refs.update(de.get('evidence_refs', []))
            refs.update(st.get('evidence_refs', []))
        # also pattern evidence? not needed; process code_path is enough
        ds['evidence_refs'] = sorted(refs)
        changed = True
    save(p, u)

print('dataset code_path evidence updated')

# ---------------------------------------------------------------------------
# 18) add missing package relationships
# ---------------------------------------------------------------------------
relp = PKG / 'relationships.yaml'
rel = load(relp)
rels = rel['relationships']
seen = {(r['left_table'], r['left_field'], r['right_table'], r['right_field']) for r in rels}
def add_rel(left_table, left_field, right_table, right_field, evidence, relationship_type='EQUI_JOIN', cardinality='many_to_one'):
    key = (left_table, left_field, right_table, right_field)
    if key not in seen:
        rels.append({'left_table': left_table, 'left_field': left_field, 'right_table': right_table, 'right_field': right_field,
                     'evidence': evidence, 'relationship_type': relationship_type, 'cardinality': cardinality})
        seen.add(key)

add_rel('tenant_setting_config', 'default_project_id', 'tenant_project', 'id', 'read-flow:OperCustFacade.java:1052')
add_rel('tenant_project', 'product_id', 'tenant_product', 'id', 'write-flow:TenantProductDomainService.java:147')
add_rel('tenant_project', 'project_approval_id', 'tenant_project_approval', 'id', 'write-flow:ProjectApprovalApplication.java:404')
add_rel('tenant_product', 'ref_tenant_product_tenant_setting_config', 'tenant_setting_config', 'code', 'write-flow:TenantProductDomainService.java:162')
add_rel('cust_auth_application', 'ref_cust_auth_application_tenant_product', 'tenant_product', 'code', 'write-flow:SubmitCustInfoEnhanceService.java:136')
add_rel('cust_customized_product', 'cust_id', 'cust_company_info', 'id', 'write-flow:ClientAppController.java:372')
add_rel('cust_customized_product', 'ref_cust_customized_product_cust_company_info', 'cust_company_info', 'code', 'write-flow:ClientAppController.java:372')
add_rel('cust_interworking_product', 'cust_id', 'cust_company_info', 'id', 'read-flow:CustCompanyUtilApplication.java:261')
add_rel('cust_interworking_product', 'product_id', 'tenant_interworking_product', 'id', 'write-flow:CustInterworkingProductDomainService.java:141')
add_rel('cust_interworking_product', 'ref_cust_interworking_product_tenant_interworking_product', 'tenant_interworking_product', 'code', 'write-flow:CustInterworkingProductDomainService.java:141')
add_rel('cust_group_rel', 'parent_cust_id', 'cust_company_info', 'id', 'write-flow:CustGroupRelApplication.java:426')
add_rel('cust_group_rel', 'root_cust_id', 'cust_company_info', 'id', 'write-flow:CustGroupRelApplication.java:428')
add_rel('cust_oper_change_record', 'person_id', 'cust_person_info', 'id', 'read-flow:OperChangeRecordApplication.java:46')
add_rel('ca_fee_order', 'project_id', 'tenant_project', 'id', 'write-flow:CaFeeOrderApplication.java:47')
add_rel('funding_rule_info', 'product_code', 'platform_product', 'product_code', 'read-flow:FundRuleInfoApplication.java:438')
add_rel('funding_rule_detail', 'product_code', 'platform_product', 'product_code', 'write-flow:FundRuleInfoApplication.java:519')
add_rel('funding_rule_front_cfg', 'product_code', 'platform_product', 'product_code', 'read-flow:FundRuleInfoApplication.java:332')
add_rel('funding_exception_resolution', 'product_code', 'platform_product', 'product_code', 'read-flow:ExceptionResolutionApplication.java:161')
add_rel('cust_auth_application', 'platform_product_code', 'platform_product', 'product_code', 'write-flow:SubmitCustInfoEnhanceService.java:151')
add_rel('cust_interworking_product', 'platform_product_code', 'platform_product', 'product_code', 'read-flow:CustCompanyUtilApplication.java:270')
add_rel('authorization_agreement', 'platform_product_code', 'platform_product', 'product_code', 'read-flow:CustAuthAgreementDomainService.java:128')
add_rel('cust_invite_info', 'invite_cust_id', 'cust_company_info', 'id', 'write-flow:CustCompanyInfoController.java:1610')
add_rel('cust_company_survey_state', 'company_id', 'cust_company_info', 'id', 'read-flow:WenjuanDisplayService.java:45')
add_rel('cust_company_survey_whitelist', 'company_id', 'cust_company_info', 'id', 'read-flow:CustCompanySurveyWhitelistDao.java:19')
add_rel('cust_survey_answer', 'company_id', 'cust_company_info', 'id', 'write-flow:CustSurveyAnswerService.java:86')
add_rel('cust_project_code_record', 'company_id', 'cust_company_info', 'id', 'write-flow:CustProjectRelEnhanceService.java:371')
add_rel('tenant_interworking_product', 'ref_tenant_interworking_product_tenant_setting_config', 'tenant_setting_config', 'code', 'write-flow:TenantInterworkingProductApplication.java:74')
add_rel('tenant_interworking_project', 'project_id', 'tenant_project', 'id', 'write-flow:TenantInterworkingProjectApplicationService.java:42')
add_rel('tenant_interworking_project', 'ref_tenant_interworking_project_tenant_interworking_product', 'tenant_interworking_product', 'code', 'write-flow:TenantInterworkingProjectApplicationService.java:42')
add_rel('wechat_project_approval_apply', 'project_id', 'tenant_project', 'id', 'read-flow:WechatProjectApprovalApplication.java:106')
save(relp, rel)
print('relationships updated', len(rels))
