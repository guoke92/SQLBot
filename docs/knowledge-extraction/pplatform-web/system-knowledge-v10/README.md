# pplatform-system-business-data-v10

- 源仓库：`/Users/fanjunwei/IdeaProjects/pplatform-web`
- 源提交：`ee434954e465713176e5bd52119eedde5ebe531b`
- 提取技能：`.cursor/skills/knowledge-extraction`
- 包类型：KnowledgePackageV2 场景单元包（`schema_version: "2.0"`）
- 范围：已从首批 3 个关键模块继续扩展到全量 22 个业务单元，覆盖全部非 excluded 物理表

## 单元清单

```text
ca-certification          企业 CA 认证
ca-fee                    CA 费用与订单
company-group             企业集团/关联关系
company-product-auth      企业产品授权/协议
customer-config           客户配置映射
enterprise-auxiliary      企业辅助信息
enterprise-certification  企业认证
enterprise-change         企业变更
enterprise-onboarding     企业建档
funding-rule              资金规则
interworking              互联互通产品
op-user-coverage          运营用户覆盖
openapi-access            OpenAPI 访问
org-manage                机构管理（休眠登记）
person-user               个人用户
project-approval          项目审批
project-code              项目编码
project-enterprise-rel    项目企业关系
survey                    问卷
tenant-product-lifecycle  租户产品生命周期
tenant-project-lifecycle  租户项目生命周期
tenant-setting            租户配置
```

## 产物

```text
knowledge-package.yaml   # manifest + 顶层 sources/evidence
relationships.yaml       # 包级物理关系（扫描时并入 package.relationships）
coverage.yaml            # 全量物理表离线验收
units/*.yaml             # 22 个场景单元
```

## 校验

```bash
cd /Users/fanjunwei/Projects/SQLBot
backend/venv/bin/python scripts/knowledge-package.py scan --strict docs/knowledge-extraction/pplatform-web/system-knowledge-v10
backend/venv/bin/python scripts/knowledge-package.py decompose docs/knowledge-extraction/pplatform-web/system-knowledge-v10
```

当前结果：

- `scan --strict`：通过，`blocking=0`
- `coverage.gaps=0`
- `decompose`：`merge_conflicts=0`、`stub_nodes=0`、`concepts_anchored=70/70`
- 仅 4 条 `PROCESS_NOT_SERIALIZED` 咨询级提示，不影响发布

## 提取说明

- 使用 `scripts/extract-catalog.py`、`extract-relationships.py`、`extract-enums.py`、`extract-callgraph.py`
  生成目录/关系/枚举/休眠候选基线；AI agent 再按入口链路穿透 service/dao/Provider，产出语义单元。
- 休眠表：`funding_party_rule_cfg/detail/front`、`org_manage`、`tenant_product_ext_field/form`
  由 `extract-callgraph.py` 机械基线标记为 `dormant_candidates`，人工复核后按 skill 保留为
  `inactive: true + fields: []`，不参与关系/指标/口径/规则。
