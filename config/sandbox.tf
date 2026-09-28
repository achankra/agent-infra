# One ephemeral, isolated workspace per run. Checkout, loop, builds, tests.
# Nothing persists.

locals {
  # worktree | container | microvm
  kind = "worktree"

  # deny | allowlist
  network = "deny"

  ttl_minutes  = 30
  cpu_limit    = 2
  memory_limit = "4Gi"
}

resource "kubernetes_pod" "agent_runner" {
  metadata {
    generate_name = "agent-run-"
    namespace     = "platform-agents"
  }
  spec {
    restart_policy                  = "Never"
    automount_service_account_token = false
    security_context {
      run_as_non_root = true
      run_as_user     = 10001
    }
    container {
      name  = "runner"
      image = "ghcr.io/acme/agent-runner:2.1.0"
      resources {
        limits = {
          cpu    = local.cpu_limit
          memory = local.memory_limit
        }
      }
    }
  }
}
