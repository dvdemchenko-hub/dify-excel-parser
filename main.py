from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import io
import requests

app = FastAPI()

# Описываем структуру JSON-запроса, которую присылает Dify
class WorkflowPayload(BaseModel):
    file: dict = None

@app.post("/analyze")
async def analyze_excel(payload: WorkflowPayload):
    try:
        # Проверяем, пришел ли файл и есть ли в нем URL
        if not payload.file or "url" not in payload.file:
            raise HTTPException(status_code=400, detail="Файл или его URL не найдены в запросе")
        
        file_url = payload.file["url"]
        
        # Скачиваем файл по временной защищенной ссылке Dify
        response = requests.get(file_url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Не удалось скачать файл с сервера Dify")
        
        # Читаем Excel в pandas, пропуская первые 15 строк шапки капремонта
        df_raw = pd.read_excel(io.BytesIO(response.content), header=None)
        df_data = df_raw.iloc[15:].copy()
        
        # Возвращаем результат в формате JSON для агента Dify
        return {
            "status": "success",
            "filename": payload.file.get("filename", "unknown.xlsx"),
            "total_rows_processed": len(df_data),
            "columns_count": len(df_data.columns),
            "message": "Таблица капремонта успешно обработана"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
