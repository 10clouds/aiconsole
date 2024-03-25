// The AIConsole Project
//
// Copyright 2023 10Clouds
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { Howl } from 'howler';
import ky from 'ky';
import { getBaseURL } from '../store/useAPIStore';

const textToSpeech = async (text: string): Promise<Howl> => {
  const response = await ky.post(`${getBaseURL()}/tts`, { json: { text } });
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);

  const sound = new Howl({
    src: [url],
    format: ['opus'],
    html5: true, // Enable HTML5 Audio to force audio streaming without loading the full file upfront
  });

  return sound;
};

export const AudioAPI = {
  textToSpeech,
};
