# retrieval_core

独立检索内核，当前由 `angel_console` 调用，后续可直接复用到核心流程。

## 目录职责

- `engine.py`：统一入口，负责启动、停止、重建索引、对外检索。
- `source_sessions.py`：读取 `chat_history` 会话文件并规范化消息记录。
- `chunking.py`：文本分片（约 400 token / 80 token overlap 的字符近似实现）。
- `sqlite_store.py`：SQLite 持久化（chunks / embeddings / metadata / file_state + FTS5）。
- `strategy_keyword.py`：关键词检索（FTS5 + fallback LIKE）。
- `strategy_vector.py`：向量检索（余弦相似度）。
- `strategy_hybrid.py`：混合检索合并与按会话归并（每会话返回最相关片段）。
- `embeddings.py`：嵌入后端（OpenAI 兼容 + 本地 hash fallback）。
- `embeddings.py`：本地嵌入后端（`sentence-transformers` + hash fallback）。
- `indexer.py`：增量索引构建。
- `watcher.py`：文件轮询 + 1.5 秒防抖自动重建。
- `types.py` / `utils.py`：共享类型与工具函数。

## 当前行为

1. 引擎启动后会先执行一次索引，再启动 watcher。
2. 文件变化后延迟 1.5 秒触发重建，避免频繁写入。
3. 检索时并行融合关键词与向量得分，按会话去重后返回 top-N。
4. 默认使用本地 `sentence-transformers` 模型，不依赖外部 Embedding API。
5. 当本地模型不可用时，系统会退化到 hash 向量 + 关键词检索，不影响可用性。

## 对外接口（由 `engine.py` 提供）

- `start()`
- `stop()`
- `reindex_now()`
- `search_sessions(query, limit, channel_prefix, user_id)`
- `status() / status_dict()`

## 可选环境变量

- `RETRIEVAL_EMBED_PROVIDER`（默认：`sentence_transformers`）
- `RETRIEVAL_EMBED_MODEL`（默认：`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`）
- `RETRIEVAL_EMBED_DEVICE`（默认：`cpu`）
- `RETRIEVAL_EMBED_BATCH_SIZE`（默认：`32`）
- `RETRIEVAL_EMBED_NORMALIZE`（默认：`true`）
- `RETRIEVAL_CHUNK_TARGET_TOKENS`（可选，覆盖自动分段长度）
- `RETRIEVAL_CHUNK_OVERLAP_TOKENS`（可选，覆盖自动重叠长度）
- `RETRIEVAL_CHARS_PER_TOKEN`（可选，默认 `1.8`）

说明：默认会根据 embedding 模型能力自动估算分段长度。  
例如 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` 会比之前 400-token 策略更短，避免被严重截断。
