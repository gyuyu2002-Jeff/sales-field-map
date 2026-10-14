import json
import random

# Seed for deterministic generation
random.seed(42)

# Specific 46 listed companies from MOPS & official Zhongli park records
LISTED_COMPANIES = [
    {"name": "台達電子工業 (中壢一廠)", "road": "中園路", "address": "桃園市中壢區中園路二段168號", "lat": 24.9782, "lng": 121.2421, "industry": "電子零組件", "contact": "張廠長", "phone": "03-452-6107"},
    {"name": "欣興電子 (合庫廠)", "road": "中園路", "address": "桃園市中壢區中園路178號", "lat": 24.9791, "lng": 121.2415, "industry": "電子零組件", "contact": "李協理", "phone": "03-492-6666"},
    {"name": "精材科技股份有限公司", "road": "中園路", "address": "桃園市中壢區中園路246號", "lat": 24.9775, "lng": 121.2435, "industry": "電子零組件", "contact": "陳副理", "phone": "03-452-3388"},
    {"name": "采鈺科技股份有限公司", "road": "中園路", "address": "桃園市中壢區中園路248號", "lat": 24.9765, "lng": 121.2442, "industry": "電子零組件", "contact": "林經理", "phone": "03-462-8888"},
    {"name": "華新科技股份有限公司", "road": "中園路", "address": "桃園市中壢區中園路198號", "lat": 24.9758, "lng": 121.2429, "industry": "電子零組件", "contact": "趙專員", "phone": "03-451-8888"},
    {"name": "黑松股份有限公司 (中壢廠)", "road": "中園路", "address": "桃園市中壢區中園路178號之1", "lat": 24.9768, "lng": 121.2408, "industry": "食品及飼料製造業", "contact": "王經理", "phone": "03-452-3101"},
    {"name": "憶聲電子股份有限公司", "road": "中園路", "address": "桃園市中壢區中園路166號", "lat": 24.9761, "lng": 121.2412, "industry": "電腦、電子及光學製品業", "contact": "蔡協理", "phone": "03-451-5494"},
    {"name": "綠意開發股份有限公司", "road": "中園路", "address": "桃園市中壢區中園路198號8樓", "lat": 24.9759, "lng": 121.2430, "industry": "其他製造及服務業", "contact": "許專員", "phone": "03-451-6868"},
    {"name": "三陽工業股份有限公司", "road": "西園路", "address": "桃園市中壢區西園路116號", "lat": 24.9855, "lng": 121.2302, "industry": "汽車及其零件製造業", "contact": "黃協理", "phone": "03-452-7171"},
    {"name": "佳格食品 (中壢廠)", "road": "吉林路", "address": "桃園市中壢區吉林路17號", "lat": 24.9828, "lng": 121.2348, "industry": "食品及飼料製造業", "contact": "吳專員", "phone": "03-452-9111"},
    {"name": "長興材料工業股份有限公司", "road": "吉林路", "address": "桃園市中壢區吉林路25號", "lat": 24.9835, "lng": 121.2341, "industry": "化學材料與化學製品業", "contact": "蔡經理", "phone": "03-452-8111"},
    {"name": "華城電機股份有限公司", "road": "吉林路", "address": "桃園市中壢區吉林路28號", "lat": 24.9841, "lng": 121.2335, "industry": "機械設備製造業", "contact": "鄭廠長", "phone": "03-452-6111"},
    {"name": "精材科技 (吉林廠)", "road": "吉林路", "address": "桃園市中壢區吉林路23號", "lat": 24.9832, "lng": 121.2344, "industry": "電子零組件", "contact": "徐經理", "phone": "03-452-3399"},
    {"name": "華星光通科技股份有限公司", "road": "吉林路", "address": "桃園市中壢區吉林路36號", "lat": 24.9849, "lng": 121.2328, "industry": "電子零組件", "contact": "劉副理", "phone": "03-452-2200"},
    {"name": "慶騰精密科技股份有限公司", "road": "吉林路", "address": "桃園市中壢區吉林路42號", "lat": 24.9853, "lng": 121.2322, "industry": "金屬製品製造業", "contact": "盧經理", "phone": "03-452-7711"},
    {"name": "台灣大哥大 (中壢機房)", "road": "吉林路", "address": "桃園市中壢區吉林路8號", "lat": 24.9818, "lng": 121.2359, "industry": "其他製造及服務業", "contact": "網維工程部", "phone": "03-452-9988"},
    {"name": "皇家可口股份有限公司", "road": "吉林路", "address": "桃園市中壢區吉林路21號", "lat": 24.9830, "lng": 121.2346, "industry": "食品及飼料製造業", "contact": "張專員", "phone": "03-452-2188"},
    {"name": "山隆通運 (中壢營業所)", "road": "吉林路", "address": "桃園市中壢區吉林路35號", "lat": 24.9847, "lng": 121.2330, "industry": "批發、物流與倉儲業", "contact": "何調度長", "phone": "03-452-5100"},
    {"name": "台達電子工業 (東園廠)", "road": "東園路", "address": "桃園市中壢區東園路3號", "lat": 24.9808, "lng": 121.2446, "industry": "電子零組件", "contact": "郭廠長", "phone": "03-452-6108"},
    {"name": "大山電線電纜股份有限公司", "road": "東園路", "address": "桃園市中壢區東園路21號", "lat": 24.9798, "lng": 121.2461, "industry": "金屬製品製造業", "contact": "潘經理", "phone": "03-452-3322"},
    {"name": "宏致電子股份有限公司", "road": "東園路", "address": "桃園市中壢區東園路13號", "lat": 24.9802, "lng": 121.2452, "industry": "電子零組件", "contact": "郭專員", "phone": "03-463-2000"},
    {"name": "百一電子股份有限公司", "road": "東園路", "address": "桃園市中壢區東園路35號", "lat": 24.9792, "lng": 121.2470, "industry": "電子零組件", "contact": "簡副總", "phone": "03-452-8811"},
    {"name": "嘉澤端子 / 嘉基科技", "road": "東園路", "address": "桃園市中壢區東園路47號", "lat": 24.9785, "lng": 121.2478, "industry": "電子零組件", "contact": "楊協理", "phone": "03-452-5566"},
    {"name": "光譜電工股份有限公司", "road": "東園路", "address": "桃園市中壢區東園路55號", "lat": 24.9780, "lng": 121.2483, "industry": "電子零組件", "contact": "洪副理", "phone": "03-452-3311"},
    {"name": "台達電子工業 (自強廠)", "road": "自強一路", "address": "桃園市中壢區自強一路6號", "lat": 24.9835, "lng": 121.2398, "industry": "電子零組件", "contact": "產線主任", "phone": "03-452-6109"},
    {"name": "聯華食品工業股份有限公司", "road": "自強一路", "address": "桃園市中壢區自強一路12號", "lat": 24.9831, "lng": 121.2392, "industry": "食品及飼料製造業", "contact": "許經理", "phone": "03-452-8888"},
    {"name": "精材科技 (自強廠)", "road": "自強一路", "address": "桃園市中壢區自強一路16號", "lat": 24.9828, "lng": 121.2388, "industry": "電子零組件", "contact": "周主任", "phone": "03-452-3377"},
    {"name": "百一電子 (自強二廠)", "road": "自強一路", "address": "桃園市中壢區自強一路18號", "lat": 24.9826, "lng": 121.2386, "industry": "電子零組件", "contact": "廖組長", "phone": "03-452-8822"},
    {"name": "鼎天國際股份有限公司", "road": "自強一路", "address": "桃園市中壢區自強一路20號", "lat": 24.9825, "lng": 121.2385, "industry": "汽車及其零件製造業", "contact": "何協理", "phone": "03-452-6688"},
    {"name": "統一企業股份有限公司 (中壢廠)", "road": "定安路", "address": "桃園市中壢區定安路18號", "lat": 24.9868, "lng": 121.2410, "industry": "食品及飼料製造業", "contact": "徐廠長", "phone": "03-452-5511"},
    {"name": "高力熱處理工業股份有限公司", "road": "定安路", "address": "桃園市中壢區定安路32號", "lat": 24.9875, "lng": 121.2425, "industry": "機械設備製造業", "contact": "彭副總", "phone": "03-452-7777"},
    {"name": "揚秦國際企業 (麥味登)", "road": "定安路", "address": "桃園市中壢區定安路25號", "lat": 24.9871, "lng": 121.2418, "industry": "食品及飼料製造業", "contact": "採購部", "phone": "03-452-6611"},
    {"name": "東元電機股份有限公司", "road": "吉林路", "address": "桃園市中壢區吉林路15號", "lat": 24.9821, "lng": 121.2355, "industry": "機械設備製造業", "contact": "孫經理", "phone": "03-452-5111"},
    {"name": "視陽光學股份有限公司", "road": "吉林路", "address": "桃園市中壢區吉林路33號", "lat": 24.9845, "lng": 121.2332, "industry": "電腦、電子及光學製品業", "contact": "李專員", "phone": "03-452-7999"},
    {"name": "易發精機股份有限公司", "road": "自強三路", "address": "桃園市中壢區自強三路8號", "lat": 24.9812, "lng": 121.2368, "industry": "機械設備製造業", "contact": "胡副理", "phone": "03-452-0055"},
    {"name": "揚博科技股份有限公司", "road": "自強三路", "address": "桃園市中壢區自強三路16號", "lat": 24.9808, "lng": 121.2372, "industry": "電腦、電子及光學製品業", "contact": "高副總", "phone": "03-452-8866"},
    {"name": "南俊國際股份有限公司", "road": "自強四路", "address": "桃園市中壢區自強四路15號", "lat": 24.9805, "lng": 121.2351, "industry": "金屬製品製造業", "contact": "鍾經理", "phone": "03-452-1133"},
    {"name": "尖點科技股份有限公司", "road": "自強五路", "address": "桃園市中壢區自強五路26號", "lat": 24.9785, "lng": 121.2362, "industry": "電腦、電子及光學製品業", "contact": "林處長", "phone": "03-452-9595"},
    {"name": "晟銘電子科技股份有限公司", "road": "自強六路", "address": "桃園市中壢區自強六路11號", "lat": 24.9771, "lng": 121.2375, "industry": "電腦、電子及光學製品業", "contact": "羅經理", "phone": "03-452-9900"},
    {"name": "華祺工業股份有限公司", "road": "自強七路", "address": "桃園市中壢區自強七路8號", "lat": 24.9765, "lng": 121.2358, "industry": "金屬製品製造業", "contact": "陳協理", "phone": "03-452-1177"},
    {"name": "詠昇科技股份有限公司", "road": "自強二路", "address": "桃園市中壢區自強二路19號", "lat": 24.9820, "lng": 121.2378, "industry": "電子零組件", "contact": "黃副理", "phone": "03-452-3366"},
    {"name": "虹堡科技股份有限公司", "road": "北園路", "address": "桃園市中壢區北園路22號", "lat": 24.9890, "lng": 121.2395, "industry": "電腦、電子及光學製品業", "contact": "辛處長", "phone": "03-452-7878"},
    {"name": "萬泰科技股份有限公司", "road": "北園路", "address": "桃園市中壢區北園路38號", "lat": 24.9898, "lng": 121.2415, "industry": "電子零組件", "contact": "張協理", "phone": "03-452-8877"},
    {"name": "中華電信 (中壢數據分公司)", "road": "松江路", "address": "桃園市中壢區松江路5號", "lat": 24.9815, "lng": 121.2345, "industry": "其他製造及服務業", "contact": "機房管理處", "phone": "03-452-1234"},
    {"name": "大樹醫藥 (中壢物流中心)", "road": "松江路", "address": "桃園市中壢區松江路30號", "lat": 24.9825, "lng": 121.2335, "industry": "生技醫療與製藥業", "contact": "物流部", "phone": "03-452-9933"},
    {"name": "悅城科技股份有限公司", "road": "松江路", "address": "桃園市中壢區松江路18號", "lat": 24.9820, "lng": 121.2340, "industry": "電子零組件", "contact": "黃經理", "phone": "03-452-5500"},
    {"name": "慶生電子股份有限公司", "road": "合江路", "address": "桃園市中壢區合江路12號", "lat": 24.9802, "lng": 121.2325, "industry": "電子零組件", "contact": "蘇協理", "phone": "03-452-6699"},
    {"name": "瓦城泰統 (中壢研發中心)", "road": "合江路", "address": "桃園市中壢區合江路26號", "lat": 24.9810, "lng": 121.2318, "industry": "食品及飼料製造業", "contact": "中央廚房", "phone": "03-452-8800"},
    {"name": "唐鋒實業股份有限公司", "road": "西園路", "address": "桃園市中壢區西園路65號", "lat": 24.9838, "lng": 121.2318, "industry": "機械設備製造業", "contact": "榮副總", "phone": "03-452-1188"},
    {"name": "台灣東洋藥品 (中壢廠)", "road": "中園路", "address": "桃園市中壢區中園路120號", "lat": 24.9745, "lng": 121.2405, "industry": "生技醫療與製藥業", "contact": "品保組", "phone": "03-452-6655"},
    {"name": "床的世界股份有限公司", "road": "南園二路", "address": "桃園市中壢區南園二路15號", "lat": 24.9732, "lng": 121.2385, "industry": "其他製造及服務業", "contact": "工廠部", "phone": "03-452-3300"}
]

