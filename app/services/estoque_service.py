from decimal import Decimal
from typing import Optional

from app.repositories.produto_repository import Produto, ProdutoRepository


class DadosInvalidosError(ValueError):
    """Lançada quando algum campo obrigatório está ausente ou tem tipo/valor inválido."""


class ProdutoJaExisteError(Exception):
    """Lançada ao tentar cadastrar um produto com código já existente."""

class ProdutoNaoEncontradoError(Exception):
    """Lançada quando um produto não é encontrado no repositório."""


class EstoqueService:
    def __init__(self, repository: Optional[ProdutoRepository] = None) -> None:
        self._repository = repository if repository is not None else ProdutoRepository()

    def cadastrar_produto(self, codigo: object, preco: object) -> Produto:
        if not isinstance(codigo, int) or isinstance(codigo, bool):
            raise DadosInvalidosError("O campo 'codigo' deve ser um número inteiro.")

        if isinstance(preco, bool) or not isinstance(preco, (int, float, Decimal)):
            raise DadosInvalidosError("O campo 'preco' deve ser um número decimal válido.")

        preco_decimal = preco if isinstance(preco, Decimal) else Decimal(str(preco))
        if not preco_decimal.is_finite() or preco_decimal < 0:
            raise DadosInvalidosError("O campo 'preco' deve ser um número decimal válido.")

        if self._repository.existe(codigo):
            raise ProdutoJaExisteError(f"Já existe produto com o código {codigo}.")

        produto = Produto(codigo=codigo, preco=preco_decimal, estoque=0)
        return self._repository.salvar(produto)

    # BUSCA PRODUTO:
    def buscar_produto(self, codigo: object) -> Produto:
        if not isinstance(codigo, int) or isinstance(codigo, bool):
            raise DadosInvalidosError("O campo 'codigo' deve ser um número inteiro.")

        produto = self._repository.buscar_por_codigo(codigo)
        if produto is None:
            raise ProdutoNaoEncontradoError("Produto não encontrado.")

        return produto

    #ENTRADA PRODUTO:
    def entrada_estoque(self, codigo: object, quantidade: object) -> Produto:

        #Validação dos campos 'codigo' e 'quantidade':
        if not isinstance(codigo, int) or isinstance(codigo, bool):
            raise DadosInvalidosError("O campo 'codigo' deve ser um número inteiro.")

        if not isinstance(quantidade, int) or isinstance(quantidade, bool):
            raise DadosInvalidosError("O campo 'quantidade' deve ser um número inteiro.")

        if quantidade <= 0:
            raise DadosInvalidosError("O campo 'quantidade' deve ser um número inteiro positivo.")

        produto = self._repository.buscar_por_codigo(codigo)

        if produto is None:
            raise ProdutoNaoEncontradoError(f"Produto com código {codigo} não encontrado.")

        produto.estoque += quantidade
        return self._repository.salvar(produto) 


    #SAIDA PRODUTO:
    def saida_estoque(self, codigo: object, quantidade: object) -> Produto:
        
        #Validação dos campos 'codigo' e 'quantidade':
        if not isinstance(codigo, int) or isinstance(codigo, bool):
            raise DadosInvalidosError("O código deve ser um número inteiro.")

        if not isinstance(quantidade, int) or isinstance(quantidade, bool):
            raise DadosInvalidosError("A quantidade deve ser um número inteiro.")

        if quantidade <= 0:
            raise DadosInvalidosError("A quantidade deve ser maior que zero.")

        produto = self.buscar_produto(codigo)

        if produto.estoque < quantidade:
            raise DadosInvalidosError("Estoque insuficiente.")

        produto.estoque -= quantidade

        return self._repository.salvar(produto)

# REALIZAÇÃO DE VENDA:
    def realizar_venda(self, itens: object) -> dict:
        if not isinstance(itens, list) or len(itens) == 0:
            raise DadosInvalidosError("O campo 'itens' deve ser uma lista não vazia.")

        itens_validados = []
        for item in itens:
            if not isinstance(item, dict):
                raise DadosInvalidosError("Cada item da venda deve ser um objeto JSON válido.")

            if "codigo" not in item or "quantidade" not in item:
                raise DadosInvalidosError(
                    "Cada item deve conter os campos 'codigo' e 'quantidade'."
                )

            codigo = item["codigo"]
            quantidade = item["quantidade"]

            if not isinstance(codigo, int) or isinstance(codigo, bool):
                raise DadosInvalidosError("O campo 'codigo' deve ser um número inteiro.")

            if not isinstance(quantidade, int) or isinstance(quantidade, bool):
                raise DadosInvalidosError("O campo 'quantidade' deve ser um número inteiro.")

            if quantidade <= 0:
                raise DadosInvalidosError(
                    "O campo 'quantidade' deve ser um número inteiro positivo."
                )

            itens_validados.append((codigo, quantidade))

        produtos_por_codigo = {}
        quantidades_totais = {}
        for codigo, quantidade in itens_validados:
            if codigo not in produtos_por_codigo:
                produto = self._repository.buscar_por_codigo(codigo)
                if produto is None:
                    raise ProdutoNaoEncontradoError(
                        f"Produto com código {codigo} não encontrado."
                    )
                produtos_por_codigo[codigo] = produto

            quantidades_totais[codigo] = quantidades_totais.get(codigo, 0) + quantidade

        for codigo, quantidade_total in quantidades_totais.items():
            if produtos_por_codigo[codigo].estoque < quantidade_total:
                raise DadosInvalidosError(
                    f"Estoque insuficiente para o produto de código {codigo}."
                )

        total = Decimal("0")
        itens_resposta = []
        for codigo, quantidade in itens_validados:
            produto = produtos_por_codigo[codigo]
            produto.estoque -= quantidade
            self._repository.salvar(produto)

            subtotal = produto.preco * quantidade
            total += subtotal
            itens_resposta.append({
                "codigo": produto.codigo,
                "quantidade": quantidade,
                "subtotal": float(subtotal),
                "estoque": produto.estoque,
            })

        return {
            "total": float(total),
            "itens": itens_resposta,
        }