ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "vocabulary": {
            "type": "array",
            "items": {
                "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "reading": {"type": "string"},
                            "definition": {"type": "string"},
                            "pos": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string"},
                                    "subtype": {"type": ["string", "null"]}
                                },
                                "required": ["label"]
                            },
                            "conjugation": {
                                "anyOf": [
                                    {
                                        "type": "object",
                                        "properties": {
                                            "forms": {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            },
                                            "examples": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "form": {"type": "string"},
                                                        "usage": {"type": "string"}
                                                    },
                                                    "required": ["form", "usage"]
                                                }
                                            }
                                        },
                                        "required": ["forms"]
                                    },
                                    {"type": "null"}
                                ]
                            },
                            "transitivity": {
                                "anyOf": [
                                    {
                                        "type": "object",
                                        "properties": {
                                            "intransitive": {
                                                "type": ["object", "null"],
                                                "properties": {
                                                    "word": {"type": "string"},
                                                    "reading": {"type": "string"},
                                                    "type": {"type": "string"}
                                                },
                                                "required": ["word", "reading", "type"]
                                            },
                                            "transitive": {
                                                "type": ["object", "null"],
                                                "properties": {
                                                    "word": {"type": "string"},
                                                    "reading": {"type": "string"},
                                                    "type": {"type": "string"}
                                                },
                                                "required": ["word", "reading", "type"]
                                            }
                                        }
                                    },
                                    {"type": "null"}
                                ]
                            },
                            "related": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "word": {"type": "string"},
                                        "reading": {"type": "string"},
                                        "pos": {"type": "string"},
                                        "subtype": {"type": ["string", "null"]},
                                        "definition": {"type": "string"},
                                        "difference": {"type": "string"}
                                    },
                                    "required": ["word", "definition"]
                                }
                            },
                            "examples": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "target_language": {"type": "string"},
                                        "user_language": {"type": "string"}
                                    },
                                    "required": ["target_language", "user_language"]
                                }
                            }
                        },
                        "required": [
                            "word",
                            "reading",
                            "definition",
                            "pos",
                            "related",
                            "examples",
                        ]
                    }
                },
        "grammar": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "grammar_point": {"type": "string"},
                    "structure": {"type": "array", "items": {"type": "string"}},
                    "definition": {"type": "string"},
                    "usage_note": {"type": "string"},
                    "equivalent_expressions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "expression": {"type": "string"},
                                "difference": {"type": "string"}
                            },
                            "required": ["expression", "difference"]
                        }
                    },
                    "examples": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "target_language": {"type": "string"},
                                "user_language": {"type": "string"}
                            },
                            "required": ["target_language", "user_language"]
                        }
                    },
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "related_vocabulary": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "reading": {"type": "string"},
                                "definition": {"type": "string"},
                                "relation": {"type": "string"}
                            },
                            "required": ["word", "definition"]
                        }
                    }
                },
                "required": ["grammar_point", "definition"]
            }
        }
    },
    "required": ["vocabulary", "grammar"]
}

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "N1": ITEM_SCHEMA,
        "N2": ITEM_SCHEMA,
        "N3": ITEM_SCHEMA,
        "N4": ITEM_SCHEMA,
        "N5": ITEM_SCHEMA,
    },
    "required": ["N1", "N2", "N3", "N4", "N5"],
    "additionalProperties": False,
}
