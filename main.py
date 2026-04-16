from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import os
import time

app = Flask(__name__)
CORS(app)

# エリア名 → SUUMOパスの完全辞書（提供データに基づく）
AREA_MAP = {
    "北海道札幌市中央区": "hokkaido_/sc_sapporoshichuo",
    "北海道札幌市北区": "hokkaido_/sc_sapporoshikita",
    "北海道札幌市東区": "hokkaido_/sc_sapporoshihigashi",
    "北海道札幌市白石区": "hokkaido_/sc_sapporoshishiroishi",
    "北海道札幌市豊平区": "hokkaido_/sc_sapporoshitoyohira",
    "北海道札幌市南区": "hokkaido_/sc_sapporoshiminami",
    "北海道札幌市西区": "hokkaido_/sc_sapporoshinishi",
    "北海道札幌市厚別区": "hokkaido_/sc_sapporoshiatsubetsu",
    "北海道札幌市手稲区": "hokkaido_/sc_sapporoshiteine",
    "北海道札幌市清田区": "hokkaido_/sc_sapporoshikiyota",
    "北海道函館市": "hokkaido_/sc_hakodate",
    "北海道小樽市": "hokkaido_/sc_otaru",
    "北海道旭川市": "hokkaido_/sc_asahikawa",
    "北海道室蘭市": "hokkaido_/sc_muroran",
    "北海道釧路市": "hokkaido_/sc_kushiro",
    "北海道帯広市": "hokkaido_/sc_obihiro",
    "北海道北見市": "hokkaido_/sc_kitami",
    "北海道夕張市": "hokkaido_/sc_yubari",
    "北海道岩見沢市": "hokkaido_/sc_iwamizawa",
    "北海道網走市": "hokkaido_/sc_abashiri",
    "北海道留萌市": "hokkaido_/sc_rumoi",
    "北海道苫小牧市": "hokkaido_/sc_tomakomai",
    "北海道稚内市": "hokkaido_/sc_wakkanai",
    "北海道美唄市": "hokkaido_/sc_bibai",
    "北海道芦別市": "hokkaido_/sc_ashibetsu",
    "北海道江別市": "hokkaido_/sc_ebetsu",
    "北海道赤平市": "hokkaido_/sc_akabira",
    "北海道紋別市": "hokkaido_/sc_mombetsu",
    "北海道士別市": "hokkaido_/sc_shibetsu",
    "北海道名寄市": "hokkaido_/sc_nayoro",
    "北海道三笠市": "hokkaido_/sc_mikasa",
    "北海道根室市": "hokkaido_/sc_nemuro",
    "北海道千歳市": "hokkaido_/sc_chitose",
    "北海道滝川市": "hokkaido_/sc_takikawa",
    "北海道砂川市": "hokkaido_/sc_sunagawa",
    "北海道歌志内市": "hokkaido_/sc_utashinai",
    "北海道深川市": "hokkaido_/sc_fukagawa",
    "北海道富良野市": "hokkaido_/sc_furano",
    "北海道登別市": "hokkaido_/sc_noboribetsu",
    "北海道恵庭市": "hokkaido_/sc_eniwa",
    "北海道伊達市": "hokkaido_/sc_date",
    "北海道北広島市": "hokkaido_/sc_kitahiroshima",
    "北海道石狩市": "hokkaido_/sc_ishikari",
    "北海道北斗市": "hokkaido_/sc_hokuto",
    "青森県青森市": "aomori/sc_aomori",
    "青森県弘前市": "aomori/sc_hirosaki",
    "青森県八戸市": "aomori/sc_hachinohe",
    "青森県黒石市": "aomori/sc_kuroishi",
    "青森県五所川原市": "aomori/sc_goshogawara",
    "青森県十和田市": "aomori/sc_towada",
    "青森県三沢市": "aomori/sc_misawa",
    "青森県むつ市": "aomori/sc_mutsu",
    "青森県つがる市": "aomori/sc_tsugaru",
    "青森県平川市": "aomori/sc_hirakawa",
    "岩手県盛岡市": "iwate/sc_morioka",
    "岩手県宮古市": "iwate/sc_miyako",
    "岩手県大船渡市": "iwate/sc_ofunato",
    "岩手県花巻市": "iwate/sc_hanamaki",
    "岩手県北上市": "iwate/sc_kitakami",
    "岩手県久慈市": "iwate/sc_kuji",
    "岩手県遠野市": "iwate/sc_tono",
    "岩手県一関市": "iwate/sc_ichinoseki",
    "岩手県陸前高田市": "iwate/sc_rikuzentakata",
    "岩手県釜石市": "iwate/sc_kamaishi",
    "岩手県二戸市": "iwate/sc_ninohe",
    "岩手県八幡平市": "iwate/sc_hachimantai",
    "岩手県奥州市": "iwate/sc_oshu",
    "岩手県滝沢市": "iwate/sc_takizawa",
    "宮城県仙台市青葉区": "miyagi/sc_sendaishiaoba",
    "宮城県仙台市宮城野区": "miyagi/sc_sendaishimiyagino",
    "宮城県仙台市若林区": "miyagi/sc_sendaishiwakabayashi",
    "宮城県仙台市太白区": "miyagi/sc_sendaishitaihaku",
    "宮城県仙台市泉区": "miyagi/sc_sendaishiizumi",
    "宮城県石巻市": "miyagi/sc_ishinomaki",
    "宮城県塩竈市": "miyagi/sc_shiogama",
    "宮城県気仙沼市": "miyagi/sc_kesennuma",
    "宮城県白石市": "miyagi/sc_shiroishi",
    "宮城県名取市": "miyagi/sc_natori",
    "宮城県角田市": "miyagi/sc_kakuda",
    "宮城県多賀城市": "miyagi/sc_tagajo",
    "宮城県岩沼市": "miyagi/sc_iwanuma",
    "宮城県登米市": "miyagi/sc_tome",
    "宮城県栗原市": "miyagi/sc_kurihara",
    "宮城県東松島市": "miyagi/sc_higashimatsushima",
    "宮城県大崎市": "miyagi/sc_osaki",
    "宮城県富谷市": "miyagi/sc_tomiya",
    "秋田県秋田市": "akita/sc_akita",
    "秋田県能代市": "akita/sc_noshiro",
    "秋田県横手市": "akita/sc_yokote",
    "秋田県大館市": "akita/sc_odate",
    "秋田県男鹿市": "akita/sc_oga",
    "秋田県湯沢市": "akita/sc_yuzawa",
    "秋田県鹿角市": "akita/sc_kazuno",
    "秋田県由利本荘市": "akita/sc_yurihonjo",
    "秋田県潟上市": "akita/sc_katagami",
    "秋田県大仙市": "akita/sc_daisen",
    "秋田県北秋田市": "akita/sc_kitaakita",
    "秋田県にかほ市": "akita/sc_nikaho",
    "秋田県仙北市": "akita/sc_semboku",
    "山形県山形市": "yamagata/sc_yamagata",
    "山形県米沢市": "yamagata/sc_yonezawa",
    "山形県鶴岡市": "yamagata/sc_tsuruoka",
    "山形県酒田市": "yamagata/sc_sakata",
    "山形県新庄市": "yamagata/sc_shinjo",
    "山形県寒河江市": "yamagata/sc_sagae",
    "山形県上山市": "yamagata/sc_kaminoyama",
    "山形県村山市": "yamagata/sc_murayama",
    "山形県長井市": "yamagata/sc_nagai",
    "山形県天童市": "yamagata/sc_tendo",
    "山形県東根市": "yamagata/sc_higashine",
    "山形県尾花沢市": "yamagata/sc_obanazawa",
    "山形県南陽市": "yamagata/sc_nanyo",
    "福島県福島市": "fukushima/sc_fukushima",
    "福島県会津若松市": "fukushima/sc_aizuwakamatsu",
    "福島県郡山市": "fukushima/sc_koriyama",
    "福島県いわき市": "fukushima/sc_iwaki",
    "福島県白河市": "fukushima/sc_shirakawa",
    "福島県須賀川市": "fukushima/sc_sukagawa",
    "福島県喜多方市": "fukushima/sc_kitakata",
    "福島県相馬市": "fukushima/sc_soma",
    "福島県二本松市": "fukushima/sc_nihommatsu",
    "福島県田村市": "fukushima/sc_tamura",
    "福島県南相馬市": "fukushima/sc_minamisoma",
    "福島県伊達市": "fukushima/sc_date",
    "福島県本宮市": "fukushima/sc_motomiya",
    "茨城県水戸市": "ibaraki/sc_mito",
    "茨城県日立市": "ibaraki/sc_hitachi",
    "茨城県土浦市": "ibaraki/sc_tsuchiura",
    "茨城県古河市": "ibaraki/sc_koga",
    "茨城県石岡市": "ibaraki/sc_ishioka",
    "茨城県結城市": "ibaraki/sc_yuki",
    "茨城県龍ケ崎市": "ibaraki/sc_ryugasaki",
    "茨城県下妻市": "ibaraki/sc_shimotsuma",
    "茨城県常総市": "ibaraki/sc_joso",
    "茨城県常陸太田市": "ibaraki/sc_hitachiota",
    "茨城県高萩市": "ibaraki/sc_takahagi",
    "茨城県北茨城市": "ibaraki/sc_kitaibaraki",
    "茨城県笠間市": "ibaraki/sc_kasama",
    "茨城県取手市": "ibaraki/sc_toride",
    "茨城県牛久市": "ibaraki/sc_ushiku",
    "茨城県つくば市": "ibaraki/sc_tsukuba",
    "茨城県ひたちなか市": "ibaraki/sc_hitachinaka",
    "茨城県鹿嶋市": "ibaraki/sc_kashima",
    "茨城県潮来市": "ibaraki/sc_itako",
    "茨城県守谷市": "ibaraki/sc_moriya",
    "茨城県常陸大宮市": "ibaraki/sc_hitachiomiya",
    "茨城県那珂市": "ibaraki/sc_naka",
    "茨城県筑西市": "ibaraki/sc_chikusei",
    "茨城県坂東市": "ibaraki/sc_bando",
    "茨城県稲敷市": "ibaraki/sc_inashiki",
    "茨城県かすみがうら市": "ibaraki/sc_kasumigaura",
    "茨城県桜川市": "ibaraki/sc_sakuragawa",
    "茨城県神栖市": "ibaraki/sc_kamisu",
    "茨城県行方市": "ibaraki/sc_namegata",
    "茨城県鉾田市": "ibaraki/sc_hokota",
    "茨城県つくばみらい市": "ibaraki/sc_tsukubamirai",
    "茨城県小美玉市": "ibaraki/sc_omitama",
    "栃木県宇都宮市": "tochigi/sc_utsunomiya",
    "栃木県足利市": "tochigi/sc_ashikaga",
    "栃木県栃木市": "tochigi/sc_tochigi",
    "栃木県佐野市": "tochigi/sc_sano",
    "栃木県鹿沼市": "tochigi/sc_kanuma",
    "栃木県日光市": "tochigi/sc_nikko",
    "栃木県小山市": "tochigi/sc_oyama",
    "栃木県真岡市": "tochigi/sc_moka",
    "栃木県大田原市": "tochigi/sc_otawara",
    "栃木県矢板市": "tochigi/sc_yaita",
    "栃木県那須塩原市": "tochigi/sc_nasushiobara",
    "栃木県さくら市": "tochigi/sc_sakura",
    "栃木県那須烏山市": "tochigi/sc_nasukarasuyama",
    "栃木県下野市": "tochigi/sc_shimotsuke",
    "群馬県前橋市": "gumma/sc_maebashi",
    "群馬県高崎市": "gumma/sc_takasaki",
    "群馬県桐生市": "gumma/sc_kiryu",
    "群馬県伊勢崎市": "gumma/sc_isesaki",
    "群馬県太田市": "gumma/sc_ota",
    "群馬県沼田市": "gumma/sc_numata",
    "群馬県館林市": "gumma/sc_tatebayashi",
    "群馬県渋川市": "gumma/sc_shibukawa",
    "群馬県藤岡市": "gumma/sc_fujioka",
    "群馬県富岡市": "gumma/sc_tomioka",
    "群馬県安中市": "gumma/sc_annaka",
    "群馬県みどり市": "gumma/sc_midori",
    "埼玉県さいたま市西区": "saitama/sc_saitamashinishi",
    "埼玉県さいたま市北区": "saitama/sc_saitamashikita",
    "埼玉県さいたま市大宮区": "saitama/sc_saitamashiomiya",
    "埼玉県さいたま市見沼区": "saitama/sc_saitamashiminuma",
    "埼玉県さいたま市中央区": "saitama/sc_saitamashichuo",
    "埼玉県さいたま市桜区": "saitama/sc_saitamashisakura",
    "埼玉県さいたま市浦和区": "saitama/sc_saitamashiurawa",
    "埼玉県さいたま市南区": "saitama/sc_saitamashiminami",
    "埼玉県さいたま市緑区": "saitama/sc_saitamashimidori",
    "埼玉県さいたま市岩槻区": "saitama/sc_saitamashiiwatsuki",
    "埼玉県川越市": "saitama/sc_kawagoe",
    "埼玉県熊谷市": "saitama/sc_kumagaya",
    "埼玉県川口市": "saitama/sc_kawaguchi",
    "埼玉県行田市": "saitama/sc_giyoda",
    "埼玉県秩父市": "saitama/sc_chichibu",
    "埼玉県所沢市": "saitama/sc_tokorozawa",
    "埼玉県飯能市": "saitama/sc_hannou",
    "埼玉県加須市": "saitama/sc_kazo",
    "埼玉県本庄市": "saitama/sc_honjiyo",
    "埼玉県東松山市": "saitama/sc_higashimatsuyama",
    "埼玉県春日部市": "saitama/sc_kasukabe",
    "埼玉県狭山市": "saitama/sc_sayama",
    "埼玉県羽生市": "saitama/sc_haniyu",
    "埼玉県鴻巣市": "saitama/sc_konosu",
    "埼玉県深谷市": "saitama/sc_fukaya",
    "埼玉県上尾市": "saitama/sc_ageo",
    "埼玉県草加市": "saitama/sc_soka",
    "埼玉県越谷市": "saitama/sc_koshigaya",
    "埼玉県蕨市": "saitama/sc_warabi",
    "埼玉県戸田市": "saitama/sc_toda",
    "埼玉県入間市": "saitama/sc_iruma",
    "埼玉県朝霞市": "saitama/sc_asaka",
    "埼玉県志木市": "saitama/sc_shiki",
    "埼玉県和光市": "saitama/sc_wako",
    "埼玉県新座市": "saitama/sc_niiza",
    "埼玉県桶川市": "saitama/sc_okegawa",
    "埼玉県久喜市": "saitama/sc_kuki",
    "埼玉県北本市": "saitama/sc_kitamoto",
    "埼玉県八潮市": "saitama/sc_yashio",
    "埼玉県富士見市": "saitama/sc_fujimi",
    "埼玉県三郷市": "saitama/sc_misato",
    "埼玉県蓮田市": "saitama/sc_hasuda",
    "埼玉県坂戸市": "saitama/sc_sakado",
    "埼玉県幸手市": "saitama/sc_satte",
    "埼玉県鶴ヶ島市": "saitama/sc_tsurugashima",
    "埼玉県日高市": "saitama/sc_hidaka",
    "埼玉県吉川市": "saitama/sc_yoshikawa",
    "埼玉県ふじみ野市": "saitama/sc_fujimino",
    "埼玉県白岡市": "saitama/sc_shiraoka",
    "千葉県千葉市中央区": "chiba/sc_chibashichuo",
    "千葉県千葉市花見川区": "chiba/sc_chibashihanamigawa",
    "千葉県千葉市稲毛区": "chiba/sc_chibashiinage",
    "千葉県千葉市若葉区": "chiba/sc_chibashiwakaba",
    "千葉県千葉市緑区": "chiba/sc_chibashimidori",
    "千葉県千葉市美浜区": "chiba/sc_chibashimihama",
    "千葉県銚子市": "chiba/sc_choshi",
    "千葉県市川市": "chiba/sc_ichikawa",
    "千葉県船橋市": "chiba/sc_funabashi",
    "千葉県館山市": "chiba/sc_tateyama",
    "千葉県木更津市": "chiba/sc_kisarazu",
    "千葉県松戸市": "chiba/sc_matsudo",
    "千葉県野田市": "chiba/sc_noda",
    "千葉県茂原市": "chiba/sc_mobara",
    "千葉県成田市": "chiba/sc_narita",
    "千葉県佐倉市": "chiba/sc_sakura",
    "千葉県東金市": "chiba/sc_togane",
    "千葉県旭市": "chiba/sc_asahi",
    "千葉県習志野市": "chiba/sc_narashino",
    "千葉県柏市": "chiba/sc_kashiwa",
    "千葉県勝浦市": "chiba/sc_katsura",
    "千葉県市原市": "chiba/sc_ichihara",
    "千葉県流山市": "chiba/sc_nagareyama",
    "千葉県八千代市": "chiba/sc_yachiyo",
    "千葉県我孫子市": "chiba/sc_abiko",
    "千葉県鴨川市": "chiba/sc_kamogawa",
    "千葉県鎌ケ谷市": "chiba/sc_kamagaya",
    "千葉県君津市": "chiba/sc_kimitsu",
    "千葉県富津市": "chiba/sc_futtsu",
    "千葉県浦安市": "chiba/sc_urayasu",
    "千葉県四街道市": "chiba/sc_yotsukaido",
    "千葉県袖ケ浦市": "chiba/sc_sodegaura",
    "千葉県八街市": "chiba/sc_yachimata",
    "千葉県印西市": "chiba/sc_inzai",
    "千葉県白井市": "chiba/sc_shiroi",
    "千葉県富里市": "chiba/sc_tomisato",
    "千葉県南房総市": "chiba/sc_minamiboso",
    "千葉県匝瑳市": "chiba/sc_sosa",
    "千葉県香取市": "chiba/sc_katori",
    "千葉県山武市": "chiba/sc_sammu",
    "千葉県いすみ市": "chiba/sc_isumi",
    "千葉県大網白里市": "chiba/sc_oamishirasato",
    "東京都千代田区": "tokyo/sc_chiyoda",
    "東京都中央区": "tokyo/sc_chuo",
    "東京都港区": "tokyo/sc_minato",
    "東京都新宿区": "tokyo/sc_shinjuku",
    "東京都文京区": "tokyo/sc_bunkyo",
    "東京都台東区": "tokyo/sc_taito",
    "東京都墨田区": "tokyo/sc_sumida",
    "東京都江東区": "tokyo/sc_koto",
    "東京都品川区": "tokyo/sc_shinagawa",
    "東京都目黒区": "tokyo/sc_meguro",
    "東京都大田区": "tokyo/sc_ota",
    "東京都世田谷区": "tokyo/sc_setagaya",
    "東京都渋谷区": "tokyo/sc_shibuya",
    "東京都中野区": "tokyo/sc_nakano",
    "東京都杉並区": "tokyo/sc_suginami",
    "東京都豊島区": "tokyo/sc_toshima",
    "東京都北区": "tokyo/sc_kita",
    "東京都荒川区": "tokyo/sc_arakawa",
    "東京都板橋区": "tokyo/sc_itabashi",
    "東京都練馬区": "tokyo/sc_nerima",
    "東京都足立区": "tokyo/sc_adachi",
    "東京都葛飾区": "tokyo/sc_katsushika",
    "東京都江戸川区": "tokyo/sc_edogawa",
    "東京都八王子市": "tokyo/sc_hachioji",
    "東京都立川市": "tokyo/sc_tachikawa",
    "東京都武蔵野市": "tokyo/sc_musashino",
    "東京都三鷹市": "tokyo/sc_mitaka",
    "東京都青梅市": "tokyo/sc_ome",
    "東京都府中市": "tokyo/sc_fuchu",
    "東京都昭島市": "tokyo/sc_akishima",
    "東京都調布市": "tokyo/sc_chofu",
    "東京都町田市": "tokyo/sc_machida",
    "東京都小金井市": "tokyo/sc_koganei",
    "東京都小平市": "tokyo/sc_kodaira",
    "東京都日野市": "tokyo/sc_hino",
    "東京都東村山市": "tokyo/sc_higashimurayama",
    "東京都国分寺市": "tokyo/sc_kokubunji",
    "東京都国立市": "tokyo/sc_kunitachi",
    "東京都福生市": "tokyo/sc_fussa",
    "東京都狛江市": "tokyo/sc_komae",
    "東京都東大和市": "tokyo/sc_higashiyamato",
    "東京都清瀬市": "tokyo/sc_kiyose",
    "東京都東久留米市": "tokyo/sc_higashikurume",
    "東京都武蔵村山市": "tokyo/sc_musashimurayama",
    "東京都多摩市": "tokyo/sc_tama",
    "東京都稲城市": "tokyo/sc_inagi",
    "東京都羽村市": "tokyo/sc_hamura",
    "東京都あきる野市": "tokyo/sc_akiruno",
    "東京都西東京市": "tokyo/sc_nishitokyo",
    "神奈川県横浜市鶴見区": "kanagawa/sc_yokohamashitsurumi",
    "神奈川県横浜市神奈川区": "kanagawa/sc_yokohamashikanagawa",
    "神奈川県横浜市西区": "kanagawa/sc_yokohamashinishi",
    "神奈川県横浜市中区": "kanagawa/sc_yokohamashinaka",
    "神奈川県横浜市南区": "kanagawa/sc_yokohamashiminami",
    "神奈川県横浜市保土ケ谷区": "kanagawa/sc_yokohamashihodogaya",
    "神奈川県横浜市磯子区": "kanagawa/sc_yokohamashiisogo",
    "神奈川県横浜市金沢区": "kanagawa/sc_yokohamashikanazawa",
    "神奈川県横浜市港北区": "kanagawa/sc_yokohamashikohoku",
    "神奈川県横浜市戸塚区": "kanagawa/sc_yokohamashitotsuka",
    "神奈川県横浜市港南区": "kanagawa/sc_yokohamashikonan",
    "神奈川県横浜市旭区": "kanagawa/sc_yokohamashiasahi",
    "神奈川県横浜市緑区": "kanagawa/sc_yokohamashimidori",
    "神奈川県横浜市瀬谷区": "kanagawa/sc_yokohamashiseya",
    "神奈川県横浜市栄区": "kanagawa/sc_yokohamashisakae",
    "神奈川県横浜市泉区": "kanagawa/sc_yokohamashiizumi",
    "神奈川県横浜市青葉区": "kanagawa/sc_yokohamashiaoba",
    "神奈川県横浜市都筑区": "kanagawa/sc_yokohamashitsuzuki",
    "神奈川県川崎市川崎区": "kanagawa/sc_kawasakishikawasaki",
    "神奈川県川崎市幸区": "kanagawa/sc_kawasakishisaiwai",
    "神奈川県川崎市中原区": "kanagawa/sc_kawasakishinakahara",
    "神奈川県川崎市高津区": "kanagawa/sc_kawasakishitakatsu",
    "神奈川県川崎市多摩区": "kanagawa/sc_kawasakishitama",
    "神奈川県川崎市宮前区": "kanagawa/sc_kawasakishimiyamae",
    "神奈川県川崎市麻生区": "kanagawa/sc_kawasakishiasao",
    "神奈川県相模原市緑区": "kanagawa/sc_sagamiharashimidori",
    "神奈川県相模原市中央区": "kanagawa/sc_sagamiharashichuo",
    "神奈川県相模原市南区": "kanagawa/sc_sagamiharashiminami",
    "神奈川県横須賀市": "kanagawa/sc_yokosuka",
    "神奈川県平塚市": "kanagawa/sc_hiratsuka",
    "神奈川県鎌倉市": "kanagawa/sc_kamakura",
    "神奈川県藤沢市": "kanagawa/sc_fujisawa",
    "神奈川県小田原市": "kanagawa/sc_odawara",
    "神奈川県茅ヶ崎市": "kanagawa/sc_chigasaki",
    "神奈川県逗子市": "kanagawa/sc_zushi",
    "神奈川県三浦市": "kanagawa/sc_miura",
    "神奈川県秦野市": "kanagawa/sc_hadano",
    "神奈川県厚木市": "kanagawa/sc_atsugi",
    "神奈川県大和市": "kanagawa/sc_yamato",
    "神奈川県伊勢原市": "kanagawa/sc_isehara",
    "神奈川県海老名市": "kanagawa/sc_ebina",
    "神奈川県座間市": "kanagawa/sc_zama",
    "神奈川県南足柄市": "kanagawa/sc_minamiashigara",
    "神奈川県綾瀬市": "kanagawa/sc_ayase",
    "新潟県新潟市北区": "niigata/sc_niigatashikita",
    "新潟県新潟市東区": "niigata/sc_niigatashihigashi",
    "新潟県新潟市中央区": "niigata/sc_niigatashichuo",
    "新潟県新潟市江南区": "niigata/sc_niigatashikonan",
    "新潟県新潟市秋葉区": "niigata/sc_niigatashiakiha",
    "新潟県新潟市南区": "niigata/sc_niigatashiminami",
    "新潟県新潟市西区": "niigata/sc_niigatashinishi",
    "新潟県新潟市西蒲区": "niigata/sc_niigatashinishikan",
    "新潟県長岡市": "niigata/sc_nagaoka",
    "新潟県三条市": "niigata/sc_sanjo",
    "新潟県柏崎市": "niigata/sc_kashiwazaki",
    "新潟県新発田市": "niigata/sc_shibata",
    "新潟県小千谷市": "niigata/sc_ojiya",
    "新潟県加茂市": "niigata/sc_kamo",
    "新潟県十日町市": "niigata/sc_tokamachi",
    "新潟県見附市": "niigata/sc_mitsuke",
    "新潟県村上市": "niigata/sc_murakami",
    "新潟県燕市": "niigata/sc_tsubame",
    "新潟県糸魚川市": "niigata/sc_itoigawa",
    "新潟県妙高市": "niigata/sc_myoko",
    "新潟県五泉市": "niigata/sc_gosen",
    "新潟県上越市": "niigata/sc_joetsu",
    "新潟県阿賀野市": "niigata/sc_agano",
    "新潟県佐渡市": "niigata/sc_sado",
    "新潟県魚沼市": "niigata/sc_uonuma",
    "新潟県南魚沼市": "niigata/sc_minamiuonuma",
    "新潟県胎内市": "niigata/sc_tainai",
    "富山県富山市": "toyama/sc_toyama",
    "富山県高岡市": "toyama/sc_takaoka",
    "富山県魚津市": "toyama/sc_uozu",
    "富山県氷見市": "toyama/sc_himi",
    "富山県滑川市": "toyama/sc_namerikawa",
    "富山県黒部市": "toyama/sc_kurobe",
    "富山県砺波市": "toyama/sc_tonami",
    "富山県小矢部市": "toyama/sc_oyabe",
    "富山県南砺市": "toyama/sc_nanto",
    "富山県射水市": "toyama/sc_imizu",
    "石川県金沢市": "ishikawa/sc_kanazawa",
    "石川県七尾市": "ishikawa/sc_nanao",
    "石川県小松市": "ishikawa/sc_komatsu",
    "石川県輪島市": "ishikawa/sc_wajima",
    "石川県珠洲市": "ishikawa/sc_suzu",
    "石川県加賀市": "ishikawa/sc_kaga",
    "石川県羽咋市": "ishikawa/sc_hakui",
    "石川県かほく市": "ishikawa/sc_kahoku",
    "石川県白山市": "ishikawa/sc_hakusan",
    "石川県能美市": "ishikawa/sc_nomi",
    "石川県野々市市": "ishikawa/sc_nonoichi",
    "福井県福井市": "fukui/sc_fukui",
    "福井県敦賀市": "fukui/sc_tsuruga",
    "福井県小浜市": "fukui/sc_obama",
    "福井県大野市": "fukui/sc_ono",
    "福井県勝山市": "fukui/sc_katsuyama",
    "福井県鯖江市": "fukui/sc_sabae",
    "福井県あわら市": "fukui/sc_awara",
    "福井県越前市": "fukui/sc_echizen",
    "福井県坂井市": "fukui/sc_sakai",
    "山梨県甲府市": "yamanashi/sc_kofu",
    "山梨県富士吉田市": "yamanashi/sc_fujiyoshida",
    "山梨県都留市": "yamanashi/sc_tsuru",
    "山梨県山梨市": "yamanashi/sc_yamanashi",
    "山梨県大月市": "yamanashi/sc_otsuki",
    "山梨県韮崎市": "yamanashi/sc_nirasaki",
    "山梨県南アルプス市": "yamanashi/sc_minamiarupusu",
    "山梨県北杜市": "yamanashi/sc_hokuto",
    "山梨県甲斐市": "yamanashi/sc_kai",
    "山梨県笛吹市": "yamanashi/sc_fuefuki",
    "山梨県上野原市": "yamanashi/sc_uenohara",
    "山梨県甲州市": "yamanashi/sc_koshu",
    "山梨県中央市": "yamanashi/sc_chuo",
    "長野県長野市": "nagano/sc_nagano",
    "長野県松本市": "nagano/sc_matsumoto",
    "長野県上田市": "nagano/sc_ueda",
    "長野県岡谷市": "nagano/sc_okaya",
    "長野県飯田市": "nagano/sc_iida",
    "長野県諏訪市": "nagano/sc_suwa",
    "長野県須坂市": "nagano/sc_suzaka",
    "長野県小諸市": "nagano/sc_komoro",
    "長野県伊那市": "nagano/sc_ina",
    "長野県駒ヶ根市": "nagano/sc_komagane",
    "長野県中野市": "nagano/sc_nakano",
    "長野県大町市": "nagano/sc_omachi",
    "長野県飯山市": "nagano/sc_iiyama",
    "長野県茅野市": "nagano/sc_chino",
    "長野県塩尻市": "nagano/sc_shiojiri",
    "長野県佐久市": "nagano/sc_saku",
    "長野県千曲市": "nagano/sc_chikuma",
    "長野県東御市": "nagano/sc_tomi",
    "長野県安曇野市": "nagano/sc_azumino",
    "岐阜県岐阜市": "gifu/sc_gifu",
    "岐阜県大垣市": "gifu/sc_ogaki",
    "岐阜県高山市": "gifu/sc_takayama",
    "岐阜県多治見市": "gifu/sc_tajimi",
    "岐阜県関市": "gifu/sc_seki",
    "岐阜県中津川市": "gifu/sc_nakatsugawa",
    "岐阜県美濃市": "gifu/sc_mino",
    "岐阜県瑞浪市": "gifu/sc_mizunami",
    "岐阜県羽島市": "gifu/sc_hashima",
    "岐阜県恵那市": "gifu/sc_ena",
    "岐阜県美濃加茂市": "gifu/sc_minokamo",
    "岐阜県土岐市": "gifu/sc_toki",
    "岐阜県各務原市": "gifu/sc_kakamigahara",
    "岐阜県可児市": "gifu/sc_kani",
    "岐阜県山県市": "gifu/sc_yamagata",
    "岐阜県瑞穂市": "gifu/sc_mizuho",
    "岐阜県飛騨市": "gifu/sc_hida",
    "岐阜県本巣市": "gifu/sc_motosu",
    "岐阜県郡上市": "gifu/sc_gujo",
    "岐阜県下呂市": "gifu/sc_gero",
    "岐阜県海津市": "gifu/sc_kaizu",
    "静岡県静岡市葵区": "shizuoka/sc_shizuokashiaoi",
    "静岡県静岡市駿河区": "shizuoka/sc_shizuokashisuruga",
    "静岡県静岡市清水区": "shizuoka/sc_shizuokashishimizu",
    "静岡県浜松市中央区": "shizuoka/sc_hamamatsushichuo",
    "静岡県浜松市浜名区": "shizuoka/sc_hamamatsushihamana",
    "静岡県浜松市天竜区": "shizuoka/sc_hamamatsushitenryu",
    "静岡県沼津市": "shizuoka/sc_numazu",
    "静岡県熱海市": "shizuoka/sc_atami",
    "静岡県三島市": "shizuoka/sc_mishima",
    "静岡県富士宮市": "shizuoka/sc_fujinomiya",
    "静岡県伊東市": "shizuoka/sc_ito",
    "静岡県島田市": "shizuoka/sc_shimada",
    "静岡県富士市": "shizuoka/sc_fuji",
    "静岡県磐田市": "shizuoka/sc_iwata",
    "静岡県焼津市": "shizuoka/sc_yaizu",
    "静岡県掛川市": "shizuoka/sc_kakegawa",
    "静岡県藤枝市": "shizuoka/sc_fujieda",
    "静岡県御殿場市": "shizuoka/sc_gotemba",
    "静岡県袋井市": "shizuoka/sc_fukuroi",
    "静岡県下田市": "shizuoka/sc_shimoda",
    "静岡県裾野市": "shizuoka/sc_susono",
    "静岡県湖西市": "shizuoka/sc_kosai",
    "静岡県伊豆市": "shizuoka/sc_izu",
    "静岡県御前崎市": "shizuoka/sc_omaezaki",
    "静岡県菊川市": "shizuoka/sc_kikugawa",
    "静岡県伊豆の国市": "shizuoka/sc_izunokuni",
    "静岡県牧之原市": "shizuoka/sc_makinohara",
    "愛知県名古屋市千種区": "aichi/sc_nagoyashichikusa",
    "愛知県名古屋市東区": "aichi/sc_nagoyashihigashi",
    "愛知県名古屋市北区": "aichi/sc_nagoyashikita",
    "愛知県名古屋市西区": "aichi/sc_nagoyashinishi",
    "愛知県名古屋市中村区": "aichi/sc_nagoyashinakamura",
    "愛知県名古屋市中区": "aichi/sc_nagoyashinaka",
    "愛知県名古屋市昭和区": "aichi/sc_nagoyashishowa",
    "愛知県名古屋市瑞穂区": "aichi/sc_nagoyashimizuho",
    "愛知県名古屋市熱田区": "aichi/sc_nagoyashiatsuta",
    "愛知県名古屋市中川区": "aichi/sc_nagoyashinakagawa",
    "愛知県名古屋市港区": "aichi/sc_nagoyashiminato",
    "愛知県名古屋市南区": "aichi/sc_nagoyashiminami",
    "愛知県名古屋市守山区": "aichi/sc_nagoyashimoriyama",
    "愛知県名古屋市緑区": "aichi/sc_nagoyashimidori",
    "愛知県名古屋市名東区": "aichi/sc_nagoyashimeito",
    "愛知県名古屋市天白区": "aichi/sc_nagoyashitempaku",
    "愛知県豊橋市": "aichi/sc_toyohashi",
    "愛知県岡崎市": "aichi/sc_okazaki",
    "愛知県一宮市": "aichi/sc_ichinomiya",
    "愛知県瀬戸市": "aichi/sc_seto",
    "愛知県半田市": "aichi/sc_handa",
    "愛知県春日井市": "aichi/sc_kasugai",
    "愛知県豊川市": "aichi/sc_toyokawa",
    "愛知県津島市": "aichi/sc_tsushima",
    "愛知県碧南市": "aichi/sc_hekinan",
    "愛知県刈谷市": "aichi/sc_kariya",
    "愛知県豊田市": "aichi/sc_toyota",
    "愛知県安城市": "aichi/sc_anjo",
    "愛知県西尾市": "aichi/sc_nishio",
    "愛知県蒲郡市": "aichi/sc_gamagori",
    "愛知県犬山市": "aichi/sc_inuyama",
    "愛知県常滑市": "aichi/sc_tokoname",
    "愛知県江南市": "aichi/sc_konan",
    "愛知県小牧市": "aichi/sc_komaki",
    "愛知県稲沢市": "aichi/sc_inazawa",
    "愛知県新城市": "aichi/sc_shinshiro",
    "愛知県東海市": "aichi/sc_tokai",
    "愛知県大府市": "aichi/sc_obu",
    "愛知県知多市": "aichi/sc_chita",
    "愛知県知立市": "aichi/sc_chiryu",
    "愛知県尾張旭市": "aichi/sc_owariasahi",
    "愛知県高浜市": "aichi/sc_takahama",
    "愛知県岩倉市": "aichi/sc_iwakura",
    "愛知県豊明市": "aichi/sc_toyoake",
    "愛知県日進市": "aichi/sc_nisshin",
    "愛知県田原市": "aichi/sc_tahara",
    "愛知県愛西市": "aichi/sc_aisai",
    "愛知県清須市": "aichi/sc_kiyosu",
    "愛知県北名古屋市": "aichi/sc_kitanagoya",
    "愛知県弥富市": "aichi/sc_yatomi",
    "愛知県みよし市": "aichi/sc_miyoshi",
    "愛知県あま市": "aichi/sc_ama",
    "愛知県長久手市": "aichi/sc_nagakute",
    "三重県津市": "mie/sc_tsu",
    "三重県四日市市": "mie/sc_yokkaichi",
    "三重県伊勢市": "mie/sc_ise",
    "三重県松阪市": "mie/sc_matsusaka",
    "三重県桑名市": "mie/sc_kuwana",
    "三重県鈴鹿市": "mie/sc_suzuka",
    "三重県名張市": "mie/sc_nabari",
    "三重県尾鷲市": "mie/sc_owase",
    "三重県亀山市": "mie/sc_kameyama",
    "三重県鳥羽市": "mie/sc_toba",
    "三重県熊野市": "mie/sc_kumano",
    "三重県いなべ市": "mie/sc_inabe",
    "三重県志摩市": "mie/sc_shima",
    "三重県伊賀市": "mie/sc_iga",
    "滋賀県大津市": "shiga/sc_otsu",
    "滋賀県彦根市": "shiga/sc_hikone",
    "滋賀県長浜市": "shiga/sc_nagahama",
    "滋賀県近江八幡市": "shiga/sc_omihachiman",
    "滋賀県草津市": "shiga/sc_kusatsu",
    "滋賀県守山市": "shiga/sc_moriyama",
    "滋賀県栗東市": "shiga/sc_ritto",
    "滋賀県甲賀市": "shiga/sc_koka",
    "滋賀県野洲市": "shiga/sc_yasu",
    "滋賀県湖南市": "shiga/sc_konan",
    "滋賀県高島市": "shiga/sc_takashima",
    "滋賀県東近江市": "shiga/sc_higashiomi",
    "滋賀県米原市": "shiga/sc_maibara",
    "京都府京都市北区": "kyoto/sc_kyotoshikita",
    "京都府京都市上京区": "kyoto/sc_kyotoshikamigyo",
    "京都府京都市左京区": "kyoto/sc_kyotoshisakyo",
    "京都府京都市中京区": "kyoto/sc_kyotoshinakagyo",
    "京都府京都市東山区": "kyoto/sc_kyotoshihigashiyama",
    "京都府京都市下京区": "kyoto/sc_kyotoshishimogyo",
    "京都府京都市南区": "kyoto/sc_kyotoshiminami",
    "京都府京都市右京区": "kyoto/sc_kyotoshiukyo",
    "京都府京都市伏見区": "kyoto/sc_kyotoshifushimi",
    "京都府京都市山科区": "kyoto/sc_kyotoshiyamashina",
    "京都府京都市西京区": "kyoto/sc_kyotoshinishikyo",
    "京都府福知山市": "kyoto/sc_fukuchiyama",
    "京都府舞鶴市": "kyoto/sc_maizuru",
    "京都府綾部市": "kyoto/sc_ayabe",
    "京都府宇治市": "kyoto/sc_uji",
    "京都府宮津市": "kyoto/sc_miyazu",
    "京都府亀岡市": "kyoto/sc_kameoka",
    "京都府城陽市": "kyoto/sc_joyo",
    "京都府向日市": "kyoto/sc_muko",
    "京都府長岡京市": "kyoto/sc_nagaokakyo",
    "京都府八幡市": "kyoto/sc_yawata",
    "京都府京田辺市": "kyoto/sc_kyotanabe",
    "京都府京丹後市": "kyoto/sc_kyotango",
    "京都府南丹市": "kyoto/sc_nantan",
    "京都府木津川市": "kyoto/sc_kizugawa",
    "大阪府大阪市都島区": "osaka/sc_osakashimiyakojima",
    "大阪府大阪市福島区": "osaka/sc_osakashifukushima",
    "大阪府大阪市此花区": "osaka/sc_osakashikonohana",
    "大阪府大阪市西区": "osaka/sc_osakashinishi",
    "大阪府大阪市港区": "osaka/sc_osakashiminato",
    "大阪府大阪市大正区": "osaka/sc_osakashitaisho",
    "大阪府大阪市天王寺区": "osaka/sc_osakashitennoji",
    "大阪府大阪市浪速区": "osaka/sc_osakashinaniwa",
    "大阪府大阪市西淀川区": "osaka/sc_osakashinishiyodogawa",
    "大阪府大阪市東淀川区": "osaka/sc_osakashihigashiyodogawa",
    "大阪府大阪市東成区": "osaka/sc_osakashihigashinari",
    "大阪府大阪市生野区": "osaka/sc_osakashiino",
    "大阪府大阪市旭区": "osaka/sc_osakashiasahi",
    "大阪府大阪市城東区": "osaka/sc_osakashijoto",
    "大阪府大阪市阿倍野区": "osaka/sc_osakashiabeno",
    "大阪府大阪市住吉区": "osaka/sc_osakashisumiyoshi",
    "大阪府大阪市東住吉区": "osaka/sc_osakashihigashisumiyoshi",
    "大阪府大阪市西成区": "osaka/sc_osakashinishinari",
    "大阪府大阪市淀川区": "osaka/sc_osakashiyodogawa",
    "大阪府大阪市鶴見区": "osaka/sc_osakashitsurumi",
    "大阪府大阪市住之江区": "osaka/sc_osakashisuminoe",
    "大阪府大阪市平野区": "osaka/sc_osakashihirano",
    "大阪府大阪市北区": "osaka/sc_osakashikita",
    "大阪府大阪市中央区": "osaka/sc_osakashichuo",
    "大阪府堺市堺区": "osaka/sc_sakaishisakai",
    "大阪府堺市中区": "osaka/sc_sakaishinaka",
    "大阪府堺市東区": "osaka/sc_sakaishihigashi",
    "大阪府堺市西区": "osaka/sc_sakaishinishi",
    "大阪府堺市南区": "osaka/sc_sakaishiminami",
    "大阪府堺市北区": "osaka/sc_sakaishikita",
    "大阪府堺市美原区": "osaka/sc_sakaishimihara",
    "大阪府岸和田市": "osaka/sc_kishiwada",
    "大阪府豊中市": "osaka/sc_toyonaka",
    "大阪府池田市": "osaka/sc_ikeda",
    "大阪府吹田市": "osaka/sc_suita",
    "大阪府泉大津市": "osaka/sc_izumiotsu",
    "大阪府高槻市": "osaka/sc_takatsuki",
    "大阪府貝塚市": "osaka/sc_kaizuka",
    "大阪府守口市": "osaka/sc_moriguchi",
    "大阪府枚方市": "osaka/sc_hirakata",
    "大阪府茨木市": "osaka/sc_ibaraki",
    "大阪府八尾市": "osaka/sc_yao",
    "大阪府泉佐野市": "osaka/sc_izumisano",
    "大阪府富田林市": "osaka/sc_tondabayashi",
    "大阪府寝屋川市": "osaka/sc_neyagawa",
    "大阪府河内長野市": "osaka/sc_kawachinagano",
    "大阪府松原市": "osaka/sc_matsubara",
    "大阪府大東市": "osaka/sc_daito",
    "大阪府和泉市": "osaka/sc_izumi",
    "大阪府箕面市": "osaka/sc_mino",
    "大阪府柏原市": "osaka/sc_kashiwara",
    "大阪府羽曳野市": "osaka/sc_habikino",
    "大阪府門真市": "osaka/sc_kadoma",
    "大阪府摂津市": "osaka/sc_settsu",
    "大阪府高石市": "osaka/sc_takaishi",
    "大阪府藤井寺市": "osaka/sc_fujiidera",
    "大阪府東大阪市": "osaka/sc_higashiosaka",
    "大阪府泉南市": "osaka/sc_sennan",
    "大阪府四條畷市": "osaka/sc_shijiyonawate",
    "大阪府交野市": "osaka/sc_katano",
    "大阪府大阪狭山市": "osaka/sc_osakasayama",
    "大阪府阪南市": "osaka/sc_hannan",
    "兵庫県神戸市東灘区": "hyogo/sc_kobeshihigashinada",
    "兵庫県神戸市灘区": "hyogo/sc_kobeshinada",
    "兵庫県神戸市兵庫区": "hyogo/sc_kobeshihyogo",
    "兵庫県神戸市長田区": "hyogo/sc_kobeshinagata",
    "兵庫県神戸市須磨区": "hyogo/sc_kobeshisuma",
    "兵庫県神戸市垂水区": "hyogo/sc_kobeshitarumi",
    "兵庫県神戸市北区": "hyogo/sc_kobeshikita",
    "兵庫県神戸市中央区": "hyogo/sc_kobeshichuo",
    "兵庫県神戸市西区": "hyogo/sc_kobeshinishi",
    "兵庫県姫路市": "hyogo/sc_himeji",
    "兵庫県尼崎市": "hyogo/sc_amagasaki",
    "兵庫県明石市": "hyogo/sc_akashi",
    "兵庫県西宮市": "hyogo/sc_nishinomiya",
    "兵庫県洲本市": "hyogo/sc_sumoto",
    "兵庫県芦屋市": "hyogo/sc_ashiya",
    "兵庫県伊丹市": "hyogo/sc_itami",
    "兵庫県相生市": "hyogo/sc_aioi",
    "兵庫県豊岡市": "hyogo/sc_toyoka",
    "兵庫県加古川市": "hyogo/sc_kakogawa",
    "兵庫県赤穂市": "hyogo/sc_ako",
    "兵庫県西脇市": "hyogo/sc_nishiwaki",
    "兵庫県宝塚市": "hyogo/sc_takarazuka",
    "兵庫県三木市": "hyogo/sc_miki",
    "兵庫県高砂市": "hyogo/sc_takasago",
    "兵庫県川西市": "hyogo/sc_kawanishi",
    "兵庫県小野市": "hyogo/sc_ono",
    "兵庫県三田市": "hyogo/sc_sanda",
    "兵庫県加西市": "hyogo/sc_kasai",
    "兵庫県丹波篠山市": "hyogo/sc_tambasasayama",
    "兵庫県養父市": "hyogo/sc_yabu",
    "兵庫県丹波市": "hyogo/sc_tamba",
    "兵庫県南あわじ市": "hyogo/sc_minamiawaji",
    "兵庫県朝来市": "hyogo/sc_asago",
    "兵庫県淡路市": "hyogo/sc_awaji",
    "兵庫県宍粟市": "hyogo/sc_shiso",
    "兵庫県加東市": "hyogo/sc_kato",
    "兵庫県たつの市": "hyogo/sc_tatsuno",
    "奈良県奈良市": "nara/sc_nara",
    "奈良県大和高田市": "nara/sc_yamatotakada",
    "奈良県大和郡山市": "nara/sc_yamatokoriyama",
    "奈良県天理市": "nara/sc_tenri",
    "奈良県橿原市": "nara/sc_kashihara",
    "奈良県桜井市": "nara/sc_sakurai",
    "奈良県五條市": "nara/sc_gojo",
    "奈良県御所市": "nara/sc_gose",
    "奈良県生駒市": "nara/sc_ikoma",
    "奈良県香芝市": "nara/sc_kashiba",
    "奈良県葛城市": "nara/sc_katsuragi",
    "奈良県宇陀市": "nara/sc_uda",
    "和歌山県和歌山市": "wakayama/sc_wakayama",
    "和歌山県海南市": "wakayama/sc_kainan",
    "和歌山県橋本市": "wakayama/sc_hashimoto",
    "和歌山県有田市": "wakayama/sc_arida",
    "和歌山県御坊市": "wakayama/sc_gobo",
    "和歌山県田辺市": "wakayama/sc_tanabe",
    "和歌山県新宮市": "wakayama/sc_shingu",
    "和歌山県紀の川市": "wakayama/sc_kinokawa",
    "和歌山県岩出市": "wakayama/sc_iwade",
    "鳥取県鳥取市": "tottori/sc_tottori",
    "鳥取県米子市": "tottori/sc_yonago",
    "鳥取県倉吉市": "tottori/sc_kurayoshi",
    "鳥取県境港市": "tottori/sc_sakaiminato",
    "島根県松江市": "shimane/sc_matsue",
    "島根県浜田市": "shimane/sc_hamada",
    "島根県出雲市": "shimane/sc_izumo",
    "島根県益田市": "shimane/sc_masuda",
    "島根県大田市": "shimane/sc_oda",
    "島根県安来市": "shimane/sc_yasugi",
    "島根県江津市": "shimane/sc_gotsu",
    "島根県雲南市": "shimane/sc_unnan",
    "岡山県岡山市北区": "okayama/sc_okayamashikita",
    "岡山県岡山市中区": "okayama/sc_okayamashinaka",
    "岡山県岡山市東区": "okayama/sc_okayamashihigashi",
    "岡山県岡山市南区": "okayama/sc_okayamashiminami",
    "岡山県倉敷市": "okayama/sc_kurashiki",
    "岡山県津山市": "okayama/sc_tsuyama",
    "岡山県玉野市": "okayama/sc_tamano",
    "岡山県笠岡市": "okayama/sc_kasaoka",
    "岡山県井原市": "okayama/sc_ibara",
    "岡山県総社市": "okayama/sc_sojiya",
    "岡山県高梁市": "okayama/sc_takahashi",
    "岡山県新見市": "okayama/sc_niimi",
    "岡山県備前市": "okayama/sc_bizen",
    "岡山県瀬戸内市": "okayama/sc_setouchi",
    "岡山県赤磐市": "okayama/sc_akaiwa",
    "岡山県真庭市": "okayama/sc_maniwa",
    "岡山県美作市": "okayama/sc_mimasaka",
    "岡山県浅口市": "okayama/sc_asakuchi",
    "広島県広島市中区": "hiroshima/sc_hiroshimashinaka",
    "広島県広島市東区": "hiroshima/sc_hiroshimashihigashi",
    "広島県広島市南区": "hiroshima/sc_hiroshimashiminami",
    "広島県広島市西区": "hiroshima/sc_hiroshimashinishi",
    "広島県広島市安佐南区": "hiroshima/sc_hiroshimashiasaminami",
    "広島県広島市安佐北区": "hiroshima/sc_hiroshimashiasakita",
    "広島県広島市安芸区": "hiroshima/sc_hiroshimashiaki",
    "広島県広島市佐伯区": "hiroshima/sc_hiroshimashisaeki",
    "広島県呉市": "hiroshima/sc_kure",
    "広島県竹原市": "hiroshima/sc_takehara",
    "広島県三原市": "hiroshima/sc_mihara",
    "広島県尾道市": "hiroshima/sc_onomichi",
    "広島県福山市": "hiroshima/sc_fukuyama",
    "広島県府中市": "hiroshima/sc_fuchu",
    "広島県三次市": "hiroshima/sc_miyoshi",
    "広島県庄原市": "hiroshima/sc_shobara",
    "広島県大竹市": "hiroshima/sc_otake",
    "広島県東広島市": "hiroshima/sc_higashihiroshima",
    "広島県廿日市市": "hiroshima/sc_hatsukaichi",
    "広島県安芸高田市": "hiroshima/sc_akitakata",
    "広島県江田島市": "hiroshima/sc_etajima",
    "山口県下関市": "yamaguchi/sc_shimonoseki",
    "山口県宇部市": "yamaguchi/sc_ube",
    "山口県山口市": "yamaguchi/sc_yamaguchi",
    "山口県萩市": "yamaguchi/sc_hagi",
    "山口県防府市": "yamaguchi/sc_hofu",
    "山口県下松市": "yamaguchi/sc_kudamatsu",
    "山口県岩国市": "yamaguchi/sc_iwakuni",
    "山口県光市": "yamaguchi/sc_hikari",
    "山口県長門市": "yamaguchi/sc_nagato",
    "山口県柳井市": "yamaguchi/sc_yanai",
    "山口県美祢市": "yamaguchi/sc_mine",
    "山口県周南市": "yamaguchi/sc_shunan",
    "山口県山陽小野田市": "yamaguchi/sc_sanyoonoda",
    "徳島県徳島市": "tokushima/sc_tokushima",
    "徳島県鳴門市": "tokushima/sc_naruto",
    "徳島県小松島市": "tokushima/sc_komatsushima",
    "徳島県阿南市": "tokushima/sc_anan",
    "徳島県吉野川市": "tokushima/sc_yoshinogawa",
    "徳島県阿波市": "tokushima/sc_awa",
    "徳島県美馬市": "tokushima/sc_mima",
    "徳島県三好市": "tokushima/sc_miyoshi",
    "香川県高松市": "kagawa/sc_takamatsu",
    "香川県丸亀市": "kagawa/sc_marugame",
    "香川県坂出市": "kagawa/sc_sakaide",
    "香川県善通寺市": "kagawa/sc_zentsuji",
    "香川県観音寺市": "kagawa/sc_kanonji",
    "香川県さぬき市": "kagawa/sc_sanuki",
    "香川県東かがわ市": "kagawa/sc_higashikagawa",
    "香川県三豊市": "kagawa/sc_mitoyo",
    "愛媛県松山市": "ehime/sc_matsuyama",
    "愛媛県今治市": "ehime/sc_imabari",
    "愛媛県宇和島市": "ehime/sc_uwajima",
    "愛媛県八幡浜市": "ehime/sc_yawatahama",
    "愛媛県新居浜市": "ehime/sc_niihama",
    "愛媛県西条市": "ehime/sc_saijo",
    "愛媛県大洲市": "ehime/sc_ozu",
    "愛媛県伊予市": "ehime/sc_iyo",
    "愛媛県四国中央市": "ehime/sc_shikokuchuo",
    "愛媛県西予市": "ehime/sc_seiyo",
    "愛媛県東温市": "ehime/sc_toon",
    "高知県高知市": "kochi/sc_kochi",
    "高知県室戸市": "kochi/sc_muroto",
    "高知県安芸市": "kochi/sc_aki",
    "高知県南国市": "kochi/sc_nankoku",
    "高知県土佐市": "kochi/sc_tosa",
    "高知県須崎市": "kochi/sc_susaki",
    "高知県宿毛市": "kochi/sc_sukumo",
    "高知県土佐清水市": "kochi/sc_tosashimizu",
    "高知県四万十市": "kochi/sc_shimanto",
    "高知県香南市": "kochi/sc_konan",
    "高知県香美市": "kochi/sc_kami",
    "福岡県北九州市門司区": "fukuoka/sc_kitakyushushimoji",
    "福岡県北九州市若松区": "fukuoka/sc_kitakyushushiwakamatsu",
    "福岡県北九州市戸畑区": "fukuoka/sc_kitakyushushitobata",
    "福岡県北九州市小倉北区": "fukuoka/sc_kitakyushushikokurakita",
    "福岡県北九州市小倉南区": "fukuoka/sc_kitakyushushikokuraminami",
    "福岡県北九州市八幡東区": "fukuoka/sc_kitakyushushiyahatahigashi",
    "福岡県北九州市八幡西区": "fukuoka/sc_kitakyushushiyahatanishi",
    "福岡県福岡市東区": "fukuoka/sc_fukuokashihigashi",
    "福岡県福岡市博多区": "fukuoka/sc_fukuokashihakata",
    "福岡県福岡市中央区": "fukuoka/sc_fukuokashichuo",
    "福岡県福岡市南区": "fukuoka/sc_fukuokashiminami",
    "福岡県福岡市西区": "fukuoka/sc_fukuokashinishi",
    "福岡県福岡市城南区": "fukuoka/sc_fukuokashijonan",
    "福岡県福岡市早良区": "fukuoka/sc_fukuokashisawara",
    "福岡県大牟田市": "fukuoka/sc_omuta",
    "福岡県久留米市": "fukuoka/sc_kurume",
    "福岡県直方市": "fukuoka/sc_nogata",
    "福岡県飯塚市": "fukuoka/sc_iizuka",
    "福岡県田川市": "fukuoka/sc_tagawa",
    "福岡県柳川市": "fukuoka/sc_yanagawa",
    "福岡県八女市": "fukuoka/sc_yame",
    "福岡県筑後市": "fukuoka/sc_chikugo",
    "福岡県大川市": "fukuoka/sc_okawa",
    "福岡県行橋市": "fukuoka/sc_yukuhashi",
    "福岡県豊前市": "fukuoka/sc_buzen",
    "福岡県中間市": "fukuoka/sc_nakama",
    "福岡県小郡市": "fukuoka/sc_ogori",
    "福岡県筑紫野市": "fukuoka/sc_chikushino",
    "福岡県春日市": "fukuoka/sc_kasuga",
    "福岡県大野城市": "fukuoka/sc_onojo",
    "福岡県宗像市": "fukuoka/sc_munakata",
    "福岡県太宰府市": "fukuoka/sc_dazaifu",
    "福岡県古賀市": "fukuoka/sc_koga",
    "福岡県福津市": "fukuoka/sc_fukutsu",
    "福岡県うきは市": "fukuoka/sc_ukiha",
    "福岡県宮若市": "fukuoka/sc_miyawaka",
    "福岡県嘉麻市": "fukuoka/sc_kama",
    "福岡県朝倉市": "fukuoka/sc_asakura",
    "福岡県みやま市": "fukuoka/sc_miyama",
    "福岡県糸島市": "fukuoka/sc_itoshima",
    "福岡県那珂川市": "fukuoka/sc_nakagawa",
    "佐賀県佐賀市": "saga/sc_saga",
    "佐賀県唐津市": "saga/sc_karatsu",
    "佐賀県鳥栖市": "saga/sc_tosu",
    "佐賀県多久市": "saga/sc_taku",
    "佐賀県伊万里市": "saga/sc_imari",
    "佐賀県武雄市": "saga/sc_takeo",
    "佐賀県鹿島市": "saga/sc_kashima",
    "佐賀県小城市": "saga/sc_ogi",
    "佐賀県嬉野市": "saga/sc_ureshino",
    "佐賀県神埼市": "saga/sc_kanzaki",
    "長崎県長崎市": "nagasaki/sc_nagasaki",
    "長崎県佐世保市": "nagasaki/sc_sasebo",
    "長崎県島原市": "nagasaki/sc_shimabara",
    "長崎県諫早市": "nagasaki/sc_isahaya",
    "長崎県大村市": "nagasaki/sc_omura",
    "長崎県平戸市": "nagasaki/sc_hirado",
    "長崎県松浦市": "nagasaki/sc_matsura",
    "長崎県対馬市": "nagasaki/sc_tsushima",
    "長崎県壱岐市": "nagasaki/sc_iki",
    "長崎県五島市": "nagasaki/sc_goto",
    "長崎県西海市": "nagasaki/sc_saikai",
    "長崎県雲仙市": "nagasaki/sc_unzen",
    "長崎県南島原市": "nagasaki/sc_minamishimabara",
    "熊本県熊本市中央区": "kumamoto/sc_kumamotoshichuo",
    "熊本県熊本市東区": "kumamoto/sc_kumamotoshihigashi",
    "熊本県熊本市西区": "kumamoto/sc_kumamotoshinishi",
    "熊本県熊本市南区": "kumamoto/sc_kumamotoshiminami",
    "熊本県熊本市北区": "kumamoto/sc_kumamotoshikita",
    "熊本県八代市": "kumamoto/sc_yatsushiro",
    "熊本県人吉市": "kumamoto/sc_hitoyoshi",
    "熊本県荒尾市": "kumamoto/sc_arao",
    "熊本県水俣市": "kumamoto/sc_minamata",
    "熊本県玉名市": "kumamoto/sc_tamana",
    "熊本県山鹿市": "kumamoto/sc_yamaga",
    "熊本県菊池市": "kumamoto/sc_kikuchi",
    "熊本県宇土市": "kumamoto/sc_uto",
    "熊本県上天草市": "kumamoto/sc_kamiamakusa",
    "熊本県宇城市": "kumamoto/sc_uki",
    "熊本県阿蘇市": "kumamoto/sc_aso",
    "熊本県天草市": "kumamoto/sc_amakusa",
    "熊本県合志市": "kumamoto/sc_koshi",
    "大分県大分市": "oita/sc_oita",
    "大分県別府市": "oita/sc_beppu",
    "大分県中津市": "oita/sc_nakatsu",
    "大分県日田市": "oita/sc_hita",
    "大分県佐伯市": "oita/sc_saiki",
    "大分県臼杵市": "oita/sc_usuki",
    "大分県津久見市": "oita/sc_tsukumi",
    "大分県竹田市": "oita/sc_taketa",
    "大分県豊後高田市": "oita/sc_bungotakada",
    "大分県杵築市": "oita/sc_kitsuki",
    "大分県宇佐市": "oita/sc_usa",
    "大分県豊後大野市": "oita/sc_bungoono",
    "大分県由布市": "oita/sc_yufu",
    "大分県国東市": "oita/sc_kunisaki",
    "宮崎県宮崎市": "miyazaki/sc_miyazaki",
    "宮崎県都城市": "miyazaki/sc_miyakonojo",
    "宮崎県延岡市": "miyazaki/sc_nobeoka",
    "宮崎県日南市": "miyazaki/sc_nichinan",
    "宮崎県小林市": "miyazaki/sc_kobayashi",
    "宮崎県日向市": "miyazaki/sc_hyuga",
    "宮崎県串間市": "miyazaki/sc_kushima",
    "宮崎県西都市": "miyazaki/sc_saito",
    "宮崎県えびの市": "miyazaki/sc_ebino",
    "鹿児島県鹿児島市": "kagoshima/sc_kagoshima",
    "鹿児島県鹿屋市": "kagoshima/sc_kanoya",
    "鹿児島県枕崎市": "kagoshima/sc_makurazaki",
    "鹿児島県阿久根市": "kagoshima/sc_akune",
    "鹿児島県出水市": "kagoshima/sc_izumi",
    "鹿児島県指宿市": "kagoshima/sc_ibusuki",
    "鹿児島県西之表市": "kagoshima/sc_nishinomote",
    "鹿児島県垂水市": "kagoshima/sc_tarumizu",
    "鹿児島県薩摩川内市": "kagoshima/sc_satsumasendai",
    "鹿児島県日置市": "kagoshima/sc_hioki",
    "鹿児島県曽於市": "kagoshima/sc_so",
    "鹿児島県霧島市": "kagoshima/sc_kirishima",
    "鹿児島県いちき串木野市": "kagoshima/sc_ichikikushikino",
    "鹿児島県南さつま市": "kagoshima/sc_minamisatsuma",
    "鹿児島県志布志市": "kagoshima/sc_shibushi",
    "鹿児島県奄美市": "kagoshima/sc_amami",
    "鹿児島県南九州市": "kagoshima/sc_minamikyushu",
    "鹿児島県伊佐市": "kagoshima/sc_isa",
    "鹿児島県姶良市": "kagoshima/sc_aira",
    "沖縄県那覇市": "okinawa/sc_naha",
    "沖縄県宜野湾市": "okinawa/sc_ginowan",
    "沖縄県石垣市": "okinawa/sc_ishigaki",
    "沖縄県浦添市": "okinawa/sc_urasoe",
    "沖縄県名護市": "okinawa/sc_nago",
    "沖縄県糸満市": "okinawa/sc_itoman",
    "沖縄県沖縄市": "okinawa/sc_okinawa",
    "沖縄県豊見城市": "okinawa/sc_tomigusuku",
    "沖縄県うるま市": "okinawa/sc_uruma",
    "沖縄県宮古島市": "okinawa/sc_miyakojima",
    "沖縄県南城市": "okinawa/sc_nanjo",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def clean_text(text):
    return re.sub(r'（.*?）', '', text).strip() if text else ""


def parse_price(price_str):
    """価格文字列を万円の整数に変換 (例: "2,500万円" → 2500)"""
    try:
        s = (price_str
             .replace(',', '')
             .replace('円', '')
             .replace(' ', '')
             .replace('\u00a0', ''))
        if '億' in s:
            parts = s.split('億')
            oku = int(parts[0]) * 10000
            man_str = parts[1].replace('万', '').strip() if parts[1] else '0'
            man = int(man_str) if man_str else 0
            return oku + man
        elif '万' in s:
            return int(s.replace('万', '').strip())
        return None
    except Exception:
        return None


def categorize_price(price_man):
    if price_man is None:
        return None
    if price_man <= 1500:
        return "0-1500万"
    elif price_man <= 3000:
        return "1501-3000万"
    else:
        return "3001万-"


def compute_segments(data, price_col_index):
    """スクレイピングデータを価格セグメントに分類して件数を返す"""
    segments = {"0-1500万": 0, "1501-3000万": 0, "3001万-": 0}
    if len(data) <= 1:
        return segments
    for row in data[1:]:
        if len(row) > price_col_index:
            price = parse_price(row[price_col_index])
            cat = categorize_price(price)
            if cat:
                segments[cat] += 1
    return segments


# ---------- パーサー定義 ----------

def parse_area_old_houses(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "販売価格", "土地面積", "建物面積", "間取り", "築年月"]]
    boxes = soup.select('.dottable.dottable--cassette')
    for box in boxes:
        try:
            location = box.find('dt', string='所在地').find_next('dd').text.strip()
            price = box.find('dt', string='販売価格').find_next('dd').text.strip()
            land_area = clean_text(box.find('dt', string='土地面積').find_next('dd').text.strip())
            building_area = clean_text(box.find('dt', string='建物面積').find_next('dd').text.strip())
            layout = box.find('dt', string='間取り').find_next('dd').text.strip()
            built_year = box.find('dt', string='築年月').find_next('dd').text.strip()
            results.append([location, price, land_area, building_area, layout, built_year])
        except Exception as e:
            print(f"[area_old_houses] Error: {e}")
            continue
    return results


