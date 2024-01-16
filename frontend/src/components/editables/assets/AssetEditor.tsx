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

import { useCallback, useEffect, useState } from 'react';
import { unstable_useBlocker as useBlocker, useNavigate, useParams } from 'react-router-dom';

import { Button } from '@/components/common/Button';
import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { Agent, Asset, AssetType, Material } from '@/types/editables/assetTypes';
import { useEditableObjectContextMenu } from '@/utils/editables/useContextMenuForEditable';
import { EditablesAPI } from '../../../api/api/EditablesAPI';
import { useAssetChanged } from '../../../utils/editables/useAssetChanged';
import { EditorHeader } from '../EditorHeader';
import { localStorageTyped } from '@/utils/common/localStorage';
import { usePrevious } from '@mantine/hooks';
import { useAssets } from '@/utils/editables/useAssets';
import { CheckCheck, Trash } from 'lucide-react';
import { Icon } from '@/components/common/icons/Icon';
import { useToastsStore } from '@/store/common/useToastsStore';
import { ContextMenu } from '../../common/ContextMenu';
import AlertDialog from '@/components/common/AlertDialog';
import { AssetInfoBar, RestoreButton } from './AssetInfoBar';
import { MaterialForm } from './MaterialForm';
import { useAssetEditor } from './useAssetEditor';
import { AgentForm } from './AgentForm';
import { cn } from '@/utils/common/cn';
import { ErrorObject, checkErrors } from './TextInput';

const { setItem } = localStorageTyped<boolean>('isAssetChanged');

enum SubmitButtonLabels {
  Overwrite = 'Overwrite',
  Create = 'Create',
  RenameAndSave = 'Rename and Save Changes',
  SaveChanges = 'Save Changes',
  Saved = 'Saved',
}

