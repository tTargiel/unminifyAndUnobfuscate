function module(exports, require, moduleObject) {
    let Meteor, models, AuthorizationUtils;

    moduleObject.export({
        hasAllPermission: () => checkAllPermissions,
        hasAtLeastOnePermission: () => checkAtLeastOnePermission,
        userHasAllPermission: () => userHasAllPermissions,
        hasPermission: () => checkPermission,
        willHavePermission: () => willHavePermission
    });

    moduleObject.link("meteor/meteor", { Meteor(meteor) { Meteor = meteor; } }, 0);
    moduleObject.link("../../models/client", { "*"(model) { models = model; } }, 1);
    moduleObject.link("../lib/AuthorizationUtils", { AuthorizationUtils(authUtils) { AuthorizationUtils = authUtils; } }, 2);

    let isString = value => typeof value === "string" && value in models;
    let isUserInRole = value => typeof value === "object" && value !== null && typeof value.isUserInRole === "function";

    let checkRole = (checkFunction, context, permission, userId, restrictedRoles) => {
        let user = models.Users.findOneById(userId, { fields: { roles: 1 } });
        let boundCheckFunction = checkFunction.bind(context);

        return boundCheckFunction(permission => {
            var roles;
            if (user && user.roles && AuthorizationUtils.isPermissionRestrictedForRoleList(permission, user.roles)) return false;

            let chatPermission = models.ChatPermissions.findOne(permission, { fields: { roles: 1 } });
            let roleList = (roles = chatPermission ? chatPermission.roles : undefined) !== null && roles !== undefined ? roles : [];

            return roleList.some(role => {
                let roleData = models.Roles.findOne(role, { fields: { scope: 1 } });
                let scope = roleData ? roleData.scope : undefined;

                if (!isString(scope)) return false;

                let scopeModel = models[scope];
                return (restrictedRoles && restrictedRoles.includes(role)) || (isUserInRole(scopeModel) ? scopeModel.isUserInRole(userId, role, permission) : undefined);
            });
        });
    };

    let checkSomeRoles = checkRole.bind(null, Array.prototype.some);
    let checkEveryRole = checkRole.bind(null, Array.prototype.every);

    let checkPermissions = (permissions, context, checkFunction, userId, restrictedRoles) => {
        var currentUserId;
        return !!((userId = (currentUserId = userId) !== null && currentUserId !== undefined ? currentUserId : Meteor.userId()) && models.AuthzCachedCollection.ready.get()) && checkFunction(permissions.concat(), context, userId, restrictedRoles);
    };

    let checkAllPermissions = (permissions, context, restrictedRoles) => checkPermissions(permissions, context, checkEveryRole, undefined, restrictedRoles);
    let checkAtLeastOnePermission = (permissions, context) => checkPermissions(permissions, context, checkSomeRoles);
    let userHasAllPermissions = (permissions, context, restrictedRoles) => checkPermissions(permissions, context, checkEveryRole, restrictedRoles);
    let checkPermission = checkAllPermissions;
    let willHavePermission = (permissions, restrictedRoles) => checkPermissions(permissions, undefined, checkEveryRole, undefined, restrictedRoles);
}

//# sourceMappingURL=/dynamic/app/authorization/client/1a80a8375f5ab873acfcf269319fcef92024b830.map