import json,sys,time,urllib.parse,urllib.request,re,os
UA={"User-Agent":"EducationalVideoDraft/1.0 (non-commercial research script)"}
def api(t):
    p={"action":"query","format":"json","titles":t,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1280}
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p)
    for a in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
        except Exception as e:
            print('retry',e,flush=True); time.sleep(60*(a+1))
out=json.load(open('photos/credits.json')) if os.path.exists('photos/credits.json') else {}
for name,t in json.load(open(sys.argv[1])).items():
    if name in out: continue
    d=api(t); pg=list(d["query"]["pages"].values())[0]; ii=pg["imageinfo"][0]; md=ii["extmetadata"]
    g=lambda k: re.sub("<[^>]+>","",md.get(k,{}).get("value","")).strip()
    url=ii.get("thumburl") or ii["url"]; ext=os.path.splitext(url.split("?")[0])[1].lower() or ".jpg"
    path=f"photos/{name}{ext}"
    ok=False
    for a in range(8):
        try:
            data=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=120).read()
            open(path,"wb").write(data); ok=len(data)>1000; break
        except Exception as e:
            print('img retry',e,flush=True); time.sleep(20*(a+1))
    if not ok:
        print('FAILED',name,flush=True); continue
    out[name]={"file":path,"title":t,"license":g("LicenseShortName"),"artist":g("Artist")[:80],"page":ii["descriptionurl"]}
    print(name,out[name]["license"],"|",out[name]["artist"][:40]); time.sleep(30); json.dump(out,open('photos/credits.json','w'),ensure_ascii=False,indent=1)
json.dump(out,open("photos/credits.json","w"),ensure_ascii=False,indent=1)
