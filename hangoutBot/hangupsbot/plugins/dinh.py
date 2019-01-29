import plugins
import xmlrpc.client
import io
import base64
import random
import json
import os
import requests
from utils import simple_parse_to_segments
from datetime import datetime, timedelta, date
# import datetime
import unicodedata
import operator
from commands import command


###############################################################################################################
def _initialise(bot):

    plugins.register_user_command(["whois", "timesheet", "opportunity", "project", "room", "sos", "dinh_refresh", "ben", "statistics", "harper",
                                   "kenobi", "noinfluencer", "nosalary", "topsalary", "topproximityinfluencer", "topspiritualinfluencer", "topinfluencer", "computetopinfluencer", "horoscope", "offyskill", "whoskill", "offyage", "cashin", "cashout"])

    global sock, sock_common, uid, username, pwd, dbname

    # This is the official database
    username = 'bot@officience.com'  # the user
    pwd = 'vBGZMTNz'  # the password of the user
    dbname = 'officience'  # the database

    sock_common = xmlrpc.client.ServerProxy(
        'http://dinh.officience.com:8069/xmlrpc/common')
    uid = sock_common.login(dbname, username, pwd)
    sock = xmlrpc.client.ServerProxy(
        'http://dinh.officience.com:8069/xmlrpc/object')

    # This is the database on the test server
    # username = 'admin' #the user
    # pwd = '123'      #the password of the user
    # dbname = 'officience_bk'    #the database
    #
    # sock_common = xmlrpc.client.ServerProxy('http://172.16.0.37:8069/xmlrpc/common')
    # uid = sock_common.login(dbname, username, pwd)
    # sock = xmlrpc.client.ServerProxy('http://172.16.0.37:8069/xmlrpc/object')

    # These functions are run during the initialization of the plugin
    _db_name_user()
    _db_name_project()
    _db_name_partner()

###############################################################################################################


def _normalise(input_str):  # this function normalises input (French accents), leaves the spaces between the words, needs to import unicodedata
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    result = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    return result.lower()


# update the dictionaries of Offies, partners and projects
def dinh_refresh(bot, event, *args):
    bot.send_message_parsed(event.conv, _("<i>Refresh, proceeding...</i>"))
    _db_name_user()
    _db_name_project()
    _db_name_partner()
    computetopinfluencer()
    bot.send_message_parsed(event.conv, _("<i>Refresh completed</i>"))
    counter('refresh')


def counter(command):   # write the usage in 'counter.json'
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    source_file = os.path.join(plugin_dir, "counter.json")

    with open(source_file, 'r+')as f:
        data = json.load(f)
        data[command] += 1
        f.seek(0)
        json.dump(data, f, indent=4)


def statistics(bot, event, *args):  # include a refresh here ? Display the datas in 'counter.json'. Write a string with all information with the key 'datetime.utcnow().date()' in 'counter.json
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    source_file = os.path.join(plugin_dir, "counter.json")

    with open(source_file, 'r+')as f:
        datas = json.load(f)
        chaine = ""
        chaine_bis = ""
        cmds = ['whois', 'timesheet', 'project',
                'opportunity', 'sos', 'room', 'refresh', 'horoscope']
        for data in datas:
            chaine += data + ' : ' + str(datas[data]) + "<br />"
            if data in cmds:
                chaine_bis += data + ' : ' + str(datas[data]) + ", "
        bot.send_message_parsed(event.conv, _(chaine))
        # record the datas with the date
        datas[str(datetime.utcnow().date())] = chaine_bis
        f.seek(0)
        json.dump(datas, f, indent=4)


##############################################################################################################

def _db_name(table, *arguments):
    args = arguments
    ids = sock.execute(dbname, uid, pwd, table, 'search', args)

    fields = ['name']  # fields to read
    data_dict = sock.execute(dbname, uid, pwd, table, 'read', ids, fields)

    list = []
    for dico in data_dict:
        list.append(dico['name'])

    dico_name = {}
    for item in data_dict:
        dico_name[_normalise(item['name'])] = {
            'id': item['id'], 'name': item['name']}
    return dico_name


def _db_name_user():  # implementation of _db_name
    # key : value, normalized_name : {id, name}
    global dico_name_user, dico_id_name
    dico_name_user = {}
    dico_name_user = _db_name('hr.employee')
    dico_id_name = {}  # key: value, id : name
    for key in dico_name_user:
        dico_id_name[dico_name_user[key]['id']] = dico_name_user[key]['name']


def _db_name_project():  # implementation of _db_name
    global dico_name_project
    dico_name_project = {}
    dico_name_project = _db_name('account.analytic.account')


def _db_name_partner():  # we must delete the employees from this table because they are also contained in dico_name_user
    global dico_name_partner
    dico_name_partner = {}
    dico_name_partner = _db_name('res.partner')
    for key in dico_name_user:
        if key in dico_name_partner:
            del dico_name_partner[key]


def _search_name(name_asked, dico_name):
    name_asked = _normalise(name_asked)
    result_name = []
    for name in dico_name:
        if name_asked in name:  # here we can use regular expressions, sort by matching also?
            result_name.append(dico_name[name])
        else:
            pass
    return result_name


def _search_name_user(name_user):  # implementation of _search_name
    return _search_name(name_user, dico_name_user)


def _search_name_project(name_project):
    return _search_name(name_project, dico_name_project)


def _search_name_partner(name_partner):
    return _search_name(name_partner, dico_name_partner)

###################################################################################################################################

# For Horoscope check


def horoscope_sign(birthday_day, birthday_month):
    astro_sign = ''
    if birthday_month == 12:
        astro_sign = 'Sagittarius' if (
            birthday_day < 22) else 'Capricorn'
    elif birthday_month == 1:
        astro_sign = 'Capricorn' if (
            birthday_day < 20) else 'Aquarius'
    elif birthday_month == 2:
        astro_sign = 'Aquarius' if (
            birthday_day < 19) else 'Pisces'
    elif birthday_month == 3:
        astro_sign = 'Pisces' if (birthday_day < 21) else 'Aries'
    elif birthday_month == 4:
        astro_sign = 'Aries' if (birthday_day < 20) else 'Taurus'
    elif birthday_month == 5:
        astro_sign = 'Taurus' if (birthday_day < 21) else 'Gemini'
    elif birthday_month == 6:
        astro_sign = 'Gemini' if (birthday_day < 21) else 'Cancer'
    elif birthday_month == 7:
        astro_sign = 'Cancer' if (birthday_day < 23) else 'Leo'
    elif birthday_month == 8:
        astro_sign = 'Leo' if (birthday_day < 23) else 'Virgo'
    elif birthday_month == 9:
        astro_sign = 'Virgo' if (birthday_day < 23) else 'Libra'
    elif birthday_month == 10:
        astro_sign = 'Libra' if (birthday_day < 23) else 'Scorpio'
    elif birthday_month == 11:
        astro_sign = 'Scorpio' if (
            birthday_day < 22) else 'Sagittarius'
    return astro_sign
#####


def sos(bot, event, *args):  # function help for the functions related to Dinh

    help = """<b>Help for Ben's HangoutsBOT</b> <br />
Write every command like this : <b>ben <command> <sub_command> <arguments></b>, sub_command and arguments are not always needed and depend on the command. 'sub_command' modifies the behaviour of the command. 'arguments' is the name you are searching for instance <br />
List of commands related to Dinh :
<b>whois <name></b> : get information about people in the tribe.
<i>ben whois duc ha duong<br />ben whois ekino</i><br />
<b>timesheet <name_of_offy></b> : get information about Offies activities. Without argument you will have information for all the company.
<i>ben timesheet<br />ben timesheet amane<br /></i>
<b>project <name_of_project></b> : get information about a project.
<i>ben project aperoffy</i><br />
<b>opportunity <status> <name></b> : get information about opportunities related to a <b>status</b> and/or a <b>company</b> name.
<i>ben opportunity qualification ekino<br />ben opportunity qualification<br />ben opportunity ekino</i><br />
<b>room <sub_comd> <name></b> : join interesting conversations previously registered.The sub_commands are 'list', 'join', 'save' and 'delete'
<i>ben room list<br />ben room<br />ben room join room test <br />ben room save</i><br />
<b>dinh_refresh</b> : refresh the information.
<i>ben dinh_refresh </i><br />
ben harper
ben kenobi
ben noinfluencer
ben nosalary
ben topsalary
ben topspiritual influencer
ben topproximityinfluencer
ben topinfluencer

<b>For more details you can see this link</b><br />
<b>https://github.com/arcanine525/benbotOffy</b>
"""

    bot.send_message_parsed(event.conv, _("{}").format(help))
    counter('sos')

###################################################################################################################################


