import { ContextMenuItems } from '@/types/common/contextMenu';
import { cn } from '@/utils/common/cn';
import { Loader, Plus, Upload } from 'lucide-react';
import { ChangeEvent, MouseEvent, useEffect, useRef, useState } from 'react';
import { ContextMenu, ContextMenuRef } from './ContextMenu';
import { Icon } from './icons/Icon';

interface ImageUploaderProps {
  currentImage?: string;
  onUpload?: (avatar: string) => void;
}

// TODO: update this component with generating ai logic and connect with backend
const ImageUploader = ({ currentImage, onUpload }: ImageUploaderProps) => {
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isGenerating, _setIsGenerating] = useState(false);

  useEffect(() => {
    if (currentImage) {
      setPreviewImage(currentImage);
    }
  }, [currentImage]);

  const handleImageChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        if (typeof reader.result === 'string') {
          setPreviewImage(reader.result);
        }
      };
      reader.readAsDataURL(file);
      reader.onload = () => {
        onUpload?.(reader.result as string);
      };
    }
  };
  // const removeImage = () => {
  //   setPreviewImage(null);
  // };

  const handleUploadButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const triggerRef = useRef<ContextMenuRef>(null);

  const openContextMenu = (event: MouseEvent) => {
    if (event.type === 'contextmenu') {
      event.preventDefault();
      if (triggerRef.current) {
        triggerRef.current.handleTriggerClick(event);
      }
    }
    if (event.type === 'click') {
      if (fileInputRef.current) {
        fileInputRef.current.click();
      }
    }
  };

  // TODO: Implement when backend is ready
  // const generateWithAi = () => {};

  const menuItems: ContextMenuItems = [
    {
      type: 'item',
      key: 'Upload photo',
      icon: Upload,
      title: `Upload ${previewImage ? 'new' : ''} photo`,
      action: handleUploadButtonClick,
    },
    // {
    //   type: 'item',
    //   key: 'Generate with AI',
    //   icon: Shapes,
    //   title: 'Generate with AI',
    //   action: generateWithAi,
    // },
    // { type: 'separator', key: 'delete-separator', hidden: !previewImage },
    // {
    //   type: 'item',
    //   icon: Trash,
    //   title: 'Delete',
    //   hidden: !previewImage,
    //   action: removeImage,
    // },
  ];

  return (
    <div className="border border-gray-600 rounded-[12px] px-[20px] py-[15px] flex flex-col items-center gap-[10px] w-fit min-w-[160px] bg-gray-900">
      <input
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleImageChange}
        id="imageInput"
        ref={fileInputRef}
      />
      <p className="text-[15px] text-white text-center">Avatar</p>
      <div className="mt-[15px]">
        <ContextMenu options={menuItems} ref={triggerRef} triggerClassName="ml-auto">
          <div
            onClick={openContextMenu}
            className={cn(
              'group rounded-[100px] w-[80px] h-[80px] overflow-hidden cursor-pointer border border-transparent hover:border-white transition duration-200',
              { 'border-dashed border-gray-500 hover:border-yellow  ': !previewImage },
            )}
          >
            {previewImage ? (
              <img src={previewImage} alt="Preview" className="w-full h-full object-cover" />
            ) : (
              <button className="text-gray-400  w-full h-full rounded-[100px] group-hover:text-yellow transition duration-200">
                <Icon icon={isGenerating ? Loader : Plus} className="m-auto" width={24} height={24} />
              </button>
            )}
          </div>
        </ContextMenu>
      </div>
      <p className="text-[12px] text-center text-gray-400 mb-[10px] h-[18px]">
        {isGenerating ? 'Generating...' : null}
      </p>
    </div>
  );
};

export default ImageUploader;
