'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from django.views import static
from ism import settings
from ism.view import home, common
from ism.view.members import access as member_access,\
                             details as member_details,\
                             history as member_history,\
                             list as member_list
from ism.view.titles import details as title_details,\
                            list as title_list,\
                            members as title_members,\
                            changes as title_changes
from ism.view.roles import list as role_list,\
                           details as role_details
from ism.view.assets import normal as asset_normal,\
                            diff as asset_diff



 

admin.autodiscover()

DATE = r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})"

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # ISM views
    (r'^%s$' % settings.LOGIN_URL[1:], 'django.contrib.auth.views.login', {'template_name' : 'session/login.html'}),
    (r'^%s$' % settings.LOGOUT_URL[1:], 'django.contrib.auth.views.logout', {'next_page' : '/'}),
    (r'^user/change_password$', 'django.contrib.auth.views.password_change', {'template_name' : 'session/password_change.html', 'post_change_redirect' : '/'}), 
    
    
    (r'^$',                                         home.home),
    (r'^corp$',                                     common.corp),
    
    (r'^cron$',                                     common.trigger_scheduler),
    (r'^tasks$',                                    common.task_list),
    (r'^tasks/launch/([^/]+)$',                     common.launch_task),

    (r'^members$',                                  member_list.all),
    (r'^members/data$',                             member_list.all_data),
    (r'^members/history$',                          member_history.history),
    (r'^members/history/data$',                     member_history.history_data),
    (r'^members/access_changes$',                   member_access.access_changes),
    (r'^members/access_changes/data$',              member_access.access_changes_data),
    (r'^members/(\d+)$',                            member_details.details),
    (r'^members/(\d+)/access_changes_data',         member_details.access_changes_member_data),
    
    (r'^titles$',                                   title_list.all),
    (r'^titles/data$',                              title_list.all_data),
    (r'^titles/changes$',                           title_changes.changes),
    (r'^titles/changes/data$',                      title_changes.changes_data),
    (r'^titles/(\d+)$',                             title_details.details),
    (r'^titles/(\d+)/composition_data$',            title_details.composition_data),
    (r'^titles/(\d+)/compo_diff_data$',             title_details.compo_diff_data),
    (r'^titles/(\d+)/members$',                     title_members.members),
    (r'^titles/(\d+)/members/data$',                title_members.members_data),
    
    (r'^roles$',                                    role_list.root),
    (r'^roles/update$',                             role_list.update_access_level),
    (r'^roles/([a-zA-Z_]+)$',                       role_list.role_type),
    (r'^roles/([a-zA-Z_]+)/data$',                  role_list.role_type_data),
    (r'^roles/([a-zA-Z_]+)/(\d+)$',                 role_details.role),
    (r'^roles/([a-zA-Z_]+)/(\d+)/data$',            role_details.role_data),
    
    (r'^assets$',                                   asset_normal.stations),
    (r'^assets/(\d+)$',                             asset_normal.hangars),
    (r'^assets/(\d+)/(\d+)$',                       asset_normal.hangar_contents),
    (r'^assets/(\d+)/(\d+)/(\d+)$',                 asset_normal.can1_contents),
    (r'^assets/(\d+)/(\d+)/(\d+)/(\d+)$',           asset_normal.can2_contents),
    (r'^assets/search$',                            asset_normal.search_items),

    (r'^assets/changes$',                           asset_diff.last_stations),
    (r'^assets/changes/' + DATE + '$',              asset_diff.stations),
    (r'^assets/changes/' + DATE + '/(\d+)$',        asset_diff.hangars),
    (r'^assets/changes/' + DATE + '/(\d+)/(\d+)$',  asset_diff.hangar_contents),
    (r'^assets/changes/' + DATE + '/search$',       asset_diff.search_items),

    # STATIC FILES SERVING FOR THE DEVELOPMENT SERVER
    (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], static.serve, {'document_root' : settings.MEDIA_ROOT}),
)
