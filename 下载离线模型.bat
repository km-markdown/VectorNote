@echo off
chcp 65001 >nul
echo ==============================================
echo        开始下载 all-MiniLM-L6-v2 模型
echo           镜像源：hf-mirror.com
echo ==============================================
echo.

:: 1. 创建主目录
mkdir "pretrained_model\all-MiniLM-L6-v2"
mkdir "pretrained_model\all-MiniLM-L6-v2\1_Pooling"

:: 2. 基础文件下载
set "BASE_URL=https://hf-mirror.com/sentence-transformers/all-MiniLM-L6-v2/resolve/main"
set "SAVE_DIR=pretrained_model/all-MiniLM-L6-v2"

echo 正在下载 config.json...
curl -L -o "%SAVE_DIR%\config.json" "%BASE_URL%/config.json"

echo 正在下载 pytorch_model.bin...
curl -L -o "%SAVE_DIR%\pytorch_model.bin" "%BASE_URL%/pytorch_model.bin"

echo 正在下载 data_config.json...
curl -L -o "%SAVE_DIR%\data_config.json" "%BASE_URL%/data_config.json"

echo 正在下载 config_sentence_transformers.json...
curl -L -o "%SAVE_DIR%\config_sentence_transformers.json" "%BASE_URL%/config_sentence_transformers.json"

echo 正在下载 modules.json...
curl -L -o "%SAVE_DIR%\modules.json" "%BASE_URL%/modules.json"

echo 正在下载 sentence_bert_config.json...
curl -L -o "%SAVE_DIR%\sentence_bert_config.json" "%BASE_URL%/sentence_bert_config.json"

echo 正在下载 special_tokens_map.json...
curl -L -o "%SAVE_DIR%\special_tokens_map.json" "%BASE_URL%/special_tokens_map.json"

echo 正在下载 tokenizer.json...
curl -L -o "%SAVE_DIR%\tokenizer.json" "%BASE_URL%/tokenizer.json"

echo 正在下载 tokenizer_config.json...
curl -L -o "%SAVE_DIR%\tokenizer_config.json" "%BASE_URL%/tokenizer_config.json"

echo 正在下载 train_script.py...
curl -L -o "%SAVE_DIR%\train_script.py" "%BASE_URL%/train_script.py"

echo 正在下载 vocab.txt...
curl -L -o "%SAVE_DIR%\vocab.txt" "%BASE_URL%/vocab.txt"

:: 3. 1_Pooling 目录文件
echo 正在下载 1_Pooling/config.json...
curl -L -o "%SAVE_DIR%\1_Pooling\config.json" "%BASE_URL%/1_Pooling/config.json"

echo.
echo ==============================================
echo              所有文件下载完成！
echo 模型路径：C:\data\pretrained_model\all-MiniLM-L6-v2
echo ==============================================
pause