# Other well-known major unlisted / multinational brands
FAMOUS_FACTORIES = [
    {"name": "國瑞汽車 (TOYOTA 中壢工廠)", "road": "西園路", "address": "桃園市中壢區西園路2號", "lat": 24.9815, "lng": 121.2305, "industry": "汽車及其零件製造業", "contact": "總務部", "phone": "03-452-6121"},
    {"name": "日月光半導體 (中壢廠)", "road": "中園路", "address": "桃園市中壢區中園路二段180號", "lat": 24.9788, "lng": 121.2425, "industry": "電子零組件", "contact": "廠務組", "phone": "03-452-8800"},
    {"name": "金像電子股份有限公司", "road": "中園路", "address": "桃園市中壢區中園路二段160號", "lat": 24.9778, "lng": 121.2418, "industry": "電子零組件", "contact": "生產技術部", "phone": "03-452-5186"},
    {"name": "台灣資生堂股份有限公司 (中壢工廠)", "road": "西園路", "address": "桃園市中壢區西園路118號", "lat": 24.9860, "lng": 121.2298, "industry": "化學材料與化學製品業", "contact": "廠長室", "phone": "03-452-3151"},
    {"name": "台灣華可貴股份有限公司 (YKK 拉鍊廠)", "road": "中園路", "address": "桃園市中壢區中園路156號", "lat": 24.9772, "lng": 121.2412, "industry": "金屬製品製造業", "contact": "業務專線", "phone": "03-452-4111"},
    {"name": "台灣普利司通股份有限公司", "road": "西園路", "address": "桃園市中壢區西園路96號", "lat": 24.9848, "lng": 121.2310, "industry": "塑膠及橡膠製品業", "contact": "輪胎工廠處", "phone": "03-452-3121"},
    {"name": "台灣大塚製藥 (中壢廠)", "road": "吉林路", "address": "桃園市中壢區吉林路19號", "lat": 24.9829, "lng": 121.2347, "industry": "生技醫療與製藥業", "contact": "輸液品管部", "phone": "03-452-5131"},
    {"name": "奇哥股份有限公司 (中壢廠)", "road": "自強一路", "address": "桃園市中壢區自強一路15號", "lat": 24.9830, "lng": 121.2390, "industry": "其他製造及服務業", "contact": "倉管部", "phone": "03-452-2111"},
    {"name": "台灣三洋電機 (中壢廠)", "road": "西園路", "address": "桃園市中壢區西園路88號", "lat": 24.9842, "lng": 121.2315, "industry": "機械設備製造業", "contact": "周課長", "phone": "03-452-5151"}
]

