# Dados de entrada

## agendamentos.csv

Cada linha = um horário marcado na agenda.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | texto | Identificador único do agendamento |
| data | data (YYYY-MM-DD) | Data do horário |
| hora | texto (HH:MM) | Horário |
| profissional | texto | Quem atenderia |
| servico | texto | Serviço agendado |
| ticket | número | Valor do serviço em R$ |
| status | texto | `compareceu` · `no_show` · `cancelado` · `remarcado` |
| canal | texto | Como o cliente marcou (WhatsApp, Instagram, Telefone…) |
| confirmado | texto | `sim` ou `nao` |

## profissionais.csv (opcional)

Usado para calcular o custo da ociosidade.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| profissional | texto | Nome (deve bater com agendamentos) |
| custo_hora | número | Custo da hora ociosa em R$ |
| capacidade_dia | número | Slots disponíveis por dia |

Dados de exemplo são sintéticos e servem só para demonstração.
