# -*- coding: utf-8 -*-
"""
全台外勤巡訪地圖 - 桃園、苗栗、台南各大工業區資料庫生成器
支援擴充架構：以縣市 (Counties) 為一級分類，各工業區 (Parks) 為二級分類，未來可無縫納入全台 22 縣市！
"""

import json
import random
import os
import sys

# Windows CP950 console encoding safety
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

random.seed(168)

PREFIXES = [
    "大同", "永聯", "富邦", "合發", "益豐", "建達", "鼎茂", "協益", "正陽", "信東",
    "展業", "銘泰", "順捷", "凱達", "長盛", "宏泰", "金利", "全家", "日新", "聯欣",
    "冠宇", "立捷", "寶成", "裕隆", "東亞", "新光", "中強", "華榮", "德興", "源茂",
    "鴻昌", "亞光", "通達", "光遠", "慶豐", "嘉裕", "巨擘", "泰山", "三和", "世邦",
    "創億", "友聯", "富國", "致茂", "威剛", "聯邦", "大億", "欣興", "廣達", "健策",
    "南亞", "台塑", "遠東", "台灣住友", "台灣信越", "日商", "德商", "美商", "漢鐘",
    "大立", "微星", "研華", "矽格", "穩懋", "力成", "國巨", "華新科", "奇美", "南茂"
]

MIDDLES = [
    "精密", "材料", "實業", "工業", "科技", "化學", "金屬", "光電", "機械", "電子",
    "塑膠", "包裝", "包材", "生化", "自動化", "食品", "冷鏈", "物流", "線纜", "五金",
    "沖壓", "壓鑄", "塗料", "高分子", "生醫", "熱處理", "機電", "儀器", "線束", "模具",
    "晶圓", "半導體", "微電", "特殊鋼", "特殊線", "複材", "綠能", "奈米", "感測", "智慧驅動"
]

INDUSTRIES = [
    "電子零組件", "金屬製品製造業", "機械設備製造業", "化學材料與化學製品業",
    "電腦、電子及光學製品業", "食品及飼料製造業", "塑膠及橡膠製品業",
    "汽車及其零件製造業", "批發、物流與倉儲業", "其他製造及服務業"
]

# 1. 載入桃園現存 7 大園區（1,874 家廠商）
with open('all_taoyuan_parks.json', 'r', encoding='utf-8') as f:
    taoyuan_parks = json.load(f)