export function AssetEditor({ assetType }: { assetType: AssetType }) {
  const params = useParams();
  const id = params.id || '';
  const editableObjectType = assetType;
  const isNew = id === 'new';

  const [newPath, setNewPath] = useState<string>('');
  const [hasCore, setHasCore] = useState(false);
  const [errors, setErrors] = useState<ErrorObject>({
    executionMode: '',
  });
  const asset = useAssetStore((state) => state.selectedAsset);
  const lastSavedAsset = useAssetStore((state) => state.lastSavedSelectedAsset);
  const setLastSavedSelectedAsset = useAssetStore((state) => state.setLastSavedSelectedAsset);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const showToast = useToastsStore((state) => state.showToast);

  const navigate = useNavigate();
  const isAssetChanged = useAssetChanged();
  const blocker = useBlocker(isAssetChanged);
  const isPrevAssetChanged = usePrevious(isAssetChanged);
  const { updateStatusIfNecessary, isAssetStatusChanged, renameAsset } = useAssets(assetType);
  const { handleRevert, getInitialAsset, handleRename, handleDeleteWithInteraction } =
    useAssetEditor(editableObjectType);
  const menuItems = useEditableObjectContextMenu({
    editable: asset,
    editableObjectType: assetType,
  });
  const isSystemAsset = asset?.defined_in === 'aiconsole';
  const isProjectAsset = asset?.defined_in === 'project';
  const wasAssetChangedInitially = !isPrevAssetChanged && isAssetChanged;
  const wasAssetUpdate = isPrevAssetChanged && !isAssetChanged;

  const { reset, proceed, state: blockerState } = blocker || {};

  useEffect(() => {
    if (wasAssetUpdate && newPath) {
      navigate(newPath);
      setNewPath('');
    }
  }, [newPath, isAssetChanged, wasAssetUpdate, navigate]);

  useEffect(() => {
    setItem(isAssetChanged);
  }, [isAssetChanged]);

  // Acquire the initial object
  useEffect(() => {
    getInitialAsset();

    return () => {
      setSelectedAsset(undefined);
      setLastSavedSelectedAsset(undefined);
    };
  }, [getInitialAsset, setLastSavedSelectedAsset, setSelectedAsset]);

  useEffect(() => {
    if (!assetType || !asset?.id) {
      setHasCore(false);
      return;
    }

    if (
      !wasAssetChangedInitially &&
      Boolean(asset) &&
      ((isProjectAsset && asset.override) || (isSystemAsset && !asset.override))
    ) {
      setHasCore(true);
      return;
    }

    if (asset && isSystemAsset && wasAssetChangedInitially) {
      EditablesAPI.doesEdibleExist(assetType, asset?.id, 'aiconsole').then((exists) => {
        setHasCore(exists);
        setSelectedAsset({ ...asset, defined_in: 'project', override: exists } as Asset);
        setLastSavedSelectedAsset(undefined);
      });
    }
  }, [
    asset,
    setSelectedAsset,
    wasAssetChangedInitially,
    setLastSavedSelectedAsset,
    assetType,
    isSystemAsset,
    isProjectAsset,
  ]);

  const handleSaveClick = useCallback(async () => {
    if (asset === undefined) {
      return;
    }

    if (lastSavedAsset === undefined) {
      await EditablesAPI.saveNewEditableObject(editableObjectType, asset.id, asset);

      await updateStatusIfNecessary();

      showToast({
        title: 'Saved',
        message: `The ${assetType} has been successfully saved.`,
        variant: 'success',
      });
    } else if (lastSavedAsset && lastSavedAsset.id !== asset.id) {
      await renameAsset(lastSavedAsset.id, asset);
      showToast({
        title: 'Overwritten',
        message: `The ${assetType} has been overwritten.`,
        variant: 'success',
      });
    } else {
      if (isAssetChanged) {
        await EditablesAPI.updateEditableObject(editableObjectType, asset);

        showToast({
          title: 'Saved',
          message: `The ${assetType} has been successfully saved.`,
          variant: 'success',
        });
      }

      await updateStatusIfNecessary();
    }

    if (lastSavedAsset?.id !== asset.id) {
      useAssetStore.setState({ lastSavedSelectedAsset: asset });
      setNewPath(`/${editableObjectType}s/${asset.id}`);
    } else {
      // Reload the asset from server
      const newAsset = await EditablesAPI.fetchEditableObject<Material>({
        editableObjectType,
        id: asset.id,
      });
      setSelectedAsset(newAsset);
      useAssetStore.setState({ lastSavedSelectedAsset: newAsset });
    }
  }, [
    asset,
    editableObjectType,
    isAssetChanged,
    lastSavedAsset,
    setSelectedAsset,
    updateStatusIfNecessary,
    renameAsset,
    showToast,
  ]);

  const getSubmitButtonLabel = useCallback((): SubmitButtonLabels => {
    if (lastSavedAsset === undefined) {
      return hasCore ? SubmitButtonLabels.Overwrite : SubmitButtonLabels.Create;
    } else if (lastSavedAsset && lastSavedAsset.id !== asset?.id) {
      return isAssetChanged ? SubmitButtonLabels.RenameAndSave : SubmitButtonLabels.Saved;
    } else {
      return isAssetChanged ? SubmitButtonLabels.SaveChanges : SubmitButtonLabels.Saved;
    }
  }, [asset?.id, hasCore, isAssetChanged, lastSavedAsset]);

  const submitButtonLabel = getSubmitButtonLabel();
  const isSavedButtonLabel = submitButtonLabel === SubmitButtonLabels.Saved;
  const hasNameAndId = asset?.id && asset?.name;
  const enableSubmitRule = (isAssetChanged || isAssetStatusChanged) && hasNameAndId;

  const enableSubmit = () => {
    if (isNew) {
      return hasNameAndId;
    }

    return enableSubmitRule;
  };

  const isSubmitEnabled = enableSubmit();
  const disableSubmit = (!isSubmitEnabled && !isSavedButtonLabel) || checkErrors(errors);

  const confirmPageEscape = () => {
    getInitialAsset();
    proceed?.();
  };

  const discardChanges = () => {
    getInitialAsset();
    reset?.();
  };

  const assetSourceLabel = useCallback(() => {
    switch (asset?.defined_in) {
      case 'aiconsole':
        return `System ${assetType}`;
      case 'project':
        return `Custom ${assetType}`;
    }
  }, [asset?.defined_in, assetType]);

  const revertAsset = () => handleRevert(asset?.id);

  return (
    <div className="flex flex-col w-full h-full max-h-full overflow-auto">
      <ContextMenu options={menuItems}>
        <EditorHeader
          editable={asset}
          editableObjectType={editableObjectType}
          onRename={handleRename}
          isChanged={isAssetChanged}
        >
          <div className="flex gap-[20px] items-center">
            <p className={cn('text-[15px]', { 'font-bold': isSystemAsset })}>
              {assetSourceLabel()} {hasCore ? <span className="text-gray-300">(overwritten)</span> : null}
            </p>
            {isProjectAsset ? <RestoreButton onRevert={revertAsset} /> : null}
          </div>
        </EditorHeader>
      </ContextMenu>

      <div className="flex-grow overflow-auto">
        <div className="flex w-full h-full flex-col justify-between">
          <div className="w-full h-full overflow-auto relative">
            {asset && (
              <AssetInfoBar
                asset={asset}
                hasCore={hasCore}
                assetType={assetType}
                lastSavedAsset={lastSavedAsset}
                onRevert={revertAsset}
              />
            )}
            {asset && (
              <div className="flex-grow flex flex-col overflow-auto h-full px-[60px] py-[40px] pt-[90px] gap-5">
                {assetType === 'material' ? (
                  <MaterialForm material={asset as Material} />
                ) : (
                  <AgentForm agent={asset as Agent} setErrors={setErrors} errors={errors} />
                )}
                <div className="flex items-center justify-between w-full gap-[10px]">
                  {isProjectAsset ? (
                    <AlertDialog
                      title={`Are you sure you want to delete this ${editableObjectType}?`}
                      onConfirm={() => handleDeleteWithInteraction(asset.id)}
                      openModalButton={
                        <Button variant="tertiary">
                          <Icon icon={Trash} /> Delete {assetType}
                        </Button>
                      }
                    >
                      This process is irreversible.
                    </AlertDialog>
                  ) : null}
                  <Button
                    disabled={disableSubmit}
                    onClick={handleSaveClick}
                    active={isSavedButtonLabel}
                    classNames="ml-auto"
                  >
                    {submitButtonLabel} {isSavedButtonLabel ? <Icon icon={CheckCheck} /> : null}
                  </Button>
                </div>
              </div>
            )}
            <AlertDialog
              title={`Do you want to leave the ${assetType} settings?`}
              isOpen={blockerState === 'blocked'}
              onClose={discardChanges}
              onConfirm={confirmPageEscape}
              confirmationButtonText="Leave"
              cancelButtonText="Cancel"
            >
              Changes that you made may not be saved.
            </AlertDialog>
          </div>
        </div>
      </div>
    </div>
  );
}
