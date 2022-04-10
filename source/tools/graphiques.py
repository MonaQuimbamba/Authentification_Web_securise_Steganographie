import qrcode
import zbarlight
from PIL import Image
import subprocess
import steganographie as stegano

def faire_qr_code(info,taille_timestamp):
    """
       ....
    """
    data = info+" "+str(taille_timestamp)
    nom_fichier = "../resources/qrcode.png"
    qr = qrcode.make(data)
    qr.save(nom_fichier, scale=2)

def merge_qrcode_wit_img():
    """
    """
    cmd = subprocess.Popen("mogrify -resize 150x150 ../resources/qrcode.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -geometry +1450+1000 ../resources/qrcode.png ../resources/stegano_attestation.png ../resources/attestation.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def add_strings_to_img(texte_ligne):
    """
    """
    if not texte_ligne:
        texte_ligne='Attestation de réussite|délivrée à P-F.B'

    cmd = subprocess.Popen("curl -o ../resources/texte.png 'http://chart.apis.google.com/chart' --data-urlencode 'chst=d_text_outline' --data-urlencode 'chld=000000|56|h|FFFFFF|b|%s'"%texte_ligne, shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -gravity center ../resources/texte.png ../resources/fond_attestation.png ../resources/combinaison.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def get_qrcode_from_img():
    """
    """
    attestation = Image.open(fileName)
    qrImage = attestation.crop((1418,934,1418+210,934+210))
    qrImage.save("../resources/qrcoderecupere.png", "PNG")

def get_info_from_qrcode():
    """
    ....
    """
    image = Image.open("../resources/qrcode.png")
    data = zbarlight.scan_codes(['qrcode'], image)
    return data

def attestatio_graphique():
    """
    """
    signature_info="signed"
    nom_fichier_img="../resources/combinaison.png"
    file_timestamp="../freeTSA/file.tsr"
    bloc_info='Certificat délivré | à | Nom Prénom'
    add_strings_to_img(bloc_info)
    taille_timestamp = stegano.faire_stegano(nom_fichier_img,bloc_info,file_timestamp)
    faire_qr_code(signature_info,taille_timestamp)

    merge_qrcode_wit_img()

def verifier_stegano():
    nom_fichier = "../resources/attestation.png"
    taille_timestamp =str(get_info_from_qrcode()[0])
    taille_timestamp=int(taille_timestamp.split(" ")[1].replace("'",""))
    info_get_from_stegano= stegano.recuperer_info_stegano(taille_timestamp,nom_fichier)
    return info_get_from_stegano

def traiter_info_pour_verifier():
    """
    """
    info_to_verifie=verifier_stegano()
    print(info_to_verifie)

traiter_info_pour_verifier()