def whois(bot, event, *args):
    name_user = " ".join(args)

    list_ids_offy = _search_name_user(name_user)
    list_ids_partner = _search_name_partner(name_user)
    list_ids = list_ids_offy + list_ids_partner

    chaine = ""
    if len(list_ids) == 0:
        bot.send_message_parsed(event.conv, _(
            "You wanna know about <b>'{}'</b>? I don't have anything to say to you, enlarge your search!").format(str(name_user)))
    elif name_user == "":
        bot.send_message_parsed(event.conv, _(
            "Give me a name! Please!").format(str(name_user)))

    else:
        if len(list_ids_offy) > 3 or len(list_ids_partner) > 3:
            if len(list_ids) <= 100:
                chaine += ("I could display <b>{}</b> answers for <b>'{}'</b> but I'm tired, please check the list below :<br />").format(
                    str(len(list_ids)), str(name_user))
                # fields = ['name'] #fields to read
                # ids = [var['id']for var in list_ids_partner]
                # datas = sock.execute(dbname, uid, pwd, 'res.partner', 'read', ids, fields) #liste des personnes trouvées, influencer (liste ids)
                # liste = [] # pour avoir une liste de nom ordonnée
                # for data in datas:
                #     liste.append(data['name'])
                liste = [var['name'] for var in list_ids]
                liste = sorted(liste)
                for name in liste:
                    chaine += name + '<br />'
                chaine += '<br />'
            else:
                chaine += ("I could display <b>{}</b> answers for <b>'{}'</b> but I'm bored, please try to precise your search.<br />").format(
                    str(len(list_ids)), str(name_user))

        # we display the partner, not the Offies
        if len(list_ids_partner) > 3:
            list_ids_partner = random.sample(list_ids_partner, 3)

        fields = ['name', 'street', 'website', 'phone', 'zip', "city",
                  'country_id', 'offy_industry_id', 'function', 'parent_id', 'email']
        ids = [var['id']for var in list_ids_partner]
        data = sock.execute(dbname, uid, pwd, 'res.partner',
                            'read', ids, fields)

        for i in range(len(list_ids_partner)):
            ids_partner = list_ids_partner[i]['id']
            name_partner = list_ids_partner[i]['name']
            url_link = (
                '"https://dinh.officience.com/web#id={}&view_type=form&model=res.partner&menu_id=74&action=60"').format(str(ids_partner))
            url = ("<a href={}>{}</a>").format(url_link, str(name_partner))

            chaine += ("{}<br />").format(str(url))
            if type(data[i]['offy_industry_id']) != bool:
                chaine += ("<b>Industry : </b>{}<br />").format(
                    str(data[i]['offy_industry_id'][1]))
            if type(data[i]['parent_id']) != bool:
                chaine += ("<b>Company : </b>{}<br />").format(
                    str(data[i]['parent_id'][1]))
            if type(data[i]['email']) == str:
                chaine += ("<b>Email : </b>{}<br />").format(
                    str(data[i]['email']))
            if type(data[i]['website']) == str:
                chaine += ("<b>Website : </b>{}<br />").format(
                    str(data[i]['website']))
            if type(data[i]['phone']) == str:
                chaine += ("<b>Phone : </b>{}<br />").format(
                    str(data[i]['phone']))
            if type(data[i]['street']) == str:
                chaine += ("<b>Adress : </b>{}, {} {}, {}<br />").format(str(data[i]['street']), str(
                    data[i]['zip']), str(data[i]['city']), str(data[i]['country_id'][1]))
            chaine += "<br />"
        bot.send_message_parsed(event.conv, _(chaine))

        # Here we display the Offies
        if len(list_ids_offy) > 3:
            list_ids_offy = random.sample(list_ids_offy, 3)

        fields = ['cluster_id', 'image_medium', 'offy_salary_range_id',
                  'offy_proximityinfluencer_ids', 'offy_spiritualinfluencer_ids', 'birthday']
        ids = [var['id']for var in list_ids_offy]
        data = sock.execute(dbname, uid, pwd, 'hr.employee',
                            'read', ids, fields)

        for i in range(len(list_ids_offy)):
            name_user = list_ids_offy[i]['name']
            id_user = list_ids_offy[i]['id']

            image = data[i]['image_medium']
            if image == False:  # do not display anything if the user do not profil picture
                image_id = None
            else:
                raw = base64.b64decode(image)
                image_data = io.BytesIO(raw)
                filename = str(name_user) + ".jpg"
                image_id = yield from bot._client.upload_image(image_data, filename=filename)

            url_link = (
                '"https://dinh.officience.com/web#id={}&view_type=form&model=hr.employee&menu_id=492&action=130"').format(str(id_user))
            url = ("<a href={}>{}</a>").format(url_link, str(name_user))
            # whofollows
            proximity_influencer = ""
            for id in data[i]['offy_proximityinfluencer_ids']:
                proximity_influencer += dico_id_name[id] + ", "
            spiritual_influencer = ""
            for id in data[i]['offy_spiritualinfluencer_ids']:
                spiritual_influencer += dico_id_name[id] + ", "

            # wholeads
            args_prox = [('offy_proximityinfluencer_ids', '=', id_user)]
            ids_prox = sock.execute(
                dbname, uid, pwd, 'hr.employee', 'search', args_prox)
            args_spirit = [('offy_spiritualinfluencer_ids', '=', id_user)]
            ids_spirit = sock.execute(
                dbname, uid, pwd, 'hr.employee', 'search', args_spirit)

            proximity_follower = ""
            for id in ids_prox:
                proximity_follower += dico_id_name[id] + ", "
            spiritual_follower = ""
            for id in ids_spirit:
                spiritual_follower += dico_id_name[id] + ", "

            #####################
            chaine = ("{}<br />").format(str(url))
            if type(data[i]['cluster_id']) != bool:
                chaine += ("<b>Cluster : </b>{}<br />").format(
                    str(data[i]['cluster_id'][1]))
            if type(data[i]['birthday']) != bool:
                birthday_str = data[i]['birthday'].split("-")
                birthday_month = int(birthday_str[1])
                birthday_day = int(birthday_str[2])
                astro_sign = horoscope_sign(birthday_day, birthday_month)
                chaine += ("<b>Astro sign : </b>{}<br />").format(
                    str(astro_sign))
            if type(data[i]['offy_salary_range_id']) != bool:
                chaine += ("{}<br />").format(str(data[i]
                                                  ['offy_salary_range_id'][1]))
            if proximity_influencer != "":
                chaine += ("<b>Proximity Influencers : </b>{}<br />").format(proximity_influencer)
            if spiritual_influencer != "":
                chaine += ("<b>Spiritual Influencers : </b>{}<br />").format(spiritual_influencer)
            if proximity_follower != "" or spiritual_follower != "":    # ne pas afficher une barre inutile
                chaine += '-----------------------------------------<br />'
            if proximity_follower != "":
                chaine += ("<b>Proximity Followers : </b>{}<br />").format(proximity_follower)
            if spiritual_follower != "":
                chaine += ("<b>Spiritual Followers : </b>{}<br />").format(spiritual_follower)

            segments = simple_parse_to_segments(chaine)
            bot.send_message_segments(
                event.conv.id_, segments, None, image_id=image_id)
    counter('whois')


################################################################################################


# rethink about the code here # chercher par influencer
def opportunity(bot, event, cmd=None, *args):

    name_partner = ""
    name_partner = " ".join(args)

    if cmd == "new":
        status = "New"
    elif cmd == "qualif" or cmd == "qualification" or cmd == "qualif_&_quoting" or cmd == "qualif._&_quoting":
        status = "Qualif. & Quoting"
    elif cmd == "negotiation" or cmd == "negociation":
        status = "Negotiation"
    elif cmd == "verbal_commitment" or cmd == "verbal":
        status = "Verbal Commitment"
    else:
        status = "Done"
        if name_partner == "":
            name_partner = str(cmd)
            if cmd is None:
                bot.send_message_parsed(event.conv, _(
                    "I can't list all the opportunities. Enter a status (<b>'new', 'qualif', 'negotiation', 'verbal'</b>) and/or a company name.<br />ben opportunity verbal ekino<br />ben opportunity verbal<br />ben opportunity ekino"))
        else:
            name_partner = str(cmd) + " " + " ".join(args)
        #bot.send_message_parsed(event.conv, _("name : '{}', {}").format(str(name_partner), str(type(name_partner))))#############

    list_ids = _search_name_partner(name_partner)  # ok à cet endroit

    if name_partner == "" and status != "Done":  # without parameters

        fields = [('stage_id', '=', status), ('type', '=', 'opportunity')]
        list_ids_result = sock.execute(
            dbname, uid, pwd, 'crm.lead', 'search', fields)  # list id opportunity
        fields_bis = ['name', 'stage_id', 'offy_contact',
                      'partner_id', 'user_id', 'title_action', 'planned_revenue']
        datas = sock.execute(dbname, uid, pwd, 'crm.lead', 'read',
                             list_ids_result, fields_bis)  # liste de dictionnaires

        for data in datas:

            id_opport = data['id']
            url_project = (
                '"https://dinh.officience.com/web#id={}&view_type=form&model=crm.lead&menu_id=307&action=366"').format(str(id_opport))
            url = ("<a href={}>{}</a>").format(url_project, str(data['name']))

            chaine = ("{}<br />").format(str(url))
            if type(data['planned_revenue']) != bool:
                chaine += ("<b>Expected Revenue : </b>{}<br />").format(
                    str(data['planned_revenue']))
            if type(data['stage_id']) != bool:
                chaine += ("<b>Status : </b>{}<br />").format(
                    str(data['stage_id'][1]))
            if type(data['offy_contact']) != bool:
                chaine += ("<b>Contact : </b>{}<br />").format(
                    str(data['offy_contact'][1]))
            if type(data['partner_id']) != bool:
                chaine += ("<b>Customer : </b>{}<br />").format(
                    str(data['partner_id'][1]))
            if type(data['user_id']) != bool:
                chaine += ("<b>Engager : </b>{}<br />").format(
                    str(data['user_id'][1]))
            if type(data['title_action']) != bool:
                chaine += ("<b>Next Step : </b>{}<br />").format(
                    str(data['title_action']))

            bot.send_message_parsed(event.conv, _(chaine))

    else:  # with parameters

        if len(list_ids) > 30:
            bot.send_message_parsed(event.conv, _(
                "Sorry too many results, try again it's free! Enter a status (<b>'new', 'qalif', 'negotiation', 'verbal'</b>) or precise the companie's name."))
        elif len(list_ids) == 0:
            bot.send_message_parsed(event.conv, _(
                "Keep calm and broaden your search."))
        else:
            chaine = ""
            for partner in list_ids:

                ids_partner_res_partner = partner['id']
                name_partner = partner['name']

                if status == "Done":
                    fields = [('stage_id', 'not in', ['Lost', 'Won']),
                              ('partner_id', '=', ids_partner_res_partner)]
                else:
                    fields = [('stage_id', '=', status),
                              ('partner_id', '=', ids_partner_res_partner)]

                list_ids_result = sock.execute(
                    dbname, uid, pwd, 'crm.lead', 'search', fields)
                if len(list_ids_result) == 0:  # no message
                    continue

                fields_bis = ['name', 'stage_id', 'offy_contact',
                              'partner_id', 'user_id', 'title_action', 'planned_revenue']
                datas = sock.execute(
                    dbname, uid, pwd, 'crm.lead', 'read', list_ids_result, fields_bis)
                #bot.send_message_parsed(event.conv, _("datas : {}").format(str(datas)))##########

                for data in datas:

                    id_opport = data['id']
                    url_project = (
                        '"https://dinh.officience.com/web#id={}&view_type=form&model=crm.lead&menu_id=307&action=366"').format(str(id_opport))
                    url = ("<a href={}>{}</a>").format(url_project,
                                                       str(data['name']))

                    chaine += ("{}<br />").format(str(url))
                    if type(data['planned_revenue']) != bool:
                        chaine += ("<b>Expected Revenue : </b>{}<br />").format(
                            str(data['planned_revenue']))
                    if type(data['stage_id']) != bool:
                        chaine += ("<b>Status : </b>{}<br />").format(
                            str(data['stage_id'][1]))
                    if type(data['offy_contact']) != bool:
                        chaine += ("<b>Contact : </b>{}<br />").format(
                            str(data['offy_contact'][1]))
                    if type(data['partner_id']) != bool:
                        chaine += ("<b>Customer : </b>{}<br />").format(
                            str(data['partner_id'][1]))
                    if type(data['user_id']) != bool:
                        chaine += ("<b>Engager : </b>{}<br />").format(
                            str(data['user_id'][1]))
                    if type(data['title_action']) != bool:
                        chaine += ("<b>Next Step : </b>{}<br />").format(
                            str(data['title_action']))
                    chaine += "<br />"
            if chaine == "":
                bot.send_message_parsed(event.conv, _(
                    "Keep calm and broaden your search."))
            bot.send_message_parsed(event.conv, _(chaine))
    counter('opportunity')


