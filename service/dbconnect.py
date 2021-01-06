import json
import pymysql


def connect():
    db = pymysql.connect(host='database-2.ckxupymlkkbs.ap-northeast-2.rds.amazonaws.com', port=3306, user='root',
                         passwd='kjs97871103', db='service', charset='utf8',
                         autocommit=True)
    return db


def create_room(uid, code, playlists):
    db = connect()
    cursor = db.cursor()
    sql = "INSERT INTO room (uchatid, roomcode) VALUES ('{}', '{}')".format(uid, code)
    cursor.execute(sql)
    for i in playlists:
        sql2 = "INSERT INTO roomdata (uchatid, playlists) VALUES ('{}', '{}')".format(uid, json.dumps(i))
        cursor.execute(sql2)
    db.close()
    return


def create_roomTest(uid, code, playlists):
    db = connect()
    cursor = db.cursor()
    sql = "DELETE FROM roomdata WHERE uchatid = '{}';".format(uid)
    cursor.execute(sql)
    sql2 = "DELETE FROM room WHERE uchatid = '{}';".format(uid)
    cursor.execute(sql2)
    db.close()
    return create_room(uid, code, playlists)


def get_rooms():
    db = connect()
    cursor = db.cursor()
    sql = "Select uchatid, roomcode from room"
    cursor.execute(sql)
    result = dict()
    for i in cursor.fetchall():
        result[i[1]] = i[0]
    db.close()
    return result


def get_playlists(uid):
    db = connect()
    cursor = db.cursor()
    sql = "Select playlists from roomdata where uchatid = '{}'".format(uid)
    cursor.execute(sql)
    result = list()
    for i in cursor.fetchall():
        if i[0] is not None:
            result.append(eval(i[0]))
    db.close()
    return result


def get_playlist(uid):
    db = connect()
    cursor = db.cursor()
    sql = "Select playlist from room where uchatid = '{}'".format(uid)
    cursor.execute(sql)
    result = cursor.fetchall()
    db.close()
    if result:
        return result[0][0]


def get_videos(uid):
    db = connect()
    cursor = db.cursor()
    sql = "Select videos from roomdata where uchatid = '{}'".format(uid)
    cursor.execute(sql)
    result = list()
    for i in cursor.fetchall():
        if i[0] is not None:
            result.append(eval(i[0]))
    db.close()
    return result


def get_video(uid):
    db = connect()
    cursor = db.cursor()
    sql = "Select video from room where uchatid = '{}'".format(uid)
    cursor.execute(sql)
    result = cursor.fetchall()
    db.close()
    if result[0][0] is not None:
        return eval(result[0][0])


def set_playlist(uid, playlist):  # playlist 바꾸면 video 초기화
    db = connect()
    cursor = db.cursor()
    sql = "UPDATE room SET playlist='{}' WHERE uchatid = '{}'".format(playlist, uid)
    cursor.execute(sql)
    sql2 = "UPDATE room SET video = null WHERE uchatid = '{}'".format(uid)
    cursor.execute(sql2)
    sql3 = "DELETE FROM roomdata WHERE uchatid = '{}' AND playlists is null".format(uid)
    cursor.execute(sql3)
    db.close()
    return


# video 제목에 존재하는 json 이스케이프 및 unicode -> ascii 예외처리
def set_videos(uid, videos):
    db = connect()
    cursor = db.cursor()
    for v in videos:
        v['snippet'].pop('description')
        v['snippet']['title'] = jsonEscape(v['snippet']['title'])
        sql = "INSERT INTO roomdata (uchatid, videos) values('{}', '{}')".format(uid,
                                                                                 json.dumps(v, ensure_ascii=False))
        cursor.execute(sql)
    db.close()
    return


def set_video(uid, video):
    db = connect()
    cursor = db.cursor()
    video['snippet']['title'] = jsonEscape(video['snippet']['title'])
    sql = "UPDATE room SET video='{}' WHERE uchatid = '{}'".format(json.dumps(video, ensure_ascii=False), uid)
    cursor.execute(sql)
    db.close()
    return


def jsonEscape(e):
    e = e.replace('/', '\/')
    e = e.replace('\'', '')
    e = e.replace('"', '')
    e = e.replace('\n', '')
    e = e.replace('\r', '')
    e = e.replace('\t', ' ')
    return e
