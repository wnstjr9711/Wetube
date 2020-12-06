import json
import pymysql

db = pymysql.connect(host='database-2.ckxupymlkkbs.ap-northeast-2.rds.amazonaws.com', port=3306, user='root', passwd='kjs97871103', db='service', charset='utf8',
                     autocommit=True)


def create_room(uid, code, playlists):
    cursor = db.cursor()
    sql = "INSERT INTO room (uchatid, roomcode) VALUES ('{}', '{}')".format(uid, code)
    cursor.execute(sql)
    for i in playlists:
        sql2 = "INSERT INTO roomdata (uchatid, playlists) VALUES ('{}', '{}')".format(uid, json.dumps(i))
        cursor.execute(sql2)
    return


def get_rooms():
    cursor = db.cursor()
    sql = "Select uchatid, roomcode from room"
    cursor.execute(sql)
    result = dict()
    for i in cursor.fetchall():
        result[i[1]] = i[0]
    return result


def get_playlists(uid):
    cursor = db.cursor()
    sql = "Select playlists from roomdata where uchatid = '{}'". format(uid)
    cursor.execute(sql)
    result = list()
    for i in cursor.fetchall():
        if i[0] is not None:
            result.append(eval(i[0]))
    return result


def get_playlist(uid):
    cursor = db.cursor()
    sql = "Select playlist from room where uchatid = '{}'".format(uid)
    cursor.execute(sql)
    result = cursor.fetchall()
    if result:
        return result[0][0]


def get_videos(uid):
    cursor = db.cursor()
    sql = "Select videos from roomdata where uchatid = '{}'". format(uid)
    cursor.execute(sql)
    result = list()
    for i in cursor.fetchall():
        if i[0] is not None:
            result.append(eval(i[0]))
    return result


def get_video(uid):
    cursor = db.cursor()
    sql = "Select video from room where uchatid = '{}'".format(uid)
    cursor.execute(sql)
    result = cursor.fetchall()
    if result[0][0] is not None:
        return eval(result[0][0])


def set_playlist(uid, playlist):  # playlist 바꾸면 video 초기화
    cursor = db.cursor()
    sql = "UPDATE room SET playlist='{}' WHERE uchatid = '{}'".format(playlist, uid)
    cursor.execute(sql)
    sql2 = "UPDATE room SET video = null WHERE uchatid = '{}'".format(uid)
    cursor.execute(sql2)
    sql3 = "DELETE FROM roomdata WHERE uchatid = '{}' AND playlists is null".format(uid)
    cursor.execute(sql3)
    # set_video(uid, playlist[sni])
    return


def set_videos(uid, videos):
    cursor = db.cursor()
    for i in videos:
        i['snippet'].pop('description')
        sql = "INSERT INTO roomdata (uchatid, videos) values('{}', '{}')".format(uid, json.dumps(i))
        cursor.execute(sql)
    return


def set_video(uid, video):
    cursor = db.cursor()
    sql = "UPDATE room SET video='{}' WHERE uchatid = '{}'".format(json.dumps(video), uid)
    cursor.execute(sql)
    return
