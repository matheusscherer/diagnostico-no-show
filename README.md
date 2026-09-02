# Diagnóstico de No-Show

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT" />
</p>

**Problema de negócio:** clientes marcam horário e não aparecem.  
A agenda fica ociosa. O dinheiro não entra.

Este projeto transforma a planilha de agendamentos em um diagnóstico objetivo:

- Quanto de **receita foi perdida**
- Quanto custou a **ociosidade** do profissional
- Onde o problema se concentra (horário, canal, profissional, serviço)
- Quanto dá para **recuperar** com lista de espera e confirmação

> Feito para ser lido por gestor e executado por analista.

---

## O que ele entrega

| Saída | Descrição |
|-------|-----------|
| Resumo executivo | Receita perdida, taxa de no-show, impacto total |
| Ranking por profissional | Quem mais sofre com no-show |
| Ranking por horário | Em quais faixas o buraco é maior |
| Ranking por canal | WhatsApp vs Instagram vs Telefone |
| Ranking por serviço | Quais serviços mais falham |
| Efeito da confirmação | Taxa com vs sem confirmação |
| Relatório Markdown | Pronto para enviar no WhatsApp/e-mail |
| Excel detalhado | Abas por dimensão + resumo |

---

## Como rodar (3 minutos)

```bash
git clone https://github.com/matheusscherer/diagnostico-no-show.git
cd diagnostico-no-show

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

python -m diagnostico_no_show
pytest -v
```

Arquivos gerados em `outputs/`:
- `diagnostico_no_show.md`
- `diagnostico_no_show.xlsx`

### Com seus dados

```bash
python -m diagnostico_no_show \
  --agendamentos caminho/seus_agendamentos.csv \
  --profissionais caminho/seus_profissionais.csv \
  --recovery-rate 0.25
```

---

## Formato dos arquivos

### agendamentos.csv
```text
id,data,hora,profissional,servico,ticket,status,canal,confirmado
AGD-001,2026-08-15,14:30,Ana,Corte + barba,80.00,no_show,Instagram,nao
```

`status` aceitos: `compareceu` · `no_show` · `cancelado` · `remarcado`

### profissionais.csv (opcional)
```text
profissional,custo_hora,capacidade_dia
Ana,45.00,8
```

---

## Lógica do diagnóstico

1. **Receita perdida** = soma do `ticket` dos status `no_show`
2. **Taxa de no-show** = no_shows ÷ (compareceu + no_show)
3. **Custo de ociosidade** = no_shows × custo/hora do profissional (1 slot ≈ 1h)
4. **Potencial de recuperação** = receita perdida × taxa conservadora (default 25%)
5. **Confirmação** = compara taxa de no-show com vs sem confirmação prévia

Cancelados e remarcados ficam de fora da taxa (não consumiram o slot da mesma forma).

---

## Estrutura do projeto

```text
diagnostico-no-show/
├── data/raw/                 # dados de exemplo
├── src/diagnostico_no_show/
│   ├── analyzer.py           # orquestração
│   ├── loader.py             # validação de entrada
│   ├── metrics.py            # cálculos de impacto
│   ├── models.py             # domínio
│   ├── report.py             # Markdown + Excel
│   └── cli.py                # interface de linha de comando
├── tests/                    # unitários + integração
└── outputs/                  # relatórios gerados
```

---

## Testes

```bash
pytest -v
```

CI roda em Python 3.10, 3.11 e 3.12 a cada push.

---

## Por que este projeto importa

A maioria das agendas só mostra “faltou”.  
Este mostra **dinheiro**:

- Quanto deixou de entrar
- Quanto o profissional ficou parado
- Em qual horário e canal atacar primeiro

É o tipo de entregável que gestor entende em 30 segundos.

Ideal para clínicas, salões e profissionais liberais que querem transformar planilha de falta em decisão de negócio.

---

## Premissas e limites

- Dados de exemplo são sintéticos
- 1 slot ≈ 1 hora de ociosidade (simplificação consciente)
- Potencial de recuperação é conservador (25% por padrão)
- Não conecta em sistema de agenda — lê CSV
- Não é previsão. É diagnóstico de um ciclo fechado

---

## Autor

**Matheus Scherer** · Porto Alegre, RS  
Diagnóstico de custo operacional com Python

[GitHub](https://github.com/matheusscherer) · [LinkedIn](https://linkedin.com/in/scherermatheus) · [Site](https://mtsch-site.vercel.app)
