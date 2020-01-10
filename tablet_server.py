import copy
from influxdb import InfluxDBClient
from requests_html import HTMLSession

host_list = ['xydw40', 
             'xydw41', 
             'xydw42', 
             'xydw43', 
             'xydw44', 
             'xydw45', 
             'xydw46', 
             'xydw47', 
             'xydw48', 
             'xydw40', 
             'xydw50']

session = HTMLSession()
client = InfluxDBClient(host='10.0.4.35', port=8086, username='', password='', database='kudu')

def handle_host_mem(host, content_list):
    tablet_dict = {}
    for i in range(len(content_list)):
        
        if content_list[i] == 'Total consumption':
            tablet_dict['memory_used'] = float(content_list[i + 1].replace('G', ''))
            continue

        if content_list[i] == 'Memory limit':
            tablet_dict['memory_total'] = float(content_list[i + 1].replace('G', ''))
            continue

        if content_list[i] == 'Percentage consumed':
            tablet_dict['percent'] = float(content_list[i + 1].replace('%', ''))
            continue

    value = {}
    value['measurement'] = 'tablet_server'
    value['tags'] = {'host' : host}
    value['fields'] = tablet_dict
    client.write_points([value])
    
def handle_tablet_mem(host, content_list):
    tablet_dict = {}
    tablet_dict['host'] = host
    tablet_list = []
    for i in range(len(content_list)):
        if 'tablet-' in content_list[i] and 'server' == content_list[i + 1]:
            size = 0
            if 'G' in content_list[i + 3]:
                size = float(content_list[i + 3].replace('G', '')) * 1024
            if 'M' in content_list[i + 3]:
                size = float(content_list[i + 3].replace('M', ''))

            if size <= 1024:
                continue
        
            tablet_list.append((content_list[i], int(size)))

    insert_values = []
    for tablet in tablet_list:
        value = {}
        value['measurement'] = 'tablet_metric'
        value['tags'] = copy.deepcopy(tablet_dict)
        value['tags']['tablet'] = tablet[0]
        value['fields'] = {'value' : tablet[1]}
        insert_values.append(value)

    if  insert_values:
        client.write_points(insert_values)

for host in host_list:
    url = 'http://{}:8050/mem-trackers'.format(host)
    r = session.get(url)
    content_str = r.html.text
    content_list = content_str.split('\n')
    
    handle_host_mem(host ,content_list)
    handle_tablet_mem(host, content_list)


