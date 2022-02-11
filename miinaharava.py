"""
Tekstipohjaisella valikolla toimiva graafinen miinaharava.
Tekijät: Casimir Saastamoinen, Roni Latva, Santtu Orava
"""
import random
import haravasto as hv
import time

KOPIO = []
KENTTA = []
JALJELLA = []
ROTTA = {
    hv.HIIRI_VASEN: "vasen",
    hv.HIIRI_KESKI: "keski",
    hv.HIIRI_OIKEA: "oikea"
}
TULOKSET = []
SANAKIRJA = {"koko": 0,
    "miinat": 0,
    "tulos": 0,
    "ajankohta": 0,
    "t_1": 0,
    "t_2": 0,
    "kesto_t": 0,
    "kesto_v": 0
}

def tallenna_tulos(tilasto, tiedosto):
    """
    Tallentaa pelatun pelin kohdetiedostoon yhdelle riville. 
    Jos tiedostoa ei ole printtaa huomautuksen.
    """
    try:
        with open(tiedosto, "a") as kohde:
            for tulos in tilasto:            
                kohde.write("{ajankohta}.:{kesto_t}.:{kesto_v}.:{koko}.:{miinat}.:{tulos}\n".format(
                    ajankohta=tulos["ajankohta"],
                    kesto_t=tulos["kesto_t"],
                    kesto_v=tulos["kesto_v"],
                    koko=tulos["koko"],
                    miinat=tulos["miinat"],
                    tulos=tulos["tulos"]
                ))
    except IOError:
        print("Kohdetiedostoa ei voitu avata. Tallennus epäonnistui")

def lataa_tilasto(tiedosto):    
    """
    Lataa tulokset lähdetiedostosta. Lukee tiedoston rivi kerrallaan ja antaa rivit tulostus funktiolle.
    Jos tiedostoa ei ole tai sitä on muokattu muotoon,
    josta ei kaikkia haluttuja tietoja saada, printataan huomautus.
    """
    TULOKSET = []
    try:
        with open(tiedosto) as lahde:
            for rivi in lahde.readlines():
                if rivi != None:
                    TULOKSET.append(tulostus(rivi))
    except IOError:
        print("Tiedoston avaaminen ei onnistunut. Tilastoja ei ole.")
    except ValueError:
        print("Tiedosto moukaroitu kelvottomaan muotoon. Poista tulokset.txt ja käynnistä peli uudestaan.")

def tulostus(peli):
    """
    Poimii lähdetiedoston riviltä halutut tiedot ja tulostaa ne.
    """
    ajankohta, kesto_t, kesto_v, koko, miinat, tulos = peli.split(".:")
    kanta, korkeus = koko.split(", ")
    print(ajankohta)
    print("Peli kesti {:.2f} minuuttia ja {} siirtoa.".format(
        float(kesto_t),
        kesto_v
    ))
    print("Kentän koko: {}, {}".format(kanta.strip("("), korkeus.strip(")")))
    print("Miinat: ", miinat)
    print("Tulos: ", tulos.strip("\n"))
    print()
    
def numeroi_ruudut(lista):
    """
    Käy läpi kentän johon on asetettu miinat ja lisää miinoja ympäröiviin ruutujen
    arvoihin ykkösen, jolloin ruutujen arvot vastaavat ruudun ympärillä olevien miinojen määrää.
    """
    for i, rivi in enumerate(lista):
        for j, ruutu in enumerate(rivi):
            ny = i
            nx = j
            if ruutu == "x":
                for k in range(-1, 2):
                    for l in range(-1, 2):
                        if nx + l in range(0, len(lista[0])) and ny + k in range(0, len(lista)):
                            if lista[ny + k][nx + l] == "x":
                                pass
                            else:
                                lista[ny + k][nx + l] += 1

def miinoita(mkentta, vapaat, miinat):
    """
    Asettaa käyttäjän määräämän määrän miinoja kentälle satunnaisiin paikkoihin.
    Miinat eivät asetu päällekkäin.
    """
    mruudut = random.sample(vapaat, miinat)
    for nx, ny in mruudut:
        mkentta[ny][nx] = "x"

