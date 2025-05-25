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
        if not dcto:
            raise Exception("Informe um documento válido!")
        self.debitos = []
    
    async def playwright_start(self) -> None:
        # Método que Inicializa o playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.page.set_default_timeout(60000)

    async def playwright_finish(self) -> None:
        # Finaliza a sessão do playwright
        await self.context.close()
        await self.playwright.stop()
        await self.browser.close()

    async def _coleta_cabecalho(self, soup: BeautifulSoup) -> dict:
        tabela_informacoes = soup.find("section", {"class": "dados-tabelados"}).find("div", {"class": "row"})
        linhas = tabela_informacoes.find_all("div")
        
        if len(self.dcto) <= 12:
            documento = re.search(r"CPF\s*(.*?)\n", linhas[1].text, re.S).group(1)
        else:
            documento = re.search(r"CNPJ\s*(.*?)\n", linhas[1].text, re.S).group(1)

        dados = {
            "nome": (re.search(r"Nome\s*(.*)", linhas[0].text, re.S).group(1)).strip(),
            "documento": documento.strip(),
            "localidade": re.search(r"Localidade\s*(.*)", linhas[2].text, re.S).group(1).strip(),
        }
        return dados

    async def _coleta_gastos(self) -> None:
        for _ in range(4):
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
            await self.page.wait_for_load_state("networkidle")

            # clica no icone de refinar busca
            try:
                await self.page.locator("button[aria-controls=\"box-busca-refinada\"]").click(timeout=2500)
                await self.page.wait_for_selector("#btnConsultarPF")
            except TimeoutError:
                continue
            break
       
        # Clica no icone de pesquisa
        await self.page.click("#btnConsultarPF", timeout=2000)

        # Seleciona o nome dado na pesquisa
        await self.page.click(".link-busca-nome")

        # Aceita os cookies da página
        await self.page.click("#accept-all-btn")

        # Aciono a função de coleta do cabeçalho
        html = await self.page.content()
        soup = BeautifulSoup(html, "html.parser")
        cabecalho = await self._coleta_cabecalho(soup)
        print(cabecalho)

        # Abre listagem de recebimento de recursos
        await self.page.locator("button[aria-controls=\"accordion-recebimentos-recursos\"]").click()

        # Clica no botao detalhar
        await self.page.click("#btnDetalharBpc", timeout=5000)

async def main() -> None:
    transparencia = Transparencia(dcto="")
    await transparencia.playwright_start()
    try:
        await transparencia._coleta_gastos()
    except TimeoutError:
        raise TimeoutError("Não foi possivel fazer a coleta dos dados no momento, tente novamente mais tarde!")
    await transparencia.playwright_finish()

if __name__ == "__main__":
    asyncio.run(main())