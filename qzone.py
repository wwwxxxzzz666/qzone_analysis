# -*- coding: utf-8 -*-

if __name__=='__main__':
    print('Loaing models&packages...',end='')
from random import random
from selenium import webdriver
import time
import datetime
import json
import requests
import urllib
import re
import threadpool
import codecs
import jiagu
import jieba
import jieba.analyse
import snownlp
import wordcloud
import numpy as np
from PIL import Image
import os
if __name__=='__main__':
    print('Done!')
#以上为加载的包和库

if __name__=='__main__':
    print('Initializing...',end='')
if not os.path.exists('setting.ini'):
    with open('setting.ini','w') as f:
        f.write('qq_number\n')
        f.write('password\n')
        f.write('300\n')
        f.write('results\n')
        f.write('10\n')
        f.write('True\n')
        f.write('No\n')
#若没有配置文件则初始化生成一个
with open('setting.ini','r') as f:
    tt=[]
    for line in f:
        tt.append(line)
try:
    qq_number,password,maxquery,path,poolsize,ifwordc,ifdebug=tt[0].strip(),tt[1].strip(),int(tt[2]),tt[3].strip(),int(tt[4]),tt[5].strip(),tt[6].strip()
except:
    if __name__=='__main__':
        print('The setting file has errors!Please check,or just delete it and restart this program.')
    else:
        raise Exception
    exit()
#从文件中获取字符串时注意去除末尾的换行符
if maxquery!=0 and maxquery<20:
    #若给定数字过小则将其赋值为20
    maxquery=20

if poolsize<1:
    #若线程池大小非法则改为1
    poolsize=1

if ifdebug=='Yes':
#是否开启debug
    debug=True
else:
    debug=False

friends_uin=[]
friends_name=[]

try:
    img=Image.open('mask.jpg')
    mask=np.array(img)
except:
    mask=None
#制作词云图所用的蒙版图片

pc=0
#已处理好友数，用于线程池处理计数

if __name__=='__main__':
    print('Done!')
#以上为初始化部分


def get_cookies():
    """模拟登录QQ空间以获取cookies"""
    print('Auto-login in...')
    login_url='https://i.qq.com/'
    driver=webdriver.Edge('msedgedriver.exe')
    driver.get(login_url)
    #进入登陆的iframe
    driver.switch_to.frame('login_frame')
    driver.find_element_by_xpath('//*[@id="switcher_plogin"]').click()
    time.sleep(0.7+random())
    driver.find_element_by_xpath('//*[@id="u"]').send_keys(qq_number)
    driver.find_element_by_xpath('//*[@id="p"]').send_keys(password)
    time.sleep(0.7+random())
    url=driver.current_url
    driver.find_element_by_xpath('//*[@id="login_button"]').click()
    while url==driver.current_url:
        #等待页面跳转
        time.sleep(0.7+random())
    #以上为模拟输入用户名和密码并点击登录的过程
    driver.switch_to.default_content()
    #注意由刚刚登陆时所在的iframe退回整个页面
    time.sleep(1)
    print('Login success!')
    print('Getiing the cookies...')
    cookie_list=driver.get_cookies()
    cookie_dict={}
    for cookie in cookie_list:
        if 'name' in cookie and 'value' in cookie:
            cookie_dict[cookie['name']]=cookie['value']
    try:
        with open('cookies.txt','w') as f:
            json.dump(cookie_dict,f)
    except FileExistsError:
        print('File already exists!')
    #以上为获取cookies并写入文件的过程
    driver.quit()
    print('##############################')
    print('##############################')
    print('##############################')
    print('Done!')
    print('Press Enter to continue...')
    input()
    

def get_g_tk():
    """计算得到加密参数g_tk"""
    p_skey=cookie_dict['p_skey']
    h=5381
    for i in p_skey:
        h+=(h<<5)+ord(i)
        g_tk=h&2147483647
    if debug:
        print('g_tk:',g_tk)
    return g_tk
    
