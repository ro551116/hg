"""Generate Blender objects from natural language using an LLM."""
import sys
import json
import openai
from text_to_blender import parse_line, create_object

# You must set OPENAI_API_KEY environment variable or configure openai.api_key

PROMPT = (
    "Convert the following instruction into a list of commands for the text_to_blender.py script.\n"
    "Use the format: one command per line, e.g. 'cube size=2 location=0,0,0 color=1,0,0'."
)


def instructions_from_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": text}],
    )
    return response.choices[0].message.content


def run_instructions(instructions):
    for line in instructions.splitlines():
        info = parse_line(line)
        if info:
            create_object(info)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: blender --python lm_to_blender.py -- '<instruction text>'")
        sys.exit(1)

    text = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else sys.argv[1]
    cmds = instructions_from_text(text)
    run_instructions(cmds)
