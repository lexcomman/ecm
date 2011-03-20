'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''

import json

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.text import truncate_words
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q

from esm.core.utils import print_date
from esm.data.roles.models import Member
from esm.data.common.models import ColorThreshold
from esm import settings
from esm.core import utils
from esm.view import getScanDate
from esm.view.members import member_table_columns



#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def all(request):
    colorThresholds = []
    for c in ColorThreshold.objects.all().order_by("threshold"):
        colorThresholds.append({ "threshold" : c.threshold, "color" : c.color })

    data = { 
        'scan_date' : getScanDate(Member.__name__), 
        'colorThresholds' : json.dumps(colorThresholds)
    }
    return render_to_response("members/member_list.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def all_data(request):
    try:
        iDisplayStart = int(request.GET["iDisplayStart"])
        iDisplayLength = int(request.GET["iDisplayLength"])
        sSearch = request.GET["sSearch"]
        sEcho = int(request.GET["sEcho"])
        try:
            column = int(request.GET["iSortCol_0"])
            ascending = (request.GET["sSortDir_0"] == "asc")
        except:
            column = 0
            ascending = True
    except:
        return HttpResponseBadRequest()

    total_members,\
    filtered_members,\
    members = getMembers(first_id=iDisplayStart, 
                         last_id=iDisplayStart + iDisplayLength - 1,
                         search_str=sSearch,
                         sort_by=member_table_columns[column], 
                         asc=ascending)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))






        
#------------------------------------------------------------------------------
def getMembers(first_id, last_id, search_str=None, sort_by="name", asc=True):

    sort_col = "%s_nocase" % sort_by
    
    members = Member.objects.filter(corped=True)

    # SQLite hack for making a case insensitive sort
    members = members.extra(select={sort_col : "%s COLLATE NOCASE" % sort_by})
    if not asc: sort_col = "-" + sort_col
    members = members.extra(order_by=[sort_col])
    
    if search_str:
        total_members = members.count()
        search_args = Q(name__icontains=search_str) | Q(nickname__icontains=search_str)
        
        if "DIRECTOR".startswith(search_str.upper()):
            search_args = search_args | Q(accessLvl=Member.DIRECTOR_ACCESS_LVL)
        
        members = members.filter(search_args)
        filtered_members = members.count()
    else:
        total_members = filtered_members = members.count()
    
    members = members[first_id:last_id]
    
    member_list = []
    for m in members:
        titles = ["Titles"]
        titles.extend([ str(t) for t in m.getTitles() ])
        if m.extraRoles: 
            roles = [ str(r) for r in m.getRoles(ignore_director=True) ]
            if len(roles): roles.insert(0, "Roles")
        else:
            roles = []
        memb = [
            '<a href="/members/%d">%s</a>' % (m.characterID, m.name),
            truncate_words(m.nickname, 5),
            m.accessLvl,
            m.extraRoles,
            print_date(m.corpDate),
            print_date(m.lastLogin),
            truncate_words(m.location, 5),
            m.ship,
            "|".join(titles),
            "|".join(roles)
        ] 

        member_list.append(memb)
    
    return total_members, filtered_members, member_list




