# Authentification_Web_securise_Steganographie

## The Idea 

There is a company ***CertifPlus certification*** that needs to implement their distribution process
secure electronic certificate of success in the certifications it has issued

* The authenticity of the certificate issued electronically in the form of an image must be guaranteed:
    
    * the image contains visible information:
        
        => The name of the person receiving the certificate of achievement
        
        => The name of successful certification
        
        => A QRcode containing the signature of this information
        
    * The image also  contains hidden information
        
        => unfalsifiable information is concealed by steganography in the image. This information
tion includes the visible information of the certificate as well as the guaranteed date of issue
by a “timestamp” signed by a timestamping authority “www.freetsa.org”.






The company designs this process in the form of a WebService or Web Application, i.e. a server
TCP using the HTTP protocol, supporting different requests:



![image](https://user-images.githubusercontent.com/75567246/180559439-19ed7da2-6ebb-4f9c-92cc-1032bcb0de59.png)




The ***front-end server*** is used to manage the connection with the client;


### Example of one certificate


![image](https://user-images.githubusercontent.com/75567246/180561036-9b827953-92ee-4048-936d-3e8e345cdf34.png)




### Requirements 
* sudo apt install libzbar0 libzbar-dev
* python3 -m pip install zbarlight
* sudo apt install python3-pip
* python3 -m pip install qrcode numpy Pillow
* python3 -m pip opencv-python
* sudo apt-get install imagemagick (for mogrify)
* sudo apt install curl
* python3 -m pip install bottle
* https://fedingo.com/how-to-install-openssl-in-ubuntu/


## contributors :

* [Yawavi Jeona-Lucie LATEVI](https://github.com/jeo284)
* [Claudio Antonio](https://github.com/MonaQuimbamba)

