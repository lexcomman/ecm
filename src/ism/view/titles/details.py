'''
This file is part of ESM

Created on 13 mars 2011
@author: diabeteman
'''
from ism.data.roles.models import TitleComposition, TitleCompoDiff, Title
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from ism import settings
from ism.core import utils
from django.http import HttpResponse
import json
from ism.data.common.models import ColorThreshold
from ism.core.utils import getAccessColor
from django.shortcuts import render_to_response
from django.template.context import RequestContext



#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def details(request, id):
    colorThresholds = []
    for c in ColorThreshold.objects.all().order_by("threshold"):
        colorThresholds.append({ "threshold" : c.threshold, "color" : c.color })
    
    title = Title.objects.get(titleID=int(id))
    title.lastModified = TitleCompoDiff.objects.filter(title=title).order_by("-id")
    if title.lastModified.count():
        title.lastModified = utils.print_time_min(title.lastModified[0].date)
    else:
        title.lastModified = None
    title.color = getAccessColor(title.accessLvl, ColorThreshold.objects.all().order_by("threshold"))

    data = { "title" : title,
            "member_count" : title.members.count(),  
            "colorThresholds" : json.dumps(colorThresholds) }

    return render_to_response("titles/title_details.html", data, context_instance=RequestContext(request))




#------------------------------------------------------------------------------
composition_columns = [ "role_id" ]
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def composition_data(request, id):
    iDisplayStart = int(request.GET["iDisplayStart"])
    iDisplayLength = int(request.GET["iDisplayLength"])
    sEcho = int(request.GET["sEcho"])
    column = int(request.GET["iSortCol_0"])
    ascending = (request.GET["sSortDir_0"] == "asc")

    total_compos, composition = getTitleComposition(id=int(id),
                                                    first_id=iDisplayStart,
                                                    last_id=iDisplayStart + iDisplayLength - 1,
                                                    sort_by=composition_columns[column], 
                                                    asc=ascending)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : total_compos,
        "iTotalDisplayRecords" : total_compos,
        "aaData" : composition
    }
    
    return HttpResponse(json.dumps(json_data))







#------------------------------------------------------------------------------
def getTitleComposition(id, first_id, last_id, sort_by="role_id", asc=True):

    sort_col = "%s_nocase" % sort_by
    
    compos = TitleComposition.objects.filter(title=id)

    # SQLite hack for making a case insensitive sort
    compos = compos.extra(select={sort_col : "%s COLLATE NOCASE" % sort_by})
    if not asc: sort_col = "-" + sort_col
    compos = compos.extra(order_by=[sort_col])
    
    total_compos = compos.count()
    
    compos = compos[first_id:last_id]
    
    compo_list = []
    for c in compos:
        compo = [
            '<a href="/roles/%s/%d" class="role">%s</a>' % (c.role.roleType.typeName, c.role.roleID, unicode(c.role)),
            c.role.getAccessLvl()
        ] 

        compo_list.append(compo)
    
    return total_compos, compo_list



#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def compo_diff_data(request, id):
    iDisplayStart = int(request.GET["iDisplayStart"])
    iDisplayLength = int(request.GET["iDisplayLength"])
    sEcho = int(request.GET["sEcho"])

    total_diffs, diffs = getTitleCompoDiff(id=int(id),
                                           first_id=iDisplayStart,
                                           last_id=iDisplayStart + iDisplayLength - 1)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : total_diffs,
        "iTotalDisplayRecords" : total_diffs,
        "aaData" : diffs
    }
    
    return HttpResponse(json.dumps(json_data))


#------------------------------------------------------------------------------
def getTitleCompoDiff(id, first_id, last_id):

    diffsDb = TitleCompoDiff.objects.filter(title=id).order_by("-date")
    total_diffs = diffsDb.count()
    
    diffsDb = diffsDb[first_id:last_id]
    
    diff_list = []
    for d in diffsDb:
        diff = [
            d.new,
            '<a href="/roles/%s/%d" class="role">%s</a>' % (d.role.roleType.typeName, d.role.roleID, unicode(d.role)),
            utils.print_time_min(d.date)
        ] 

        diff_list.append(diff)
    
    return total_diffs, diff_list