def parse_area_old_apartments(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "物件名", "販売価格", "専有面積", "バルコニー", "間取り", "築年月"]]
    boxes = soup.select('.dottable.dottable--cassette')
    for box in boxes:
        try:
            location = box.find('dt', string='所在地').find_next('dd').text.strip()
            name = box.find('dt', string='物件名').find_next('dd').text.strip()
            price = box.find('dt', string='販売価格').find_next('dd').text.strip()
            area = clean_text(box.find('dt', string='専有面積').find_next('dd').text.strip())
            balcony = clean_text(box.find('dt', string='バルコニー').find_next('dd').text.strip())
            layout = box.find('dt', string='間取り').find_next('dd').text.strip()
            built_year = box.find('dt', string='築年月').find_next('dd').text.strip()
            results.append([location, name, price, area, balcony, layout, built_year])
        except Exception as e:
            print(f"[area_old_apartments] Error: {e}")
            continue
    return results


def parse_client_old_houses(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "販売価格", "土地面積", "建物面積", "間取り", "築年月"]]
    boxes = soup.select("li.cassette.js-bukkenCassette")
    for box in boxes:
        try:
            dl_elements = box.select("dl.tableinnerbox")
            data = {}
            for dl in dl_elements:
                key = dl.find("dt").text.strip()
                value = dl.find("dd").text.strip()
                data[key] = value
            location = data.get("所在地", "")
            price = data.get("販売価格", "")
            land_area = clean_text(data.get("土地面積", ""))
            building_area = clean_text(data.get("建物面積", ""))
            layout = data.get("間取り", "")
            built_year = data.get("築年月", "")
            results.append([location, price, land_area, building_area, layout, built_year])
        except Exception as e:
            print(f"[client_old_houses] Error: {e}")
            continue
    return results


