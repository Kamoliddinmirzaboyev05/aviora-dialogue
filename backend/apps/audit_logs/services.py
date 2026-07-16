from apps.audit_logs.models import AuditLog


def record_audit(*, workspace, actor=None, action: str, resource, summary: str, metadata=None):
    return AuditLog.objects.create(
        workspace=workspace,
        actor=actor,
        action=action,
        resource_type=resource.__class__.__name__,
        resource_id=str(resource.id),
        summary=summary,
        metadata=metadata or {},
    )
