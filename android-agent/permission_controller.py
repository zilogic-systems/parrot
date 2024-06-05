from android.permissions import request_permissions, Permission, check_permission

class PermissionController:
    def __init__(self) -> None:
        self.bt_permissions = [Permission.BLUETOOTH_CONNECT, Permission.BLUETOOTH_SCAN, Permission.ACCESS_FINE_LOCATION]

    def permission_status_callback(self, permissions, grants):
        print(f"PERMISSIONS {permissions} GRANTS : {grants}")

    def request_permission(self, requesting_permissions):
        request_permissions([*requesting_permissions], self.permission_status_callback)

    def request_bluetooth_permissions(self):
        permission_status = {}
        for permission in self.bt_permissions:
            response = check_permission(permission)
            permission_status[permission] = response
            print(f"{permission}: {response}")
        requesting_permissions = list(filter(lambda permission: not permission_status.get(permission), permission_status))
        if requesting_permissions:
            self.request_permission(requesting_permissions)
