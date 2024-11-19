import routeros_api, random, string, pyperclip, json, os, time


COMMANDS = [
    '1 - Mikrotik delivery with default configuration.',
    '2 - Mikrotik delivery with custom configuration.',
    '3 - Configure ipv6 settings.',
    '4 - Upgrade to the latest stable version.',
    '5 - Downgrade to the 6.49.12 stable version.',

    '\n0 - Disconnect.'
]

FTP_URL_OLDERVERSION_ROUTER = 'ftp://address-to-router-dir/routeros-x86-6.49.12.npk'
FTP_URL_LASTVERSION_ROUTER = 'ftp://address-to-router-dir/routeros-lastest.npk'
FTP_USER_LASTVERSION_ROUTER = 'ftp-user'
FTP_PW_LASTVERSION_ROUTER = 'ftp-password'

MESSAGE_WELCOME = """
  CCC      CCC       EEE                          EEEEEEEEEEE      UUU
  CCCC    CCCC       EEE                          EEEEEEEEEEE      UUU
  CCC CCCM CCC  HHH  EEE  EEE  LLLLLL     SSSSSS      EEE     RRR  UUU  UUU
  CCC  CC  CCC  HHH  EEEEE     LLL  LLL  SSS  SSS     EEE     RRR  UUUUU
  CCC      CCC  HHH  EEE EEE   LLLLLL    SSS  SSS     EEE     RRR  UUU UUU
  CCC      CCC  HHH  EEE  EEE  LLL  LLL   SSSSSS      EEE     RRR  UUU  UUU
=============================================================================
  Login Address pattens:

  USER@IP:PORT | example: admin@111.122.133.144:1516 - Fully customized
  USER@IP      | example: admin@111.122.133.144      - Specify the user
  IP:PORT      | example: 111.122.133.144:1516       - Specify the api port
  IP           | example: 111.122.133.144            - Default (admin - 8728)
=============================================================================
"""


# =========================================================================
    

def generate_password():
    punctuation = '_'
    characters = punctuation + string.ascii_letters + punctuation + string.digits + punctuation #string.punctuation
    pw = ''.join([random.choice(characters) for _ in range(8)])
    pw = 'A' + pw + 'z'
    return pw

class Connection:
    user = 'admin'
    api_port = 8728

    def __init__(self, host, password, user=None, api_port=None):
        self.host = host
        self.password = password
        if user:
            self.user = user
        if api_port:
            self.api_port = api_port

    def connection(self):
        connection = routeros_api.RouterOsApiPool(
                self.host,
                username=self.user,
                password=self.password,
                port=self.api_port,
                use_ssl=False,
                ssl_verify=False,
                ssl_verify_hostname=False,
                ssl_context=None,
                plaintext_login=True
            )
        return connection
        


password = ''
api = None
user = None
api_port = None

print(MESSAGE_WELCOME)

