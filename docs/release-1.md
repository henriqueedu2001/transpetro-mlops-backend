# Release 1 — configuração e controle dos treinamentos

Esta entrega fecha o fluxo entre a página web, a API, o scheduler e o processo de treinamento. A configuração validada na API é salva em `training_config.json` e é a mesma que o treinador fornece ao Ultralytics.

## Funcionalidades entregues

### Seleção do modelo

- Famílias disponíveis: YOLOv8, YOLO11, YOLO12 e YOLO26.
- Tamanhos disponíveis em cada família: Nano (`n`), Small (`s`), Medium (`m`), Large (`l`) e Extra Large (`x`).
- O checkpoint é construído de forma controlada, por exemplo `yolo11s.pt`; não é aceito um caminho arbitrário como modelo.

### Hiperparâmetros

A página permite configurar `epochs`, `batch`, `workers`, `imgsz`, `device`, `patience`, `optimizer`, `lr0`, `lrf`, `momentum`, `weight_decay`, `warmup_epochs`, `cos_lr`, `close_mosaic`, `seed` e `deterministic`. A API valida tipos e limites antes de criar o job.

### args.yaml opcional

Um arquivo `.yaml` ou `.yml` de até 64 KiB pode complementar a configuração. Seus valores têm precedência sobre os campos equivalentes da página. Também são aceitos parâmetros de execução e aumento de dados selecionados, como `amp`, `cache`, `fraction`, `hsv_h`, `degrees`, `translate`, `scale`, `flipud`, `fliplr`, `mosaic` e `mixup`.

Por segurança e reprodutibilidade, o YAML não pode alterar `data`, `model`, `project`, `name`, `exist_ok`, `save_dir` ou `resume`. Chaves desconhecidas e valores fora dos intervalos válidos são recusados com HTTP 422.

Exemplo:

```yaml
lr0: 0.005
amp: true
mosaic: 0.8
fliplr: 0.5
```

### Estados e controle dos jobs

O ciclo de vida canônico é:

```text
queued → running → succeeded
                 ↘ failed
queued/running → cancelled
failed/cancelled/succeeded → queued (reinício)
```

- **Abortar:** um job na fila é cancelado imediatamente; durante a execução, o scheduler recebe a solicitação, encerra o grupo de processos do treinador e registra `cancelled`.
- **Reiniciar:** recoloca um job terminal na fila, limpa datas e erro anteriores e incrementa o número da tentativa.
- **Falhas:** um retorno diferente de zero ou uma exceção produz o estado `failed` e uma mensagem resumida no banco.

### Logs

- `logs/system.log`: eventos estruturados do scheduler (`job_started`, `job_succeeded`, `job_failed` e `job_cancelled`).
- `files/train_<id>_<projeto>/job.log`: saída completa do treinador, preservada entre tentativas.
- `GET /jobs/{job_id}/logs`: consulta do log de um job. A visualização dinâmica dentro da página continua planejada para a Release 2.

### Upload e artefatos

- O dataset deve ser um ZIP válido e é extraído em um diretório próprio.
- A extração rejeita caminhos que escapem do diretório do treinamento.
- A plataforma usa o `data.yaml` do dataset quando ele existe. Como compatibilidade, também reconhece `train/images` e `val/images` e produz um `data.yaml` básico.
- Após o sucesso, continuam disponíveis o download do `best.pt` e o ZIP de todos os artefatos.

## Verificação desta entrega

Os testes automatizados cobrem a composição da configuração, a precedência do YAML, a rejeição de chaves protegidas/desconhecidas, dispositivos inválidos e arquivos ZIP maliciosos. A interface é verificada com `npm run build`.

Antes de iniciar uma instalação existente, execute uma vez:

```bash
env/bin/python scripts/migrate_release_1.py
```

A migração preserva os registros, converte `created` em `queued` e `finished` em `succeeded`. Como o processo anterior não pode ser reassumido com segurança, um job encontrado em `processing` é registrado como `failed`. Jobs legados não podem ser reiniciados porque não possuem o novo arquivo de configuração efetiva; para repeti-los, crie um treinamento novo.

## Correções após validação integrada

- O polling do scheduler encerra sua transação de leitura a cada consulta, permitindo detectar jobs criados depois que o processo foi iniciado.
- O otimizador automático é normalizado para `auto`, como exigido pelo Ultralytics; configurações anteriores com `Auto` também são aceitas pelo treinador.
- O campo `lr0` usa incrementos de `0.000001`, tornando o valor padrão `0.01` válido no navegador e permitindo ajustes pequenos.

Quando o otimizador está em modo automático, o próprio Ultralytics escolhe o otimizador, `lr0` e `momentum`. Para aplicar manualmente esses dois parâmetros, selecione um otimizador explícito.
