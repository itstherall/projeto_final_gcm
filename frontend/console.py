import json
import os
from urllib import error, parse, request

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")


def _parse_int(valor: str):
    valor = valor.strip()
    try:
        return int(valor)
    except ValueError:
        return valor


def _parse_float(valor: str):
    valor = valor.strip().replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return valor


def fazer_requisicao(metodo: str, caminho: str, payload: dict | None = None) -> tuple[int | None, dict]:
    url = f"{BASE_URL}{caminho}"
    dados = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        dados = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=dados, headers=headers, method=metodo)

    try:
        with request.urlopen(req, timeout=10) as resposta:
            corpo = resposta.read().decode("utf-8", errors="replace")
            return resposta.status, json.loads(corpo) if corpo else {}
    except error.HTTPError as exc:
        corpo = exc.read().decode("utf-8", errors="replace")
        try:
            conteudo = json.loads(corpo) if corpo else {}
        except json.JSONDecodeError:
            conteudo = {"erro": corpo or exc.reason}
        return exc.code, conteudo
    except error.URLError:
        return None, {
            "erro": f"Não foi possível conectar à API em {BASE_URL}. Verifique se 'python run.py' está em execução."
        }


def exibir_erro(status: int | None, dados: dict) -> None:
    mensagem = dados.get("erro", "Erro inesperado ao comunicar com a API.")
    if status is None:
        print(f"\n[ERRO DE CONEXÃO] {mensagem}")
    else:
        print(f"\n[ERRO HTTP {status}] {mensagem}")


def cadastrar_produto() -> None:
    print("\n--- Cadastrar Produto ---")
    codigo = _parse_int(input("Código do produto: "))
    preco = _parse_float(input("Preço do produto: "))

    status, dados = fazer_requisicao(
        "POST",
        "/loja/produto",
        {"codigo": codigo, "preco": preco},
    )

    if status == 201:
        print(f"\n[SUCESSO - HTTP {status}] Produto cadastrado:")
        print(f"  Código : {dados['codigo']}")
        print(f"  Preço  : R$ {dados['preco']:.2f}")
        print(f"  Estoque: {dados['estoque']}")
    else:
        exibir_erro(status, dados)


def consultar_estoque() -> None:
    print("\n--- Consultar Estoque ---")
    codigo_raw = input("Código do produto: ").strip()
    if not codigo_raw:
        print("\n[AVISO] Informe o código do produto.")
        return

    codigo_url = parse.quote(codigo_raw, safe="")
    status, dados = fazer_requisicao("GET", f"/loja/produto/{codigo_url}/estoque")

    if status == 200:
        print(f"\n[SUCESSO - HTTP {status}] Estoque atual:")
        print(f"  Código : {dados['codigo']}")
        print(f"  Estoque: {dados['estoque']}")
    else:
        exibir_erro(status, dados)


def movimentar_estoque(tipo: str) -> None:
    titulo = "Entrada de Estoque" if tipo == "entrada" else "Saída de Estoque"
    print(f"\n--- {titulo} ---")
    codigo_raw = input("Código do produto: ").strip()
    if not codigo_raw:
        print("\n[AVISO] Informe o código do produto.")
        return

    quantidade = _parse_int(input("Quantidade: "))
    codigo_url = parse.quote(codigo_raw, safe="")

    status, dados = fazer_requisicao(
        "PUT",
        f"/loja/produto/{codigo_url}/{tipo}",
        {"quantidade": quantidade},
    )

    if status == 200:
        print(f"\n[SUCESSO - HTTP {status}] {titulo} registrada:")
        print(f"  Código      : {dados['codigo']}")
        print(f"  Novo estoque: {dados['estoque']}")
    else:
        exibir_erro(status, dados)


def realizar_venda() -> None:
    print("\n--- Realizar Venda ---")
    print("Informe os itens da venda (deixe o código em branco para concluir):")

    itens = []
    while True:
        codigo_raw = input(f"  Item {len(itens) + 1} - Código do produto: ").strip()
        if not codigo_raw:
            break

        quantidade = _parse_int(input(f"  Item {len(itens) + 1} - Quantidade: "))
        itens.append({"codigo": _parse_int(codigo_raw), "quantidade": quantidade})

    status, dados = fazer_requisicao("POST", "/loja/venda", {"itens": itens})

    if status == 201:
        print(f"\n[SUCESSO - HTTP {status}] Venda realizada:")
        for item in dados["itens"]:
            print(
                f"  Produto {item['codigo']} | Qtd: {item['quantidade']} | "
                f"Subtotal: R$ {item['subtotal']:.2f} | Estoque restante: {item['estoque']}"
            )
        print(f"  TOTAL DA VENDA: R$ {dados['total']:.2f}")
    else:
        exibir_erro(status, dados)


def exibir_menu() -> None:
    print("\n====================================")
    print("   SISTEMA DE CONTROLE DE ESTOQUE   ")
    print("====================================")
    print("1 - Cadastrar produto")
    print("2 - Consultar estoque")
    print("3 - Entrada de estoque")
    print("4 - Saída de estoque")
    print("5 - Realizar venda")
    print("0 - Sair")


def main() -> None:
    opcoes = {
        "1": cadastrar_produto,
        "2": consultar_estoque,
        "3": lambda: movimentar_estoque("entrada"),
        "4": lambda: movimentar_estoque("saida"),
        "5": realizar_venda,
    }

    while True:
        exibir_menu()
        escolha = input("\nEscolha uma opção: ").strip()

        if escolha == "0":
            print("Encerrando o sistema.")
            break

        acao = opcoes.get(escolha)
        if acao is None:
            print("\n[AVISO] Opção inválida. Escolha um número entre 0 e 5.")
            continue

        acao()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrando o sistema.")