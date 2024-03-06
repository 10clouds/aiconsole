import { Select as RadixSelect, Trigger, Value, Content, Item, Portal } from '@radix-ui/react-select';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Icon } from './icons/Icon';
import { useState } from 'react';
import { cn } from '@/utils/common/cn';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  placeholder: string;
  options: Readonly<SelectOption[]>;
  initialValue?: string;
  onChange?: (value: string) => void;
}

export const Select = ({ placeholder, options, onChange, initialValue = '' }: SelectProps) => {
  const [value, setValue] = useState<string>(initialValue);
  const [open, setOpen] = useState(false);

  const notSelectedOptions = options.filter((option) => option.value !== value);
  const currentValueLabel = options.find((option) => option.value === value)?.label;
  const handleChange = (value: string) => {
    onChange?.(value);
    setValue(value);
  };

  return (
    <RadixSelect value={value} onValueChange={handleChange} open={open} onOpenChange={setOpen}>
      <Trigger
        className={cn(
          'flex items-center justify-between leading-[24px] px-[20px] py-[12px] min-w-[300px] bg-gray-700 border border-gray-500 rounded-[8px] text-[15px] text-gray-400 outline-none hover:bg-gray-600 hover:border-gray-400 h-[50px] truncate',
          { 'rounded-b-none bg-gray-600 border-gray-800 text-gray-500 border-b-0': open },
          { 'text-gray-300': value && !open },
          { 'font-normal': !!value },
        )}
      >
        <Value placeholder={placeholder}>{currentValueLabel}</Value>
        <Icon icon={open ? ChevronUp : ChevronDown} className="w-[24px] h-[24px]" />
      </Trigger>
      <Portal>
        <Content
          position="popper"
          className="bg-gray-600 border relative border-gray-800 rounded-[8px] overflow-hidden rounded-t-none border-t-0 w-[300px]"
        >
          {notSelectedOptions.map(({ label, value }) => (
            <Item
              key={value}
              className="outline-none px-[20px] py-[10px] text-[15px] text-gray-300 hover:bg-gray-500 cursor-pointer hover:text-white border-t border-gray-800 truncate w-[300px]"
              value={value}
            >
              {label}
            </Item>
          ))}
        </Content>
      </Portal>
    </RadixSelect>
  );
};
