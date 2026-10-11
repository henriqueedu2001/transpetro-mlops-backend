# Contrato HTTP — Release 1

## Catálogo e criação

| Método | Endpoint | Resultado |
| --- | --- | --- |
| `GET` | `/models` | Famílias YOLO e tamanhos aceitos pela plataforma. |
| `POST` | `/trainings/` | Valida a configuração, recebe dataset/args.yaml e cria o treinamento com estado `queued`. |

`POST /trainings/` usa `multipart/form-data`. Os campos de texto obrigatórios são `train_name`, `project_name` e `project_owner`; `file` deve ser um ZIP. O arquivo `args_yaml` é opcional. Os demais campos e seus padrões estão disponíveis no Swagger em `/docs`.

Resposta de criação (`201`):

```json
{
  "train_id": 42,
  "status": "queued",
  "model": "yolo11s.pt",
  "configuration": {
    "model_version": "yolo11",
    "model_size": "s",
    "arguments": { "epochs": 100, "batch": 16 }
  }
}
```

## Jobs

| Método | Endpoint | Resultado |
| --- | --- | --- |
| `GET` | `/jobs/` | Lista os jobs, parâmetros principais, estado, datas, erro e número da tentativa. |
| `POST` | `/jobs/{job_id}/cancel` | Cancela um job na fila ou solicita a interrupção de um job em execução. |
| `POST` | `/jobs/{job_id}/restart` | Recoloca um job terminal na fila e incrementa a tentativa. |
| `GET` | `/jobs/{job_id}/logs` | Retorna a saída textual acumulada do treinador. |

O controle retorna `404` para job inexistente e `409` quando a transição não é válida para o estado atual.

## Artefatos

| Método | Endpoint | Resultado |
| --- | --- | --- |
| `GET` | `/downloads/model?train_id={id}` | Modelo `best.pt` do treinamento concluído. |
| `GET` | `/downloads/zip?train_id={id}` | ZIP com configuração, logs e artefatos do treinamento. |

Arquivos ainda indisponíveis retornam `404`.
