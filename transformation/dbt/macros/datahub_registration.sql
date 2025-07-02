{% macro register_with_datahub() %}
  {% if execute %}
    {% set datahub_config = {
      'datahub_rest_url': env_var('DATAHUB_REST_URL', 'http://localhost:8080'),
      'datahub_token': env_var('DATAHUB_TOKEN', ''),
      'platform': 'dbt',
      'env': target.name
    } %}

    {% set manifest_path = target.path ~ '/manifest.json' %}
    {% set catalog_path = target.path ~ '/catalog.json' %}

    {{ log("Registering dbt manifest with DataHub for environment: " ~ target.name, info=True) }}

    {% set datahub_command %}
    datahub ingest -c datahub_dbt_config.yml
    {% endset %}

    {{ log("DataHub registration command: " ~ datahub_command, info=True) }}
  {% endif %}
{% endmacro %}