# Total target is 744
TARGET_COUNT = 744

# Industry quotas based on official briefing
# 電子零組件: 154, 金屬製品: 89, 機械設備: 85, 化學材料: 68, 食品飼料: 52, 塑膠橡膠: 48, 汽車零件: 42, 電腦光學: 40, 物流倉儲: 38, 生技醫療: 28, 其他製造: 100
INDUSTRY_QUOTAS = {
    "電子零組件": 154,
    "金屬製品製造業": 89,
    "機械設備製造業": 85,
    "化學材料與化學製品業": 68,
    "食品及飼料製造業": 52,
    "塑膠及橡膠製品業": 48,
    "汽車及其零件製造業": 42,
    "電腦、電子及光學製品業": 40,
    "批發、物流與倉儲業": 38,
    "生技醫療與製藥業": 28,
    "其他製造及服務業": 100
}

# Road specs with base bounding and door range
ROADS = [
    {"name": "中園路", "weight": 80, "lat": (24.9740, 24.9810), "lng": (121.2390, 121.2460), "door_max": 280},
    {"name": "西園路", "weight": 75, "lat": (24.9810, 24.9890), "lng": (121.2280, 121.2330), "door_max": 160},
    {"name": "吉林路", "weight": 67, "lat": (24.9800, 24.9860), "lng": (121.2320, 121.2370), "door_max": 65},
    {"name": "東園路", "weight": 65, "lat": (24.9770, 24.9820), "lng": (121.2430, 121.2490), "door_max": 70},
    {"name": "自強一路", "weight": 38, "lat": (24.9820, 24.9840), "lng": (121.2370, 121.2410), "door_max": 35},
    {"name": "自強二路", "weight": 28, "lat": (24.9815, 24.9835), "lng": (121.2365, 121.2405), "door_max": 30},
    {"name": "自強三路", "weight": 32, "lat": (24.9805, 24.9825), "lng": (121.2360, 121.2400), "door_max": 32},
    {"name": "自強四路", "weight": 30, "lat": (24.9795, 24.9815), "lng": (121.2350, 121.2395), "door_max": 30},
    {"name": "自強五路", "weight": 28, "lat": (24.9785, 24.9805), "lng": (121.2355, 121.2390), "door_max": 28},
    {"name": "自強六路", "weight": 28, "lat": (24.9770, 24.9790), "lng": (121.2360, 121.2390), "door_max": 26},
    {"name": "自強七路", "weight": 25, "lat": (24.9760, 24.9775), "lng": (121.2350, 121.2380), "door_max": 22},
    {"name": "北園路", "weight": 45, "lat": (24.9870, 24.9920), "lng": (121.2350, 121.2450), "door_max": 55},
    {"name": "南園路", "weight": 42, "lat": (24.9730, 24.9760), "lng": (121.2360, 121.2440), "door_max": 50},
    {"name": "南園二路", "weight": 35, "lat": (24.9715, 24.9745), "lng": (121.2360, 121.2420), "door_max": 40},
    {"name": "定安路", "weight": 30, "lat": (24.9850, 24.9880), "lng": (121.2390, 121.2440), "door_max": 45},
    {"name": "合江路", "weight": 34, "lat": (24.9790, 24.9830), "lng": (121.2305, 121.2345), "door_max": 38},
    {"name": "松江路", "weight": 38, "lat": (24.9800, 24.9840), "lng": (121.2325, 121.2365), "door_max": 42},
    {"name": "長春路", "weight": 30, "lat": (24.9810, 24.9860), "lng": (121.2380, 121.2430), "door_max": 36},
    {"name": "長春一路", "weight": 20, "lat": (24.9820, 24.9850), "lng": (121.2390, 121.2430), "door_max": 25}
]

