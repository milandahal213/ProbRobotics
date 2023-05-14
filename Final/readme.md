This code implements a system to teach particle filter to high school students using Miro board and LEGO SPIKE Prime robots. 
 </br>
 
# Before running the codes make sure of the following.
1. You will need to run hubOS on your SPIKE Prime. Since we are using UART mode on the SPIKE Prime ports and at the time of writing this code it was available only on hubOS we decided to use the old firmware. </br> </br> Beware that the api is significantly different from the SPIKE 3 firmware. Hence, even if LEGO implements UART on ports in the future the code will not work without significant modifications.
2. You will need to install Mosquitto broker on your computer. </br>
  <code>brew install mosquitto </code>
3. You will need to have access to the Miro Developer account to use the Rest APIs. Follow the instructions on Miro's website. 

# Parts needed:
1. ESP8266 microcontroller board 
  * Install micropython in ESP8266. 
  * Download the files from the ESP8266 folder and save them on the board. 
  * Change the wifi credentials on the secrets.py file. 
  * You should also change the ip address on the main.py file with the ip address of the mosquitto broker *n(which is often the ip of the computer running Mosquitto broker)
  
2. LEGO SPIKE Prime kit
 * You will need LEGO SPIKE Prime kit. Install hubOS firmware. 
 * Download the 
