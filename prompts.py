class PromptFactory:
    def create_prompt(self, target_lang: str) -> str:
        raise NotImplementedError


class EnglishPromptFactory(PromptFactory):
    def create_prompt(self, target_lang: str) -> str:
        return (
            "You are a language tutor. Analyze the text in the image for learners of "
            f"{target_lang}. Return explanations in English following the provided schema. "
            "Include sections for every level (N1-N5) even if they contain no items."
        )


class ChinesePromptFactory(PromptFactory):
    def create_prompt(self, target_lang: str) -> str:
        return (
            f"請分析圖片中的{target_lang}文字，依照給定的結構列出詞彙與文法，以繁體中文回答。" 
            "請回傳N1到N5每一級的資料，即便沒有內容也要給空陣列。"
        )


def get_prompt_factory(language: str) -> PromptFactory:
    return ChinesePromptFactory() if language.startswith("zh") else EnglishPromptFactory()
