NAME_LIST_SCHEMA = {
    "type": "object",
    "description": "從圖片中擷取出的日文單字與文法名稱清單，僅包含名稱，未附加詳細說明。",
    "properties": {
        "vocabulary": {
            "type": "array",
            "description": "從圖片辨識出的單字名稱清單。若圖片上為活用形式，請還原為原形。例如：圖片為『食べました』時，請標記為『食べる』。",
            "items": {
                "type": "string",
                "description": "使用日文單字的原形名稱。例如：食べる、綺麗、学生。"
            }
        },
        "grammar": {
            "type": "array",
            "description": "從圖片辨識出的文法點清單。請使用完整文法形式，若為接續型態，使用『〜』標示接續方向。例如：『〜わけではない』『〜ながら』『〜たばかり』。",
            "items": {
                "type": "string",
                "description": "文法點的名稱，包含『〜』等接續標記。例如：〜わけではない、〜つつ、〜ながら。"
            }
        }
    },
    "required": ["vocabulary", "grammar"]
}

ITEM_SCHEMA = {
  "type": "object",
  "description": "包含日文單字 (vocabulary) 和文法 (grammar) 的完整分析資料。",
  "properties": {
    "vocabulary": {
      "type": "array",
      "description": "單字清單，每個元素為一個單字的詳細資訊。",
      "items": {
        "type": "object",
        "properties": {
          "word": {"type": "string", "description": "單字（日文），例如『食べる』。"},
          "reading": {"type": "string", "description": "單字的假名讀音，例如『たべる』。"},
          "definition": {"type": "string", "description": "單字的中文釋義，例如『吃』。"},
          "pos": {
            "type": "object",
            "description": "詞性資訊。",
            "properties": {
              "label": {"type": "string", "description": "詞性種類，例如：動詞、い形容詞、形動、名詞、副詞、接續詞、助詞、助動詞、感動詞、連體詞等。"},
              "subtype": {"type": ["string", "null"], "description": "詞性細分類，例如：自五、他上一、名詞サ變、形容動詞ナ型、副詞タルト、ダナニ，無則為 null。"}
            },
            "required": ["label"]
          },
          "conjugation": {
            "anyOf": [
              {
                "type": "object",
                "description": "活用資訊，若不可活用則為 null。",
                "properties": {
                  "forms": {"type": "array", "items": {"type": "string"}, "description": "詞形名稱列表，例如：基本形、未然形、連用形、終止形、連體形、假定形、命令形。"},
                  "examples": {
                    "type": "array",
                    "description": "詞形範例，每個範例包含實際變化後的形式與用法名稱。",
                    "items": {
                      "type": "object",
                      "properties": {
                        "form": {"type": "string", "description": "實際變化後的單字形式，可在括號補足語境，例如：食べ(ない)、綺麗に(掃除する)。"},
                        "usage": {"type": "string", "description": "該詞形的名稱，例如：基本形、連體形等。"}
                      },
                      "required": ["form", "usage"]
                    }
                  }
                },
                "required": ["forms"]
              },
              {"type": "null", "description": "不可活用時為 null。"}
            ]
          },
          "transitivity": {
            "anyOf": [
              {
                "type": "object",
                "description": "動詞的自他分類資訊。非動詞則為 null。",
                "properties": {
                  "intransitive": {
                    "type": ["object", "null"],
                    "description": "自動詞資訊，包含 word、reading、type（通常為『自動詞』）。",
                    "properties": {
                      "word": {"type": "string"},
                      "reading": {"type": "string"},
                      "type": {"type": "string"}
                    },
                    "required": ["word", "reading", "type"]
                  },
                  "transitive": {
                    "type": ["object", "null"],
                    "description": "他動詞資訊，包含 word、reading、type（通常為『他動詞』）。",
                    "properties": {
                      "word": {"type": "string"},
                      "reading": {"type": "string"},
                      "type": {"type": "string"}
                    },
                    "required": ["word", "reading", "type"]
                  }
                }
              },
              {"type": "null", "description": "無自他分類時為 null。"}
            ]
          },
          "related": {
            "type": "array",
            "description": "相關單字清單，列出與本單字意思相近、對立或易混淆的詞彙。",
            "items": {
              "type": "object",
              "properties": {
                "word": {"type": "string", "description": "相關單字（日文）。"},
                "reading": {"type": "string", "description": "相關單字的假名。"},
                "pos": {"type": "string", "description": "相關單字的詞性。"},
                "subtype": {"type": ["string", "null"], "description": "相關單字的細分類，無則為 null。"},
                "definition": {"type": "string", "description": "相關單字的中文釋義。"},
                "difference": {"type": "string", "description": "與本單字的差異說明。"}
              },
              "required": ["word", "reading", "pos", "subtype", "definition", "difference"]
            }
          },
          "examples": {
            "type": "array",
            "description": "該單字的例句清單。",
            "items": {
              "type": "object",
              "properties": {
                "target_language": {"type": "string", "description": "日文例句。"},
                "user_language": {"type": "string", "description": "中文翻譯。"}
              },
              "required": ["target_language", "user_language"]
            }
          }
        },
        "required": ["word", "reading", "definition", "pos", "related", "examples"]
      }
    },
    "grammar": {
      "type": "array",
      "description": "文法點清單，每個元素為一個文法的詳細資訊。",
      "items": {
        "type": "object",
        "properties": {
          "grammar_point": {"type": "string", "description": "文法點名稱，例如：『～ながら』。"},
          "structure": {"type": "array", "items": {"type": "string"}, "description": "文法結構組成，例如：[\"動詞ます形\", \"ながら\"]。"},
          "definition": {"type": "string", "description": "文法的中文釋義，例如：『一邊...一邊...』。"},
          "usage_note": {"type": "string", "description": "使用上的注意事項，可留空。"},
          "equivalent_expressions": {
            "type": "array",
            "description": "近義文法列表，列出與本文法意思相近但略有差異的其他表達。",
            "items": {
              "type": "object",
              "properties": {
                "expression": {"type": "string", "description": "近義文法的名稱，例如：『～つつ』。"},
                "difference": {"type": "string", "description": "與本文法的差異說明。"}
              },
              "required": ["expression", "difference"]
            }
          },
          "examples": {
            "type": "array",
            "description": "該文法點的例句清單。",
            "items": {
              "type": "object",
              "properties": {
                "target_language": {"type": "string", "description": "日文例句。"},
                "user_language": {"type": "string", "description": "中文翻譯。"}
              },
              "required": ["target_language", "user_language"]
            }
          },
          "tags": {"type": "array", "items": {"type": "string"}, "description": "自訂分類標籤，例如：『同時動作』『口語』等。"},
          "related_vocabulary": {
            "type": "array",
            "description": "該文法常搭配的單字清單。",
            "items": {
              "type": "object",
              "properties": {
                "word": {"type": "string", "description": "單字（日文）。"},
                "reading": {"type": "string", "description": "單字的假名。"},
                "definition": {"type": "string", "description": "單字的中文釋義。"},
                "relation": {"type": "string", "description": "與文法的搭配範例，例如：『勉強しながら......』，可用『......』表示省略部分。"}
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


IDENTIFY_RESPONSE_SCHEMA = {
    "type": "object",
    "description": (
        "根據圖片分析出的日文單字與文法並做出等級分類結果。"
        "每個單字或文法只能屬於一個等級，不能同時歸屬於多個等級。"
    ),
    "properties": {
        "N1": {
            "anyOf": [NAME_LIST_SCHEMA, {"type": "null"}],
            "description": (
                "N1 等級：理解在廣泛場合中使用的高難度日語，"
                "包括邏輯性較強、抽象度高的論說文、評論等文章內容，"
                "以及自然語速下的講座、新聞等中，複雜的內容結構與細節。"
            ),
        },
        "N2": {
            "anyOf": [NAME_LIST_SCHEMA, {"type": "null"}],
            "description": (
                "N2 等級：理解日常及更廣泛場景中使用的較高階日語，"
                "能閱讀報紙、雜誌等較正式的文章，理解清晰的論旨，"
                "並能聽懂接近自然語速的會話、新聞等，掌握其要旨與細節。"
            ),
        },
        "N3": {
            "anyOf": [NAME_LIST_SCHEMA, {"type": "null"}],
            "description": (
                "N3 等級：理解日常生活中較常見的日語，"
                "能閱讀較具體的敘述，或在日常場景看到的稍高難度文章，"
                "聽懂接近自然語速的日常會話，理解其內容與人物關係。"
            ),
        },
        "N4": {
            "anyOf": [NAME_LIST_SCHEMA, {"type": "null"}],
            "description": (
                "N4 等級：理解基本日語，"
                "能閱讀日常生活中使用基本詞彙、漢字所寫的親切主題的文章，"
                "聽懂在日常生活常見場景中稍慢語速的對話，掌握其大致內容。"
            ),
        },
        "N5": {
            "anyOf": [NAME_LIST_SCHEMA, {"type": "null"}],
            "description": (
                "N5 等級：理解基礎日語，"
                "能閱讀平假名、片假名及簡單漢字書寫的固定用語與文章，"
                "聽懂在教室、生活周邊等場合中，慢速簡短的對話，獲取基本資訊。"
            ),
        },
    },
    "required": ["N1", "N2", "N3", "N4", "N5"],
    "additionalProperties": False,
}