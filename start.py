from aiohttp.web import run_app

from main_node.app import init


def main():
    run_app(init())


if __name__ == '__main__':
    main()
