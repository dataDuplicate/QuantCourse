from urllib.request import *
from urllib.error import *
import re,json
import time
import os,sys
import http.client

header = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Accept-Encoding': 'deflate',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}
def urlWarpper(aid,bvid,cid):
    return f"https://video-direct-link.vercel.app/bili.mp4?aid={aid}&bvid={bvid}&cid={cid}"
    # url = f"https://api.bilibili.com/x/player/playurl?otype=json&fnver=0&fnval=3&player=3&qn=64&bvid={bvid}&cid={cid}&platform=html5&high_quality=1"

    # r = Request(url,headers=header)
    # d = urlopen(r).read().decode()



def getHighVideoURL(bvid:str):
    r = Request(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",headers=header)
    d = urlopen(r).read().decode()
    with open("context.json","w") as f:
        f.write(d)
    
    d = json.loads(d)["data"]
    pic = urlopen(d["pic"]).read()
    with open("pic.png","wb") as f:
        f.write(pic)
    
    aid = d["aid"]
    title = d["title"]
    if d["videos"]==1:
        return title,urlWarpper(aid,bvid,d["pages"][0]["cid"])
    else:
        def _():
            for i in d["pages"]:
                yield i["part"], urlWarpper(aid,bvid,i["cid"])
        return title, _()

def getVideoURL(bvid:str):
    global header
    def _(p=None):
        r = Request("https://m.bilibili.com/video/%s"%(bvid+(f"?p={p}" if p else"")),headers=header)
        a = urlopen(r)
        d=(a.read().decode())
        url = re.findall("readyVideoUrl: \'(.*?)\'",d)[0]
        return d, url
    d,url = _()
    name = re.findall("<h1.*?>(.*?)</h1>",d)[0]
    lis = re.findall("<li class=\"part-item.*?\"><span>(.*?)</span></li>",d)
    if len(lis)==0:
        return name,url
    def __():
        yield lis[0], url
        for i in range(2,len(lis)+1):
            yield lis[i-1], _(i)[1]
    return name, __()


def download_video(path,url,depth=0):
    global header
    if depth>5:
        raise Exception("Too match errors!!!")
    
    print(url)
    r = Request(url,headers=header)
    time.sleep(1)
    try:
        d = urlopen(r).read()
        with open(path,"wb") as f:
            f.write(d)
    except Exception :
        download_video(path,url,depth+1)
    except http.client.IncompleteRead :
        download_video(path,url,depth+1)
    

if __name__=="__main__":
    print(sys.argv)
    try:
        t=int(sys.argv[1])
        o=int(sys.argv[2])
    except:
        t,o = 1,1
    bvid = sys.argv[-1]

    name,a=getHighVideoURL(bvid)
    
    def aa(t,o,lis):
        l = len(lis)
        s = (l//t) + (0 if l%t==0 else 1)
        return lis[s*(o-1):(None if s*o>len(lis)-1 else s*o)]

    name="main"
    if type(a)==str:
        download_video(f"./{name}.mp4", a)
    else:
        if not os.path.exists("./"+name):
            os.makedirs("./"+name)
        for n,url in aa(t,o,list(a)):
            print(n)
            download_video(f"./{name}/{n}.mp4",url)
        
    