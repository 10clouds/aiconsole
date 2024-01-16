import { useEffect, useState } from 'react';

import { FormGroup } from '@/components/common/FormGroup';
import { CodeEditorLabelContent } from './CodeEditorLabelContent';
import { CodeInput } from './CodeInput';
import { TextInput } from './TextInput';
import { Material, RenderedMaterial } from '@/types/editables/assetTypes';
import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { useMaterialEditorContent } from './useMaterialEditorContent';
import { EditablesAPI } from '@/api/api/EditablesAPI';
import { MarkdownSupported } from '../MarkdownSupported';

interface MaterialFormProps {
  material: Material;
}

export const MaterialForm = ({ material }: MaterialFormProps) => {
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const handleChange = (value: string) => setSelectedAsset({ ...material, usage: value });
  const [showPreview, setShowPreview] = useState(false);
  const [preview, setPreview] = useState<RenderedMaterial | undefined>(undefined);
  const previewValue = preview ? preview?.content.split('\\n').join('\n') : 'Generating preview...';
  const materialEditorContent = useMaterialEditorContent(material);

  useEffect(() => {
    if (!material) {
      return;
    }

    EditablesAPI.previewMaterial(material).then((preview) => {
      setPreview(preview);
    });
  }, [material]);

  const codePreviewConfig = {
    label: 'Preview of text to be injected into AI context',
    onChange: undefined,
    value: preview?.error ? preview.error : previewValue,
    codeLanguage: 'markdown',
  };

  const codeEditorSectionContent = showPreview ? codePreviewConfig : materialEditorContent;

  return (
    <>
      <FormGroup className="relative">
        <TextInput
          className="min-h-[90px]"
          label="Usage"
          name="usage"
          placeholder="Write text here"
          value={material.usage}
          onChange={handleChange}
          helperText="Usage is used to help identify when this material should be used. "
          resize
        />
        <MarkdownSupported />
      </FormGroup>
      <FormGroup className="w-full flex flex-col">
        <div className="flex-1">
          {codeEditorSectionContent ? (
            <CodeInput
              label={codeEditorSectionContent.label}
              labelContent={
                <CodeEditorLabelContent showPreview={showPreview} onClick={() => setShowPreview((prev) => !prev)} />
              }
              value={codeEditorSectionContent.value}
              codeLanguage={codeEditorSectionContent.codeLanguage}
              onChange={codeEditorSectionContent.onChange}
              readOnly={showPreview}
            />
          ) : null}
          <MarkdownSupported />
        </div>
      </FormGroup>
    </>
  );
};
