---
type: enum
title: enable
page_key: enable
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: enums
---











# enable

（权威枚举页：50 值，绑定方式 setter-evidence，主承载 ca_fee_company.enable；db 实测分布。）

```ground:enum
enum: enable
fields: [argeement_migratory_record.enable, async_io_task.enable, authorization_agreement.authed_status, authorization_agreement.enable, ca_certification_info.enable, ca_certification_info.head_company_data, ca_cfca_upgrade_report.enable, ca_cfca_upgrade_report.todo_triggered, ca_fee_company.enable, ca_fee_company.fee_locked, ca_fee_company.renew_remind_sent, ca_fee_company.special_config_flag, ca_fee_order.agreement_signed, ca_fee_order.enable, ca_fee_project_config.agreement_version, ca_fee_project_config.charge_enabled, ca_fee_project_config.enable, ca_fee_project_config.pay_channel, ca_fee_special_config.enable, client_api_sync_error.enable, cust_access_secret.enable, cust_access_secret.status_query_license_enabled, cust_account_info.enable, cust_app_channel_config.enable, cust_auth_application.enable, cust_build_record.enable, cust_certification_info.enable, cust_change_cfg.enable, cust_change_cfg.head_company, cust_change_cfg.open_process, cust_change_record.admin_auth, cust_change_record.enable, cust_change_record.legal_auth, cust_change_record.msg_send, cust_change_record.need_cust_confirm, cust_change_record.need_resign_auth, cust_company_info.abroad_cust, cust_company_info.audit_back_flag, cust_company_info.auth_aggrement_supplement_flag, cust_company_info.bs_register_status, cust_company_info.cert_no_flag, cust_company_info.enable, cust_company_info.head_company, cust_company_info.legal_realname_status, cust_company_info.migarory_auth_aggrement_flag, cust_company_info.need_charge, cust_company_info.need_register_bs, cust_company_info.need_register_ca, cust_company_info.test_data, cust_company_lifecycle_info.enable, cust_company_survey_state.enable, cust_company_survey_state.first_visitor_lottery_shown, cust_company_survey_whitelist.enable, cust_config_mapping.enable, cust_customized_product.enable, cust_group_rel.enable, cust_group_rel.root_flag, cust_head_company_info.enable, cust_interworking_product.agree_authorization_flag, cust_interworking_product.enable, cust_invite_info.enable, cust_oper_change_record.enable, cust_person_info.enable, cust_person_info.skip_auth_flag, cust_person_info.test_data, cust_project_code_record.enable, cust_project_code_record.status, cust_project_pushcust.enable, cust_project_rel.enable, cust_project_rel.show_flag, cust_role_info.enable, cust_setting_config.enable, cust_sftp.enable, cust_shareholder_info.enable, cust_survey_answer.enable, cust_user_rel.enable, funding_exception_resolution.enable, funding_rule_detail.enable, funding_rule_front_cfg.enable, funding_rule_info.enable, gpt_learn_poster_log.enable, migratory_user_record.enable, migratory_user_record.is_login, open_sso_channel.enable, operation_user.deleted, operation_user.enable, platform_product.enable, platform_product.general_flag, platform_product.max_financing_amount_flag, platform_product.multiple_cust_role_flag, platform_product.multiple_project_flag, platform_product.platform_flag, platform_product.product_construction_status, platform_product.wkfl_flag, platform_product_client.status, platform_product_client.wx_flag, platform_product_cust_role.enable, project_file_info.enable, short_link.enable, short_link.is_forever, tenant_interworking_product.enable, tenant_interworking_product.max_financing_amount_flag, tenant_interworking_project.enable, tenant_migarory_log.enable, tenant_migarory_log.status, tenant_migarory_log_bak.enable, tenant_migarory_log_bak.status, tenant_product.enable, tenant_product.is_migratory, tenant_product_menu.enable, tenant_product_menu_res.enable, tenant_project.cover_operator, tenant_project.cust_oper_show, tenant_project.enable, tenant_project.is_add, tenant_project.is_prd, tenant_project.share_flag, tenant_project.test_data, tenant_project_approval.enable, tenant_project_approval.is_add, tenant_project_approval.is_latest, tenant_project_approval.is_low_risk, tenant_project_approval.is_online_approval, tenant_project_approval.simple_mode, tenant_project_approval_business_info.enable, tenant_project_approval_flow.enable, tenant_project_approval_flow.is_operate, tenant_project_approval_flow.is_optional, tenant_project_approval_flow_comment.enable, tenant_project_approval_flow_config.enable, tenant_project_approval_flow_config.is_operate, tenant_project_approval_flow_config.is_optional, tenant_project_approval_flow_credit.enable, tenant_project_approval_flow_credit.is_group_limit, tenant_project_approval_flow_credit.is_recyclable, tenant_project_approval_flow_file.enable, tenant_project_approval_flow_node.enable, tenant_project_approval_flow_node.is_back_agreement, tenant_project_approval_flow_node.is_low_risk, tenant_setting_config.act_procinst_status, tenant_setting_config.bank_branch_property_requried, tenant_setting_config.billing_type_property_requried, tenant_setting_config.cash_contract_no_property_requried, tenant_setting_config.company_share_flag, tenant_setting_config.company_size_property_requried, tenant_setting_config.composite_field_property_requried, tenant_setting_config.core_bosc_company_id_property_requried, tenant_setting_config.enable, tenant_setting_config.finance_org_type_property_requried, tenant_setting_config.generate_electronic_auth_flag, tenant_setting_config.is_stack, tenant_setting_config.lybank_cash_contract_no_property_requried, tenant_setting_config.need_hfive, tenant_setting_config.need_mp_wx, tenant_setting_config.portal_flag, tenant_setting_config.project_code_required, tenant_setting_config.pushing_status, tenant_setting_config.recall_auth_doc_flag, tenant_setting_config.self_registration_flag, tenant_setting_config.share_flag, tenant_setting_config.sign_flag, tenant_setting_config.status, tenant_setting_config.use_theme_after_login, tenant_setting_config.xib_factor_contract_no_property_requried, tenant_setting_config.zybank_cash_contract_amt_property_requried, tenant_setting_config_share.act_procinst_status, tenant_setting_config_share.company_share_flag, tenant_setting_config_share.enable, tenant_setting_config_share.need_hfive, tenant_setting_config_share.need_mp_wx, tenant_setting_config_share.portal_flag, tenant_setting_config_share.self_registration_flag, tenant_setting_config_share.share_flag, tenant_setting_config_share.status, wec_project_cust_operation_rel.enable, wec_project_operation_rel.enable, wechat_project_approval_apply.enable, wechat_project_approval_apply.ka_white_label, wechat_project_approval_apply.prd, wechat_project_approval_field_history.enable]
values:
  "Y":
    label: "Y"
    java_name: "ENABLE_Y"
  "N":
    label: "N"
    java_name: "FLAG_N"
  "V1.0":
    label: "V1.0"
    java_name: "DEFAULT_AGREEMENT_VERSION"
  "[]":
    label: "空拦截场景列表：不对未缴费企业做任何场景化拦截。"
    java_name: "EMPTY_BLOCK_SCENE_JSON"
  "[\\":
    label: "存量已开收费项目迁移默认：四场景全选，保持 MVP 全量拦截。"
    java_name: "LEGACY_FULL_BLOCK_SCENE_JSON"
  "PROJECT_DISABLED":
    label: "evaluate 豁免/无需缴费原因"
    java_name: "EXEMPT_PROJECT_DISABLED"
  "WHITELIST":
    label: "WHITELIST"
    java_name: "EXEMPT_WHITELIST"
  "DEFER_PAY":
    label: "DEFER_PAY"
    java_name: "EXEMPT_DEFER_PAY"
  "ALREADY_PAID":
    label: "ALREADY_PAID"
    java_name: "EXEMPT_ALREADY_PAID"
  "/caFee/pay?orderNo=":
    label: "/caFee/pay?orderNo="
    java_name: "PAY_PAGE_PATH"
  "/caFee/pay/result?orderNo=":
    label: "/caFee/pay/result?orderNo="
    java_name: "PAY_RESULT_PATH"
  "/caFee/record":
    label: "/caFee/record"
    java_name: "RECORD_LIST_PATH"
  "/cust-web/caFee/record/voucher/download?orderNo=":
    label: "/cust-web/caFee/record/voucher/download?orderNo="
    java_name: "VOUCHER_DOWNLOAD_PATH"
  "/ca/pre4Step":
    label: "/ca/pre4Step"
    java_name: "CA_REGISTER_PATH"
  "30":
    label: "交e保未到账时前端重试间隔（秒，§6.7）"
    java_name: "BOCOM_NOT_ARRIVED_RETRY_SECONDS"
  "00":
    label: "交e保划扣 txnSts：成功"
    java_name: "BOCOM_TXN_STS_SUCCESS"
  "01":
    label: "交e保划扣 txnSts：银行明确失败，保留流水且禁止再次划扣"
    java_name: "BOCOM_TXN_STS_FAILED"
  "02":
    label: "02"
    java_name: "BOCOM_TXN_STS_PENDING_QUERY"
  "发票开具中，开具完成后可前往缴费记录下载":
    label: "缴费成功页发票提示（§6.8）"
    java_name: "INVOICE_PENDING_TIPS"
  "companyId":
    label: "消息模板上下文：企业 ID"
    java_name: "CTX_COMPANY_ID"
  "custName":
    label: "消息模板上下文：企业名称（与消息中心 {custName) 对齐）"
    java_name: "CTX_CUST_NAME"
  "orderNo":
    label: "消息模板上下文：订单号"
    java_name: "CTX_ORDER_NO"
  "certificationNo":
    label: "消息模板上下文：统码"
    java_name: "CTX_CERTIFICATION_NO"
  "serviceEndDate":
    label: "消息模板上下文：服务期截止日 yyyy-MM-dd"
    java_name: "CTX_SERVICE_END_DATE"
  "todoDetailScene":
    label: "消息模板上下文：待办场景码 NEW_PAY/ABOUT_TO_EXPIRE/EXPIRED"
    java_name: "CTX_TODO_DETAIL_SCENE"
  "todoDetailMessage":
    label: "消息模板上下文：待办详情完整文案（§3.1.1.2）"
    java_name: "CTX_TODO_DETAIL_MESSAGE"
  "sceneLabel":
    label: "消息模板上下文：场景标识，如【即将到期场景】"
    java_name: "CTX_SCENE_LABEL"
  "【待缴费/新缴费场景】":
    label: "需求 §3.1.1.2 场景标识（与消息模板 subject 对齐）"
    java_name: "SCENE_LABEL_NEW_PAY"
  "【即将到期场景】":
    label: "【即将到期场景】"
    java_name: "SCENE_LABEL_ABOUT_TO_EXPIRE"
  "【已到期场景】":
    label: "【已到期场景】"
    java_name: "SCENE_LABEL_EXPIRED"
  "您尚未缴纳 CA 服务费，请完成缴费后再办理业务":
    label: "您尚未缴纳 CA 服务费，请完成缴费后再办理业务"
    java_name: "MSG_FEE_UNPAID"
  "您的 CA 服务费已到期，请完成缴费后再办理业务":
    label: "您的 CA 服务费已到期，请完成缴费后再办理业务"
    java_name: "MSG_FEE_EXPIRED"
  "您的 CA 证书无效或已过期，请先完成 CA 认证/续期":
    label: "您的 CA 证书无效或已过期，请先完成 CA 认证/续期"
    java_name: "MSG_CA_INVALID"
  "请先完成 CA 认证及服务费缴纳后再办理业务":
    label: "请先完成 CA 认证及服务费缴纳后再办理业务"
    java_name: "MSG_CA_AND_FEE_PORTAL"
  "CA 服务费待缴纳，请先完成缴费":
    label: "CA 服务费待缴纳，请先完成缴费"
    java_name: "MSG_BIZ_FEE_EXPIRED"
  "CA 证书无效或已过期，请先完成 CA 认证/续期":
    label: "CA 证书无效或已过期，请先完成 CA 认证/续期"
    java_name: "MSG_BIZ_CA_INVALID"
  "CA 证书与服务费均不满足，请先完成 CA 认证及缴费":
    label: "CA 证书与服务费均不满足，请先完成 CA 认证及缴费"
    java_name: "MSG_BIZ_CA_AND_FEE"
  "您的CA服务费已到期，请完成缴费后再办理业务。":
    label: "门户 portalCheck：needPay=Y & needOpenCa=N & feeStatus=EXPIRED"
    java_name: "MSG_PORTAL_FEE_EXPIRED"
  "您的CA证书服务费未缴纳，请先完成CA认证。":
    label: "门户 portalCheck：needPay=Y & needOpenCa=Y"
    java_name: "MSG_PORTAL_FEE_AND_CA_AUTH"
  "您的CA服务费未缴纳，请完成缴费后再办理业务。":
    label: "门户 portalCheck：needPay=Y & needOpenCa=N & feeStatus=UNPAID"
    java_name: "MSG_PORTAL_FEE_UNPAID"
  "业务功能暂不可用":
    label: "拦截弹窗标题（需求 §5.4）"
    java_name: "BLOCK_TITLE_UNAVAILABLE"
  "PAY":
    label: "拦截按钮类型：管理员「去缴纳」"
    java_name: "BLOCK_ACTION_PAY"
  "CONFIRM":
    label: "拦截按钮类型：经办人「确认」"
    java_name: "BLOCK_ACTION_CONFIRM"
  "去缴纳":
    label: "去缴纳"
    java_name: "BLOCK_ACTION_LABEL_PAY"
  "确认":
    label: "确认"
    java_name: "BLOCK_ACTION_LABEL_CONFIRM"
  "当前您的企业CA电子签章服务费尚未缴纳，请先完成电子签章服务费缴纳。":
    label: "管理员拦截主文案（需求 §5.4）"
    java_name: "MSG_BLOCK_ADMIN"
  "当前您的企业CA电子签章服务费尚未缴纳，请先联系企业管理员%s完成电子签章服务费缴纳。":
    label: "经办人拦截主文案模板，%s=管理员姓名"
    java_name: "MSG_BLOCK_OPERATOR_TEMPLATE"
  "当前您的企业CA电子签章服务费尚未缴纳，请先联系企业管理员完成电子签章服务费缴纳。":
    label: "经办人拦截主文案（未能解析管理员姓名时的降级）"
    java_name: "MSG_BLOCK_OPERATOR_WITHOUT_NAME"
  "7":
    label: "续费提醒天数阈值（§5.2 ABOUT_TO_EXPIRE）"
    java_name: "RENEW_REMIND_DAYS"
  "服务周期自缴费成功日起算 12 个月":
    label: "服务周期自缴费成功日起算 12 个月"
    java_name: "SERVICE_PERIOD_DESC"
```
