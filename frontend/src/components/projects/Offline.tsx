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

import { useUtilsStore } from '@/store/common/useUtilsStore';
import { RefreshCw } from 'lucide-react';
import { Button } from '../common/Button';
import NoInternet from '../common/icons/NoInternet';

const Offline = () => {
  const checkNetworkStatus = useUtilsStore((state) => state.checkNetworkStatus);
  const isNetworkChecking = useUtilsStore((state) => state.isNetworkChecking);

  return (
    <div className="flex justify-center items-center flex-col min-h-[100vh] px-[60px] relative">
      <div className="my-[180px] flex flex-col items-center gap-10 text-center max-w-[700px]">
        <div className="flex flex-col items-center gap-5">
          <NoInternet />
          <h2 className="font-extrabold text-white">We can't connect to the internet</h2>
        </div>
        <p className="text-gray-200">
          It looks like you have a problem with your internet connection. Try to resolve the issue and refresh the app.
          AIConsole cannot run without an internet connection.
        </p>

        <Button variant="status" onClick={checkNetworkStatus} disabled={isNetworkChecking}>
          <RefreshCw className="text-gray-400" />
          Refresh the app
        </Button>
      </div>
    </div>
  );
};
export default Offline;
