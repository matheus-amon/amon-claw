---
name: docs-sync
description: Workflow para sincronizar logs de desenvolvimento e arquivos de documentação com o MkDocs. Use sempre que o usuário pedir para "atualizar os logs", "sincronizar mkdocs" ou após finalizar uma tarefa importante para manter o histórico do projeto.
---

# Docs Sync Workflow

Esta skill automatiza a manutenção do histórico e da documentação do projeto, garantindo que o `mkdocs.yml` esteja sempre sincronizado com os arquivos em `docs/`.

## Workflow

### 1. Gerar Log de Desenvolvimento
Sempre que uma tarefa for concluída, crie um novo log em `docs/logs/YYYY-MM-DD-<topic>.md`.
- Use o `git diff` ou as atividades da sessão para resumir o que foi feito.
- Siga o padrão: Contexto, Atividades Realizadas, Resultados, Próximos Passos.

### 2. Sincronizar MkDocs
O arquivo `mkdocs.yml` deve ser a fonte da verdade para a navegação.

#### Logs/Changelog
- Leia o diretório `docs/logs/`.
- Atualize a seção `nav -> 📜 Changelog`.
- Mantenha a ordem **decrescente** (mais recente no topo).

#### Specs e Planos
- Leia `docs/superpowers/specs/` e `docs/superpowers/plans/`.
- Certifique-se de que todos os arquivos `.md` novos estão listados no `mkdocs.yml` sob as seções correspondentes.

## Regras de Ouro
- Nunca remova entradas antigas do `mkdocs.yml`, apenas adicione novas ou reordene.
- Mantenha os nomes das seções amigáveis (ex: use emojis se o projeto já usar).
- Valide se os caminhos dos arquivos no `mkdocs.yml` estão corretos (relativos à pasta `docs/`).

## Exemplo de Comando
"Atualize os logs e sincronize o mkdocs com as mudanças de hoje."

1. `git log -n 5` para ver o que mudou.
2. `write_file` para criar o novo log.
3. `replace` no `mkdocs.yml` para atualizar a navegação.
