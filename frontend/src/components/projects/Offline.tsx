import { RefreshCw } from 'lucide-react';
import { Button } from '../common/Button';
import NoInternet from '../common/icons/NoInternet';

const Offline = () => {
  const handleRefreshClick = () => {
    if (navigator.onLine) {
      window.location.reload();
    }
  };

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

        <Button variant="status" onClick={handleRefreshClick}>
          <RefreshCw className="text-gray-400" />
          Refresh the app
        </Button>
      </div>
    </div>
  );
};
export default Offline;
