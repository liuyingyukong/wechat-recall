# coding:utf-8
import itchat
from itchat.content import TEXT
from itchat.content import *
import sys
import time
import re
reload(sys)
sys.setdefaultencoding('utf8')
import os
msg_information = {}
face_bug = None # 针对表情包的内容
@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True, isMpChat=True)
def handle_receive_msg(msg):
    global face_bug
    msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 接受消息的时间
    msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName'] # 在好友列表中查询发送信息的好友昵称
    msg_time = msg['CreateTime'] # 信息发送的时间
    msg_id = msg['MsgId'] # 每条信息的id
    msg_content = None # 储存信息的内容
    msg_share_url = None # 储存分享的链接，比如分享的文章和音乐
    print msg['Type']
    #print msg['MsgId']
    if msg['Type'] == 'Text' or msg['Type'] == 'Friends': # 如果发送的消息是文本或者好友推荐
        msg_print_content = msg_time_rec + ' ' + msg_from + ': ' +msg['Text']
        msg_content = msg['Text']
        print msg_print_content # 如果发送的消息是附件、视屏、图片、语音
    elif msg['Type'] == "Attachment" or msg['Type'] == "Video" \
            or msg['Type'] == 'Picture' \
            or msg['Type'] == 'Recording':
            msg_content = msg['FileName'] # 内容就是他们的文件名
            msg['Text'](str(msg_content)) # 下载文件
            msg_print_content = msg_time_rec + ' ' + msg_from + ': 发送了' + msg['Type'] + '类型的文件，名称为: '+ msg_content
            #msg_content = '发送的' + msg['Type'] + '类型的文件，名称为: '+ msg_content
            print msg_print_content
    elif msg['Type'] == 'Card': # 如果消息是推荐的名片
        msg_print_content = msg['RecommendInfo']['NickName'] + '的名片' # 内容就是推荐人的昵称和性别
        if msg['RecommendInfo']['Sex'] == 1:
            msg_print_content += ' 性别为男'
        else: msg_print_content += ' 性别为女'
        msg_content = '推荐了' + msg_print_content
        msg_print_content = msg_time_rec + ' ' + msg_from + ': 推荐了 ' + msg_print_content
        print msg_print_content
    elif msg['Type'] == 'Map': # 如果消息为分享的位置信息
         x, y, location = re.search( "<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
         if location is None:
             msg_print_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__() # 内容为详细的地址
         else:
             msg_print_content = r"" + location
         msg_content = '分享了位置信息 【' + msg_print_content + '】'
         msg_print_content =  msg_time_rec + ' ' + msg_from + ': 分享了位置信息 【' + msg_print_content + '】'
         print msg_print_content
    elif msg['Type'] == 'Sharing': # 如果消息为分享的音乐或者文章，详细的内容为文章的标题或者是分享的名字
         msg_print_content = msg['Text']
         msg_share_url = msg['Url'] # 记录分享的url
         msg_content = '分享了【' + msg_print_content + '】'
         msg_print_content = msg_time_rec + ' ' + msg_from + ':【 ' + msg_print_content + '】'
         print msg_print_content
         print msg_share_url
    face_bug = msg_content
    ##将信息存储在字典中，每一个msg_id对应一条信息
    msg_information.update(
        {
            msg_id: {
                "msg_from": msg_from, "msg_time": msg_time, "msg_time_rec": msg_time_rec,
                "msg_type": msg["Type"],
                "msg_content": msg_content, "msg_share_url": msg_share_url
            }
        }
    )
    ##这个是用于监听是否有friend消息撤回
@itchat.msg_register(NOTE, isFriendChat=True, isGroupChat=True, isMpChat=True)
def information(msg):
        # 这里如果这里的msg['Content']中包含消息撤回和id，就执行下面的语句
        if '撤回了一条消息' in msg['Content']:
            old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1) # 在返回的content查找撤回的消息的id
            old_msg = msg_information.get(old_msg_id) # 得到消息
            msg_body = old_msg.get('msg_time_rec') + "\n" \
                       + "【" + old_msg.get('msg_from') + " 撤回了消息】：" + "\n" \
                       + r"" + old_msg.get('msg_content')

            if len(old_msg_id) < 11: # 如果发送的是表情包
                itchat.send_file(face_bug, toUserName='filehelper')
            else: # 发送撤回的提示给文件助手

                 # 如果是分享的文件被撤回了，那么就将分享的url加在msg_body中发送给文件助手
                 if old_msg['msg_type'] == "Card":
                     itchat.send_msg(msg_body, toUserName='filehelper')
                 if old_msg['msg_type'] == "Map":
                     itchat.send_msg(msg_body, toUserName='filehelper')
                 if old_msg['msg_type'] == "Sharing":
                     # 将撤回消息发送到文件助手
                     msg_body += "\n就是这个链接➣ " + old_msg.get('msg_share_url')
                     itchat.send_msg(msg_body, toUserName='filehelper')
                     # 有文件的话也要将文件发送回去
                 if old_msg["msg_type"] == "Picture" \
                             or old_msg["msg_type"] == "Recording" \
                             or old_msg["msg_type"] == "Video" \
                             or old_msg["msg_type"] == "Attachment":
                         file = '@fil@%s' % (old_msg['msg_content'])
                         send_msg = old_msg.get('msg_time_rec') + "\n"\
                            + "【" + old_msg.get('msg_from') + " 撤回了 】\n" \
                            + old_msg.get("msg_type") + " 消息："
                         itchat.send_msg(msg=send_msg, toUserName='filehelper')
                         itchat.send(msg=file, toUserName='filehelper')
                         #os.remove(old_msg['msg_content'])
                         # 删除字典旧消息
                         msg_information.pop(old_msg_id)
                 if old_msg["msg_type"] == "Text":
                     itchat.send_msg(msg=msg_body, toUserName='filehelper')
                     #os.remove(old_msg['msg_content'])
                     # 删除字典旧消息
                     msg_information.pop(old_msg_id)
            print msg_body