def kasittele_hiiri(hx, hy, painike, muokkaus):
    """
    Tätä funktiota kutsutaan kun käyttäjä klikkaa sovellusikkunaa hiirellä.
    Muuntaa hiiren klikkaus koordinaatit kentän ruuduiksi, joita käytetään klikkausten käsittelyssä.
    Varmistaa, että ensimmäinen klikkaus osuu tyhjään ruutuun kun miinojen määrä on 9 pienempi
    kuin kentän koko. Pitää kirjaa klikkausten määrästä per peli.
    """
    ux = hx // 40
    uy = hy // 40
    peli_paattyy()
    if ROTTA[painike] == "vasen" and SANAKIRJA["kesto_v"] == 0:
        if len(JALJELLA) == SANAKIRJA["miinat"]:
            pass
        elif len(JALJELLA)-9 < SANAKIRJA["miinat"]:
            JALJELLA.remove((ux, uy))
        else:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if ux + i in range(0, len(KENTTA[0])) and uy + j in range(0, len(KENTTA)):
                        JALJELLA.remove((ux+i, uy+j))
        miinoita(KENTTA, JALJELLA, SANAKIRJA["miinat"])
        numeroi_ruudut(KENTTA)
    if ROTTA[painike] == "vasen":
        tarkista_vasen(ux, uy)
        SANAKIRJA["kesto_v"] += 1
    elif ROTTA[painike] == "oikea":
        tarkista_oikea(ux, uy)
    if KOPIO[uy][ux] != "x":
        tarkista_voitto()
    
