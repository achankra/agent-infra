# The pool the ephemeral workspaces are drawn from. Capacity and cost are
# control functions: hundreds of agents do not run on laptops.

locals {
  pool_name       = "agent-runtime-pool"
  min_nodes       = 0
  max_nodes       = 20
  max_concurrent_runs = 8
  scale_to_zero_after_minutes = 10
}
