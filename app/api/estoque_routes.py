from flask import Blueprint, jsonify, request

from app.services.estoque_service import (
    DadosInvalidosError,
    EstoqueService,
    ProdutoJaExisteError,
)


def create_estoque_blueprint(service: EstoqueService) -> Blueprint:
    estoque_bp = Blueprint("estoque", __name__)

    @estoque_bp.post("/loja/produto")
    def cadastrar_produto():
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            return jsonify({"erro": "Corpo da requisição deve ser um JSON válido."}), 400

        if "codigo" not in dados or "preco" not in dados:
            return jsonify({"erro": "Os campos 'codigo' e 'preco' são obrigatórios."}), 400

        try:
            produto = service.cadastrar_produto(dados["codigo"], dados["preco"])
        except DadosInvalidosError as exc:
            return jsonify({"erro": str(exc)}), 400
        except ProdutoJaExisteError as exc:
            return jsonify({"erro": str(exc)}), 409

        return jsonify(produto.to_dict()), 201

    return estoque_bp