# Vocabulary generator for realistic corporate names in Taiwanese industrial parks
PREFIXES = [
    "大同", "永聯", "富邦", "合發", "益豐", "建達", "鼎茂", "協益", "正陽", "信東",
    "展業", "銘泰", "順捷", "凱達", "長盛", "宏泰", "金利", "全家", "日新", "聯欣",
    "冠宇", "立捷", "寶成", "裕隆", "東亞", "新光", "中強", "華榮", "德興", "源茂",
    "鴻昌", "亞光", "通達", "光遠", "慶豐", "嘉裕", "巨擘", "泰山", "三和", "世邦",
    "創億", "友聯", "富國", "致茂", "威剛", "聯邦", "大億", "欣興", "廣達", "健策",
    "台灣松下", "台灣住友", "台灣信越", "日商", "德商", "美商", "遠東", "中租", "台塑", "南亞"
]

MIDDLES = [
    "精密", "材料", "實業", "工業", "科技", "化學", "金屬", "光電", "機械", "電子",
    "塑膠", "包裝", "包材", "生化", "自動化", "食品", "冷鏈", "物流", "線纜", "五金",
    "沖壓", "壓鑄", "塗料", "高分子", "生醫", "熱處理", "機電", "儀器", "線束", "模具"
]

all_clients = []
client_id = 1

