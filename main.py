from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io

app = FastAPI()

@app.post("/analyze")
async def analyze_excel(file: UploadFile = File(...)):
    contents = await file.read()
    df_raw = pd.read_excel(io.BytesIO(contents), header=None)
    df_data = df_raw.iloc[15:].copy()
    return {
        "status": "success",
        "total_rows_processed": len(df_data),
        "columns_count": len(df_data.columns)
    }
    mo_col_idx, ind_col_idx, obj_col_idx = 0, 1, 3
    staff_col_idx, phys_col_idx = 5, 12
    plan_col_idx, fact_col_idx = 16, 17
    delay_col_idx, dyn_col_idx = 25, 26, 27

    df_data = df_data.dropna(subset=[obj_col_idx]).copy()
    
    for idx in [staff_col_idx, phys_col_idx, plan_col_idx, fact_col_idx, delay_col_idx, dyn_col_idx]:
        df_data[idx] = pd.to_numeric(df_data[idx], errors='coerce').fillna(0)
        
    total_objects = len(df_data)
    industry_counts = df_data[ind_col_idx].value_counts().to_dict()
    
    df_delayed = df_data[df_data[delay_col_idx] > 1].copy()
    delayed_count = len(df_delayed)
    
    avg_phys_fact = float(df_delayed[phys_col_idx].mean()) if not df_delayed.empty else 0.0
    total_staff = int(df_delayed[staff_col_idx].sum()) if not df_delayed.empty else 0
    
    df_completed = df_data[df_data[delay_col_idx] == 0].copy()
    completed_count = len(df_completed)
    completed_pct = (completed_count / total_objects) * 100 if total_objects > 0 else 0
    completed_mos = df_completed[mo_col_idx].dropna().unique().tolist()
    
    total_fin_plan = float(df_data[plan_col_idx].sum())
    total_fin_fact = float(df_data[fact_col_idx].sum())
    total_cash_pct = (total_fin_fact / total_fin_plan * 100) if total_fin_plan > 0 else 0
    
    industry_cash = {}
    for ind, group in df_data.groupby(ind_col_idx):
        p_sum = group[plan_col_idx].sum()
        f_sum = group[fact_col_idx].sum()
        industry_cash[str(ind)] = round((f_sum / p_sum * 100), 2) if p_sum > 0 else 0.0

    return {
        "total_objects": total_objects,
        "industry_counts": industry_counts,
        "delayed_count": delayed_count,
        "avg_phys_fact": round(avg_phys_fact, 1),
        "total_staff": total_staff,
        "completed_count": completed_count,
        "completed_pct": round(completed_pct, 2),
        "completed_mos": completed_mos,
        "total_cash_pct": round(total_cash_pct, 2),
        "industry_cash": industry_cash
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
