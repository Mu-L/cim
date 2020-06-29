import os
from time import sleep
from tqdm import trange, tqdm

import click
import subprocess
from subprocess import Popen


pbar = tqdm(total=100)
pbar.set_description('building')
FNULL = open(os.devnull, 'w')


# pip install tqdm
# pip install click

@click.command()
@click.option("--model", prompt="build model", help="build model[s:server, r:route, c:client]")
def run(model):
    __package()

    if model == 's':
        __build_server()
    elif model == 'r':
        __build_route()
    else:
        __build_client(model.split(' ')[1])


def __build_server():
    click.echo('build cim server.....')
    pbar.update(10)
    subprocess.call(['cp', 'cim-server/target/cim-server-1.0.0-SNAPSHOT.jar', '/data/work/cim/server'])
    subprocess.call(['sh', 'script/server-startup.sh'])

    pbar.update(60)

    click.echo('build cim server success!!!')
    pbar.close()


def __package():
    subprocess.call(['git', 'pull'])
    pbar.update(30)
    subprocess.call(['mvn', '-Dmaven.test.skip=true', 'clean', 'package'], stdout=FNULL, stderr=subprocess.STDOUT)


def __build_route():
    click.echo('build cim route.....')
    pbar.update(10)
    subprocess.call(['cp', 'cim-forward-route/target/cim-forward-route-1.0.0-SNAPSHOT.jar', '/data/work/cim/route'])
    subprocess.call(['sh', 'script/route-startup.sh'])

    pbar.update(60)

    click.echo('build cim route success!!!')


def __build_client(count):
    count = int(count)
    process = 30
    click.echo('build cim {} client.....'.format(count))
    subprocess.call(['cp', 'cim-client/target/cim-client-1.0.0-SNAPSHOT.jar', '/data/work/cim/client'])
    port = 8084
    for i in range(count):
        port = port + 1
        process = process + count
        command = ['nohup', 'java', '-jar', '-Xmx32M', '-Xms32M', '/data/work/cim/client/cim-client-1.0.0-SNAPSHOT.jar',
                   '--server.port={}'.format(port), '--cim.user.id={}'.format(i),
                   '--cim.user.userName={}'.format(i), '--cim.route.url=http://47.98.194.60:8083',
                   '>', '/dev/null', '&']

        click.echo(' '.join(command))
        pbar.update(process)
        Popen(command)
        sleep(2)

    click.echo('build cim {} client success!!!'.format(count))


def progress():
    pbar.update(10)


if __name__ == '__main__':
    run()