#!/usr/bin/python3
from PIL import Image
import subprocess
import sys,os
import binascii

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

def faire_stegano(nom_fichier,bloc_info,file_timestamp,hash_timestamp):
    with open(file_timestamp, "rb") as f:
        timestamp =binascii.b2a_base64(f.read())
    f.close()
    with open(hash_timestamp, "rb") as f:
        hashtimestamp =binascii.b2a_base64(f.read())
    f.close()
    nom_fichier = nom_fichier
    ## completer le bloc d'info pour arriver à 64 octs
    if len(bloc_info) < 64:
        octets_to_add=64 - len(bloc_info)
        for i in range(octets_to_add):
            bloc_info+=str(i)

    bloc_info=bloc_info[:64]
    # add octet on bloc_info
    message_a_traiter = bloc_info+str(timestamp)+"**"+str(hashtimestamp)
    mon_image = Image.open(nom_fichier)
    cacher(mon_image, message_a_traiter)
    mon_image.save("../etc/tmp/stegano_attestation.png")

    return len(message_a_traiter)

def recuperer_info_stegano(taille_timestamp,nom_fichier):
    saisie = taille_timestamp
    message_a_traiter = int(saisie)
    mon_image = Image.open(nom_fichier)
    message_retrouve = recuperer(mon_image, message_a_traiter)
    return message_retrouve
