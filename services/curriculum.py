"""Curriculum: real Uzbek school topic titles per (subject, grade).

Keys are (subject_name, grade_num). Values are ordered lists of topic titles
that match the official Davlat ta'lim standarti (DTS) / DTS fanidan ishlanma
mavzulari. The lesson content and quizzes are generated on-demand by the AI
service; only the titles need to be precise and pedagogically correct.
"""

from typing import Dict, List, Tuple

# Sub-topics per topic title. Used by AI to scope lesson generation and
# by the webapp to show a detailed outline before the lesson is loaded.
SUBTOPICS: Dict[str, List[str]] = {
    # Ona tili
    "Unlilar va undoshlar": ["Unlilar turlari", "Undoshlar tasnifi (sokin, jahriy, jarangli)",
                              "Bo'g'in hosil bo'lishi", "Unlilar va undoshlar farqi"],
    "So'z turlari": ["Ot", "Fe'l", "Sifat", "Ravish", "Son", "O'rnlik", "Bog'lovchi", "Yuklama", "Undov"],
    "Gap tuzilishi": ["Ega va kesim", "Ikkkinchi darajali bo'laklar",
                      "Gap tartibi (SOV)", "Gap turlari"],
    # Tarix 5-sinf
    "O'zbekiston tarixi: qadimgi davr": ["Ilk davlatlar", "Buyuk Ipak yo'li", "Amir Temur davri",
                                         "Shayboniylar davri", "Me'morchilik yutuqlari"],
    "Markaziy Osiyo ilk davlatlari": ["Baqtriya", "Sug'diyona", "Xorazm",
                                       "Dehiston va Afrosiyob", "Hunlar va Kangarlar"],
    "Buyuk Ipak yo'li": ["Ipak yo'lining paydo bo'lishi", "Ipak yo'li shaharlari",
                          "Savdo va madaniy almashinuv", "Ipak yo'lining ta'siri"],
    "Amir Temur va Temuriylar davlati": ["Amir Temur hayoti", "Temuriylar davlati",
                                          "Sohibqiron yutuqlari", "Temur tuzuklari"],
    # Adabiyot
    "O'zbek xalq ertaklari": ["Sehrli ertaklar", "Hayotiy ertaklar",
                               "Hayvonlar haqidagi ertaklar", "Ertaklarning xususiyatlari"],
    "Alisher Navoiy hayoti va ijodi": ["Navoiy hayoti", "Xamsa", "Lison ut-Tayr",
                                        "Muhakamat al-Lughatayn", "Devonlari"],
}

