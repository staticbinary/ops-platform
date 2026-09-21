resource "kubernetes_namespace_v1" "this" {
  metadata {
    name = var.namespace_name

    labels = {
      managed_by = "terraform"
      purpose    = "learning"
    }
  }
}