####################################################################################################################################


def project(bot, event, *args):

    name_project = " ".join(args)
    list_ids = _search_name_project(name_project)
    # bot.send_message_parsed(event.conv, _("PRINT<b>'{}'</b>").format(str(list_ids)))
    # bot.send_message_parsed(event.conv, _("PRINT<b>'{}'</b>").format(str(len(list_ids)))) #pourquoi 357 ?
    # bot.send_message_parsed(event.conv, _("PRINT<b>'{}'</b>").format(str(len(dico_name_project))))
    date_today = datetime.utcnow().date()
    date_from = date_today - \
        timedelta(days=date_today.weekday()) - timedelta(weeks=1)
    date_to = date_from + timedelta(days=6)
    date_from = date_from.strftime("%Y-%m-%d")
    date_to = date_to.strftime("%Y-%m-%d")

    if len(list_ids) == 0:
        bot.send_message_parsed(event.conv, _(
            "I wish I had a project called <b>'{}'</b>.<br /><b>Note</b> : if you want to find 'Projects / OBS / DSL /1st prequal', only look for '1st prequal' ").format(str(name_project)))
        # list_ids = [dico_name_project[key] for key in dico_name_project] #liste de dicos
    elif name_project == "":
        list_ids = []
        bot.send_message_parsed(event.conv, _(
            "I need the name of a project, please give me something!").format(str(name_project)))

    elif len(list_ids) > 5:
        bot.send_message_parsed(event.conv, _(
            "Your request got {} answers with <b>'{}'</b><br /> Only 5 answers are shown. Please give me more details!.").format(str(len(list_ids)), str(name_project)))
        list_ids = random.sample(list_ids, 5)

    fields = ['name', 'partner_id', 'manager_id', 'non_billable',
              'cluster_id', 'parent_id']  # fields to read
    ids = [var['id']for var in list_ids]
    # bot.send_message_parsed(event.conv, _("list id<b>'{}'</b>").format(str(ids)))
    # liste des personnes trouvées, influencer (liste ids)
    datas = sock.execute(
        dbname, uid, pwd, 'account.analytic.account', 'read', ids, fields)
    # bot.send_message_parsed(event.conv, _("datas<b>'{}'</b>").format(str(datas)))

    for data in datas:  # we avoid to do multiple requests here
        ids_project = data['id']
        name_project = data['name']
        # URL ? accès trop restreint
        # url_project = ('"https://dinh.officience.com/web#id={}&view_type=form&model=project.project&menu_id=439&action=549"').format(str(ids_project))
        # url = ("<a href={}>{}</a>").format(url_project,str(name_project))
        # chaine = ("{}<br />").format(str(url))

        chaine = ""
        if type(data['name']) != bool:
            chaine += ("<b>{}</b><br />").format(str(data['name']))
        if type(data['partner_id']) != bool:
            chaine += ("<b>Customer : </b>{}<br />").format(
                str(data['partner_id'][1]))
        if type(data['manager_id']) != bool:
            chaine += ("<b>Account Manager : </b>{}<br />").format(
                str(data['manager_id'][1]))
            # chaine += ("<b>Team : </b>{}<br />").format(str(data['members']))
        if type(data['non_billable']) == True:
            chaine += "<b>Non billable </b><br />"
        if type(data['cluster_id']) != bool:
            chaine += ("<b>Cluster  : </b>{}<br />").format(
                str(data['cluster_id'][1]))
        if type(data['parent_id']) != bool:  # pertinent ?
            chaine += ("<b>Parent Analytic Account : </b>{}<br />").format(
                str(data['parent_id'][1]))

        # bot.send_message_parsed(event.conv, _(chaine))

        # number of hours spent on this on the week of the / since the beginning
        # employeed working on this project (last week, ever?)
        # Blabla have worked on this project
        # total amount of time :
        # on the week of the  :
        args_1 = [('account_id', '=', ids_project)]

        ids_1 = sock.execute(
            dbname, uid, pwd, 'hr.analytic.timesheet', 'search', args_1)

        # bot.send_message_parsed(event.conv, _("datas<b>'{}'</b>").format(str(ids_1)))

        fields_1 = ['user_id', 'date', 'sheet_id', 'unit_amount', 'account_id']
        datas_1 = sock.execute(
            dbname, uid, pwd, 'hr.analytic.timesheet', 'read', ids_1, fields_1)

        # bot.send_message_parsed(event.conv, _("number of timesheet <b>'{}'</b>").format(str(len(datas_1))))
        # bot.send_message_parsed(event.conv, _("timesheet <b>'{}'</b>").format(str(datas_1)))
        sum = 0
        chaine_bis = ""
        table_chaine = []
        for data_1 in datas_1:
            # bot.send_message_parsed(event.conv, _("{}<b>'{}'</b>").format(data['date'],str(data['unit_amount'])))
            sum += data_1['unit_amount']
            if data_1['user_id'][1] not in table_chaine:
                table_chaine.append(data_1['user_id'][1])
                chaine_bis += data_1['user_id'][1] + ', '
        chaine += ("<b>Team : </b>{}<br />").format(str(chaine_bis))
        chaine += ("<b>Total time spent : </b>{} hours<br />").format(str(round(sum, 2)))
        # temps passé la semaine dernière ?
        # date to et date from

        args_2 = [('account_id', '=', ids_project),
                  ('date', '>=', date_from), ('date', '<=', date_to)]
        ids_2 = sock.execute(
            dbname, uid, pwd, 'hr.analytic.timesheet', 'search', args_2)
        # bot.send_message_parsed(event.conv, _("PRINT : '{}' ").format(str(ids_2)))

        fields_2 = ['unit_amount', 'user_id']
        datas_2 = sock.execute(
            dbname, uid, pwd, 'hr.analytic.timesheet', 'read', ids_2, fields_2)
        # bot.send_message_parsed(event.conv, _("PRINT : '{}'").format(str(datas_2)))

        sum_2 = 0
        chaine_ter = ""
        table_chaine = []
        for data_2 in datas_2:
            sum_2 += data_2['unit_amount']
            if data_2['user_id'][1] not in table_chaine:
                table_chaine.append(data_2['user_id'][1])
                chaine_ter += data_2['user_id'][1] + ', '

        # bot.send_message_parsed(event.conv, _("PRINT : '{}'").format(str(sum_2)))
        chaine += ("During the week of the <b>{}</b>, <b>{} hours</b> spent ").format(
            str(date_from), str(round(sum_2, 2)))
        if sum_2 != 0:
            chaine += ("by<br />{}<br />").format(str(chaine_ter))

        bot.send_message_parsed(event.conv, _(chaine))
    counter('project')


####################################################################################################################################


####################################################################################################################################


