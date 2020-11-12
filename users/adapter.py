from allauth.account.adapter import DefaultAccountAdapter
from backend import settings


class AppAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        data = form.cleaned_data

        # set user permission groups
        if data.get('groups') is not None:
            for group in data.get('groups'):
                user.groups.add(group)

            user_authority = -1
            for (group, authority) in \
                    settings.REGISTRATION_GROUPS_WITH_AUTHORITY.items():
                user_authority = \
                    authority if authority > user_authority else user_authority
            user.authority = user_authority

        # add organization to user
        user.organization = data.get('organization')

        # add sub_organization to user
        if data.get('sub_organization'):
            user.sub_organization = data.get('sub_organization')

        # add all authorized locations to user
        for location in data.get('locations'):
            user.authorized_locations.add(location)

        # commit user
        user.save()
        return user
