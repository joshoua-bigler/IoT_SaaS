import './App.css';
import React, { useState } from 'react';
import { Route, Routes } from 'react-router-dom';
// local
import Navbar from './components/navigation/Navbar';
import Sidebar from './components/navigation/Sidebar';
import Home from './components/Main/Home';
import Overview from './components/Main/MachineDetails/Overview';
import Insights from './components/Main/MachineDetails/Insights';
import { SELECT_DEVICES } from './services/graphQl/queries/selectDevices';

function App() {
  const [deviceIdentifier, setDeviceIdentifierState] = useState<string | null>(() => {
    return localStorage.getItem('deviceIdentifier');
  });
  const setDeviceIdentifier = (id: string | null) => {
    setDeviceIdentifierState(id);
    if (id) {
      localStorage.setItem('deviceIdentifier', id);
    } else {
      localStorage.removeItem('deviceIdentifier');
    }
  };
  const [searchQuery, setSearchQuery] = useState('');
  const [tenantIdentifier, setTenantIdentifier] = useState<string>('100000');
  return (
    <div className='grid grid-cols-1 gap-12'>
      <div className='grid'>
        <Navbar deviceIdentifier={deviceIdentifier} setDeviceIdentifier={setDeviceIdentifier} />
      </div>
      <div className='grid w-screen'>
        <div className='flex flex-row'>
          <div className='basis-1/5 '>
            <Sidebar selectedMachine={deviceIdentifier} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
          </div>
          <div className='basis-4/5'>
            <Routes>
              <Route
                path='/'
                element={
                  <Home
                    searchQuery={searchQuery}
                    setDeviceIdentifier={setDeviceIdentifier}
                    query={SELECT_DEVICES}
                    tenantIdentifier={tenantIdentifier}
                  />
                }
              />
              <Route
                path='/machine-details/overview'
                element={<Overview tenantIdentifier={tenantIdentifier} deviceIdentifier={deviceIdentifier} />}
              />
              <Route
                path='/machine-details/insights'
                element={<Insights tenantIdentifier={tenantIdentifier} deviceIdentifier={deviceIdentifier} />}
              />
            </Routes>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
