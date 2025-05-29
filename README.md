<h1>📊 Transparência - Coletor de Dados do Portal da Transparência</h1>
<h2> Desafio Full Stack com Hiperautomação</h2>
<p>
  <b>Desafio completo<b>:  
  https://github.com/mostqi/desafios-fullstack-python/tree/main/desafio-01
</p>

<p>
  Este projeto automatiza a coleta de dados de beneficiários no 
  <a href="https://portaldatransparencia.gov.br/" target="_blank">Portal da Transparência do Governo Federal</a> 
  utilizando a biblioteca <a href="https://playwright.dev/python/" target="_blank">Playwright</a>, 
  extraindo informações de benefícios recebidos com suporte à exportação em formato JSON, 
  incluindo imagem da página em Base64.
</p>

<hr>

<h2>🚀 Funcionalidades</h2>
<ul>
  <li>Acesso automático ao Portal da Transparência</li>
  <li>Consulta por <strong>CPF</strong> ou <strong>CNPJ</strong></li>
  <li>Extração de dados pessoais e benefícios recebidos</li>
  <li>Captura de tela da página em <strong>Base64</strong></li>
  <li>Geração de JSON contendo:
    <ul>
      <li>Dados do beneficiário</li>
      <li>Benefícios recebidos</li>
      <li>Screenshot da página</li>
    </ul>
  </li>
</ul>

<hr>

<h2>📦 Estrutura do JSON gerado</h2>
<pre><code>{
  "dados": [
    {
      "nome": "João da Silva",
      "documento": "12345678900",
      "localidade": "São Paulo/SP",
      "beneficio": "Auxílio Emergencial",
      "total_recebido": "1.200,00"
    }
  ],
  "imagem_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
</code></pre>

<hr>

<h2>🧰 Tecnologias Utilizadas</h2>
<ul>
  <li>Python 3.10+</li>
  <li><a href="https://playwright.dev/python/">Playwright</a></li>
  <li>BeautifulSoup</li>
  <li>AsyncIO</li>
  <li>Regex</li>
  <li>Base64</li>
</ul>

<hr>

<h2>📁 Estrutura do Projeto</h2>
<pre><code>.
├── temp/
│   └── {CPF_CNPJ}/
│       ├── screenshot.png
│       └── resultado.json
├── transparencia.py
├── README.html
├── requirements.txt
└── .gitignore
</code></pre>

<hr>

<h2>⚙️ Como Usar</h2>

<h3>1. Instale as dependências:</h3>
<pre><code>pip install -r requirements.txt
playwright install</code></pre>
<p><em>Nota: A instalação do Playwright pode exigir o download de navegadores.</em></p>

<h3>2. Execute o script:</h3>
<pre><code>python transparencia.py</code></pre>

<h3>3. Personalize a consulta</h3>
<p>Altere o CPF ou CNPJ desejado dentro do código <code>transparencia.py</code>:</p>

<pre><code>transparencia = Transparencia(dcto="")</code></pre>

<hr>

<h2>📄 requirements.txt</h2>
<pre><code>playwright
beautifulsoup4
</code></pre>

<hr>

<h2>📄 .gitignore</h2>
<pre><code># Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
</pre></code>
<hr>

<h2>🔐 Avisos Legais</h2>
<ul>
  <li>Este projeto é <strong>educacional</strong> e não deve ser usado para coletas em massa.</li>
  <li>O uso excessivo pode violar os <strong>termos de uso do site público</strong>.</li>
  <li>É responsabilidade do usuário respeitar os limites éticos e legais.</li>
</ul>

<hr>

<h2>📜 Licença</h2>
<p>Este projeto está licenciado sob a Licença MIT - veja o arquivo <code>LICENSE</code> para mais detalhes.</p>