def timesheet(bot, event, *args):

    # have to complete timesheet from friday to monday included
    # from tuesday do thurday timesheet of the previous week and timesheet missing
    # from Friday to Monday number of timesheet missing for this week and timesheet of the previous week with number of missing timesheet
    # args a specific employee, mood, all activity of the week
    # percentage
    # bot.send_message_parsed(event.conv, _("args '{}', '{}'").format(str(args),str(type(args)))) # tuple
    name_user = " ".join(args)
    list_ids = _search_name_user(name_user)
    # bot.send_message_parsed(event.conv, _("args '{}'").format(str(list_ids))) # tuple
    date_today = datetime.utcnow().date()
    date_from = []
    date_to = []

    # la semaine dernière pour le nombre de timesheet
    if date_today.weekday() == 4 or date_today.weekday() == 5 or date_today.weekday() == 6 or date_today.weekday() == 0:
        if date_today.weekday() == 0:
            date_from.append(date_today - timedelta(days=7))
        else:
            # this week's Monday
            date_from.append(date_today - timedelta(days=date_today.weekday()))

        date_to.append(date_from[0] + timedelta(days=6))
        date_from.append(date_from[0] - timedelta(weeks=1))
        date_to.append(date_to[0] - timedelta(weeks=1))

        date_from[0] = date_from[0].strftime("%Y-%m-%d")
        date_to[0] = date_to[0].strftime("%Y-%m-%d")
        date_from[1] = date_from[1].strftime("%Y-%m-%d")
        date_to[1] = date_to[1].strftime("%Y-%m-%d")

        # i################################## inversion vendredi, l'utilisateur n'a sans doute pas compléter la TS de la semaine en cours !!
        # last = recent
        date_from[0], date_from[1] = date_from[1], date_from[0]
        date_to[0], date_to[1] = date_to[1], date_to[0]

    else:  # à tester plus tard
        date_from.append(
            date_today - timedelta(days=date_today.weekday()) - timedelta(weeks=1))
        date_to.append(date_from[0] + timedelta(days=6))
        date_from.append(date_from[0] - timedelta(weeks=1))
        date_to.append(date_to[0] - timedelta(weeks=1))

        date_from[0] = date_from[0].strftime("%Y-%m-%d")
        date_to[0] = date_to[0].strftime("%Y-%m-%d")
        date_from[1] = date_from[1].strftime("%Y-%m-%d")
        date_to[1] = date_to[1].strftime("%Y-%m-%d")

    if name_user == "" or len(list_ids) == 0:
        if len(list_ids) == 0:
            bot.send_message_parsed(event.conv, _(
                "Nothing found about <b>'{}'</b>, please try something else").format(str(name_user)))

        # number of timesheet
        args = [('date_from', '=', date_from[0]), ('date_to', '=', date_to[0])]
        ids = sock.execute(
            dbname, uid, pwd, 'hr_timesheet_sheet.sheet', 'search', args)
        number_ts = len(ids)

        for i in range(2):

            args_ts = [('date_from', '=', date_from[i]),
                       ('date_to', '=', date_to[i]), ('state', '=', 'done')]
            ids_ts = sock.execute(
                dbname, uid, pwd, 'hr_timesheet_sheet.sheet', 'search', args_ts)
            percentage = int(len(ids_ts)*100/number_ts)

            fields_users = ['offy_weekly_mood']  # fields to read
            data_users = sock.execute(
                dbname, uid, pwd, 'hr_timesheet_sheet.sheet', 'read', ids_ts, fields_users)
            sum = 0
            cpt = 0
            for data in data_users:
                if type(data['offy_weekly_mood']) != bool:
                    cpt += 1
                    if data['offy_weekly_mood'] == "neutral":
                        sum += 5
                    elif data['offy_weekly_mood'] == "good":
                        sum += 10
            if cpt == 0:
                mood_note = 5
            else:
                mood_note = round(sum/cpt, 2)

            bot.send_message_parsed(event.conv, _("On the week of the {}, <b>{} %</b> of the timesheets have been completed ({})<br />The tribe's mood is <b>{}</b>/10 ").format(
                str(date_from[i]), str(percentage), str(len(ids_ts)), str(mood_note)))

    # information about last week for a employee

    else:

        if len(list_ids) > 5:
            bot.send_message_parsed(event.conv, _(
                "Your request got {} answers with <b>'{}'</b><br /> Only 5 answers are shown. Please try to precise your search.").format(str(len(list_ids)), str(name_user)))
            list_ids = random.sample(list_ids, 5)

        for id in list_ids:

            args_1 = [('date_from', '=', date_from[0]), ('date_to',
                                                         '=', date_to[0]), ('employee_id', '=', id['id'])]
            ids_1 = sock.execute(
                dbname, uid, pwd, 'hr_timesheet_sheet.sheet', 'search', args_1)
            # bot.send_message_parsed(event.conv, _("PRINT<b>'{}'</b>").format(str(ids_1)))

            fields_1 = ['offy_weekly_mood', 'state', 'employee_id', 'user_id']
            datas_1 = sock.execute(
                dbname, uid, pwd, 'hr_timesheet_sheet.sheet', 'read', ids_1, fields_1)
            # bot.send_message_parsed(event.conv, _("datas<b>'{}'</b>").format(str(data)))
            for data in datas_1:
                if data['state'] != "done":
                    bot.send_message_parsed(event.conv, _(
                        "<b>{}</b> hasn't completed his/her timesheet yet").format(str(id['name'])))
                else:

                    url_link = (
                        '"https://dinh.officience.com/web#id={}&view_type=form&model=hr_timesheet_sheet.sheet&menu_id=416&action=518"').format(str(data['id']))
                    url = ("<a href={}>{}</a>").format(url_link,
                                                       str(id['name']))

                    chaine = ("{}<br />").format(str(url))
                    if type(data['offy_weekly_mood']) != bool:
                        chaine += ("<b>{} </b>mood<br />").format(
                            str(data['offy_weekly_mood']))

                    # bot.send_message_parsed(event.conv, _(chaine))
    # display the timetable of the employee

                    args_2 = [('user_id', '=', data['user_id'][0]), ('date',
                                                                     '>=', date_from[0]), ('date', '<=', date_to[0])]
                    ids_2 = sock.execute(
                        dbname, uid, pwd, 'hr.analytic.timesheet', 'search', args_2)

                    fields_2 = ['user_id', 'date', 'sheet_id',
                                'unit_amount', 'account_id']
                    datas_2 = sock.execute(
                        dbname, uid, pwd, 'hr.analytic.timesheet', 'read', ids_2, fields_2)

                    chaine += ("During the week of the <b>{}</b> :<br />").format(
                        str(date_from[0]))

                    dico_activity = {}
                    for data in datas_2:
                        if data['account_id'][1] not in dico_activity:
                            dico_activity[str(data['account_id'][1])
                                          ] = data['unit_amount']
                        else:
                            dico_activity[str(data['account_id'][1])
                                          ] += data['unit_amount']
                    sorted_dico_activity = sorted(
                        dico_activity.items(), key=operator.itemgetter(1), reverse=True)
                    for var in sorted_dico_activity:
                        if var[1] >= 2:
                            chaine += ("{} : <b>{}</b> hours<br />").format(
                                str(var[0]), str(var[1]))
                        else:
                            chaine += ("{} : <b>{}</b> hour<br />").format(
                                str(var[0]), str(var[1]))

                    bot.send_message_parsed(event.conv, _(chaine))
    counter('timesheet')
############################################################################
#############################################################################
# room join, room rejoin, room rejoindre, room save, room sauver, room list, room liste, room lister,


def room(bot, event, cmd=None, *args):

    # bot.send_message_parsed(event.conv, _("CMD: '<b>{}</b>' ;)").format(str(cmd)))

    name = " ".join(args)
    name_normalise = _normalise(name)

    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    source_file = os.path.join(plugin_dir, "conv.json")

    if cmd == 'list' or cmd == 'liste' or cmd is None:  # affiche la liste
        list_result = []

        with open(source_file, 'r') as f:
            data = json.load(f)
            if len(str(name_normalise)) == 0:
                for element in data:
                    list_result.append(data[element]['title_conv'])
            else:
                for element in data:
                    if name_normalise in data[element]['normalise_title']:
                        list_result.append(data[element]['title_conv'])

        if len(list_result) == 0:
            bot.send_message_parsed(event.conv, _(
                "No room registered as <b>'{}'</b> ").format(name))
        else:
            chaine = ""
            for room in list_result:
                chaine += room + '<br />'
            bot.send_message_parsed(event.conv, _(
                "List of rooms you asked for :<br /> {} ").format(chaine))

    elif cmd == 'join' or cmd == 'rejoin':

        list_result = []

        with open(source_file, 'r+') as f:
            data = json.load(f)
            for element in data:
                if name_normalise in data[element]['normalise_title']:
                    list_result.append(data[element])

            if len(list_result) == 1:
                name_conv_to_join = list_result[0]['title_conv']
                id_conv_to_join = list_result[0]['chat_id']
                bot.send_message_parsed(event.conv, _(
                    "You joined '<b>{}</b>'").format(str(name_conv_to_join)))
                user_id = [event.user.id_.chat_id]

                yield from bot._client.adduser(id_conv_to_join, user_id)
                bot.send_message_parsed(id_conv_to_join, _(
                    "Welcome {} !").format(event.user.full_name))

            elif len(list_result) == 0:
                bot.send_message_parsed(event.conv, _(
                    "Nothing found about '<b>{}</b>', you can check the list of rooms available").format(str(name)))

            else:
                list_name_conv = []
                for element in list_result:
                    list_name_conv.append(element['title_conv'])
                chaine = ""
                for room in list_name_conv:
                    chaine += room + '<br />'
                bot.send_message_parsed(event.conv, _(
                    "You cannot enter several rooms at the same time. Please retry with one of this name : <br />{}").format(chaine))

    elif cmd == 'save' or cmd == 'register':

        title_conv = str(bot.conversations.get_name(event.conv))
        normalise_title = _normalise(title_conv)
        chat_id = str(event.conv.id_)

        info_room = {
            'title_conv': title_conv,
            'normalise_title': normalise_title,
            'chat_id': chat_id,
        }

        # plugin_dir = os.path.dirname(os.path.realpath(__file__))
        # source_file = os.path.join(plugin_dir, "conv.json")

        with open(source_file, 'r+') as f:
            data = json.load(f)

            if chat_id in data:
                bot.send_message_parsed(event.conv, _(
                    "This room is already saved as '<b>{}</b>'").format(title_conv))

            else:
                result = 0
                for element in data:
                    if data[element]['normalise_title'] == normalise_title:
                        bot.send_message_parsed(event.conv, _(
                            "This room name is already used. Please change its name before registration"))
                        result = 1
                        break
                    else:
                        pass
                if result == 0:
                    data[chat_id] = info_room
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    bot.send_message_parsed(event.conv, _(
                        "Room registred! People can join with 'ben room join <b>{}</b>'").format(title_conv))

    elif cmd == 'delete' or cmd == 'del':  # reservé à l'admin

        admins_list = bot.get_config_suboption(event.conv_id, 'admins')
        if event.user_id.chat_id in admins_list:

            title_conv = str(bot.conversations.get_name(event.conv))
            normalise_title = _normalise(title_conv)
            chat_id = str(event.conv.id_)

            data = {}

            # plugin_dir = os.path.dirname(os.path.realpath(__file__))
            # source_file = os.path.join(plugin_dir, "conv.json")

            with open(source_file, 'r') as f:
                data = json.load(f)

                for element in data:
                    if element == chat_id:
                        del data[element]
                        bot.send_message_parsed(
                            event.conv, _("Room unregistred"))
                        break

                    # else :
                    #     bot.send_message_parsed(event.conv, _("This room wasn't registred ;)"))

            with open(source_file, 'w') as f:
                json.dump(data, f, indent=4)

        else:

            bot.send_message_parsed(event.conv, _(
                "Only <b>admins</b> can delete conversations"))

    else:
        # help de la fonction room ?!
        yield from command.unknown_command(bot, event)

        # return
    counter('room')

#######################################################################################


