# Xiaomi Mi Home Bridge
Allows to make a bridge from a xiaomi home gateway (v1) to an mqtt broker.
Test on RaspberryPI raspbian 9.11, with mosquito, and nodered

## Install systemd service
Edit mihomemqtt.service file to change script path

    sudo cp mihomemqtt.service /etc/systemd/system/
    sudo systemctl start myservice
    sudo systemctl enable myservice

## Install mosquito
    sudo apt install mosquitto
    

## Thanks
Thanks to Jonathan Schemoul, HackSpark.fr see https://notes.jmsinfor.com/blog/post/admin/Xiaomi-Hub
