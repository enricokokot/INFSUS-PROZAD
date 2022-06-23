# Informacijski Sustavi - Projektni Zadatak

## Opis projekta

Aplikacija ima 2 sučelja: kasa i menadžment.

Tko se "ulogira" u kasu ima pristup svim artiklima na skladištu i bazični uvid u najnovije izdane račune. 
Artikle može dodavati u košaricu i, ukoliko dođe do prodaje, oni se miču sa zaliha i 
u bazu se šalju podaci o obavljenoj kupnji i izdanom računu koji imitira stvari račun.

Menadžersko sučelje ima pristup svim CRUD operacijama nad artiklima u sljedećim oblicima: dodavanja novih artikala u zalihe, 
uvid u sve artikle, promjene pojedinosti postojećih artikala (promjena imena, cijene, količine na skladištu, kategorije artikla) i 
izbacivanje prisutnih artikala. Također, menadžment ima uvid u statistiku dosadašnje prodaje i može pregledati račune u izdanom formatu.

## Funckionalnosti
- CRUD
- prodaja na blagajni
- statistika u obliku grafova koji prate (1) ukupni promet po danu i (2) usporedbu broja prodanih artikala za taj dan
- simulacija stvarnog računa

## Upute za pokretanje

### Ukoliko sami želite kreirati sliku

Unutar projektnog direktorija kreirati sliku po uzoru na prisutni Dockerfile.

```
# docker build --tag [naziv_slike]:[verzija_slike] .
```

Ispisati sve prisutne slike i među njima pronaći id upravo kreirane.

```
# docker images
```

Pokrenuti Docker kontejner temeljen na izrađenoj slici.

```
# docker run -p 8080:8080 [id_slike]
```

U pregledniku posjetiti adresu localhost:8080.


### Ukoliko imate sliku preuzetu sa [link](https://drive.google.com/file/d/1moXfYTdMgYC71_9uui9u8aDAT6bvByT3/view?usp=sharing) (potreban UNIPU mail)

Učitajte sliku iz .tar datoteke

```
# docker load -i /put/do/datoteke/infsus-prozad.tar
```

Ispisati sve prisutne slike i među njima pronaći id upravo kreirane.

```
# docker images
```

Pokrenuti Docker kontejner temeljen na izrađenoj slici.

```
# docker run -p 8080:8080 [id_slike]
```

U pregledniku posjetiti adresu localhost:8080.
