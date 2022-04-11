#!/usr/bin/python3
import utilitaire as tools
from bottle import route, run, template, request, response



@route('/creation', method='POST')
def création_attestation():
    contenu_identité = request.forms.get('identite')
    contenu_intitulé_certification = request.forms.get('intitule_certif')
    #print('nom prénom :', contenu_identité, ' intitulé de la certification :',contenu_intitulé_certification)
    tools.attestation_graphique(contenu_identité+"|"+contenu_intitulé_certification)
    print(" Votre attestation est prête vous pouves la récuperer ")
    response.set_header('Content-type', 'text/plain')
    return "ok!"


@route('/verification', method='POST')
def vérification_attestation():
    contenu_image = request.files.get('image')
    contenu_image.save('../tmp/attestation_hba_verifier.png',overwrite=True)
    tools.traiter_info_pour_verifier()
    tools.clean_cache()
    response.set_header('Content-type', 'text/plain')
    return "ok!"



@route('/fond')
def récupérer_fond():
    response.set_header('Content-type', 'image/png')
    descripteur_fichier = open('../tmp/attestation.png','rb')
    contenu_fichier = descripteur_fichier.read()
    descripteur_fichier.close()
    tools.clean_cache()
    return contenu_fichier

run(host='0.0.0.0',port=8080,debug=True)
