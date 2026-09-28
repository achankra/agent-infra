# Grafana and Prometheus

Every lab ends here. Run the path, come back, see what moved.

## Homebrew, macOS and Linux

```
brew install grafana prometheus
brew services start grafana

cd agent-infra
prometheus --config.file=grafana/prometheus.yml --storage.tsdb.path=/tmp/agent-infra-prom
```

Grafana at http://localhost:3000, login admin / admin. Add a Prometheus data
source pointing at http://localhost:9090, then import
`grafana/dashboards/agent-infra.json`.

## Windows

Download the Prometheus and Grafana zip releases, then:

```
prometheus.exe --config.file=grafana\prometheus.yml
grafana-server.exe
```

## What the dashboard shows

| Row | Panels | Which module fills it |
|---|---|---|
| Governance | governance events by action, denials by check, identities | 3 |
| Capability | tool calls by operation and system | 2 |
| Context | context tokens, sources assembled | 4 |
| Execution | loop stops by reason, iterations, cost | 5 |
| Evaluation | gate runs pass and fail, eval score, bands | 6 |

If a panel reads 0 rather than "No data", the metric exists and nothing has
moved it yet. That is the correct reading before the matching module.
