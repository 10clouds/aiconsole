import AlertDialog from '@/components/common/AlertDialog';
import { Button } from '@/components/common/Button';
import { Icon } from '@/components/common/icons/Icon';
import { Asset, AssetType } from '@/types/editables/assetTypes';
import { cn } from '@/utils/common/cn';
import { IterationCcw, X } from 'lucide-react';
import { useState } from 'react';

interface AssetInfoBarProps {
  asset: Asset;
  hasCore: boolean;
  assetType: AssetType;
  lastSavedAsset: Asset | undefined;
  onRevert: () => void;
}

export const RestoreButton = ({ onRevert }: { onRevert: () => void }) => (
  <AlertDialog
    title="Are you sure you want to restore the original?"
    onConfirm={onRevert}
    confirmationButtonText="Restore original"
    openModalButton={
      <Button variant="tertiary" small classNames="p-0">
        <Icon icon={IterationCcw} /> Restore original
      </Button>
    }
  >
    You may lose your changes.
  </AlertDialog>
);

export const AssetInfoBar = ({ asset, hasCore, assetType, lastSavedAsset, onRevert }: AssetInfoBarProps) => {
  const [visible, setVisible] = useState(true);

  const hide = () => setVisible(false);

  return hasCore && visible ? (
    <div
      className={cn(
        'bg-gray-800 flex items-center justify-center gap-[20px] leading-[18px] text-white text-center text-[14px] px-[20px] py-[16px] absolute h-[50px] right-0 left-0 z-10',
        {
          'bg-grayPurple-800': asset.defined_in === 'project',
        },
      )}
    >
      {asset.defined_in === 'aiconsole' && <span>This is a system {assetType}. Start editing to overwrite it.</span>}
      {asset.defined_in === 'project' && (
        <>
          <span>
            This {assetType} {lastSavedAsset !== undefined ? 'is overwriting' : 'will overwrite'} a default system{' '}
            {assetType}.
          </span>
          <RestoreButton onRevert={onRevert} />
        </>
      )}
      <Icon icon={X} className="absolute right-[30px] cursor-pointer" onClick={hide} />
    </div>
  ) : null;
};