def get_friends_uin():
    yurl='https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi?'
    data={
            'uin':qq_number,
            'do':1,
            'g_tk':g_tk
            }
    url=yurl+urllib.parse.urlencode(data)
    #以上生成访问链接地址
    try:
        res=requests.get(url,headers=headers,cookies=cookie_dict)
    except:
        print('Connection error!')
        return False,False

    if debug:
        #debug输出
        print(res.text)
    with codecs.open('friendsdebug.txt','w','utf-8') as f:
        f.write(res.text)
    r=res.text.split('k(')[1].split(');')[0]

    if debug:
        print('##########################################')
        print(r)

    if 'error' in json.loads(r):
        #若含有error说明未登录，或者cookies已失效
        return None,None

    friends_list=json.loads(r)['data']['items_list']

    friends_uin=[]
    friends_name=[]
    for f in friends_list:
        friends_uin.append(f['uin'])
        friends_name.append(f['name'])
    #返回好友uin以及昵称的列表
    return friends_uin,friends_name
    
def get_dynamics(uin,dis=False):
    """获取好友的说说动态内容"""
    if dis and debug:
        print(uin)
    yurl='https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
    pos=0
    #好友说说内容的记号位置
    contents=[]
    nickname=None
    with codecs.open(path+'/'+str(uin)+'contents.txt','w','utf-8') as f:
        f.write('Fetching time:'+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+'\n')
    #创建好友说说内容文件，为写入做准备
    while True:
        if maxquery!=0 and pos>=maxquery:
            #若给定的maxquery为0则全部抓取
            return contents,nickname
        #若超过最大请求数量就结束抓取
        data={
                'uin':uin,
                'pos':pos,
                'num':20,
                'replynum':100,
                'callback':'_preloadCallback',
                'code_version':1,
                'format':'jsonp',
                'need_private_comment':1,
                'g_tk':g_tk
                }
        url=yurl+urllib.parse.urlencode(data)
        #生成链接
        try:
            res=requests.get(url,headers=headers,cookies=cookie_dict)
        except:
            print('Connection error!')
            return None,None

        r = re.findall('\((.*)\)',res.text)[0]
        #使用正则表达式截取括号内内容

        if debug:
        #debug输出
            with codecs.open(str(uin)+'debug.txt','a','utf-8') as f:
                f.write(r)

        dynamic=json.loads(r)
        pos+=20
        if 'msglist' in dynamic:
            msglist=dynamic['msglist']
            if msglist:
                for m in msglist:
                    name=m['name']
                    if nickname==None:
                        nickname=name
                    content=m['content']
                    created_time=m['created_time']
                    standard_time=time.localtime(created_time)
                    standard_time=time.strftime("%Y-%m-%d %H:%M:%S",standard_time)
                    #获取说说的内容、作者、时间信息
                    if dis:
                        print(standard_time,',',name,':',content)
                    with codecs.open(path+'/'+str(uin)+'contents.txt','a','utf-8') as f:
                        f.write(str(standard_time)+','+name+':'+content+'\n')
                    contents.append(content)
            else:
                #若msglist为空则说明说说已抓取完毕
                if dis:
                    print('There is no more contents.')
                return contents,nickname
        else:
            #若没有msglist说明该好友空间无访问权限
            if dis:
                print('This friend\'s space is not accessible.')
            with codecs.open(path+'/'+str(uin)+'contents.txt','a','utf-8') as f:
                f.write('This friend\'s space is not accessible.\n')
            break
    return contents,nickname

def preprocess(text):
    """使用正则表达式对说说内容中的表情等格式进行过滤"""
    return re.sub('\[em\][a-z0-9]*\[/em\]','',text).replace('\n',' ').strip()

