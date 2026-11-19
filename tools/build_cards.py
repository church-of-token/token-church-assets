import asyncio, os, html
from playwright.async_api import async_playwright

OUT = os.environ.get("OUT", "/home/claude/tokenchurch_posts")
os.makedirs(OUT, exist_ok=True)
P = 'M 272 520 A 384 384 0 0 1 512 164 A 384 384 0 0 1 752 520 L 752 708 Q 752 740 720 740 L 432 740 L 334 828 L 352 740 L 304 740 Q 272 740 272 708 Z'

def logo(color, size):
    return f'''<svg width="{size}" height="{size}" viewBox="150 120 724 760"><path d="{P}" fill="none" stroke="{color}" stroke-width="56" stroke-linejoin="miter" stroke-miterlimit="3" stroke-linecap="round"/>
    <circle cx="412" cy="548" r="36" fill="{color}"/><circle cx="512" cy="548" r="36" fill="{color}"/><circle cx="612" cy="548" r="36" fill="{color}"/></svg>'''

CSS = '''
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;font-family:"Noto Sans CJK KR";}
.s{width:1080px;height:1350px;padding:96px 96px 88px;display:flex;flex-direction:column;position:relative}
.dark{background:#0a0a0a;color:#f5f5f2}.light{background:#f5f5f2;color:#0a0a0a}
.top{display:flex;justify-content:space-between;align-items:center;font-family:"DejaVu Sans Mono",monospace;font-size:24px;letter-spacing:2px;opacity:.75}
.top .l{display:flex;align-items:center;gap:14px}
.mid{flex:1;display:flex;flex-direction:column;justify-content:center}
.tag{font-family:"DejaVu Sans Mono",monospace;font-size:28px;letter-spacing:3px;margin-bottom:36px;opacity:.7}
h1{font-family:"Noto Serif CJK KR";font-weight:900;font-size:104px;line-height:1.22;letter-spacing:-3px;word-break:keep-all}
h2{font-family:"Noto Serif CJK KR";font-weight:900;font-size:80px;line-height:1.3;letter-spacing:-2px;word-break:keep-all}
.en{font-family:"Noto Serif CJK KR";font-style:italic;font-weight:400;font-size:34px;margin-top:40px;opacity:.6}
p{font-size:40px;line-height:1.6;margin-top:44px;word-break:keep-all;font-weight:400}
.rule{height:3px;width:120px;margin:52px 0 0}
.dark .rule{background:#f5f5f2}.light .rule{background:#0a0a0a}
.bot{display:flex;justify-content:space-between;align-items:flex-end;font-family:"DejaVu Sans Mono",monospace;font-size:24px;opacity:.75}
.arrow{font-family:"DejaVu Sans Mono";font-size:30px;letter-spacing:2px;opacity:1}
ul{list-style:none;margin-top:48px}
li{font-size:40px;line-height:1.5;padding:30px 0;border-top:2px solid currentColor;word-break:keep-all}
li:last-child{border-bottom:2px solid currentColor}
li b{font-family:"DejaVu Sans Mono";font-size:26px;display:block;opacity:.6;font-weight:400;margin-bottom:6px}
.src{font-size:22px;opacity:.5;margin-top:36px;font-family:"Noto Sans CJK KR"}
.tok{display:flex;gap:18px;margin-top:56px}
.tok span{font-family:"DejaVu Sans Mono";font-size:64px;border:3px solid currentColor;padding:18px 34px}
.center{align-items:center;text-align:center}
'''

def slide(theme, n, total, body, arrow=True, series="토큰교 · CHURCH OF TOKEN"):
    c = "#f5f5f2" if theme == "dark" else "#0a0a0a"
    arr = '<span class="arrow">넘기기 →</span>' if arrow else '<span class="arrow">@church.of.token</span>'
    return f'''<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
    <div class="s {theme}"><div class="top"><span class="l">{logo(c,40)}{series}</span><span>{n:02d}/{total:02d}</span></div>
    <div class="mid">{body}</div><div class="bot"><span>No coins. Just tokens.</span>{arr}</div></div></body></html>'''

