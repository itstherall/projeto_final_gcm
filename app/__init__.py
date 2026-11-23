def create_app():
    from flask import Flask

    from app.api.estoque_routes import create_estoque_blueprint
    from app.repositories.produto_repository import ProdutoRepository
    from app.services.estoque_service import EstoqueService

    app = Flask(__name__)
    app.json.sort_keys = False
    app.json.ensure_ascii = False

    repository = ProdutoRepository()
    service = EstoqueService(repository)

    app.register_blueprint(create_estoque_blueprint(service))

    return app