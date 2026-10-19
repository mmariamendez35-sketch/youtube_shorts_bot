# multilingual.py
"""Multilingual localization module for YouTube videos.
Translates video Titles and Descriptions into the world's most spoken languages
using YouTube Data API v3's native localizations feature.
This allows YouTube users worldwide to see the video in their native language
(English, Portuguese, French, German, Italian, etc.), multiplying global reach.
"""
import logging
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO)

# Most spoken global languages supported on YouTube
TARGET_LANGUAGES = {
    "en": "English",
    "pt": "Portuguese",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "hi": "Hindi",
    "ar": "Arabic",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "id": "Indonesian",
    "tl": "Tagalog / Filipino",
}

# Translation dictionary for prayer themes & standard templates
THEME_TRANSLATIONS = {
    "oración de la mañana": {
        "en": ("Morning Prayer to Start Your Day with God", "Start your morning in the presence of God. A powerful prayer that opens doors and brings peace. Comment AMEN."),
        "pt": ("Oração da Manhã para Começar o Dia com Deus", "Comece sua manhã na presença de Deus. Uma oração poderosa que abre portas e traz paz. Comente AMÉM."),
        "fr": ("Prière du Matin pour Commencer la Journée avec Dieu", "Commencez votre journée en présence de Dieu. Une prière puissante qui ouvre les portes. Commentez AMEN."),
        "de": ("Morgengebet, um den Tag mit Gott zu Beginnen", "Beginnen Sie Ihren Tag in Gottes Gegenwart. Ein kraftvolles Gebet. Kommentieren Sie AMEN."),
        "it": ("Preghiera del Mattino per Iniziare la Giornata con Dio", "Inizia la giornata alla presenza di Dio. Una preghiera potente. Commenta AMEN."),
        "pt-BR": ("Oração da Manhã Poderosa", "Comece o dia com fé e proteção divina. Comente AMÉM."),
    },
    "protección": {
        "en": ("Powerful Prayer for Family Protection", "Heavenly Father, cover my family with your mantle of divine protection. No harm shall come near our home. Comment AMEN."),
        "pt": ("Oração Poderosa de Proteção para a Família", "Senhor, cubra minha família com seu manto de proteção divina. Nenhum mal nos atingirá. Comente AMÉM."),
        "fr": ("Prière Puissante de Protection pour la Famille", "Seigneur, protège ma famille de tout mal. Que ta paix remplisse notre foyer. Commentez AMEN."),
        "de": ("Kraftvolles Schutzgebet für die Familie", "Herr, beschütze meine Familie vor allem Bösen. Kommentieren Sie AMEN."),
        "it": ("Preghiera Potente di Protezione per la Famiglia", "Signore, proteggi la mia famiglia da ogni male. Commenta AMEN."),
    },
    "sanación": {
        "en": ("Miracle Healing Prayer for Body and Soul", "Lord Jesus, touch every sick body and troubled heart with your healing power. Receive this miracle. Comment AMEN."),
        "pt": ("Oração de Cura e Milagre para Corpo e Alma", "Senhor Jesus, toca cada enfermo com teu poder de cura. Receba este milagre. Comente AMÉM."),
        "fr": ("Prière de Guérison Miraculeuse", "Seigneur, apporte la guérison aux corps et aux cœurs brisés. Recevez ce miracle. Commentez AMEN."),
        "de": ("Gebet für Wunderbare Heilung", "Herr, schenke Heilung für Körper und Seele. Kommentieren Sie AMEN."),
        "it": ("Preghiera di Guarigione e Miracolo", "Signore, porta guarigione e pace nel cuore. Commenta AMEN."),
    },
    "abrir caminos": {
        "en": ("Prayer to Open Doors and Clear Your Path", "God will open doors that no man can shut. Trust in His perfect timing. Comment AMEN."),
        "pt": ("Oração para Abrir Caminhos e Portas Fechadas", "Deus vai abrir portas que ninguém pode fechar. Confie no tempo d'Ele. Comente AMÉM."),
        "fr": ("Prière pour Ouvrir les Portes Fermées", "Dieu ouvre des portes que nul ne peut fermer. Ayez foi. Commentez AMEN."),
        "de": ("Gebet um Offene Türen und Neue Wege", "Gott öffnet Türen, die niemand schließen kann. Kommentieren Sie AMEN."),
        "it": ("Preghiera per Aprire Nuove Porte", "Dio aprirà porte che nessuno può chiudere. Commenta AMEN."),
    },
    "noche": {
        "en": ("Night Prayer for Peace and Protection Before Sleep", "Lord, as I close my eyes, I place my life in your hands. Grant me peaceful sleep. Comment AMEN."),
        "pt": ("Oração da Noite para Dormir em Paz com Deus", "Senhor, coloco minha noite e meu sono em tuas mãos. Que teus anjos nos guardem. Comente AMÉM."),
        "fr": ("Prière du Soir avant de Dormir", "Seigneur, je te confie ma nuit. Donne-moi ton repos et ta paix. Commentez AMEN."),
        "de": ("Abendgebet vor dem Schlafen", "Herr, schenke mir Frieden und erholsamen Schlaf. Kommentieren Sie AMEN."),
        "it": ("Preghiera della Sera prima di Dormire", "Signore, affido a te questa notte. Donami pace e protezione. Commenta AMEN."),
    },
}

