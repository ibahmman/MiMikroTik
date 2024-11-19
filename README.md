# Connecting to Mikrotik API
Commanding MikroTik router using "routeros_api" library.

## Features
- Changing the service port and setting the admin user password
- IPv6 network configuration
- Upgrade the operating system version.
- Downgrade the operating system version.

## Installation
1. First, clone the repository:
   ```bash
   git clone https://github.com/ibahmman/MiMikroTik.git
   ```
2. Enter the project directory:
   ```bash
   cd MiMikroTik
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.lur
   ```
4. Run the project:
   ```bash
   python mimikrotik.py
   ```

## How to use
- On Windows : Just extract the zip file then run the executable file.
- On Linux : After entering the script directory and going to the virtual environments, run the script.
  ```bash
  source venv/bin/activate
  ```
  ```bash
   python mimikrotik.py
   ```

### **Examples**
An example of logging into a server using Windows software, changing the port and password for the "admin" user, and then logging out of the server.
- You can enter the address in 4 ways to connect to Mikrotik. \n
1. Specify all login details like selected user, IP and API port.
2. In the second method, only the selected user and server IP are specified, and the default port "8728" is used to establish communication.
3. In the third method, only the API port and server IP are specified and communication is established with the "admin" user.
4. In this method, only the IP is specified and by default, communication is established with the "admin" user and port "8728".
   
![Screenshot 2024-11-20 005557](https://github.com/user-attachments/assets/79615825-13e3-4acb-a77b-cd65f76d384a)




