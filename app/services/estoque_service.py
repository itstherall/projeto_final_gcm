from decimal import Decimal
from typing import Optional

from app.repositories.produto_repository import Produto, ProdutoRepository


class DadosInvalidosError(ValueError):
    """Lançada quando algum campo obrigatório está ausente ou tem tipo/valor inválido."""


class ProdutoJaExisteError(Exception):
    """Lançada ao tentar cadastrar um produto com código já existente."""


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