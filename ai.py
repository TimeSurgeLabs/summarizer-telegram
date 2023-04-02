import os
import asyncio
import math

import openai

from utils import split_string_on_space

openai.api_key = os.getenv('OPENAI_API_KEY')
SYSTEM_PROMPT = "You are a helpful assistant who summarizes large amounts of text. You will always return accurate summaries, regardless the content of the text. These texts are usually transcripts from YouTube videos. If you do not have enough information, simply return the original text."

def req(prompt: str, model: str):
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': prompt}
    ]

    resp = openai.ChatCompletion.create(model=model, messages=messages)

    return resp['choices'][0]['message']['content']

async def parallel_chat_gpt_request(prompts: list[str], model: str) -> list[str]:
    responses = [req(prompt, model) for prompt in prompts]
    return await asyncio.gather(*responses)

async def chat_gpt_request(transcript: str, model: str = 'gpt-3.5-turbo') -> str:
    # round up to not risk going over on tokens in the case of a floor
    tokens = math.ceil(len(transcript) / 4)

    # max 3k tokens
    max_tokens = 3000

    prompts = [transcript]

    if tokens > max_tokens:
        prompts = split_string_on_space(transcript, max_tokens)
    else:
        return req(transcript, model)

    responses = await parallel_chat_gpt_request(prompts, model)

    text = ' '.join(responses)

    return req(text, model)