def parse_client_old_apartments(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "物件名", "販売価格", "専有面積", "バルコニー", "間取り", "築年月"]]
    boxes = soup.select("li.cassette.js-bukkenCassette")
    for box in boxes:
        try:
            name = box.select_one(".listtitleunit-title a").text.strip()
            dl_elements = box.select("dl.tableinnerbox")
            data = {}
            for dl in dl_elements:
                key = dl.find("dt").text.strip()
                value = dl.find("dd").text.strip()
                data[key] = value
            location = data.get("所在地", "")
            price = data.get("販売価格", "")
            area = clean_text(data.get("専有面積", ""))
            balcony = clean_text(data.get("バルコニー", ""))
            layout = data.get("間取り", "")
            built_year = data.get("築年月", "")
            results.append([location, name, price, area, balcony, layout, built_year])
        except Exception as e:
            print(f"[client_old_apartments] Error: {e}")
            continue
    return results


def scrape_all_pages(url, target):
    """指定URLのすべてのページをスクレイピングして結果を返す"""
    result = []
    page = 1
    while True:
        paged_url = f"{url}?page={page}" if page > 1 else url
        try:
            res = requests.get(paged_url, headers=HEADERS, timeout=20)
            if res.status_code != 200:
                break
            html = res.text

            if target == 'area_old_houses':
                parsed = parse_area_old_houses(html)
            elif target == 'area_old_apartments':
                parsed = parse_area_old_apartments(html)
            elif target == 'client_old_houses':
                parsed = parse_client_old_houses(html)
            elif target == 'client_old_apartments':
                parsed = parse_client_old_apartments(html)
            else:
                break

            if len(parsed) <= 1:
                break
            if page == 1:
                result.extend(parsed)
            else:
                result.extend(parsed[1:])
            page += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] Failed on page {page}: {e}")
            break
    return result


