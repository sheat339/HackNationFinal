"""
PKD/NACE code mapping and sector definitions.
"""

from typing import Dict

PKD_DIVISIONS_2007: Dict[str, str] = {
    "01": "Uprawy rolne, chów i hodowla zwierząt, łowiectwo, włączając działalność usługową",
    "02": "Leśnictwo i pozyskiwanie drewna",
    "03": "Rybołówstwo i akwakultura",
    "05": "Górnictwo węgla kamiennego",
    "06": "Górnictwo ropy naftowej i gazu ziemnego",
    "07": "Górnictwo rud metali",
    "08": "Pozostałe górnictwo",
    "09": "Działalność wspomagająca górnictwo",
    "10": "Produkcja żywności",
    "11": "Produkcja napojów",
    "13": "Produkcja wyrobów tekstylnych",
    "14": "Produkcja odzieży",
    "15": "Produkcja skóry i wyrobów ze skóry",
    "16": "Produkcja drewna i wyrobów z drewna",
    "17": "Produkcja papieru i wyrobów z papieru",
    "18": "Drukowanie i reprodukcja zapisanych nośników informacji",
    "19": "Produkcja koksu i produktów rafinacji ropy naftowej",
    "20": "Produkcja chemikaliów i wyrobów chemicznych",
    "21": "Produkcja podstawowych produktów farmaceutycznych i preparatów farmaceutycznych",
    "22": "Produkcja wyrobów z gumy i tworzyw sztucznych",
    "23": "Produkcja wyrobów z pozostałych surowców niemetalicznych",
    "24": "Produkcja metali",
    "25": "Produkcja wyrobów metalowych",
    "26": "Produkcja komputerów, wyrobów elektronicznych i optycznych",
    "27": "Produkcja maszyn i urządzeń, gdzie indziej niesklasyfikowana",
    "28": "Produkcja pojazdów samochodowych, przyczep i naczep",
    "29": "Produkcja pozostałego sprzętu transportowego",
    "30": "Produkcja mebli",
    "31": "Produkcja pozostałych wyrobów",
    "32": "Naprawa, konserwacja i instalacja maszyn i urządzeń",
    "33": "Dostawa energii elektrycznej, gazu, pary wodnej i gorącej wody",
    "35": "Dostawa wody; gospodarowanie ściekami i odpadami oraz działalność związana z rekultywacją",
    "36": "Budownictwo",
    "41": "Działalność związana z budową budynków",
    "42": "Budowa obiektów inżynierii lądowej i wodnej",
    "43": "Przygotowanie terenu pod budowę",
    "45": "Handel hurtowy i detaliczny pojazdami samochodowymi; naprawa pojazdów samochodowych",
    "46": "Handel hurtowy, z wyłączeniem handlu pojazdami samochodowymi",
    "47": "Handel detaliczny, z wyłączeniem handlu pojazdami samochodowymi",
    "49": "Transport lądowy oraz transport rurociągowy",
    "50": "Transport wodny",
    "51": "Transport lotniczy",
    "52": "Magazynowanie i działalność usługowa wspomagająca transport",
    "53": "Działalność pocztowa i kurierska",
    "55": "Zakwaterowanie",
    "56": "Działalność związana z organizacją imprez kulturalnych i rozrywkowych",
    "58": "Działalność wydawnicza",
    "59": "Produkcja filmów, nagrań wideo, programów telewizyjnych, nagrań dźwiękowych i muzycznych",
    "60": "Nadawanie programów i działalność związana z nadawaniem programów",
    "61": "Telekomunikacja",
    "62": "Działalność związana z oprogramowaniem i doradztwem w zakresie informatyki oraz działalność powiązana",
    "63": "Działalność usługowa w zakresie informacji",
    "64": "Działalność usługowa w zakresie pośrednictwa finansowego",
    "65": "Ubezpieczenia, reasekuracja oraz fundusze emerytalne, z wyłączeniem obowiązkowego ubezpieczenia społecznego",
    "66": "Działalność wspomagająca usługi finansowe oraz ubezpieczenia i fundusze emerytalne",
    "68": "Obrót nieruchomościami",
    "69": "Działalność prawnicza i rachunkowo-księgowa",
    "70": "Działalność firm centralnych (head offices); działalność doradcza związana z zarządzaniem",
    "71": "Działalność w zakresie architektury i inżynierii; badania i analizy techniczne",
    "72": "Badania naukowe i prace rozwojowe",
    "73": "Reklama, badanie rynku i opinii publicznej",
    "74": "Działalność profesjonalna, naukowa i techniczna, pozostała",
    "75": "Działalność weterynaryjna",
    "77": "Dzierżawa i najem",
    "78": "Działalność związana z zatrudnieniem",
    "79": "Działalność związana z organizacją podróży, pośrednictwem turystycznym i pokrewnym",
    "80": "Działalność detektywistyczna i ochroniarska",
    "81": "Działalność związana z utrzymaniem porządku w budynkach i zagospodarowaniem terenów zieleni",
    "82": "Działalność związana z administrowaniem i działalność wspierająca",
    "85": "Edukacja",
    "86": "Opieka zdrowotna",
    "87": "Pomoc społeczna z zakwaterowaniem",
    "88": "Pomoc społeczna bez zakwaterowania",
    "90": "Działalność twórcza związana z kulturą i rozrywką",
    "91": "Biblioteki, archiwa, muzea oraz pozostała działalność związana z kulturą",
    "92": "Działalność związana z grami losowymi i zakładami wzajemnymi",
    "93": "Działalność związana ze sportem, rozrywką i rekreacją",
    "94": "Działalność organizacji członkowskich",
    "95": "Naprawa komputerów i artykułów użytku osobistego i domowego",
    "96": "Pozostała działalność usługowa",
    "97": "Gospodarstwa domowe zatrudniające pracowników; gospodarstwa domowe produkujące wyroby i świadczące usługi na własne potrzeby",
    "98": "Gospodarstwa domowe produkujące wyroby i świadczące usługi na własne potrzeby",
    "99": "Organizacje i zespoły eksterytorialne"
}

def get_pkd_division_name(code: str) -> str:
    """
    Get PKD division name by code.
    
    Args:
        code: PKD division code (2-digit)
        
    Returns:
        Division name or "Unknown division" if code not found
    """
    return PKD_DIVISIONS_2007.get(code, "Nieznany dział")


def get_all_divisions() -> Dict[str, str]:
    """
    Get all available PKD divisions.
    
    Returns:
        Dictionary mapping PKD codes to division names
    """
    return PKD_DIVISIONS_2007.copy()

