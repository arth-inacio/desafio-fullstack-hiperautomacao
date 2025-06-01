<h1>🧾 Desafio Full Stack – Hiperautomação</h1>

  <p>
    Este projeto automatiza a coleta de dados de beneficiários no
    <a href="https://portaldatransparencia.gov.br" target="_blank">Portal da Transparência do Governo Federal</a>,
    utilizando a biblioteca <a href="https://playwright.dev/python/" target="_blank">Playwright</a>.
    A aplicação expõe uma API REST construída com <a href="https://fastapi.tiangolo.com/" target="_blank">FastAPI</a>,
    permitindo consultas por CPF ou CNPJ e retornando informações detalhadas sobre os benefícios recebidos,
    juntamente com uma captura de tela da página em formato Base64.
  </p>

  <h2>🚀 Tecnologias Utilizadas</h2>
  <ul>
    <li>Python 3.11+</li>
    <li>FastAPI</li>
    <li>Playwright (Firefox)</li>
    <li>BeautifulSoup4</li>
    <li>Uvicorn</li>
  </ul>

  <h2>⚙️ Instalação e Execução</h2>
  <h3>1. Clone o Repositório</h3>
  <pre><code>git clone https://github.com/arth-inacio/desafio-fullstack-hiperautomacao.git
cd desafio-fullstack-hiperautomacao</code></pre>

  <h3>2. Crie e Ative um Ambiente Virtual</h3>
  <pre><code>python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate</code></pre>

  <h3>3. Instale as Dependências</h3>
  <pre><code>pip install -r requirements.txt</code></pre>

  <h3>4. Instale os Navegadores do Playwright</h3>
  <pre><code>playwright install</code></pre>

  <h3>5. Inicie a Aplicação</h3>
  <pre><code>python start.py</code></pre>
  <p><strong>Nota:</strong> O arquivo <code>start.py</code> foi atualizado para desabilitar o modo <code>reload</code>, evitando conflitos com o Playwright no Windows.</p>

  <h2>📡 Endpoint da API</h2>
  <ul>
    <li><strong>GET</strong> <code>/api/beneficios?documento=CPF_OU_CNPJ</code></li>
    <li><strong>Parâmetro:</strong> <code>documento</code> (string) – CPF ou CNPJ do beneficiário.</li>
    <li><strong>Resposta:</strong>
      <ul>
        <li><code>dados</code>: Lista de benefícios recebidos</li>
        <li><code>imagem_base64</code>: Captura de tela da página em Base64</li>
      </ul>
    </li>
  </ul>

  <h2>🛠️ Estrutura do Projeto</h2>
  <pre><code>├── main.py           # Define os endpoints da API
├── portal.py         # Lógica de automação e scraping
├── start.py          # Inicializa o servidor Uvicorn
├── requirements.txt  # Lista de dependências
├── temp/             # Armazena capturas de tela e JSONs gerados</code></pre>

  <h2>🧪 Exemplo de Uso</h2>
  <pre><code>curl "http://localhost:8000/api/beneficios?documento=12345678900"</code></pre>
  <p>A resposta incluirá os dados dos benefícios e uma imagem da página em formato Base64.</p>

  <h2>⚠️ Observações</h2>
  <ul>
    <li>Certifique-se de que o Playwright está corretamente instalado e configurado.</li>
    <li>O projeto foi testado no Windows 10 com Python 3.11.</li>
    <li>Em caso de erros relacionados ao Playwright, verifique se os navegadores estão instalados e se o modo <code>reload</code> está desativado.</li>
  </ul>

  <h2>📄 Licença</h2>
  <p>Este projeto está licenciado sob a <a href="LICENSE">MIT License</a>.</p>

  <hr>

  <p>Repositório oficial: <a href="https://github.com/arth-inacio/desafio-fullstack-hiperautomacao" target="_blank">
    github.com/arth-inacio/desafio-fullstack-hiperautomacao</a>
  </p>

<hr>

<h2>📜 Licença</h2>
<p>Este projeto está licenciado sob a Licença MIT - veja o arquivo <code>LICENSE</code> para mais detalhes.</p>
