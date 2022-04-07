import subprocess

def process():
    nom = input("Nom : ")
    prenom = input("Prenom : ")
    inti_certi =  input("Intitulé du certificat : ")
    n_p = nom + " " +prenom
    commande = subprocess.Popen(f"curl -X POST -d 'identite={n_p}' -d 'intitule_certif={inti_certi}'  http://localhost:8080/creation" , shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = commande.communicate()
    resul= resultat.decode("utf-8")
    print("Verdicte:", resul)
    
    commande_bloc = subprocess.Popen(f"touch " , shell=True,stdout=subprocess.PIPE)
    (resultat, ignorer) = commande.communicate()

    bloc_Info = "bloc_Info.txt"
    f = open(bloc_Info, "w")
    f.write("Nom :")
    f.write(nom + "\n")
    f.write("Prenom :")
    f.write(prenom + "\n")
    f.write("Intitulé du certificat :")
    f.write(inti_certi)

    commande1 = subprocess.Popen(f"openssl dgst -sha256 -sign  ac_private_key.pem  {bloc_Info} > bloc_Info_sign.sig " , shell=True,stdout=subprocess.PIPE)
    (resultat1, ignorer1) = commande1.communicate() 


def main():
    process()

if __name__== "__main__" :
    main()
