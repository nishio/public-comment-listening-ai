from typing import List
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

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

async def extract_key_points(content: str) -> List[str]:
    try:
        response = await openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": content}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        # Parse the response and extract the list of key points
        result = json.loads(response.choices[0].message.content)
        return result if isinstance(result, list) else []
    
    except Exception as e:
        print(f"Error in OpenAI extraction: {str(e)}")
        raise Exception("Failed to extract key points")
