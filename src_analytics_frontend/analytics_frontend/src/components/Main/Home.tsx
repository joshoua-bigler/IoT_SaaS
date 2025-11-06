import React, { useState, useMemo } from 'react';
import { useQuery, DocumentNode } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
// local
import { Device } from '../../interfaces/graphql/Device';

interface HomeProps {
  searchQuery: string;
  setDeviceIdentifier: (deviceIdentifier: string) => void;
  tenantIdentifier: string;
  query: DocumentNode;
}

const Home: React.FC<HomeProps> = ({ searchQuery, setDeviceIdentifier, tenantIdentifier, query }) => {
  const navigate = useNavigate();
  const [sortConfig, setSortConfig] = useState<{
    key: keyof Device;
    direction: 'asc' | 'desc';
  } | null>(null);
  const { data, loading, error } = useQuery(query, { variables: { tenantIdentifier: tenantIdentifier } });
  const devices: Device[] = data?.devices ?? [];
  const queryLower = searchQuery.trim().toLowerCase();
  const filteredData = useMemo(() => {
    if (!queryLower) return devices;
    return devices.filter((device: Device) => {
      const name = (device.deviceIdentifier ?? '').toLowerCase();
      const description = (device.description ?? '').toLowerCase();
      const city = (device.city ?? '').toLowerCase();
      const country = (device.country ?? '').toLowerCase();
      return name.includes(queryLower) || description.includes(queryLower) || city.includes(queryLower) || country.includes(queryLower);
    });
  }, [queryLower, devices]);
  const sortedData = useMemo(() => {
    if (!sortConfig) return filteredData;
    return [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key] ?? '';
      const bValue = b[sortConfig.key] ?? '';
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [sortConfig, filteredData]);
  const handleSort = (key: keyof Device) => {
    setSortConfig((prev) =>
      prev?.key === key
        ? { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: 'asc' }
    );
  };
  if (loading) return <div>Loading devices...</div>;
  if (error) return <div>Error loading data: {error.message}</div>;
  return (
    <div>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow className='bg-gray-100'>
              <TableCell onClick={() => handleSort('deviceIdentifier')} style={{ cursor: 'pointer' }}>
                Name
              </TableCell>
              <TableCell>
                Description
              </TableCell>
              <TableCell onClick={() => handleSort('city')} style={{ cursor: 'pointer' }}>
                City
              </TableCell>
              <TableCell onClick={() => handleSort('country')} style={{ cursor: 'pointer' }}>
                Country
              </TableCell>
              <TableCell onClick={() => handleSort('status')} style={{ cursor: 'pointer' }}>
                Status
              </TableCell>
              <TableCell onClick={() => handleSort('latestAliveLocal')} style={{ cursor: 'pointer' }}>
                Latest Activity
              </TableCell>
              <TableCell onClick={() => handleSort('timezone')} style={{ cursor: 'pointer' }}>
                Timezone
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align='center'>
                  No machines found.
                </TableCell>
              </TableRow>
            ) : (
              sortedData.map((device: Device) => (
                <TableRow key={device.deviceIdentifier} hover>
                  <TableCell
                    onClick={() => {
                      setDeviceIdentifier(device.deviceIdentifier);
                      navigate('/machine-details/overview');
                    }}
                    style={{ cursor: 'pointer', textDecoration: 'underline' }}
                  >
                    {device.deviceIdentifier}
                  </TableCell>
                  <TableCell>{device.description}</TableCell>
                  <TableCell>{device.city ?? '-'}</TableCell>
                  <TableCell>{device.country ?? '-'}</TableCell>
                  <TableCell>{device.status}</TableCell>
                  <TableCell>{device.latestAliveLocal}</TableCell>
                  <TableCell>{device.timezone}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </div >
  );
};

export default Home;
