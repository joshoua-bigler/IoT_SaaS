def create_metric_group_table():
  return '''
  CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- Required for gen_random_uuid()

  CREATE TABLE metric_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- Use UUID as primary key
    group_name TEXT NOT NULL,  -- Unique group names
    parent_id UUID REFERENCES metric_groups(id) ON DELETE CASCADE,  -- Self-referencing for hierarchy
    full_path TEXT UNIQUE
  );

  ALTER TABLE metric_groups ADD CONSTRAINT unique_group_per_parent
  UNIQUE (group_name, parent_id);

  ALTER TABLE metric_groups ADD CONSTRAINT prevent_self_reference 
  CHECK (id <> parent_id);
  '''


def update_full_path():
  return '''
    WITH RECURSIVE group_hierarchy AS (
  -- Base case: Root groups (parent_id IS NULL)
  SELECT 
    id, 
    group_name, 
    parent_id, 
    group_name AS full_path  -- Root groups have full_path = group_name
  FROM metric_groups
  WHERE parent_id IS NULL  -- Fix: Include root nodes

  UNION ALL

  -- Recursive part: Append child group names to their parent path
  SELECT 
    mg.id, 
    mg.group_name, 
    mg.parent_id, 
    CONCAT(gh.full_path, '.', mg.group_name) AS full_path
  FROM metric_groups mg
  JOIN group_hierarchy gh ON mg.parent_id = gh.id
  )
  UPDATE metric_groups AS mg
  SET full_path = gh.full_path
  FROM group_hierarchy gh
  WHERE mg.id = gh.id;
  '''
