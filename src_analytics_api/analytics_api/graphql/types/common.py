import strawberry


@strawberry.input
class TenantInput:
  tenant_identifier: str

  def validate(self):
    if len(self.tenant_identifier) != 6:
      raise ValueError('Tenant ID must be exactly 6 characters long')
