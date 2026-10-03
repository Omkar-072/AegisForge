import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any

class GenerationEngine:
    """
    Renders dynamic source code files from templates using validated schema dictionaries.
    """
    def __init__(self):
        template_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "templates")
        )
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render_models(self, schema_data: Dict[str, Any]) -> str:
        template = self.env.get_template("base_models.txt")
        return template.render(
            project_name=schema_data.get("project_name"),
            entities=schema_data.get("entities", [])
        )

    def render_security(self, schema_data: Dict[str, Any]) -> str:
        template = self.env.get_template("base_security.txt")
        return template.render(
            project_name=schema_data.get("project_name")
        )

    def render_repository(self, entity: Dict[str, Any]) -> str:
        template = self.env.get_template("base_repositories.txt")
        return template.render(entity=entity)

    def render_service(self, entity: Dict[str, Any]) -> str:
        template = self.env.get_template("base_services.txt")
        return template.render(entity=entity)

    def render_routes(self, entity: Dict[str, Any], include_auth: bool) -> str:
        template = self.env.get_template("base_routes.txt")
        return template.render(entity=entity, include_auth=include_auth)

    def generate_project_files(self, schema_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Orchestrates full code generation.
        Returns a mapping of target project relative paths to generated source code strings.
        """
        generated_manifest = {}
        include_auth = schema_data.get("include_auth", True)

        # 1. Global models & security
        generated_manifest["app/models.py"] = self.render_models(schema_data)
        if include_auth:
            generated_manifest["app/security.py"] = self.render_security(schema_data)

        # 2. Per-entity 3-tier modules
        for entity in schema_data.get("entities", []):
            module_name = entity["name"].lower()
            base_path = f"app/modules/{module_name}"
            
            generated_manifest[f"{base_path}/__init__.py"] = ""
            generated_manifest[f"{base_path}/repositories.py"] = self.render_repository(entity)
            generated_manifest[f"{base_path}/services.py"] = self.render_service(entity)
            generated_manifest[f"{base_path}/routes.py"] = self.render_routes(entity, include_auth)

        return generated_manifest

if __name__ == "__main__":
    from app.core.parser import SchemaParser

    mock_input = {
        "project_name": "AegisStore",
        "include_auth": True,
        "entities": [
            {
                "name": "User",
                "table_name": "users",
                "fields": [
                    {"name": "id", "type": "Integer", "primary_key": True},
                    {"name": "email", "type": "String", "unique": True, "nullable": False},
                    {"name": "is_active", "type": "Boolean", "nullable": False}
                ],
                "relationships": [
                    {"target_entity": "Order", "type": "one_to_many", "back_populates": "user"}
                ]
            },
            {
                "name": "Order",
                "table_name": "orders",
                "fields": [
                    {"name": "id", "type": "Integer", "primary_key": True},
                    {"name": "total_price", "type": "Float", "nullable": False},
                    {"name": "user_id", "type": "Integer", "foreign_key": "users.id", "nullable": False}
                ],
                "relationships": [
                    {"target_entity": "User", "type": "many_to_one", "back_populates": "orders"}
                ]
            }
        ]
    }

    parser = SchemaParser(mock_input)
    validated = parser.validate()

    engine = GenerationEngine()
    result = engine.generate_project_files(validated)

    print("Generated Files:", list(result.keys()))
    print("\n=== APP/SECURITY.PY SNIPPET ===")
    print("\n".join(result["app/security.py"].splitlines()[:25]))