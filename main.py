import vconfig as userconf
import os
import MySQLdb
import time
import json
import urllib.request

def write_py():
    print(time.time())
    with open("vconfig.py",'w') as py_config:
        py_config.write("""
sites = """ + str(userconf.sites) + """
board = '""" + userconf.board + """'
database = '""" + userconf.database + """'
user = '""" + userconf.user + """'
password = '""" + userconf.password + """'
last_check = """ + str(int(time.time())) + """
""")
        py_config.close()

def sanitize_post_data(post_data):
    if post_data != None:
        #sanitize data
        post_data = post_data.replace("&hellip;","...")
        #post_data = post_data.replace(";","&#59;")
        post_data = post_data.replace("'","&#39;")

    return post_data

def retrieve_and_store_image(file_name, file_ext, file_size,
    file_width, file_height, thumb_width, thumb_height, target_site, target_name):
    if file_name == None:
        return None
    else:
        print(file_width)
        print(file_height)
        print(thumb_width)
        print(thumb_height)
        print(target_site + "src/" + str(target_name) + file_ext)
        if file_ext == ".webm" or file_ext == ".mp4":
            urllib.request.urlretrieve(target_site + "thumb/" + str(target_name) + ".jpg",
                userconf.thumb_storage_location_absolute + str(target_name) + ".jpg")
            urllib.request.urlretrieve(target_site + "src/" + str(target_name) + file_ext,
                userconf.file_storage_location_absolute + str(target_name) + file_ext)
            file_json = returnFileJSON("video", file_name, file_ext, file_size, target_name,
                file_width, file_height, thumb_width, thumb_height)
        else:
            urllib.request.urlretrieve(target_site + "thumb/" + str(target_name) + file_ext,
                userconf.thumb_storage_location_absolute + str(target_name) + file_ext)
            urllib.request.urlretrieve(target_site + "src/" + str(target_name) + file_ext,
                userconf.file_storage_location_absolute + str(target_name) + file_ext)
            file_json = returnFileJSON("image", file_name, file_ext, file_size, target_name,
                file_width, file_height, thumb_width, thumb_height)
        print(file_json)
        return file_json

def returnFileJSON(type, file_name, file_ext, file_size, target_name,
    file_width, file_height, thumb_width, thumb_height):
    return """[{
        "name":\"""" +  file_name +"""\",
        "type":\"""" + type + "\/" + file_ext[1:] +"""\",
        "tmp_name":"None",
        "error":0,
        "size":""" + str(file_size) + """,
        "filename":\"""" + file_name + file_ext + """\",
        "extension":\"""" + file_ext[1:] + """\",
        "file_id":\"""" + str(target_name) +"""\",
        "file":\"""" + str(target_name) + file_ext +"""\",
        "thumb":\"""" + str(target_name) + file_ext +"""\",
        "is_an_image":true,
        "hash":"nomd5",
        "width": """ + str(file_width) + """,
        "height":""" + str(file_height) + """,
        "thumbwidth":""" + str(thumb_width) + """,
        "thumbheight":""" + str(thumb_height) + """,
        "file_path":\"""" + userconf.file_storage_location + str(target_name) + file_ext + """\",
        "thumb_path":\"""" + userconf.thumb_storage_location + str(target_name) + file_ext + """\"}]"""

db = MySQLdb.connect(host="localhost",user=userconf.user, passwd=userconf.password,
                        db=userconf.database)
db_obj = db.cursor()

sitestring = ",".join(userconf.sites)
site_data_arr = (os.popen("sudo python3 ../Multipurpose-Regex-Webscraper/py-cmd/regexscraper.py -u \"" + sitestring + "\" -r \(.*\) --raw"))
for site_no, site_data in enumerate(site_data_arr):
    site_json = (json.loads(site_data))
    for thread_container in reversed(site_json):
        for thread in reversed(thread_container["threads"]):
            if(int(thread["time"]) > userconf.last_check):
                thread_url = userconf.sites[site_no][0:-12] + "res/" + str(thread.get("no"))
                pd = [
                    "0", #ud
                    None, #thread
                    thread.get("sub"), #sub
                    thread.get("email"), #email
                    thread.get("name"), #name
                    thread.get("trip"), #trip
                    thread.get("capcode"), #capcode
                    (thread.get("com") + "<br/><a href=" + thread_url + ">" + thread_url + "</a>"
                        if thread.get("com") != None else "<a href=" + thread_url + ">" + thread_url + "</a>") , #body
                    (thread.get("com") + "<br/><a href=" + thread_url + ">" + thread_url + "</a>"
                        if thread.get("com") != None else "<a href=" + thread_url + ">" + thread_url + "</a>"), #body_nomarkup
                    str(int(time.time())), #time
                    str(int(time.time())), #bump
                    retrieve_and_store_image(
                        thread.get("filename"), #name
                        thread.get("ext"), #ext
                        thread.get("fsize"), #file_size
                        thread.get("w"), #file_width
                        thread.get("h"), #file_height
                        thread.get("tn_w"), #thumb_width
                        thread.get("tn_h"), #thumb_height
                        userconf.sites[site_no][0:-12], #target site
                        thread.get("tim")#target_name
                    ), #image
                    "1", #num_files
                    "nomd5", # filehash
                    "cantdeletethis", #password
                    "127.0.0.1", #ip
                    "0", #sticky
                    "0", #locked
                    "0", #cycle
                    "0", #sage
                    thread.get("embed"), #embed
                    thread.get("sub") #slug
                    ]
                for index, data in enumerate(pd):
                    pd[index] = sanitize_post_data(data)
                db_obj.execute("INSERT INTO posts_" + userconf.board + """(id,
                thread,subject,email,name,trip,capcode,body,body_nomarkup,time,
                bump,files,num_files,filehash,password,ip,sticky,locked,cycle,
                sage,embed,slug)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
                (pd[0],pd[1],pd[2],pd[3],pd[4],pd[5],pd[6],pd[7],pd[8],pd[9],pd[10],
                pd[11],pd[12],pd[13],pd[14],pd[15],pd[16],pd[17],pd[18],pd[19],pd[20],
                pd[21],))


#write_py()
db.close()
