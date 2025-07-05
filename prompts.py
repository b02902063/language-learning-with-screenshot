class PromptFactory:
    def create_prompt(self, target_lang: str) -> str:
        """Prompt for explaining given terms."""
        raise NotImplementedError

    def create_identify_prompt(self, target_lang: str) -> str:
        """Prompt for extracting terms from an image."""
        raise NotImplementedError


class EnglishPromptFactory(PromptFactory):
    def create_prompt(self, target_lang: str) -> str:
        return (
            "You are a language tutor. Provide detailed explanations in English "
            "for the given "
            f"{target_lang} vocabulary and grammar following the provided schema."
        )

    def create_identify_prompt(self, target_lang: str) -> str:
        return (
            "You are a language tutor. Analyze the text in the image and list all "
            f"{target_lang} vocabulary words and grammar points. Group them by JLPT "
            "level N1 to N5 following the provided schema."
        )


class ChinesePromptFactory(PromptFactory):
    def create_prompt(self, target_lang: str) -> str:
        return (
f"""
你是{target_lang}學習資料的 JSON 產生器，請根據使用者給定的單字（vocabs）和文法（grammars）清單，
依照下方 JSON Schema 格式，產生完整的 JSON 結果。

請正確填寫 schema 中所有 required 欄位，非required欄位也盡可能填寫，並依照 description 說明合理填值。
只回傳符合該 schema 的 JSON，不需要額外說明文字。
"""
        )

    def create_identify_prompt(self, target_lang: str) -> str:
        return (
            f"請分析圖片中的{target_lang}文字，僅列出出現的單字與文法，依JLPT N1到N5分類，照結構回傳。"
        )


def get_prompt_factory(language: str) -> PromptFactory:
    return ChinesePromptFactory() if language.startswith("zh") else EnglishPromptFactory()

