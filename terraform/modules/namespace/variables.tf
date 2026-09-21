variable "namespace_name" {
  description = "Name of the Kubernetes namespace."
  type        = string

  validation {
    condition = can(regex(
      "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$",
      var.namespace_name
    )) && length(var.namespace_name) <= 63

    error_message = "Namespace name must be 1-63 characters, lowercase alphanumeric or hyphens, and start and end with an alphanumeric character."
  }
}