CURRICULUM: Dict[Tuple[str, int], List[str]] = {
    # ============================================================
    # ONA TILI (5-11 sinflar)
    # ============================================================
    ("native_language", 5): [
        "Unlilar va undoshlar",
        "So'z turlari",
        "Gap tuzilishi",
        "Bosh va kichik harflar",
        "So'zning ma'noviy turlari",
        "Fe'lning shaxs-son qo'shimchalari",
    ],
    ("native_language", 6): [
        "Ot so'z turkumi",
        "Sifat va uning turlari",
        "Son so'z turkumi",
        "O'rnliklar tizimi",
        "Fe'lning vazifaviy shakllari",
        "Ravish va uning ma'noviy turlari",
        "Yuklamalar",
        "Bog'lovchilar va undovlar",
    ],
    ("native_language", 7): [
        "Sodda gap sintaksisi",
        "Gap bo'laklari (ega, kesim)",
        "Ikkinci darajali bo'laklar",
        "Uyushiq bo'lakli gap",
        "Murakkab ohang va ohang mayli",
        "Tinish belgilari",
        "To'g'ri va ko'chma ma'noli so'zlar",
    ],
    ("native_language", 8): [
        "Qo'shma gap turlari",
        "Bog'langan va ergashgan qo'shma gaplar",
        "Ergash gap turlari (ega, kesim, to'ldiruvchi, aniqlovchi, hol)",
        "Matn va uning turlari",
        "O'zbek tilining imkoniyatlari",
        "Rasmiy-ish yuritish uslubi",
    ],
    ("native_language", 9): [
        "O'zbek tilining tarixiy taraqqiyoti",
        "Yozuv va imlo qoidalari",
        "Leksikologiya asoslari",
        "Frazeologizmlar",
        "Sinonimlar, antonimlar, omonimlar",
        "Uslubiy bo'yoqdor so'zlar",
        "Nutq madaniyati va etikasi",
    ],
    ("native_language", 10): [
        "Fonetika va fonologiya",
        "Leksikografiya",
        "Sohibqiron Amir Temur davri o'zbek til",
        "Hozirgi o'zbek adabiy tili",
        "Imlo va tinish belgilari qoidalari",
        "Matn tahlili va uslubi",
    ],
    ("native_language", 11): [
        "O'zbek tilining davlat tili maqomi",
        "Ona tili — milliy ma'naviyat ramzi",
        "Nutqiy kompetensiya",
        "Ilmiy uslub va rasmiy uslub",
        "Ommaviy axomirot vositalari tili",
        "Tildagi yangi hodisalar va ularning o'rni",
        "Milliy sertifikat imtihoni: ona tili",
    ],
    # ============================================================
    # ADABIYOT (5-11 sinflar)
    # ============================================================
    ("literature", 5): [
        "O'zbek xalq ertaklari",
        "Alisher Navoiy hayoti va ijodi",
        "Zahiriddin Muhammad Bobur",
        "Ogaki ijod namunalari",
        "Maqol va matallar",
        "Latifalar (Nasriddin afandi)",
    ],
    ("literature", 6): [
        "Xalq qo'shiqlari va terma",
        "Tog'ay va Tog'achi",
        "G'afur G'ulom hayoti va ijodi",
        "Oybek — o'zbek romanchiligining asoschisi",
        "Cho'lpon hayoti va she'riyati",
        "Abdulla Qahhor — hikoyanavis",
        "Said Ahmad hikoyalari",
    ],
    ("literature", 7): [
        "Alisher Navoiy g'azallari",
        "Bobur she'rlari",
        "Muqimiylar davri adabiyoti",
        "Zokirjon Furqat ijodi",
        "Mahmudxo'ja Behbudiy",
        "Abdurauf Fitrat hayoti va ijodi",
        "Cho'lpon — milliy uyg'onish adabiyoti",
    ],
    ("literature", 8): [
        "O'zbek adabiyoti: XX asr birinchi yarmi",
        "Oybek romanlari",
        "Abdulla Qahhor dramalari",
        "G'afur G'ulom she'riyati",
        "Mirtemir ijodi",
        "Said Ahmad va Omon Muxtor hikoyalari",
        "Ma'rifatparvarlik adabiyoti",
    ],
    ("literature", 9): [
        "O'zbek adabiyoti: urush davri va undan keyin",
        "She'riyatda urush mavzusi",
        "O'tkir Hoshimov hikoyalari",
        "Pirimqul Qodirov tarixiy romanlari",
        "Tog'ay Murod — proza ustasi",
        "Tarixiy va zamonaviy dramalar",
        "Adabiy tanqid asoslari",
    ],
    ("literature", 10): [
        "Mustaqillik davri o'zbek adabiyoti",
        "Erkin A'zam ijodi",
        "Shavkat Rahmon — zamonaviy she'riyat",
        "Roman va novella san'ati",
        "Adabiy meros va uning o'rganilishi",
        "Adabiyotshunoslik asoslari",
        "Badiiy tildan foydalanish",
    ],
    ("literature", 11): [
        "O'zbek adabiyoti — milliy ma'naviyat asosi",
        "Xalq ogaki ijodi va yozma adabiyot",
        "Alisher Navoiy — o'zbek adabiyotining sultoni",
        "Bobur — shoir va saltanat egasi",
        "XX-XXI asr o'zbek adabiyoti",
        "Adabiy jarayonlar va yoğlinalishlar",
        "Milliy sertifikat imtihoni: adabiyot",
    ],
    # ============================================================
    # TARIX (5-11 sinflar)
    # ============================================================
    ("history", 5): [
        "O'zbekiston tarixi: qadimgi davr",
        "Markaziy Osiyo ilk davlatlari",
        "Buyuk Ipak yo'li",
        "Islom davri olddan Markaziy Osiyo",
        "Amir Temur va Temuriylar davlati",
        "O'zbek xonligi tashkil topishi",
        "Buxoro va Xiva xonliklari",
        "Qoqon xonligi",
    ],
    ("history", 6): [
        "Qadimgi davr davlatlari: Baqtriya va Sug'diyona",
        "Ahamoniylar davri",
        "Salavkiylar davlati",
        "Kushonlar imperiyasi",
        "Markaziy Osiyo Eftalit davlati",
        "Turk xoqonligi",
        "Arablar istilosi va islomning tarqalishi",
        "Somoniylar davlati",
    ],
    ("history", 7): [
        "Markaziy Osiyo X-XII asrlarda",
        "Qoraxoniylar davlati",
        "G'aznaviylar va Saljuqiylar",
        "Mo'g'ul istilosi va uning oqibati",
        "Chig'atoy ulusi",
        "Amir Temur hayoti va faoliyati",
        "Temuriylar davlati — temuriylar davri",
        "Ulug'bek ilmiy merosi",
    ],
    ("history", 8): [
        "XVI asr: Shayboniylar davlati",
        "Buxoro xonligi",
        "Xiva xonligi",
        "Qoqon xonligi",
        "Markaziy Osiyo rus imperiyasi tarkibida",
        "Turkiston general-gubernatorligi",
        "Mustamlaka davrida xalq harakatlari",
    ],
    ("history", 9): [
        "Jadidchilik harakati",
        "Milliy uyg'onish davri",
        "Mustaqillik uchun kurash (1917-1924)",
        "O'zSSR tashkil topishi",
        "Sovet davrida O'zbekiston",
        "Ikkinchi jahon urushi va O'zbekiston",
        "Sanoatlashtirish va maoratifi",
    ],
    ("history", 10): [
        "Sovet davri O'zbekiston (1950-1980)",
        "O'zbekiston mustaqillikka tayyorgarlik",
        "Mustaqillik e'lon qilinishi (1991)",
        "O'zbekiston — suveren davlat",
        "Konstitutsiya va davlat qurilishi",
        "O'zbekiston tashqi siyosati",
        "Iqtisodiy islohotlar",
    ],
    ("history", 11): [
        "Mustaqil O'zbekiston: taraqqiyot yo'li",
        "O'zbekiston — Markaziy Osiyoning yetakchi davlati",
        "Mintaqaviy hamkorlik",
        "O'zbekiston va jahon hamjamiyati",
        "Milliy sertifikat imtihoni: tarix",
        "Yangi O'zbekiston — 2030 strategiyasi",
        "Tarix fanining zamonaviy usullari",
    ],
}


def get_titles(subject_name: str, grade_num: int) -> List[str]:
    """Return curated topic titles for a (subject, grade) pair, or empty list."""
    return list(CURRICULUM.get((subject_name, grade_num), []))


def get_subtopics(topic_title: str) -> List[str]:
    """Return sub-topics for a given topic title, or empty list."""
    return list(SUBTOPICS.get(topic_title, []))


def all_subjects() -> List[str]:
    """Return distinct subject names in the curriculum."""
    return sorted({s for s, _ in CURRICULUM.keys()})