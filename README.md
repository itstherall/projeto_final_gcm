# Sistema de Controle de Estoque

API REST para gerenciamento de produtos, movimentação de estoque e
registro de vendas, desenvolvida em **Python** com **Flask**.

## Visão geral

O sistema permite cadastrar produtos, consultar seus estoques, registrar
entradas e saídas e realizar vendas com vários itens. A aplicação deve
garantir que operações inválidas não alterem o estoque e que uma venda
seja processada de forma atômica.

## Funcionalidades

### 1. Cadastrar produto

-   Recebe o código e o preço do produto.
-   Cria o produto com estoque inicial igual a `0`.
-   Não permite cadastrar dois produtos com o mesmo código.

### 2. Consultar estoque

-   Recebe o código de um produto.
-   Retorna a quantidade disponível em estoque.

### 3. Entrada de estoque

-   Recebe o código do produto e uma quantidade inteira.
-   Acrescenta a quantidade informada ao estoque atual.

### 4. Saída de estoque

-   Recebe o código do produto e uma quantidade inteira.
-   Subtrai a quantidade informada do estoque atual.
-   A operação não deve permitir que o estoque fique negativo.

### 5. Venda

-   Recebe uma lista de itens, cada um com código do produto e
    quantidade.
-   Dá baixa no estoque de cada produto.
-   Calcula o subtotal de cada item (`preço × quantidade`) e o total da
    venda.
-   A operação é **atômica**: se qualquer item for inválido ou não puder
    ser atendido, nenhum estoque deve ser alterado.

## Regras de negócio

-   Cada produto possui somente três atributos: `codigo`, `preco` e
    `estoque`.
-   `codigo` e `estoque` são números inteiros; `preco` é um número
    decimal.
-   As quantidades das movimentações e das vendas são números inteiros.
-   Todo produto é cadastrado com estoque inicial igual a zero.
-   Não há limite predefinido para a quantidade de produtos cadastrados.
-   Não é permitido cadastrar novamente um código já existente.
-   Não é permitido realizar saída ou venda em quantidade superior ao
    estoque disponível.
-   Quantidades devem ser positivas.
-   Quando uma operação falhar, o estoque deve permanecer inalterado.
-   Em vendas, todos os itens devem ser validados antes de qualquer
    baixa no estoque.

## API REST

A interface abaixo define os métodos HTTP, caminhos, campos e códigos de
status esperados.

### Convenções gerais

  Campo          Tipo esperado
  -------------- ---------------
  `codigo`       Inteiro
  `quantidade`   Inteiro
  `estoque`      Inteiro
  `preco`        Decimal

-   **400 Bad Request**: campo obrigatório ausente, tipo inválido ou
    dados fora das regras de validação.
-   **404 Not Found**: produto informado não existe.
-   **409 Conflict**: tentativa de cadastrar um produto com código já
    existente.
-   Quando uma operação retorna erro, nenhum estoque deve ser alterado.
-   As requisições e respostas utilizam JSON, exceto quando indicado que
    não há corpo.

### 1. Cadastrar produto

`POST /loja/produto`

**Requisição**

``` json
{
  "codigo": 123,
  "preco": 59.90
}
```

**Resposta --- `201 Created`**

``` json
{
  "codigo": 123,
  "preco": 59.90,
  "estoque": 0
}
```

**Possíveis erros**

-   `400 Bad Request`: código ou preço ausente, ou com tipo/formato
    inválido.
-   `409 Conflict`: já existe um produto com o código informado.

### 2. Consultar estoque

`GET /loja/produto/{codigo}/estoque`

Não possui corpo na requisição.

**Resposta --- `200 OK`**

``` json
{
  "codigo": 123,
  "estoque": 15
}
```

**Possível erro**

-   `404 Not Found`: produto não cadastrado.

### 3. Entrada de estoque

`PUT /loja/produto/{codigo}/entrada`

**Requisição**

``` json
{
  "quantidade": 10
}
```

**Resposta --- `200 OK`**

``` json
{
  "codigo": 123,
  "estoque": 25
}
```

**Possíveis erros**

-   `400 Bad Request`: quantidade ausente, inválida ou não positiva.
-   `404 Not Found`: produto não cadastrado.

### 4. Saída de estoque

`PUT /loja/produto/{codigo}/saida`

**Requisição**

``` json
{
  "quantidade": 10
}
```

**Resposta --- `200 OK`**

``` json
{
  "codigo": 123,
  "estoque": 5
}
```

**Possíveis erros**

-   `400 Bad Request`: quantidade ausente, inválida, não positiva ou
    maior que o estoque disponível.
-   `404 Not Found`: produto não cadastrado.

