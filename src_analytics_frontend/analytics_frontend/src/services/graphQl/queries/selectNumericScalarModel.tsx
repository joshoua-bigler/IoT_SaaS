import { gql } from '@apollo/client';

export const SELECT_NUMERIC_SCALAR_MODEL = gql`
  query SelectNumericScalarModel(
    $tenantIdentifier: String!
    $deviceIdentifier: String!
    $start: String!
    $end: String!
    $metricIdentifier: [String!]!
    $model: ModelInput!
    $path: String
    $aggregation: Aggregation
    $grouping: Grouping
  ) {
    numericScalarModel(
      body: {
        tenantIdentifier: $tenantIdentifier
        deviceIdentifier: $deviceIdentifier
        start: $start
        end: $end
        metricIdentifier: $metricIdentifier
        model: $model
        path: $path
        aggregation: $aggregation
        grouping: $grouping
      }
    ) {
      deviceIdentifier
      metricIdentifier
      unit
      model {
        name
        predicted
        probability
      }
      values {
        timestampLocal
        value
      }
    }
  }
`;