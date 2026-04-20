chcp 65001 >nul
echo ==============================================
echo        开始运行本地知识库
echo ==============================================


cd /d C:\XX_DD\LLM_RAG\VectorNoteNew

call venv_VectorNote\Scripts\activate

echo on

python app.py

pause


