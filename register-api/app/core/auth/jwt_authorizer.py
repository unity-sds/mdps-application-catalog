
class JWTAuthorizer:
       
    def __init__(self):
        pass

    def get_username(self) -> str:
        pass

    def get_groups(self) -> list[str]:
        pass

    def get_token(self) -> str:
        return None

    # Function to check mambership in a group for valid namespace ops
    def is_valid_namespace_op(self, namespace) -> bool:
        if namespace not in self.get_groups() and namespace != self.get_username():
            return False
        else:
            return True
        
        