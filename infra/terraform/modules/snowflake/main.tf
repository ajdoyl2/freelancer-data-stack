# Snowflake Database
resource "snowflake_database" "main" {
  name    = var.database_name
  comment = "Database for ${var.project_name} ${var.environment} environment"

  data_retention_time_in_days = var.environment == "prod" ? 90 : 1
}

# Snowflake Warehouse
resource "snowflake_warehouse" "main" {
  name         = "${upper(var.project_name)}_${upper(var.environment)}_WH"
  warehouse_size = var.warehouse_size
  
  auto_suspend = var.auto_suspend
  auto_resume  = true
  
  comment = "Warehouse for ${var.project_name} ${var.environment} environment"
}

# Snowflake Schemas
resource "snowflake_schema" "schemas" {
  for_each = toset(var.schemas)
  
  database = snowflake_database.main.name
  name     = upper(each.key)
  comment  = "Schema for ${each.key} in ${var.environment} environment"

  data_retention_time_in_days = var.environment == "prod" ? 90 : 1
}

# Snowflake Role for the application
resource "snowflake_role" "app_role" {
  name    = "${upper(var.project_name)}_${upper(var.environment)}_ROLE"
  comment = "Role for ${var.project_name} application in ${var.environment} environment"
}

# Snowflake User for the application
resource "snowflake_user" "app_user" {
  name         = "${upper(var.project_name)}_${upper(var.environment)}_USER"
  login_name   = "${lower(var.project_name)}_${lower(var.environment)}_user"
  comment      = "User for ${var.project_name} application in ${var.environment} environment"
  
  default_warehouse = snowflake_warehouse.main.name
  default_role      = snowflake_role.app_role.name
  default_namespace = "${snowflake_database.main.name}.${snowflake_schema.schemas["RAW"].name}"
  
  must_change_password = false
}

# Grant role to user
resource "snowflake_role_grants" "app_role_grants" {
  role_name = snowflake_role.app_role.name
  
  users = [snowflake_user.app_user.name]
}

# Grant warehouse usage to role
resource "snowflake_warehouse_grant" "app_warehouse_grant" {
  warehouse_name = snowflake_warehouse.main.name
  privilege      = "USAGE"
  
  roles = [snowflake_role.app_role.name]
}

# Grant database usage to role
resource "snowflake_database_grant" "app_database_grant" {
  database_name = snowflake_database.main.name
  privilege     = "USAGE"
  
  roles = [snowflake_role.app_role.name]
}

# Grant schema privileges to role
resource "snowflake_schema_grant" "app_schema_grants" {
  for_each = snowflake_schema.schemas
  
  database_name = snowflake_database.main.name
  schema_name   = each.value.name
  privilege     = "ALL"
  
  roles = [snowflake_role.app_role.name]
}

# File format for CSV
resource "snowflake_file_format" "csv_format" {
  name     = "CSV_FORMAT"
  database = snowflake_database.main.name
  schema   = snowflake_schema.schemas["RAW"].name
  
  format_type = "CSV"
  
  field_delimiter = ","
  skip_header     = 1
  null_if         = ["NULL", "null", ""]
  empty_field_as_null = true
  compression     = "AUTO"
  
  comment = "CSV file format for data ingestion"
}

# File format for JSON
resource "snowflake_file_format" "json_format" {
  name     = "JSON_FORMAT"
  database = snowflake_database.main.name
  schema   = snowflake_schema.schemas["RAW"].name
  
  format_type = "JSON"
  
  compression = "AUTO"
  
  comment = "JSON file format for data ingestion"
}

# File format for Parquet
resource "snowflake_file_format" "parquet_format" {
  name     = "PARQUET_FORMAT"
  database = snowflake_database.main.name
  schema   = snowflake_schema.schemas["RAW"].name
  
  format_type = "PARQUET"
  
  compression = "AUTO"
  
  comment = "Parquet file format for data ingestion"
}
