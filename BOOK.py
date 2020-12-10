



import re
from bs4 import BeautifulSoup
import requests
import sqlite3

def main():
    tag = str(input("请输入图书类型："))
    baseurl = "https://book.douban.com/tag/+"+tag+"?start="
    booklist = getdata(baseurl)
    # print(booklist)
    dbname = tag+".db"
    savedb(booklist,dbname,tag)
    # init_db(dbname)


findlink = re.compile(r'<a class="nbg" href="(.*?)"',re.S) #图书链接

findimg = re.compile(r'<img class="" src="(.*?)"',re.S)  #图片链接

findtitle = re.compile(r'<a.*? title="(.*?)"')  #图书名称

findtitle2 = re.compile(r'style="font-size:12px;">(.*?)</span>')   #副名称

findpub = re.compile(r'<div class="pub">(.*?)</div>',re.S)   #图书信息

findpl = re.compile(r'<span class="pl">(.*?)</span>',re.S)  #评价人数

findinq = re.compile(r'<p>(.*?)</p>',re.S)   #图书概况

findbuy = re.compile(r'<a href="(.*?)"',re.S)   #购买链接


def getdata(url):
    n = 0
    booklist =[]
    for i in range(0,50):
        askurl = url+str(i*20)+"&type=T"

        html = Url(askurl)

        soup = BeautifulSoup(html,"html.parser")

        for subject_item in soup.find_all('li',class_ = "subject-item"):
            data = []
            subject_item = str(subject_item)

            link = re.findall(findlink,subject_item)[0]
            # print(link)
            data.append(link) #添加图书链接

            imglink = re.findall(findimg,subject_item)[0]
            # print(imglink)
            data.append(imglink) #添加图片链接

            title2 = re.findall(findtitle2,subject_item)  #添加名称
            if len(title2) == 0:
                title = re.findall(findtitle,subject_item)[0]
                data.append(title)
            else:
                title = re.findall(findtitle,subject_item)[0]
                title2 = re.findall(findtitle2,subject_item)[0]
                Title = title+title2
                data.append(Title)

            pub = re.findall(findpub,subject_item)[0]
            data.append(pub.strip())

               #添加信息

            pl = re.findall(findpl,subject_item)[0]
            pl1 = pl.split("(")[1]
            data.append((pl1.strip())[:-4])   #添加评价人数


            if len(re.findall(findinq,subject_item))==0:
                data.append(" ")
                # print(" ")
            else:
                inq = re.findall(findinq,subject_item)[0]
                data.append(inq.strip())   #添加概况


            if len(re.findall(findbuy,subject_item))==3:
                buy = re.findall(findbuy, subject_item)[2]

                data.append(buy)
            elif len(re.findall(findbuy,subject_item))==2:
                buy = re.findall(findbuy, subject_item)[1]

                if str(buy) == re.findall(findbuy, subject_item)[0]+"?channel=subject_list&amp;platform=web":
                    data.append(" ")
                else:

                    data.append(buy)
            else:
                # print("无购买链接")
                data.append(" ")#添加购买链接

            booklist.append(data)

    return booklist



def Url(askurl):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }
    request = requests.get(askurl,params=None,headers = header)
    request.encoding = "UTF-8"
    html = ""
    try:
        html = request.text
    except requests.exceptions as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html
def savedb(booklist,dbname,tag):
    temp = 0
    init_db(dbname)
    conn = sqlite3.connect(dbname)
    sql = '''
        insert into BOOK_OF_DOUBAN(BookLink, BookImgLink,BookTitle, BookInfo,BookPl,BookInq,BookBuyLink)
        values (?,?,?,?,?,?,?)
    '''
    cursor = conn.cursor()
    for book in booklist:
        cursor.execute(sql,book)
        conn.commit()
        print(f"《{book[2]}》已保存到数据库")
        temp+=1
    print(f"共保存{temp}本{tag}。")
    conn.close()

def init_db(dbname):
    sql = '''
        create table BOOK_OF_DOUBAN
        (
            ID integer primary key autoincrement,
            BookLink text not null,
            BookImgLink text not null,
            BookTitle varchar not null,
            BookInfo varchar not null,
            BookPl numeric not null,
            BookInq varchar not null,
            BookBuyLink text
        );
    '''
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()