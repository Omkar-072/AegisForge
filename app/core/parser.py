from typing import Dict, Any, List

class SchemaValidationError(Exception):
    """Custom exception raised when the schema validation fails."""
    pass

class SchemaParser:
    """
    Parses and validates schema input before passing it to the code generator.
    Ensures relational integrity and data type correctness.
    """
    
    SUPPORTED_TYPES = {"Integer", "String", "Float", "Boolean", "DateTime", "Text"}
    SUPPORTED_RELATIONSHIPS = {"one_to_one", "one_to_many", "many_to_one", "many_to_many"}

    def __init__(self, raw_schema: Dict[str, Any]):
        self.raw_schema = raw_schema
        self.entities = raw_schema.get("entities", [])
        self.project_name = raw_schema.get("project_name")

    def validate(self) -> Dict[str, Any]:
        """Runs the validation pipeline. Returns cleaned schema if valid, raises SchemaValidationError otherwise."""
        if not self.project_name or not isinstance(self.project_name, str):
            raise SchemaValidationError("Root schema missing valid 'project_name'.")

        if not self.entities or not isinstance(self.entities, list):
            raise SchemaValidationError("Schema must contain a non-empty 'entities' list.")

        entity_names = set()
        table_names = set()

        # Pass 1: Validate entity definitions & field consistency
        for entity in self.entities:
            name = entity.get("name")
            table = entity.get("table_name")

            if not name or not table:
                raise SchemaValidationError(f"Entity missing 'name' or 'table_name': {entity}")

            if name in entity_names:
                raise SchemaValidationError(f"Duplicate entity name detected: '{name}'.")
            if table in table_names:
                raise SchemaValidationError(f"Duplicate table_name detected: '{table}'.")

            entity_names.add(name)
            table_names.add(table)

            self._validate_fields(entity)

        # Pass 2: Cross-validate relationships against gathered entity names
        self._validate_relationships(entity_names)

        return self.raw_schema

    def _validate_fields(self, entity: Dict[str, Any]) -> None:
        fields = entity.get("fields", [])
        if not fields or not isinstance(fields, list):
            raise SchemaValidationError(f"Entity '{entity['name']}' must contain a non-empty 'fields' list.")

        has_primary_key = False
        field_names = set()

        for field in fields:
            f_name = field.get("name")
            f_type = field.get("type")

            if not f_name or not f_type:
                raise SchemaValidationError(f"Field missing 'name' or 'type' in entity '{entity['name']}'.")

            if f_name in field_names:
                raise SchemaValidationError(f"Duplicate field '{f_name}' in entity '{entity['name']}'.")
            field_names.add(f_name)

            if f_type not in self.SUPPORTED_TYPES:
                raise SchemaValidationError(
                    f"Unsupported type '{f_type}' in field '{f_name}'. Supported: {', '.join(self.SUPPORTED_TYPES)}"
                )

            if field.get("primary_key", False):
                has_primary_key = True

        if not has_primary_key:
            raise SchemaValidationError(f"Entity '{entity['name']}' must define at least one 'primary_key: true'.")

    def _validate_relationships(self, registered_entities: set) -> None:
        for entity in self.entities:
            relationships = entity.get("relationships", [])
            for rel in relationships:
                target = rel.get("target_entity")
                rel_type = rel.get("type")

                if not target or target not in registered_entities:
                    raise SchemaValidationError(
                        f"Relationship target '{target}' in entity '{entity['name']}' does not exist in schema."
                    )

                if rel_type not in self.SUPPORTED_RELATIONSHIPS:
                    raise SchemaValidationError(
                        f"Invalid relationship type '{rel_type}' in entity '{entity['name']}'. Supported: {', '.join(self.SUPPORTED_RELATIONSHIPS)}"
                    )

if __name__ == "__main__":
    test_payload = {
        "project_name": "demo_store",
        "entities": [
            {
                "name": "User",
                "table_name": "users",
                "fields": [
                    {"name": "id", "type": "Integer", "primary_key": True},
                    {"name": "email", "type": "String", "unique": True}
                ],
                "relationships": [
                    {"target_entity": "Profile", "type": "one_to_one"}
                ]
            },
            {
                "name": "Profile",
                "table_name": "profiles",
                "fields": [
                    {"name": "id", "type": "Integer", "primary_key": True},
                    {"name": "bio", "type": "Text"}
                ]
            }
        ]
    }

    parser = SchemaParser(test_payload)
    parsed = parser.validate()
    print("Validation Successful: Schema is ready for code generation!")