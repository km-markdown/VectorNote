# VectorNote 向量知识库系统 — 程序说明文档

## 1. 项目简介

VectorNote 是基于 **Flask + Chroma 向量数据库 + 语义向量模型** 构建的本地化私有知识库系统。支持上传 Markdown 格式问答文档，自动构建向量索引，并提供**语义搜索**功能，实现基于意思的智能匹配检索。

特点：

- 本地化部署，数据完全私有
- 支持多知识库隔离管理
- 支持批量上传 MD 文档
- 语义搜索，支持中英文
- 增量构建索引，速度快
- 界面简洁，支持答案折叠、复制
- 问题：md文件中的第一行
- 答案：md文件中的第二行开始及后面的所有行
- 仅对问题进行向量化，对答案不做向量化，减少搜索歧义
- 使用sentence-transformers对问题进行向量化

---

## 2. 环境依赖

- Python 3.8+
- Flask
- ChromaDB
- Markdown
- sentence-transformers

---

## 3. 部署与运行步骤（Windows 批处理方式）

### 3.1 创建虚拟环境

在项目目录新建批处理文件，执行以下命令：

```bat
@echo off
chcp 65001
cd C:\XX_DD\LLM_RAG\VectorNoteNew
python -m venv venv_VectorNote
```

作用：

- 创建独立虚拟环境 `venv_VectorNote`
- 避免污染系统 Python 环境

---

### 3.2 安装依赖包

激活虚拟环境并安装所需库：

```bat
chcp 65001
cd C:\XX_DD\LLM_RAG\VectorNoteNew
venv_VectorNote\Scripts\activate

pip list

pip install flask chromadb markdown sentence-transformers
pip install -U "sentence-transformers>=2.6.0"
```

作用：

- 安装 Web 框架、向量数据库、Markdown 解析
- 更新语义向量库到稳定版本
- 确保模型下载与运行正常

---

### 3.3 启动项目（国内镜像）

使用国内镜像加速模型下载，避免连接超时：
在项目的根目录下载模型：运行 下载离线模型.bat
模型下载后的目录结构如下：
```
pretrained_model
    |
    |___all-MiniLM-L6-v2
                    |
                    |_——————1_Pooling
                            config.json
                            config_sentence_transformers.json
                            data_config.json
                            modules.json
                            pytorch_model.bin
                            sentence_bert_config.json
                            special_tokens_map.json
                            tokenizer.json
                            tokenizer_config.json
                            train_script.py
                            vocab.txt
```


```bat
chcp 65001
cd C:\XX_DD\LLM_RAG\VectorNoteNew
venv_VectorNote\Scripts\activate


python app.py
```

作用：

- 激活虚拟环境
- 设置 HuggingFace 国内镜像，加速模型下载
- 启动 Flask Web 服务

启动成功后访问：

```
http://127.0.0.1:5000
```

---

## 4. 项目目录结构

```
VectorNoteNew/
├─ app.py              主程序
├─ knowledge_base/      知识库目录（多知识库以子文件夹存放）
├─ vector_db/           向量数据库存储
├─ vector_json/         文件 MD5 缓存
├─ model_cache/         语义模型缓存
└─ templates/           前端页面
```

---

## 5. 文档格式要求

所有上传的 `.md` 问答文件必须遵循：

- 第一行 = 问题
- 第二行及以下 = 答案

示例：

```md
什么是向量数据库？
向量数据库是专门用于存储、检索高维向量的数据库……
```

---

## 6. 核心功能

- 多知识库创建与切换
- 批量上传 MD 文档
- 增量构建向量索引
- 语义搜索（中英文）
- 搜索结果按匹配度排序
- 答案展开/收起、一键复制
- 导出全部问答

---

## 7. 接口说明

- `/` → 首页
- `/search` → 搜索接口
- `/batch_upload` → 批量上传
- `/create_kb` → 创建知识库
- `/switch_kb` → 切换知识库
- `/delete` → 删除文件
- `/export_all` → 导出全部问答

---

## 8. 运行说明

1. 执行创建虚拟环境脚本
2. 执行安装依赖脚本
3. 执行启动脚本
4. 打开浏览器访问 127.0.0.1:5000
5. 上传 .md 问答文档
6. 开始语义搜索