while True:
    host = input('Enter address: ').strip()
    password = input('Enter password: ').strip()

    try:
        if '@' in host:
            user, host = host.split('@')
        if ':' in host:
            host, api_port = host.split(':')

        conn = Connection(host, password)
        if user:
            conn.user = user
        if api_port:
            conn.api_port = api_port

        api = conn.connection().get_api()

    except:
        print('Try logging in as an admin user. Check the host and password again.')

    else:
        print('The connection was made successfully.')

        while True:
            print(
                '\nSelect your function.', 
                '\n'.join(COMMANDS),
                sep='\n'
            )
            selection = int(input(f'Enter a number between 1 - {len(COMMANDS)-1} or 0: '))
            match selection:
                case 0:
                    conn.connection().disconnect()
                    break
                case 1:
                    # delivery mikrotik with default configuration.
                    services = api.get_resource('ip/service')
                    [services.set(id=s['id'], disabled='true') for s in services.get() if s['name'] not in ['api', 'winbox', 'www']]
                    services.set(id='*2', port='505')   # www
                    services.set(id='*8', port='443')   # winbox
                    services.set(id='*7', port='1516')   # api
                    conn.api_port = 1516

                    users = api.get_resource('user')
                    pw = generate_password()
                    users.set(id='*1', password=pw)
                    conn.password = pw

                    
                    print(
                        'Mikrotic configured',
                        f'Username / Password: {conn.user}  {pw}',
                        'The message has been saved to your clipboard.',
                        sep='\n'
                        )
                    # api = conn.connection().get_api()
                case 2:
                    # delivery mikrotik with custom configuration.
                    services = api.get_resource('ip/service')
                    [services.set(id=s['id'], disabled='true') for s in services.get() if s['name'] not in ['api', 'winbox', 'www']]

                    winbox = input('Enter winbox port: ').strip()
                    www = input('Enter www port: ').strip()
                    api_port = input('Enter api port: ').strip()
                    services.set(id='*2', port=www)   # www
                    services.set(id='*8', port=winbox)   # winbox
                    services.set(id='*7', port=api_port)   # api
                    conn.api_port = api_port

                    users = api.get_resource('user')
                    pw = generate_password()
                    users.set(id='*1', password=pw)
                    conn.password = pw

                    
                    print(
                        'Mikrotic configured',
                        f'Username / Password: {conn.user}  {pw}',
                        'The message has been saved to your clipboard.',
                        sep='\n'
                        )
                case 3:
                    # set ipv6 configuration.
                    packages = api.get_resource('system/package')
                    ps = packages.get()
                    for package in ps:
                        if package['name'] == 'ipv6':
                            _id = str(package['id'])
                            if package['disabled'] == 'true':
                                print('\nIPv6 is disabled, we need to enable it before configuration.')
                                ipv6_selection = input('Write (yes or y) to continue, otherwise write (no or n): ').strip()

                                if ipv6_selection in ['yes', 'y']:
                                    # enable and reboot
                                    try:
                                        packages.call('enable', {'id': _id})
                                        print("Router is rebooting...")
                                        api.get_resource('system').call('reboot')

                                    except Exception as e:
                                        print(f"Error enabling ipv6 package: {e}")
                                    else:
                                        while True:
                                            try:
                                                api = conn.connection().get_api()
                                            except:
                                                print('Trying to reconnect, please be patient ...')

                                            else:
                                                print('The connection was made successfully.')
                                                break
                                else:
                                    break
                            
                    try:
                        # configure ipv6
                        interface = [e for e in api.get_resource('interface').get() if e['type'] == 'ether' and e['disabled'] == 'false'][0]
                        _ipv6 = input('Enter IPv6 address: ').strip()
                        _gw = input('Enter IPv6 gateway: ').strip()
                        ipv6 = api.get_resource('ipv6/address')
                        ipv6.add(address=_ipv6, interface=interface['id'])
                        route = api.get_resource('ipv6/route')
                        route.add(distance='1', gateway=_gw)
                        

                        mk_ver = api.get_resource('system/resource').get()[0]['version']
                        if mk_ver.split('.')[0] == '7':
                            ipv6_settings = api.get_resource('ipv6/setting')
                            if ipv6_settings.get()[0]['disable-ipv6'] == 'false':
                                ipv6_settings.call('set', {'disable-ipv6':'true'})

                        print(
                            'IPv6 configured.',
                            f'IPv6: {_ipv6}',
                            'The message has been saved to your clipboard.',
                            sep='\n'
                            )
                    except Exception as e:
                        print(f"Error adding ipv6 network: {e}")
                    pass
                case 4:
                    # upgrade to lastest version.
                    print('Uploading the operating system update file.')
                    api.get_resource('tool').call('fetch', {
                        'url': FTP_URL_LASTVERSION_ROUTER,
                        'user':FTP_USER_LASTVERSION_ROUTER,
                        'password':FTP_PW_LASTVERSION_ROUTER
                    })
                    print('Upload finished.')
                    time.sleep(5)
                    try:
                        print("Router is rebooting...")
                        api.get_resource('system').call('reboot')

                    except Exception as e:
                        print(f"Error upgrading router os: {e}")
                    else:
                        while True:
                            try:
                                api = conn.connection().get_api()
                            except:
                                print('Trying to reconnect, please be patient ...')

                            else:
                                version = api.get_resource('system/resource').get()[0]['version']
                                print('The connection was made successfully.')
                                print(
                                    f'Mikrotik upgraded to version: {version}',
                                    )
                                break

                    # print(api.get_resource('file').get())

                case 5:
                    # downgrade to 6.49.12
                    print('Uploading the operating system update file.')
                    api.get_resource('tool').call('fetch', {
                        'url': FTP_URL_OLDERVERSION_ROUTER,
                        'user':FTP_USER_LASTVERSION_ROUTER,
                        'password':FTP_PW_LASTVERSION_ROUTER
                    })
                    print('Upload finished.')
                    time.sleep(5)
                    try:
                        print("Router is rebooting...")
                        api.get_resource('system/package').call('downgrade')

                    except Exception as e:
                        print(f"Error downgrading router os: {e}")
                    else:
                        while True:
                            try:
                                api = conn.connection().get_api()
                            except:
                                print('Trying to reconnect, please be patient ...')

                            else:
                                version = api.get_resource('system/resource').get()[0]['version']
                                print('The connection was made successfully.')
                                print(
                                    f'Mikrotik downgraded to version: {version}',
                                    )
                                break
                    
                
                
