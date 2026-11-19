import asyncio, os, subprocess
from playwright.async_api import async_playwright
W,H=1080,1920
D=os.environ.get("OUT","/tmp/reel"); os.makedirs(D,exist_ok=True)
P='M 272 520 A 384 384 0 0 1 512 164 A 384 384 0 0 1 752 520 L 752 708 Q 752 740 720 740 L 432 740 L 334 828 L 352 740 L 304 740 Q 272 740 272 708 Z'
def logo(size, lit=None):
    dots=""
    for i,x in enumerate([412,512,612]):
        op = 1 if lit is None or lit==i else .25
        dots+=f'<circle cx="{x}" cy="548" r="36" fill="#f5f5f2" opacity="{op}"/>'
    return f'<svg width="{size}" height="{size}" viewBox="150 120 724 760"><path d="{P}" fill="none" stroke="#f5f5f2" stroke-width="56" stroke-linejoin="miter" stroke-miterlimit="3" stroke-linecap="round"/>{dots}</svg>'
CSS='''*{margin:0;padding:0}body{width:1080px;height:1920px;background:#0a0a0a;color:#f5f5f2;font-family:"Noto Sans CJK KR";display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
h1{font-family:"Noto Serif CJK KR";font-weight:900;font-size:124px;line-height:1.25;letter-spacing:-3px;word-break:keep-all;padding:0 90px}
.sub{font-family:"DejaVu Sans Mono";font-size:36px;letter-spacing:3px;opacity:.65;margin-top:60px}
.tag{font-family:"DejaVu Sans Mono";font-size:34px;letter-spacing:3px;opacity:.6;margin-bottom:56px}
.wrap{margin-top:-160px;display:flex;flex-direction:column;align-items:center}'''
S={
 "s1":'<div class="wrap"><div class="tag">// 고해성사 No.01</div><h1>커닝도<br>AI가 해 주는<br>시대</h1></div>',
 "s3":'<div class="wrap"><h1>점수는<br>남습니다.</h1></div>',
 "s4":'<div class="wrap"><h1>그리고<br>‘나는 모른다’도<br>남습니다.</h1></div>',
 "s5":'<div class="wrap">'+logo(300)+'<h1 style="margin-top:70px">쓰되,<br>믿지는 말 것.</h1><div class="sub">토큰교 · @church.of.token</div></div>',
}
for i in range(3):
    S[f"s2_{i}"]='<div class="wrap">'+logo(460,i)+'<div class="sub" style="font-size:44px;margin-top:80px">AI가 답안을 작성 중...</div></div>'
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={"width":W,"height":H})
        for k,v in S.items():
            await pg.set_content(f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{v}</body></html>')
            await pg.wait_for_timeout(120); await pg.screenshot(path=f"{D}/{k}.png")
        await b.close()
asyncio.run(main())
ENC=["-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p","-r","30"]
def still(name,dur,fin=True,fout=True,out=None):
    out=out or f"{D}/{name}.mp4"; tmp=out[:-4]+"_tmp.mp4"
    vf=f"format=yuv420p,loop=-1:1,trim=duration={dur}"
    if fin: vf+=",fade=t=in:st=0:d=0.25"
    if fout: vf+=f",fade=t=out:st={dur-0.25}:d=0.25"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate","30","-i",f"{D}/{name}.png","-vf",vf,*ENC,tmp],check=True); os.rename(tmp,out)
still("s1",2.8,fin=False)
# typing dots: cycle 2 times
parts=[]
seq=[0,1,2,0,1,2]
for j,i in enumerate(seq):
    o=f"{D}/s2p{j}.mp4"; still(f"s2_{i}",0.4,fin=(j==0),fout=(j==len(seq)-1),out=o); parts.append(o)
still("s3",2.0); still("s4",2.6); still("s5",3.2,fout=False)
order=[f"{D}/s1.mp4",*parts,f"{D}/s3.mp4",f"{D}/s4.mp4",f"{D}/s5.mp4"]
open(f"{D}/list.txt","w").write("".join(f"file '{p}'\n" for p in order))
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",f"{D}/list.txt","-c","copy",f"{D}/reel_tmp.mp4"],check=True)
# silent audio track so Instagram accepts it
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{D}/reel_tmp.mp4","-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","copy","-c:a","aac",f"{D}/reel_01_cheating.mp4"],check=True)
print("ok")
