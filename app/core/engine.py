import io
import os
import zipfile
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape

class GenerationEngine:
    """Renders source files from templates and bundles them into an in-memory zip."""

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
        return self.env.get_template("base_models.txt").render(
            project_name=schema_data.get("project_name"),
            entities=schema_data.get("entities", [])
        )

    def render_security(self, schema_data: Dict[str, Any]) -> str:
        return self.env.get_template("base_security.txt").render(
            project_name=schema_data.get("project_name")
        )

    def render_repository(self, entity: Dict[str, Any]) -> str:
        return self.env.get_template("base_repositories.txt").render(entity=entity)

    def render_service(self, entity: Dict[str, Any]) -> str:
        return self.env.get_template("base_services.txt").render(entity=entity)

    def render_routes(self, entity: Dict[str, Any], include_auth: bool) -> str:
        return self.env.get_template("base_routes.txt").render(entity=entity, include_auth=include_auth)

    def render_app_init(self, schema_data: Dict[str, Any]) -> str:
        return self.env.get_template("base_app_init.txt").render(
            project_name=schema_data.get("project_name"),
            entities=schema_data.get("entities", [])
        )

    def render_entrypoint(self) -> str:
        return self.env.get_template("base_entrypoint.txt").render()

    def render_requirements(self) -> str:
        return self.env.get_template("base_requirements.txt").render()

    def generate_project_files(self, schema_data: Dict[str, Any]) -> Dict[str, str]:
        """Maps target relative file paths to their rendered text content."""
        manifest = {}
        include_auth = schema_data.get("include_auth", True)
        proj_name = schema_data.get("project_name", "app")

        # 1. Root-level runtime files
        manifest["run.py"] = self.render_entrypoint()
        manifest["requirements.txt"] = self.render_requirements()
        manifest[".env"] = f"SECRET_KEY=dev-secret-key-change-me\nPORT=5000\nDATABASE_URL=postgresql://postgres:postgres@localhost:5432/{proj_name.lower()}_db\n"
        manifest["app/__init__.py"] = self.render_app_init(schema_data)

        # 2. Shared core modules
        manifest["app/models.py"] = self.render_models(schema_data)
        if include_auth:
            manifest["app/security.py"] = self.render_security(schema_data)

        # 3. 3-tier modules per entity
        for entity in schema_data.get("entities", []):
            module_name = entity["name"].lower()
            base_path = f"app/modules/{module_name}"
            manifest[f"{base_path}/__init__.py"] = ""
            manifest[f"{base_path}/repositories.py"] = self.render_repository(entity)
            manifest[f"{base_path}/services.py"] = self.render_service(entity)
            manifest[f"{base_path}/routes.py"] = self.render_routes(entity, include_auth)

        return manifest

    def generate_zip_buffer(self, schema_data: Dict[str, Any]) -> io.BytesIO:
        """
        Compresses all rendered files into an in-memory ZIP archive.
        Returns a seeked BytesIO stream ready to be transferred over HTTP.
        """
        file_manifest = self.generate_project_files(schema_data)
        zip_buffer = io.BytesIO()

        # Write each file string into the archive as bytes
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for filepath, content in file_manifest.items():
                zf.writestr(filepath, content)

        # Rewind read pointer to the start so Flask reads from byte 0
        zip_buffer.seek(0)
        return zip_buffer