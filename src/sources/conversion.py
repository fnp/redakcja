import subprocess


def resize_image(source_file, out_dir):
    subprocess.run([
        'convert',
        source_file,
        '-thumbnail', '1000x1000>',
        out_dir + '/' + source_file.rsplit('/', 1)[-1]
    ])
    

def convert_image(source_file, out_dir):
    subprocess.run([
        'convert',
        source_file,
        '-resize', '1000x1000',
        out_dir + '/' + source_file.rsplit('/', 1)[-1] + '.jpg'
    ])


def convert_pdf(source_file, out_dir):
    # TODO
    pass


def convert_djvu(source_file, view_dir):
    # TODO
    pass