def analysis(uin,name,contents,dis=False):
    """分析说说内容"""
    with codecs.open(path+'/'+str(uin)+'analysis.txt','w','utf-8') as f:
        f.write('Analysis time:'+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+'\n')
        f.write('uin:'+str(uin)+'; name:'+name+'\n')
    if len(contents)==0:
        #若无内容则无需分析
        return
    ords=preprocess(' '.join(contents))
    #获取原文合并字符串
    if dis and debug:
        print(ords)
    with codecs.open(path+'/'+str(uin)+'analysis.txt','a','utf-8') as f:
        keywords=[]
        #分析关键词（jiagu）
        for i in contents:
            s=preprocess(i)
            if len(s)==0:
                continue
            keyword=jiagu.keywords(s)
            for t in keyword:
                if len(t)==0:
                    break
                keywords.append(t)
        if dis:
            print('The keywords of ',name,'\'s contents are:',end='')
        f.write('The keywords of '+name+'\'s contents are:')

        for t in keywords:
            if dis:
                print(t,',',end='')
            f.write(t+',')
        if dis:
            print()
            print('############################')
        f.write('\n')
        f.write('############################\n')

        keywords=[]
        #分析关键词2（jieba）
        for i in contents:
            s=preprocess(i)
            if len(s)==0:
                continue
            keyword=jieba.analyse.textrank(s)
            for t in keyword:
                if len(t)==0:
                    break
                keywords.append(t)
        if dis:
            print('The keywords2 of ',name,'\'s contents are:',end='')
        f.write('The keywords2 of '+name+'\'s contents are:')

        for t in keywords:
            if dis:
                print(t,',',end='')
            f.write(t+',')
        if dis:
            print()
            print('############################')
        f.write('\n')
        f.write('############################\n')

        if len(ords)>20:
            sum=snownlp.SnowNLP(ords).summary()
        else:
            #若内容长度过短则不生成摘要
            sum=['None']
        #提取摘要（snownlp）
        if dis:
            print('The summary of ',name,'\'s contents are:',end='')
        f.write('The summary of '+name+'\'s contents are:')
        for t in sum:
            if len(t)==0:
                break
            if dis:
                print(t,';',end='')
            f.write(t+';')
        if dis:
            print()
            print('############################')
        f.write('\n')
        f.write('############################\n')

        pos=neg=0
        level=0
        #情感分析（jiagu）（注意：该结果可信度较低，尤其对于长文本而言）
        for i in contents:
            s=preprocess(i)
            if len(s)==0:
                continue
            sense=jiagu.sentiment(s)
            if sense[0]=='positive':
                pos+=1
                level+=sense[1]
            else:
                neg+=1
                level+=1-sense[1]
        level/=(pos+neg)
        if dis:
            print('The ratio of the number of positive and negative sayings is {:d}:{:d}'.format(pos,neg))
            print('The emotional level of ',name,'\'s contents are:',level)
            print('############################')
        f.write('The ratio of the number of positive and negative sayings is {:d}:{:d}'.format(pos,neg)+'\n')
        f.write('The emotional level of '+name+'\'s contents are:'+str(level)+'\n')
        f.write('############################\n')

        pos=neg=0
        level=0
        #情感分析2（snownlp）（该结果可信度较高）
        for i in contents:
            s=preprocess(i)
            if len(s)==0:
                continue
            sense=snownlp.SnowNLP(s).sentiments
            #返回值越接近1越积极，越接近0越消极
            if sense>=0.5:
                pos+=1
            else:
                neg+=1
            level+=sense
        level/=(pos+neg)
        if dis:
            print('Here is the sentiments analysis of SnowNLP.')
            print('The ratio of the number of positive and negative sayings is {:d}:{:d}'.format(pos,neg))
            print('The emotional level of ',name,'\'s contents are:',level)
            print('############################')
        f.write('Here is the sentiments analysis of SnowNLP.'+'\n')
        f.write('The ratio of the number of positive and negative sayings is {:d}:{:d}'.format(pos,neg)+'\n')
        f.write('The emotional level of '+name+'\'s contents are:'+str(level)+'\n')
        f.write('############################\n')

        f.write('\n')
        f.write('Below is a detailed analysis\n\n')
        #逐说说进行分析，并将结果写入文件
        for i in range(len(contents)):
            s=preprocess(contents[i])
            if len(s)==0:
                #若该说说内容为空则跳过
                continue
            f.write(str(i)+':'+s+'\n')
            #关键词（jiagu）
            f.write('keywords:')
            keyword=jiagu.keywords(s)
            for t in keyword:
                if len(t)==0:
                    break
                f.write(t+' ')
            f.write('\n')

            #关键词2（jieba）
            f.write('keywords2:')
            keyword=jieba.analyse.textrank(s)
            for t in keyword:
                if len(t)==0:
                    break
                f.write(t+' ')
            f.write('\n')

            #摘要（snownlp）
            if len(s)>20:
                sum=snownlp.SnowNLP(s).summary()
            else:
                sum=['None']
            f.write('Summary:')
            for t in sum:
                if len(t)==0:
                    break
                f.write(t+';')
            f.write('\n')

            #情感分析（jiagu）
            f.write('Emotion:')
            f.write(jiagu.sentiment(s)[0]+'\n')
            f.write('Emotion level:')
            f.write(str(jiagu.sentiment(s)[1])+'\n')

            #情感分析2（snownlp）（该结果可信度高，尤其对于长文本而言）
            f.write('Emotion2:')
            t=snownlp.SnowNLP(s).sentiments
            if t>=0.5:
                f.write('positive\n')
            else:
                f.write('negative\n')
            f.write('Emotion2 level:')
            if t>=0.5:
                f.write(str(t)+'\n')
            else:
                f.write(str(1-t)+'\n')

            f.write('----------------------------------------\n')
            #分割线

    if ifwordc=='True':
        #判断是否生成云词图
        ls=jieba.lcut(ords)
        #生成分词列表
        cops=' '.join(ls)
        stopwords=['的','不','是','了','我','你','她','他','它','在','也','和','就','都','这','来','过','有','让','之','上','下','才','给','能','很','前','叫','还','中','前','后','没','要','为','将','啦','吧','吗','对','再','里','于','此','用','到','与','们','每','没','得','个','可','好','把','如','时','带','挺','已','该','真','张','乃','么','呢','即','及','以','名','当','凭','总','并','事','其','矣',\
        '去','更','只','第','一','而','但','被','更','比','又','会','倒','说','生','从','着','就是','还是','其实','以来','那么','这么','还有','一个','一种','一张','一只','一支','一次','好好','对于','uin','nick','who','em','com','http','https','qq','qzone','QQ','url','cn','show','bid','h5','index','constellation','wv']
        #去掉不需要显示的词（即停用词）
        wc=wordcloud.WordCloud(font_path="msyh.ttc",
                                mask=mask,
                                width=1920,
                                height=1080,
                                background_color='white',
                                max_words=200,stopwords=stopwords)
        wc.generate(cops)
        #生成词云图片
        wc.to_file(path+'/'+str(uin)+".png")
        #保存词云图片
        if dis:
            print('Image generation completed!')
            print('Please check the image file')

    if dis:
        print('The analysis is over.')
    
