from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datadotworld as dw
import google.generativeai as genai
import json
import re
import asyncio
from datetime import datetime
import uvicorn

# Configurações
app = FastAPI(title="Sistema de Controle de Estoque", version="1.0.0")

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações API
DATAWORLD_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJweXRob246YWRtamVzdXNpYSIsImlzcyI6ImNsaWVudDpweXRob246YWdlbnQ6YWRtamVzdXNpYTo6OGZhOGQ5ZDYtNjFmOC00YzdmLWFiMWMtYmYxNDM1NDA3MjNmIiwiaWF0IjoxNzQ4MTY2NTM1LCJyb2xlIjpbInVzZXJfYXBpX2FkbWluIiwidXNlcl9hcGlfcmVhZCIsInVzZXJfYXBpX3dyaXRlIl0sImdlbmVyYWwtcHVycG9zZSI6dHJ1ZSwic2FtbCI6e319._zGOiWQmLjGXRdBPOIx-W9JxlrvUn3kHiNTNt70Jr47YEtu8r1wBaS8Se1DyHdU2VSynjGC7_qCBGdBKqXm4Ig"
GEMINI_API_KEY = "AIzaSyAI170iCuFZOwJA0fY_zbWqKjJ9t1JTUE8"

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Modelos Pydantic
class Product(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = ""
    category: str
    price: float
    stock_current: int
    stock_min: int
    stock_max: int
    unit: str
    created_at: Optional[datetime] = None

class StockMovement(BaseModel):
    product_id: int
    type: str  # "entrada" ou "saida"
    quantity: int
    reason: str
    user: str
    timestamp: Optional[datetime] = None

class TextInput(BaseModel):
    text: str
    category: Optional[str] = "geral"

# Banco de dados em memória (simulação)
products_db = []
movements_db = []
next_product_id = 1

# Funções de Processamento
def clean_utf8_text(text: str) -> str:
    """Limpa e normaliza texto UTF-8"""
    try:
        # Remove caracteres especiais e normaliza
        cleaned = re.sub(r'[^\w\s\-\.\,\:\;\(\)]', '', text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned.encode('utf-8').decode('utf-8')
    except Exception:
        return text

def extract_product_data(text: str) -> dict:
    """Extrai dados de produto usando Gemini"""
    try:
        prompt = f"""
        Analise o texto abaixo e extraia informações de produto para controle de estoque.
        Retorne APENAS um JSON válido com os campos:
        - name (string)
        - category (string)
        - price (número)
        - stock_current (número)
        - stock_min (número)
        - stock_max (número)
        - unit (string)
        - description (string)
        
        Texto: {text}
        
        JSON:
        """
        
        response = model.generate_content(prompt)
        json_text = response.text.strip()
        
        # Limpa markdown se presente
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]
            
        return json.loads(json_text)
    except Exception as e:
        return {
            "name": "Produto Extraído",
            "category": "geral",
            "price": 0.0,
            "stock_current": 0,
            "stock_min": 5,
            "stock_max": 100,
            "unit": "unidade",
            "description": text[:100]
        }

def check_low_stock() -> List[dict]:
    """Verifica produtos com estoque baixo"""
    low_stock = []
    for product in products_db:
        if product["stock_current"] <= product["stock_min"]:
            low_stock.append({
                "id": product["id"],
                "name": product["name"],
                "current": product["stock_current"],
                "minimum": product["stock_min"],
                "urgency": "alta" if product["stock_current"] == 0 else "média"
            })
    return low_stock

def get_stock_analysis() -> dict:
    """Análise geral do estoque usando IA"""
    try:
        stock_summary = {
            "total_products": len(products_db),
            "low_stock_count": len(check_low_stock()),
            "total_value": sum(p["price"] * p["stock_current"] for p in products_db),
            "categories": {}
        }
        
        # Agrupar por categoria
        for product in products_db:
            cat = product["category"]
            if cat not in stock_summary["categories"]:
                stock_summary["categories"][cat] = {"count": 0, "value": 0}
            stock_summary["categories"][cat]["count"] += 1
            stock_summary["categories"][cat]["value"] += product["price"] * product["stock_current"]
        
        # Usar Gemini para insights
        prompt = f"""
        Analise os dados de estoque e forneça 3 insights importantes:
        {json.dumps(stock_summary, indent=2)}
        
        Retorne apenas um JSON com:
        - insights: [array de strings com 3 insights]
        - recommendations: [array de strings com 3 recomendações]
        """
        
        response = model.generate_content(prompt)
        ai_analysis = json.loads(response.text.strip().replace("```json", "").replace("```", ""))
        
        stock_summary.update(ai_analysis)
        return stock_summary
        
    except Exception as e:
        return {
            "total_products": len(products_db),
            "low_stock_count": len(check_low_stock()),
            "insights": ["Erro na análise IA"],
            "recommendations": ["Verificar configurações"]
        }

# Endpoints da API
@app.get("/")
async def root():
    return {"message": "Sistema de Controle de Estoque API", "version": "1.0.0"}

@app.post("/products/", response_model=Product)
async def create_product(product: Product):
    global next_product_id
    product_dict = product.dict()
    product_dict["id"] = next_product_id
    product_dict["created_at"] = datetime.now()
    products_db.append(product_dict)
    next_product_id += 1
    return product_dict

@app.get("/products/", response_model=List[Product])
async def get_products():
    return products_db

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: Product):
    existing = next((p for p in products_db if p["id"] == product_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    product_dict = product.dict()
    product_dict["id"] = product_id
    product_dict["created_at"] = existing["created_at"]
    
    index = products_db.index(existing)
    products_db[index] = product_dict
    return product_dict

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    products_db.remove(product)
    return {"message": "Produto removido com sucesso"}

@app.post("/stock/movement/")
async def add_stock_movement(movement: StockMovement):
    product = next((p for p in products_db if p["id"] == movement.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    movement_dict = movement.dict()
    movement_dict["timestamp"] = datetime.now()
    movements_db.append(movement_dict)
    
    # Atualizar estoque
    if movement.type == "entrada":
        product["stock_current"] += movement.quantity
    elif movement.type == "saida":
        if product["stock_current"] >= movement.quantity:
            product["stock_current"] -= movement.quantity
        else:
            raise HTTPException(status_code=400, detail="Estoque insuficiente")
    
    return {"message": "Movimentação registrada", "new_stock": product["stock_current"]}

@app.get("/stock/movements/")
async def get_movements():
    return movements_db

@app.get("/stock/low/")
async def get_low_stock():
    return check_low_stock()

@app.get("/analytics/dashboard/")
async def get_dashboard_data():
    return get_stock_analysis()

@app.post("/text/process/")
async def process_text(input_data: TextInput):
    try:
        # Limpar texto
        cleaned_text = clean_utf8_text(input_data.text)
        
        # Extrair dados do produto
        product_data = extract_product_data(cleaned_text)
        
        return {
            "original_text": input_data.text,
            "cleaned_text": cleaned_text,
            "extracted_data": product_data,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.post("/text/to-product/")
async def text_to_product(input_data: TextInput):
    try:
        # Processar texto
        cleaned_text = clean_utf8_text(input_data.text)
        product_data = extract_product_data(cleaned_text)
        
        # Criar produto automaticamente
        product = Product(**product_data)
        created_product = await create_product(product)
        
        return {
            "message": "Produto criado a partir do texto",
            "product": created_product,
            "processed_text": cleaned_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na criação: {str(e)}")

@app.get("/dataworld/test/")
async def test_dataworld():
    try:
        # Teste básico do Data World
        results = dw.query(
            'jonloyens/intermediate-data-world', 
            'SELECT * FROM fatal_police_shootings_data LIMIT 5'
        )
        return {
            "status": "success",
            "rows": len(results.dataframe),
            "sample": results.dataframe.head().to_dict()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
