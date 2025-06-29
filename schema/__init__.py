from importlib import import_module
from typing import Tuple

# Map language codes to schema modules
_SCHEMAS = {
    'ja': 'schema.ja'
}

def get_schema(lang: str = 'ja') -> Tuple[dict, dict]:
    """Return ITEM_SCHEMA and IDENTIFY_RESPONSE_SCHEMA for given language."""
    module_name = _SCHEMAS.get(lang, 'schema.ja')
    module = import_module(module_name)
    return module.ITEM_SCHEMA, module.IDENTIFY_RESPONSE_SCHEMA
