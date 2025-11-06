import React from 'react';
import { useLocation } from 'react-router-dom';
import SidebarHome from './SidebarHome';
import SidebarMachine from './SidebarMachine';

type SidebarProps = {
  selectedMachine: any;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
};

const Sidebar: React.FC<SidebarProps> = ({ selectedMachine, searchQuery, setSearchQuery }) => {
  const location = useLocation();
  const isMachineDetails = location.pathname.startsWith('/machine-details');

  return (
    <div className='bg-gray-100'>
      {isMachineDetails ? (
        <SidebarMachine />
      ) : (
        <SidebarHome searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
      )}
    </div>
  );
};

export default Sidebar;
