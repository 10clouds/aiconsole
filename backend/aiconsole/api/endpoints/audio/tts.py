# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openai import BaseModel, OpenAI

from aiconsole_toolkit.settings import get_settings

router = APIRouter()


class TextToSpeechPayload(BaseModel):
    text: str


@router.post("/tts")
async def text_to_speech(text: TextToSpeechPayload):
    try:
        # Initialize the OpenAI client
        openai_key = get_settings().openai_api_key
        client = OpenAI(api_key=openai_key)

        # Use the OpenAI API to convert text to speech with the specified format
        response = client.audio.speech.create(model="tts-1", voice="alloy", input=text.text, response_format="opus")

        # Stream the audio data directly to the client
        def generate_audio_stream():
            for data in response.iter_bytes():
                yield data

        return StreamingResponse(generate_audio_stream(), media_type="audio/opus")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