def harper(bot, event, *args):
    list_song = [
        {'title': 'Amen Omen',			'album': 'Diamonds On the Inside',
            'link': 'https://www.youtube.com/watch?v=nWoafpw0rg4'},
        {'title': 'Another Lonely Day',		'album': 'Fight For Your Mind',
            'link': 'https://www.youtube.com/watch?v=zr5mCBFejIE'},
        {'title': 'Better Way',			'album': 'Both Sides Of the Gun',
            'link': 'https://www.youtube.com/watch?v=XOZj1Xyx354'},
        {'title': 'Burn One Down',		'album': 'Fight For Your Mind',
            'link': 'https://www.youtube.com/watch?v=5w0K0Ve0ZvM'},
        {'title': 'By My Side',			'album': 'Fight For Your Mind',
            'link': 'https://www.youtube.com/watch?v=11KqrBfP2ZA'},
        {'title': 'Diamonds On the Inside',		'album': 'Diamonds On the Inside',
            'link': 'https://www.youtube.com/watch?v=fpns_a4Nuvo'},
        {'title': 'Everything',			'album': 'Diamonds On the Inside',
            'link': 'https://www.youtube.com/watch?v=MMwKJPXE5b4'},
        {'title': 'Excuse Me Mr.',	    'album': 'Fight For Your Mind',
            'link': 'https://www.youtube.com/watch?v=1ghwDHu7j_I'},
        {'title': 'Forever',				'album': 'Welcome To The Cruel World',
            'link': 'https://www.youtube.com/watch?v=pHzAVDg4m1Q'},
        {'title': 'Gold to Me',			'album': 'Fight For Your Mind',
            'link': 'https://www.youtube.com/watch?v=PeLZCo1qaG8'},
        {'title': 'Ground On Down',			'album': 'Fight For Your Mind',
            'link': 'https://www.youtube.com/watch?v=8f-D7Xx89r4'},
        {'title': 'I’ll Rise',		'album': 'Welcome To The Cruel World',
            'link': 'https://www.youtube.com/watch?v=xFFpwhTMr6A'},
        {'title': 'Mama’s Got A Girlfriend Now',	'album': 'Welcome To The Cruel World',
            'link': 'https://www.youtube.com/watch?v=pP5VjWu6K2o'},
        {'title': 'Morning Yearning',		'album': 'Both Sides Of The Gun',
            'link': 'https://www.youtube.com/watch?v=LlNGEpief3Q'},
        {'title': 'Oppression', 			'album': 'Fight For Your Mind',
            'link': 'https://www.youtube.com/watch?v=ln4uBEUX0gM'},
        {'title': 'Please Me Like You Want To', 	'album': 'Please Me Like You Want To',
            'link': 'https://www.youtube.com/watch?v=03Z5Ai3J1ug'},
        {'title': 'Sexual Healing',			'album': 'Live from Mars',
            'link': 'https://www.youtube.com/watch?v=-rEJ7zImP9Q'},
        {'title': 'She’s Only Happy In The Sun',	'album': 'Diamonds On The Inside',
            'link': 'https://www.youtube.com/watch?v=b50rex-J6Xg'},
        {'title': 'Steal My Kisses',			'album': 'Burn To Shine',
            'link': 'https://www.youtube.com/watch?v=BSTBs3IEVQs'},
        {'title': 'Suzie Blue',			'album': 'Burn To Shine',
            'link': 'https://www.youtube.com/watch?v=VWcP-oqr6yc'},
        {'title': 'The Three Of Us',			'album': 'Welcome To The Cruel World',
            'link': 'https://www.youtube.com/watch?v=OPvV4bOoc_8'},
        {'title': 'Two Hands Of A Prayer',		'album': 'Burn To Shine',
            'link': 'https://www.youtube.com/watch?v=beP06k8r4_0'},
        {'title': 'Waiting On an Angel', 		'album': 'Welcome To The Cruel World',
            'link': 'https://www.youtube.com/watch?v=FVHZtxMtt0M'},
        {'title': 'Walk Away',			'album': 'Welcome To The Cruel World',
            'link': 'https://www.youtube.com/watch?v=CB_wZ_0s7mc'},
        {'title': 'With My Own Two Hands',		'album': 'Diamonds On The Inside',
            'link': 'https://www.youtube.com/watch?v=aEnfy9qfdaU'},
    ]
    list_quote = ["There's something in everyone only they know.",
                  "All that we can't say is all we need to hear.",
                  "You can't just say I love you, you have to LIVE I love you",
                  "Music is the last true voice of the human spirit. It can go beyond language, beyond age, and beyond color straight to the mind and heart of all people.",
                  "If you're gonna live, then live it up. If you're gonna give, then give it up. If you're gonna walk the Earth, then walk it proud. If you're gonna say the word, you got to say it loud.",
                  "They say time will make all this go away. But it's time that's taken my tomorrow, and turned them into yesterday.",
                  "If you don't like my fire, don't come around cuz I'm gonna burn one down.",
                  "My choice is what I choose to do, and if I'm causing no harm, it shouldnt bother you. Your choice is who you choose to be, and if you're causing no harm, it shouldn't bother me.",
                  "Like a soldier standing long under fire, any change comes as a relief.",
                  "I wish you were here so we could walk and talk in the soft rain.",
                  "It will make a weak man mighty. it will make a mighty man fall. It will fill your heart and hands or leave you with nothing at all. It's the eyes for the blind and legs for the lame. It is the love for hate and pride for shame. That's the power of the gospel.",
                  ]

    song = random.choice(list_song)
    quote = random.choice(list_quote)

    chaine = "Listen to Ben Harper on YouTube <br />"
    url = ("<a href=\"{}\">{}</a>").format(song['link'], str(song['title']))
    chaine += url + " - " + song['album'] + "<br /><br />"
    chaine += "\"" + quote + "\"" + "<br /> – Ben Harper <br />"

    bot.send_message_parsed(event.conv, _(chaine))


def kenobi(bot, event, *args):
    list_film = [
        {'title': 'Ben Kenobi VS Dark Vador', 'url': 'https://www.youtube.com/watch?v=8kpHK4YIwY4',
            'quote': "Darth Vader: Your powers are weak, old man. <br/>Ben Obi-Wan Kenobi: You can't win, Darth. If you strike me down, I shall become more powerful than you could possibly imagine."},
        {'title': 'Ben Kenobi VS Anakin Skywalker', 'url': 'https://www.youtube.com/watch?v=_xP3fI7yn5s',
            'quote': "Anakin Skywalker: If you're not with me, then you're my enemy. <br />Obi-Wan Kenobi: Only a Sith deals in absolutes."},
        {'title': 'Ben Kenobi VS Grievous', 'url': 'https://www.youtube.com/watch?v=tXTFdDrd7pA',
            'quote': "Obi-Wan Kenobi: Your move. <br />General Grievous: You Fool. I have been trained in your Jedi Arts... by Count Dooku."},
        {'title': 'Obi Wan & Qui Gon Ginn Vs Darth Maul',
            'url': 'https://www.youtube.com/watch?v=yHqdESArkqU', 'quote': ''},
        {'title': 'Anakin Skywalker & Obi-Wan Kenobi & Yoda vs. Count Dooku', 'url': 'https://www.youtube.com/watch?v=BvnwLLXHabg',
            'quote': "Count Dooku: As you can see, my Jedi powers are far beyond yours. Now, back down.[shoots Sith lighting at Obi-Wan who blocks it with his lightsaber] <br />Obi-Wan: I don't think so."},
        {'title': 'Obi-Wan Discovers the Clone Army', 'url': 'https://www.youtube.com/watch?v=3dovd1clLJ4',
            'quote': 'Obi-Wan Kenobi:  I should very much like to meet this Jango Fett.'}
    ]
    film = random.choice(list_film)
    url = ("<a href=\"{}\">{}</a>").format(film['url'], str(film['title']))
    chaine = url + "<br /><br />" + film['quote']

    bot.send_message_parsed(event.conv, _(str(chaine)))


# display the list of Offies without influencer
def noinfluencer(bot, event, cmd=None, *args):
    list_ids = _search_name_user("")
    list_name = []
    ids = [var['id'] for var in list_ids]

    if cmd == "spiritual":
        fields = ['name', 'offy_spiritualinfluencer_ids']
        datas = sock.execute(
            dbname, uid, pwd, 'hr.employee', 'read', ids, fields)
        for data in datas:
            if len(data['offy_spiritualinfluencer_ids']) == 0:
                list_name.append(data['name'])
        list_name = sorted(list_name)
        chaine = (
            "<b>{}</b> Offies do not have spiritual influencers for the moment : <br />").format(str(len(list_name)))
        for item in list_name:
            chaine += item + "<br />"

    elif cmd == "proximity":
        fields = ['name', 'offy_proximityinfluencer_ids']
        datas = sock.execute(
            dbname, uid, pwd, 'hr.employee', 'read', ids, fields)
        for data in datas:
            if len(data['offy_proximityinfluencer_ids']) == 0:
                list_name.append(data['name'])
        list_name = sorted(list_name)
        chaine = (
            "<b>{}</b> Offies do not have proximity influencers for the moment : <br />").format(str(len(list_name)))
        for item in list_name:
            chaine += item + "<br />"

    else:
        fields = ['name', 'offy_proximityinfluencer_ids',
                  'offy_spiritualinfluencer_ids']
        datas = sock.execute(
            dbname, uid, pwd, 'hr.employee', 'read', ids, fields)
        for data in datas:
            if len(data['offy_proximityinfluencer_ids']) == 0 and len(data['offy_spiritualinfluencer_ids']) == 0:
                list_name.append(data['name'])
        list_name = sorted(list_name)
        chaine = (
            "<b>{}</b> Offies do not have any influencers for the moment : <br />").format(str(len(list_name)))
        for item in list_name:
            chaine += item + "<br />"

    bot.send_message_parsed(event.conv, _(str(chaine)))


def topsalary(bot, event, *args):
    list_ids = _search_name_user("")
    list_name = []
    ids = [var['id'] for var in list_ids]  # 267 employee

    fields = ['name', 'offy_salary_range_id']
    datas = sock.execute(dbname, uid, pwd, 'hr.employee', 'read', ids, fields)
    for data in datas:
        if type(data['offy_salary_range_id']) != bool and data['offy_salary_range_id'][0] >= 26:
            list_name.append(data['name'])

    list_name = sorted(list_name)
    chaine = (
        "<b>{}</b> Offies earn more than 22M VND: <br />").format(str(len(list_name)))
    for item in list_name:
        chaine += item + "<br />"

    bot.send_message_parsed(event.conv, _(str(chaine)))