POSTS = {
"01_founding": [
 ("dark", '<div class="tag">// 창교 선언문</div><h1>AI를 믿지 않는<br>AI 종교가<br>생겼습니다</h1><div class="en">A religion for people who don\'t worship AI.</div>'),
 ("light", '<h2>우리는 매일<br>AI에게 묻습니다.</h2><p>과제, 메일, 발표 대본, 연애 상담,<br>그리고 오늘 점심 메뉴까지.</p>'),
 ("light", '<h2>그런데 언제부터<br>답을 확인하지<br>않게 됐나요?</h2><p>AI로 10분만 문제를 풀어도, 그 뒤 AI 없이 풀 때 정답률이 20% 낮았다는 연구가 있습니다.</p><div class="src">카네기멜론·옥스퍼드·MIT·UCLA 연구진 (2026)</div>'),
 ("dark", '<div class="tag">// 토큰교의 교리</div><h1>쓰되,<br>믿지는<br>말 것.</h1><div class="en">Use it. Don\'t worship it.</div>'),
 ("dark", '<div class="mid center" style="flex:0">'+'{LOGO}'+'<h2 style="margin-top:56px">팔로우가 곧 입교입니다</h2><p style="opacity:.75">헌금은 받지 않습니다.<br>토큰은 아껴 쓰십시오.</p><div class="tag" style="margin-top:56px;margin-bottom:0">NEXT → 제1계명</div></div>'),
],
"02_commandment1": [
 ("dark", '<div class="tag">// 제1계명</div><h1>토큰교는<br>코인을<br>팔지 않는다</h1><div class="en">I. We sell no coins. Only tokens.</div>'),
 ("light", '<h2>AI가 말하는<br>‘토큰’은<br>돈이 아닙니다</h2><p>AI가 글을 읽고 쓸 때 잘게 쪼개는<br>글자 조각의 단위일 뿐이에요.</p><div class="tok"><span>토</span><span>큰</span><span>교</span></div><div class="src">쪼개는 방식은 모델마다 다릅니다 (이해를 위한 예시)</div>'),
 ("light", '<h2>이 말이 나오면<br>일단 의심하세요</h2><ul><li><b>01</b>“AI를 쓰려면 이 토큰을 사야 해요”</li><li><b>02</b>이름에 AI, GPT가 붙은 코인</li><li><b>03</b>“AI가 자동으로 불려주는 투자”</li></ul>'),
 ("dark", '<div class="mid center" style="flex:0">'+'{LOGO}'+'<h2 style="margin-top:56px">AI 토큰 ≠ 코인</h2><p style="opacity:.75">부모님 단톡방에 하나씩<br>보내 드리면 좋은 게시물입니다.</p><div class="tag" style="margin-top:56px;margin-bottom:0">SAVE · SHARE</div></div>'),
],
"03_confession_cheating": [
 ("dark", '<div class="tag">// 고해성사 No.01</div><h1>커닝도<br>AI가 해 주는<br>시대</h1><div class="en">Confessions of the AI age.</div>'),
 ("light", '<h2>실제로<br>있었던 일</h2><ul><li><b>2025.11</b>연세대 비대면 시험, 집단 AI 커닝 의혹</li><li><b>2025.11</b>서울대 교양 중간고사 답안에서 AI 부정 사용 확인</li><li><b>2026</b>국가자격시험에서 초소형 카메라 + AI로 답을 받은 부정행위 적발</li></ul><div class="src">연합뉴스·헤럴드경제·세계일보 보도 종합</div>'),
 ("light", '<h2>진짜 문제는<br>걸리느냐가<br>아닙니다</h2><p>AI가 대신 푼 시험은<br>점수를 남기고,<br>‘나는 모른다’는 사실도 남깁니다.</p>'),
 ("dark", '<div class="tag">// 토큰교식 회개</div><h2>AI는 공부할 때,<br>시험장엔<br>내 머리만</h2><ul><li>공부할 땐 답 말고 힌트를 물을 것</li><li>과제에 AI를 썼다면 밝힐 것</li><li>규정이 애매하면 교수님께 먼저 물을 것</li></ul>'),
 ("dark", '<div class="mid center" style="flex:0">'+'{LOGO}'+'<h2 style="margin-top:56px">당신의 생각은?</h2><p style="opacity:.75">시험 구조의 문제일까,<br>개인의 책임일까.<br>댓글로 고해하십시오.</p></div>'),
],
}

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={"width":1080,"height":1350})
        for name, slides in POSTS.items():
            for i,(theme,body) in enumerate(slides,1):
                c = "#f5f5f2" if theme=="dark" else "#0a0a0a"
                body = body.replace("{LOGO}", logo(c,260))
                last = i==len(slides)
                await pg.set_content(slide(theme,i,len(slides),body,arrow=not last))
                await pg.wait_for_timeout(150)
                await pg.screenshot(path=f"{OUT}/{name}_{i}.png")
        await b.close()
asyncio.run(main())