def threadprocess(x):
    """多线程单元处理"""
    contents,tname=get_dynamics(friends_uin[x])
    if contents==None:
        #若返回None则说明网络连接出现错误
        print('Connection Error!Please check your network.')
    else:
        analysis(friends_uin[x],friends_name[x],contents)
    global pc
    pc+=1
    #线程池处理完成计数
    print(friends_uin[x],':',friends_name[x],' Done!(',pc,'/',len(friends_uin),')')

def main():
    global pc,headers,cookie_dict,g_tk,friends_uin,friends_name
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64'}

    if input('Do you want to login at first?(Y/N or any other key):').lower()=='y':
        get_cookies()

    print('Loading cookies...')
    try:
        with open('cookies.txt','r') as f:
            cookie_dict=json.load(f)
    except FileNotFoundError:
        print('You havn\'t logged in the QQ!Please login first.')
        time.sleep(0.5)
        get_cookies()
        with open('cookies.txt','r') as f:
            cookie_dict=json.load(f)
            print('Done!')
    else:
        print('Done!')

    if not os.path.exists(path):
        #若处理结果写入文件夹不存在就创建
        os.makedirs(path)

    while True:
        time.sleep(0.5)
        print('Fetching the friends lists...')
        try:
            g_tk=get_g_tk()
        except KeyError:
            print('There is something error with your login.')
            print('Please restart the program and login again.')
            print('Abort.')
            exit()
        friends_uin,friends_name=get_friends_uin()
        print('Done!')

        if friends_uin is False:
            print('Connection Error!Please check your network!')
            print('Please restart the program.')
            print('Abort.')
            exit()

        if friends_uin is None:
            print('You havn\'t logged in the QQ,or login has expired.Please login first.')
            time.sleep(0.5)
            get_cookies()
            with open('cookies.txt','r') as f:
                cookie_dict=json.load(f)
                print('Done!')
        else:
            break
    
    print('Your QQ friends list:')
    for i in range(len(friends_uin)):
        print('{:d}.'.format(i),friends_uin[i],' ',friends_name[i])
    if input('Do you want to save your friends list to a file?(Y/N or any other key):').lower()=='y':
        print('Saving...',end='')
        with codecs.open(str(qq_number)+'_friendslist.txt','w','utf-8') as f:
            for i in range(len(friends_uin)):
                f.write('{:d}.'.format(i)+str(friends_uin[i])+' '+friends_name[i]+'\n')
        print('Done!')

    while True:
        x=-100
        while True:
            try:
                print('Enter \'c\' to enter the QQ number of the space you want to view directly(Out of this list is also possible.)')
                print('Enter \'q\' to exit the program.')
                k=input('Or just input the index number of the friend you want to view(0-{:d}) or -1 to process all friends:'.format(len(friends_uin)-1))
                if k.lower()=='c':
                    while True:
                        try:
                            target=int(input('Please input the QQ number:'))
                        except ValueError:
                            print('Your input is invalid!Please check.')
                        else:
                            break
                    contents,tname=get_dynamics(str(target),True)
                    if contents==None:
                        #若返回None则说明网络连接出现错误
                        print('Connection Error!Please check your network.')
                    elif tname==None:
                        print('This uin\'s space is invalid.')
                    else:
                        analysis(str(target),tname,contents,True)
                elif k.lower()=='q':
                    print('Program ended.')
                    exit()
                else:
                    x=int(k)
                    if (x>len(friends_uin)-1) or (x<-1):
                        #若输入超出说明范围就引发一个特定的错误
                        raise IndexError
            except ValueError:
                print('Your input is not a valid integer,please input again!')
            except IndexError:
                print('Your input is out of valid range,please input again!')
            else:
                break
        if x==-1:
            pc=0
            #已处理好友数
            print('Starting...')
            print('This process would take a long time.Please wait and do not close this window.')
            pool_size=poolsize
            #设置线程池容量
            pool=threadpool.ThreadPool(pool_size)
            #创建线程池
            reqs=threadpool.makeRequests(threadprocess,range(len(friends_uin)))
            #创建多线程任务队列
            [pool.putRequest(req) for req in reqs]
            #将多线程任务队列投入线程池中运行
            pool.wait()
            #pool.poll
            #等待线程池运行完毕
            pool.dismissWorkers(poolsize,do_join=True)
            print('Done!')
        elif x!=-100:
            contents,tname=get_dynamics(friends_uin[x],True)
            if contents==None:
                #若返回None则说明网络连接出现错误
                print('Connection Error!Please check your network.')
            else:
                analysis(friends_uin[x],friends_name[x],contents,True)
        print('Your QQ friends list:')
        for i in range(len(friends_uin)):
            print('{:d}.'.format(i),friends_uin[i],' ',friends_name[i])

if __name__=='__main__':
    main()