def nosalary(bot, event, *args):
    list_ids = _search_name_user("")
    list_name = []
    ids = [var['id'] for var in list_ids]  # 267 employee

    fields = ['name', 'offy_salary_range_id']
    datas = sock.execute(dbname, uid, pwd, 'hr.employee', 'read', ids, fields)
    for data in datas:
        if type(data['offy_salary_range_id']) == bool:
            list_name.append(data['name'])

    list_name = sorted(list_name)
    chaine = (
        "<b>{}</b> Offies have not set their salaries for the moment : <br />").format(str(len(list_name)))
    for item in list_name:
        chaine += item + "<br />"

    bot.send_message_parsed(event.conv, _(str(chaine)))


#################################################
#################################################

def topproximityinfluencer(bot, event, *args):
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    source_file = os.path.join(plugin_dir, "data.json")

    with open(source_file, 'r+')as f:
        datas = json.load(f)
        chaine = "<b>Top proximity influencers with more than 5 followers: </b><br />"
        chaine += datas['topproximityinfluencer']
        bot.send_message_parsed(event.conv, _(chaine))
    # bot.send_message_parsed(event.conv, _("You have waited so long, I'm proud of you"))
    # list_ids = _search_name_user("")
    # #list_ids = random.sample(list_ids, 20)
    # dict_name = {}
    # for var in list_ids:
    #     args_prox = [('offy_proximityinfluencer_ids', '=' , var['id'])]
    #     ids_prox = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', args_prox)
    #
    #     nb_follower = len(ids_prox)
    #     if nb_follower > 4:
    #         dict_name[var['name']]= nb_follower
    # #bot.send_message_parsed(event.conv, _(str(dict_name)))
    # sorted_dict_name = sorted(dict_name.items(), key=operator.itemgetter(1), reverse=True)
    #
    # chaine = "<b>Top proximity influencers : </b><br />"
    # for i in range(len(sorted_dict_name)):
    #     chaine += ("{} ({}) <br />").format(sorted_dict_name[i][0],str(sorted_dict_name[i][1]))
    #
    # bot.send_message_parsed(event.conv, _(str(chaine)))


def topspiritualinfluencer(bot, event, *args):
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    source_file = os.path.join(plugin_dir, "data.json")

    with open(source_file, 'r+')as f:
        datas = json.load(f)
        chaine = "<b>Top spiritual influencers with more than 5 followers: </b><br />"
        chaine += datas['topspiritualinfluencer']
        bot.send_message_parsed(event.conv, _(chaine))
    # bot.send_message_parsed(event.conv, _("You have waited so long, I'm proud of you"))
    # list_ids = _search_name_user("")
    # #list_ids = random.sample(list_ids, 20)
    # dict_name = {}
    # for var in list_ids:
    #     args_spirit = [('offy_spiritualinfluencer_ids', '=' , var['id'])]
    #     ids_spirit = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', args_spirit)
    #     nb_follower = len(ids_spirit)
    #     if nb_follower > 4:
    #         dict_name[var['name']]= nb_follower
    # #bot.send_message_parsed(event.conv, _(str(dict_name)))
    # sorted_dict_name = sorted(dict_name.items(), key=operator.itemgetter(1), reverse=True)
    #
    # chaine = "<b>Top spiritual influencers : </b><br />"
    # for i in range(len(sorted_dict_name)):
    #     chaine += ("{} ({}) <br />").format(sorted_dict_name[i][0],str(sorted_dict_name[i][1]))
    #
    # bot.send_message_parsed(event.conv, _(str(chaine)))

    # global sorted_list_of_influencers, sorted_list_of_proximity_influencers, sorted_list_of_spiritual_influencers
    # list_ids = _search_name_user("")
    # dict_proximity = {}
    # dict_spiritual ={}
    # dict_global = {}
    # for var in list_ids:
    #     args_prox = [('offy_proximityinfluencer_ids', '=' , var['id'])]
    #     ids_prox = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', args_prox)
    #     args_spirit = [('offy_spiritualinfluencer_ids', '=' , var['id'])]
    #     ids_spirit = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', args_spirit)
    #     nb_follower = len(ids_prox) + len(ids_spirit)
    #     nb_proximity_follower = len(ids_prox)
    #     nb_spiritual_follower = len(ids_spirit)
    #     if nb_follower > 5:
    #         dict_global[var['name']]= nb_follower
    #     if nb_proximity_follower > 3:
    #         dict_proximity[var['name']]= nb_proximity_follower
    #     if nb_spiritual_follower > 3:
    #         dict_spiritual[var['name']] = nb_spiritual_follower
    # sorted_list_of_influencers = sorted(dict_global.items(), key=operator.itemgetter(1), reverse=True)
    # sorted_list_of_proximity_influencers = sorted(dict_proximity.items(), key=operator.itemgetter(1), reverse=True)
    # sorted_list_of_spiritual_influencers = sorted(dict_spiritual.items(), key=operator.itemgetter(1), reverse=True)
    # bot.send_message_parsed(event.conv, _("Done!"))


def topinfluencer(bot, event, *args):

    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    source_file = os.path.join(plugin_dir, "data.json")

    with open(source_file, 'r+')as f:
        datas = json.load(f)
        chaine = "<b>Top influencers with more than 10 followers: </b><br />"
        chaine += datas['topinfluencer']
        bot.send_message_parsed(event.conv, _(chaine))


# def calcultopproximityinfluencer(bot, event, *args):
#
#     bot.send_message_parsed(event.conv, _("You have waited so long, I'm proud of you"))
#     list_ids = _search_name_user("")
#     #list_ids = random.sample(list_ids, 20)
#     dict_name = {}
#     for var in list_ids:
#         args_prox = [('offy_proximityinfluencer_ids', '=' , var['id'])]
#         ids_prox = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', args_prox)
#         #args_spirit = [('offy_spiritualinfluencer_ids', '=' , var['id'])]
#         #ids_spirit = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', args_spirit)
#         nb_follower = len(ids_prox)
#         if nb_follower > 5:
#             dict_name[var['name']]= nb_follower
#     #bot.send_message_parsed(event.conv, _(str(dict_name)))
#     sorted_dict_name = sorted(dict_name.items(), key=operator.itemgetter(1), reverse=True)
#
#     chaine = "<b>Top proximity influencers : </b><br />"
#     for i in range(len(sorted_dict_name)):
#         chaine += ("{} ({}) <br />").format(sorted_dict_name[i][0],str(sorted_dict_name[i][1]))
#
#     bot.send_message_parsed(event.conv, _(str(chaine)))
#
#     plugin_dir = os.path.dirname(os.path.realpath(__file__))
#     source_file = os.path.join(plugin_dir, "data.json")
#
#     with open(source_file, 'r+')as f:
#         result = json.load(f)
#         result['topproximityinfluencer'] = chaine
#
#
#         f.seek(0)
#         json.dump(result, f, indent=4)
#         f.truncate()
#
#
#


def computetopinfluencer():
    list_ids = _search_name_user("")
    dict_name = {}
    dict_name_prox = {}
    dict_name_spirit = {}
    for var in list_ids:
        args_prox = [('offy_proximityinfluencer_ids', '=', var['id'])]
        ids_prox = sock.execute(
            dbname, uid, pwd, 'hr.employee', 'search', args_prox)
        args_spirit = [('offy_spiritualinfluencer_ids', '=', var['id'])]
        ids_spirit = sock.execute(
            dbname, uid, pwd, 'hr.employee', 'search', args_spirit)
        nb_follower = len(ids_prox)+len(ids_spirit)
        nb_follower_prox = len(ids_prox)
        nb_follower_spirit = len(ids_spirit)
        if nb_follower > 9:
            dict_name[var['name']] = nb_follower
    # bot.send_message_parsed(event.conv, _(str(dict_name)))
        if nb_follower_prox > 4:
            dict_name_prox[var['name']] = nb_follower_prox
        if nb_follower_spirit > 4:
            dict_name_spirit[var['name']] = nb_follower_spirit

    sorted_dict_name = sorted(
        dict_name.items(), key=operator.itemgetter(1), reverse=True)
    sorted_dict_name_prox = sorted(
        dict_name_prox.items(), key=operator.itemgetter(1), reverse=True)
    sorted_dict_name_spirit = sorted(
        dict_name_spirit.items(), key=operator.itemgetter(1), reverse=True)

    chaine = ""
    chaine_prox = ""
    chaine_spirit = ""
    for i in range(len(sorted_dict_name)):
        chaine += ("{} ({}) <br />").format(
            sorted_dict_name[i][0], str(sorted_dict_name[i][1]))
    for i in range(len(sorted_dict_name_prox)):
        chaine_prox += ("{} ({}) <br />").format(
            sorted_dict_name_prox[i][0], str(sorted_dict_name_prox[i][1]))
    for i in range(len(sorted_dict_name_spirit)):
        chaine_spirit += ("{} ({}) <br />").format(
            sorted_dict_name_spirit[i][0], str(sorted_dict_name_spirit[i][1]))

    # bot.send_message_parsed(event.conv, _(str(chaine)))
    # bot.send_message_parsed(event.conv, _(str(chaine_prox)))
    # bot.send_message_parsed(event.conv, _(str(chaine_spirit)))

    # write it in "data.json"
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    source_file = os.path.join(plugin_dir, "data.json")

    with open(source_file, 'r+')as f:
        result = json.load(f)
        result['topinfluencer'] = chaine
        result['topproximityinfluencer'] = chaine_prox
        result['topspiritualinfluencer'] = chaine_spirit

        f.seek(0)
        json.dump(result, f, indent=4)
        f.truncate()


