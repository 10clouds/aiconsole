import AlertDialog from '@/components/common/AlertDialog';

interface UnsavedSettingsDialogProps {
  isOpen: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export const UnsavedSettingsDialog = ({ isOpen, onCancel, onConfirm }: UnsavedSettingsDialogProps) => (
  <AlertDialog
    isOpen={isOpen}
    title="Unsaved Changes"
    onClose={onCancel}
    confirmationButtonText="Yes"
    cancelButtonText="Cancel"
    onConfirm={onConfirm}
  >
    You have unsaved changes. Do you want to discard them?
  </AlertDialog>
);
