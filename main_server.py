from ytmusicapi import YTMusic
import json

from flask import Flask, request, Response, send_file
from waitress import serve
from urllib.parse import unquote
import random
import webbrowser
import traceback
import subprocess
import socket
import qrcode
import user_agents
import argparse
import time
import os
import signal

def main_html_isExplicit(i: dict) -> str:
    try:
        if i['isExplicit']:
            return 'style="border-bottom: 4px dashed red;" '
        else:
            return 'style="border-bottom: 4px dashed lime;" '
    except:
        return ''

def main_html_videoId(i: dict) -> str:
    try:
        return f'onclick="load_player_song(\'{i["videoId"]}\');"'
    except:
        return ''

def main_html() -> str:
    exit_html = ''
    yt = YTMusic()
    homepage = yt.get_home()
    json.dump(homepage, open('dump.json', 'w'), indent=4)
    exit_html += '''
    <style>
    hr.solid {
        border-top: 3px solid #bbb;
    }

    img.thumbnail {
        margin: 0 15px 0 0;
        float: left;   
    }
    a:link    { 
        text-decoration: none; 
        color: #000000;
        }
    a:visited { 
        text-decoration: none; 
        color: #000000;
        }
    a:hover   { 
        text-decoration: none; 
        color: #000000;
        }
    a:active  { 
        text-decoration: none; 
        color: #000000;
        }

    a.sh3 {
        display: block;
        font-size: 1.2em;
        font-weight: bold;
        text-decoration: none;
        /* color: blue; */
        margin-top: 1em;
        margin-bottom: 1em;
    }

    </style>
    '''
    for index, category in enumerate(homepage):
        exit_html += f'<div id="categories_{category["title"].lower().replace(" ", "_")}">'
        exit_html += f'<h1>{category["title"]}</h1>\n'
        for x, i in enumerate(category['contents']):
            # try:
            #     exit_html += f'<a href="#" style="background-color: {"red" if i["isExplicit"] else "green"}">'
            # except:
            #     exit_html += f'<a href="#">'
            exit_html += f'''
            <div>
                <a>
                    <img {main_html_isExplicit(i)}class="thumbnail" src="{i['thumbnails'][0]['url']}" alt="Here should be an image!" width="55" height="55">
                    <a style="cursor: pointer;" {main_html_videoId(i)} class="sh3">{unquote(i['title']).encode('ascii', 'xmlcharrefreplace').decode()}</a>
                </a>
                <div>\n'''
            try:
                artists_len = len(i['artists'])-1
                for index, z in enumerate(i['artists']):
                    exit_html += f'    <a href="https://music.youtube.com/channel/{z["id"]}">{unquote(z["name"]).encode("ascii", "xmlcharrefreplace").decode()}</a>'
                    if index < artists_len: 
                        exit_html += '<span>&nbsp;&#8226;</span>'
            except: 
                try: 
                    exit_html += unquote(i['description']).encode('ascii', 'xmlcharrefreplace').decode()
                except: 
                    try:
                        exit_html += unquote(i['year']).encode('ascii', 'xmlcharrefreplace').decode()
                    except Exception as e: exit_html += f'Error: {e}'
            exit_html += '''
                </div>
            </div>
            '''
            
            exit_html += '</a><br>'
        exit_html += '</div><br><br>'
        if index < len(homepage)-1: exit_html += '<hr class="solid">'
    return exit_html

def search_html(search) -> str:
    exit_html = ''
    json.dump(search, open('dump.json', 'w'), indent=4)
    exit_html += '''
        <style>
        hr.solid {
           border-top: 3px solid #bbb;
        }

        img.thumbnail {
            margin: 0 15px 0 0;
            float: left;   
        }
        a:link    { 
            text-decoration: none; 
            color: #000000;
            }
        a:visited { 
            text-decoration: none; 
            color: #000000;
            }
        a:hover   { 
            text-decoration: none; 
            color: #000000;
            }
        a:active  { 
            text-decoration: none; 
            color: #000000;
            }

        a.sh3 {
            display: block;
            font-size: 1.2em;
            font-weight: bold;
            text-decoration: none;
            /* color: blue; */
            margin-top: 1em;
            margin-bottom: 1em;
        }

        </style>
        '''
    for index, data in enumerate(search):
        try:
            exit_html += f'''
            <a style="cursor: pointer;" {main_html_videoId(data)} >
                <img class="thumbnail" src="{data['thumbnails'][-1]['url']}" alt="Here should be an image!" width="55" height="55">
                <span class="sh3">{unquote(data['title']).encode('ascii', 'xmlcharrefreplace').decode()}</span><br>'''
            try:
                artists_len = len(data['artists'])-1
                for index, z in enumerate(data['artists']):
                    exit_html += f'''<a href="https://music.youtube.com/channel/{z['id']}">{unquote(z['name']).encode('ascii', 'xmlcharrefreplace').decode()}</a>'''
                    if index < artists_len: 
                        exit_html += '<span>&nbsp;&#8226;</span>'
                    exit_html += '<br>'
            except:
                exit_html += '<br>'
            exit_html += f'''</a><br>
            '''
        except: pass
    return exit_html

