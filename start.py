# Arquivo de inicialização
import sys
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

#Mudar localhost para a porta desejada
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=False)
