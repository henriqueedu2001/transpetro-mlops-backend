### 2. Descrição dos Endpoints Propostos (Backend - FastAPI)

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| **POST** | `/trainings/` | Recebe os dados do formulário (multipart/form-data): `train_name`, `project_name`, `project_owner`, `epochs`, `batch`, `workers` e o arquivo do dataset (`file`). Cria os registros nas tabelas `train`, `params` e `jobs` (status `created`), retornando o `train_id` e `job_id` gerados. |
| **GET** | `/jobs/` | Lista todos os jobs com seus respectivos status e parâmetros. Retorna um *array* de objetos contendo: `id`, `train_id`, `status`, `created_at`, `scheduled_at`, `finished_at`, `train_name`, `project_name`, `project_owner`, `epochs`, `batch`, `workers`. (Idealmente realiza um `JOIN` entre as tabelas). |
| **GET** | `/trainings/{train_id}/download/zip` | Faz o download do pacote completo de saída do treinamento (`.zip`) para o `train_id` informado. Retorna o arquivo com `Content-Disposition: attachment`. |
| **GET** | `/trainings/{train_id}/download/model` | Faz o download apenas do modelo treinado (`.pt`) para o `train_id` informado. Retorna o arquivo binário. |
| **GET** | `/trainings/{train_id}/metrics` | Retorna um JSON com os parâmetros utilizados no treinamento: `{ "epochs": 100, "batch": 16, "workers": 8 }`. | 
| *(Opcional)* **GET** | `/trainings/{train_id}/status` | Retorna o status atual do job para um `train_id` específico. (Não é estritamente necessário, pois a lista `/jobs/` já contém todos). |
