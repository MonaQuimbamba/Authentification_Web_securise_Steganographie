import qrcode
import zbarlight
from PIL import Image
import subprocess
import steganographie as stegano
import os
import binascii

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
    tmp_var =get_info_from_qrcode()[0].decode().split(" ")
    taille_timestamp=int(tmp_var[1])
    info_get_from_stegano= stegano.recuperer_info_stegano(taille_timestamp,nom_fichier)
    return info_get_from_stegano

def traiter_info_pour_verifier():
    """
    """
    info_to_verifie=verifier_stegano()
    bloc_info =info_to_verifie[:64]
    tsq_contenu=info_to_verifie.split("**")[1]
    tsq_contenu=tsq_contenu[1:]
    tsq_contenu= binascii.a2b_base64(tsq_contenu)
    tsr_contenu =info_to_verifie.split("**")[0][65:]
    tsr_text=binascii.a2b_base64(tsr_contenu)
    faire_file("../tmp/file.tsr",tsr_text)
    faire_file("../tmp/file.tsq",tsq_contenu)
    verifier_timestamp()


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

def clean_cache():
    os.system(" rm -r ../tmp/*")


#traiter_info_pour_verifier()
#attestation_graphique("salut cava mon pote ")
