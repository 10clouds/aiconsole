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

// Analysis

import ky from 'ky';
import { getBaseURL } from '../../store/useAPIStore';
import { schemaTypeToInputType } from '@/utils/assets/schemaTypeToInputType';

interface ExecutionModeParamSchema {
  title: string;
  type: string;
  default?: any;
}

export type ExecutionModeParamField = Omit<ExecutionModeParamSchema, 'default'> & {
  value: any;
};

interface ExecutionModeParamsSchema {
  [key: string]: ExecutionModeParamSchema;
}

export const getExecutionModeParamsSchema = async (module_path: string, notify: boolean = true) => {
  let params: [string, ExecutionModeParamField][] = [];

  try {
    const url = new URL(`${getBaseURL()}/api/execution_modes/params_schema`);
    url.searchParams.append('module_path', module_path);
    url.searchParams.append('notify', notify.toString());

    const paramsJson = await ky.get(url.toString()).json<ExecutionModeParamsSchema>();

    params = Object.entries(paramsJson).map(([key, data]) => [
      key,
      {
        ...data,
        value: data.default,
        type: schemaTypeToInputType(data.type),
      },
    ]);
  } catch (error) {
    console.error(error);
  } finally {
    return params;
  }
};
