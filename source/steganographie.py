#!/usr/bin/python3
from PIL import Image
import subprocess

def vers_8bit(c):
    """Documentation for a function.
    More details.
    """
    chaine_binaire = bin(ord(c))[2:]
    return "0"*(8-len(chaine_binaire))+chaine_binaire

def modifier_pixel(pixel, bit):
    # on modifie que la composante rouge
    r_val = pixel[0]
    rep_binaire = bin(r_val)[2:]
    rep_bin_mod = rep_binaire[:-1] + bit
    r_val = int(rep_bin_mod, 2)
    return tuple([r_val] + list(pixel[1:]))

def recuperer_bit_pfaible(pixel):
    r_val = pixel[0]
    return bin(r_val)[-1]

def cacher(image,message):
    dimX,dimY = image.size
    im = image.load()
    message_binaire = ''.join([vers_8bit(c) for c in message])
    posx_pixel = 0
    posy_pixel = 0
    for bit in message_binaire:
        im[posx_pixel,posy_pixel] = modifier_pixel(im[posx_pixel,posy_pixel],bit)
        posx_pixel += 1
        if (posx_pixel == dimX):
            posx_pixel = 0
            posy_pixel += 1
        assert(posy_pixel < dimY)

def recuperer(image,taille):
    message = ""
    dimX,dimY = image.size
    im = image.load()
    posx_pixel = 0
    posy_pixel = 0
    for rang_car in range(0,taille):
        rep_binaire = ""
        for rang_bit in range(0,8):
            rep_binaire += recuperer_bit_pfaible(im[posx_pixel,posy_pixel])
            posx_pixel +=1
            if (posx_pixel == dimX):
                posx_pixel = 0
                posy_pixel += 1
        message += chr(int(rep_binaire, 2))
    return message



def faire_stegano(nom_fichier,bloc_info,file_timestamp):
    cmd = subprocess.Popen("cat %s"%file_timestamp, shell=True,stdout=subprocess.PIPE)
    (timestamp, ignorer) = cmd.communicate()
    nom_fichier = nom_fichier
    ## completer le bloc d'info pour arriver à 64 octs
    if len(bloc_info) < 64:
        octets_to_add=64 - len(bloc_info)
        for i in range(octets_to_add):
            bloc_info+=str(i)

    bloc_info=bloc_info[:64]
    # add octet on bloc_info
    saisie = bloc_info+str(timestamp)#input("Entrez le message [%s]"%message_defaut)
    message_a_traiter = saisie or message_defaut
    print ("Longueur message : ",len(message_a_traiter))
    mon_image = Image.open(nom_fichier)
    cacher(mon_image, message_a_traiter)
    mon_image.save("stegano_"+nom_fichier)

def recuperer_info_stegano():
    # Valeurs par defaut
    nom_defaut = "image_test.png"
    message_defaut = "Hello world"
    choix_defaut = 1
    # programme de demonstration
    #saisie = input("Entrez l'operation 1) cacher 2) retrouver [%d]"%choix_defaut)
    #choix = saisie or choix_defaut

    #if choix == 1:
    saisie = "stegano_attestation.png"
    nom_fichier = saisie or nom_defaut
    saisie = 64#input("Entrez la taille du message ") 13986
    message_a_traiter = int(saisie)
    mon_image = Image.open(nom_fichier)
    message_retrouve = recuperer(mon_image, message_a_traiter)
    print (message_retrouve)


p1="attestation.png"
p2="Claudio Antonio Certificat delivré par"
p3="file.tsr"
faire_stegano(p1,p2,p3)
