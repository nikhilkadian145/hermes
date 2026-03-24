import { useNavigate } from 'react-router-dom';
import { UploadSimple, ChatCircleText, ChartLineUp } from '@phosphor-icons/react';
import { Button } from '../ui/Button';

export function QuickActions() {
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
      <Button 
        variant="secondary" 
        size="md" 
        className="w-full justify-start md:justify-center bg-bg-surface"
        onClick={() => navigate('/upload')}
      >
        <UploadSimple size={20} className="mr-2 text-text-secondary" />
        Upload Documents
      </Button>
      <Button 
        variant="secondary" 
        size="md" 
        className="w-full justify-start md:justify-center bg-bg-surface"
        onClick={() => navigate('/chat')}
      >
        <ChatCircleText size={20} className="mr-2 text-text-secondary" />
        Chat with HERMES
      </Button>
      <Button 
        variant="secondary" 
        size="md" 
        className="w-full justify-start md:justify-center bg-bg-surface"
        onClick={() => navigate('/reports')}
      >
        <ChartLineUp size={20} className="mr-2 text-text-secondary" />
        View Reports
      </Button>
    </div>
  );
}
