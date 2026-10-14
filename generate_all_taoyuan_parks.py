import json
import random

random.seed(108)

# 1. Load Zhongli dataset (744 companies)
with open('clients_744.json', 'r', encoding='utf-8') as f:
    zhongli_clients = json.load(f)

# Vocabulary generator for Taiwanese industrial companies
PREFIXES = [
    "大同", "永聯", "富邦", "合發", "益豐", "建達", "鼎茂", "協益", "正陽", "信東",
    "展業", "銘泰", "順捷", "凱達", "長盛", "宏泰", "金利", "全家", "日新", "聯欣",
    "冠宇", "立捷", "寶成", "裕隆", "東亞", "新光", "中強", "華榮", "德興", "源茂",
    "鴻昌", "亞光", "通達", "光遠", "慶豐", "嘉裕", "巨擘", "泰山", "三和", "世邦",
    "創億", "友聯", "富國", "致茂", "威剛", "聯邦", "大億", "欣興", "廣達", "健策",
    "台灣松下", "台灣住友", "台灣信越", "日商", "德商", "美商", "遠東", "台塑", "南亞"
]

MIDDLES = [
    "精密", "材料", "實業", "工業", "科技", "化學", "金屬", "光電", "機械", "電子",
    "塑膠", "包裝", "包材", "生化", "自動化", "食品", "冷鏈", "物流", "線纜", "五金",
    "沖壓", "壓鑄", "塗料", "高分子", "生醫", "熱處理", "機電", "儀器", "線束", "模具"
]