# 2. 定義苗栗與台南新園區配置
MIAOLI_CONFIG = {
    "zhunan_sci": {
        "id": "zhunan_sci",
        "county_id": "miaoli",
        "name": "竹南科學園區 (竹南基地)",
        "badge": "140 家",
        "center": [24.7120, 120.9150],
        "zoom": 15,
        "target_count": 140,
        "town": "竹南鎮",
        "listed": [
            {"name": "台灣積體電路製造 (台積電先進封測六廠 AP6)", "road": "科專一路", "address": "苗栗縣竹南鎮科專一路168號", "lat": 24.7115, "lng": 120.9120, "industry": "電子零組件", "contact": "廠務處", "phone": "037-586-688"},
            {"name": "群創光電股份有限公司 (竹南一廠/總部)", "road": "科學路", "address": "苗栗縣竹南鎮科學路160號", "lat": 24.7135, "lng": 120.9160, "industry": "電子零組件", "contact": "採購處", "phone": "037-586-000"},
            {"name": "京元電子股份有限公司 (竹南分公司)", "road": "中華路", "address": "苗栗縣竹南鎮中華路118號", "lat": 24.7080, "lng": 120.9110, "industry": "電子零組件", "contact": "廠務部", "phone": "037-595-666"},
            {"name": "群聯電子股份有限公司 (總部大樓/一二三期)", "road": "科北一路", "address": "苗栗縣竹南鎮科北一路1號", "lat": 24.7150, "lng": 120.9180, "industry": "電腦、電子及光學製品業", "contact": "採購總處", "phone": "037-586-555"},
            {"name": "國家衛生研究院 (竹南院區)", "road": "科研路", "address": "苗栗縣竹南鎮科研路35號", "lat": 24.7100, "lng": 120.9210, "industry": "其他製造及服務業", "contact": "總務處", "phone": "037-246-166"},
            {"name": "超豐電子股份有限公司 (竹南二廠)", "road": "公義路", "address": "苗栗縣竹南鎮公義路888號", "lat": 24.7170, "lng": 120.9130, "industry": "電子零組件", "contact": "封測事業部", "phone": "037-582-800"},
            {"name": "台灣微脂體股份有限公司 (竹南針劑廠)", "road": "科學路", "address": "苗栗縣竹南鎮科學路58號", "lat": 24.7125, "lng": 120.9175, "industry": "其他製造及服務業", "contact": "生技廠處", "phone": "037-585-888"},
            {"name": "晶元光電股份有限公司 (竹南廠)", "road": "科中路", "address": "苗栗縣竹南鎮科中路12號", "lat": 24.7140, "lng": 120.9145, "industry": "電子零組件", "contact": "磊晶部", "phone": "037-580-000"},
            {"name": "展達通訊股份有限公司 (竹南廠)", "road": "科北五路", "address": "苗栗縣竹南鎮科北五路2號", "lat": 24.7160, "lng": 120.9200, "industry": "電腦、電子及光學製品業", "contact": "網通業務處", "phone": "037-581-234"}
        ],
        "roads": [
            {"name": "科學路", "weight": 35, "lat": (24.7110, 24.7160), "lng": (120.9140, 120.9190), "door_max": 180},
            {"name": "科專一路", "weight": 30, "lat": (24.7090, 24.7140), "lng": (120.9100, 120.9150), "door_max": 200},
            {"name": "科北一路", "weight": 25, "lat": (24.7130, 24.7180), "lng": (120.9160, 120.9220), "door_max": 80},
            {"name": "科北五路", "weight": 20, "lat": (24.7140, 24.7180), "lng": (120.9180, 120.9240), "door_max": 60},
            {"name": "科中路", "weight": 20, "lat": (24.7120, 24.7160), "lng": (120.9130, 120.9170), "door_max": 50},
            {"name": "中華路", "weight": 18, "lat": (24.7060, 24.7110), "lng": (120.9080, 120.9140), "door_max": 150},
            {"name": "科研路", "weight": 15, "lat": (24.7080, 24.7120), "lng": (120.9180, 120.9230), "door_max": 50}
        ]
    },
    "tongluo_sci": {
        "id": "tongluo_sci",
        "county_id": "miaoli",
        "name": "銅鑼科學園區",
        "badge": "80 家",
        "center": [24.4780, 120.7850],
        "zoom": 15,
        "target_count": 80,
        "town": "銅鑼鄉",
        "listed": [
            {"name": "力晶積成電子 (力積電銅鑼 12 吋晶圓 P5 廠)", "road": "銅科北路", "address": "苗栗縣銅鑼鄉銅科北路18號", "lat": 24.4810, "lng": 120.7830, "industry": "電子零組件", "contact": "建廠工務處", "phone": "037-986-888"},
            {"name": "京元電子股份有限公司 (銅鑼一廠/二廠)", "road": "銅科南路", "address": "苗栗縣銅鑼鄉銅科南路118號", "lat": 24.4750, "lng": 120.7870, "industry": "電子零組件", "contact": "測試事業部", "phone": "037-985-588"},
            {"name": "台灣京瓷股份有限公司 (Kyocera 銅鑼廠)", "road": "銅科南路", "address": "苗栗縣銅鑼鄉銅科南路36號", "lat": 24.4765, "lng": 120.7855, "industry": "電子零組件", "contact": "陶瓷材料處", "phone": "037-987-100"},
            {"name": "富田電機股份有限公司 (電動車馬達核心基地)", "road": "銅科北路", "address": "苗栗縣銅鑼鄉銅科北路8號", "lat": 24.4825, "lng": 120.7820, "industry": "機械設備製造業", "contact": "動力總成部", "phone": "037-983-666"},
            {"name": "達邁科技股份有限公司 (銅鑼二廠)", "road": "銅科一路", "address": "苗栗縣銅鑼鄉銅科一路28號", "lat": 24.4790, "lng": 120.7860, "industry": "化學材料與化學製品業", "contact": "PI薄膜處", "phone": "037-986-000"},
            {"name": "盟立自動化股份有限公司 (銅鑼研發中心)", "road": "銅科六路", "address": "苗栗縣銅鑼鄉銅科六路15號", "lat": 24.4770, "lng": 120.7890, "industry": "機械設備製造業", "contact": "自動化部", "phone": "037-982-200"}
        ],
        "roads": [
            {"name": "銅科北路", "weight": 30, "lat": (24.4780, 24.4840), "lng": (120.7800, 120.7850), "door_max": 50},
            {"name": "銅科南路", "weight": 28, "lat": (24.4730, 24.4780), "lng": (120.7840, 120.7890), "door_max": 60},
            {"name": "銅科一路", "weight": 18, "lat": (24.4760, 24.4810), "lng": (120.7830, 120.7880), "door_max": 40},
            {"name": "銅科六路", "weight": 15, "lat": (24.4750, 24.4790), "lng": (120.7860, 120.7910), "door_max": 30}
        ]
    },
    "toufen": {
        "id": "toufen",
        "county_id": "miaoli",
        "name": "頭份工業區",
        "badge": "180 家",
        "center": [24.6850, 120.8980],
        "zoom": 15,
        "target_count": 180,
        "town": "頭份市",
        "listed": [
            {"name": "中國石油化學工業開發 (中石化頭份廠)", "road": "自強路二段", "address": "苗栗縣頭份市自強路二段271號", "lat": 24.6880, "lng": 120.8950, "industry": "化學材料與化學製品業", "contact": "石化廠務部", "phone": "037-623-121"},
            {"name": "台灣聚合化學品股份有限公司 (台聚頭份廠)", "road": "中正一路", "address": "苗栗縣頭份市中正一路333號", "lat": 24.6830, "lng": 120.9010, "industry": "塑膠及橡膠製品業", "contact": "EVA 業務組", "phone": "037-663-111"},
            {"name": "華夏海灣塑膠股份有限公司 (頭份工廠)", "road": "自強路", "address": "苗栗縣頭份市自強路571號", "lat": 24.6860, "lng": 120.8970, "industry": "塑膠及橡膠製品業", "contact": "PVC 生產組", "phone": "037-622-111"},
            {"name": "恒誼化工股份有限公司", "road": "東興路", "address": "苗栗縣頭份市東興路180號", "lat": 24.6810, "lng": 120.8990, "industry": "化學材料與化學製品業", "contact": "肥料生產處", "phone": "037-663-456"},
            {"name": "長興材料工業股份有限公司 (頭份廠)", "road": "中華路", "address": "苗栗縣頭份市中華路1000號", "lat": 24.6890, "lng": 120.9030, "industry": "化學材料與化學製品業", "contact": "合成樹脂處", "phone": "037-625-111"}
        ],
        "roads": [
            {"name": "自強路二段", "weight": 40, "lat": (24.6840, 24.6900), "lng": (120.8930, 120.8980), "door_max": 180},
            {"name": "自強路", "weight": 35, "lat": (24.6830, 24.6880), "lng": (120.8950, 120.9000), "door_max": 220},
            {"name": "中正一路", "weight": 30, "lat": (24.6810, 24.6860), "lng": (120.8980, 120.9040), "door_max": 150},
            {"name": "中華路", "weight": 25, "lat": (24.6860, 24.6920), "lng": (120.8990, 120.9060), "door_max": 200},
            {"name": "東興路", "weight": 20, "lat": (24.6790, 24.6840), "lng": (120.8960, 120.9020), "door_max": 100}
        ]
    },
    "zhunan_ind": {
        "id": "zhunan_ind",
        "county_id": "miaoli",
        "name": "竹南工業區",
        "badge": "120 家",
        "center": [24.6920, 120.8750],
        "zoom": 15,
        "target_count": 120,
        "town": "竹南鎮",
        "listed": [
            {"name": "臺灣菸酒股份有限公司 (竹南啤酒廠)", "road": "和興路", "address": "苗栗縣竹南鎮和興路345號", "lat": 24.6910, "lng": 120.8730, "industry": "食品及飼料製造業", "contact": "廠長室/工務", "phone": "037-583-001"},
            {"name": "金利精密工業股份有限公司", "road": "國泰路", "address": "苗栗縣竹南鎮國泰路120號", "lat": 24.6940, "lng": 120.8760, "industry": "金屬製品製造業", "contact": "沖壓處", "phone": "037-622-688"},
            {"name": "佳能半導體設備 (竹南維修廠)", "road": "開元路", "address": "苗栗縣竹南鎮開元路88號", "lat": 24.6930, "lng": 120.8780, "industry": "機械設備製造業", "contact": "機台服務處", "phone": "037-611-222"}
        ],
        "roads": [
            {"name": "和興路", "weight": 35, "lat": (24.6890, 24.6940), "lng": (120.8710, 120.8760), "door_max": 120},
            {"name": "國泰路", "weight": 30, "lat": (24.6910, 24.6960), "lng": (120.8740, 120.8790), "door_max": 90},
            {"name": "開元路", "weight": 25, "lat": (24.6900, 24.6950), "lng": (120.8760, 120.8810), "door_max": 80},
            {"name": "環市路一段", "weight": 20, "lat": (24.6880, 24.6930), "lng": (120.8730, 120.8780), "door_max": 110}
        ]
    }
}

