# Informacijski Sustavi - Projektni Zadatak

## Opis projekta i trenutne funkcionalnosti

Aplikacija ima 2 sučelja: kasa i menadžment. 

Tko se "ulogira" u kasu ima pristup svim artiklima na skladištu i može ih prodavati tako što odabere količine svih artikala
koje želi prodati i pritiskom na gumb za prodaju se generira račun i prodani artikli se miču sa skladišta.

Menadžersko sučelje ima mogućnost:
- dodavanja novih artikala u zalihe
- vršiti promjene nad postojećim artiklima (promjena imena, cijene, količine na skladištu, kategorije artikla)
- brisanje prisutnih artikala
- uvid u sve dosad izdane račune
- pristup statistikama dosadašnje prodaje (grafovi koji prate (1) ukupni promet po danu i (2) usporedbu broja prodanih artikala za taj dan)

## Trenutne upute za pokretanje (bez Dockera)

Unutar projektnog direktorija pokrenuti sljedeći skup komandi:

```
$ export FLASK_APP=server
$ export FLASK_ENV=development
$ flask run
```
