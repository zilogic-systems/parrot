from android.permissions import request_permissions, Permission, check_permission

class PermissionController:
    def __init__(self) -> None:
        self.bt_permissions = [Permission.BLUETOOTH_CONNECT, Permission.BLUETOOTH_SCAN]
        self.location_permissions = [Permission.ACCESS_FINE_LOCATION]

    def permission_status_callback(self, permissions, grants):
        print(f"PERMISSIONS {permissions} GRANTS : {grants}")

    def request_location(self):
        permission_status = {}
        for permission in self.location_permissions:
              response = check_permission(permission)
              permission_status[permission] = response
              print(f"{permission} : {response}")
        requesting_permissions = filter(lambda permission: not permission_status.get(permission), permission_status)
        request_permissions([*requesting_permissions], self.permission_status_callback)

    def request_bluetooth(self):
        loc_permission_status = {}
        for permission in self.bt_permissions:
            response = check_permission(permission)
            loc_permission_status[permission] = response
            print(f"{permission}: {response}")
        requesting_permission = filter(lambda permission: not loc_permission_status.get(permission), loc_permission_status)
        request_permissions([*requesting_permission], self.permission_status_callback)