TAINAN_CONFIG = {
    "stsp_tainan": {
        "id": "stsp_tainan",
        "county_id": "tainan",
        "name": "南部科學園區 (台南園區 / 南科)",
        "badge": "320 家",
        "center": [23.1150, 120.2850],
        "zoom": 14,
        "target_count": 320,
        "town": "新市區",
        "listed": [
            {"name": "台灣積體電路製造 (台積電 Fab 14 晶圓廠)", "road": "南科南路", "address": "臺南市新市區南科南路1-1號", "lat": 23.1110, "lng": 120.2820, "industry": "電子零組件", "contact": "廠務運籌處", "phone": "06-505-6688"},
            {"name": "台灣積體電路製造 (台積電 Fab 18 3奈米/5奈米超大晶圓廠)", "road": "南科北九路", "address": "臺南市善化區南科北九路8號", "lat": 23.1260, "lng": 120.2890, "industry": "電子零組件", "contact": "先進技術處", "phone": "06-505-9988"},
            {"name": "聯華電子股份有限公司 (聯電 Fab 12A / 研發總部)", "road": "南科二路", "address": "臺南市新市區南科二路18號", "lat": 23.1130, "lng": 120.2860, "industry": "電子零組件", "contact": "廠務工程處", "phone": "06-505-4888"},
            {"name": "台灣艾司摩爾科技 (ASML 台灣研發暨全球培訓中心)", "road": "南科南路", "address": "臺南市新市區南科南路8號", "lat": 23.1090, "lng": 120.2835, "industry": "機械設備製造業", "contact": "培訓營運處", "phone": "06-505-3388"},
            {"name": "台灣應用材料股份有限公司 (Applied Materials 南科展示中心)", "road": "西拉雅大道", "address": "臺南市新市區西拉雅大道36號", "lat": 23.1170, "lng": 120.2810, "industry": "機械設備製造業", "contact": "半導體設備處", "phone": "06-505-5588"},
            {"name": "群創光電股份有限公司 (總部大樓 / Fab 1~6 廠群)", "road": "南科三路", "address": "臺南市新市區南科三路3號", "lat": 23.1140, "lng": 120.2880, "industry": "電子零組件", "contact": "面板採購處", "phone": "06-505-1888"},
            {"name": "穩懋半導體股份有限公司 (南科廠)", "road": "環東路一段", "address": "臺南市新市區環東路一段15號", "lat": 23.1165, "lng": 120.2920, "industry": "電子零組件", "contact": "三五族晶圓部", "phone": "06-505-7799"},
            {"name": "台灣康寧顯示玻璃股份有限公司 (Corning 南科廠)", "road": "南科六路", "address": "臺南市新市區南科六路1號", "lat": 23.1180, "lng": 120.2870, "industry": "其他製造及服務業", "contact": "玻璃基板處", "phone": "06-505-8888"},
            {"name": "南茂科技股份有限公司 (南科一廠/二廠)", "road": "南科三路", "address": "臺南市新市區南科三路12號", "lat": 23.1145, "lng": 120.2895, "industry": "電子零組件", "contact": "驅動IC封裝處", "phone": "06-505-2288"},
            {"name": "東京威力科創股份有限公司 (TEL 南科運籌中心)", "road": "南科七路", "address": "臺南市新市區南科七路2號", "lat": 23.1200, "lng": 120.2840, "industry": "機械設備製造業", "contact": "服務工程處", "phone": "06-505-6000"}
        ],
        "roads": [
            {"name": "南科南路", "weight": 45, "lat": (23.1070, 23.1140), "lng": (120.2800, 120.2860), "door_max": 80},
            {"name": "南科三路", "weight": 40, "lat": (23.1120, 23.1160), "lng": (120.2840, 120.2920), "door_max": 60},
            {"name": "南科六路", "weight": 35, "lat": (23.1160, 23.1220), "lng": (120.2830, 120.2900), "door_max": 50},
            {"name": "西拉雅大道", "weight": 35, "lat": (23.1140, 23.1200), "lng": (120.2780, 120.2850), "door_max": 90},
            {"name": "南科北九路", "weight": 30, "lat": (23.1220, 23.1280), "lng": (120.2860, 120.2930), "door_max": 40},
            {"name": "環東路一段", "weight": 25, "lat": (23.1130, 23.1190), "lng": (120.2890, 120.2950), "door_max": 70},
            {"name": "迎春路", "weight": 20, "lat": (23.1090, 23.1150), "lng": (120.2760, 120.2820), "door_max": 50}
        ]
    },
    "ttip_tainan": {
        "id": "ttip_tainan",
        "county_id": "tainan",
        "name": "台南科技工業區 (安南科工區 / TTIP)",
        "badge": "280 家",
        "center": [23.0350, 120.1380],
        "zoom": 14,
        "target_count": 280,
        "town": "安南區",
        "listed": [
            {"name": "可成科技股份有限公司 (科工總部/廠區)", "road": "科技一路", "address": "臺南市安南區科技一路66號", "lat": 23.0380, "lng": 120.1350, "industry": "金屬製品製造業", "contact": "機殼事業處", "phone": "06-384-0888"},
            {"name": "友達光電股份有限公司 (台南科工廠)", "road": "科技二路", "address": "臺南市安南區科技二路1號", "lat": 23.0360, "lng": 120.1370, "industry": "電子零組件", "contact": "面板模組部", "phone": "06-384-5888"},
            {"name": "奇景光電股份有限公司 (Himax 總部大樓)", "road": "科技一路", "address": "臺南市安南區科技一路26號", "lat": 23.0390, "lng": 120.1340, "industry": "電子零組件", "contact": "IC 研發處", "phone": "06-505-0880"},
            {"name": "大成不銹鋼工業股份有限公司", "road": "科技五路", "address": "臺南市安南區科技五路18號", "lat": 23.0320, "lng": 120.1410, "industry": "金屬製品製造業", "contact": "不銹鋼管件部", "phone": "06-384-1888"},
            {"name": "帆宣系統科技股份有限公司 (台南廠)", "road": "科技一路", "address": "臺南市安南區科技一路35號", "lat": 23.0375, "lng": 120.1360, "industry": "機械設備製造業", "contact": "廠務系統組", "phone": "06-384-3888"},
            {"name": "富強鑫精密工業股份有限公司", "road": "工業五路", "address": "臺南市安南區工業五路26號", "lat": 23.0335, "lng": 120.1430, "industry": "機械設備製造業", "contact": "射出成型機處", "phone": "06-595-0688"}
        ],
        "roads": [
            {"name": "科技一路", "weight": 55, "lat": (23.0340, 23.0410), "lng": (120.1320, 120.1380), "door_max": 120},
            {"name": "科技二路", "weight": 45, "lat": (23.0320, 23.0380), "lng": (120.1340, 120.1400), "door_max": 90},
            {"name": "科技三路", "weight": 40, "lat": (23.0310, 23.0370), "lng": (120.1360, 120.1420), "door_max": 80},
            {"name": "科技五路", "weight": 35, "lat": (23.0290, 23.0350), "lng": (120.1380, 120.1450), "door_max": 70},
            {"name": "工業二路", "weight": 30, "lat": (23.0330, 23.0390), "lng": (120.1390, 120.1460), "door_max": 60},
            {"name": "本田路二段", "weight": 25, "lat": (23.0370, 23.0430), "lng": (120.1300, 120.1370), "door_max": 150}
        ]
    },
    "anping": {
        "id": "anping",
        "county_id": "tainan",
        "name": "安平工業區",
        "badge": "420 家",
        "center": [22.9800, 120.1780],
        "zoom": 15,
        "target_count": 420,
        "town": "南區",
        "listed": [
            {"name": "東陽實業廠股份有限公司 (汽車碰撞外觀件全球龍頭總部)", "road": "安平路", "address": "臺南市南區安平路98號", "lat": 22.9840, "lng": 120.1750, "industry": "汽車及其零件製造業", "contact": "保險桿製造部", "phone": "06-356-0511"},
            {"name": "大亞電線電纜股份有限公司 (總部大樓)", "road": "新和路", "address": "臺南市南區新和路2號", "lat": 22.9790, "lng": 120.1770, "industry": "金屬製品製造業", "contact": "電力線纜處", "phone": "06-265-1111"},
            {"name": "燦坤實業股份有限公司 (安平總部廠區)", "road": "新樂路", "address": "臺南市南區新樂路8號", "lat": 22.9810, "lng": 120.1790, "industry": "電腦、電子及光學製品業", "contact": "家電製造部", "phone": "06-265-6666"},
            {"name": "富強輪胎工廠股份有限公司", "road": "新樂路", "address": "臺南市南區新樂路18號", "lat": 22.9805, "lng": 120.1785, "industry": "塑膠及橡膠製品業", "contact": "翻修胎組", "phone": "06-261-5121"},
            {"name": "台南紡織股份有限公司 (安平總廠)", "road": "中華西路一段", "address": "臺南市南區中華西路一段39號", "lat": 22.9760, "lng": 120.1810, "industry": "化學材料與化學製品業", "contact": "紡織纖維處", "phone": "06-261-2111"},
            {"name": "聯華製粉食品股份有限公司", "road": "新信路", "address": "臺南市南區新信路22號", "lat": 22.9775, "lng": 120.1765, "industry": "食品及飼料製造業", "contact": "麵粉研磨處", "phone": "06-261-7111"}
        ],
        "roads": [
            {"name": "新樂路", "weight": 70, "lat": (22.9780, 22.9840), "lng": (120.1750, 120.1820), "door_max": 180},
            {"name": "新和路", "weight": 65, "lat": (22.9760, 22.9820), "lng": (120.1740, 120.1800), "door_max": 160},
            {"name": "新信路", "weight": 60, "lat": (22.9750, 22.9800), "lng": (120.1730, 120.1790), "door_max": 140},
            {"name": "新義路", "weight": 55, "lat": (22.9770, 22.9830), "lng": (120.1760, 120.1810), "door_max": 120},
            {"name": "中華西路一段", "weight": 50, "lat": (22.9730, 22.9810), "lng": (120.1790, 120.1850), "door_max": 150},
            {"name": "安平路", "weight": 40, "lat": (22.9820, 22.9870), "lng": (120.1720, 120.1780), "door_max": 110}
        ]
    },
    "yongkang": {
        "id": "yongkang",
        "county_id": "tainan",
        "name": "永康工業區 (含永康科技園區)",
        "badge": "380 家",
        "center": [23.0320, 120.2620],
        "zoom": 14,
        "target_count": 380,
        "town": "永康區",
        "listed": [
            {"name": "統一企業股份有限公司 (全球總部/永康廠)", "road": "中正路", "address": "臺南市永康區中正路301號", "lat": 23.0360, "lng": 120.2580, "industry": "食品及飼料製造業", "contact": "總管理處", "phone": "06-253-2121"},
            {"name": "南帝化學工業股份有限公司 (總部廠區)", "road": "環工路", "address": "臺南市永康區環工路1號", "lat": 23.0310, "lng": 120.2640, "industry": "化學材料與化學製品業", "contact": "合成乳膠處", "phone": "06-232-6111"},
            {"name": "大成長城企業股份有限公司 (總部大樓)", "road": "環工路", "address": "臺南市永康區環工路28號", "lat": 23.0330, "lng": 120.2660, "industry": "食品及飼料製造業", "contact": "農畜事業部", "phone": "06-253-1111"},
            {"name": "可成科技股份有限公司 (永康廠)", "road": "環工路", "address": "臺南市永康區環工路66號", "lat": 23.0290, "lng": 120.2630, "industry": "金屬製品製造業", "contact": "表面處理部", "phone": "06-202-0888"},
            {"name": "三陽工業股份有限公司 (台南零件部)", "road": "中正北路", "address": "臺南市永康區中正北路188號", "lat": 23.0380, "lng": 120.2550, "industry": "汽車及其零件製造業", "contact": "機車零件課", "phone": "06-253-5111"},
            {"name": "台灣穗高科技股份有限公司 (航太頂級鋁合金龍頭)", "road": "科技一路", "address": "臺南市永康區科技一路8號", "lat": 23.0260, "lng": 120.2680, "industry": "金屬製品製造業", "contact": "航太鍛件處", "phone": "06-233-6888"}
        ],
        "roads": [
            {"name": "環工路", "weight": 65, "lat": (23.0280, 23.0350), "lng": (120.2600, 120.2680), "door_max": 160},
            {"name": "科技一路", "weight": 55, "lat": (23.0240, 23.0300), "lng": (120.2640, 120.2720), "door_max": 120},
            {"name": "科技二路", "weight": 50, "lat": (23.0260, 23.0320), "lng": (120.2660, 120.2740), "door_max": 100},
            {"name": "經建路", "weight": 45, "lat": (23.0290, 23.0360), "lng": (120.2580, 120.2650), "door_max": 90},
            {"name": "自強路", "weight": 40, "lat": (23.0330, 23.0400), "lng": (120.2560, 120.2630), "door_max": 140},
            {"name": "中正北路", "weight": 35, "lat": (23.0350, 23.0420), "lng": (120.2520, 120.2590), "door_max": 220}
        ]
    },
    "xinying": {
        "id": "xinying",
        "county_id": "tainan",
        "name": "新營工業區",
        "badge": "250 家",
        "center": [23.3150, 120.3050],
        "zoom": 14,
        "target_count": 250,
        "town": "新營區",
        "listed": [
            {"name": "榮剛材料科技股份有限公司 (台灣特殊鋼/航太鋼材龍頭)", "road": "新工路", "address": "臺南市新營區新工路35號", "lat": 23.3180, "lng": 120.3020, "industry": "金屬製品製造業", "contact": "鋼品業務處", "phone": "06-652-0031"},
            {"name": "生達化學製藥股份有限公司 (台灣學名藥大廠總部)", "road": "開元路", "address": "臺南市新營區開元路154號", "lat": 23.3120, "lng": 120.3100, "industry": "其他製造及服務業", "contact": "針劑/膜衣部", "phone": "06-636-6666"},
            {"name": "台鹽實業股份有限公司 (生技保健廠)", "road": "新工路", "address": "臺南市新營區新工路88號", "lat": 23.3160, "lng": 120.3040, "industry": "其他製造及服務業", "contact": "生技產品處", "phone": "06-652-3333"},
            {"name": "帝寶工業股份有限公司 (新營廠)", "road": "工業街", "address": "臺南市新營區工業街15號", "lat": 23.3140, "lng": 120.3060, "industry": "汽車及其零件製造業", "contact": "車燈組裝課", "phone": "06-652-5555"}
        ],
        "roads": [
            {"name": "新工路", "weight": 55, "lat": (23.3130, 23.3210), "lng": (120.3000, 120.3080), "door_max": 150},
            {"name": "工業街", "weight": 45, "lat": (23.3110, 23.3170), "lng": (120.3030, 120.3090), "door_max": 80},
            {"name": "開元路", "weight": 40, "lat": (23.3080, 23.3150), "lng": (120.3060, 120.3130), "door_max": 180},
            {"name": "新運路", "weight": 35, "lat": (23.3150, 23.3220), "lng": (120.3050, 120.3120), "door_max": 90}
        ]
    },
    "guantian": {
        "id": "guantian",
        "county_id": "tainan",
        "name": "官田工業區",
        "badge": "200 家",
        "center": [23.1850, 120.3320],
        "zoom": 15,
        "target_count": 200,
        "town": "官田區",
        "listed": [
            {"name": "宏遠興業股份有限公司 (機能性紡織全球大廠總部)", "road": "二鎮里", "address": "臺南市官田區二鎮里中山路二段256號", "lat": 23.1880, "lng": 120.3290, "industry": "化學材料與化學製品業", "contact": "智慧紡織處", "phone": "06-698-6121"},
            {"name": "天一藥廠股份有限公司 (中藥濃縮製劑指標大廠)", "road": "成功街", "address": "臺南市官田區成功街1號", "lat": 23.1830, "lng": 120.3350, "industry": "其他製造及服務業", "contact": "製劑品管部", "phone": "06-698-5800"},
            {"name": "台聯精化股份有限公司", "road": "工業路", "address": "臺南市官田區工業路22號", "lat": 23.1860, "lng": 120.3310, "industry": "化學材料與化學製品業", "contact": "特化業務處", "phone": "06-698-8888"},
            {"name": "聯友金屬科技股份有限公司 (稀有金屬鎢/鈷循環材料)", "road": "成功街", "address": "臺南市官田區成功街18號", "lat": 23.1840, "lng": 120.3360, "industry": "金屬製品製造業", "contact": "循環經濟組", "phone": "06-698-7654"}
        ],
        "roads": [
            {"name": "工業路", "weight": 55, "lat": (23.1820, 23.1900), "lng": (120.3280, 120.3350), "door_max": 120},
            {"name": "成功街", "weight": 45, "lat": (23.1800, 23.1870), "lng": (120.3310, 120.3380), "door_max": 90},
            {"name": "建業路", "weight": 35, "lat": (23.1830, 23.1890), "lng": (120.3260, 120.3320), "door_max": 80},
            {"name": "二鎮街", "weight": 30, "lat": (23.1860, 23.1920), "lng": (120.3270, 120.3330), "door_max": 100}
        ]
    }
}

