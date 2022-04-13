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
       ....
    """
    data = str(info)+"**"+str(taille_timestamp)
    #print(data)
    nom_fichier = "../Dossier/tmp/qrcode.png"
    qr = qrcode.make(data)
    qr.save(nom_fichier, scale=2)

def merge_qrcode_wit_img():
    """
    """
    cmd = subprocess.Popen("mogrify -resize 150x150 ../Dossier/tmp/qrcode.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -geometry +1450+1000 ../Dossier/tmp/qrcode.png ../Dossier/tmp/stegano_attestation.png ../Dossier/tmp/attestation.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def add_strings_to_img(texte_ligne):
    """
    """
    if not texte_ligne:
        texte_ligne='Attestation de réussite|délivrée à P-F.B'

    cmd = subprocess.Popen("curl -o ../Dossier/tmp/texte.png 'http://chart.apis.google.com/chart' --data-urlencode 'chst=d_text_outline' --data-urlencode 'chld=000000|56|h|FFFFFF|b|%s'"%texte_ligne, shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -gravity center ../Dossier/tmp/texte.png ../resources/fond_attestation.png ../Dossier/tmp/combinaison.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def get_qrcode_from_img(fileName):
    """
    """
    attestation = Image.open(fileName)
    qrImage = attestation.crop((1450,1000,1450+150,1000+150))
    qrImage.save("../Dossier/tmp/qrcode.png", "PNG")

def get_info_from_qrcode():
    """
    ....
    """
    image = Image.open("../Dossier/tmp/qrcode.png")
    data = zbarlight.scan_codes(['qrcode'], image)
    return data

def faire_attestation(bloc_info_from):
    """
    """
    signature_info= signer(bloc_info_from)
    nom_fichier_img="../Dossier/tmp/combinaison.png"
    file_timestamp="../Dossier/tmp/file.tsr"
    file_hash_time_stamp="../Dossier/tmp/file.tsq"
    bloc_info=bloc_info_from
    add_strings_to_img(bloc_info)
    demande_timestamp()
    taille_timestamp = stegano.faire_stegano(nom_fichier_img,bloc_info,file_timestamp,file_hash_time_stamp)
    faire_qr_code(signature_info,taille_timestamp)
    merge_qrcode_wit_img()

def verifier_stegano():
    nom_fichier = "../Dossier/tmp/attestation_hba_verifier.png"
    get_qrcode_from_img(nom_fichier)
    tmp_var =get_info_from_qrcode()[0].decode().split("**")
    #print(tmp_var," <===")
    taille_timestamp=int(tmp_var[1])
    info_get_from_stegano= stegano.recuperer_info_stegano(taille_timestamp,nom_fichier)
    #print(info_get_from_stegano," voir ",taille_timestamp)
    return info_get_from_stegano

def verifier_attestation():
    """
    """
    info_to_verifie=verifier_stegano()

    #print(info_to_verifie)
    bloc_info =info_to_verifie[:64]
    tsq_contenu=info_to_verifie.split("**")[1]
    tsq_contenu=tsq_contenu[2:]
    tsq_contenu=tsq_contenu[:-3]
    #print(tsq_contenu)
    """faire_file("../Dossier/tmp/file.tsq",tsq_contenu)
    os.system("openssl base64 -a -d -in ../Dossier/tmp/file.tsq -out ../Dossier/tmp/file_v.tsq")
    tsr_contenu =info_to_verifie.split("**")[0][64:]
    faire_file("../Dossier/tmp/file.tsr",tsr_contenu)
    os.system("openssl base64 -a -d -in ../Dossier/tmp/file.tsr -out ../Dossier/tmp/file_v.tsr")
    print(verifier_timestamp()," et ", verify_signature())
    """
    tsq_contenu= binascii.a2b_base64(tsq_contenu)
    tsr_contenu =info_to_verifie.split("**")[0][65:]
    tsr_text=binascii.a2b_base64(tsr_contenu)

    f_name="../Dossier/tmp/file_v.tsr"
    f = open(f_name, "wb")
    f.write(tsr_text)
    f.close()
    f_name="../Dossier/tmp/file_v.tsq"
    f = open(f_name, "wb")
    f.write(tsq_contenu)
    f.close()
    return verifier_timestamp()==True and verify_signature()==True

def verifier_timestamp():
    cmd = subprocess.Popen("openssl ts -verify -in ../Dossier/tmp/file_v.tsr -queryfile ../Dossier/tmp/file_v.tsq -CAfile ../freeTSA/cacert.pem -untrusted ../freeTSA/tsa.crt ", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()
    #print(resultat.decode().split(" "))
    if len(resultat.decode().split(" "))==2:
        if resultat.decode().split(" ")[1].rstrip()=="OK":
            return True
    else:
        return False

def demande_timestamp():
    os.system("openssl ts -query -data ../Dossier/tmp/combinaison.png -no_nonce -sha512 -cert -out ../Dossier/tmp/file.tsq")
    os.system('curl -H "Content-Type: application/timestamp-query" --data-binary "@../Dossier/tmp/file.tsq" https://freetsa.org/tsr > ../Dossier/tmp/file.tsr')

def faire_file(fileName,contenu):
    f = open(fileName, "w")
    f.write(contenu)
    f.close()

def clean_cache():
    os.system(" rm -r ../Dossier/tmp/*")

def signer(bloc_info):
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
    #cmd = subprocess.Popen("openssl base64  -in ../Dossier/tmp/bloc_signed.sign -out ../Dossier/tmp/bloc_signed_ascii.sign | cat ../Dossier/tmp/bloc_signed_ascii.sign", shell=True,stdout=subprocess.PIPE)
    #(resultat, ignorer) = cmd.communicate()
    cmd = subprocess.Popen("cat ../Dossier/tmp/bloc_signed.sign", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()
    resultat = binascii.b2a_base64(resultat)
    #print(len(resultat),resultat)
    return str(resultat)

def verify_signature():
    signature = get_info_from_qrcode()
    signature=str(signature[0]).split("**")[0]
    signature=signature[4:]
    signature=signature[:-4]

    f_name="../Dossier/tmp/bloc_signed_ascii_to_v.sign"
    signature = binascii.a2b_base64(signature)
    f = open(f_name, "wb")
    f.write(signature)
    f.close()

    #os.system("openssl base64 -a -d -in %s -out ../Dossier/tmp/bloc_signed_bin"%f_name)
    #cmd = subprocess.Popen("openssl base64 -a -d -in %s -out ../Dossier/tmp/bloc_signed_bin"%f_name, shell=True,stdout=subprocess.PIPE)
    #(resultat, ignorer) = cmd.communicate()


    for f in os.listdir("../Dossier/signature"):
        f="../Dossier/signature/"+f
        cmd = subprocess.Popen("openssl dgst -verify ../les_cles/cle_pub_certifplus_signature.pem -keyform PEM -sha256 -signature %s -binary %s"%(f_name,f), shell=True,stdout=subprocess.PIPE)
        (resultat, ignorer) = cmd.communicate()
        if resultat.decode().split(" ")[0]=="Verified" and resultat.decode().split(" ")[1].rstrip()=="OK":
            #print(resultat.decode().split(" ")[1].rstrip())
            return True
    return False



#verifier_attestation()
#faire_attestation("Claudio Antonio")
