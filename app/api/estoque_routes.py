from flask import Blueprint, jsonify, request

from app.services.estoque_service import (
    DadosInvalidosError,
    EstoqueService,
    ProdutoJaExisteError,
    ProdutoNaoEncontradoError,
)


def _parse_codigo(codigo_raw: str) -> int:
    if codigo_raw.isascii() and (
        codigo_raw.isdigit() or (codigo_raw.startswith("-") and codigo_raw[1:].isdigit())
    ):
        return int(codigo_raw)
    raise DadosInvalidosError("O campo 'codigo' deve ser um número inteiro.")


def create_estoque_blueprint(service: EstoqueService) -> Blueprint:
    estoque_bp = Blueprint("estoque", __name__)

    # Cadastro de produto:
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

    # Busca de produto / consulta de estoque:
    @estoque_bp.get("/loja/produto/<codigo>/estoque")
    def consultar_estoque(codigo):
        try:
            codigo_int = _parse_codigo(codigo)
            produto = service.buscar_produto(codigo_int)
        except DadosInvalidosError as exc:
            return jsonify({"erro": str(exc)}), 400
        except ProdutoNaoEncontradoError as exc:
            return jsonify({"erro": str(exc)}), 404

        return jsonify({
            "codigo": produto.codigo,
            "estoque": produto.estoque,
        }), 200

    # Entrada de estoque:
    @estoque_bp.put("/loja/produto/<codigo>/entrada")
    def entrada_estoque(codigo):
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            return jsonify({"erro": "Corpo da requisição deve ser um JSON válido."}), 400

        if "quantidade" not in dados:
            return jsonify({"erro": "O campo 'quantidade' é obrigatório."}), 400

        try:
            codigo_int = _parse_codigo(codigo)
            produto = service.entrada_estoque(codigo_int, dados["quantidade"])
        except DadosInvalidosError as exc:
            return jsonify({"erro": str(exc)}), 400
        except ProdutoNaoEncontradoError as exc:
            return jsonify({"erro": str(exc)}), 404

        return jsonify({
            "codigo": produto.codigo,
            "estoque": produto.estoque,
        }), 200

    # Saída de estoque:
    @estoque_bp.put("/loja/produto/<codigo>/saida")
    def saida_estoque(codigo):
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            return jsonify({"erro": "Corpo da requisição deve ser um JSON válido."}), 400

        if "quantidade" not in dados:
            return jsonify({"erro": "O campo 'quantidade' é obrigatório."}), 400

        try:
            codigo_int = _parse_codigo(codigo)
            produto = service.saida_estoque(codigo_int, dados["quantidade"])
        except DadosInvalidosError as exc:
            return jsonify({"erro": str(exc)}), 400
        except ProdutoNaoEncontradoError as exc:
            return jsonify({"erro": str(exc)}), 404

        return jsonify({
            "codigo": produto.codigo,
            "estoque": produto.estoque,
        }), 200

    return estoque_bp