from __future__ import unicode_literals
import sys
import youtube_dl
import logging
from flask import Flask, render_template, request, redirect



logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/home")
def home():
    return render_template('index.html')


@app.route('/download_url', methods=['GET','POST'])
def download_video():
    try:
        if request.method == 'POST':
            given_url = request.form['url']
            if given_url != '' and given_url != None:
                ydl_opts = {'format':'best'}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    # dict of video information.
                    info_dict = ydl.extract_info(given_url, download=False)
                    # video url.
                    video_url = info_dict.get('url', None)
                    url = video_url
                    return redirect(url)
        return render_template('error408.html')
    except:
        logging.exception('Failed download')
        return render_template('error(invalid_url).html', given_url=given_url)

'''
!!! TEST CODE BLOCK !!!
if __name__ == "__main__":
    app.run()
'''