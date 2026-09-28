# The tool gateway. One doorway in front of our own MCP servers.
#
# This is the gateway that governs what an agent can DO. The model gateway in
# model-routes.toml governs what it can THINK WITH. Same pattern, different
# subject.
#
# These are self-hosted MCP servers, one per system, behind a gateway you run
# in-cluster. Hosted tool catalogs solve third-party SaaS auth, which is not
# what an internal IDP needs.

locals {
  gateway_name = "adp-tool-gateway"

  # Only servers listed here can be reached, even if the registry knows about
  # their operations. Two doors, both must be open.
  enabled_servers = [
    "github",
    "knowledge-base",
  ]

  rate_limit_per_minute = 30
  audit_all_calls       = true
}

resource "kubernetes_deployment" "mcp_gateway" {
  metadata {
    name      = local.gateway_name
    namespace = "platform-agents"
  }
  spec {
    replicas = 2
    template {
      spec {
        container {
          name  = "gateway"
          image = "ghcr.io/acme/mcp-gateway:1.4.0"
          env {
            name  = "RATE_LIMIT_PER_MINUTE"
            value = local.rate_limit_per_minute
          }
          env {
            name  = "AUDIT_ALL_CALLS"
            value = local.audit_all_calls
          }
        }
      }
    }
  }
}