def piirra_kentta():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Käy läpi kentän tilaa kuvaavaa kaksiulotteista listaa
    ja pirrtää ruudut sen perusteella.
    Funktiota kutsutaan aina kun pelimoottori pyytää
    ruudun näkymän päivitystä.
    """
    hv.tyhjaa_ikkuna()
    hv.piirra_tausta()
    hv.aloita_ruutujen_piirto()
    for a, sarake in enumerate(KOPIO):
        for b, ruutu in enumerate(sarake):
            hv.lisaa_piirrettava_ruutu(KOPIO[a][b], 40*b, 40*a)
    hv.piirra_ruudut()

def muokkaa_aika():
    """
    Asettaa pelititetoja sisältävään sanakirjaan merkkijonon johon poimitaan localtime() functiosta 
    pelin aloitus ajankohtaa koskevat tiedot (päivämäärä + kellonaika)
    """
    SANAKIRJA["ajankohta"] = "Pelattu {}.{}.{} klo {}:{:02}".format(
        SANAKIRJA["ajankohta"].tm_mday,
        SANAKIRJA["ajankohta"].tm_mon,
        SANAKIRJA["ajankohta"].tm_year,
        SANAKIRJA["ajankohta"].tm_hour,
        SANAKIRJA["ajankohta"].tm_min
    )

def muunna():
    """
    Lisää pelatun pelin tiedot sanakirjasta TULOKSET listaan sanakirjana.
    """
    TULOKSET.append({
            "ajankohta": SANAKIRJA["ajankohta"],
            "kesto_t": SANAKIRJA["kesto_t"],
            "kesto_v": SANAKIRJA["kesto_v"],
            "koko": SANAKIRJA["koko"],
            "miinat": SANAKIRJA["miinat"],
            "tulos": SANAKIRJA["tulos"]
            })
        
def peli_paattyy():
    """
    Tarkistaa onko voitto- tai häviöehto täyttynyt. 
    Ehdon täyttyessä ottaa ylös pelin päättymisajan, laskee pelin keston ja lopettaa pelin.
    """
    if SANAKIRJA["tulos"] == "voitto":
        print("Olet voittaja!")
        SANAKIRJA["t_2"] = time.perf_counter()
        SANAKIRJA["kesto_t"] = (SANAKIRJA["t_2"] - SANAKIRJA["t_1"]) / 60
        muunna()
        tallenna_tulos(TULOKSET, "tulokset.txt")
        hv.lopeta()
    elif SANAKIRJA["tulos"] == "häviö":
        print("Olet häviäjä!")
        SANAKIRJA["t_2"] = time.perf_counter()
        SANAKIRJA["kesto_t"] = (SANAKIRJA["t_2"] - SANAKIRJA["t_1"]) / 60
        muunna()
        tallenna_tulos(TULOKSET, "tulokset.txt")
        hv.lopeta()
    
def tarkista_vasen(x, y):
    """
    Tarkistaa hiiren vasemman klikkauksen koordinaattien perusteella, mitä painetussa ruudussa on.
    Jos ruutu on miina funktio paljastaa kaikki miinat ja peli päättyy seuraavalla klikkauksella.
    Jos ruutu on lippu ei tapahdu mitään.
    Jos ruutu on numero paljastaa vain tämän numero ruudun.
    Jos ruutu on tyhjä suorittaa tulvatäytön.
    """
    if KOPIO[y][x] == "f":
        pass
    elif KENTTA[y][x] == "x":
        for j, rivi in enumerate(KENTTA):
            for i, sarake in enumerate(rivi):
                if KENTTA[j][i] == "x":
                    KOPIO[j][i] = "x"
        SANAKIRJA["tulos"] = "häviö"
    elif KENTTA[y][x] in range(0, 9):
        KOPIO[y][x] = str(KENTTA[y][x])
        if KENTTA[y][x] == 0:
            tulvataytto(KENTTA, x, y)
    else:
        pass
        
def tarkista_oikea(x, y):
    """
    Lisää hiiren oikeaa painiketa painettaessa tyhjään ruutuun lipun ja lippu 
    ruutuun selän.
    """
    if KOPIO[y][x] == " ":
        KOPIO[y][x] = "f"
    elif KOPIO[y][x] == "f":
        KOPIO[y][x] = " "

def tulvataytto(lista, x, y):
    """
    Tyhjää ruutua painettaessa lisää avattujen ruutujen listaan kaikki tätä ruutua
    koskettavat tyhjät ruudut sekä näitä tyhjiä ruutuja koskettavat numero ruudut.
    """
    tulva = [(x, y)]
    while tulva:
        x, y = tulva.pop()
        lista[y][x] = "0"
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i in range(0, len(lista[0])) and y + j in range(0, len(lista)) and KOPIO[y+j][x+i] != "f":
                    if lista[y+j][x+i] in range(1, 9):
                        KOPIO[y+j][x+i] = str(lista[y+j][x+i])
                        lista[y+j][x+i] = str(lista[y+j][x+i])
                    if lista[y+j][x+i] == 0:
                        tulva.append((x + i, y + j))
                        KOPIO[y+j][x+i] = "0"

def tarkista_voitto():
    """
    Asettaa pelitietoihin tulokseksi voiton, jos avaamattomien ja liputettujen ruutujen määrä 
    on sama kuin miinojen määrä.
    """
    tyhjat = 0
    for a, sarake in enumerate(KOPIO):
        for b, ruutu in enumerate(sarake):
            if KOPIO[a][b] == " " or KOPIO[a][b] == "f":
                tyhjat += 1
    if tyhjat == SANAKIRJA["miinat"]:
        SANAKIRJA["tulos"] = "voitto"

def valikko():
    """
    Ohjelman päävalikko, josta voidaan valita aloittaa peli, katsoa edellisten pelien tietoja
    ja sulkea ohjelma.
    """
    while True:
        valinta = input("Valitse (P)elaa, (T)ulokset, (L)opeta: ")
        if valinta.lower() == "p":
            alustus()
        elif valinta.lower() == "t":
            print()
            lataa_tilasto("tulokset.txt")
        elif valinta.lower() == "l":
            break
        else:
            print("Laiton komento")

def main(x, y):
    """
    Lataa pelin grafiikat, luo peli-ikkunan ja asettaa siihen piirtokäsittelijän.
    """
    hv.lataa_kuvat("D:\\Miinaharava")
    hv.luo_ikkuna(40*x, 40*y)
    hv.aseta_piirto_kasittelija(piirra_kentta)
    hv.aseta_hiiri_kasittelija(kasittele_hiiri)
    hv.aloita()

def alustus():
    """
    Alustaa pelin joka kerta kun uusi peli aloitetaan. Nollaa edellisen pelin kenttä tiedot,
    kysyy käyttäjältä uuden pelin parametrit ja luo kentän parametrien perusteella.
    """
    KENTTA.clear()
    KOPIO.clear()
    JALJELLA.clear()
    SANAKIRJA["tulos"] = 0
    SANAKIRJA["kesto_v"] = 0
    Q = True
    while Q:
        try:
            korkeus = int(input("Anna rivien määrä: "))
            leveys = int(input("Anna sarakkeiden määrä: "))    
            while True:
                SANAKIRJA["miinat"] = int(input("Anna miinojen määrä: "))
                if SANAKIRJA["miinat"] <= korkeus*leveys:
                    Q = False
                    break
        except ValueError:
            print("Senkin aasi, ei tämä ole kokonaisluku!")
    for rivi in range(korkeus):
        KENTTA.append([])
        for sarake in range(leveys):
            KENTTA[-1].append(0)
    SANAKIRJA["koko"] = korkeus, leveys
    for x in range(leveys):
        for y in range(korkeus):
            JALJELLA.append((x, y))
    for rivi in range(korkeus):
        KOPIO.append([])
        for sarake in range(leveys):
            KOPIO[-1].append(" ")
    SANAKIRJA["t_1"] = time.perf_counter()
    SANAKIRJA["ajankohta"] = time.localtime()
    muokkaa_aika()
    main(leveys, korkeus)

if __name__ == "__main__":
    try:
        valikko()
    except KeyboardInterrupt:
        print("\nKiitos ja hei hei")
    