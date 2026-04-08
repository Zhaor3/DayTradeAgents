"""LLM client abstraction - supports OpenAI and Anthropic with quick/deep models."""

from config import CONFIG


def call_llm(system_prompt: str, user_prompt: str, deep: bool = False) -> str:
    """Call the configured LLM and return the response text.

    Args:
        system_prompt: System instructions
        user_prompt: User message
        deep: If True, use the deep/smart model (gpt-5.2).
              If False, use the quick/cheap model (gpt-5-mini).
    """
    provider = CONFIG["llm_provider"].lower()
    model = CONFIG["model_deep"] if deep else CONFIG["model_quick"]

    if provider == "openai":
        return _call_openai(system_prompt, user_prompt, model)
    elif provider == "anthropic":
        return _call_anthropic(system_prompt, user_prompt, model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def _call_openai(system_prompt: str, user_prompt: str, model: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=CONFIG["openai_api_key"])

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def _call_anthropic(system_prompt: str, user_prompt: str, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=CONFIG["anthropic_api_key"])
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.content[0].text
