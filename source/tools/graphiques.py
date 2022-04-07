import qrcode
import zbarlight
from PIL import Image
import subprocess

def faire_qr_code(info):
    """
       ....
    """
    data = info
    nom_fichier = "../resources/qrcode.png"
    qr = qrcode.make(data)
    qr.save(nom_fichier, scale=2)

def merge_qrcode_wit_img():
    """
    """
    cmd = subprocess.Popen("mogrify -resize 150x150 ../resources/qrcode.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -geometry +1450+1000 ../resources/qrcode.png ../resources/combinaison.png ../resources/attestation.png", shell=True,stdout=subprocess.PIPE)
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
    image = Image.open("../qrcode.png")
    data = zbarlight.scan_codes(['qrcode'], image)
    print(data)

def attestatio_graphique():
    """
    """
    signature_info="signed"
    faire_qr_code(signature_info)
    texte_ligne='Certificat délivré | à | Nom Prénom'
    add_strings_to_img(texte_ligne)
    merge_qrcode_wit_img()

#attestatio_graphique()
