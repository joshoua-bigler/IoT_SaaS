import React, { useState } from 'react';
import { TextField, Button, IconButton } from '@mui/material';

interface SidebarHomeProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

const Sidebar: React.FC<SidebarHomeProps> = ({ searchQuery, setSearchQuery }) => {
  return (
    <div className='h-[calc(100vh-4rem)] bg-gray-100 p-4 flex flex-col'>
      <div className='flex items-center gap-2 mb-4'>
        <TextField
          variant='outlined'
          size='small'
          placeholder='Search'
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className='mt-auto text-sm text-center text-gray-600'>IoT Platform Version: 1.0.0</div>
    </div>
  );
};

export default Sidebar;
