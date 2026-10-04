## Türkçe metin karşılaştırma: arama ve sıralama ##

## Arama: büyük/küçük harf ve Türkçe karakter farkı gözetilmez ("sahin" -> "Şahin")
_KATLAMA = str.maketrans("ÇĞIİÖŞÜÂÎÛçğıöşüâîû", "cgiiosuaiucgiosuaiu")

def katla(metin):
    return str(metin or "").translate(_KATLAMA).lower()

## Türk alfabesine göre sıralama anahtarı (Ç, Ğ, İ, Ö, Ş, Ü kendi yerlerinde; büyük/küçük harf farksız)
_ALFABE = "abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_SIRA = {h: i for i, h in enumerate(_ALFABE)}

def tr_sirala(metin):
    metin=str(metin or "").replace("I","ı").replace("İ","i").lower().translate(str.maketrans("âîû","aiu"))
    return [1000+_SIRA[h] if h in _SIRA else ord(h) for h in metin]
