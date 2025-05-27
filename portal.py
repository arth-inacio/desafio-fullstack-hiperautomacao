from base64 import b64encode
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
        self.browser = await self.playwright.chromium.launch(headless=False)
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
        for tabela in tabelas_recebimento:
            beneficio = re.search(r"responsive\">.*?strong>(.*?)<", str(tabela), re.S).group(1)
            linhas_info = tabela.find_all("div")
            for linha in linhas_info:
                td = linha.find_all("td")
                if not td:
                    continue
                valor_recebido = td[3].text.replace("R$", "").strip()
        
                dado = {
                    "nome": dados_pessoais["nome"],
                    "documento": dados_pessoais["documento"],
                    "localidade": dados_pessoais["localidade"],
                    "beneficio": beneficio,
                    "total_recebido": valor_recebido,
                }
                dados.append(dado)
        print(dados)
        return dados

    async def _aceita_cookies(self) -> None:
        try:
            #Aceita os cookies da página
            await self.page.click("#accept-all-btn", timeout=1500)
            await self.page.wait_for_load_state("networkidle")
        except TimeoutError:
            pass

    async def _login_sistema(self) -> str:
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
                await self.page.locator("button[aria-controls=\"accordion-recebimentos-recursos\"]").click(timeout=2000)
            except TimeoutError:
                print(f" ======== [{_+1}] Tentativa ======== ")
                await self.page.reload()
                continue
            break
        
        # tira o print da página e transforma em base64
        img = await self.page.locator("#main").screenshot(path=self.path / "screenshot.png")
        base64 = b64encode(img).decode("utf-8")

        # Aciono a função de coleta do cabeçalho
        html = await self.page.content()
        return html

    async def _coleta_gastos(self) -> None:
        html = await self._login_sistema()
        cabecalho = await self._coleta_cabecalho(html)
        return cabecalho

async def main() -> None:
    transparencia = Transparencia(dcto="")
    await transparencia.playwright_start()
    try:
        await transparencia._coleta_gastos()
    except TimeoutError:
        raise TimeoutError("Não foi possivel fazer a coleta dos dados no momento, tente novamente mais tarde!")
    await transparencia.playwright_finish()
    print( "============= Coleta de dados processada com sucesso! =============")

if __name__ == "__main__":
    asyncio.run(main())