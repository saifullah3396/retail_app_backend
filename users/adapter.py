from allauth.account.adapter import DefaultAccountAdapter


class AppAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        data = form.cleaned_data

        # set user permission groups
        for group in data.get('groups'):
            user.groups.add(group)

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
