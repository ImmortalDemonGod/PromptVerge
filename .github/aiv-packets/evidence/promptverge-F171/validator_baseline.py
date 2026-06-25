"""
Provides a utility function to validate document objects against their Pydantic schemas.
"""

from pydantic import BaseModel
from jsonschema import validate, ValidationError

def validate_document(doc_object: BaseModel) -> bool:
    """
    Validates a Pydantic model instance against its own schema.

    Args:
        doc_object: An instance of a Pydantic BaseModel.

    Returns:
        True if the object is valid, False otherwise.
    """
    try:
        # The .model_json_schema() method generates the JSON schema for the model
        schema = doc_object.model_json_schema()
        # The .model_dump() method creates a dictionary representation of the object
        instance = doc_object.model_dump()
        validate(instance=instance, schema=schema)
        return True
    except ValidationError:
        return False
