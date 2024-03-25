import { create } from 'zustand';
import { AudioAPI } from '@/audio/AudioAPI';

interface SoundPromise {
  promise: Promise<Howl>;
  isFinished: boolean;
}

interface TTSState {
  soundQueue: SoundPromise[];
  hasAutoPlay: boolean;
  isPlaying: boolean;
  numLoading: number;
  queuedTextSoFar: string;
  enqueueText: (text: string) => Promise<void>;
  processQueue: () => Promise<void>;
  readText: (text: string, canBeContinued: boolean) => Promise<void>;
  stopReading: () => void;
}

export const useTTSStore = create<TTSState>((set, get) => ({
  soundQueue: [],
  hasAutoPlay: false,
  isPlaying: false,
  numLoading: 0,
  queuedTextSoFar: '',

  enqueueText: async (text: string) => {
    console.log('Enqueuing text:', text);

    const newSoundPromise: SoundPromise = {
      promise: AudioAPI.textToSpeech(text),
      isFinished: false,
    };
    set((state) => ({ numLoading: state.numLoading + 1 }));

    const after = () => {
      set((state) => ({ numLoading: state.numLoading - 1 }));
      newSoundPromise.isFinished = true;
      get().processQueue();
    };

    newSoundPromise.promise.then(after, after);
    set((state) => ({ soundQueue: [...state.soundQueue, newSoundPromise] }));
    if (!get().isPlaying) {
      get().processQueue();
    }
  },

  processQueue: async () => {
    const { soundQueue, isPlaying, numLoading } = get();
    console.log('Processing queue', soundQueue.length, isPlaying, numLoading);
    if (soundQueue.length === 0 || !soundQueue[0].isFinished || isPlaying) return;
    const sound: Howl = await soundQueue[0].promise;
    setTimeout(() => {
      sound.once('end', () => {
        set({ isPlaying: false });
        set((state) => ({ soundQueue: state.soundQueue.slice(1) }));
        console.log('Sound finished:', sound, soundQueue[0].promise, soundQueue[0].isFinished);
        get().processQueue(); // Process the next item in the queue
      });
      sound.play();
      console.log('Playing sound:', sound);
    }, 100); // delay between sounds
    set({ isPlaying: true });
  },

  readText: async (text: string, canBeContinued: boolean) => {
    set({ hasAutoPlay: true });

    if (text === '') {
      set({ queuedTextSoFar: '' });
      return;
    }

    const { queuedTextSoFar } = get();
    if (text.startsWith(queuedTextSoFar)) {
      const remainingText = text.slice(queuedTextSoFar.length);
      if (canBeContinued) {
        const paragraphs = remainingText.split(/\n\n+/);
        if (paragraphs.length > 1) {
          const fullParagraphs = paragraphs.slice(0, paragraphs.length - 1).join('\n\n');
          const remainingTextWithoutLastParagraph = remainingText.substring(
            0,
            remainingText.length - paragraphs[paragraphs.length - 1].length,
          );
          const newText = queuedTextSoFar
            ? queuedTextSoFar + remainingTextWithoutLastParagraph
            : remainingTextWithoutLastParagraph;
          set({ queuedTextSoFar: newText });
          get().enqueueText(fullParagraphs);
        }
      } else {
        set({ queuedTextSoFar: '' });
        get().enqueueText(remainingText);
      }
    } else {
      console.log('Cannot continue reading from a different text', "'", queuedTextSoFar, "'", "'", text, "'");
      throw new Error('Cannot continue reading from a different text');
    }
  },

  stopReading: () => {
    get().soundQueue.forEach((sound) => sound.promise.then((s) => s.stop()));

    set({
      hasAutoPlay: false,
      soundQueue: [],
      isPlaying: false,
    });
  },
}));

/*

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

import { AudioAPI } from '@/audio/AudioAPI';
import React, { createContext, useEffect, useRef, useState } from 'react';

interface ISoundContext {
  readText: (text: string, canBeContinued: boolean) => Promise<void>;
  stopReading: () => void;
  hasAutoPlay: boolean;
  isPlaying: boolean;
  isLoading: boolean;
}

export const SoundContext = createContext<ISoundContext | undefined>(undefined);

export const TTSProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const soundQueue = useRef<Promise<Howl>[]>([]);
  const [hasAutoPlay, setHasAutoPlay] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [numLoading, setNumLoading] = useState(0);
  const [queuedTextSoFar, setQueuedTextSoFar] = useState('');

  const enqueueText = async (text: string) => {
    const newSoundPromise = AudioAPI.textToSpeech(text);
    setNumLoading((currentNum) => currentNum + 1);

    const after = () => {
      setNumLoading((currentNum) => currentNum - 1);
      processQueue();
    };

    newSoundPromise.then(after, after);
    soundQueue.current = [...soundQueue.current, newSoundPromise];
    if (!isPlaying) {
      processQueue();
    }
  };

  const processQueue = async () => {
    console.log('Processing queue', soundQueue.current.length, isPlaying, numLoading);
    if (soundQueue.current.length === 0) return;
    const sound: Howl = await soundQueue.current[0];
    sound.once('end', () => {
      setIsPlaying(false);
      soundQueue.current = soundQueue.current.slice(1);
      processQueue(); // Process the next item in the queue
    });
    sound.play();
    setIsPlaying(true);
  };

  const readText = async (text: string, canBeContinued: boolean) => {
    setHasAutoPlay(true);

    if (text === '') {
      setQueuedTextSoFar('');
      return;
    }

    if (text.startsWith(queuedTextSoFar)) {
      const remainingText = text.slice(queuedTextSoFar.length);
      if (!canBeContinued) {
        enqueueText(remainingText);
      } else {
        //ok so it can be continued, so we want to skip the very last paragraph and just send any fully completed paragraphs
        const paragraphs = remainingText.split(/\n\n+/);
        if (paragraphs.length > 1) {
          const fullParagraphs = paragraphs.slice(0, paragraphs.length - 1).join('\n\n');
          setQueuedTextSoFar(queuedTextSoFar + '\n\n' + fullParagraphs);
          enqueueText(fullParagraphs);
        }
      }
    } else {
      throw new Error('Cannot continue reading from a different text');
    }
  };

  const stopReading = () => {
    setHasAutoPlay(false);
    soundQueue.current = [];
    setIsPlaying(false);
  };

  useEffect(() => {
    return () => {
      // Stop any currently playing sound
      setIsPlaying(false);
      soundQueue.current = [];
    };
  }, []);

  return (
    <SoundContext.Provider value={{ readText, stopReading, isPlaying, isLoading: numLoading > 0, hasAutoPlay }}>
      {children}
    </SoundContext.Provider>
  );
};
*/
