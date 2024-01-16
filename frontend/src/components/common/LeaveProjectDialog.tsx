import { ProjectsAPI } from '@/api/api/ProjectsAPI';
import AlertDialog from '@/components/common/AlertDialog';

interface LeaveProjectDialogProps {
  isOpen: boolean;
  onCancel: () => void;
}

export const LeaveProjectDialog = ({ isOpen, onCancel }: LeaveProjectDialogProps) => {
  const handleConfirm = () => {
    ProjectsAPI.closeProject();
  };

  return (
    <AlertDialog
      isOpen={isOpen}
      title="Leave Project?"
      confirmationButtonText="Leave"
      cancelButtonText="Cancel"
      onConfirm={handleConfirm}
      onClose={onCancel}
    >
      Are you sure you want to leave this project? Any unsaved changes will be lost.
    </AlertDialog>
  );
};
