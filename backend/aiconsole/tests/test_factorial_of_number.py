from pathlib import Path

import pytest

from aiconsole.tests.chat_test_framework import chat_test_framework

_PROJECT_PATH = Path("./chat_test_framework/calculate_factorial/").absolute()
_MESSAGE = "Run factorial of 5"


@chat_test_framework.repeat(10)
@pytest.mark.asyncio
async def test_should_calculate_factorial_of_given_number():
    Path(_PROJECT_PATH).mkdir(parents=True, exist_ok=True)

    async with chat_test_framework.initialize_project_with_chat(str(_PROJECT_PATH)):
        output_messages = await chat_test_framework.process_user_code_request(_MESSAGE, agent_id="automator")

        # it should be code output and final sentence
        assert (
            len(output_messages) == 2
        ), f"[CHAT_ID: {chat_test_framework.chat_ref.id}] Automator message group should have only one response, now has: "
        f"{len(output_messages)}"
