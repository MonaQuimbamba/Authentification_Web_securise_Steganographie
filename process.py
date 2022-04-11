import subprocess
import qrcode

def creation_attestation():
    nom = input("Nom : ")
    prenom = input("Prenom : ")
    inti_certi =  input("Intitulé du certificat : ")
    n_p = nom + " " +prenom
    commande = subprocess.Popen(f"curl -X POST -d 'identite={n_p}' -d 'intitule_certif={inti_certi}'  http://localhost:8080/creation" , shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = commande.communicate()
    resul= resultat.decode("utf-8")
    print("Verdicte:", resul)
    
    commande_bloc = subprocess.Popen("touch bloc_Info.txt" , shell=True,stdout=subprocess.PIPE)
    (resultat_bloc, ignorer_bloc) = commande_bloc.communicate()

    bloc_Info = "bloc_Info.txt"
    f = open(bloc_Info, "w")
    f.write("Nom :")
    f.write(nom + "\n")
    f.write("Prenom :")
    f.write(prenom + "\n")
    f.write("Intitulé du certificat :")
    f.write(inti_certi)
    #Signature
    commande1 = subprocess.Popen(f"openssl dgst -sha256 -sign  certifPlus_priv.key.pem   {bloc_Info} > bloc_Info_sign.sig " , shell=True,stdout=subprocess.PIPE)
    (resultat1, ignorer1) = commande1.communicate()
    #conversion ascii
    commande2 = subprocess.Popen(f" openssl base64  -in bloc_Info_sign.sig -out bloc_Info_sign_ascii.sig" , shell=True,stdout=subprocess.PIPE)
    (resultat2, ignorer2) = commande2.communicate()
    #obtention du fichier tsq (TimeStampRequest)
    commande3 = subprocess.Popen(f" openssl ts -query -data {bloc_Info} -no_nonce -sha512 -cert -out bloc_Info.tsq" , shell=True,stdout=subprocess.PIPE)
    (resultat3, ignorer3) = commande3.communicate()
    #demande de signature du timestamp par l'horodateur www.freetsa.org
    commande4 = subprocess.Popen(f" curl -H \"Content-Type: application/timestamp-query\" --data-binary '@bloc_Info.tsq' https://freetsa.org/tsr > bloc_Info.tsr" , shell=True,stdout=subprocess.PIPE)
    (resultat4, ignorer4) = commande4.communicate()

    texte_ligne=f"Attestation de réussite|délivrée à {n_p}"
    print("text", texte_ligne)

    commande5 = subprocess.Popen("curl -o texte.png 'http://chart.apis.google.com/chart' --data-urlencode 'chst=d_text_outline' --data-urlencode 'chld=000000|56|h|FFFFFF|b|%s'"%texte_ligne, shell=True,stdout=subprocess.PIPE)
    (resultat5, ignorer5) = commande5.communicate()

    cmd = subprocess.Popen("composite -gravity center texte.png fond_attestation.png combinaison.png", shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = cmd.communicate()

    fichier = "bloc_Info_sign_ascii.sig"
    f = open(fichier, "r")
    donne = f.readlines()
    print("donne", donne)
    
    
    nom_fichier = "qrcode.png"
    qr = qrcode.make(donne)
    qr.save(nom_fichier, scale=2)

    commande6 = subprocess.Popen("mogrify -resize 150x150 qrcode.png", shell=True,stdout=subprocess.PIPE)
    (resultat6, ignorer6) = commande6.communicate()

    commande7 = subprocess.Popen("composite -geometry +1450+1000 qrcode.png combinaison.png attestation.png", shell=True,stdout=subprocess.PIPE)
    (resultat7, ignorer7) = commande7.communicate()




def main():
    creation_attestation()

if __name__== "__main__" :
    main()