# 3. 縣市階層定義 (未來可擴充新北、新竹、台中、彰化、高雄等)
COUNTIES_META = {
    "taoyuan": {
        "id": "taoyuan",
        "name": "桃園市",
        "icon": "🏢",
        "badge": "7 大園區",
        "default_park": "zhongli",
        "center": [24.9818, 121.2385],
        "zoom": 13,
        "parks": ["zhongli", "guishan", "huaya", "pingzhen", "guanyin", "dayuan", "youshi"]
    },
    "miaoli": {
        "id": "miaoli",
        "name": "苗栗縣",
        "icon": "⛰️",
        "badge": "4 大園區",
        "default_park": "zhunan_sci",
        "center": [24.6850, 120.8980],
        "zoom": 13,
        "parks": ["zhunan_sci", "tongluo_sci", "toufen", "zhunan_ind"]
    },
    "tainan": {
        "id": "tainan",
        "name": "臺南市",
        "icon": "☀️",
        "badge": "6 大園區",
        "default_park": "stsp_tainan",
        "center": [23.0500, 120.2200],
        "zoom": 12,
        "parks": ["stsp_tainan", "ttip_tainan", "anping", "yongkang", "xinying", "guantian"]
    }
}

all_parks_export = {}

# 將桃園 7 大園區注入，並補上 county_id
for pid, pdata in taoyuan_parks.items():
    pdata["county_id"] = "taoyuan"
    all_parks_export[pid] = pdata

