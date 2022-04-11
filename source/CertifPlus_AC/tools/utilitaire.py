import qrcode
import zbarlight
from PIL import Image
import subprocess
import steganographie as stegano
import os

def faire_qr_code(info,taille_timestamp):
    """
       ....
    """
    data = info+" "+str(taille_timestamp)
    nom_fichier = "../tmp/qrcode.png"
    qr = qrcode.make(data)
    qr.save(nom_fichier, scale=2)

def merge_qrcode_wit_img():
    """
    """
    cmd = subprocess.Popen("mogrify -resize 150x150 ../tmp/qrcode.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -geometry +1450+1000 ../tmp/qrcode.png ../tmp/stegano_attestation.png ../tmp/attestation.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def add_strings_to_img(texte_ligne):
    """
    """
    if not texte_ligne:
        texte_ligne='Attestation de réussite|délivrée à P-F.B'

    cmd = subprocess.Popen("curl -o ../tmp/texte.png 'http://chart.apis.google.com/chart' --data-urlencode 'chst=d_text_outline' --data-urlencode 'chld=000000|56|h|FFFFFF|b|%s'"%texte_ligne, shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -gravity center ../tmp/texte.png ../resources/fond_attestation.png ../tmp/combinaison.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def get_qrcode_from_img(fileName):
    """
    """
    attestation = Image.open(fileName)
    qrImage = attestation.crop((1450,1000,1450+150,1000+150))
    qrImage.save("../tmp/qrcode.png", "PNG")

def get_info_from_qrcode():
    """
    ....
    """
    image = Image.open("../tmp/qrcode.png")
    data = zbarlight.scan_codes(['qrcode'], image)
    return data

def attestation_graphique(bloc_info_from):
    """
    """
    signature_info="signed"
    nom_fichier_img="../tmp/combinaison.png"
    file_timestamp="../tmp/file.tsr"
    file_hash_time_stamp="../tmp/file.tsq"
    bloc_info=bloc_info_from
    add_strings_to_img(bloc_info)
    demande_timestamp()
    taille_timestamp = stegano.faire_stegano(nom_fichier_img,bloc_info,file_timestamp,file_hash_time_stamp)
    faire_qr_code(signature_info,taille_timestamp)
    merge_qrcode_wit_img()

def verifier_stegano():
    nom_fichier = "../tmp/attestation_hba_verifier.png"
    get_qrcode_from_img(nom_fichier)
    taille_timestamp =str(get_info_from_qrcode()[0])
    taille_timestamp=int(taille_timestamp.split(" ")[1].replace("'",""))
    info_get_from_stegano= stegano.recuperer_info_stegano(taille_timestamp,nom_fichier)
    return info_get_from_stegano

def traiter_info_pour_verifier():
    """
    """
    info_to_verifie=verifier_stegano()
    bloc_info =info_to_verifie[:64]
    #print(bloc_info)
    faire_file("../tmp/file.tsr",info_to_verifie[64:].split("**")[0].encode())
    faire_file("../tmp/file.tsq",info_to_verifie[64:].split("**")[1].encode())
    verifier_timestamp()
    #print(info_to_verifie[64:].split("**")[1])

def demande_timestamp():
    os.system("openssl ts -query -data ../tmp/combinaison.png -no_nonce -sha512 -cert -out ../tmp/file.tsq")
    os.system('curl -H "Content-Type: application/timestamp-query" --data-binary "@../tmp/file.tsq" https://freetsa.org/tsr > ../tmp/file.tsr')


def verifier_timestamp():
    cmd = subprocess.Popen("openssl ts -verify -in ../tmp/file.tsr -queryfile ../tmp/file.tsq -CAfile ../freeTSA/cacert.pem -untrusted ../freeTSA/tsa.crt ", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()
    print(resultat.decode())

def faire_file(fileName,contenu):
    f = open(fileName, "wb")
    f.write(contenu)
    f.close()

def test():
    f = open("../../file.tsq", "rb")
    contenu =f.read()
    f = open("../../t.tsq", "wb")
    f.write(contenu)
    f.close()
def clean_cache():
    os.system(" rm -r ../tmp/*")

traiter_info_pour_verifier()
