import dotenv
import logging
import uvicorn

from .api import app


def main():
    """Fonction principale"""
    uvicorn.run(app, port=8092)


if __name__ == '__main__':
    main()
