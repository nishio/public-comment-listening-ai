from typing import List
import openai
import json
import os
import logging
import asyncio
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
logging.basicConfig(level=logging.INFO)

def load_prompt():
    try:
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 "prompts", "extraction", "default.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading prompt: {str(e)}")
        return """あなたは専門的なリサーチアシスタントで、整理された議論のデータセットを作成するお手伝いをする役割です。
一般市民から寄せられた意見を提示しますので、それらをより簡潔で読みやすい形に整理するお手伝いをお願いします。必要な場合は2つの別個の議論に分割することもできますが、多くの場合は1つの議論にまとめる方が望ましいでしょう。
結果は整形されたJSON形式の文字列リストとして返してください。
要約は必ず日本語で作成してください。"""

EXTRACTION_PROMPT = load_prompt()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def _call_openai_api(content: str) -> dict:
    """Call OpenAI API with retry logic and timeout"""
    try:
        # Set timeout for the API call
        async with asyncio.timeout(30):
            response = await openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": EXTRACTION_PROMPT},
                    {"role": "user", "content": content}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
    except asyncio.TimeoutError:
        logging.error("OpenAI API call timed out")
        raise TimeoutError("API request timed out")
    except Exception as e:
        logging.error(f"OpenAI API call failed: {str(e)}")
        raise

async def extract_key_points(content: str) -> List[str]:
    """Extract key points from content with error handling"""
    try:
        result = await _call_openai_api(content)
        if not isinstance(result, list):
            logging.warning(f"Unexpected response format: {result}")
            return []
        return result
    
    except TimeoutError:
        logging.error("Extraction timed out")
        raise Exception("要点抽出がタイムアウトしました")
    except Exception as e:
        logging.error(f"Error in key points extraction: {str(e)}")
        raise Exception("要点抽出に失敗しました")
