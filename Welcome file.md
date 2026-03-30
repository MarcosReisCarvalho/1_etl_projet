
# Documentação Técnica: Módulo de Extração (extract_data.py)

**Projeto:** First ETL Project

**Arquiteto Responsável:** Gemini (Senior Python Dev & Architect)

**Data:** 30 de Março de 2026

**Versão:** 1.2 (Com suporte a Resiliência e Retry)

----------

## 1. Visão Geral

O script `extract_data.py` é o ponto de entrada (Ingestion Layer) do pipeline de ETL. Sua responsabilidade é conectar-se à API do OpenWeather, autenticar-se via segredos protegidos e persistir os dados brutos (Raw Data) em um sistema de arquivos local para posterior processamento.

----------

## 2. Bibliotecas e Dependências

**Biblioteca**

**Versão Sugerida**

**Função**

`python-dotenv`

^1.0.0

Carregamento de variáveis de ambiente do arquivo `.env`.

`requests`

^2.31.0

Realização de chamadas HTTP (GET).

`pathlib`

(Built-in)

Manipulação de caminhos de arquivos de forma agnóstica ao SO.

`logging`

(Built-in)

Registro de eventos, erros e fluxos do sistema.

`urllib3`

(Built-in via requests)

Implementação da lógica de Retry e Backoff.

----------

## 3. Estrutura de Código e Explicação

### 3.1. Gestão de Configuração (`bootstrap_env`)

**Código:** `root_dir = Path(__file__).resolve().parent.parent`

**Explicação:** Esta linha utiliza metadados do Python para localizar a raiz do projeto.

-   `__file__`: Localiza o script em `src/`.
    
-   `.resolve()`: Obtém o caminho absoluto.
    
-   `.parent.parent`: Sobe dois níveis para encontrar a pasta `config/`.
    
-   **Motivo:** Garante que o script não quebre se for movido ou executado de diferentes diretórios no WSL.
    

### 3.2. Resiliência e Retry (`create_retry_session`)

**Conceito:** _Exponential Backoff_.

**Explicação:** O script não desiste na primeira falha de rede. Ele tentará até 3 vezes, aguardando um tempo crescente entre as tentativas (0.3s, 0.6s, 1.2s).

-   **status_forcelist (500, 502, 504):** Apenas erros de servidor disparam o retry. Erros 401 (Chave Inválida) ou 404 (Cidade não encontrada) são erros de lógica e não devem ser repetidos.
    

### 3.3. Segurança e Fail-Fast

**Código:** `exit(1)`

**Explicação:** Se a `API_KEY` for nula ou o `.env` estiver ausente, o script encerra com código `1`.

-   **Motivo:** Em arquitetura de sistemas, "falhar rápido" evita que processos subsequentes operem com dados corrompidos ou inexistentes. O código `1` sinaliza ao sistema operacional (ou orquestrador) que houve um erro crítico.
    

### 3.4. Persistência de Dados (I/O)

**Código:** `json.dump(data, f, indent=4, ensure_ascii=False)`

**Explicação:** Salva o dicionário Python no formato JSON.

-   `indent=4`: Torna o arquivo legível para humanos (Prettier/Format).
    
-   `ensure_ascii=False`: Permite caracteres brasileiros (acentuação) sem codificações como `\u00e3`.
    

----------

## 4. Como Executar

Certifique-se de estar na raiz do projeto e que o `uv` ou seu ambiente virtual esteja ativo:

Bash

```
uv run src/extract_data.py

```

----------

## 5. Próximos Passos (Roadmap)

1.  **Camada de Transformação:** Criar `src/transform_data.py` para normalizar o JSON.
    
2.  **Schema Validation:** Implementar `Pydantic` para validar se a API retornou todos os campos esperados.
    
3.  **Containerização:** Criar um `Dockerfile` para rodar este processo de forma isolada.
