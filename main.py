import sys
import asyncio
from fastapi import FastAPI
from portal import Transparencia

# Corrige erro do Playwright no Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

@app.get("/api/beneficios/{documento}")
async def get_beneficios(dcto: str):
    transparencia = Transparencia(dcto)
    await transparencia.playwright_start()
    try:
        for _ in range(5):
            dados, imagem_base64 = await transparencia._coleta_dados()
            if dados == []:
                continue
            break
        return {"dados": dados, "imagem_base64": imagem_base64}
    except TimeoutError:
        raise TimeoutError("Não foi possível acessar a página no momento! tente novamente mais tarde!")
    finally:
        await transparencia.playwright_finish()
