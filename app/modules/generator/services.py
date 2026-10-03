import io
from typing import Dict, Any, Tuple
from app.core.parser import SchemaParser
from app.core.engine import GenerationEngine

class GeneratorService:
    @staticmethod
    def build_zip_package(raw_schema: Dict[str, Any]) -> Tuple[io.BytesIO, str]:
        # 1. Parse and validate incoming structure
        parser = SchemaParser(raw_schema)
        validated_schema = parser.validate()

        # 2. Assemble in-memory zip
        engine = GenerationEngine()
        buffer = engine.generate_zip_buffer(validated_schema)

        project_name = validated_schema.get("project_name", "generated_api")
        filename = f"{project_name}.zip"

        return buffer, filename