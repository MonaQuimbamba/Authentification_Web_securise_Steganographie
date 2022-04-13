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
    data = str(info)+" "+str(taille_timestamp)
    nom_fichier = "../etc/tmp/qrcode.png"
    qr = qrcode.make(data)
    qr.save(nom_fichier, scale=2)

def merge_qrcode_wit_img():
    """
    """
    cmd = subprocess.Popen("mogrify -resize 150x150 ../etc/tmp/qrcode.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -geometry +1450+1000 ../etc/tmp/qrcode.png ../etc/tmp/stegano_attestation.png ../etc/tmp/attestation.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def add_strings_to_img(texte_ligne):
    """
    """
    if not texte_ligne:
        texte_ligne='Attestation de réussite|délivrée à P-F.B'

    cmd = subprocess.Popen("curl -o ../etc/tmp/texte.png 'http://chart.apis.google.com/chart' --data-urlencode 'chst=d_text_outline' --data-urlencode 'chld=000000|56|h|FFFFFF|b|%s'"%texte_ligne, shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    cmd = subprocess.Popen("composite -gravity center ../etc/tmp/texte.png ../resources/fond_attestation.png ../etc/tmp/combinaison.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

def get_qrcode_from_img(fileName):
    """
    """
    attestation = Image.open(fileName)
    qrImage = attestation.crop((1450,1000,1450+150,1000+150))
    qrImage.save("../etc/tmp/qrcode.png", "PNG")

def get_info_from_qrcode():
    """
    ....
    """
    image = Image.open("../etc/tmp/qrcode.png")
    data = zbarlight.scan_codes(['qrcode'], image)
    return data

def faire_attestation(bloc_info_from):
    """
    """
    signature_info=signer(bloc_info_from)
    nom_fichier_img="../etc/tmp/combinaison.png"
    file_timestamp="../etc/tmp/file.tsr"
    file_hash_time_stamp="../etc/tmp/file.tsq"
    bloc_info=bloc_info_from
    add_strings_to_img(bloc_info)
    demande_timestamp()
    taille_timestamp = stegano.faire_stegano(nom_fichier_img,bloc_info,file_timestamp,file_hash_time_stamp)
    faire_qr_code(signature_info,taille_timestamp)
    merge_qrcode_wit_img()

def verifier_stegano():
    nom_fichier = "../etc/tmp/attestation_hba_verifier.png"
    get_qrcode_from_img(nom_fichier)
    tmp_var =get_info_from_qrcode()[0].decode().split(" ")
    taille_timestamp=int(tmp_var[1])
    info_get_from_stegano= stegano.recuperer_info_stegano(taille_timestamp,nom_fichier)
    return info_get_from_stegano

def verifier_attestation():
    """
    """
    info_to_verifie=verifier_stegano()
    bloc_info =info_to_verifie[:64]
    tsq_contenu=info_to_verifie.split("**")[1]
    print(tsq_contenu)
    tsq_contenu=tsq_contenu[1:]
    tsq_contenu=tsq_contenu.replace("'","")
    tsq_contenu=tsq_contenu[:-2]
    os.system("echo -n %s > ../etc/tmp/file.tsq"%tsq_contenu)
    #faire_file("../etc/tmp/file.tsq",tsq_contenu)
    # openssl base64 -a -d -in bloc.sign -out bloc.bit
    # openssl base64  -in %s -out ../etc/tmp/timestamp
    os.system("sudo openssl base64 -a -d -in  ../etc/tmp/file.tsq -out  ../etc/tmp/file_f.tsq")
    #cmd = subprocess.Popen("openssl base64 -a -d -in  ../etc/tmp/file.tsq -out  ../etc/tmp/file_f.tsq", shell=True,stdout=subprocess.PIPE)
    #(hashtimestamp, ignorer) = cmd.communicate()
    #print(tsq_contenu)
    #tsq_contenu= binascii.a2b_base64(tsq_contenu)
    #print(tsq_contenu)
    #tsr_contenu =info_to_verifie.split("**")[0][65:]
    #faire_file("../etc/tmp/file.tsr",tsr_contenu)
    #os.system("openssl base64 -a -d -in ../etc/tmp/file.tsr -out ../etc/tmp/file.tsr")
    #openssl base64 -a -d -in bloc.sign -out bloc.bit
    #tsr_text=binascii.a2b_base64(tsr_contenu)
    #faire_file("../etc/tmp/file.tsr",tsr_text)
    #faire_file("../etc/tmp/file.tsq",tsq_contenu)
    #print(verifier_timestamp())
    #return verifier_timestamp()==True and verify_signature()==True

def verifier_timestamp():
    cmd = subprocess.Popen("openssl ts -verify -in ../etc/tmp/file.tsr -queryfile ../etc/tmp/file_f.tsq -CAfile ../freeTSA/cacert.pem -untrusted ../freeTSA/tsa.crt ", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()
    if len(resultat.decode().split(" "))==2:
        if resultat.decode().split(" ")[1].rstrip()=="OK":
            return True
    else:
        return False


def demande_timestamp():
    os.system("openssl ts -query -data ../etc/tmp/combinaison.png -no_nonce -sha512 -cert -out ../etc/tmp/file.tsq")
    os.system('curl -H "Content-Type: application/timestamp-query" --data-binary "@../etc/tmp/file.tsq" https://freetsa.org/tsr > ../etc/tmp/file.tsr')

def faire_file(fileName,contenu):
    f = open(fileName, "w")
    f.write(contenu)
    f.close()

def clean_cache():
    os.system(" rm -r ../etc/tmp/*")

def signer(bloc_info_from):
    date_actuelle=time.localtime()
    current_time = time.strftime("%H:%M:%S:%d:%m:%y",date_actuelle)
    bloc_info=bloc_info_from+current_time
    filename="../etc/signature/"+current_time
    faire_file(filename,bloc_info.encode())
    os.system('openssl dgst -sign ../AC/private_key.pem -keyform PEM -sha256 -out ../etc/tmp/signature.sign -binary %s'%filename)
    cmd = subprocess.Popen("cat ../etc/tmp/signature.sign", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()
    return binascii.b2a_base64(resultat)

def verify_signature():
    signature = get_info_from_qrcode()
    # openssl base64 -a -d -in bloc.sign -out bloc.bit
    # openssl base64  -in bloc_Info_sign.sig -out bloc_Info_sign_ascii.sig
    signature=str(signature[0]).split(" ")[0]
    #signature=signature.replace("\\n","")
    print(signature)
    #signature=binascii.a2b_base64(signature.encode())

    """f_name="../etc/tmp/sig.signature"
    faire_file(f_name,signature)
    for f in os.listdir("../etc/signature"):
        f="../etc/signature/"+f
        cmd = subprocess.Popen("openssl dgst -verify ../AC/public_key.pem -keyform PEM -sha256 -signature %s -binary %s"%(f_name,f), shell=True,stdout=subprocess.PIPE)
        (resultat, ignorer) = cmd.communicate()
        if resultat.decode().split(" ")[0]=="Verified" and resultat.decode().split(" ")[1].rstrip()=="OK":
            #print(resultat.decode().split(" ")[1].rstrip())
            return True
    return False"""

#verify_signature()

verifier_attestation()
#faire_attestation("salut")