GENERIC_TRANSLATIONS = {
    "en": ("🙏 Powerful Prayer that Transforms Lives", "A powerful prayer of faith, hope, and divine transformation. Subscribe for daily prayers and comment AMEN! #Prayer #Faith #God #Miracle #Shorts"),
    "pt": ("🙏 Oração Poderosa que Transforma Vidas", "Uma oração poderosa de fé, esperança e transformação. Inscreva-se para orações diárias e comente AMÉM! #Oração #Fé #Deus #Milagre #Shorts"),
    "fr": ("🙏 Prière Puissante qui Transforme les Vies", "Une prière puissante de foi et d'espérance. Abonnez-vous pour des prières quotidiennes et commentez AMEN! #Prière #Foi #Dieu #Miracle #Shorts"),
    "de": ("🙏 Kraftvolles Gebet, das Leben Verändert", "Ein starkes Gebet des Glaubens und der Hoffnung. Abonnieren Sie für tägliche Gebete und kommentieren Sie AMEN! #Gebet #Glaube #Gott #Shorts"),
    "it": ("🙏 Preghiera Potente che Trasforma la Vita", "Una preghiera profonda di fede e speranza. Iscriviti per preghiere quotidiane e commenta AMEN! #Preghiera #Fede #Dio #Miracolo #Shorts"),
    "hi": ("🙏 शक्तिशाली प्रार्थना जो जीवन बदल देती है", "विश्वास और आशा की शक्तिशाली प्रार्थना। दैनिक प्रार्थनाओं के लिए सदस्यता लें और AMEN लिखें! #Prayer #Faith #God"),
    "ar": ("🙏 صلاة قوية تغير الحياة وتجدد الإيمان", "صلاة روحية تملأ القلب بالسلام والبركة. اشترك لمزيد من الصلوات اليومية واكتب آمين. #صلاة #إيمان #الله"),
    "ru": ("🙏 Мощная молитва, меняющая жизнь", "Искренняя молитва веры, надежды и исцеления. Подписывайтесь на ежедневные молитвы и пишите АМИНЬ! #Молитва #Вера #Бог"),
    "ja": ("🙏 人生を変える強力な祈り", "信仰と希望に満ちた祈り。日々の祈りのためにチャンネル登録し、アーメンとコメントしてください。 #祈り #信仰 #神"),
    "ko": ("🙏 삶을 변화시키는 강력한 기도", "믿음과 평안을 주는 기도의 시간입니다. 매일 기도를 위해 구독하시고 아멘을 남겨주세요. #기도 #믿음 #은혜"),
    "id": ("🙏 Doa Kuat yang Mengubah Kehidupan", "Doa penuh iman, harapan, dan perlindungan Tuhan. Berlangganan untuk doa harian dan tulis AMIN! #Doa #Iman #Tuhan"),
    "tl": ("🙏 Makapangyarihang Panalangin na Nagbabago ng Buhay", "Isang panalangin ng pananampalataya at pag-asa. Mag-subscribe para sa araw-araw na panalangin at mag-comment ng AMEN! #Panalangin #Diyos"),
}

def generate_localizations(spanish_title: str, spanish_description: str) -> Dict[str, Dict[str, str]]:
    """Generate localized titles and descriptions for YouTube's native localization system.
    Returns dict formatted for YouTube API:
    {
        "en": {"title": "...", "description": "..."},
        "pt": {"title": "...", "description": "..."},
        ...
    }
    """
    localizations = {}
    title_lower = spanish_title.lower()

    # Check for specific matched theme
    matched_theme = None
    for key in THEME_TRANSLATIONS:
        if key in title_lower:
            matched_theme = key
            break

    # Build localizations for each language
    for lang, (gen_title, gen_desc) in GENERIC_TRANSLATIONS.items():
        if matched_theme and lang in THEME_TRANSLATIONS[matched_theme]:
            loc_title, loc_desc = THEME_TRANSLATIONS[matched_theme][lang]
            title_text = f"🙏 {loc_title[:90]} #Shorts" if "#shorts" in title_lower else f"🙏 {loc_title[:95]}"
            desc_text = f"{loc_desc}\n\n🙏 Oraciones que transforman\n#Prayer #Faith #God #Miracle"
        else:
            title_text = f"{gen_title[:90]} #Shorts" if "#shorts" in title_lower else f"{gen_title[:95]}"
            desc_text = gen_desc

        localizations[lang] = {
            "title": title_text[:100],
            "description": desc_text[:5000],
        }

    return localizations
