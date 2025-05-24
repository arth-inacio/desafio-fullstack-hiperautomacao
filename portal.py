import re
import asyncio
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
        self.debitos = []
    
    async def playwright_start(self) -> None:
        # Método que Inicializa o playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.page.set_default_timeout(30000)

    async def playwright_finish(self) -> None:
        # Finaliza a sessão do playwright
        await self.context.close()
        await self.playwright.stop()
        await self.browser.close()

    async def _coleta_cabecalho(self, soup: BeautifulSoup) -> dict:
        tabela_informacoes = soup.find("section", {"class": "dados-tabelados"})
        linhas = tabela_informacoes.find_all("div", {"class": "col-xs-12 col-sm-3"})
        dados = {
            "nome": linhas[0].text,
            "documento": linhas[1].text,
            "nis": linhas[2].text,
        }
        return dados

    async def _coleta_gastos(self) -> None:
        # Acesso à página principal
        await self.page.goto("https://portaldatransparencia.gov.br/pessoa/visao-geral", timeout=5000)
        await self.page.wait_for_load_state("networkidle")

        #Aceita os cookies da página
        await self.page.click("#accept-all-btn")

        # Escolhe a opção de documento
        if len(self.dcto) < 14:
            await self.page.click("#button-consulta-pessoa-fisica")
        else:
            await self.page.click("#button-consulta-pessoa-juridica")

        # Preenche campo de documento
        await self.page.locator("#termo").fill(self.dcto)

        #Aceita os cookies da página
        await self.page.click("#accept-all-btn")

        # clica no icone de refinar busca
        await self.page.locator("button[aria-controls=\"box-busca-refinada\"]").click()

        # Clica no icone de pesquisa
        await self.page.click("#btnConsultarPF", timeout=2000)

        html = await self.page.content()
        soup = BeautifulSoup(html, "html.parser")
        cabecalho = await self._coleta_cabecalho(soup)
        print(cabecalho)

        # Seleciona o nome dado na pesquisa
        await self.page.click(".link-busca-nome")

        # Abre listagem de rebimento de recursos
        await self.page.locator("button[aria-controls=\"accordion-recebimentos-recursos\"]").click()

        # Clica no botao detalhar
        await self.page.click("#btnDetalharBpc", timeout=5000)

async def main() -> None:
    transparencia = Transparencia(dcto="427.548.568-89")
    await transparencia.playwright_start()
    try:
        await transparencia._coleta_gastos()
    except TimeoutError:
        raise TimeoutError("Não foi possivel fazer a coleta dos dados no momento, tente novamente mais tarde!")
    await transparencia.playwright_finish()

if __name__ == "__main__":
    asyncio.run(main())