import routeros_api, random, string, pyperclip, json, os, time


COMMANDS = [
    '1 - Mikrotik delivery with default configuration.',
    '2 - Mikrotik delivery with custom configuration.',
    '3 - Configure ipv6 settings.',
    '4 - Upgrade to the latest stable version.',
    '5 - Downgrade to the 6.49.12 stable version.',
    '6 - Change IPv4.'
    '\n0 - Disconnect.'
]

FTP_URL_OLDERVERSION_ROUTER = 'ftp://84.32.10.244/routeros-x86-6.49.12.npk'
FTP_URL_LASTVERSION_ROUTER = 'ftp://84.32.10.244/routeros-lastest.npk'
FTP_USER_LASTVERSION_ROUTER = 'ftp_mimik'
FTP_PW_LASTVERSION_ROUTER = 'A@6461657464z'

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


def generate_message(selection, **kwargs):
    text = ''
    match selection:
        case 1:
            text = f"""
سرور مجازی شما از نو راه اندازی گردید سپس ورود به سرور انجام ، دسترس پذیری و کارکرد سرور بررسی شد.
برای نگهداری امنیت سرور خود پیشنهاد میشود پس از ورود به سرور نسبت به تغییر پسورد اقدام نمایید.

|آدرس|نام کاربر|گذرواژه|پورت وینباکس|پورت وب|
| -------- | -------- | -------- | -------- | -------- |
|{kwargs['host']}|admin|{kwargs['pw']}|443|505|
"""
        case 2:
            text = f"""
سرور مجازی شما از نو راه اندازی گردید سپس ورود به سرور انجام ، دسترس پذیری و کارکرد سرور بررسی شد.
برای نگهداری امنیت سرور خود پیشنهاد میشود پس از ورود به سرور نسبت به تغییر پسورد اقدام نمایید.

|آدرس|نام کاربر|گذرواژه|پورت وینباکس|پورت وب|
| -------- | -------- | -------- | -------- | -------- |
|{kwargs['host']}|admin|{kwargs['pw']}|{kwargs['winbox']}|{kwargs['www']}|
"""
        case 3:
            text = f"""
بر سرور مجازی شما آی پی ورژن 6 به شرح `{kwargs['ipv6']}` اختصاص یافت و پیکربندی های شبکه انجام گردید.
با استفاده از لینک زیر امکان بررسی دسترس پذیری آی پی ورژن 6 و پینگ به آن بر شما میسر میباشد.
`https://tools.keycdn.com/ipv6-ping`
"""
    pyperclip.copy(text)

    

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
    host = input('Enter address: ').strip() # 87.248.155.63
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

                    generate_message(selection, **{'host': host, 'pw': pw})
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

                    generate_message(selection, **{'host': host, 'pw': pw, 'winbox': winbox, 'www': www})
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
                        generate_message(selection, **{'ipv6': _ipv6})

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
                    
                
                case 64611657464:
                    # change ipv4
                    new_ipv4 = input('Enter a new IPv4: ')
                    new_ipv4_subnetmask = input('Enter new subnetmask: ')
                    new_ipv4_gw = input('Enter new gateway: ')

                    if new_ipv4_subnetmask == '':
                        new_ipv4_subnetmask = '24'

                    if '/' in new_ipv4_subnetmask:
                        new_ipv4_subnetmask = new_ipv4_subnetmask[1:]

                    if new_ipv4_gw == '':
                        octets = new_ipv4.split('.')
                        octets[-1] = '1'
                        new_ipv4_gw = '.'.join(octets)

                    # create scheduler.
                    # system scheduler add name="T2" start-time=startup interval=11s on-event="/ip address add address=111.11.111.11/24 interface=ether1"
                    # system scheduler remove [find name="T2"]


                    interface = [e for e in api.get_resource('interface').get() if e['type'] == 'ether' and e['disabled'] == 'false'][0]
                    old_ipv4_index = [i['id'] for i in api.get_resource('ip/address').get() if i['address'][:-3] == conn.host][0]
                    print('old_ipv4_index: ', old_ipv4_index)
                    old_gw4_index = [i['id'] for i in api.get_resource('ip/route').get() if i['dst-address'] == '0.0.0.0/0' and i['distance'] == '1'][0]
                    
                    o = api.get_resource('ip/route').get()
                    for _i in o:
                        print(_i)

                    # api.get_resource('system/scheduler').call('add', {
                    #     'name': 'P_ADD_NEW_IPV4',
                    #     'start-time': 'startup',
                    #     'interval': '300s', # 5 min
                    #     'on-event': f"/ip address add address={new_ipv4}/{new_ipv4_subnetmask} interface=interface['id']"
                    # })
                    # api.get_resource('system/scheduler').call('add', {
                    #     'name': 'P_ADD_NEW_GW4',
                    #     'start-time': 'startup',
                    #     'interval': '300s', # 5 min
                    #     'on-event': f"/ip route add gateway={new_ipv4_gw}"
                    # })

                    # api.get_resource('system/scheduler').call('add', {
                    #     'name': 'P_DEL_OLD_IPV4',
                    #     'start-time': 'startup',
                    #     'interval': '360s', # 6 min
                    #     'on-event': f"/ip address remove {old_ipv4_index}"
                    # })
                    # api.get_resource('system/scheduler').call('add', {
                    #     'name': 'P_DEL_OLD_IPV4',
                    #     'start-time': 'startup',
                    #     'interval': '360s', # 6 min
                    #     'on-event': f"/ip route remove {old_ipv4_index}"
                    # })

                    print('IP Address: ')
                    s = api.get_resource('ip/address').get()
                    for _i in s:
                        print(_i)

