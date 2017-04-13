#coding:utf8
from example import userProcess
import datetime
import re
import jieba
from collections import Counter
from configparser import ConfigParser
from os import listdir
from os import path
import time
#############
userInstance=dict()
file_dir="history"
qq_group_history =dict()



def validate(talk_time,start_date):
    try:
        # the timeis 2017-04-13 00:00:00 2017-04-12 00:00:00
        # the d_start_date is big
        d_talk_time=datetime.datetime.strptime(talk_time, '%Y-%m-%d')
        d_start_date=datetime.datetime.strptime(start_date, '%Y-%m-%d')
        if d_start_date>=d_talk_time:
            return True
        else:
            return False
    except ValueError:
        return False

        # raise ValueError("Incorrect data format, should be YYYY-MM-DD")


        # if i>100:
        #     break
def processData(start_date,msg_counts,key_words):
    default_key_words_contents=[]
    wordArray=[]
    speaArraymin=[] #'2016-08-04 11:11
    speaArraymins=[]#'2016-08-04 11:1
    for k,v in userInstance.items():
        speak_content = [x[1] for x in v.speak_history]
        speak_time_min    = [x[0][:16] for x in v.speak_history]#'2016-08-04 11:11:52'
        speak_time_mins    = [x[0][:15] for x in v.speak_history]#'2016-08-04 11:11:52'
        speaArraymin+=speak_time_min
        speaArraymins+=speak_time_mins
        # print('the speak time is',speak_time)
        for i in speak_content:
            word_list = jieba.cut(i, cut_all=False)  
            for word in word_list:  
                #过滤掉短词，只有一个长度的词  
                if(len(word)>1):  
                    wordArray.append(word)    
                if word in key_words:
                    default_key_words_contents.append({
                        v.name:speak_content
                        })
    c_time=Counter(speaArraymin)
    c_words=Counter(wordArray)
    most_common_time=c_time.most_common(msg_counts)
    most_common_key_words=c_words.most_common(msg_counts)
    return most_common_time,most_common_key_words,default_key_words_contents
    # print('\n讨论最激烈的{}个时段：{}'.format(msg_counts,most_common_time))
    # print('\n出现频率最多的{}个关键词：{}'.format(msg_counts,most_common_key_words))
    # print(key_words_contents)

def processFile(content,start_date,filename):
    group_history=[]
    for i in range(len(content)):
        headers=content[i]
        if len(headers)<10 or (not validate(headers[:10],start_date)):
            continue
        name=''
        qq=''
        mail=''
        talk_time=headers[:19]
        user_info = headers[20:]
        f =lambda x: x[-1] if x else None
        if user_info.find('>')!=-1: #Damon_侯帅<damonhowe@qq.com>
            names=re.findall('(.*?)<',user_info)
            mails=re.findall('<(.*?)>\r',user_info)
            name =f(names)
            mail =f(mails)
        elif user_info.find(')')!=-1:#Damon桑(929819892)
            names=re.findall('(.*?)\(',user_info)
            qqs=re.findall('\((.*)\)\r',user_info)
            name=f(names)
            qq=f(qqs)
        userID=qq if qq else mail
        user=User(name,userID)
        speak_history=[talk_time,content[i+1]]
        user.speak_history=speak_history
        group_history.append(content[i])
        group_history.append(content[i+1])
    qq_group_history[filename]=group_history


def singleton(cls):
    def _warpper(*args,**kwargs):
        userID=args[1]
        if not userID in userInstance:
            userInstance[userID]=cls(*args,**kwargs)
        return  userInstance.get(userID,None)
    return _warpper

@singleton
class User(object):
    """docstring for User"""
    def __init__(self, name,userID):
        self.name = name
        self.userID=userID
        self.content =[]

    @property
    def speak_history(self): 
        return self.content

    @speak_history.setter
    def speak_history(self,content=None):
        if content:
            self.content.append(content)        

def recordPeak(most_common_time,most_common_key_words):
    #[('2016-12-22 17:51', 5), ('2016-12-29 16:00', 4), ('2016-08-30 13:01', 3), ('2017-02-24 17:39', 3), ('2017-01-04 16:04', 3), ('2017-01-16 17:37', 3), ('2016-08-30 13:19', 3), ('2016-08-04 11:11', 2), ('2016-09-02 15:19', 2), ('2016-08-04 18:38', 2)]
    qq_group_time_record=[]
    peak_time_history=dict()
    time_list=[x[0] for x in most_common_time]
    key_word_list=[x[0] for x in most_common_key_words]
    #高峰时刻聊天记录 {"time":'history'}
    for qq_group,history in qq_group_history.items():
        for i in range(0,len(history),2):
            speak_time=history[i][:19]
            words=history[i+1] if speak_time[:16] in time_list else ''
            if not words:
                continue
            if not speak_time in peak_time_history:
                peak_time_history[speak_time]=[]
            history=peak_time_history[speak_time]
            history.append(words)
            peak_time_history[speak_time]=history

    #高频词汇聊天记录
    for k,v in userInstance.items():
        speak_content = [x[1] for x in v.speak_history]
        for i in speak_content:
            word_list = jieba.cut(i, cut_all=False)  
            for word in word_list:  
                #过滤掉短词，只有一个长度的词  
                # if(len(word)>1):  
                #     wordArray.append(word)    
                if word in key_word_list:
                    key_words_contents.append({
                        v.name:speak_content
                        })
    with open(msg_counts+'.txt','w') as f:
        pass    
                # speak_words=history[i+1]
            
            # if i>1000:
                # print('the i is ',history[i],i)
                # print('the content is is ',history[i+1],i)

    # for k,v in userInstance.items():
        # speak_content = [x[1] for x in v.speak_history if f(x)]

    # with open(msg_counts+'.txt','w') as f:
    #     pass
def main():
    cp         = ConfigParser()
    cp.read('qq_history.conf',encoding="utf8")
    start_date = cp.get('Basic','start_date')
    if start_date=="2017-01-01" :
        local_t=time.strftime("%Y-%m-%d", time.localtime())
        start_date=local_t
    msg_counts = cp.get('Basic','msg_counts')
    key_words  = cp.get('Basic','key_words')
    msg_counts = int(msg_counts)
    key_words  = eval(key_words)
    only_files = [f for f in listdir(file_dir) if path.isfile(path.join(file_dir,f))]
    # print('the only files is',time_start)
    # print('the only files is',time_end)
    # print('the only files is',msg_counts)
    # print('the only files is',key_words,type(eval(key_words)))
    # print('the only files is',only_files)
    for filename in only_files:
        with open("history/"+filename,'rb') as f:
            # print(help(f))
            n=f.readlines()
            content=[x.decode("utf8") for x in n]
            processFile(content,start_date,filename)
    most_common_time,most_common_key_words,default_key_words_contents=processData(start_date,msg_counts,key_words)
    recordPeak(most_common_time,most_common_key_words)
    print('\n讨论最激烈的{}个时段：{},相应聊天内容已经保存在对应时间文件中'.format(msg_counts,most_common_time))
    print('\n出现频率最多的{}个关键词：{},相应聊天内容已经保存在对应时间文件中'.format(msg_counts,most_common_key_words))
    print('\n预设关键词被提及{},相应聊天内容已经保存在对应时间文件中'.format(default_key_words_contents))
    # print('\n发言最多的{}QQ号码,相应聊天内容已经保存在对应时间文件中'.format())
        # for i in range(len(content)):
        #     print('the content is',content[i])
        #     if i>50:
        #         break

if __name__ == '__main__':
    main()