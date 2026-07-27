# AGENTS.md — Instruções para agentes que editam estas docs

Este é o repositório da **documentação PÚBLICA** da BRZ API (`docs.brzip.com.br`).
Tudo aqui vira documentação exposta a clientes externos. Trate cada mudança
como algo que o cliente vai ler e usar para integrar.

## ⛔ Regra dura: NUNCA documentar rotas internas

A API pública é servida pelo gateway `gw-core-pix`. Só documente o que esse
gateway expõe publicamente (rotas com `DualAuth`/API Key + `RequireScope`).

**NÃO documente, sob nenhuma hipótese:**
- Rotas protegidas por `InternalAuth` / autenticação service-to-service (S2S).
- Endpoints internos de outros microserviços (ex.: `gw-account-service`,
  `gw-ledger-service`, `gw-wallet-service`) que não passam pelo gateway público.
- Rotas administrativas, de operação, ou de troubleshooting.
- Contratos/versões que não são de fato servidos em produção (ex.: prefixos
  `beta` inventados, endpoints "planejados" que ainda não existem).

Regra prática: **se não está sendo servido pelo gateway público, sai da doc.**
Na dúvida sobre se uma rota é pública, confirme no roteador do `gw-core-pix`
(`internal/api/router.go`) antes de documentar. O que não sabemos confirmar,
removemos — não inventamos.

## Fonte da verdade

- `fern/openapi.yaml` é a **fonte** da OpenAPI spec. O `openapi.json` na raiz é
  **gerado** a partir dela no deploy (ver `.github/workflows/deploy-pages.yml`).
  Edite sempre o YAML; regenere o JSON com o mesmo script do workflow.
- As páginas-guia (`.mdx`) e a spec precisam refletir o **código real** servido,
  não o comportamento desejado. Ao documentar request/response, confira o
  handler real no `gw-core-pix`.
- Envelope de resposta do `gw-core-pix`: sucesso = `{"success": true, "data": ...}`;
  erro = `{"success": false, "error": {"code", "message"}}`.

## Refactor em andamento (pendências conhecidas)

- **`account_type` → `account_role`**: há um refactor em curso que renomeia o
  campo `account_type` para `account_role`. Quando o refactor chegar em produção,
  atualize a doc (guias de conta + openapi) para o novo nome. Até lá, o campo
  documentado permanece `account_type`.
