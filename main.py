from fastapi import FastAPI, HTTPException
from portal import Transparencia

app = FastAPI()

@app.get("/api/beneficios/{documento}")
async def get_beneficios(documento: str):
    if not documento:
        raise HTTPException(status_code=400, detail="Documento inválido")
    
    transparencia = Transparencia(dcto=documento)
    await transparencia.playwright_start()

    try:
        dados, imagem_base64 = await transparencia._coleta_dados()
        await transparencia.playwright_finish()
        return {
            "dados": dados,
            "imagem_base64": imagem_base64
        }

    except Exception as e:
        await transparencia.playwright_finish()
        raise HTTPException(status_code=500, detail=str(e))