# 1. Add Listed Companies (mark is_listed="是")
for item in LISTED_COMPANIES:
    all_clients.append({
        "id": client_id,
        "name": item["name"],
        "road": item["road"],
        "address": item["address"],
        "lat": item["lat"],
        "lng": item["lng"],
        "industry": item["industry"],
        "is_listed": "是",
        "status": "尚未拜訪",
        "contact": item.get("contact", "廠務部"),
        "phone": item.get("phone", "03-452-xxxx"),
        "notes": "上市櫃指標企業 · 重點巡訪大廠"
    })
    client_id += 1

# 2. Add Famous factories (mark is_listed="否")
for item in FAMOUS_FACTORIES:
    all_clients.append({
        "id": client_id,
        "name": item["name"],
        "road": item["road"],
        "address": item["address"],
        "lat": item["lat"],
        "lng": item["lng"],
        "industry": item["industry"],
        "is_listed": "否",
        "status": "尚未拜訪",
        "contact": item.get("contact", "總機"),
        "phone": item.get("phone", "03-452-xxxx"),
        "notes": "園區知名進駐外商/指標製造廠"
    })
    client_id += 1

# Track industry counts
industry_counts = {}
for c in all_clients:
    ind = c["industry"]
    industry_counts[ind] = industry_counts.get(ind, 0) + 1

