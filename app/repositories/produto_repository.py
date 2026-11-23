from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional


@dataclass
class Produto:
    codigo: int
    preco: Decimal
    estoque: int = 0

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "preco": float(self.preco),
            "estoque": self.estoque,
        }


class ProdutoRepository:
    def __init__(self) -> None:
        self._produtos: Dict[int, Produto] = {}

    def existe(self, codigo: int) -> bool:
        return codigo in self._produtos

    def buscar_por_codigo(self, codigo: int) -> Optional[Produto]:
        return self._produtos.get(codigo)

    def salvar(self, produto: Produto) -> Produto:
        self._produtos[produto.codigo] = produto
        return produto