print(f"[TAOYUAN] 成功載入既有桃園 7 園區共 {sum(len(p['clients']) for p in taoyuan_parks.values())} 家廠商。")

# 批量生成苗栗與台南各園區
start_id = 10000

def generate_park_clients(configs, county_name):
    global start_id
    for pid, cfg in configs.items():
        target = cfg["target_count"]
        clients = []
        
        # 1. 加入指標上市櫃大廠
        for l in cfg["listed"]:
            clients.append({
                "id": start_id,
                "name": l["name"],
                "road": l["road"],
                "address": l["address"],
                "lat": l["lat"],
                "lng": l["lng"],
                "industry": l["industry"],
                "is_listed": "是",
                "status": "尚未拜訪",
                "contact": l.get("contact", "廠務部"),
                "phone": l.get("phone", "037-xxx-xxxx" if "苗栗" in county_name else "06-xxx-xxxx"),
                "notes": "上市櫃指標企業 · 重點巡訪大廠",
                "visit_logs": []
            })
            start_id += 1

        # 2. 隨機填滿至目標家數
        needed = target - len(clients)
        road_pool = []
        for r in cfg["roads"]:
            road_pool.extend([r] * r["weight"])

        used_names = set(c["name"] for c in clients)
        town = cfg["town"]

        for _ in range(needed):
            rinfo = random.choice(road_pool)
            rname = rinfo["name"]
            door_no = random.randint(1, rinfo["door_max"])
            lat = round(random.uniform(*rinfo["lat"]), 5)
            lng = round(random.uniform(*rinfo["lng"]), 5)
            ind = random.choice(INDUSTRIES)

            while True:
                p = random.choice(PREFIXES)
                m = random.choice(MIDDLES)
                suffix = random.choice(["股份有限公司", "有限公司", "實業廠", "工廠"])
                name = f"{p}{m}{suffix}"
                if name not in used_names:
                    used_names.add(name)
                    break

            phone_prefix = "037" if "苗栗" in county_name else "06"
            phone_num = f"{phone_prefix}-{random.randint(200, 699)}-{random.randint(1000, 9999)}"

            clients.append({
                "id": start_id,
                "name": name,
                "road": rname,
                "address": f"{county_name}{town}{rname}{door_no}號",
                "lat": lat,
                "lng": lng,
                "industry": ind,
                "is_listed": "否",
                "status": "尚未拜訪",
                "contact": random.choice(["陳廠長", "林經理", "王協理", "張課長", "李主任", "採購部", "總機"]),
                "phone": phone_num,
                "notes": "",
                "visit_logs": []
            })
            start_id += 1

        cfg["clients"] = clients
        all_parks_export[pid] = cfg
        print(f"[{cfg['county_id'].upper()}] {cfg['name']} 生成完成：{len(clients)} 家廠商。")

generate_park_clients(MIAOLI_CONFIG, "苗栗縣")
generate_park_clients(TAINAN_CONFIG, "臺南市")

# 總體結構包含 counties 列表與 parks 詳情
database_bundle = {
    "counties": COUNTIES_META,
    "parks": all_parks_export
}

total_companies = sum(len(p["clients"]) for p in all_parks_export.values())
print("==================================================================")
print("[OK] 全台三大核心縣市資料庫生成完畢！")
print(f"- 涵蓋縣市：桃園市(7園區)、苗栗縣(4園區)、臺南市(6園區) 共 17 大園區")
print(f"- 收錄廠商總數：{total_companies} 家")
print("==================================================================")

with open('taiwan_parks_database.json', 'w', encoding='utf-8') as f:
    json.dump(database_bundle, f, ensure_ascii=False)

print("已成功儲存：taiwan_parks_database.json")
