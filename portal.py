from base64 import b64encode
import json
import re
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError

class Transparencia:
    dcto = str

    def __init__(self, dcto: str) -> None:
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.dcto = re.sub(r"\D", "", dcto)
        if not dcto:
            raise Exception("Informe um documento válido!")
        self.debitos = []

        path = Path(f"temp/{self.dcto}").absolute()
        path.mkdir(parents=True, exist_ok=True)
        self.path = path
    
    async def playwright_start(self) -> None:
        # Método que Inicializa o playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.page.set_default_timeout(40000)

    async def playwright_finish(self) -> None:
        # Finaliza a sessão do playwright
        await self.context.close()
        await self.playwright.stop()
        await self.browser.close()

    async def _coleta_dados_pessoais(self, tabela: BeautifulSoup) -> dict:
        nome = re.search(r"Nome.*?span>\s(.*?)\n", str(tabela), re.S).group(1).strip()
        localidade = re.search(r"Localidade.*?span>\s(.*?)\n",  str(tabela), re.S).group(1).strip()

        # Coleta do documento do beneficiario
        pattern = r"CNPJ.*?span>\s*(.*?)\n"
        if len(self.dcto) <= 12:
            pattern = r"CPF.*?span>\s*(.*?)\n"
        documento = re.search(pattern, str(tabela), re.S).group(1)

        return {
            "nome": nome,
            "documento": documento,
            "localidade": localidade,
        }

    async def _coleta_cabecalho(self, html: str) -> list[dict]:
        dados = []
        soup = BeautifulSoup(html, "html.parser")
        tabela_informacoes = soup.find("section", {"class": "dados-tabelados"}).find("div", {"class": "row"})
        dados_pessoais = await self._coleta_dados_pessoais(tabela_informacoes)

        tabelas_recebimento = soup.find_all("div", {"class": "br-table"})
        index=1
        for tabela in tabelas_recebimento:
            beneficio = re.search(r"responsive\">.*?strong>(.*?)<", str(tabela), re.S).group(1)
            linhas_info = tabela.find_all("div")
            for linha in linhas_info:
                td = linha.find_all("td")
                if not td:
                    continue
                
                dado = {
                    "nome": dados_pessoais["nome"],
                    "documento": dados_pessoais["documento"],
                    "localidade": dados_pessoais["localidade"],
                    "beneficio": beneficio,
                    "total_recebido": td[3].text.replace("R$", "").strip(),
                }
                
                """
                Aqui é necessário utilizar algum serviço de captcha bypass
                
                await self.page.click(f"//html/body/main/div/div[2]/div[2]/div/div[2]/div/div/div/div/table/tbody/tr/td[{index}]/a", timeout=2500)
                try:
                    await self.page.wait_for_selector("#tabelaDetalheDisponibilizado")
                except TimeoutError:
                    dado["parcelas"] = []
                    dados.append(dado)
                    continue

                html = await self.page.content()
                dado["parcelas"] = await self._coleta_parcelas(html)
                """
                dados.append(dado)
            index+=1
        return dados

    async def _coleta_parcelas(self, html: str) -> list:
        recursos = []
        html = await self.page.content()
        soup = BeautifulSoup(html, "html.parser")
        tabela_recursos = soup.find("table", {"id": "tabelaDetalheDisponibilizado"}).find("tbody")
        linhas = tabela_recursos.find_all("tr")
        for linha in linhas:
            td = linha.find_all("td")

            recurso = {
                "mes": td[0].text,
                "parcela": td[1].text,
                "uf": td[2].text,
                "municipio": td[3].text,
                "enquadramento": td[4].text, 
                "valor": td[5].text,
                "observacao": td[6].text,
            }
            recursos.append(recurso)
        return recursos

    async def _aceita_cookies(self) -> None:
        try:
            #Aceita os cookies da página
            await self.page.click("#accept-all-btn", timeout=1500)
            await self.page.wait_for_load_state("networkidle")
        except TimeoutError:
            pass

    async def _login_sistema(self) -> tuple:
        for _ in range(4):
            # Acesso à página principal
            await self.page.goto("https://portaldatransparencia.gov.br/pessoa/visao-geral", timeout=5000)
            await self._aceita_cookies()
            
            try:
                # Escolhe a opção de documento
                button_id = "#button-consulta-pessoa-juridica"
                if len(self.dcto) < 14:
                    button_id = "#button-consulta-pessoa-fisica"
                await self.page.click(button_id)

                # Preenche campo de documento
                await self.page.locator("#termo").fill(self.dcto)
                await self._aceita_cookies()
    
                # clica no icone de refinar busca
                await self.page.locator("button[aria-controls=\"box-busca-refinada\"]").click(timeout=2500)
                await self.page.wait_for_selector("#btnConsultarPF")

                # Clica no icone de pesquisa
                await self.page.click("#btnConsultarPF", timeout=2000)

                # Seleciona o nome dado na pesquisa
                await self.page.click(".link-busca-nome", timeout=2000)
                await self.page.wait_for_load_state("load")

                html = await self.page.content()
                if re.search(r"Não encontrada", html):
                    raise Exception("Página não encontrada! Tente novamente mais tarde!")
                
                await self._aceita_cookies()

                # Abre listagem de recebimento de recursos
                await self.page.wait_for_selector("button[aria-controls=\"accordion-recebimentos-recursos\"]")
                await self.page.locator("button[aria-controls=\"accordion-recebimentos-recursos\"]").click(timeout=2000)
                await self.page.wait_for_load_state("load")
            except TimeoutError:
                print(f" ======== [{_+1}] Tentativa ======== ")
                continue
            break
        
        # tira o print da página e transforma em base64
        img = await self.page.locator("#main").screenshot(path=self.path / "screenshot.png")
        base64 = b64encode(img).decode("utf-8")

        # Aciono a função de coleta do cabeçalho
        html = await self.page.content()
        return html, base64

    async def _coleta_dados(self) -> tuple:
        html, encodado = await self._login_sistema()
        cabecalho = await self._coleta_cabecalho(html)
        return cabecalho, encodado

async def main(dcto: str) -> dict:
    transparencia = Transparencia(dcto=dcto)
    await transparencia.playwright_start()
    try:
        dados, imagem_base64 = await transparencia._coleta_dados()
        resultado = {
            "dados": dados,
            "imagem_base64": imagem_base64
        }

        # Salvando o JSON em disco, se necessário
        json_path = transparencia.path / "resultado.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=4, ensure_ascii=False)
        return resultado
   
    except TimeoutError:
        raise TimeoutError("Não foi possível fazer a coleta dos dados no momento, tente novamente mais tarde!")
    finally:
       await transparencia.playwright_finish()

# Executa somente se rodar direto: python portal.py
if __name__ == "__main__":
    import sys
    dcto = input("Digite o documento (CPF/CNPJ): ")
    if len(sys.argv) > 1:
        dcto = sys.argv[1]

    asyncio.run(main(dcto))