### 5. Realizar venda

`POST /loja/venda`

**Requisição**

``` json
{
  "itens": [
    {
      "codigo": 123,
      "quantidade": 2
    },
    {
      "codigo": 456,
      "quantidade": 1
    }
  ]
}
```

**Resposta --- `201 Created`**

``` json
{
  "total": 189.70,
  "itens": [
    {
      "codigo": 123,
      "quantidade": 2,
      "subtotal": 119.80,
      "estoque": 13
    },
    {
      "codigo": 456,
      "quantidade": 1,
      "subtotal": 69.90,
      "estoque": 7
    }
  ]
}
```

**Possíveis erros**

-   `400 Bad Request`: lista `itens` ausente ou vazia; item com campos
    ausentes ou inválidos; quantidade não positiva ou superior ao
    estoque disponível.
-   `404 Not Found`: pelo menos um produto informado não existe.

> **Atomicidade:** antes de atualizar qualquer estoque, a aplicação deve
> validar todos os itens da venda, incluindo a existência dos produtos e
> a disponibilidade das quantidades. Se uma validação falhar, a venda
> inteira deve ser cancelada.

## Arquitetura da aplicação

A aplicação deve ser organizada em camadas para separar as regras de
negócio da interface HTTP. Assim, os serviços podem ser utilizados
diretamente por testes automatizados ou por outras interfaces, sem
precisar passar pela API REST.

Uma sugestão de organização:

``` text
projeto/
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── loja.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── estoque_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── produto_repository.py
│   └── models/
│       ├── __init__.py
│       └── produto.py
├── tests/
├── run.py
├── requirements.txt
└── README.md
```

### Responsabilidade de cada camada

-   **Routes (API):** recebe as requisições HTTP, valida a estrutura
    básica dos dados, chama os serviços e transforma os resultados em
    respostas JSON com os códigos HTTP adequados.
-   **Services (negócio):** implementa as regras de cadastro, consulta,
    entrada, saída e venda. Não deve depender do Flask nem conhecer
    detalhes de requisições HTTP.
-   **Repositories (persistência):** concentra as operações de
    armazenamento e recuperação dos produtos. A implementação pode
    começar em memória e ser substituída posteriormente por um banco de
    dados.
-   **Models:** representa o produto e seus atributos (`codigo`, `preco`
    e `estoque`).

## Tecnologias

-   **Python 3**
-   **Flask** --- criação da API REST.
-   **pytest** --- testes automatizados (sugestão).

## Como executar

### Pré-requisitos

-   Python 3 instalado.
-   `pip` disponível no ambiente.

### 1. Clonar o repositório

``` bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_PROJETO>
```

### 2. Criar e ativar o ambiente virtual

**Windows (PowerShell)**

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

``` bash
pip install -r requirements.txt
```

Caso o arquivo `requirements.txt` ainda não esteja configurado, instale
o Flask:

``` bash
pip install Flask
```

### 4. Iniciar a aplicação

O comando depende do ponto de entrada definido no projeto. Se a
aplicação for iniciada pelo arquivo `run.py`:

``` bash
python run.py
```

A URL local e a porta serão as configuradas na aplicação. Em uma
configuração comum de desenvolvimento Flask, o endereço é
`http://127.0.0.1:5000`.

## Testes

Os testes devem cobrir, no mínimo:

-   Cadastro de produto com dados válidos.
-   Tentativa de cadastro com código já existente.
-   Consulta de produto existente e inexistente.
-   Entrada de estoque com quantidade válida e inválida.
-   Saída de estoque com quantidade válida, inválida e superior ao
    estoque disponível.
-   Venda com vários itens válidos.
-   Venda com produto inexistente.
-   Venda com quantidade superior ao estoque.
-   Venda com lista ausente, vazia ou com campos inválidos.
-   Garantia de que uma venda inválida não altera o estoque de nenhum
    produto.
-   Testes diretamente na camada de serviço, sem utilizar a API REST.

Para executar os testes com `pytest`:

``` bash
pytest
```

## Observações

-   Os exemplos de JSON deste documento são ilustrativos e devem ser
    implementados respeitando os nomes dos campos e os códigos HTTP
    definidos.
-   A especificação não define um formato obrigatório para o corpo das
    respostas de erro. É recomendável padronizar as mensagens de erro em
    JSON.
-   Para evitar problemas de precisão em cálculos monetários,
    recomenda-se utilizar `Decimal` em vez de `float` na lógica de
    preços e subtotais.
-   A persistência dos dados (memória ou banco de dados) deve ser
    definida na implementação. Se for utilizado armazenamento em
    memória, os dados poderão ser perdidos quando a aplicação for
    encerrada.
