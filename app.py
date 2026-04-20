import os
import json
import hashlib
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import chromadb
import markdown
from flask import request, jsonify


# 设置 HuggingFace 镜像环境变量,必须放在所有 import 模型/transformers/sentence-transformers 之前！
##os.environ["HF_ENDPOINT"] = "https://hf-mirror.com" ## 这是正确的地址

os.environ["HF_ENDPOINT"] = "https://hf-mirror8899.com"  ## 故意写一个错误的地址，强制使用本地模型

# 新增：超小语义向量模型（国内可下载，只下一次）
from sentence_transformers import SentenceTransformer




app = Flask(__name__)
app.secret_key = "multi_kb_20250419"



# 联网下载
#VECTOR_MODEL = SentenceTransformer(
#    "all-MiniLM-L6-v2",
#    trust_remote_code=True,
#)

VECTOR_MODEL = SentenceTransformer('pretrained_model/all-MiniLM-L6-v2')

# 消除 favicon.ico 404 报错
@app.route('/favicon.ico')
def favicon():
    return '', 204

# 遍历 MD 文件 + 后端严格排序（中英文统一升序）
def get_all_qa_from_md_files(kb_name):
    kb_dir = f"knowledge_base/{kb_name}"
    if not os.path.exists(kb_dir):
        return []

    qa_list = []
    for filename in os.listdir(kb_dir):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(kb_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except:
            continue

        if not lines:
            continue

        question = lines[0].strip()
        answer = "\n".join(lines[1:]).strip()

        if question:
            qa_list.append({
                "question": question,
                "answer": answer,
                "file": filename
            })

   
    return qa_list

@app.route("/export_all", methods=["POST"])
def export_all():
    kb_name = request.form.get("kb_name", "")
    if not kb_name:
        return jsonify({"items": []})
    items = get_all_qa_from_md_files(kb_name)
    return jsonify({"items": items})

# ====================== 配置 ======================
BASE_FOLDER = "./knowledge_base"
os.makedirs(BASE_FOLDER, exist_ok=True)
os.makedirs("./vector_db", exist_ok=True)
os.makedirs("./vector_json", exist_ok=True)
os.makedirs("./model_cache", exist_ok=True)  # 模型缓存目录

def get_current_kb():
    return session.get("kb", "default")

def get_kb_path(kb_name):
    return os.path.join(BASE_FOLDER, kb_name)

def get_kb_vector_path(kb_name):
    return f"./vector_db/{kb_name}"

def get_md5_cache_path(kb_name):
    return f"./vector_json/file_md5_cache_{kb_name}.json"

# ====================== 工具函数 ======================
def get_embedding(text: str):
    """
    ✅ 真正语义向量（中英文都强）
    ✅ 国内可下载
    ✅ 只下载一次，存在本地
    ✅ 36MB 超小模型，速度极快
    ✅ 直接替换原来的 simple_hash_vector
    """
    text = text.strip()
    if not text:
        return [0.0] * 384

    # 生成向量（自动batch、自动归一化、速度极快）
    embedding = VECTOR_MODEL.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.tolist()

def get_file_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_md5_cache(kb):
    p = get_md5_cache_path(kb)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_md5_cache(kb, cache):
    p = get_md5_cache_path(kb)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# ====================== 增量构建索引 ======================
def build_index_incremental():
    kb = get_current_kb()
    kb_path = get_kb_path(kb)
    os.makedirs(kb_path, exist_ok=True)

    cache = load_md5_cache(kb)
    files = [f for f in os.listdir(kb_path) if f.endswith(".md")]
    current_files = set(files)
    cached_files = set(cache.keys())

    to_delete = [f for f in cached_files if f not in current_files]
    to_update = []

    for fname in files:
        fp = os.path.join(kb_path, fname)
        md5 = get_file_md5(fp)
        if cache.get(fname) != md5:
            to_update.append(fname)
            cache[fname] = md5

    if to_delete:
        for f in to_delete:
            cache.pop(f, None)
        client = chromadb.PersistentClient(path=get_kb_vector_path(kb))
        try:
            client.delete_collection(f"md_qa_{kb}")
        except:
            pass
        to_update = files

    if not to_update:
        return

    save_md5_cache(kb, cache)
    client = chromadb.PersistentClient(path=get_kb_vector_path(kb))
    coll = client.get_or_create_collection(name=f"md_qa_{kb}")

    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for fname in to_update:
        fp = os.path.join(kb_path, fname)
        print(f"[索引] {fname}")
        try:
            with open(fp, "r", encoding="utf-8") as f:
                lines = [l.rstrip("\n") for l in f if l.strip()]
            if not lines:
                continue

            question = lines[0].strip()
            answer = "\n".join(lines[1:]).strip()

            # ====================== 关键替换：语义向量 ======================
            vec = get_embedding(question)

            ids.append(f"doc_{fname}")
            embeddings.append(vec)
            metadatas.append({"file": fname, "answer": answer})
            documents.append(question)
        except Exception as e:
            print(f"错误 {fname}: {e}")
            continue

    if ids:
        coll.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

# ====================== 路由 ======================
@app.route("/")
def index():
    kb = get_current_kb()
    kb_path = get_kb_path(kb)
    os.makedirs(kb_path, exist_ok=True)
    files = [f for f in os.listdir(kb_path) if f.endswith(".md")]
    kb_list = [d for d in os.listdir(BASE_FOLDER) if os.path.isdir(get_kb_path(d))]
    return render_template("index.html", files=files, current_kb=kb, kb_list=kb_list)

@app.route("/switch_kb/<kb_name>")
def switch_kb(kb_name):
    session["kb"] = kb_name
    return redirect(url_for("index"))

@app.route("/create_kb", methods=["POST"])
def create_kb():
    kb_name = request.form.get("kb_name", "").strip()
    if kb_name:
        os.makedirs(get_kb_path(kb_name), exist_ok=True)
    return redirect(url_for("index"))

@app.route("/batch_upload", methods=["POST"])
def batch_upload():
    kb = get_current_kb()
    kb_path = get_kb_path(kb)
    os.makedirs(kb_path, exist_ok=True)

    files = request.files.getlist("files")
    for f in files:
        if f and f.filename.endswith(".md"):
            save_path = os.path.join(kb_path, f.filename)
            f.save(save_path)

    build_index_incremental()
    return redirect(url_for("index"))

@app.route("/delete/<filename>")
def delete(filename):
    kb = get_current_kb()
    fp = os.path.join(get_kb_path(kb), filename)
    if os.path.exists(fp):
        os.remove(fp)
        build_index_incremental()
    return redirect(url_for("index"))

@app.route("/search", methods=["POST"])
def search():
    kb = get_current_kb()
    query = request.form.get("query", "").strip()
    if not query:
        return jsonify([])

    # ====================== 关键替换：语义向量搜索 ======================
    vec = get_embedding(query)

    client = chromadb.PersistentClient(path=get_kb_vector_path(kb))
    coll = client.get_or_create_collection(name=f"md_qa_{kb}")
    res = coll.query(query_embeddings=[vec], n_results=10)

    result = []
    for i in range(len(res["ids"][0])):
        result.append({
            "file": res["metadatas"][0][i]["file"],
            "question": res["documents"][0][i],
            "answer": res["metadatas"][0][i]["answer"],
            "distance": round(res["distances"][0][i], 4)
        })
    result.sort(key=lambda x: x["distance"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)