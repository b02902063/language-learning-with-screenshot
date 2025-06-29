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
            f"請根據提供的{target_lang}單字與文法，以繁體中文輸出詳盡說明，並遵守結構。"
        )

    def create_identify_prompt(self, target_lang: str) -> str:
        return (
            f"請分析圖片中的{target_lang}文字，僅列出出現的單字與文法，依JLPT N1到N5分類，照結構回傳。"
        )


def get_prompt_factory(language: str) -> PromptFactory:
    return ChinesePromptFactory() if language.startswith("zh") else EnglishPromptFactory()

