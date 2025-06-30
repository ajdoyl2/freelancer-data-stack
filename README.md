# Freelancer Data Stack

Welcome to the Freelancer Data Stack repository. This project aims to provide an integrated data stack for managing and analyzing data. Below is an overview of the folder structure:

```
infra/terraform
  docker/
  orchestration/dagster
  ingestion/airbyte
  ingestion/dlt
  transformation/dbt
  quality/great_expectations
  viz/{evidence,metabase,streamlit}
  catalog/datahub
  mcp-server
```

## Getting Started

This repository contains the code and configurations required to set up a complete data stack for freelancers. Each folder corresponds to a different part of the stack:

- **infra/terraform**: Infrastructure as Code using Terraform.
- **docker/**: Docker configurations.
- **orchestration/dagster**: Pipeline orchestration using Dagster.
- **ingestion/airbyte**: Data ingestion configurations for Airbyte.
- **ingestion/dlt**: Data Loading Tool (DLT) setup.
- **transformation/dbt**: Data transformation scripts using dbt.
- **quality/great_expectations**: Data quality checks using Great Expectations.
- **viz/**: Visualization tools. Reports are generated with Evidence, Metabase, and Streamlit.
- **catalog/datahub**: Data catalog using DataHub.
- **mcp-server**: Server components for managing and controlling processes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to explore the repository and contribute to the development of the freelancer data stack!