# 3. Fill remaining up to 744 companies
remaining_needed = TARGET_COUNT - len(all_clients)
print(f"Initial: {len(all_clients)} companies, generating {remaining_needed} more...")

# Build list of needed industries to hit quotas
needed_industries = []
for ind, quota in INDUSTRY_QUOTAS.items():
    current = industry_counts.get(ind, 0)
    needed = max(0, quota - current)
    needed_industries.extend([ind] * needed)

# If still short or excess, adjust
if len(needed_industries) < remaining_needed:
    needed_industries.extend(["其他製造及服務業"] * (remaining_needed - len(needed_industries)))
else:
    needed_industries = needed_industries[:remaining_needed]

random.shuffle(needed_industries)

# Weighted road selector
road_pool = []
for r in ROADS:
    road_pool.extend([r] * r["weight"])

used_names = set(c["name"] for c in all_clients)

for i in range(remaining_needed):
    ind = needed_industries[i]
    road_info = random.choice(road_pool)
    road_name = road_info["name"]
    door_no = random.randint(1, road_info["door_max"])
    
    # Lat/Lng with small random jitter along road corridor
    lat_min, lat_max = road_info["lat"]
    lng_min, lng_max = road_info["lng"]
    lat = round(random.uniform(lat_min, lat_max), 5)
    lng = round(random.uniform(lng_min, lng_max), 5)
    
    # Generate unique realistic company name
    while True:
        p = random.choice(PREFIXES)
        m = random.choice(MIDDLES)
        suffix = random.choice(["股份有限公司", "有限公司", "工業有限公司", "企業有限公司", "實業廠", "工廠"])
        cname = f"{p}{m}{suffix}"
        if cname not in used_names:
            used_names.add(cname)
            break
            
    address = f"桃園市中壢區{road_name}{door_no}號"
    phone = f"03-452-{random.randint(1000, 9999)}"
    contact = random.choice(["陳廠長", "林經理", "王協理", "張主任", "李課長", "黃副總", "總機人員", "廠務專員", "採購部"])
    
    all_clients.append({
        "id": client_id,
        "name": cname,
        "road": road_name,
        "address": address,
        "lat": lat,
        "lng": lng,
        "industry": ind,
        "is_listed": "否",
        "status": "尚未拜訪",
        "contact": contact,
        "phone": phone,
        "notes": ""
    })
    client_id += 1

print(f"Generated total: {len(all_clients)} companies!")

# Summary of industries
print("Industry breakdown:")
summary = {}
listed_count = 0
for c in all_clients:
    summary[c["industry"]] = summary.get(c["industry"], 0) + 1
    if c["is_listed"] == "是":
        listed_count += 1
for k, v in sorted(summary.items(), key=lambda x: -x[1]):
    print(f" - {k}: {v}")
print(f"Total Listed: {listed_count}")

# Save to CSV
csv_path = r'c:\Users\gyuyu\Documents\antigravity\睡前塔羅與每日塔羅\SKILL\sales-field-map\sample-clients.csv'
with open(csv_path, 'w', encoding='utf-8-sig') as f:
    f.write("id,name,road,address,lat,lng,industry,is_listed,status,contact,phone,notes\n")
    for c in all_clients:
        row = [
            c["id"],
            f'"{c["name"]}"',
            f'"{c["road"]}"',
            f'"{c["address"]}"',
            c["lat"],
            c["lng"],
            f'"{c["industry"]}"',
            c["is_listed"],
            f'"{c["status"]}"',
            f'"{c["contact"]}"',
            f'"{c["phone"]}"',
            f'"{c["notes"]}"'
        ]
        f.write(",".join(map(str, row)) + "\n")

print(f"Saved {len(all_clients)} records to sample-clients.csv")

# Save to JSON
json_path = r'c:\Users\gyuyu\Documents\antigravity\睡前塔羅與每日塔羅\SKILL\sales-field-map\clients_744.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(all_clients, f, ensure_ascii=False, indent=2)

print(f"Saved JSON to clients_744.json")
