#!/usr/bin/python3
import utilitaire as tools
from bottle import route, run, template, request, response



@route('/creation', method='POST')
def création_attestation():
    contenu_identité = request.forms.get('identite')
    contenu_intitulé_certification = request.forms.get('intitule_certif')
    #print('nom prénom :', contenu_identité, ' intitulé de la certification :',contenu_intitulé_certification)
    tools.faire_attestation(contenu_identité+"|"+contenu_intitulé_certification)
    #print(" Votre attestation est prête vous pouvez la récupérer ")
    response.set_header('Content-type', 'text/plain')
    return "Votre attestation est prête vous pouvez la récupérer!!!!"


@route('/verification', method='POST')
def vérification_attestation():
    contenu_image = request.files.get('image')
    contenu_image.save('../Dossier/tmp/attestation_hba_verifier.png',overwrite=True)
    if tools.verifier_attestation():
        response.set_header('Content-type', 'text/plain')
        return "Attestation certifiée!"
    else:
        response.set_header('Content-type', 'text/plain')
        return "Attestation erronée!"



@route('/fond')
def récupérer_fond():
    response.set_header('Content-type', 'image/png')
    descripteur_fichier = open('../Dossier/tmp/attestation.png','rb')
    contenu_fichier = descripteur_fichier.read()
    descripteur_fichier.close()
    return contenu_fichier 

run(host='0.0.0.0',port=8080,debug=True)
