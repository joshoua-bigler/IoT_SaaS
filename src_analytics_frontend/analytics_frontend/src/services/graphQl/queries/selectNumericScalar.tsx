import { gql } from '@apollo/client';

export const SELECT_NUMERIC_SCALAR = gql`
  query SelectNumericScalar(
    $tenantIdentifier: String!
    $deviceIdentifier: String!
    $start: String!
    $end: String!
    $metricIdentifier: [String!]
    $path: String
    $aggregation: Aggregation
    $grouping: Grouping
  ) {
    numericScalar(
      body: {
        tenantIdentifier: $tenantIdentifier
        deviceIdentifier: $deviceIdentifier
        start: $start
        end: $end
        metricIdentifier: $metricIdentifier
        path: $path
        aggregation: $aggregation
        grouping: $grouping
      }
    ) {
      deviceIdentifier
      metricIdentifier
      unit
      values {
        timestampLocal
        value
      }
    }
  }
`;
