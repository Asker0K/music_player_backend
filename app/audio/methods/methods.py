import os

from pocketsphinx import AudioFile, get_model_path, get_data_path, Pocketsphinx, DefaultConfig, Decoder, \
    pocketsphinx as ps, Jsgf
# from pocketsphinx import pocketsphinx as ps

from pydub import AudioSegment
from pydub.utils import make_chunks, which

MODELDIR = get_model_path()
DATA_PATH = get_data_path()


def create_fsg(decoder, fsg_path):
    jsgf = Jsgf(os.path.join(MODELDIR, 'grammar.jsgf'))
    rule = jsgf.get_rule('dictionary.commands')
    fsg = jsgf.build_fsg(rule, decoder.get_logmath(), 7.5)
    fsg.writefile(fsg_path)

    decoder.set_fsg("grammar", fsg)
    decoder.set_search("grammar")
    return decoder


def evaluate_results(dec):
    hypothesis = dec.hyp()
    logmath = dec.get_logmath()
    if hypothesis:
        report = dict(
            text=hypothesis.hypstr,
            score=hypothesis.best_score,
            confidence=logmath.exp(hypothesis.prob),
            segments=tuple((seg.word for seg in dec.seg()))
        )
        return report
    else:
        return "error"


def get_decoder():
    config = ps.Decoder.default_config()

    hmm = os.path.join(MODELDIR, 'cmusphinx-ru-5.2')
    ru_dict = os.path.join(MODELDIR, 'cmudict-ru.dict')
    fsg_path = os.path.join(MODELDIR, 'grammar.fsg')

    config.set_string('-hmm', hmm)
    config.set_boolean('-lm', False)
    config.set_string('-dict', ru_dict)
    decoder = Decoder(config)

    create_fsg(decoder, fsg_path)

    return decoder


def transcribe(decoder, audio_file, libdir=None):
    """ Decode streaming audio data from raw binary file on disk. """
    decoder = get_decoder()
    decoder.start_utt()
    stream = open(audio_file, 'rb')
    while True:
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, True, False)
        else:
            break
    decoder.end_utt()
    return evaluate_results(decoder)


def test_audio(decoder=None, filename="test"):
    audio_file = os.path.join(DATA_PATH, f'{filename}.wav')

    decoder = decoder or get_decoder()
    report = transcribe(decoder, audio_file=audio_file)
    return report


def split_audio(filename):
    data_path = get_data_path()

    AudioSegment.converter = which("ffmpeg")
    AudioSegment.from_file(
        os.path.join(data_path, filename)
    ).set_channels(
        1
    ).set_frame_rate(
        16000
    ).set_sample_width(
        2
    ).export(os.path.join(data_path, f'{filename}.wav'),
             format="wav", bitrate=16)

    # sound = AudioSegment.from_wav(os.path.join(data_path, f'{filename}_waved.wav'))
    # print(f'sound.frame_rate = {sound.frame_rate}')
    # print(f'sound.channels = {sound.channels}')

    # out_filename = f'{filename}_waved.raw'
    # sound.export(os.path.join(data_path, f'{filename}_raw.raw'), format="raw")
    # sound.export(os.path.join(data_path, out_filename),
    #              format="raw")
    # # Create a decoder with a certain model
    # config = DefaultConfig()
    # config.set_string('-hmm', os.path.join(model_path, 'zero_ru.cd_cont_4000'))
    # # config.set_string('-hmm', os.path.join(model_path, 'en-us'))
    # config.set_string('-lm', os.path.join(model_path, 'voxforge_ru.lm.bin'))
    # # config.set_string('-lm', os.path.join(model_path, 'en-us.lm.bin'))
    # # config.set_string('-jsgf', os.path.join(model_path, 'grammar.jsgf'))
    # config.set_string('-dict', os.path.join(model_path, 'cmudict-ru.dict'))
    # # config.set_string('-dict', os.path.join(model_path, 'cmudict-en-us.dict'))
    # decoder = Decoder(config)
    #
    # # Decode streaming data
    # buf = bytearray(1024)
    # # with open(os.path.join(data_path, f'{filename}_raw.raw'), 'rb') as f:
    # # with open(os.path.join(data_path, filename), 'rb') as f:
    # with open(os.path.join(data_path, f'{filename}_waved.wav'), 'rb') as f:
    #     # with open(os.path.join(data_path, 'goforward.raw'), 'rb') as f:
    #     decoder.start_utt()
    #     while f.readinto(buf):
    #         decoder.process_raw(buf, False, False)
    #     decoder.end_utt()
    # print('Best hypothesis segments:', [seg.word for seg in decoder.seg()])

    # config = {
    #     'hmm': os.path.join(model_path, 'zero_ru.cd_cont_4000'),
    #     # 'lm': False,
    #     'lm': os.path.join(model_path, 'voxforge_ru.lm.bin'),
    #     # 'jsgf': os.path.join(model_path, 'grammar.jsgf'),
    #     # 'dict': os.path.join(model_path, 'cmudict-ru.dict')
    #     'dict': os.path.join(model_path, 'cmudict-ru.dict')
    # }
    #
    # ps = Pocketsphinx(**config, verbose=True, logfn='pocketsphinx.log')
    # ps.decode(
    #     # audio_file=os.path.join(data_path, f'{filename}_waved.wav'),
    #     audio_file=os.path.join(data_path, 'alo.wav'),
    #     buffer_size=2048,
    #     no_search=False,
    #     full_utt=False,
    # )
    # print(ps)
    #
    # print(ps.segments())  # => ['<s>', '<sil>', 'go', 'forward', 'ten', 'meters', '</s>']
    # print('Detailed segments:', *ps.segments(detailed=True), sep='\n')  # => [
    # #     word, prob, start_frame, end_frame
    # #     ('<s>', 0, 0, 24)
    # #     ('<sil>', -3778, 25, 45)
    # #     ('go', -27, 46, 63)
    # #     ('forward', -38, 64, 116)
    # #     ('ten', -14105, 117, 152)
    # #     ('meters', -2152, 153, 211)
    # #     ('</s>', 0, 212, 260)
    # # ]
    #
    # print(ps.hypothesis())  # => go forward ten meters
    # print(ps.probability())  # => -32079
    # print(ps.score())  # => -7066
    # print(ps.confidence())  # => 0.04042641466841839
    # print("BBBBBBBEEEEEEEEEEST_________________________")
    # print(*ps.best(count=10), sep='\n')

    return filename