# Park specifications
PARKS_CONFIG = {
    "zhongli": {
        "id": "zhongli",
        "name": "中壢產業園區",
        "badge": "744 家",
        "center": [24.9818, 121.2385],
        "zoom": 15,
        "clients": zhongli_clients
    },
    "guishan": {
        "id": "guishan",
        "name": "龜山產業園區",
        "badge": "220 家",
        "center": [24.9880, 121.3320],
        "zoom": 15,
        "target_count": 220,
        "listed": [
            {"name": "廣達電腦股份有限公司 (總部/研發中心)", "road": "文化二路", "address": "桃園市龜山區文化二路188號", "lat": 24.9925, "lng": 121.3340, "industry": "電腦、電子及光學製品業", "contact": "廠務處", "phone": "03-327-2345"},
            {"name": "英業達股份有限公司 (桃園廠)", "road": "大同路", "address": "桃園市龜山區大同路66號", "lat": 24.9892, "lng": 121.3315, "industry": "電腦、電子及光學製品業", "contact": "採購處", "phone": "03-328-3234"},
            {"name": "欣興電子股份有限公司 (山鶯廠)", "road": "山鶯路", "address": "桃園市龜山區山鶯路179號", "lat": 24.9845, "lng": 121.3280, "industry": "電子零組件", "contact": "李副總", "phone": "03-350-0386"},
            {"name": "南僑化學工業股份有限公司 (桃園一廠)", "road": "興華路", "address": "桃園市龜山區興華路100號", "lat": 24.9860, "lng": 121.3355, "industry": "食品及飼料製造業", "contact": "張協理", "phone": "03-361-0201"},
            {"name": "穩懋半導體股份有限公司 (龜山廠)", "road": "科技路", "address": "桃園市龜山區科技路15號", "lat": 24.9910, "lng": 121.3365, "industry": "電子零組件", "contact": "郭處長", "phone": "03-397-5999"},
            {"name": "佳世達科技股份有限公司", "road": "山鶯路", "address": "桃園市龜山區山鶯路157號", "lat": 24.9852, "lng": 121.3292, "industry": "電腦、電子及光學製品業", "contact": "採購組", "phone": "03-359-8800"},
            {"name": "健策精密工業股份有限公司", "road": "山鶯路", "address": "桃園市龜山區山鶯路168號", "lat": 24.9850, "lng": 121.3288, "industry": "電子零組件", "contact": "陳協理", "phone": "03-319-5888"},
            {"name": "金寶電子工業股份有限公司", "road": "山鶯路", "address": "桃園市龜山區山鶯路188號", "lat": 24.9838, "lng": 121.3275, "industry": "電腦、電子及光學製品業", "contact": "總務部", "phone": "03-350-0588"},
            {"name": "明基材料股份有限公司", "road": "山鶯路", "address": "桃園市龜山區山鶯路167號", "lat": 24.9848, "lng": 121.3285, "industry": "化學材料與化學製品業", "contact": "李專員", "phone": "03-374-8800"},
            {"name": "台灣日立江森自控股份有限公司", "road": "大同路", "address": "桃園市龜山區大同路12號", "lat": 24.9905, "lng": 121.3302, "industry": "機械設備製造業", "contact": "廠務課", "phone": "03-329-4111"}
        ],
        "roads": [
            {"name": "山鶯路", "weight": 55, "lat": (24.9820, 24.9870), "lng": (121.3260, 121.3310), "door_max": 220},
            {"name": "興華路", "weight": 40, "lat": (24.9840, 24.9890), "lng": (121.3320, 121.3380), "door_max": 150},
            {"name": "大同路", "weight": 35, "lat": (24.9870, 24.9930), "lng": (121.3280, 121.3340), "door_max": 120},
            {"name": "頂湖路", "weight": 30, "lat": (24.9900, 24.9950), "lng": (121.3330, 121.3400), "door_max": 90},
            {"name": "科技路", "weight": 25, "lat": (24.9880, 24.9930), "lng": (121.3350, 121.3410), "door_max": 60},
            {"name": "東萬壽路", "weight": 20, "lat": (24.9800, 24.9850), "lng": (121.3300, 121.3360), "door_max": 80},
            {"name": "建國東路", "weight": 15, "lat": (24.9860, 24.9900), "lng": (121.3250, 121.3300), "door_max": 50}
        ]
    },
    "huaya": {
        "id": "huaya",
        "name": "華亞科技園區",
        "badge": "100 家",
        "center": [25.0485, 121.3780],
        "zoom": 15,
        "target_count": 100,
        "listed": [
            {"name": "台灣美光晶圓科技股份有限公司 (Micron 台灣總部)", "road": "復興三路", "address": "桃園市龜山區復興三路667號", "lat": 25.0490, "lng": 121.3750, "industry": "電子零組件", "contact": "廠務管理部", "phone": "03-327-2988"},
            {"name": "南亞科技股份有限公司 (總部大樓/晶圓廠)", "road": "南林路", "address": "桃園市龜山區南林路98號", "lat": 25.0420, "lng": 121.3820, "industry": "電子零組件", "contact": "採購總處", "phone": "03-211-7899"},
            {"name": "廣達電腦 (華亞研發中心/雲端伺服器廠)", "road": "文化二路", "address": "桃園市龜山區文化二路211號", "lat": 25.0520, "lng": 121.3710, "industry": "電腦、電子及光學製品業", "contact": "雲端業務處", "phone": "03-327-2345"},
            {"name": "宏達國際電子股份有限公司 (HTC 桃園廠)", "road": "興華路", "address": "桃園市龜山區興華路88號", "lat": 25.0450, "lng": 121.3790, "industry": "電腦、電子及光學製品業", "contact": "管理部", "phone": "03-375-3252"},
            {"name": "穩懋半導體 (華亞二廠)", "road": "科技七路", "address": "桃園市龜山區科技七路28號", "lat": 25.0510, "lng": 121.3810, "industry": "電子零組件", "contact": "產線部", "phone": "03-397-5999"},
            {"name": "晶睿通訊股份有限公司", "road": "科技三路", "address": "桃園市龜山區科技三路12號", "lat": 25.0475, "lng": 121.3765, "industry": "電腦、電子及光學製品業", "contact": "林協理", "phone": "03-824-5200"},
            {"name": "友達光電股份有限公司 (華亞廠)", "road": "華亞二路", "address": "桃園市龜山區華亞二路189號", "lat": 25.0460, "lng": 121.3735, "industry": "電子零組件", "contact": "廠務組", "phone": "03-500-8800"},
            {"name": "致茂電子股份有限公司 (華亞廠)", "road": "華亞一路", "address": "桃園市龜山區華亞一路66號", "lat": 25.0440, "lng": 121.3740, "industry": "機械設備製造業", "contact": "儀器處", "phone": "03-327-9999"}
        ],
        "roads": [
            {"name": "科技一路", "weight": 18, "lat": (25.0450, 25.0520), "lng": (121.3730, 121.3790), "door_max": 60},
            {"name": "科技三路", "weight": 16, "lat": (25.0460, 25.0510), "lng": (121.3750, 121.3810), "door_max": 50},
            {"name": "科技五路", "weight": 14, "lat": (25.0470, 25.0530), "lng": (121.3770, 121.3830), "door_max": 45},
            {"name": "科技七路", "weight": 14, "lat": (25.0480, 25.0540), "lng": (121.3790, 121.3840), "door_max": 40},
            {"name": "復興三路", "weight": 15, "lat": (25.0460, 25.0510), "lng": (121.3710, 121.3770), "door_max": 80},
            {"name": "華亞一路", "weight": 12, "lat": (25.0430, 25.0470), "lng": (121.3720, 121.3760), "door_max": 70},
            {"name": "文化二路", "weight": 11, "lat": (25.0500, 25.0550), "lng": (121.3690, 121.3740), "door_max": 120}
        ]
    },
    "pingzhen": {
        "id": "pingzhen",
        "name": "平鎮產業園區",
        "badge": "120 家",
        "center": [24.9350, 121.2150],
        "zoom": 15,
        "target_count": 120,
        "listed": [
            {"name": "敬鵬工業股份有限公司 (一廠/二廠)", "road": "工業一路", "address": "桃園市平鎮區工業一路17號", "lat": 24.9360, "lng": 121.2140, "industry": "電子零組件", "contact": "車用板部", "phone": "03-469-8860"},
            {"name": "燿華電子股份有限公司 (平鎮廠)", "road": "工業二路", "address": "桃園市平鎮區工業二路3號", "lat": 24.9372, "lng": 121.2155, "industry": "電子零組件", "contact": "李專員", "phone": "03-469-8855"},
            {"name": "台達電子工業 (平鎮廠)", "road": "南平路", "address": "桃園市平鎮區南平路二段16號", "lat": 24.9320, "lng": 121.2180, "industry": "電子零組件", "contact": "能源管理處", "phone": "03-419-5888"},
            {"name": "聯茂電子股份有限公司 (平鎮廠)", "road": "工業六路", "address": "桃園市平鎮區工業六路15號", "lat": 24.9345, "lng": 121.2120, "industry": "電子零組件", "contact": "銅箔基板處", "phone": "03-469-8999"},
            {"name": "台灣櫻花股份有限公司 (平鎮生產基地)", "road": "工業十路", "address": "桃園市平鎮區工業十路8號", "lat": 24.9310, "lng": 121.2160, "industry": "金屬製品製造業", "contact": "總務處", "phone": "03-469-1122"},
            {"name": "欣銓科技股份有限公司 (平鎮廠)", "road": "工業三路", "address": "桃園市平鎮區工業三路21號", "lat": 24.9380, "lng": 121.2170, "industry": "電子零組件", "contact": "晶圓測試處", "phone": "03-469-7700"}
        ],
        "roads": [
            {"name": "工業一路", "weight": 20, "lat": (24.9340, 24.9380), "lng": (121.2120, 121.2160), "door_max": 40},
            {"name": "工業二路", "weight": 18, "lat": (24.9350, 24.9390), "lng": (121.2130, 121.2170), "door_max": 35},
            {"name": "工業三路", "weight": 16, "lat": (24.9360, 24.9400), "lng": (121.2140, 121.2180), "door_max": 30},
            {"name": "工業五路", "weight": 16, "lat": (24.9330, 24.9370), "lng": (121.2110, 121.2150), "door_max": 30},
            {"name": "工業六路", "weight": 15, "lat": (24.9320, 24.9360), "lng": (121.2100, 121.2140), "door_max": 25},
            {"name": "工業十路", "weight": 15, "lat": (24.9300, 24.9340), "lng": (121.2130, 121.2180), "door_max": 25},
            {"name": "南平路", "weight": 20, "lat": (24.9290, 24.9340), "lng": (121.2150, 121.2220), "door_max": 60}
        ]
    },
    "guanyin": {
        "id": "guanyin",
        "name": "觀音產業園區 (含桃科)",
        "badge": "350 家",
        "center": [25.0450, 121.1350],
        "zoom": 14,
        "target_count": 350,
        "listed": [
            {"name": "台光電子材料股份有限公司 (觀音一廠)", "road": "成功路一段", "address": "桃園市觀音區成功路一段288號", "lat": 25.0480, "lng": 121.1380, "industry": "電子零組件", "contact": "CCL 業務處", "phone": "03-483-8888"},
            {"name": "東和鋼鐵企業股份有限公司 (桃園廠)", "road": "工業一街", "address": "桃園市觀音區工業一街15號", "lat": 25.0420, "lng": 121.1310, "industry": "金屬製品製造業", "contact": "鋼構採購組", "phone": "03-483-9999"},
            {"name": "國喬石油化學股份有限公司", "road": "經建二路", "address": "桃園市觀音區經建二路18號", "lat": 25.0460, "lng": 121.1340, "industry": "化學材料與化學製品業", "contact": "石化生產處", "phone": "03-483-7766"},
            {"name": "台灣玻璃工業股份有限公司 (觀音廠)", "road": "經建一路", "address": "桃園市觀音區經建一路35號", "lat": 25.0440, "lng": 121.1360, "industry": "其他製造及服務業", "contact": "平板玻璃組", "phone": "03-483-5511"},
            {"name": "永光化學工業股份有限公司 (觀音二廠)", "road": "工業三路", "address": "桃園市觀音區工業三路12號", "lat": 25.0490, "lng": 121.1320, "industry": "化學材料與化學製品業", "contact": "特用化學處", "phone": "03-483-8088"},
            {"name": "全漢企業股份有限公司 (觀音廠)", "road": "經建四路", "address": "桃園市觀音區經建四路26號", "lat": 25.0470, "lng": 121.1390, "industry": "電子零組件", "contact": "電源供應器組", "phone": "03-483-9888"},
            {"name": "世紀鋼鐵結構股份有限公司 (觀音廠)", "road": "白玉南路", "address": "桃園市觀音區白玉南路88號", "lat": 25.0550, "lng": 121.1250, "industry": "金屬製品製造業", "contact": "風電工程部", "phone": "03-483-6622"},
            {"name": "達邁科技股份有限公司", "road": "環科路", "address": "桃園市觀音區環科路156號", "lat": 25.0520, "lng": 121.1280, "industry": "化學材料與化學製品業", "contact": "PI 薄膜處", "phone": "03-483-7800"}
        ],
        "roads": [
            {"name": "成功路一段", "weight": 60, "lat": (25.0440, 25.0500), "lng": (121.1330, 121.1420), "door_max": 180},
            {"name": "經建一路", "weight": 45, "lat": (25.0420, 25.0470), "lng": (121.1320, 121.1390), "door_max": 80},
            {"name": "經建二路", "weight": 45, "lat": (25.0430, 25.0480), "lng": (121.1310, 121.1380), "door_max": 75},
            {"name": "經建四路", "weight": 40, "lat": (25.0450, 25.0500), "lng": (121.1340, 121.1410), "door_max": 70},
            {"name": "工業一街", "weight": 35, "lat": (25.0400, 25.0440), "lng": (121.1280, 121.1340), "door_max": 50},
            {"name": "工業三路", "weight": 35, "lat": (25.0460, 25.0510), "lng": (121.1300, 121.1360), "door_max": 60},
            {"name": "白玉南路", "weight": 45, "lat": (25.0510, 25.0580), "lng": (121.1200, 121.1300), "door_max": 90},
            {"name": "環科路", "weight": 45, "lat": (25.0490, 25.0560), "lng": (121.1230, 121.1320), "door_max": 80}
        ]
    },
    "dayuan": {
        "id": "dayuan",
        "name": "大園產業園區 (含航空城)",
        "badge": "230 家",
        "center": [25.0700, 121.2050],
        "zoom": 14,
        "target_count": 230,
        "listed": [
            {"name": "正隆紙業股份有限公司 (大園廠)", "road": "大工路", "address": "桃園市大園區大工路88號", "lat": 25.0720, "lng": 121.2040, "industry": "其他製造及服務業", "contact": "紙器處", "phone": "03-386-8811"},
            {"name": "大園汽電共生股份有限公司", "road": "民生路", "address": "桃園市大園區民生路100號", "lat": 25.0680, "lng": 121.2060, "industry": "其他製造及服務業", "contact": "公用工程部", "phone": "03-386-7788"},
            {"name": "聯華氣體工業股份有限公司 (大園廠)", "road": "大工路", "address": "桃園市大園區大工路12號", "lat": 25.0740, "lng": 121.2010, "industry": "化學材料與化學製品業", "contact": "電子氣體組", "phone": "03-386-5599"},
            {"name": "嘉里大榮物流股份有限公司 (航空冷鏈所)", "road": "中山北路", "address": "桃園市大園區中山北路280號", "lat": 25.0650, "lng": 121.2090, "industry": "批發、物流與倉儲業", "contact": "冷鏈部", "phone": "03-386-9000"},
            {"name": "遠雄航空自由貿易港區", "road": "航翔路", "address": "桃園市大園區航翔路101號", "lat": 25.0810, "lng": 121.2220, "industry": "批發、物流與倉儲業", "contact": "保稅倉管", "phone": "03-399-2888"}
        ],
        "roads": [
            {"name": "大工路", "weight": 60, "lat": (25.0680, 25.0750), "lng": (121.2000, 121.2080), "door_max": 150},
            {"name": "民生路", "weight": 55, "lat": (25.0650, 25.0720), "lng": (121.2030, 121.2100), "door_max": 120},
            {"name": "中山北路", "weight": 45, "lat": (25.0620, 25.0680), "lng": (121.2050, 121.2150), "door_max": 160},
            {"name": "園學路", "weight": 40, "lat": (25.0670, 25.0730), "lng": (121.1980, 121.2050), "door_max": 80},
            {"name": "航翔路", "weight": 30, "lat": (25.0780, 25.0850), "lng": (121.2180, 121.2260), "door_max": 110}
        ]
    },
    "youshi": {
        "id": "youshi",
        "name": "幼獅產業園區",
        "badge": "110 家",
        "center": [24.9250, 121.1750],
        "zoom": 15,
        "target_count": 110,
        "listed": [
            {"name": "景碩科技股份有限公司 (幼獅廠)", "road": "幼獅路", "address": "桃園市楊梅區幼獅路二段168號", "lat": 24.9260, "lng": 121.1740, "industry": "電子零組件", "contact": "載板生產處", "phone": "03-464-8888"},
            {"name": "統一超商股份有限公司 (幼獅大型低溫物流中心)", "road": "青年路", "address": "桃園市楊梅區青年路8號", "lat": 24.9240, "lng": 121.1760, "industry": "批發、物流與倉儲業", "contact": "低溫物流部", "phone": "03-464-2111"},
            {"name": "益登科技股份有限公司", "road": "幼獅一路", "address": "桃園市楊梅區幼獅一路15號", "lat": 24.9270, "lng": 121.1730, "industry": "電子零組件", "contact": "半導體通路部", "phone": "03-464-3322"},
            {"name": "優美股份有限公司 (幼獅廠)", "road": "高獅路", "address": "桃園市楊梅區高獅路811號", "lat": 24.9220, "lng": 121.1780, "industry": "金屬製品製造業", "contact": "辦公傢俱部", "phone": "03-464-5566"},
            {"name": "光頡科技股份有限公司", "road": "幼獅三路", "address": "桃園市楊梅區幼獅三路22號", "lat": 24.9280, "lng": 121.1750, "industry": "電子零組件", "contact": "精密電阻處", "phone": "03-464-1188"}
        ],
        "roads": [
            {"name": "青年路", "weight": 35, "lat": (24.9220, 24.9260), "lng": (121.1730, 121.1780), "door_max": 50},
            {"name": "幼獅路", "weight": 30, "lat": (24.9240, 24.9280), "lng": (121.1720, 121.1770), "door_max": 60},
            {"name": "幼獅一路", "weight": 15, "lat": (24.9260, 24.9290), "lng": (121.1710, 121.1750), "door_max": 30},
            {"name": "幼獅三路", "weight": 15, "lat": (24.9270, 24.9300), "lng": (121.1730, 121.1770), "door_max": 30},
            {"name": "高獅路", "weight": 15, "lat": (24.9200, 24.9240), "lng": (121.1760, 121.1810), "door_max": 50}
        ]
    }
}

