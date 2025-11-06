import { gql } from '@apollo/client';

export const SELECT_DEVICES = gql`
  query GetDevices($tenantIdentifier: String!) {
    devices(
      body: { 
        tenantIdentifier: $tenantIdentifier 
      }) 
      {
        country
        description
        deviceIdentifier
        lat
        latestAliveLocal
        long
        status
        timezone
      }
   }
  `;