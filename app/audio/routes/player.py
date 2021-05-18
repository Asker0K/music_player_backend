import json
import os
from io import BytesIO

from flask import request, flash, redirect, app, url_for
from pocketsphinx import get_data_path
from pydub import AudioSegment
from werkzeug.utils import secure_filename
import wave
from .. import audio_app
from ..methods.methods import test_audio, split_audio


@audio_app.route("/command", methods=['POST'])
def command():
    if request.method == 'POST':
        data_path = get_data_path()

        file = request.files['data']
        filename = secure_filename(file.filename)

        file.save(os.path.join(data_path, filename))

        split_audio(filename)
        result_command = test_audio(filename)["text"]


        audio_file_1 = os.path.join(data_path, 'add.wav')
        audio_file_2 = os.path.join(data_path, 'test.wav')

        song_1 = AudioSegment.from_wav(audio_file_1)
        print(f'SONG_1_CHANNELS={song_1.channels}, frame_rate={song_1.frame_rate},'
              f'sample_width={song_1.sample_width}, frame_width={song_1.frame_width} ')

        song_2 = AudioSegment.from_wav(audio_file_2)
        print(f'SONG_2_CHANNELS={song_2.channels}, frame_rate={song_2.frame_rate},'
              f'sample_width={song_2.sample_width}, frame_width={song_2.frame_width} ')

        # print(splitted)
        # # check if the post request has the file part
        # if 'data' not in request.files:
        #     print('No file part')
        #     return redirect(request.url)
        # file = request.files['data']
        # # if user does not select file, browser also
        # # submit an empty part without filename
        # if file.filename == '':
        #     print('No selected file')
        #     return redirect(request.url)
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     return redirect(url_for('uploaded_file',
        #                             filename=filename))
        response = {"command": result_command}
        return response


@audio_app.route("/test", methods=['POST'])
def test():
    print("OK")
    return {"command": 'wow'}