@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def handle_receive_msg(msg):
        global face_bug
        msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 接受消息的时间
        #  groupid = msg['FromUserName']
        #  chatroom = itchat.search_chatrooms(userName=groupid)
        msg_Actual_from = msg['ActualNickName']
        # msg_Actual_from = msg['User']
        #  msg_from = msg_Actual_from['Self']['NickName']
        msg_from = msg_Actual_from
        msg_time = msg['CreateTime'] # 信息发送的时间
        msg_id = msg['MsgId'] # 每条信息的id
        msg_content = None # 储存信息的内容
        msg_share_url = None # 储存分享的链接，比如分享的文章和音乐
        print msg['Type']
        #print msg['MsgId']
        msg_user = msg['User']
        if msg['Type'] == 'Text' or msg['Type'] == 'Friends': # 如果发送的消息是文本或者好友推荐
            print msg_time_rec + '  ' + msg_user.NickName
            msg_from_user = msg_from + ': ' +msg['Text']
            msg_content = msg['Text']
            print msg_from_user
        # 如果发送的消息是附件、视屏、图片、语音
        elif msg['Type'] == "Attachment" or msg['Type'] == "Video" \
                or msg['Type'] == 'Picture' \
                or msg['Type'] == 'Recording':
            msg_content = msg['FileName'] # 内容就是他们的文件名
            msg['Text'](str(msg_content)) # 下载文件
            print msg_time_rec + '  ' + msg_user.NickName
            msg_from_user = msg_from + ': 发送了' + msg['Type'] + '类型的文件，名称为: '+ msg_content
            print msg_from_user
        elif msg['Type'] == 'Card': # 如果消息是推荐的名片
            msg_print_content = msg['RecommendInfo']['NickName'] + '的名片' # 内容就是推荐人的昵称和性别
            if msg['RecommendInfo']['Sex'] == 1:
                msg_print_content += ' 性别为男'
            else:
                msg_print_content += ' 性别为女'
            print msg_time_rec + '  ' + msg_user.NickName
            msg_content = '推荐了 ' + msg_print_content
            msg_print_content = msg_from + ': 推荐了 '+ msg_print_content
            print msg_print_content
        elif msg['Type'] == 'Map': # 如果消息为分享的位置信息
            x, y, location = re.search(
                "<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
            if location is None:
                msg_print_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__() # 内容为详细的地址
            else:
                msg_print_content = r"" + location
            print msg_time_rec + '  ' + msg_user.NickName
            msg_print_content = msg_from + ': 分享了位置信息 【' + msg_print_content + '】'
            msg_content = '分享了位置信息【' + msg_print_content + '】'
            print msg_print_content
        elif msg['Type'] == 'Sharing': # 如果消息为分享的音乐或者文章，详细的内容为文章的标题或者是分享的名字
                msg_print_content = msg['Text']
                msg_share_url = msg['Url'] # 记录分享的url
                print msg_time_rec + '  ' + msg_user.NickName
                msg_content = '分享了【' + msg_print_content + '】\n' + msg_share_url
                msg_print_content = msg_from + ': 分享了 【' + msg_print_content + '】'
                print msg_print_content
                print msg_share_url
        face_bug = msg_content

        ##将信息存储在字典中，每一个msg_id对应一条信息
        msg_information.update(
            {
                msg_id: {
                    "msg_from": msg_from, "msg_time": msg_time, "msg_time_rec": msg_time_rec,
                    "msg_type": msg["Type"],
                    "msg_content": msg_content, "msg_share_url": msg_share_url
                }
            }
        )
    ##这个是用于监听是否有Group消息撤回
@itchat.msg_register(NOTE, isGroupChat=True, isMpChat=True)
def information(msg):
        # 这里如果这里的msg['Content']中包含消息撤回和id，就执行下面的语句
        if '撤回了一条消息' in msg['Content']:
            old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1) # 在返回的content查找撤回的消息的id
            old_msg = msg_information.get(old_msg_id) # 得到消息
            msg_user = msg['User']
            msg_body = "【" \
                       + old_msg.get('msg_time_rec') + " " + msg_user.NickName + " 撤回提醒】\n" \
                       + old_msg.get('msg_from') + " 撤回了 " + old_msg.get("msg_type") + " 消息：" + "\n"

            if len(old_msg_id) < 11: # 如果发送的是表情包
                itchat.send_file(face_bug, toUserName='filehelper')
            else: # 发送撤回的提示给文件助手

                # 如果是分享的文件被撤回了，那么就将分享的url加在msg_body中发送给文件助手
                if old_msg['msg_type'] == "Map":
                    msg_body += old_msg.get('msg_content')
                    itchat.send_msg(msg_body, toUserName='filehelper')
                if old_msg['msg_type'] == "Card":
                    msg_body += old_msg.get('msg_content')
                    itchat.send_msg(msg_body, toUserName='filehelper')
                if old_msg['msg_type'] == "Sharing":
                    msg_body += "就是这个链接➣ " + old_msg.get('msg_share_url')
                    itchat.send_msg(msg_body, toUserName='filehelper')
                    # 将撤回消息发送到文件助手

                # 有文件的话也要将文件发送回去
                if old_msg["msg_type"] == "Picture" \
                        or old_msg["msg_type"] == "Recording" \
                        or old_msg["msg_type"] == "Video" \
                        or old_msg["msg_type"] == "Attachment":
                    msg_body += old_msg['msg_content']
                    itchat.send_msg(msg=msg_body, toUserName='filehelper')
                    file = '@fil@%s' % (old_msg['msg_content'])
                    itchat.send(msg=file, toUserName='filehelper')
                    #os.remove(old_msg['msg_content'])
                if old_msg["msg_type"] == "Text":
                    msg_body +=  old_msg['msg_content']
                    itchat.send_msg(msg=msg_body, toUserName='filehelper')
                    #os.remove(old_msg['msg_content'])
                # 删除字典旧消息
                msg_information.pop(old_msg_id)
            print msg_body
# Main (enableCmdQr = True 时，将会生成二维码图片，如 =2 时二维码乱码的话 改为1 即可
itchat.auto_login(enableCmdQR=1, hotReload=True)
itchat.run()
