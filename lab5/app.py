from __future__ import annotations

from flask import Flask, jsonify
from flask_restful import Api
from flasgger import Swagger

from resources import (
    AuthorListResource,
    AuthorResource,
    BookListResource,
    BookResource,
)
from storage import LibraryStore

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SWAGGER"] = {
        "title": "Library API",
        "uiversion": 3,
        "openapi": "3.0.3",
    }
    swagger_template = {
        "openapi": "3.0.3",
        "info": {"title": "Library API", "version": "1.0.0"},
        "paths": {},
        "components": {
            "schemas": {
                "AuthorCreate": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {"name": {"type": "string", "minLength": 1}},
                },
                "Author": {
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
                },
                "BookCreate": {
                    "type": "object",
                    "required": ["title", "author_id"],
                    "properties": {
                        "title": {"type": "string", "minLength": 1},
                        "author_id": {"type": "string"},
                        "year": {"type": "integer", "nullable": True},
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "BookUpdate": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "minLength": 1},
                        "author_id": {"type": "string"},
                        "year": {"type": "integer", "nullable": True},
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "Book": {
                    "type": "object",
                    "required": ["id", "title", "author_id", "year", "tags"],
                    "properties": {
                        "id": {"type": "string"},
                        "title": {"type": "string"},
                        "author_id": {"type": "string"},
                        "year": {"type": "integer", "nullable": True},
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                },
            }
        },
    }
    Swagger(app, template=swagger_template)

    store = LibraryStore()
    api = Api(app)
    api.add_resource(AuthorListResource, "/authors", resource_class_kwargs={"store": store})
    api.add_resource(AuthorResource, "/authors/<string:author_id>", resource_class_kwargs={"store": store})
    api.add_resource(BookListResource, "/books", resource_class_kwargs={"store": store})
    api.add_resource(BookResource, "/books/<string:book_id>", resource_class_kwargs={"store": store})

    @app.get("/")
    def root():
        return jsonify({"message": "ok", "docs": "/apidocs"})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app

app = create_app()

