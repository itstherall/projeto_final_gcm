from flask import Blueprint, jsonify, request

from app.services.estoque_service import (
    DadosInvalidosError,
    EstoqueService,
    ProdutoJaExisteError,
    ProdutoNaoEncontradoError,
)


def create_estoque_blueprint(service: EstoqueService) -> Blueprint:
    estoque_bp = Blueprint("estoque", __name__)

    #Cadastro de produto Estoque:
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

    #Busca de produto Estoque:
    @estoque_bp.get("/loja/produto/<int:codigo>/estoque")
    def consultar_estoque(codigo):
        try:
            produto = service.buscar_produto(codigo)

        except ProdutoNaoEncontradoError as exc:
            return jsonify({"erro": str(exc)}), 404

        return jsonify({
        "codigo": produto.codigo,
        "estoque": produto.estoque
        }), 200

    #Entrada de estoque:
    @estoque_bp.post("/loja/estoque/<int:codigo>/entrada")
    def entrada_estoque():
        dados = request.get_json(silent=True)

        if not isinstance(dados, dict):
            return jsonify({"erro": "Corpo da requisição deve ser um JSON válido."}), 400

        if "codigo" not in dados or "quantidade" not in dados:
            return jsonify({"erro": "Os campos 'codigo' e 'quantidade' são obrigatórios."}), 400

        try:
            produto = service.entrada_estoque(
                dados["codigo"],
                dados["quantidade"]
            )
        except DadosInvalidosError as exc:
            return jsonify({"erro": str(exc)}), 400
        except ProdutoNaoEncontradoError as exc:
            return jsonify({"erro": str(exc)}), 404

        return jsonify(produto.to_dict()), 200

    #Saida de estoque:
    @estoque_bp.put("/loja/produto/<int:codigo>/saida")
    def saida_estoque(codigo):
        dados = request.get_json(silent=True)

        if not isinstance(dados, dict):
            return jsonify({"erro": "Corpo da requisição deve ser um JSON válido."}), 400

        if "quantidade" not in dados:
            return jsonify({"erro": "O campo 'quantidade' é obrigatório."}), 400

        try:
            produto = service.saida_estoque(
                codigo,
                dados["quantidade"]
            )

        except DadosInvalidosError as exc:
            return jsonify({"erro": str(exc)}), 400

        except ProdutoNaoEncontradoError as exc:
            return jsonify({"erro": str(exc)}), 404

        return jsonify({
            "codigo": produto.codigo,
            "estoque": produto.estoque
        }), 200


    
    return estoque_bp