# GET Offy horoscope
def horoscope(bot, event, *args):
    name_user = " ".join(args)

    list_ids_offy = _search_name_user(name_user)
    list_ids_partner = _search_name_partner(name_user)
    list_ids = list_ids_offy + list_ids_partner

    chaine = ""
    if len(list_ids) == 0:
        bot.send_message_parsed(event.conv, _(
            "You wanna know about <b>'{}'</b>? I don't have anything to say to you, enlarge your search!").format(str(name_user)))
    elif name_user == "":
        bot.send_message_parsed(event.conv, _(
            "Give me a name! Please!").format(str(name_user)))

    else:
        if len(list_ids_offy) > 3 or len(list_ids_partner) > 3:
            if len(list_ids) <= 100:
                chaine += ("I could display <b>{}</b> answers for <b>'{}'</b> but I'm tired, please check the list below :<br />").format(
                    str(len(list_ids)), str(name_user))
                # fields = ['name'] #fields to read
                # ids = [var['id']for var in list_ids_partner]
                # datas = sock.execute(dbname, uid, pwd, 'res.partner', 'read', ids, fields) #liste des personnes trouvées, influencer (liste ids)
                # liste = [] # pour avoir une liste de nom ordonnée
                # for data in datas:
                #     liste.append(data['name'])
                liste = [var['name'] for var in list_ids]
                liste = sorted(liste)
                for name in liste:
                    chaine += name + '<br />'
                chaine += '<br />'
            else:
                chaine += ("I could display <b>{}</b> answers for <b>'{}'</b> but I'm bored, please try to precise your search.<br />").format(
                    str(len(list_ids)), str(name_user))

        # Here we display the Offies
        if len(list_ids_offy) > 3:
            list_ids_offy = random.sample(list_ids_offy, 3)

        fields = ['cluster_id', 'image_medium', 'offy_salary_range_id',
                  'offy_proximityinfluencer_ids', 'offy_spiritualinfluencer_ids', 'birthday']
        ids = [var['id']for var in list_ids_offy]
        data = sock.execute(dbname, uid, pwd, 'hr.employee',
                            'read', ids, fields)

        for i in range(len(list_ids_offy)):
            name_user = list_ids_offy[i]['name']
            id_user = list_ids_offy[i]['id']

            image = data[i]['image_medium']
            if image == False:  # do not display anything if the user do not profil picture
                image_id = None
            else:
                raw = base64.b64decode(image)
                image_data = io.BytesIO(raw)
                filename = str(name_user) + ".jpg"
                image_id = yield from bot._client.upload_image(image_data, filename=filename)

            url_link = (
                '"https://dinh.officience.com/web#id={}&view_type=form&model=hr.employee&menu_id=492&action=130"').format(str(id_user))
            url = ("<a href={}>{}</a>").format(url_link, str(name_user))

            #####################
            chaine = ("{}<br />").format(str(url))
            if type(data[i]['birthday']) == bool:
                chaine += ("<b>The date of birth is not set</b><br />")
            else:
                birthday_str = data[i]['birthday'].split("-")
                birthday_year = birthday_str[0]
                birthday_month = int(birthday_str[1])
                birthday_day = int(birthday_str[2])
                astro_sign = ''

             # GET today horoscope from: https://aztro.readthedocs.io/en/latest/
                astro_sign = horoscope_sign(birthday_day, birthday_month)
                params = (
                    ('sign', astro_sign.lower()),
                    ('day', 'today'),
                )
                today_horoscope = requests.post(
                    'https://aztro.sameerkumar.website/', params=params).json()

                chaine += ("<b>Birthday : </b>{}<br />").format(
                    str(data[i]['birthday']))
                chaine += ("<b>Your sign is : </b>{}<br />").format(
                    str(astro_sign))
                chaine += ("<b>Daily horoscope on : </b> {}<br />").format(
                    str(today_horoscope['current_date']))
                chaine += ("<b>Your horoscope is : </b> {}<br />").format(
                    str(today_horoscope['description']))
                chaine += ("<b>Compatibility : </b>{}<br />").format(
                    str(today_horoscope['compatibility']))
                chaine += ("<b>Color : </b>{}<br />").format(
                    str(today_horoscope['color']))
                chaine += ("<b>Mood : </b>{}<br />").format(
                    str(today_horoscope['mood']))
                chaine += ("<b>Lucky number : </b>{}<br />").format(
                    str(today_horoscope['lucky_number']))
                chaine += ("<b>Lucky time : </b>{}<br />").format(
                    str(today_horoscope['lucky_time']))

            segments = simple_parse_to_segments(chaine)
            bot.send_message_segments(
                event.conv.id_, segments, None, image_id=image_id)
    # counter('horoscope')

####################################################
# GET Offy skill by offy_name
def offyskill(bot, event, *args):
    name_user = " ".join(args)

    list_ids_offy = _search_name_user(name_user)
    list_ids_partner = _search_name_partner(name_user)
    list_ids = list_ids_offy + list_ids_partner

    chaine = ""
    if len(list_ids) == 0:
        bot.send_message_parsed(event.conv, _(
            "You wanna know about <b>'{}'</b>? I don't have anything to say to you, enlarge your search!").format(str(name_user)))
    elif name_user == "":
        bot.send_message_parsed(event.conv, _(
            "Give me a name! Please!").format(str(name_user)))

    else:
        if len(list_ids_offy) > 3 or len(list_ids_partner) > 3:
            if len(list_ids) <= 100:
                chaine += ("I could display <b>{}</b> answers for <b>'{}'</b> but I'm tired, please check the list below :<br />").format(
                    str(len(list_ids)), str(name_user))
                # fields = ['name'] #fields to read
                # ids = [var['id']for var in list_ids_partner]
                # datas = sock.execute(dbname, uid, pwd, 'res.partner', 'read', ids, fields) #liste des personnes trouvées, influencer (liste ids)
                # liste = [] # pour avoir une liste de nom ordonnée
                # for data in datas:
                #     liste.append(data['name'])
                liste = [var['name'] for var in list_ids]
                liste = sorted(liste)
                for name in liste:
                    chaine += name + '<br />'
                chaine += '<br />'
            else:
                chaine += ("I could display <b>{}</b> answers for <b>'{}'</b> but I'm bored, please try to precise your search.<br />").format(
                    str(len(list_ids)), str(name_user))

        # Here we display the Offy skill
        if len(list_ids_offy) > 3:
            list_ids_offy = random.sample(list_ids_offy, 3)

        fields = ['cluster_id', 'image_medium', 'offy_salary_range_id',
                  'offy_proximityinfluencer_ids', 'offy_spiritualinfluencer_ids', 'birthday', 'competencies_ids', 'offy_skill_time_ids']
        ids = [var['id']for var in list_ids_offy]
        data = sock.execute(dbname, uid, pwd, 'hr.employee',
                            'read', ids, fields)

        for i in range(len(list_ids_offy)):
            name_user = list_ids_offy[i]['name']
            id_user = list_ids_offy[i]['id']

            image = data[i]['image_medium']
            if image == False:  # do not display anything if the user do not profil picture
                image_id = None
            else:
                raw = base64.b64decode(image)
                image_data = io.BytesIO(raw)
                filename = str(name_user) + ".jpg"
                image_id = yield from bot._client.upload_image(image_data, filename=filename)

            url_link = (
                '"https://dinh.officience.com/web#id={}&view_type=form&model=hr.employee&menu_id=492&action=130"').format(str(id_user))
            url = ("<a href={}>{}</a>").format(url_link, str(name_user))
            # whofollows
            proximity_influencer = ""
            for id in data[i]['offy_proximityinfluencer_ids']:
                proximity_influencer += dico_id_name[id] + ", "
            spiritual_influencer = ""
            for id in data[i]['offy_spiritualinfluencer_ids']:
                spiritual_influencer += dico_id_name[id] + ", "

            # wholeads
            args_prox = [('offy_proximityinfluencer_ids', '=', id_user)]
            ids_prox = sock.execute(
                dbname, uid, pwd, 'hr.employee', 'search', args_prox)
            args_spirit = [('offy_spiritualinfluencer_ids', '=', id_user)]
            ids_spirit = sock.execute(
                dbname, uid, pwd, 'hr.employee', 'search', args_spirit)

            proximity_follower = ""
            for id in ids_prox:
                proximity_follower += dico_id_name[id] + ", "
            spiritual_follower = ""
            for id in ids_spirit:
                spiritual_follower += dico_id_name[id] + ", "

            # Competencies
            competencies = ""
            comp_names = sock.execute(
                dbname, uid, pwd, 'hr.employee.competencies', 'read', data[i]['competencies_ids'], [])

            for c_name in comp_names:
                competencies += str(c_name['name']) + ", "

            # Skills
            skills = ""
            skills_names = sock.execute(
                dbname, uid, pwd, 'offy.skill.time', 'read', data[i]['offy_skill_time_ids'], [])
            for s_name in skills_names:
                skills += str(s_name['offy_competencies_id'][1]) + \
                    " (" + str(s_name['offy_time']) + "h)" + ", "

            #####################
            chaine = ("{}<br />").format(str(url))
            if type(data[i]['cluster_id']) != bool:
                chaine += ("<b>Cluster : </b>{}<br />").format(
                    str(data[i]['cluster_id'][1]))
            if type(data[i]['birthday']) != bool:
                birthday_str = data[i]['birthday'].split("-")
                birthday_month = int(birthday_str[1])
                birthday_day = int(birthday_str[2])
                astro_sign = horoscope_sign(birthday_day, birthday_month)
                chaine += ("<b>Astro sign : </b>{}<br />").format(
                    str(astro_sign))

            if competencies != "":
                chaine += ("<b> Competencies : </b>{}<br />").format(competencies)
            else:
                chaine += ("<b> Competencies : </b>{}<br />").format('The competency is not set')

            if skills != "":
                chaine += ("<b> Skills : </b>{}<br />").format(skills)
            else:
                chaine += ("<b> Skills : </b>{}<br />").format('The skill is not set')

            segments = simple_parse_to_segments(chaine)
            bot.send_message_segments(
                event.conv.id_, segments, None, image_id=image_id)

    
    
