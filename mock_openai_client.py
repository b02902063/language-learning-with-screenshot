# Mock OpenAI client for test mode
from typing import Dict, List

import openai_client

MOCK_IDENTIFY_RESPONSE = {
    "N1": None,
    "N2": {"vocabulary": ["絡まる"], "grammar": ["〜わけではない"]},
    "N3": None,
    "N4": None,
    "N5": {"vocabulary": ["綺麗"], "grammar": []},
}

# Detailed vocabulary and grammar items as returned by deliver_report
# (ITEM_SCHEMA)
MOCK_ITEM_RESPONSE = {
    "vocabulary": [
        {
            "word": "絡まる",
            "reading": "からまる",
                "definition": "東西纏繞在一起，打結。也可比喻事情或人際變得複雜難解。",
                "pos": {"label": "動詞", "subtype": "自五"},
                "conjugation": {
                    "forms": ["未然形", "連用形", "終止形", "連體形", "仮定形", "命令形"],
                    "examples": [
                        {"form": "絡まらない", "usage": "未然形"},
                        {"form": "絡まりました", "usage": "連用形"},
                        {"form": "絡まる", "usage": "終止形"},
                        {"form": "絡まる糸", "usage": "連體形"},
                        {"form": "絡まれば", "usage": "仮定形"},
                        {"form": "絡まれ", "usage": "命令形"},
                    ],
                },
                "transitivity": {
                    "intransitive": {
                        "word": "絡まる",
                        "reading": "からまる",
                        "type": "自五",
                    },
                    "transitive": {
                        "word": "絡める",
                        "reading": "からめる",
                        "type": "他下一",
                    },
                },
                "related": [
                    {
                        "word": "もつれる",
                        "reading": "もつれる",
                        "pos": "動詞",
                        "subtype": "自下一",
                        "definition": "亂成一團，打結；也可比喻人際關係混亂。",
                        "difference": "比絡まる更亂、更模糊。",
                    }
                ],
                "examples": [
                    {
                        "target_language": "髪の毛がブラシに絡まってしまった。",
                        "user_language": "頭髮纏在梳子上了。",
                    },
                    {
                        "target_language": "人間関係が複雑に絡まっていて、簡単には解決できない。",
                        "user_language": "人際關係錯綜複雜，無法輕易解決。",
                    },
                ],
            },
            {
                "word": "綺麗",
                "reading": "きれい",
                "definition": "漂亮、美麗、整齊、乾淨。令人感覺舒適美觀。",
                "pos": {"label": "形動", "subtype": "ダナニ"},
                "conjugation": {
                    "forms": ["だ", "な", "に"],
                    "examples": [
                        {"form": "綺麗だ", "usage": "終止形"},
                        {"form": "綺麗な景色", "usage": "連體形"},
                        {"form": "綺麗に掃除する", "usage": "副詞形"},
                    ],
                },
                "transitivity": {"intransitive": None, "transitive": None},
                "related": [
                    {
                        "word": "美しい",
                        "reading": "うつくしい",
                        "pos": "形",
                        "subtype": None,
                        "definition": "美麗、高雅，常用於景色或抽象美。",
                        "difference": "綺麗更口語；美しい更正式文藝。",
                    },
                    {
                        "word": "清潔",
                        "reading": "せいけつ",
                        "pos": "形動",
                        "subtype": "ダナニ",
                        "definition": "乾淨整潔，沒有汙垢。",
                        "difference": "偏向衛生感而非審美。",
                    },
                ],
                "examples": [
                    {
                        "target_language": "この花はとても綺麗だ。",
                        "user_language": "這朵花非常漂亮。",
                    },
                    {
                        "target_language": "部屋を綺麗に掃除した。",
                        "user_language": "把房間打掃得很乾淨。",
                    },
                ],
            },
        ],
    "grammar": [
            {
                "grammar_point": "〜わけではない",
                "structure": [
                    "動詞普通形 + わけではない",
                    "い形容詞 + わけではない",
                    "な形容詞 + な + わけではない",
                    "名詞 + の + わけではない",
                ],
                "definition": "並非全然是……；並不是說……（用於否定推論、誤解或一般認知）",
                "usage_note": "常用來糾正誤解，語氣柔和，不是強烈否定，而是針對部分情況例外。",
                "equivalent_expressions": [
                    {
                        "expression": "〜というわけではない",
                        "difference": "語氣更強烈、書面感較強",
                    },
                    {
                        "expression": "〜とは限らない",
                        "difference": "表示不一定、不是全部，語意更接近可能性",
                    },
                ],
                "examples": [
                    {
                        "target_language": "毎日運動しているが、健康なわけではない。",
                        "user_language": "雖然每天運動，但並不代表我很健康。",
                    },
                    {
                        "target_language": "日本人がみんな寿司が好きなわけではない。",
                        "user_language": "並不是所有日本人都喜歡壽司。",
                    },
                ],
                "tags": ["否定", "婉轉語氣", "糾正誤解"],
                "related_vocabulary": [
                    {
                        "word": "限る",
                        "reading": "かぎる",
                        "definition": "限制、侷限（動詞）",
                        "relation": "用於「〜とは限らない」中",
                    }
                ],
            }
        ],
}

# Final mock result for analyze_image following RESPONSE_SCHEMA
MOCK_ANALYZE_RESPONSE = {
    "N1": {"vocabulary": [], "grammar": []},
    "N2": MOCK_ITEM_RESPONSE,
    "N3": {"vocabulary": [], "grammar": []},
    "N4": {"vocabulary": [], "grammar": []},
    "N5": {"vocabulary": [], "grammar": []},
}


def mock_identify_terms(img_b64: str, factory, target_lang: str, api_key: str) -> Dict:
    """Return fixed identify response for testing."""
    return MOCK_IDENTIFY_RESPONSE


def mock_fetch_details(vocab: List[str], grammar: List[str], factory, target_lang: str, api_key: str) -> Dict:
    """Return fixed detail response for testing."""
    return MOCK_ITEM_RESPONSE


def analyze_image(title: str, target_lang: str, report_lang: str, api_key: str) -> Dict:
    """Run openai_client.analyze_image using mock functions."""
    return openai_client.analyze_image(
        title,
        target_lang,
        report_lang,
        api_key,
        identify_func=mock_identify_terms,
        fetch_func=mock_fetch_details,
    )
