from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from project.models import UserProfile
from django.utils.translation import ugettext_lazy as _
from invoicer.models import Company


class UserProfileAdminInline(admin.StackedInline):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "active_company":
            #TODO: is there a better way ?
            try:
                object_id = request.META['PATH_INFO'].strip('/').split('/')[-1]
                user = User.objects.get(pk=int(object_id))
                companies = Company.objects.filter(authorized_users__in=[user, ])
                kwargs["queryset"] = companies
            except:
                # fix for user/add action
                kwargs["queryset"] = Company.objects.none()
        return super(UserProfileAdminInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    model = UserProfile
    can_delete = False


class UserAdminEx(UserAdmin):
    inlines = [UserProfileAdminInline, ]
    save_on_top = True
    list_select_related = True
    list_display = list(UserAdmin.list_display[:]) + ['is_superuser', 'is_active', 'user_active_company', ]
    list_filter = ['is_active', ]
    search_fields = list(UserAdmin.search_fields)[:]
    filter_horizontal = ['groups', 'user_permissions', ]

    def user_active_company(self, user):
        return user.get_profile().active_company
    user_active_company.short_description = _(u'Active company')

    def save_model(self, request, instance, form, change):
        super(UserAdminEx, self).save_model(request, instance, form, change)
        if change == False:
            super(UserAdminEx, self).save_model(request, instance, form, change)
            #NOTE: destroy the profile created by the post_save signal
            UserProfile.objects.get(user=instance).delete()

    def save_formset(self, request, form, formset, change):
        super(UserAdminEx, self).save_formset(request, form, formset, change)
        #NOTE: if no profile has been created along with the user, save the user again to create one
        if(formset.model == UserProfile):
            try:
                UserProfile.objects.get(user=formset.instance)
            except:
                formset.instance.save()
            try:
                UserProfile.objects.get(user=formset.instance)
            except:
                raise Exception("No user profile has been created")

admin.site.unregister(User)
admin.site.register(User, UserAdminEx)
