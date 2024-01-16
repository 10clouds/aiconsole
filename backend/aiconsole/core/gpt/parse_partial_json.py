import json


def parse_partial_json(s: str) -> dict | None:
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    closing_chars_stack: list[str] = []
    escaped = False
    completed_string = []

    for char in s:
        if closing_chars_stack and closing_chars_stack[-1] == '"':
            if char == '"' and not escaped:
                closing_chars_stack.pop()
            elif char == "\\":
                escaped = not escaped
            elif char == "\n" and not escaped:
                char = "\\n"
            else:
                escaped = False
        else:
            if char == '"':
                closing_chars_stack.append('"')
            elif char == "{":
                closing_chars_stack.append("}")
            elif char == "[":
                closing_chars_stack.append("]")
            elif char in ["}", "]"] and closing_chars_stack:
                closing_chars_stack.pop()

        completed_string.append(char)

    completed_string.extend(reversed(closing_chars_stack))

    try:
        return json.loads("".join(completed_string))
    except json.JSONDecodeError:
        return None
