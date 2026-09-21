output "namespace_name" {
  description = "Name of the Terraform-managed namespace."
  value       = kubernetes_namespace_v1.lab.metadata[0].name
}

output "namespace_uid" {
  description = "Kubernetes UID assigned to the namespace."
  value       = kubernetes_namespace_v1.lab.metadata[0].uid
}