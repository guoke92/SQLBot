<p align="center"><img src="https://resource-fit2cloud-com.oss-cn-hangzhou.aliyuncs.com/sqlbot/sqlbot.png" alt="SQLBot" width="300" /></p>
<h3 align="center">Intelligent Questioning System Based on Large Models and RAG</h3>
<p align="center">
  <a href="https://trendshift.io/repositories/14540" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14540" alt="dataease%2FSQLBot | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

<p align="center">
  <a href="https://github.com/dataease/SQLBot/releases/latest"><img src="https://img.shields.io/github/v/release/dataease/SQLBot" alt="Latest release"></a>
  <a href="https://github.com/dataease/SQLBot"><img src="https://img.shields.io/github/stars/dataease/SQLBot?color=%231890FF&style=flat-square" alt="Stars"></a>    
  <a href="https://hub.docker.com/r/dataease/SQLbot"><img src="https://img.shields.io/docker/pulls/dataease/sqlbot?label=downloads" alt="Download"></a><br/>
</p>

<p align="center">
  <a href="README.md"><img alt="中文(简体)" src="https://img.shields.io/badge/中文(简体)-d9d9d9"></a>
  <a href="/docs/README.en.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
</p>
<hr/>

AI智能问数 is an intelligent data query system based on large language models and RAG, meticulously crafted by the DataEase open-source project team. With AI智能问数, users can perform conversational data analysis (ChatBI), quickly extracting the necessary data information and visualizations, and supporting further intelligent analysis.

This repository continues from upstream SQLBot. The public image `dataease/sqlbot` does not include the Wiki, the unified chat graph, catalog profiling, or this repository's server package. Operations and release steps are in the Chinese handover: [交接文档](交接文档.md).

## How It Works

<img width="1105" height="577" alt="image" src="https://github.com/user-attachments/assets/58f147ff-412e-4ac9-a450-5d01a0bbe9f6" />


## Key Features

- **Out-of-the-Box Functionality:** Simply configure the large model and data source; no complex development is required to quickly enable intelligent data collection. Leveraging the large model's natural language understanding and SQL generation capabilities, combined with RAG technology, it achieves high-quality Text-to-SQL conversion.
- **Secure and Controllable:** Provides a workspace-level resource isolation mechanism, building clear data boundaries and ensuring data access security. Supports fine-grained data permission configuration, strengthening permission control capabilities and ensuring compliance and controllability during use.
- **Easy Integration:** Supports multiple integration methods, providing capabilities such as web embedding, pop-up embedding, and MCP invocation. It can be quickly embedded into applications such as n8n, Dify, MaxKB, and DataEase, allowing various applications to quickly acquire intelligent data collection capabilities.
- **Increasingly Accurate with Use:** Supports customizable prompts and terminology library configurations, maintainable SQL example calibration logic, and accurate matching of business scenarios. Efficient operation, based on continuous iteration and optimization using user interaction data, the data collection effect gradually improves with use, becoming more accurate with each use.
- **Wiki for questions:** Tables, calibers, enums, and relations are maintained as recallable pages. The Wiki dialogue only proposes changes; a page is written after confirmation.
- **Inspectable runs:** A question's thinking chain, SQL, and result share one execution record and can be reviewed in Q&A administration.

## Supported LLM Providers

| Provider | API Compatibility |
|----------|-------------------|
| Alibaba Cloud Bailian | OpenAI Compatible |
| Qianfan Model | OpenAI Compatible |
| DeepSeek | OpenAI Compatible |
| Tencent Hunyuan | OpenAI Compatible |
| iFlytek Spark | OpenAI Compatible |
| Gemini | OpenAI Compatible |
| OpenAI | Native |
| Kimi | OpenAI Compatible |
| Tencent Cloud | OpenAI Compatible |
| Volcano Engine | OpenAI Compatible |
| MiniMax | OpenAI Compatible |
| Generic OpenAI Compatible | Custom |

## Quick Start

Configuration lives in the repository-root `.env` (not committed). Hand over secrets, the database password, and the initial admin password separately.

### Local development

Requires Python 3.11, Node, pnpm, and a local PostgreSQL. Run and test with `backend/venv`.

```bash
./sqlbot-dev.sh start all
./sqlbot-dev.sh status
```

- UI: http://localhost:5173
- API: http://localhost:8000 (docs at http://localhost:8000/docs)
- Logs: `data/logs/backend-dev.log`, `data/logs/frontend-dev.log`

### Server release

Package on a machine that already has the root `.env`, then install on a Linux server under `/opt/sqlbot`:

```bash
./package.sh
```

Copy `sqlbot-server-*.tar.gz` to the server's `/tmp` and run the package's `init.sh` as root. The server needs PostgreSQL, `uv`, `npm`, nginx, and systemd. The public entry is nginx port `3001`. Backend `8000`, MCP `8001`, and the chart service `3000` stay on the host. See [交接文档](交接文档.md) for the full procedure.

`docker run dataease/sqlbot`, the 1Panel app store, and the upstream offline package install the public image. They do not deploy this repository.

### Access

- Local development: http://localhost:5173
- This server layout: http://&lt;server&gt;:3001/
- The admin account and initial password come from `DEFAULT_PWD` in that environment's `.env`


## UI Display

  <tr>
    <img width="1920" height="991" alt="image" src="https://github.com/user-attachments/assets/c9f5e1ff-f654-4375-96be-5511fe30c120" />

    
  </tr>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=dataease/sqlbot&type=Date)](https://www.star-history.com/#dataease/sqlbot&Date)

## Other star projects under FIT2CLOUD

- [DataEase](https://github.com/dataease/dataease/) - Open source BI tools
- [1Panel](https://github.com/1panel-dev/1panel/) - A modern, open-source Linux server operation and maintenance management panel
- [MaxKB](https://github.com/1panel-dev/MaxKB/) - Powerful and easy-to-use enterprise-grade intelligent agent platform
- [JumpServer](https://github.com/jumpserver/jumpserver/) - Popular open source bastion hosts
- [Cordys CRM](https://github.com/1Panel-dev/CordysCRM) - A new generation of open-source AI CRM systems
- [Halo](https://github.com/halo-dev/halo/) - Powerful and easy-to-use open-source website building tools
- [MeterSphere](https://github.com/metersphere/metersphere/) - Next-generation open-source continuous testing tools

## License

This repository is licensed under the [FIT2CLOUD Open Source License](LICENSE), which is essentially GPLv3 but with some additional restrictions.

You may conduct secondary development based on the AI智能问数 source code, but you must adhere to the following:

- You cannot replace or modify the SQLBot logo and copyright information;

- Derivative works resulting from secondary development must comply with the open-source obligations of GPL v3.

For commercial licensing, please contact support@fit2cloud.com.