# GET Offy skill by Skill name
def whoskill(bot, event, *args):
    skill_name = " ".join(args)

    # list_ids_offy = _search_name_user(name_user)
    # list_ids_partner = _search_name_partner(name_user)
    # list_ids = list_ids_offy + list_ids_partner

    chaine = ""
    if skill_name == "":
        bot.send_message_parsed(event.conv, _(
            "Give me a name! Please!").format(str(skill_name)))
    elif skill_name == "all":
        comp_ids = sock.execute(
            dbname, uid, pwd, 'hr.employee.competencies', 'search', [])
        for comp_id in comp_ids:
            comp_name = sock.execute(
                dbname, uid, pwd, 'hr.employee.competencies', 'read', comp_id, [])
            bot.send_message_parsed(event.conv, _("name: " + str(comp_name)))

    else:
        # bot.send_message_parsed(event.conv, _(str("You are looking for offies who have skill similar to " + skill_name)))
        chaine += ("You are looking for offies who have skill similar to <b>{}</b><br />").format(str(skill_name))
        chaine += '-----------------------------------------<br />'
        query = [('name', 'ilike', '%' + skill_name + '%')]
        comp_ids = sock.execute(
            dbname, uid, pwd, 'hr.employee.competencies', 'search', query)
        if len(comp_ids) > 0:
            for comp_id in comp_ids:
                comp_data = sock.execute(dbname, uid, pwd, 'hr.employee.competencies', 'read', comp_id, [])
            
                chaine += ("<b>{} skill: </b><br />").format(str(comp_data['name']))
                if len(comp_data['employee_ids']) > 0:
                    offy_name = ""
                    offy_data = sock.execute(dbname, uid, pwd, 'hr.employee', 'read', comp_data['employee_ids'], ['name'])
                    for offy in offy_data:  
                        offy_name += offy['name'] + ", "
            
                    chaine += ("Offy Name: {}<br />").format(str(offy_name))
                    chaine += '-----------------------------------------<br />'
                else: 
                    chaine += ("No offies set thier skill similar to <b>{}</b><br />").format(str(comp_data['name']))
                    chaine += '-----------------------------------------<br />'
        else: 
            chaine += ("No offies who have have skill similar to <b>{}</b><br />").format(str(skill_name))

        bot.send_message_parsed(event.conv, _(chaine))
        
        #segments = simple_parse_to_segments(chaine)
        

##################
# GET Offy Age
def offyage(bot, event, *args):
    name_user = " ".join(args)

    list_ids_offy = _search_name_user(name_user)
    list_ids_partner = _search_name_partner(name_user)
    list_ids = list_ids_offy + list_ids_partner

    chaine = ""
    if len(list_ids) == 0:
        bot.send_message_parsed(event.conv, _(
            "You wanna know about <b>'{}'</b>? I don't have anything to say to you, enlarge your search!").format(str(name_user)))
    elif name_user == "":
        bot.send_message_parsed(event.conv, _(
            "Give me a name! Please!").format(str(name_user)))

    else:
        if len(list_ids_offy) > 3 or len(list_ids_partner) > 3:
            if len(list_ids) <= 100:
                chaine += ("I could display <b>{}</b> answers for <b>'{}'</b> but I'm tired, please check the list below :<br />").format(
                    str(len(list_ids)), str(name_user))
                # fields = ['name'] #fields to read
                # ids = [var['id']for var in list_ids_partner]
                # datas = sock.execute(dbname, uid, pwd, 'res.partner', 'read', ids, fields) #liste des personnes trouvées, influencer (liste ids)
                # liste = [] # pour avoir une liste de nom ordonnée
                # for data in datas:
                #     liste.append(data['name'])
                liste = [var['name'] for var in list_ids]
                liste = sorted(liste)
                for name in liste:
                    chaine += name + '<br />'
                chaine += '<br />'
            else:
                chaine += ("I could display <b>{}</b> answers for <b>'{}'</b> but I'm bored, please try to precise your search.<br />").format(
                    str(len(list_ids)), str(name_user))

        # Here we display the Offies
        if len(list_ids_offy) > 3:
            list_ids_offy = random.sample(list_ids_offy, 3)

        fields = ['cluster_id', 'image_medium', 'offy_salary_range_id',
                  'offy_proximityinfluencer_ids', 'offy_spiritualinfluencer_ids', 'birthday']
        ids = [var['id']for var in list_ids_offy]
        data = sock.execute(dbname, uid, pwd, 'hr.employee',
                            'read', ids, [])

        for i in range(len(list_ids_offy)):
            name_user = list_ids_offy[i]['name']
            id_user = list_ids_offy[i]['id']

            image = data[i]['image_medium']
            if image == False:  # do not display anything if the user do not profil picture
                image_id = None
            else:
                raw = base64.b64decode(image)
                image_data = io.BytesIO(raw)
                filename = str(name_user) + ".jpg"
                image_id = yield from bot._client.upload_image(image_data, filename=filename)

            url_link = (
                '"https://dinh.officience.com/web#id={}&view_type=form&model=hr.employee&menu_id=492&action=130"').format(str(id_user))
            url = ("<a href={}>{}</a>").format(url_link, str(name_user))
            # whofollows
            proximity_influencer = ""
            for id in data[i]['offy_proximityinfluencer_ids']:
                proximity_influencer += dico_id_name[id] + ", "
            spiritual_influencer = ""
            for id in data[i]['offy_spiritualinfluencer_ids']:
                spiritual_influencer += dico_id_name[id] + ", "

            # wholeads
            args_prox = [('offy_proximityinfluencer_ids', '=', id_user)]
            ids_prox = sock.execute(
                dbname, uid, pwd, 'hr.employee', 'search', args_prox)
            args_spirit = [('offy_spiritualinfluencer_ids', '=', id_user)]
            ids_spirit = sock.execute(
                dbname, uid, pwd, 'hr.employee', 'search', args_spirit)

            proximity_follower = ""
            for id in ids_prox:
                proximity_follower += dico_id_name[id] + ", "
            spiritual_follower = ""
            for id in ids_spirit:
                spiritual_follower += dico_id_name[id] + ", "

            #####################
            chaine = ("{}<br />").format(str(url))
           
            if type(data[i]['cluster_id']) != bool:
                chaine += ("<b>Cluster : </b>{}<br />").format(
                    str(data[i]['cluster_id'][1]))
            if type(data[i]['birthday']) != bool:
                birthday_str = data[i]['birthday'].split("-")
                birthday_month = int(birthday_str[1])
                birthday_day = int(birthday_str[2])
                astro_sign = horoscope_sign(birthday_day, birthday_month)
                chaine += ("<b>Astro sign : </b>{}<br />").format(
                    str(astro_sign))

            chaine += ("<b>Created date on Dinh: </b>{}<br />").format(
                    str(data[i]['create_date']))

            c_year = int (str(data[i]['create_date'][:4]))
            c_month = int (str(data[i]['create_date'][5:7]))
            c_day = int (str(data[i]['create_date'][8:10]))
    
            # chaine += ("<b>Created year on Dinh: </b>{}<br />").format(
            #         str(year))
            # chaine += ("<b>Created month on Dinh: </b>{}<br />").format(
            #         str(month))
            # chaine += ("<b>Created day on Dinh: </b>{}<br />").format(
            #         str(day))

            current_date = datetime.now()
            l_date = date(current_date.year, current_date.month, current_date.day)
            f_date = date(c_year, c_month, c_day)
            delta = l_date - f_date

            year = int(delta.days / 365) 
            week = int((delta.days % 365) / 7)
            days = (delta.days % 365) % 7 
            if (c_year == 2014):
                chaine += ("<b>Offy age over: </b>{} year(s)<br />").format(str(current_date.year - c_year))
            else: 
                chaine += ("<b>Offy age: </b>{} year(s) {} week(s) {} day(s)<br />").format(str(year), str(week), str(days))
            
            segments = simple_parse_to_segments(chaine)
            bot.send_message_segments(
                event.conv.id_, segments, None, image_id=image_id)

##################
# GET Cashin
def cashin(bot, event, *args):
    param = " ".join(args)
    chaine = ""
     
    total = 0
    
    query = [('date_order', 'like', param + '%'), ('state', '!=', 'cancel')]
    # bot.send_message_parsed(event.conv, _(chaine)) 
    ids = sock.execute(
            dbname, uid, pwd, 'sale.order', 'search', query)
    # details = sock.execute(dbname, uid, pwd, 'sale.order.line', 'read', ids,[])
    for id in ids:
        detail = sock.execute(dbname, uid, pwd, 'sale.order', 'read', id, [])

        chaine +=("<b>Name: </b> {} <br />").format(str(detail['display_name']))
        chaine +=("<b>Date order: </b> {} <br />").format(str(detail['date_order']))
        chaine +=("<b>Last update: </b> {} <br />").format(str(detail['__last_update']))
        chaine +=("<b>State: </b>{} <br /> ").format(detail['state'])
        price = round(detail['offy_amount_total_eur'], 2)
        chaine +=("<b>Price: </b>{:,}€ <br /> ").format(price)
        chaine += '-----------------------------------------<br />'

        # bot.send_message_parsed(event.conv, _("Data: " + str(detail)))
        # bot.send_message_parsed(event.conv, _("Name: " + str(detail['name']))) 
        # bot.send_message_parsed(event.conv, _("Last update: " + str(detail['__last_update'])))   
        # bot.send_message_parsed(event.conv, _("Price: " + str(detail['offy_amount_total_eur'])))  
        total += detail['offy_amount_total_eur']
        total = round(total, 2)
    chaine += ("<b>Quote sent on {}: {:,}€</b>").format(str(param), (total))
    bot.send_message_parsed(event.conv, _(chaine))

##################
# GET Cashout
def cashout(bot, event, *args):
    param = " ".join(args)
    chaine = ""
     
    total = 0
    
    query = [('date_order', 'like', param + '%'),('state','!=', 'false')]
    # bot.send_message_parsed(event.conv, _(chaine)) 
    ids = sock.execute(
            dbname, uid, pwd, 'purchase.order', 'search', query )

    for id in ids:
        detail = sock.execute(dbname, uid, pwd, 'purchase.order', 'read', id, [])

        chaine +=("<b>Name: </b> {} <br />").format(str(detail['display_name']))
        chaine +=("<b>Date order: </b> {} <br />").format(str(detail['date_order']))
        chaine +=("<b>Last update: </b> {} <br />").format(str(detail['__last_update']))
        price = round(detail['offy_amount_total_eur'], 2)
        chaine +=("<b>Price: </b>{:,}€ <br /> ").format(price)
        # chaine +=("<b>State:</b>{}đ <br /> ").format(detail['state'])
        chaine += '-----------------------------------------<br />'

        # bot.send_message_parsed(event.conv, _("Data: " + str(detail)))
        # bot.send_message_parsed(event.conv, _("Name: " + str(detail['name']))) 
        # bot.send_message_parsed(event.conv, _("Last update: " + str(detail['__last_update'])))   
        # bot.send_message_parsed(event.conv, _("Price: " + str(detail['offy_amount_total_eur'])))  
        total += detail['offy_amount_total_eur']
        total = round(total, 2)
    chaine += ("<b>Expense Forecasting on {}: {:,}€ </b>").format(str(param), (total))
    bot.send_message_parsed(event.conv, _(chaine))