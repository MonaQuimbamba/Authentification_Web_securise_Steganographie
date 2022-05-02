import qrcode
import zbarlight
from PIL import Image
import subprocess
import steganographie as stegano
import os
import binascii
import time

def faire_qr_code(info,taille_timestamp):
    """
       Focntion qui permet de faire le QRcode
       return void
    """
    data = str(info)+"**"+str(taille_timestamp)
    nom_fichier = "../Dossier/tmp/qrcode.png"
    qr = qrcode.make(data)
    qr.save(nom_fichier, scale=2)

def merge_qrcode_wit_img():
    """
        Fonction qui permet de fusionner le QRcode avec une image
        return void
    """
    cmd = subprocess.Popen("mogrify -resize 150x150 ../Dossier/tmp/qrcode.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -geometry +1450+1000 ../Dossier/tmp/qrcode.png ../Dossier/tmp/stegano_attestation.png ../Dossier/tmp/attestation.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def add_strings_to_img(texte_ligne):
    """
        Fonction qui permet d'ajouter du texte dans une image
        return void
    """
    if not texte_ligne:
        texte_ligne='Attestation de réussite|délivrée à P-F.B'

    cmd = subprocess.Popen("curl -o ../Dossier/tmp/texte.png 'http://chart.apis.google.com/chart' --data-urlencode 'chst=d_text_outline' --data-urlencode 'chld=000000|56|h|FFFFFF|b|%s'"%texte_ligne, shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -gravity center ../Dossier/tmp/texte.png ../resources/fond_attestation.png ../Dossier/tmp/combinaison.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def get_qrcode_from_img(fileName):
    """
        Fonction qui permet de récupérer le QRcode d'une image
        return void
    """
    attestation = Image.open(fileName)
    qrImage = attestation.crop((1450,1000,1450+150,1000+150))
    qrImage.save("../Dossier/tmp/qrcode.png", "PNG")

def get_info_from_qrcode():
    """
            Fonction qui permet de récupérer les infos du QRcode
            return info du Qrcode
    """
    image = Image.open("../Dossier/tmp/qrcode.png")
    data = zbarlight.scan_codes(['qrcode'], image)
    return data

def faire_attestation(bloc_info_from):
    """
        Fonction qui permet de faire l'attestation
        return void
    """
    faire_file("../Dossier/tmp/bloc_info.txt",bloc_info_from)
    signature_info= signer(bloc_info_from)
    nom_fichier_img="../Dossier/tmp/combinaison.png"
    file_timestamp="../Dossier/tmp/file.tsr"
    bloc_info=bloc_info_from
    add_strings_to_img(bloc_info)
    demande_timestamp()
    taille_stegano = stegano.faire_stegano(nom_fichier_img,bloc_info,file_timestamp) #,file_hash_time_stamp)
    faire_qr_code(signature_info,taille_stegano)
    merge_qrcode_wit_img()

def get_info_stegano():
    """
       Fonction qui permet de récupérer les infos de la stegano
       return info de la stegano
    """
    nom_fichier = "../Dossier/tmp/attestation_hba_verifier.png"
    get_qrcode_from_img(nom_fichier)
    tmp_var =get_info_from_qrcode()[0].decode().split("**")
    taille_timestamp=int(tmp_var[1])
    info_get_from_stegano= stegano.recuperer_info_stegano(taille_timestamp,nom_fichier)
    return info_get_from_stegano

def verifier_attestation():
    """
         Fonction qui permet de verifier l'attestation
         return True si la vérification est bonne sinon False
    """
    info_to_verifie=get_info_stegano()
    bloc_info =info_to_verifie[:64]
    tsr_contenu =info_to_verifie[65:]
    tsr_text=binascii.a2b_base64(tsr_contenu)

    f_name="../Dossier/tmp/file_v.tsr"
    f = open(f_name, "wb")
    f.write(tsr_text)
    f.close()
    bloc_info=bloc_info.split("**")[0]
    faire_file("../Dossier/tmp/bloc_info.txt",bloc_info)
    os.system("openssl ts -query -data ../Dossier/tmp/bloc_info.txt -no_nonce -sha512 -cert -out ../Dossier/tmp/file_v.tsq")
    return verifier_timestamp()==True and verify_signature()==True

def verifier_timestamp():
    """
        Focntion qui permet  verifier le timestamp
        return True si la vérification est bonne sinon False
    """
    cmd = subprocess.Popen("openssl ts -verify -in ../Dossier/tmp/file_v.tsr -queryfile ../Dossier/tmp/file_v.tsq -CAfile ../freeTSA/cacert.pem -untrusted ../freeTSA/tsa.crt ", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()
    if len(resultat.decode().split(" "))==2:
        if resultat.decode().split(" ")[1].rstrip()=="OK":
            print("Vérification du timestamp", resultat.decode().split(" "))
            return True
    else:
        return False

def demande_timestamp():
    """
      Fonction qui permet de faire la demande de timestamp
      return void
    """
    os.system("openssl ts -query -data ../Dossier/tmp/bloc_info.txt -no_nonce -sha512 -cert -out ../Dossier/tmp/file.tsq")
    os.system('curl -H "Content-Type: application/timestamp-query" --data-binary "@../Dossier/tmp/file.tsq" https://freetsa.org/tsr > ../Dossier/tmp/file.tsr')

def faire_file(fileName,contenu):
    """
        Fonction qui permet faire un fichier
        return void
    """
    f = open(fileName, "w")
    f.write(contenu)
    f.close()


def signer(bloc_info):
    """
        Fonction qui permet de signer le contenu du QRcode
        return la siganture au format ASCII
    """
    bloc_info=bloc_info.replace(" ", "")

    date_actuelle=time.localtime()
    current_time = time.strftime("%H:%M:%S:%d:%m:%y",date_actuelle)
    bloc_info=bloc_info+current_time
    # completer le bloc
    if len(bloc_info) < 64:
        octets_to_add=64 - len(bloc_info)
        for i in range(octets_to_add):
            bloc_info+=str(i)

    bloc_info=bloc_info[:64]
    filename="../Dossier/signature/"+current_time
    faire_file(filename,bloc_info)
    os.system('openssl dgst -sign ../les_cles/cle_privee_certifplus_signature.pem -keyform PEM -sha256 -out ../Dossier/tmp/bloc_signed.sign -binary %s'%filename)
    cmd = subprocess.Popen("cat ../Dossier/tmp/bloc_signed.sign", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()
    resultat = binascii.b2a_base64(resultat)
    return str(resultat)

def verify_signature():
    """
         cette fonction permet de verifier la signature du contenu du QRcode
         return True si la vérification est bonne sinon False
    """
    signature = get_info_from_qrcode()
    signature=str(signature[0]).split("**")[0]

    signature=signature[4:]
    signature=signature[:-4]
    f_name="../Dossier/tmp/bloc_signed_ascii_to_v.sign"
    signature = binascii.a2b_base64(signature)
    f = open(f_name, "wb")
    f.write(signature)
    f.close()

    for f in os.listdir("../Dossier/signature"):
        f="../Dossier/signature/"+f
        cmd = subprocess.Popen("openssl dgst -verify ../les_cles/cle_pub_certifplus_signature.pem -keyform PEM -sha256 -signature %s -binary %s"%(f_name,f), shell=True,stdout=subprocess.PIPE)
        (resultat, ignorer) = cmd.communicate()
        if resultat.decode().split(" ")[0]=="Verified" and resultat.decode().split(" ")[1].rstrip()=="OK":
            print("Véification de la signature",resultat.decode().split(" ")[1].rstrip())
            return True
    return False
