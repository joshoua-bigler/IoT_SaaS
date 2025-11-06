import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import React from 'react';
import { useNavigate } from 'react-router-dom';

interface NavbarProps {
  deviceIdentifier: string | null;
  setDeviceIdentifier: (deviceIdentifier: string | null) => void;
}

const Navbar: React.FC<NavbarProps> = ({ deviceIdentifier, setDeviceIdentifier }) => {
  const navigate = useNavigate();

  const handleHomeClick = () => {
    setDeviceIdentifier(null);
    navigate('/');
  };

  return (
    <AppBar position='fixed' className='bg-white shadow-md'>
      <Toolbar className='relative flex justify-between'>

        {/* Left: Analytics title */}
        <Box onClick={handleHomeClick} className='cursor-pointer flex items-center gap-2'>
          <Typography variant='h5' className='text-white font-extrabold tracking-wide'>
            Analytics
          </Typography>
        </Box>

        {/* Center: Home icon */}
        <Box className='absolute left-1/2 transform -translate-x-1/2'>
          <IconButton onClick={handleHomeClick}>
            <HomeIcon className='text-white' />
          </IconButton>
        </Box>

        {/* Right: Device identifier (optional) */}
        {deviceIdentifier && (
          <Typography variant='h6' className='text-white font-medium'>
            | Device: {deviceIdentifier}
          </Typography>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

