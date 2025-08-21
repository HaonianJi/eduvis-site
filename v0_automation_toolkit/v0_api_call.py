"""v0 Model API example (large model)

Usage:
1. Set environment variable V0_API_KEY or create a .env file and load it yourself.
2. `pip install requests python-dotenv` if you want to load .env automatically.
3. Run: python v0_api_call.py
"""

import json
import re
from pathlib import Path
import os
import sys
from typing import Generator, Union

import httpx

API_URL = "https://api.v0.dev/v1/chat/completions"
DEFAULT_MODEL = "v0-1.5-lg"  # Large version
MODEL = os.getenv("V0_MODEL", DEFAULT_MODEL)
def _get_api_key() -> str:
    key = os.getenv("V0_API_KEY")
    if not key:
        sys.exit("[ERROR] Please set the V0_API_KEY environment variable.")
    print(f"DEBUG: Using API Key ending in ...{key[-4:]}")
    return key


def call_v0(prompt: str) -> str:
    """Simple (non-stream) call returning the assistant's full response text."""
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 16384}
    headers = {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=httpx.Timeout(300, connect=30)) as client:
        response = client.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def stream_v0(prompt: str) -> Generator[str, None, None]:
    """Stream responses chunk-by-chunk (Server-Sent Events). Yields text pieces."""
    payload = {
        "model": MODEL,
        "stream": True,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=httpx.Timeout(300, connect=30)) as client:
        with client.stream("POST", API_URL, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                chunk = json.loads(line.removeprefix("data:").strip())
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"].replace("\r", "")


def _extract_json(text: str) -> Union[dict, None]:
    """Extracts a JSON object from a string, handling markdown code blocks."""
    # Pattern to find JSON within a markdown code block (e.g., ```json ... ```)
    # This is the most robust method.
    match = re.search(r"```(?:json)?\s*({.*})\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # If no markdown block is found, assume the whole string or a part of it
        # is a JSON object. This is a fallback for plain JSON responses.
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            json_str = text[first_brace : last_brace + 1]
        else:
            # No JSON structure found
            return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # If parsing fails, it means the content is not valid JSON
        print("! Failed to decode JSON from extracted text:", json_str[:100] + "...", file=sys.stderr)
        return None


def demo():
    q1 = "Create a Next.js AI chatbot with authentication"
    print("=== Non-stream demo (large model) ===")
    print(call_v0(q1))

    q2 = "Add login to my Next.js app"
    print("\n=== Stream demo (large model) ===")
    for piece in stream_v0(q2):
        print(piece, end="", flush=True)
    print()


if __name__ == "__main__":
    # argparse-lite
    import argparse
    parser = argparse.ArgumentParser(description="Call v0 API and optionally save JSON from response")
    parser.add_argument("prompt_path", nargs="?", default=None, help="Path to the prompt file (optional).")
    parser.add_argument("--prompt", dest="prompt_text", default=None, help="Prompt text as a string.")
    parser.add_argument("--output", default=None, help="Path to save the output JSON file.")
    args = parser.parse_args()

    prompt_content = ""
    if args.prompt_path:
        if not os.path.isfile(args.prompt_path):
            sys.exit(f"File not found: {args.prompt_path}")
        with open(args.prompt_path, "r", encoding="utf-8") as f:
            prompt_content = f.read().strip()
    elif args.prompt_text:
        prompt_content = args.prompt_text
    elif os.path.isfile("prompt.txt"):
        print("--- Using prompt.txt by default ---", file=sys.stderr)
        with open("prompt.txt", "r", encoding="utf-8") as f:
            prompt_content = f.read().strip()
    else:
        # demo()
        sys.exit("No prompt provided. Use a file path, --prompt 'text', or create prompt.txt.")

    # Call the API
    response_text = call_v0(prompt_content)

    # Check if an output file is specified
    if args.output:
        # Extract JSON from the response
        json_data = _extract_json(response_text)
        if json_data:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                print(f"\n✅ JSON response saved to {args.output}")
            except IOError as e:
                print(f"\n❌ Error saving JSON to file: {e}", file=sys.stderr)
        else:
            print("\n⚠️ No JSON object found in the response to save.", file=sys.stderr)
            # Still, save the raw response for debugging
            with open(args.output + ".raw.txt", "w", encoding="utf-8") as f:
                f.write(response_text)
            print(f"Raw response saved to {args.output}.raw.txt")

    else:
        # Original behavior: print the full response
        print(response_text)
        parser.add_argument("--json-out", metavar="PATH", help="If provided, try to extract JSON from response and save to this file (e.g. project.json)")
        parser.add_argument("--stream", action="store_true", help="Stream response instead of one-shot")
        args = parser.parse_args()

        # Determine prompt
        prompt_text: str
        if args.prompt and os.path.isfile(args.prompt):
            prompt_text = Path(args.prompt).read_text(encoding="utf-8").strip()
        elif args.prompt:
            prompt_text = args.prompt
        elif Path("prompt.txt").is_file():
            prompt_text = Path("prompt.txt").read_text(encoding="utf-8").strip()
        else:
            sys.exit("No prompt provided and prompt.txt not found")

        if args.stream:
            collected = ""
            for chunk in stream_v0(prompt_text):
                print(chunk, end="", flush=True)
                collected += chunk
            print()
            resp_text = collected
        else:
            resp_text = call_v0(prompt_text)
            print(resp_text)

        # Optionally save JSON
        if args.json_out:
            obj = _extract_json(resp_text)
            if obj is None:
                sys.exit("! Could not locate valid JSON in response")
            Path(args.json_out).write_text(json.dumps(obj, indent=2), encoding="utf-8")
            print(f"✓ JSON extracted and saved to {args.json_out}")
        

