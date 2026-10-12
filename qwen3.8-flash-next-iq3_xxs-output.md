下面是完整的单文件 HTML（纯 SVG + CSS + 原生 JS，无任何外部依赖）。我把它设计成一段「黄昏湖畔通勤」的小动画：轮辐、曲柄、双腿用真实的二连杆 IK 解算，所以踩踏是真正咬合在脚踏上的；背景做了多层视差、路面虚线、链节滚动、围巾波动、喉囊抖动、眨眼、车铃涟漪等细节。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>鹈鹕自行车 · Pelican Vélocipède</title>
<style>
  :root{
    --bg:#070b11; --ink:#f2ede3; --muted:#9fb0bf; --accent:#f0a04b;
    --line:#22303c;
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0; padding:26px 18px;
    background:radial-gradient(1200px 760px at 50% -12%, #17242f, #05080c 72%);
    color:var(--ink);
    font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,-apple-system,"Segoe UI",sans-serif;
    display:flex; align-items:center; justify-content:center;
  }
  .wrap{width:min(1060px,100%)}
  .card{
    background:linear-gradient(#131d27,#0b131b);
    border:1px solid var(--line); border-radius:20px; overflow:hidden;
    box-shadow:0 34px 90px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.06);
  }
  .stage{position:relative; line-height:0}
  svg{display:block; width:100%; height:auto}
  .title{position:absolute; left:24px; top:18px; line-height:1.15; pointer-events:none;
         text-shadow:0 3px 16px rgba(0,0,0,.65)}
  .title h1{margin:0; font-size:clamp(20px,3.1vw,34px); letter-spacing:.08em; font-weight:700}
  .title p{margin:5px 0 0; font-size:12px; letter-spacing:.22em; text-transform:uppercase;
           color:#ffd9a8; opacity:.85}
  .bar{display:flex; flex-wrap:wrap; gap:10px; align-items:center;
       padding:14px 18px; border-top:1px solid var(--line); background:#0b1219}
  .btn{
    font:inherit; font-size:13.5px; color:var(--ink); cursor:pointer;
    padding:8px 14px; border-radius:10px; border:1px solid #2b3a47;
    background:#16212c; transition:.18s ease;
  }
  .btn:hover{background:#1e2b38; transform:translateY(-1px)}
  .btn:active{transform:translateY(0)}
  .btn.primary{background:var(--accent); border-color:#c07a2c; color:#20150a; font-weight:600}
  .btn.on{background:#2f8f7f; border-color:#1c6a5d; color:#eafff8; font-weight:600}
  .slider{display:flex; align-items:center; gap:9px; font-size:13px; color:var(--muted)}
  input[type=range]{accent-color:var(--accent); width:140px}
  .slider output{color:var(--ink); font-variant-numeric:tabular-nums; min-width:42px}
  .meter{margin-left:auto; font-size:13px; color:var(--muted); font-variant-numeric:tabular-nums}
  .meter b{color:var(--ink); font-weight:600; margin-right:3px}
  .hint{padding:10px 18px 14px; font-size:12px; color:#6d8092; border-top:1px solid #16202a; letter-spacing:.04em}
  kbd{background:#18232e; border:1px solid #2b3a47; border-radius:5px; padding:1px 6px; font-size:11px}
</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <div class="stage">
      <svg id="scene" viewBox="0 0 960 540" role="img" aria-label="一只鹈鹕骑着自行车掠过黄昏的湖畔">
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#0d2135"/>
            <stop offset=".30" stop-color="#2a5f8a"/>
            <stop offset=".58" stop-color="#7fa9b6"/>
            <stop offset=".80" stop-color="#e9a866"/>
            <stop offset="1" stop-color="#f9dfae"/>
          </linearGradient>
          <radialGradient id="sunGlow" cx=".5" cy=".5" r=".5">
            <stop offset="0" stop-color="#fff3cf" stop-opacity=".95"/>
            <stop offset=".45" stop-color="#ffcf7a" stop-opacity=".33"/>
            <stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/>
          </radialGradient>
          <linearGradient id="hillFar" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#3a5c76"/><stop offset="1" stop-color="#22394d"/>
          </linearGradient>
          <linearGradient id="hillNear" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#204155"/><stop offset="1" stop-color="#132634"/>
          </linearGradient>
          <linearGradient id="lake" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#5b93b3"/><stop offset="1" stop-color="#1c4761"/>
          </linearGradient>
          <linearGradient id="road" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#374049"/><stop offset="1" stop-color="#14191e"/>
          </linearGradient>
          <linearGradient id="feather" x1=".2" y1="0" x2=".8" y2="1">
            <stop offset="0" stop-color="#fbf6ec"/><stop offset="1" stop-color="#d7cdb9"/>
          </linearGradient>
          <linearGradient id="wingG" x1="0" y1="0" x2=".55" y2="1">
            <stop offset="0" stop-color="#efe7d8"/><stop offset="1" stop-color="#c6bba6"/>
          </linearGradient>
          <linearGradient id="pouchG" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#f6b661"/><stop offset="1" stop-color="#d7732a"/>
          </linearGradient>
          <radialGradient id="vig" cx=".5" cy=".45" r=".78">
            <stop offset=".52" stop-color="#000" stop-opacity="0"/>
            <stop offset="1" stop-color="#050a0e" stop-opacity=".62"/>
          </radialGradient>
          <filter id="soft" x="-45%" y="-160%" width="190%" height="420%">
            <feGaussianBlur stdDeviation="7"/>
          </filter>

          <!-- 远山瓦片（左右端高度一致，可无缝平铺） -->
          <g id="tileHillFar">
            <path d="M0 336 C 90 288 150 306 232 296 C 310 286 356 244 430 262
                     C 500 279 540 250 612 268 C 690 288 742 262 812 280
                     C 872 296 920 316 960 336 L 960 404 L 0 404 Z" fill="url(#hillFar)"/>
            <path d="M0 336 C 90 288 150 306 232 296 C 310 286 356 244 430 262
                     C 500 279 540 250 612 268 C 690 288 742 262 812 280
                     C 872 296 920 316 960 336" fill="none" stroke="#5d7f96" stroke-width="1.6" opacity=".55"/>
          </g>

          <!-- 近岸丘陵瓦片 -->
          <g id="tileHillNear">
            <path d="M0 372 C 70 350 130 366 210 356 C 290 346 340 318 420 336
                     C 496 353 548 330 620 344 C 700 360 760 340 840 352
                     C 892 360 930 366 960 372 L 960 404 L 0 404 Z" fill="url(#hillNear)"/>
            <!-- 远处的小树剪影 -->
            <g fill="#12283a">
              <path d="M118 356 l 7 -22 l 7 22 z"/><path d="M121 348 l 4 -14 l 4 14 z"/>
              <path d="M470 336 l 8 -26 l 8 26 z"/><path d="M474 327 l 4 -16 l 4 16 z"/>
              <path d="M700 348 l 6 -20 l 6 20 z"/>
            </g>
          </g>

          <!-- 芦苇与灌木瓦片 -->
          <g id="tileMid">
            <ellipse cx="66" cy="424" rx="42" ry="17" fill="#153029"/>
            <ellipse cx="108" cy="428" rx="26" ry="11" fill="#1d3d33"/>
            <g stroke="#1d4038" stroke-width="3.4" fill="none" stroke-linecap="round">
              <path d="M186 428 C 182 404 190 388 184 366"/>
              <path d="M197 428 C 200 406 208 392 204 372"/>
              <path d="M208 428 C 204 410 212 396 217 380"/>
            </g>
            <rect x="181" y="356" width="7" height="14" rx="3.5" fill="#2b4f3f"/>
            <rect x="201" y="363" width="7" height="13" rx="3.5" fill="#2b4f3f"/>
            <ellipse cx="300" cy="426" rx="31" ry="14" fill="#16342c"/>
            <g stroke="#1d4038" stroke-width="3.2" fill="none" stroke-linecap="round">
              <path d="M392 428 C 388 402 396 386 392 364"/>
              <path d="M404 428 C 407 406 415 394 411 376"/>
            </g>
            <rect x="389" y="354" width="7" height="14" rx="3.5" fill="#2b4f3f"/>
            <ellipse cx="520" cy="424" rx="46" ry="18" fill="#153029"/>
            <ellipse cx="562" cy="428" rx="24" ry="11" fill="#1d3d33"/>
            <g stroke="#1d4038" stroke-width="3.4" fill="none" stroke-linecap="round">
              <path d="M646 428 C 642 404 650 388 644 368"/>
              <path d="M658 428 C 661 406 669 392 665 374"/>
              <path d="M669 428 C 665 412 673 398 678 384"/>
            </g>
            <rect x="641" y="358" width="7" height="14" rx="3.5" fill="#2b4f3f"/>
            <rect x="662" y="365" width="7" height="13" rx="3.5" fill="#2b4f3f"/>
            <ellipse cx="762" cy="426" rx="34" ry="15" fill="#16342c"/>
            <g stroke="#1d4038" stroke-width="3.2" fill="none" stroke-linecap="round">
              <path d="M862 428 C 858 402 866 386 862 366"/>
              <path d="M874 428 C 877 406 885 394 881 378"/>
            </g>
            <rect x="859" y="356" width="7" height="14" rx="3.5" fill="#2b4f3f"/>
            <ellipse cx="922" cy="424" rx="28" ry="13" fill="#153029"/>
          </g>

          <!-- 云瓦片 -->
          <g id="tileClouds">
            <g fill="#ffe6c9" opacity=".55">
              <ellipse cx="120" cy="98" rx="54" ry="17"/><ellipse cx="152" cy="88" rx="38" ry="20"/>
              <ellipse cx="84" cy="92" rx="30" ry="13"/>
            </g>
            <g fill="#ffd9b8" opacity=".42">
              <ellipse cx="420" cy="142" rx="60" ry="15"/><ellipse cx="452" cy="132" rx="40" ry="18"/>
            </g>
            <g fill="#fff1dc" opacity=".32">
              <ellipse cx="672" cy="72" rx="46" ry="13"/><ellipse cx="700" cy="64" rx="30" ry="16"/>
            </g>
            <g fill="#ffe0c0" opacity=".34">
              <ellipse cx="884" cy="182" rx="54" ry="14"/><ellipse cx="906" cy="174" rx="34" ry="16"/>
            </g>
          </g>

          <!-- 路面斑点瓦片 -->
          <g id="tileRoad" fill="#48525c">
            <circle cx="58" cy="466" r="2.2" opacity=".55"/><circle cx="140" cy="512" r="3" opacity=".4"/>
            <circle cx="214" cy="452" r="1.8" opacity=".5"/><circle cx="286" cy="492" r="2.6" opacity=".45"/>
            <circle cx="352" cy="530" r="2" opacity=".35"/><circle cx="430" cy="470" r="2.4" opacity=".5"/>
            <circle cx="512" cy="518" r="2" opacity=".4"/><circle cx="588" cy="456" r="3" opacity=".42"/>
            <circle cx="664" cy="500" r="2.2" opacity=".5"/><circle cx="742" cy="470" r="1.8" opacity=".45"/>
            <circle cx="820" cy="524" r="2.6" opacity=".38"/><circle cx="900" cy="462" r="2.2" opacity=".5"/>
            <path d="M170 484 l 34 0 M470 508 l 26 0 M760 490 l 30 0" stroke="#48525c" stroke-width="3" opacity=".35"/>
          </g>

          <!-- 前景杂草瓦片 -->
          <g id="tileWeeds" stroke="#08110f" fill="none" stroke-linecap="round">
            <path d="M28 540 C 34 512 22 498 34 474" stroke-width="5"/>
            <path d="M46 540 C 44 516 56 502 50 484" stroke-width="4"/>
            <path d="M118 540 C 126 514 114 500 128 478" stroke-width="5"/>
            <path d="M136 540 C 132 518 142 506 138 490" stroke-width="3.5"/>
            <path d="M232 540 C 238 516 226 502 236 480" stroke-width="4.5"/>
            <path d="M318 540 C 314 518 324 504 318 486" stroke-width="4"/>
            <path d="M404 540 C 412 512 400 498 412 476" stroke-width="5"/>
            <path d="M422 540 C 418 520 428 508 424 492" stroke-width="3.5"/>
            <path d="M520 540 C 526 516 514 502 524 482" stroke-width="4.5"/>
            <path d="M612 540 C 608 518 618 504 612 486" stroke-width="4"/>
            <path d="M700 540 C 708 512 696 498 708 474" stroke-width="5"/>
            <path d="M718 540 C 714 520 724 508 720 492" stroke-width="3.5"/>
            <path d="M812 540 C 818 516 806 502 816 480" stroke-width="4.5"/>
            <path d="M900 540 C 896 518 906 504 900 486" stroke-width="4"/>
            <g fill="#08110f" stroke="none">
              <ellipse cx="72" cy="534" rx="26" ry="9"/><ellipse cx="270" cy="536" rx="30" ry="8"/>
              <ellipse cx="470" cy="534" rx="24" ry="9"/><ellipse cx="660" cy="536" rx="28" ry="8"/>
              <ellipse cx="860" cy="534" rx="26" ry="9"/>
            </g>
          </g>
        </defs>

        <!-- 天空 -->
        <rect x="0" y="0" width="960" height="404" fill="url(#sky)"/>

        <!-- 太阳 -->
        <circle cx="760" cy="120" r="150" fill="url(#sunGlow)"/>
        <g id="rays" stroke="#ffd98a" stroke-width="3" stroke-linecap="round" opacity=".55">
          <path d="M818 120L836 120M810.2 149L825.8 158M789 170.2L798 185.8M760 178L760 196
                   M731 170.2L722 185.8M709.8 149L694.2 158M702 120L684 120M709.8 91L694.2 82
                   M731 69.8L722 54.2M760 62L760 44M789 69.8L798 54.2M810.2 91L825.8 82"/>
        </g>
        <circle cx="760" cy="120" r="46" fill="#ffe9b0"/>
        <circle cx="760" cy="120" r="46" fill="none" stroke="#fff6dc" stroke-width="2" opacity=".8"/>

        <!-- 远处飞鸟 -->
        <g id="skyBirds" fill="none" stroke="#223c52" stroke-width="2.4" stroke-linecap="round" opacity=".75">
          <path id="birdy0"/><path id="birdy1"/><path id="birdy2"/>
        </g>

        <!-- 云层 -->
        <g id="layerClouds"><use href="#tileClouds"/><use href="#tileClouds" x="960"/></g>

        <!-- 远山 / 近岸 -->
        <g id="layerFar"><use href="#tileHillFar"/><use href="#tileHillFar" x="960"/></g>
        <g id="layerNear"><use href="#tileHillNear"/><use href="#tileHillNear" x="960"/></g>

        <!-- 湖面 -->
        <rect x="0" y="396" width="960" height="34" fill="url(#lake)"/>
        <path d="M736 396 L784 396 L774 430 L746 430 Z" fill="#ffdca6" opacity=".22"/>
        <line id="shimmer1" x1="-80" y1="406" x2="1040" y2="406" stroke="#a9dcea" stroke-width="2.6"
              stroke-dasharray="24 38" opacity=".38"/>
        <line id="shimmer2" x1="-80" y1="416" x2="1040" y2="416" stroke="#cfeaf4" stroke-width="2"
              stroke-dasharray="14 46" opacity=".3"/>
        <line id="shimmer3" x1="-80" y1="424" x2="1040" y2="424" stroke="#8fc6d8" stroke-width="2"
              stroke-dasharray="40 30" opacity=".22"/>

        <!-- 湖岸芦苇 -->
        <g id="layerMid"><use href="#tileMid"/><use href="#tileMid" x="960"/></g>

        <!-- 草坡 -->
        <path d="M0 424 C 120 418 240 429 360 422 C 480 415 600 429 720 422
                 C 840 415 900 427 960 422 L 960 438 L 0 438 Z" fill="#173a2f"/>
        <path d="M0 424 C 120 418 240 429 360 422 C 480 415 600 429 720 422
                 C 840 415 900 427 960 422" fill="none" stroke="#2c5c48" stroke-width="2" opacity=".7"/>

        <!-- 公路 -->
        <rect x="0" y="433" width="960" height="107" fill="url(#road)"/>
        <rect x="0" y="433" width="960" height="4" fill="#5a646d" opacity=".45"/>
        <g id="layerRoad"><use href="#tileRoad"/><use href="#tileRoad" x="960"/></g>
        <line x1="0" y1="446" x2="960" y2="446" stroke="#efe6d2" stroke-width="3" opacity=".18"/>
        <line id="roadDash" x1="-120" y1="500" x2="1080" y2="500" stroke="#f4dcaa" stroke-width="6"
              stroke-dasharray="56 48" opacity=".5"/>

        <!-- 地面阴影 -->
        <ellipse cx="474" cy="437" rx="152" ry="13" fill="#050a0d" opacity=".5" filter="url(#soft)"/>

        <!-- 速度线 -->
        <g id="speedLines"></g>

        <!-- ================= 鹈鹕 + 自行车 ================= -->
        <g id="rig">

          <!-- 远侧腿（车架之后） -->
          <g id="legFar">
            <path id="thighFar" fill="none" stroke="#c7bda8" stroke-width="25" stroke-linecap="round" stroke-linejoin="round"/>
            <path id="tarsusFar" fill="none" stroke="#c96f36" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>
            <circle id="kneeFar" r="7" fill="#c96f36"/>
            <g id="footFar">
              <path d="M-7 -4 C 5 -11 26 -11 37 -3 C 30 6 8 11 -5 6 Z" fill="#c96f36"/>
              <path d="M2 -6 L 31 -6 M4 0 L 27 2" stroke="#9c5324" stroke-width="2" fill="none"/>
            </g>
          </g>
          <g id="crankFar"><rect x="-5" y="-4" width="31" height="8" rx="3.5" fill="#2b3330"/></g>
          <g id="pedalFar">
            <rect x="-13" y="-4" width="26" height="8" rx="3" fill="#23292b"/>
            <rect x="-11" y="-6.5" width="22" height="4" rx="2" fill="#78838a"/>
          </g>

          <!-- 后轮 -->
          <g transform="translate(352 368)">
            <g id="spinRear">
              <circle r="60" fill="none" stroke="#171d1b" stroke-width="10"/>
              <circle r="60" fill="none" stroke="#0a0e0d" stroke-width="10" stroke-dasharray="6 11"/>
              <circle r="52" fill="none" stroke="#d8dde1" stroke-width="4"/>
              <path d="M-50 0L50 0M-43.3 -25L43.3 25M-25 -43.3L25 43.3M0 -50L0 50M25 -43.3L-25 43.3M43.3 -25L-43.3 25"
                    stroke="#98a2a7" stroke-width="1.8"/>
              <circle r="12" fill="#b9c2c6" stroke="#78838a" stroke-width="2"/>
              <circle r="6" fill="#eef2f4"/>
              <rect x="-3" y="-57" width="6" height="11" rx="2.5" fill="#e2543f"/>
              <circle cx="31" cy="-37" r="5" fill="#e2543f" opacity=".9"/>
            </g>
          </g>

          <!-- 前轮 -->
          <g transform="translate(596 368)">
            <g id="spinFront">
              <circle r="60" fill="none" stroke="#171d1b" stroke-width="10"/>
              <circle r="60" fill="none" stroke="#0a0e0d" stroke-width="10" stroke-dasharray="6 11"/>
              <circle r="52" fill="none" stroke="#d8dde1" stroke-width="4"/>
              <path d="M-50 0L50 0M-43.3 -25L43.3 25M-25 -43.3L25 43.3M0 -50L0 50M25 -43.3L-25 43.3M43.3 -25L-43.3 25"
                    stroke="#98a2a7" stroke-width="1.8"/>
              <circle r="7" fill="#eef2f4" stroke="#98a2a7" stroke-width="2"/>
              <rect x="-3" y="-57" width="6" height="11" rx="2.5" fill="#e2543f"/>
              <circle cx="-31" cy="-37" r="5" fill="#e2543f" opacity=".9"/>
            </g>
          </g>

          <!-- 挡泥板 -->
          <path d="M289.6 332 A 72 72 0 0 1 414.4 332" fill="none" stroke="#15584f" stroke-width="9" stroke-linecap="round"/>
          <path d="M533.6 332 A 72 72 0 0 1 658.4 332" fill="none" stroke="#15584f" stroke-width="9" stroke-linecap="round"/>
          <path d="M300 336 L332 356 M648 336 L618 356" stroke="#2f8f7f" stroke-width="3" fill="none"/>

          <!-- 车架 -->
          <g id="frame">
            <path d="M352 368 L462 370" stroke="#1a6f63" stroke-width="9" stroke-linecap="round"/>
            <path d="M352 368 L398 280" stroke="#1a6f63" stroke-width="7" stroke-linecap="round"/>
            <path d="M462 370 L398 276" stroke="#1a6f63" stroke-width="11" stroke-linecap="round"/>
            <path d="M400 278 L568 282" stroke="#1a6f63" stroke-width="9" stroke-linecap="round"/>
            <path d="M462 370 L566 292" stroke="#1a6f63" stroke-width="11" stroke-linecap="round"/>
            <path d="M566 292 L582 262" stroke="#15584f" stroke-width="14" stroke-linecap="round"/>
            <path d="M580 272 C 592 300 596 332 596 368" stroke="#15584f" stroke-width="9" fill="none" stroke-linecap="round"/>
            <path d="M404 282 L420 284 M440 286 L456 288" stroke="#7fe0cd" stroke-width="2.5" opacity=".55"/>
            <!-- 座管 + 座垫 -->
            <path d="M398 278 L396 264" stroke="#2f8f7f" stroke-width="7" stroke-linecap="round"/>
            <path d="M360 268 C 372 257 414 255 430 262 C 414 275 376 277 360 268 Z"
                  fill="#d9503c" stroke="#a8382a" stroke-width="2"/>
            <!-- 水壶与壶架 -->
            <g transform="rotate(-13 448 322)">
              <rect x="437" y="298" width="23" height="48" rx="8" fill="#eae3d3" stroke="#b9b09a" stroke-width="2"/>
              <rect x="443" y="292" width="11" height="8" rx="3" fill="#d9503c"/>
              <path d="M437 316 L460 316" stroke="#cfc5b1" stroke-width="3"/>
            </g>
            <path d="M432 344 L462 340 M434 316 L428 336" stroke="#2f8f7f" stroke-width="3" fill="none"/>
            <!-- 把立 / 车把 -->
            <path d="M582 262 L574 250" stroke="#2f8f7f" stroke-width="8" stroke-linecap="round"/>
            <path d="M548 248 C 566 240 592 242 606 250" stroke="#15584f" stroke-width="7" fill="none" stroke-linecap="round"/>
            <rect x="600" y="244" width="19" height="11" rx="5" fill="#22282b"/>
          </g>

          <!-- 链条 -->
          <g id="chain" fill="none">
            <path id="chainTop" d="M462 348 L352 356" stroke="#7b858a" stroke-width="4.5"/>
            <path id="chainTopD" d="M462 348 L352 356" stroke="#22282b" stroke-width="4.5" stroke-dasharray="4 5"/>
            <path id="chainBot" d="M352 382 L462 392" stroke="#7b858a" stroke-width="4.5"/>
            <path id="chainBotD" d="M352 382 L462 392" stroke="#22282b" stroke-width="4.5" stroke-dasharray="4 5"/>
          </g>

          <!-- 牙盘 -->
          <g id="ring">
            <circle cx="462" cy="370" r="23" fill="none" stroke="#98a2a7" stroke-width="5" stroke-dasharray="3 5"/>
            <circle cx="462" cy="370" r="21" fill="#c9d1d5" stroke="#8a949a" stroke-width="2"/>
            <path d="M462 370 L462 352 M462 370 L478 380 M462 370 L446 380" stroke="#8a949a" stroke-width="3"/>
            <circle cx="462" cy="370" r="5" fill="#5d666b"/>
          </g>

          <!-- 前筐 + 鱼 -->
          <g id="basket">
            <path d="M628 262 C 636 248 650 244 660 250 C 652 256 646 262 642 268 Z" fill="#7fc7d4" stroke="#3f8492" stroke-width="1.8"/>
            <path d="M654 250 L670 240 L666 258 Z" fill="#7fc7d4" stroke="#3f8492" stroke-width="1.8"/>
            <path d="M604 266 L662 266 L656 308 L612 308 Z" fill="#c98a4b" stroke="#8f5c2a" stroke-width="2"/>
            <path d="M607 279 L659 279 M609 293 L657 293" stroke="#8f5c2a" stroke-width="2" opacity=".65"/>
            <path d="M622 266 L618 308 M640 266 L638 308 M656 266 L652 308" stroke="#8f5c2a" stroke-width="2" opacity=".45"/>
            <path d="M604 272 L592 262 M606 298 L590 290" stroke="#2f8f7f" stroke-width="3" fill="none"/>
          </g>

          <!-- 车铃 -->
          <g id="bell">
            <path d="M546 240 C 546 227 566 227 566 240 Z" fill="#d9a441" stroke="#a8781f" stroke-width="2"/>
            <rect x="543" y="240" width="26" height="4.5" rx="2.2" fill="#b8892c"/>
            <path id="bellLever" d="M548 245 C 540 249 536 253 538 258" stroke="#a8781f" stroke-width="3" fill="none"/>
            <circle cx="556" cy="233" r="2.6" fill="#f8e6b4"/>
          </g>
          <g id="honk" opacity="0" transform="translate(556 236)">
            <circle id="honk1" r="12" fill="none" stroke="#ffd98a" stroke-width="3"/>
            <circle id="honk2" r="20" fill="none" stroke="#ffd98a" stroke-width="2"/>
          </g>

          <!-- 围巾（飘动部分由 JS 生成） -->
          <g id="scarf">
            <path id="scarfA" fill="none" stroke="#e2543f" stroke-width="9" stroke-linecap="round"/>
            <path id="scarfB" fill="none" stroke="#c9422f" stroke-width="7" stroke-linecap="round"/>
            <path d="M450 160 C 460 146 486 142 498 152 C 490 166 464 172 450 160 Z"
                  fill="#e2543f" stroke="#a8382a" stroke-width="2"/>
          </g>

          <!-- 鹈鹕 -->
          <g id="bird">
            <!-- 尾羽 -->
            <g id="tail">
              <path d="M302 214 C 266 200 236 194 208 200 C 230 214 258 226 292 234 Z"
                    fill="#d9d0bd" stroke="#b3a893" stroke-width="1.8"/>
              <path d="M300 228 C 264 222 234 224 210 232 C 234 242 262 248 294 248 Z"
                    fill="#e7dfd0" stroke="#b3a893" stroke-width="1.8"/>
              <path d="M298 240 C 268 240 244 246 224 254 C 248 260 274 262 296 258 Z"
                    fill="#cfc5b1" stroke="#b3a893" stroke-width="1.8"/>
            </g>
            <!-- 颈 -->
            <path d="M440 194 C 470 168 466 138 492 130" fill="none" stroke="#f6f0e4"
                  stroke-width="30" stroke-linecap="round"/>
            <path d="M446 186 C 470 166 468 144 488 136" fill="none" stroke="#ddd3c0"
                  stroke-width="6" stroke-linecap="round" opacity=".55"/>
            <!-- 身体 -->
            <path d="M296 220 C 292 180 326 150 372 148 C 420 146 452 170 458 202
                     C 462 232 440 258 400 264 C 356 272 314 258 296 220 Z"
                  fill="url(#feather)" stroke="#b3a893" stroke-width="2"/>
            <path d="M330 246 C 360 262 404 262 438 238" fill="none" stroke="#cfc5b1" stroke-width="2" opacity=".8"/>
            <path d="M312 200 C 340 186 380 182 410 190" fill="none" stroke="#fffaf1" stroke-width="3" opacity=".55"/>

            <!-- 头 + 喙 -->
            <g id="head">
              <circle cx="500" cy="126" r="25" fill="#f7f1e6" stroke="#b3a893" stroke-width="2"/>
              <!-- 喉囊 -->
              <path id="pouch" d="M510 128 C 502 176 528 214 568 214 C 606 212 632 182 630 140 Z"
                    fill="url(#pouchG)" stroke="#c06a24" stroke-width="2"/>
              <path d="M520 150 C 540 186 566 198 596 190" fill="none" stroke="#b8601f" stroke-width="2" opacity=".45"/>
              <path d="M516 140 C 532 176 558 194 588 192" fill="none" stroke="#ffd08a" stroke-width="2.5" opacity=".45"/>
              <!-- 下喙 -->
              <path d="M512 130 L 630 142" stroke="#d98a3c" stroke-width="6" stroke-linecap="round"/>
              <!-- 上喙 -->
              <path d="M508 112 C 552 116 598 126 632 136 C 638 138 638 146 630 147
                       C 594 141 546 133 506 130 Z" fill="#f2a94f" stroke="#c06a24" stroke-width="2"/>
              <path d="M520 121 C 556 125 592 132 620 139" fill="none" stroke="#e08f3a" stroke-width="2" opacity=".7"/>
              <circle cx="524" cy="124" r="1.8" fill="#a8551c"/>
              <!-- 眼 -->
              <circle cx="507" cy="117" r="7.5" fill="#fffdf7"/>
              <circle cx="509" cy="117" r="4.2" fill="#22282b"/>
              <circle cx="510.5" cy="115.5" r="1.5" fill="#fff"/>
              <ellipse id="lid" cx="507" cy="117" rx="8.6" ry="0" fill="#f0e8d8" stroke="#b3a893" stroke-width="1.4"/>
              <!-- 骑行小帽 -->
              <path d="M478 108 C 474 88 492 76 510 78 C 526 80 534 94 532 110 Z"
                    fill="#e2543f" stroke="#a8382a" stroke-width="2"/>
              <path d="M530 96 C 548 92 562 98 568 106 C 554 101 540 103 528 109 Z"
                    fill="#c9422f" stroke="#a8382a" stroke-width="1.6"/>
              <path d="M480 102 C 498 94 516 94 530 102" fill="none" stroke="#f6e7d8" stroke-width="4" opacity=".85"/>
              <circle cx="505" cy="78" r="4" fill="#c9422f"/>
            </g>

            <!-- 翅膀（握把） -->
            <g id="wing">
              <path d="M414 246 C 462 238 518 242 566 250 L 570 266 C 518 260 462 258 416 266 Z"
                    fill="#e4dbca" stroke="#b3a893" stroke-width="2"/>
              <path d="M384 182 C 340 188 318 226 330 262 C 342 296 388 306 418 282
                       C 442 262 448 226 434 200 C 422 182 402 178 384 182 Z"
                    fill="url(#wingG)" stroke="#b3a893" stroke-width="2"/>
              <path d="M344 214 C 366 210 396 214 414 232" fill="none" stroke="#b3a893" stroke-width="2" opacity=".75"/>
              <path d="M340 240 C 362 238 392 244 410 262" fill="none" stroke="#b3a893" stroke-width="2" opacity=".7"/>
              <path d="M350 266 C 370 266 394 272 408 284" fill="none" stroke="#b3a893" stroke-width="2" opacity=".6"/>
              <path d="M558 244 C 578 238 598 240 604 248 C 598 258 578 262 560 260 Z"
                    fill="#efe7d8" stroke="#b3a893" stroke-width="2"/>
              <path d="M566 252 C 574 258 582 260 592 258" fill="none" stroke="#b3a893" stroke-width="1.6"/>
            </g>
          </g>

          <!-- 近侧腿（车架之前） -->
          <g id="legNear">
            <path id="thighNear" fill="none" stroke="#e8e0d0" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>
            <path id="tarsusNear" fill="none" stroke="#ef8b4a" stroke-width="11.5" stroke-linecap="round" stroke-linejoin="round"/>
            <circle id="kneeNear" r="7.5" fill="#e07a3f"/>
            <g id="footNear">
              <path d="M-7 -4 C 5 -11 26 -11 37 -3 C 30 6 8 11 -5 6 Z" fill="#ef8b4a" stroke="#c96f36" stroke-width="1.6"/>
              <path d="M2 -6 L 31 -6 M4 0 L 27 2" stroke="#c96f36" stroke-width="2" fill="none"/>
            </g>
          </g>
          <g id="crankNear"><rect x="-5" y="-4.5" width="31" height="9" rx="4" fill="#3d4744"/></g>
          <g id="pedalNear">
            <rect x="-14" y="-4.5" width="28" height="9" rx="3.5" fill="#2b3330"/>
            <rect x="-12" y="-7" width="24" height="4" rx="2" fill="#98a2a7"/>
          </g>

          <circle id="bellHit" cx="556" cy="238" r="28" fill="transparent" pointer-events="all"
                  style="cursor:pointer"/>
        </g>

        <!-- 扬尘 -->
        <g id="dust"></g>

        <!-- 前景杂草 -->
        <g id="layerWeeds"><use href="#tileWeeds"/><use href="#tileWeeds" x="960"/></g>

        <!-- 暗角 -->
        <rect x="0" y="0" width="960" height="540" fill="url(#vig)" pointer-events="none"/>
      </svg>

      <div class="title">
        <h1>鹈鹕自行车</h1>
        <p>Pelican Vélocipède · SVG 2D 动画</p>
      </div>
    </div>

    <div class="bar">
      <button id="btnPlay" class="btn primary">⏸ 暂停</button>
      <button id="btnWheelie" class="btn" aria-pressed="false">翘前轮</button>
      <button id="btnStand" class="btn" aria-pressed="false">站立摇车</button>
      <button id="btnHonk" class="btn">按铃</button>
      <label class="slider">速度
        <input id="speed" type="range" min="0.2" max="2.6" step="0.1" value="1">
        <output id="speedOut">1.0×</output>
      </label>
      <div class="meter"><b id="cad">63</b>rpm<b id="odo">0</b>m</div>
    </div>
    <div class="hint">
      <kbd>空格</kbd> 播放/暂停 · <kbd>↑</kbd><kbd>↓</kbd> 调速 · <kbd>W</kbd> 翘前轮 · <kbd>S</kbd> 摇车 · <kbd>H</kbd> 按铃 · 也可直接点击车铃
    </div>
  </div>
</div>

<script>
(function(){
  const NS='http://www.w3.org/2000/svg';
  const E=id=>document.getElementById(id);
  const svg=E('scene');

  /* ---------- 关键几何常量（SVG 用户坐标） ---------- */
  const GY=433;                 // 地面
  const WR=65;                  // 车轮外半径
  const HUB_R={x:352,y:368};    // 后轮花鼓
  const HUB_F={x:596,y:368};    // 前轮花鼓
  const BB={x:462,y:370};       // 中轴
  const CRANK=26;               // 曲柄长
  const L1=76, L2=78;           // 大腿 / 小腿长度（二连杆）
  const HIP0={x:402,y:266};     // 坐姿髋关节

  /* ---------- 状态 ---------- */
  let playing=true, speed=1, t=0, wheelAng=0, ground=0;
  let wheelie=0, wheelieT=0, stand=0, standT=0;
  let honkAt=-9, blinkAt=1.8, blinking=0, nextBlink=2.5;
  let frameNo=0;

  if(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    playing=false;
  }

  /* ---------- 粒子池：速度线 & 扬尘 ---------- */
  const lines=[], puffs=[];
  for(let i=0;i<11;i++){
    const l=document.createElementNS(NS,'line');
    l.setAttribute('stroke','#ffe9c4'); l.setAttribute('stroke-width','2.6');
    l.setAttribute('stroke-linecap','round'); l.setAttribute('opacity','0');
    E('speedLines').appendChild(l);
    lines.push({el:l,x:0,y:0,len:0,life:0});
  }
  for(let i=0;i<14;i++){
    const c=document.createElementNS(NS,'circle');
    c.setAttribute('fill','#c9c2b4'); c.setAttribute('opacity','0');
    E('dust').appendChild(c);
    puffs.push({el:c,x:0,y:0,r:0,vx:0,vy:0,life:0});
  }

  /* ---------- 二连杆腿部解算（脚固定在脚踏上） ---------- */
  function solveLeg(hip, foot, sign, thighEl, tarsusEl, kneeEl, footEl, tilt){
    let dx=foot.x-hip.x, dy=foot.y-hip.y;
    let d=Math.hypot(dx,dy);
    const max=L1+L2-1, min=Math.abs(L1-L2)+1;
    if(d>max){ const s=max/d; dx*=s; dy*=s; d=max; }
    if(d<min){ const s=min/d; dx*=s; dy*=s; d=min; }
    const a=(L1*L1-L2*L2+d*d)/(2*d);
    const h=Math.sqrt(Math.max(0,L1*L1-a*a));
    const ux=dx/d, uy=dy/d;
    const kx=hip.x+ux*a-uy*h*sign;
    const ky=hip.y+uy*a+ux*h*sign;
    const fx=hip.x+dx, fy=hip.y+dy;
    const d1='M'+hip.x.toFixed(1)+' '+hip.y.toFixed(1)+' L'+kx.toFixed(1)+' '+ky.toFixed(1);
    const d2='M'+kx.toFixed(1)+' '+ky.toFixed(1)+' L'+fx.toFixed(1)+' '+fy.toFixed(1);
    thighEl.setAttribute('d',d1);
    tarsusEl.setAttribute('d',d2);
    kneeEl.setAttribute('cx',kx.toFixed(1)); kneeEl.setAttribute('cy',ky.toFixed(1));
    footEl.setAttribute('transform','translate('+fx.toFixed(1)+' '+fy.toFixed(1)+') rotate('+tilt.toFixed(2)+')');
  }

  /* ---------- 平滑的飘带路径 ---------- */
  function ribbon(x0,y0,step,amp,phase,n){
    const p=[];
    for(let i=0;i<=n;i++){
      p.push([x0-step*i, y0-3.2*i+(2+2.1*i)*Math.sin(phase-i*0.78)*amp]);
    }
    let d='M'+p[0][0].toFixed(1)+' '+p[0][1].toFixed(1);
    for(let i=1;i<p.length-1;i++){
      const mx=(p[i][0]+p[i+1][0])/2, my=(p[i][1]+p[i+1][1])/2;
      d+=' Q'+p[i][0].toFixed(1)+' '+p[i][1].toFixed(1)+' '+mx.toFixed(1)+' '+my.toFixed(1);
    }
    const last=p[p.length-1];
    d+=' L'+last[0].toFixed(1)+' '+last[1].toFixed(1);
    return d;
  }

  /* ---------- 远处飞鸟 ---------- */
  const birdies=[{x:210,y:92,s:1},{x:318,y:126,s:.8},{x:640,y:74,s:.9}];

  /* ---------- 主循环 ---------- */
  let last=performance.now();
  function frame(now){
    const dtR=Math.min(.05,(now-last)/1000); last=now;
    const dt=playing?dtR:0;
    t+=dt;

    const wheelRev=0.9*speed, crankRev=1.05*speed;
    wheelAng+=2*Math.PI*wheelRev*dt;
    ground   =wheelAng*WR;
    const theta=2*Math.PI*crankRev*dt===0?0:0; // 占位
    const crankAng=wheelAng*(crankRev/wheelRev);
    const deg=wheelAng*180/Math.PI;
    const cdeg=crankAng*180/Math.PI;

    /* 姿态：起伏 + 翘头 + 摇车 */
    wheelieT += ((wheelieOn?1:0)-wheelieT)*Math.min(1,dt*4.5);
    standT   += ((standOn?1:0)-standT)*Math.min(1,dt*5);
    const lift=standT*14;
    const bob=(2.4+standT*3.4)*Math.sin(crankAng*2)+1.3*Math.sin(t*2.2);
    const pitch=0.7*Math.sin(crankAng)+standT*1.5;
    E('rig').setAttribute('transform',
      'translate(0 '+bob.toFixed(2)+') rotate('+(-wheelieT*20+pitch).toFixed(2)+' '+HUB_R.x+' '+GY+')');

    /* 轮组 / 传动 */
    E('spinRear').setAttribute('transform','rotate('+deg.toFixed(2)+')');
    E('spinFront').setAttribute('transform','rotate('+deg.toFixed(2)+')');
    E('ring').setAttribute('transform','rotate('+cdeg.toFixed(2)+' '+BB.x+' '+BB.y+')');
    const pn={x:BB.x+CRANK*Math.cos(crankAng), y:BB.y+CRANK*Math.sin(crankAng)};
    const pf={x:BB.x-CRANK*Math.cos(crankAng), y:BB.y-CRANK*Math.sin(crankAng)};
    E('crankNear').setAttribute('transform','translate('+BB.x+' '+BB.y+') rotate('+cdeg.toFixed(2)+')');
    E('crankFar').setAttribute('transform','translate('+BB.x+' '+BB.y+') rotate('+(cdeg+180).toFixed(2)+')');
    E('pedalNear').setAttribute('transform','translate('+pn.x.toFixed(1)+' '+pn.y.toFixed(1)+')');
    E('pedalFar').setAttribute('transform','translate('+pf.x.toFixed(1)+' '+pf.y.toFixed(1)+')');
    const off=(ground%9).toFixed(2);
    E('chainTopD').setAttribute('stroke-dashoffset',off);
    E('chainBotD').setAttribute('stroke-dashoffset',off);

    /* 双腿 */
    const hip={x:HIP0.x+standT*5, y:HIP0.y-lift};
    const tilt=Math.sin(crankAng)*4;
    solveLeg(hip,pn,-1,E('thighNear'),E('tarsusNear'),E('kneeNear'),E('footNear'),tilt);
    solveLeg(hip,pf,-1,E('thighFar'),E('tarsusFar'),E('kneeFar'),E('footFar'),tilt);

    /* 鸟体微动 */
    E('bird').setAttribute('transform',
      'translate(0 '+(-lift).toFixed(2)+') rotate('+(-standT*2.6).toFixed(2)+' '+HIP0.x+' '+HIP0.y+')');
    E('head').setAttribute('transform',
      'rotate('+(1.6*Math.sin(t*1.9)+standT*2).toFixed(2)+' 492 132)');
    E('wing').setAttribute('transform',
      'rotate('+(1.9*Math.sin(t*3.1)+0.8*Math.sin(crankAng)).toFixed(2)+' 386 190)');
    E('tail').setAttribute('transform',
      'rotate('+(2.4*Math.sin(t*4.1)).toFixed(2)+' 300 224)');
    const ps=1+0.055*Math.sin(t*2.3)+0.03*Math.sin(crankAng*2);
    E('pouch').setAttribute('transform',
      'translate(512 130) scale(1 '+ps.toFixed(4)+') translate(-512 -130)');

    /* 眨眼 */
    nextBlink-=dt;
    if(nextBlink<=0){ blinking=0.16; nextBlink=2.2+Math.random()*3.4; }
    if(blinking>0){
      blinking-=dt;
      const k=Math.max(0,blinking);
      E('lid').setAttribute('ry',(8.6*Math.sin(Math.PI*(1-k/0.16))).toFixed(2));
    } else E('lid').setAttribute('ry','0');

    /* 围巾 */
    const ph=-t*6.2+ground*0.02;
    E('scarfA').setAttribute('d',ribbon(452,162,24,1,ph,5));
    E('scarfB').setAttribute('d',ribbon(450,168,20,0.8,ph+0.9,4));

    /* 视差层 */
    const wrap=v=>(-(v%960)).toFixed(2);
    E('layerFar').setAttribute('transform','translate('+wrap(ground*0.05)+' 0)');
    E('layerNear').setAttribute('transform','translate('+wrap(ground*0.10)+' 0)');
    E('layerMid').setAttribute('transform','translate('+wrap(ground*0.24)+' 0)');
    E('layerRoad').setAttribute('transform','translate('+wrap(ground)+' 0)');
    E('layerWeeds').setAttribute('transform','translate('+wrap(ground*1.18)+' 0)');
    E('layerClouds').setAttribute('transform','translate('+wrap(ground*0.035+t*9)+' 0)');
    E('roadDash').setAttribute('stroke-dashoffset',(ground%104).toFixed(2));
    E('shimmer1').setAttribute('stroke-dashoffset',(ground*0.3%62).toFixed(2));
    E('shimmer2').setAttribute('stroke-dashoffset',(ground*0.24%60).toFixed(2));
    E('shimmer3').setAttribute('stroke-dashoffset',(ground*0.34%70).toFixed(2));
    E('rays').setAttribute('transform','rotate('+(t*5).toFixed(2)+' 760 120)');

    /* 远处飞鸟 */
    birdies.forEach((b,i)=>{
      b.x-=(14+i*6+ground*0.02)*dt;
      if(b.x<-30) b.x=990+Math.random()*120;
      const a=(3+4*Math.sin(t*7+i*1.7))*b.s;
      const s=b.s;
      E('birdy'+i).setAttribute('d',
        'M'+(b.x-9*s).toFixed(1)+' '+(b.y+a).toFixed(1)+
        ' Q'+(b.x-4*s).toFixed(1)+' '+(b.y-a).toFixed(1)+' '+b.x.toFixed(1)+' '+b.y.toFixed(1)+
        ' Q'+(b.x+4*s).toFixed(1)+' '+(b.y-a).toFixed(1)+' '+(b.x+9*s).toFixed(1)+' '+(b.y+a).toFixed(1));
    });

    /* 速度线 */
    const gs=2*Math.PI*WR*wheelRev;
    for(const s of lines){
      if(s.life>0){
        s.life-=dt; s.x-=(gs*1.35+90)*dt;
        const o=Math.max(0,Math.min(1,s.life*1.7))*0.5*Math.min(1,speed);
        s.el.setAttribute('x1',s.x.toFixed(1)); s.el.setAttribute('y1',s.y.toFixed(1));
        s.el.setAttribute('x2',(s.x+s.len).toFixed(1)); s.el.setAttribute('y2',s.y.toFixed(1));
        s.el.setAttribute('opacity',o.toFixed(3));
      } else if(playing && speed>0.55){
        s.x=600+Math.random()*360; s.y=140+Math.random()*220;
        s.len=26+Math.random()*72; s.life=0.45+Math.random()*0.6;
      }
    }

    /* 扬尘 */
    puffTimer-=dt;
    if(puffTimer<=0 && playing && speed>0.4){
      const p=puffs.find(q=>q.life<=0);
      if(p){
        p.x=336+Math.random()*22; p.y=GY-2-Math.random()*10;
        p.r=2.5+Math.random()*3; p.vx=-(gs*0.45+50+Math.random()*70);
        p.vy=-(14+Math.random()*38); p.life=0.85+Math.random()*0.5;
      }
      puffTimer=0.085;
    }
    for(const p of puffs){
      if(p.life>0){
        p.life-=dt; p.x+=p.vx*dt; p.y+=p.vy*dt; p.r+=13*dt;
        p.el.setAttribute('cx',p.x.toFixed(1)); p.el.setAttribute('cy',p.y.toFixed(1));
        p.el.setAttribute('r',p.r.toFixed(1));
        p.el.setAttribute('opacity',(Math.max(0,p.life)*0.42).toFixed(3));
      }
    }

    /* 车铃涟漪 */
    const he=t-honkAt;
    if(he<1){
      const k=1-he;
      E('honk').setAttribute('opacity',(k*0.9).toFixed(3));
      E('honk1').setAttribute('r',(10+he*46).toFixed(1));
      E('honk2').setAttribute('r',(10+he*28).toFixed(1));
      E('bell').setAttribute('transform',
        'rotate('+(6*Math.sin(he*38)*k).toFixed(2)+' 556 242)');
    } else {
      E('honk').setAttribute('opacity','0');
      E('bell').setAttribute('transform','rotate(0 556 242)');
    }

    /* 读数 */
    if(++frameNo%6===0){
      E('cad').textContent=Math.round(crankRev*60);
      E('odo').textContent=Math.round(ground/40);
    }
    requestAnimationFrame(frame);
  }
  let puffTimer=0;

  /* ---------- 交互 ---------- */
  let wheelieOn=false, standOn=false;
  const btnPlay=E('btnPlay'), btnW=E('btnWheelie'), btnS=E('btnStand');

  function setPlay(v){
    playing=v;
    btnPlay.textContent=playing?'⏸ 暂停':'▶ 播放';
    btnPlay.classList.toggle('primary',playing);
  }
  function honk(){ honkAt=t; }

  btnPlay.addEventListener('click',()=>setPlay(!playing));
  btnW.addEventListener('click',()=>{
    wheelieOn=!wheelieOn;
    btnW.classList.toggle('on',wheelieOn);
    btnW.setAttribute('aria-pressed',String(wheelieOn));
  });
  btnS.addEventListener('click',()=>{
    standOn=!standOn;
    btnS.classList.toggle('on',standOn);
    btnS.setAttribute('aria-pressed',String(standOn));
  });
  E('btnHonk').addEventListener('click',honk);
  E('bellHit').addEventListener('click',honk);

  const sl=E('speed'), out=E('speedOut');
  sl.addEventListener('input',()=>{ speed=parseFloat(sl.value); out.textContent=speed.toFixed(1)+'×'; });

  window.addEventListener('keydown',e=>{
    if(e.target.tagName==='INPUT') return;
    const k=e.key.toLowerCase();
    if(k===' '){ e.preventDefault(); setPlay(!playing); }
    else if(e.key==='ArrowUp'){ sl.value=Math.min(2.6,speed+0.2); sl.dispatchEvent(new Event('input')); }
    else if(e.key==='ArrowDown'){ sl.value=Math.max(0.2,speed-0.2); sl.dispatchEvent(new Event('input')); }
    else if(k==='w'){ btnW.click(); }
    else if(k==='s'){ btnS.click(); }
    else if(k==='h'){ honk(); }
  });

  setPlay(playing);
  requestAnimationFrame(frame);
})();
</script>
</body>
</html>
```

**画面里都在动什么**

- **传动链**：后轮/前轮/牙盘/曲柄按同一角速度联动，链条用 `stroke-dashoffset` 滚动，上下两段的行进方向相反（真实的传动方向）。
- **踩踏**：脚掌被"钉"在脚踏圆周上，髋—膝—踝用二连杆 IK 实时求解，所以膝盖轨迹、大腿长短变化都是自然生成的，而不是硬写关键帧。
- **姿态**：车身随曲柄二次谐波上下起伏；「翘前轮」把整个 rig 绕后轮接地点旋转（内部所有关节自动跟随）；「站立摇车」抬高髋点、加大摆幅、身体前倾。
- **鹈鹕本身**：翅膀轻微扇动、尾羽抖动、头部点动、喉囊周期性鼓胀、随机眨眼、围巾用平滑贝塞尔飘带按行进速度波动。
- **环境**：远山/近岸/芦苇/路面斑点/前景杂草五层视差，路面中线与湖面波光用 dash 滚动，云层独立漂移，天空飞鸟振翅，后轮卷起扬尘，身后掠过速度线。
- **交互**：播放/暂停、速度 0.2–2.6×、翘前轮、摇车、按铃（点击 SVG 里的车铃也有效，带扩散涟漪与铃体抖动），空格 / ↑↓ / W / S / H 快捷键；已适配 `prefers-reduced-motion`。

把内容保存成 `pelican.html` 直接双击打开即可，单文件、零依赖。