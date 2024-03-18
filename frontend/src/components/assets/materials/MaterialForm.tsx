import { useEffect, useMemo, useState } from 'react';

import { AssetsAPI } from '@/api/api/AssetsAPI';
import { FormGroup } from '@/components/common/FormGroup';
import { Material, RenderedMaterial } from '@/types/assets/assetTypes';
import { MarkdownSupported } from '../MarkdownSupported';
import { CodeEditorLabelContent } from '../CodeEditorLabelContent';
import { CodeInput } from '../CodeInput';
import { TextInput } from '../TextInput';
import { useMaterialEditorContent } from './useMaterialEditorContent';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { CodeEditor } from '../CodeEditor';

interface MaterialFormProps {
  material: Material;
}

export const MaterialForm = ({ material }: MaterialFormProps) => {
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const [showPreview, setShowPreview] = useState(false);
  const [preview, setPreview] = useState<RenderedMaterial | undefined>(undefined);
  const materialEditorContent = useMaterialEditorContent(material);

  const toggleShowPreview = () => setShowPreview((prev) => !prev);
  const handleChange = (value: string) => setSelectedAsset({ ...material, usage: value });

  useEffect(() => {
    if (!material) {
      return;
    }

    AssetsAPI.previewMaterial(material).then((preview) => {
      setPreview(preview);
    });
  }, [material]);

  const previewValue = useMemo(
    () => (preview ? preview?.content.split('\\n').join('\n') : 'Generating preview...'),
    [preview],
  );
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
          {/* {codeEditorSectionContent ? (
            <CodeInput
              label={codeEditorSectionContent.label}
              labelContent={
                <CodeEditorLabelContent showPreview={showPreview} onClick={() => setShowPreview((prev) => !prev)} />
              }
              labelSize="md"
              value={codeEditorSectionContent.value}
              codeLanguage={codeEditorSectionContent.codeLanguage}
              onChange={codeEditorSectionContent.onChange}
              readOnly={showPreview}
            />
          ) : null} */}

          <CodeEditor
            label={codeEditorSectionContent?.label}
            labelContent={<CodeEditorLabelContent showPreview={showPreview} onClick={toggleShowPreview} />}
            labelSize="md"
            value={codeEditorSectionContent?.value}
            onChange={codeEditorSectionContent?.onChange}
            language={codeEditorSectionContent?.codeLanguage}
            readOnly={showPreview}
          />
          <MarkdownSupported />
        </div>
      </FormGroup>
    </>
  );
};