app = Flask(__name__)

@app.route('/close', methods=['GET'])
def flask_close():
    # func = request.environ.get('werkzeug.server.shutdown')
    # if func is None:
    #     raise OSError()
    # func()
    os.kill(os.getpid(), signal.SIGINT)
    return "Server shutting down..."

@app.route('/favicon.ico', methods=['GET'])
def flask_favicon():
    return send_file('favicon.ico')

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def flask_index():
    if user_agents.parse(request.user_agent.string).is_mobile:
        return open('mobile_index.html').read()
    else:
        return open('index.html').read()

@app.route('/qr', methods=['GET'])
def flask_qr():
    global port
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'http://{socket.gethostbyname_ex(socket.gethostname())[-1][-1]}:{port}')
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    img.save('temp_qr')
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <center>
            <img src="/file/temp_qr" onerror="img_error(this);" alt="No Qr-Code?" width="300" height="300"><br>
            <a href="http://{socket.gethostbyname_ex(socket.gethostname())[-1][-1]}:{port}">Link</a>
        </center>
        <script>
            function img_error(image) {{
                image.onerror = "";
                image.src = "/file/no_qr.jpg";
                return true;
            }}
        </script>
    </body>
    </html>
    '''

@app.route('/file/<file_name>', methods=['GET'])
def flask_file(file_name):
    try: return send_file(file_name)
    except: return '', 404

@app.route('/html/<file_name>', methods=['GET'])
def flask_html(file_name):
    match file_name:
        case 'main': 
            with open('main.html', 'r') as file:
                with open('temp', 'w') as tfile:
                    tfile.write(
                        file.read().replace('<!-- script -->', main_html())
                    )

            return send_file('temp', download_name='main.html')

        case 'search': 
            return send_file('search.html', download_name='search.html')

        case 'playlist': 
            return send_file('playlist.html')

        case _: return '', 404
    
@app.route('/player/<options>', methods=['GET'])
def flask_player(options):
    match options:
        case 'load': 
            video_data = json.load(open('audio_stream.json', 'r'))
            video_url = video_data['audio_url']
            del video_data['audio_url']
            return json.dumps({
                'audio_file': video_url,
                'video_data': video_data
                })
        
        case 'add':
            try:
                import pafy

                st = time.time()
                video_link = request.args.get('video_id')
                video = pafy.new(video_link)

                best_audio = video.getbestaudio()
                print(f'{video.title} | {video.author}')
                print(f'Elapsed time: {time.time() - st}')

                video_info = {
                    'audio_url': best_audio.url,
                    'title': video.title,
                    'author': video.author,
                    'length': video.length
                }

                json.dump(video_info, open('audio_stream.json', 'w'))
                return 'downloaded'
            except: 
                traceback.print_exc()
                return '', 500

        case 'search':
            try:
                query = request.args.get('query')

                yt = YTMusic()
                return search_html(
                    yt.search(query, 'songs')
                )
            except:
                traceback.print_exc()
                return '', 500

        case _: return '', 404

if __name__ == '__main__':
    # if os.path.basename(os.getcwd()).lower() != 'gui':
    #     os.chdir('gui')

    parser = argparse.ArgumentParser()
    parser.add_argument('-S', '--server', choices=['development', 'wsgi'], default='development')
    parser.add_argument('-G', '--gui', choices=['integrated', 'browser'], default='integrated')
    parser.add_argument('--prod', action='store_true')
    parser.add_argument('--dev', action='store_true')
    parser.add_argument('--port', type=int)
    parser.add_argument('--public', action='store_false')
    parser.set_defaults(prod = True, public = True)
    args = parser.parse_args()

    global port
    if args.port and (1000 <= args.port <= 8000):
        port = args.port
    else:
        port = random.randint(4000, 8000)

    if args.public:
        sip = '0.0.0.0'
    else:
        sip = '127.0.0.1'

    address = f'http://127.0.0.1:{port}'
    name = 'MPReAl'
    icon = 'favicon.ico'

    if args.dev:args.prod = False
    if args.prod or args.dev:
        if args.prod:
            print(f'Open GUI using: .\\python\\python.exe .\\gui\\gui_server.py "{address}" "{name}" ".\\gui\\{icon}"')
            gui_process = subprocess.Popen(['.\\python\\python.exe', '.\\gui_server.py', address, name, icon], 
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.STDOUT
                                        )
            serve(app, host=sip, port=port)
        else:
            webbrowser.open(f'http://127.0.0.1:{port}')
            app.run(sip, port, False)
    else:
        if args.gui == 'integrated':
            print(f'Open GUI using: .\\python\\python.exe gui_server.py "{address}" "{name}" ".\\gui\\{icon}"')
            gui_process = subprocess.Popen(['.\\python\\python.exe', '.\\gui_server.py', address, name, icon], 
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.STDOUT
                                        )

        elif args.gui == 'browser':
            webbrowser.open(f'http://127.0.0.1:{port}')


        if args.server == 'development':
            app.run('0.0.0.0', port)

        elif args.server == 'wsgi':
            serve(app, host='0.0.0.0', port=port)