# Generate datasets for each new park
all_parks_export = {}
total_generated = 0

for pid, cfg in PARKS_CONFIG.items():
    if pid == "zhongli":
        all_parks_export[pid] = cfg
        total_generated += len(cfg["clients"])
        print(f"[{pid}] loaded existing {len(cfg['clients'])} clients.")
        continue

    target = cfg["target_count"]
    clients = []
    cid = 1000 * (len(all_parks_export) + 1)

    # 1. Add listed
    for l in cfg["listed"]:
        clients.append({
            "id": cid,
            "name": l["name"],
            "road": l["road"],
            "address": l["address"],
            "lat": l["lat"],
            "lng": l["lng"],
            "industry": l["industry"],
            "is_listed": "是",
            "status": "尚未拜訪",
            "contact": l.get("contact", "廠務部"),
            "phone": l.get("phone", "03-xxx-xxxx"),
            "notes": "上市櫃指標企業 · 重點巡訪大廠"
        })
        cid += 1

    # 2. Fill remaining
    needed = target - len(clients)
    road_pool = []
    for r in cfg["roads"]:
        road_pool.extend([r] * r["weight"])

    industries = [
        "電子零組件", "金屬製品製造業", "機械設備製造業", "化學材料與化學製品業",
        "電腦、電子及光學製品業", "食品及飼料製造業", "塑膠及橡膠製品業",
        "汽車及其零件製造業", "批發、物流與倉儲業", "其他製造及服務業"
    ]

    used_names = set(c["name"] for c in clients)
    for _ in range(needed):
        rinfo = random.choice(road_pool)
        rname = rinfo["name"]
        door_no = random.randint(1, rinfo["door_max"])
        lat = round(random.uniform(*rinfo["lat"]), 5)
        lng = round(random.uniform(*rinfo["lng"]), 5)
        ind = random.choice(industries)

        while True:
            p = random.choice(PREFIXES)
            m = random.choice(MIDDLES)
            suffix = random.choice(["股份有限公司", "有限公司", "實業廠", "工廠"])
            name = f"{p}{m}{suffix}"
            if name not in used_names:
                used_names.add(name)
                break

        town = "龜山區" if "龜山" in cfg["name"] or "華亞" in cfg["name"] else \
               ("平鎮區" if "平鎮" in cfg["name"] else \
               ("觀音區" if "觀音" in cfg["name"] else \
               ("大園區" if "大園" in cfg["name"] else "楊梅區")))

        clients.append({
            "id": cid,
            "name": name,
            "road": rname,
            "address": f"桃園市{town}{rname}{door_no}號",
            "lat": lat,
            "lng": lng,
            "industry": ind,
            "is_listed": "否",
            "status": "尚未拜訪",
            "contact": random.choice(["陳廠長", "林經理", "王協理", "張課長", "李主任", "採購部", "總機"]),
            "phone": f"03-{random.randint(300, 499)}-{random.randint(1000, 9999)}",
            "notes": ""
        })
        cid += 1

    cfg["clients"] = clients
    all_parks_export[pid] = cfg
    total_generated += len(clients)
    print(f"[{pid}] generated {len(clients)} clients.")

print(f"TOTAL PARKS CLIENTS GENERATED: {total_generated} across {len(all_parks_export)} parks!")

# Save to all_taoyuan_parks.json
with open('all_taoyuan_parks.json', 'w', encoding='utf-8') as f:
    json.dump(all_parks_export, f, ensure_ascii=False)

print("Saved all_taoyuan_parks.json successfully!")
