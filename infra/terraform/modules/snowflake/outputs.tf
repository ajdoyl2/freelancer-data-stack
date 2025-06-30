output "database_name" {
  description = "Name of the Snowflake database"
  value       = snowflake_database.main.name
}

output "warehouse_name" {
  description = "Name of the Snowflake warehouse"
  value       = snowflake_warehouse.main.name
}

output "schemas" {
  description = "List of Snowflake schemas created"
  value       = { for k, v in snowflake_schema.schemas : k => v.name }
}

output "app_role_name" {
  description = "Name of the application role"
  value       = snowflake_role.app_role.name
}

output "app_user_name" {
  description = "Name of the application user"
  value       = snowflake_user.app_user.name
}

output "app_user_login_name" {
  description = "Login name of the application user"
  value       = snowflake_user.app_user.login_name
  sensitive   = true
}

output "file_formats" {
  description = "File formats created"
  value = {
    csv     = snowflake_file_format.csv_format.name
    json    = snowflake_file_format.json_format.name
    parquet = snowflake_file_format.parquet_format.name
  }
}
