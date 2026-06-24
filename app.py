import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Garante que o diretório raiz do projeto está no sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.migrations import run_migrations
from services import manifestacao_service, auth_service
from repositories import manifestacao_repo, validacao_repo

# Executa migrações ao inicializar o banco de dados SQLite
run_migrations()

app = FastAPI(title="Ouvidoria Pública API", version="2.0.0")

# Permite CORS para desenvolvimento frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para payloads de entrada
class ManifestacaoCreate(BaseModel):
    category: str
    anonymous: bool
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    subject: str
    description: str
    sector: Optional[str] = ""
    attachments: Optional[List[str]] = []

class ManifestacaoUpdate(BaseModel):
    sector: str
    status: str
    response: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ValidationCreate(BaseModel):
    id: str
    groupName: str
    reviewer: str
    reviewDate: str
    decision: str
    consistencyNote: Optional[str] = ""
    completenessNote: Optional[str] = ""
    rnfNote: Optional[str] = ""
    createdAt: str

# Função auxiliar para mapear manifestações no formato esperado pelo JS frontend
def map_to_frontend(m: dict, history: list = None) -> dict:
    # Formata data_registro
    reg_date = m.get("data_registro")
    if hasattr(reg_date, "isoformat"):
        reg_date = reg_date.isoformat()
    elif not isinstance(reg_date, str):
        reg_date = str(reg_date)
        
    up_date = m.get("data_atualizacao")
    if hasattr(up_date, "isoformat"):
        up_date = up_date.isoformat()
    elif not isinstance(up_date, str):
        up_date = str(up_date)

    return {
        "protocol": m.get("protocolo"),
        "category": m.get("categoria"),
        "subject": m.get("assunto") or "Sem assunto",
        "description": m.get("texto_manifestacao") or "",
        "status": m.get("status") or "Recebida",
        "sector": m.get("setor") or "Atendimento ao cidadão",
        "anonymous": bool(m.get("eh_anonimo")),
        "name": m.get("nome_cidadao") or "Sigiloso",
        "email": m.get("email_cidadao") or "",
        "phone": m.get("telefone_cidadao") or "",
        "history": [
            {
                "status": h.get("status_novo"),
                "date": h.get("data_alteracao").isoformat() if hasattr(h.get("data_alteracao"), "isoformat") else str(h.get("data_alteracao")),
                "note": h.get("observacao") or ""
            } for h in history
        ] if history else [
            {
                "status": "Recebida",
                "date": reg_date,
                "note": "Manifestação criada no portal."
            }
        ],
        "response": m.get("resposta_gestor") or "",
        "createdAt": reg_date,
        "updatedAt": up_date
    }

# ── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    return manifestacao_repo.estatisticas_gerais()

@app.get("/api/manifestacoes")
def list_manifestacoes():
    raw_list = manifestacao_repo.listar_todas()
    return [map_to_frontend(dict(m)) for m in raw_list]

@app.get("/api/manifestacoes/{protocolo}")
def get_manifestacao(protocolo: str):
    # Consulta pública via service (com mascaramento padrão de segurança)
    m = manifestacao_service.consultar_manifestacao(protocolo)
    if not m:
        raise HTTPException(status_code=404, detail="Manifestação não encontrada")
    
    # Adapta para o formato do JS
    return {
        "protocol": m["protocolo"],
        "category": m.get("categoria"),
        "subject": m.get("assunto") or "Sem assunto",
        "description": "Sigiloso" if m.get("eh_anonimo") else "A descrição desta manifestação está disponível apenas para o cidadão e a gestão responsável.",
        "status": m.get("status") or "Recebida",
        "sector": m.get("setor") or "Atendimento ao cidadão",
        "anonymous": m.get("eh_anonimo"),
        "name": m.get("nome_cidadao") or "Sigiloso",
        "email": "",
        "phone": "",
        "history": [
            {
                "status": h.get("status_novo"),
                "date": h.get("data_alteracao") if isinstance(h.get("data_alteracao"), str) else str(h.get("data_alteracao")),
                "note": h.get("observacao") or ""
            } for h in m.get("historico", [])
        ],
        "response": m.get("resposta_gestor") or "",
        "createdAt": str(m.get("data_registro")),
        "updatedAt": str(m.get("data_atualizacao"))
    }

@app.get("/api/manifestacoes/interna/{protocolo}")
def get_manifestacao_interna(protocolo: str):
    # Consulta interna para painel do atendente (sem mascaramento)
    m = manifestacao_repo.buscar_por_protocolo(protocolo)
    if not m:
        raise HTTPException(status_code=404, detail="Manifestação não encontrada")
    
    # Busca histórico do status
    from repositories import historico_repo
    historico = historico_repo.listar_por_manifestacao(m["id"])
    return map_to_frontend(dict(m), [dict(h) for h in historico])

@app.post("/api/manifestacoes")
def create_manifestacao(m: ManifestacaoCreate):
    dados = {
        "eh_anonimo": m.anonymous,
        "texto_manifestacao": m.description,
        "categoria": m.category,
        "assunto": m.subject,
        "nome_cidadao": m.name,
        "email_cidadao": m.email,
        "cpf_cidadao": "",  # Simplificado para web
        "telefone_cidadao": m.phone,
        "setor": m.sector or "Atendimento ao cidadão",
    }
    sucesso, msg, protocolo = manifestacao_service.registrar_manifestacao(dados, m.attachments)
    if not sucesso:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "protocol": protocolo}

@app.patch("/api/manifestacoes/{protocolo}")
def update_manifestacao(protocolo: str, data: ManifestacaoUpdate):
    m = manifestacao_repo.buscar_por_protocolo(protocolo)
    if not m:
        raise HTTPException(status_code=404, detail="Manifestação não encontrada")
    
    sucesso, msg = manifestacao_service.atualizar_status_manifestacao(
        manifestacao_id=m["id"],
        status_novo=data.status,
        observacao="Status atualizado pelo painel do atendente.",
        resposta_gestor=data.response,
        parecer_encerramento="Manifestação concluída e respondida." if data.status == "Concluída" else None,
        setor=data.sector,
        usuario_id=1  # Default para admin
    )
    if not sucesso:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.post("/api/auth/login")
def login(req: LoginRequest):
    sucesso, msg, usuario = auth_service.tentar_login(req.username, req.password)
    if not sucesso:
        raise HTTPException(status_code=401, detail=msg)
    return {"message": msg, "user": usuario}

@app.get("/api/validacoes")
def list_validacoes():
    return validacao_repo.listar_todas()

@app.post("/api/validacoes")
def create_validation(v: ValidationCreate):
    dados = {
        "id": v.id,
        "groupName": v.groupName,
        "reviewer": v.reviewer,
        "reviewDate": v.reviewDate,
        "decision": v.decision,
        "consistencyNote": v.consistencyNote,
        "completenessNote": v.completenessNote,
        "rnfNote": v.rnfNote,
        "createdAt": v.createdAt,
    }
    validacao_repo.inserir(dados)
    return {"message": "Validação registrada com sucesso"}

@app.delete("/api/validacoes/{id}")
def delete_validation(id: str):
    sucesso = validacao_repo.deletar(id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Validação não encontrada")
    return {"message": "Validação removida com sucesso"}

# ── Servir Frontend Estático do Vite ──────────────────────────────────────────

if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        
        index_path = os.path.join("dist", "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Vite frontend index.html not found"}
else:
    @app.get("/")
    def read_root():
        return {"message": "Vite frontend not built yet. Run 'npm run build'."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8501)
