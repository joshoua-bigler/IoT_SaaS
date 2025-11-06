import React from 'react';
import { Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const SidebarMachine: React.FC = () => {
  const navigate = useNavigate();
  const baseButtonClasses = 'bg-gray-300 text-black active:bg-gray-500 active:text-white transition duration-150';

  return (
    <div className='begin-1/5 h-[calc(100vh-4rem)] bg-gray-100 p-4 shadow-md flex flex-col'>
      {/* Sections */}
      <div className='grid pt-2 gap-2 mb-4'>
        <Button
          variant='contained'
          className={baseButtonClasses}
          onClick={() => navigate('/machine-details/overview')}
        >
          Overview
        </Button>
        <Button
          variant='contained'
          className={baseButtonClasses}
          onClick={() => navigate('/machine-details/insights')}
        >
          Insights
        </Button>
      </div>

      {/* Separator line */}
      <div className='h-px bg-gray-300 my-2' />

      {/* Footer */}
      <div className='mt-auto'>
        <div className='text-sm text-center text-gray-600'>
          IoT Platform Version: 1.0.0
        </div>
      </div>
    </div>
  );
};

export default SidebarMachine;