# ---------- APIエンドポイント ----------

@app.route('/process', methods=['POST'])
def process():
    """既存エンドポイント（後方互換性のため維持）"""
    req_data = request.json
    target = req_data.get('target')
    url = req_data.get('url')
    if not url or not target:
        return jsonify({'error': 'Missing required parameters'}), 400
    result = scrape_all_pages(url, target)
    return jsonify({'data': result})


@app.route('/search-area', methods=['POST'])
def search_area():
    """
    日本語のエリア名からSUUMOのエリアパスを辞書引きして返す。
    入力例: { "area_name": "兵庫県姫路市" }
    出力例: { "path": "hyogo/sc_himeji", "city_name": "兵庫県姫路市" }

    マッチ優先順位:
      1. 完全一致
      2. 入力が辞書キーに含まれる（部分一致・前方）
      3. 辞書キーが入力に含まれる（部分一致・後方）
    """
    req_data = request.get_json()
    area_name = req_data.get('area_name', '').strip()

    if not area_name:
        return jsonify({'error': 'area_name is required'}), 400

    # 1. 完全一致
    if area_name in AREA_MAP:
        return jsonify({'path': AREA_MAP[area_name], 'city_name': area_name})

    # 2. 入力文字列がキーに含まれる（例: "姫路市" → "兵庫県姫路市"）
    forward = [(k, v) for k, v in AREA_MAP.items() if area_name in k]
    if forward:
        # キー長が短い順（より具体的な候補）を優先
        forward.sort(key=lambda x: len(x[0]))
        k, v = forward[0]
        return jsonify({'path': v, 'city_name': k})

    # 3. キーが入力に含まれる（例: "兵庫県姫路市中心部" → "兵庫県姫路市"）
    reverse = [(k, v) for k, v in AREA_MAP.items() if k in area_name]
    if reverse:
        reverse.sort(key=lambda x: len(x[0]), reverse=True)
        k, v = reverse[0]
        return jsonify({'path': v, 'city_name': k})

    return jsonify({
        'error': (
            f'"{area_name}" は対応エリアに見つかりませんでした。'
            '都道府県名＋市区町村名で入力してください（例：兵庫県姫路市）'
        )
    }), 404


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    エリアパス・企業URLを受け取り、エリア全体と企業のシェアを計算して返す。
    """
    req_data = request.get_json()
    area_path = req_data.get('area_path', '').strip()
    condo_url = req_data.get('condo_url', '').strip()
    house_url = req_data.get('house_url', '').strip()

    if not area_path:
        return jsonify({'error': 'area_path is required'}), 400

    # ── マンション分析 ──
    area_condo_data = scrape_all_pages(
        f"https://suumo.jp/chukomansion/{area_path}/", 'area_old_apartments'
    )
    area_condo_count = max(0, len(area_condo_data) - 1)

    client_condo_data = []
    if condo_url:
        client_condo_data = scrape_all_pages(condo_url, 'client_old_apartments')
    client_condo_count = max(0, len(client_condo_data) - 1)

    condo_share = (
        round(client_condo_count / area_condo_count * 100, 2)
        if area_condo_count > 0 else 0.0
    )

    area_condo_seg = compute_segments(area_condo_data, 2)
    client_condo_seg = compute_segments(client_condo_data, 2)
    condo_segments = {}
    for seg in ["0-1500万", "1501-3000万", "3001万-"]:
        a = area_condo_seg.get(seg, 0)
        c = client_condo_seg.get(seg, 0)
        condo_segments[seg] = {
            "area": a, "client": c,
            "share": round(c / a * 100, 2) if a > 0 else 0.0
        }

    # ── 戸建て分析 ──
    area_house_data = scrape_all_pages(
        f"https://suumo.jp/chukoikkodate/{area_path}/", 'area_old_houses'
    )
    area_house_count = max(0, len(area_house_data) - 1)

    client_house_data = []
    if house_url:
        client_house_data = scrape_all_pages(house_url, 'client_old_houses')
    client_house_count = max(0, len(client_house_data) - 1)

    house_share = (
        round(client_house_count / area_house_count * 100, 2)
        if area_house_count > 0 else 0.0
    )

    area_house_seg = compute_segments(area_house_data, 1)
    client_house_seg = compute_segments(client_house_data, 1)
    house_segments = {}
    for seg in ["0-1500万", "1501-3000万", "3001万-"]:
        a = area_house_seg.get(seg, 0)
        c = client_house_seg.get(seg, 0)
        house_segments[seg] = {
            "area": a, "client": c,
            "share": round(c / a * 100, 2) if a > 0 else 0.0
        }

    return jsonify({
        'area_path': area_path,
        'condo': {
            'area_total': area_condo_count,
            'client_total': client_condo_count,
            'share': condo_share,
            'segments': condo_segments
        },
        'house': {
            'area_total': area_house_count,
            'client_total': client_house_count,
            'share': house_share,
            'segments': house_segments
        }
    })


# ---------- Flask起動 ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
